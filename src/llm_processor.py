import requests
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import re

from config import Config
from models import MeetingTranscript, MeetingMinutes, ActionItem, Decision, CalendarEvent

class LLMProcessor:
    """Handles LLM processing using Ollama with Llama 3.2 for meeting analysis"""
    
    def __init__(self):
        """Initialize the LLM processor with Ollama configuration"""
        self.base_url = Config.OLLAMA_BASE_URL
        self.model = Config.OLLAMA_MODEL
        
        # Test connection to Ollama
        self._test_connection()
    
    def _test_connection(self):
        """Test connection to Ollama service"""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            if response.status_code != 200:
                raise ConnectionError(f"Failed to connect to Ollama: {response.status_code}")
            print(f"Connected to Ollama successfully. Available models: {[m['name'] for m in response.json()['models']]}")
        except Exception as e:
            print(f"Warning: Could not connect to Ollama: {str(e)}")
            print("Make sure Ollama is running and Llama 3.2 is installed")
    
    def _call_ollama(self, prompt: str, system_prompt: str = "") -> str:
        """
        Make a call to Ollama API
        
        Args:
            prompt: The user prompt
            system_prompt: The system prompt (optional)
            
        Returns:
            Response from the LLM
        """
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "top_p": 0.9,
                    "max_tokens": 4000
                }
            }
            
            if system_prompt:
                payload["system"] = system_prompt
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=120
            )
            
            if response.status_code != 200:
                raise Exception(f"Ollama API error: {response.status_code} - {response.text}")
            
            result = response.json()
            return result.get("response", "")
            
        except Exception as e:
            print(f"Error calling Ollama: {str(e)}")
            raise
    
    def extract_first_json_block(self, text):
        start = text.find('{')
        if start == -1:
            raise ValueError("No JSON object found in response.")
        brace_count = 0
        for i in range(start, len(text)):
            if text[i] == '{':
                brace_count += 1
            elif text[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    try:
                        return json.loads(text[start:i+1])
                    except json.JSONDecodeError:
                        break
        raise ValueError("No valid JSON object found in response.")
    
    def generate_meeting_minutes(self, transcript: MeetingTranscript) -> MeetingMinutes:
        """
        Generate structured meeting minutes from transcript
        
        Args:
            transcript: MeetingTranscript object
            
        Returns:
            MeetingMinutes object
        """
        try:
            print("Generating meeting minutes...")
            
            # Prepare transcript text for analysis
            transcript_text = self._prepare_transcript_text(transcript)
            
            # System prompt for meeting minutes generation
            system_prompt = """You are an expert meeting assistant. Your task is to analyze a meeting transcript and generate comprehensive meeting minutes. 
            
            Focus on:
            1. Key points discussed
            2. Action items with assignees and due dates
            3. Decisions made with rationale
            4. Next steps
            
            Be concise but thorough. Extract specific dates, times, and commitments mentioned."""
            
            # User prompt
            prompt = f"""Please analyze this meeting transcript and generate structured meeting minutes:

{transcript_text}

Please provide the analysis in the following JSON format:
{{
    "key_points": ["point1", "point2", ...],
    "action_items": [
        {{
            "description": "action item description",
            "assignee": "person name or 'TBD'",
            "due_date": "YYYY-MM-DD or null",
            "priority": "low/medium/high"
        }}
    ],
    "decisions": [
        {{
            "topic": "decision topic",
            "decision": "what was decided",
            "rationale": "why this decision was made"
        }}
    ],
    "next_steps": ["step1", "step2", ...],
    "summary": "brief summary of the meeting"
}}"""
            
            # Get LLM response
            response = self._call_ollama(prompt, system_prompt)
            
            # Parse JSON response
            try:
                parsed_data = self.extract_first_json_block(response)
            except Exception as e:
                print(f"Error parsing LLM response: {e}")
                print(f"Raw response: {response}")
                parsed_data = self._fallback_parsing(response)
            
            # Create action items
            action_items = []
            for item in parsed_data.get("action_items", []):
                due_date = None
                if item.get("due_date"):
                    try:
                        due_date = datetime.strptime(item["due_date"], "%Y-%m-%d")
                    except ValueError:
                        pass
                
                action_items.append(ActionItem(
                    description=item.get("description", ""),
                    assignee=item.get("assignee"),
                    due_date=due_date,
                    priority=item.get("priority", "medium")
                ))
            
            # Create decisions
            decisions = []
            for decision in parsed_data.get("decisions", []):
                decisions.append(Decision(
                    topic=decision.get("topic", ""),
                    decision=decision.get("decision", ""),
                    rationale=decision.get("rationale")
                ))
            
            # Get unique participants
            participants = list(set([segment.speaker for segment in transcript.segments]))
            
            # Ensure all list fields are not None
            key_points = parsed_data.get("key_points") or []
            next_steps = parsed_data.get("next_steps") or []
            action_items = action_items or []
            decisions = decisions or []

            # Create meeting minutes
            minutes = MeetingMinutes(
                meeting_id=transcript.meeting_id,
                date=transcript.created_at,
                duration=timedelta(milliseconds=transcript.duration),
                participants=participants,
                key_points=key_points,
                action_items=action_items,
                decisions=decisions,
                next_steps=next_steps,
                summary=parsed_data.get("summary", "")
            )
            
            print("Meeting minutes generated successfully")
            return minutes
            
        except Exception as e:
            print(f"Error generating meeting minutes: {str(e)}")
            raise
    
    def parse_datetime(self, dt_str):
        for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S"):
            try:
                return datetime.strptime(dt_str, fmt)
            except ValueError:
                continue
        raise ValueError(f"Time data '{dt_str}' does not match expected formats.")

    def extract_calendar_events(self, transcript: MeetingTranscript, minutes: MeetingMinutes) -> List[CalendarEvent]:
        """
        Extract calendar events from meeting transcript and minutes
        
        Args:
            transcript: MeetingTranscript object
            minutes: MeetingMinutes object
            
        Returns:
            List of CalendarEvent objects
        """
        try:
            print("Extracting calendar events...")
            
            # Prepare transcript text for analysis
            transcript_text = self._prepare_transcript_text(transcript)
            
            # Get today's date and time
            now = datetime.now()
            today_str = now.strftime("%A, %B %d, %Y")
            time_str = now.strftime("%I:%M %p")
            
            # System prompt for calendar event extraction with explicit rules
            system_prompt = f"""Today is {today_str}. The current time is {time_str}.

When extracting event dates/times from the transcript:
- "Thursday" means the next Thursday after today.
- "Next Sunday" means the Sunday after the coming Sunday.
- "23rd Afternoon" means 12pm-1pm on the 23rd of this month (or next month if the 23rd has passed).
- "29th June around 2pm" means 29th June of this year at 2pm.
- "5pm today" means today at 5pm.
- If the transcript mentions "lunch", set the time to 12:00 pm.
- If the transcript mentions "afternoon", set the time to 1:00 pm.
- If the transcript mentions "evening", set the time to 6:00 pm.
- If the transcript mentions "morning", set the time to 9:00 am.
- If a date is ambiguous, prefer the next possible occurrence.
- Always return the event start and end time in the format YYYY-MM-DD HH:MM (24-hour time).
"""
            
            # User prompt
            prompt = f"""Please analyze this meeting transcript and extract any calendar events that should be scheduled:

{transcript_text}

Please provide the events in the following JSON format:
{{
    "events": [
        {{
            "summary": "event title",
            "description": "event description",
            "start_time": "YYYY-MM-DD HH:MM",
            "end_time": "YYYY-MM-DD HH:MM",
            "attendees": ["email1@example.com", "email2@example.com"],
            "location": "meeting location or null"
        }}
    ]
}}

Only include events that have specific dates and times mentioned. If no clear events are found, return an empty events array."""
            
            # Get LLM response
            response = self._call_ollama(prompt, system_prompt)
            
            # Parse JSON response
            try:
                parsed_data = self.extract_first_json_block(response)
            except Exception as e:
                print(f"Error parsing calendar events response: {e}")
                print(f"Raw response: {response}")
                return []
            
            # Create calendar events
            events = []
            for event_data in parsed_data.get("events", []):
                try:
                    start_time = self.parse_datetime(event_data["start_time"])
                    end_time = self.parse_datetime(event_data["end_time"])
                    
                    events.append(CalendarEvent(
                        summary=event_data.get("summary", ""),
                        description=event_data.get("description", ""),
                        start_time=start_time,
                        end_time=end_time,
                        attendees=event_data.get("attendees", []),
                        location=event_data.get("location")
                    ))
                except (ValueError, KeyError) as e:
                    print(f"Error parsing event data: {e}")
                    continue
            
            print(f"Extracted {len(events)} calendar events")
            return events
            
        except Exception as e:
            print(f"Error extracting calendar events: {str(e)}")
            return []
    
    def _prepare_transcript_text(self, transcript: MeetingTranscript) -> str:
        """
        Prepare transcript text for LLM analysis
        
        Args:
            transcript: MeetingTranscript object
            
        Returns:
            Formatted transcript text
        """
        text_parts = []
        
        # Add speaker information
        speakers_info = ", ".join([f"Speaker {s.speaker_id}" for s in transcript.speakers])
        text_parts.append(f"Meeting Participants: {speakers_info}")
        text_parts.append("")
        
        # Add transcript segments
        for segment in transcript.segments:
            timestamp = f"[{segment.start//1000//60:02d}:{segment.start//1000%60:02d}]"
            text_parts.append(f"{timestamp} Speaker {segment.speaker}: {segment.text}")
        
        return "\n".join(text_parts)
    
    def _fallback_parsing(self, response: str) -> Dict[str, Any]:
        """
        Fallback parsing when JSON parsing fails
        
        Args:
            response: Raw LLM response
            
        Returns:
            Parsed data dictionary
        """
        print("Using fallback parsing for LLM response")
        
        # Simple extraction of key information
        key_points = []
        action_items = []
        decisions = []
        next_steps = []
        summary = ""
        
        # Extract key points (lines starting with - or •)
        for line in response.split('\n'):
            line = line.strip()
            if line.startswith(('-', '•', '*')) and len(line) > 2:
                key_points.append(line[1:].strip())
        
        # Extract summary (look for summary section)
        if "summary" in response.lower():
            summary_match = re.search(r'summary[:\s]+(.+?)(?:\n|$)', response, re.IGNORECASE)
            if summary_match:
                summary = summary_match.group(1).strip()
        
        return {
            "key_points": key_points,
            "action_items": [],
            "decisions": [],
            "next_steps": [],
            "summary": summary
        }

    def infer_speaker_names(self, transcript):
        """
        Use the LLM to infer real names for speaker labels based on transcript context.
        Returns a dict mapping speaker labels to names.
        """
        # Prepare transcript text for analysis
        transcript_lines = []
        for segment in transcript.segments:
            timestamp = f"[{segment.start//1000//60:02d}:{segment.start//1000%60:02d}]"
            transcript_lines.append(f"{timestamp} {segment.speaker}: {segment.text}")
        transcript_text = "\n".join(transcript_lines)

        system_prompt = (
            "You are an expert meeting assistant specializing in speaker identification. "
            "Given a meeting transcript with speaker labels and their utterances, "
            "infer the most likely real names for each speaker label based on context clues, "
            "introductions, self-identifications, or references by other speakers. "
            "Look for patterns like: 'Hi, I'm John', 'This is Sarah speaking', 'John mentioned...', etc. "
            "If a name cannot be determined with reasonable confidence, keep the original label. "
            "Output only a JSON mapping of speaker labels to names."
        )
        
        prompt = f"""
Please analyze this meeting transcript and infer the real names for each speaker:

{transcript_text}

Provide a JSON mapping of speaker labels to inferred names. For example:
{{
  "A": "John Smith",
  "B": "Sarah Johnson",
  "C": "C"
}}

Only change labels where you can confidently infer a name from the context.
Look for:
- Self-introductions ("Hi, I'm Alex")
- Direct references ("Hey Jessica")
- Context clues that reveal names
"""
        
        try:
            response = self._call_ollama(prompt, system_prompt)
            mapping = self.extract_first_json_block(response)
            
            if not isinstance(mapping, dict):
                raise ValueError("Response is not a valid dictionary")
            
            # Validate the mapping
            validated_mapping = {}
            for speaker_label, inferred_name in mapping.items():
                if isinstance(speaker_label, str) and isinstance(inferred_name, str):
                    validated_mapping[speaker_label] = inferred_name
            
            print(f"🔍 LLM inferred speaker mapping: {validated_mapping}")
            return validated_mapping
            
        except Exception as e:
            print(f"Error inferring speaker names: {e}")
            print(f"Raw response: {response}")
            return {}

    def analyze_speaker_names_from_text(self, transcript_text: str) -> dict:
        """
        Analyze transcript text to infer speaker names
        
        Args:
            transcript_text: Raw transcript text content
            
        Returns:
            Dictionary mapping speaker labels to inferred names
        """
        system_prompt = (
            "You are an expert meeting assistant specializing in speaker identification. "
            "Given a meeting transcript, analyze the content to infer the most likely real names "
            "for each speaker label based on context clues, introductions, self-identifications, "
            "or references by other speakers. "
            "Look for patterns like: 'Hi, I'm John', 'This is Sarah speaking', 'John mentioned...', etc. "
            "If a name cannot be determined with reasonable confidence, keep the original label. "
            "Output only a JSON mapping of speaker labels to names."
        )
        
        prompt = f"""
Please analyze this meeting transcript and infer the real names for each speaker:

{transcript_text}

Provide a JSON mapping of speaker labels to inferred names. For example:
{{
  "Speaker A": "John Smith",
  "Speaker B": "Sarah Johnson",
  "Speaker C": "Speaker C"
}}

Only change labels where you can confidently infer a name from the context.
"""
        
        try:
            response = self._call_ollama(prompt, system_prompt)
            mapping = self.extract_first_json_block(response)
            
            if not isinstance(mapping, dict):
                raise ValueError("Response is not a valid dictionary")
            
            # Validate the mapping
            validated_mapping = {}
            for speaker_label, inferred_name in mapping.items():
                if isinstance(speaker_label, str) and isinstance(inferred_name, str):
                    validated_mapping[speaker_label] = inferred_name
            
            return validated_mapping
            
        except Exception as e:
            print(f"Error analyzing speaker names from text: {e}")
            print(f"Raw response: {response}")
            return {} 