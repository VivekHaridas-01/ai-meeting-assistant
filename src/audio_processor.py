import assemblyai as aai
import requests
import time
import json
from typing import Optional, Dict, Any
from pathlib import Path

from config import Config
from models import MeetingTranscript, TranscriptionSegment, Speaker, SpeakerRole

class AudioProcessor:
    """Handles audio transcription and speaker diarization using AssemblyAI"""
    
    def __init__(self):
        """Initialize the audio processor with AssemblyAI configuration"""
        if not Config.ASSEMBLYAI_API_KEY:
            raise ValueError("AssemblyAI API key is required")
        
        self.config = aai.TranscriptionConfig(
            speaker_labels=True,
            speakers_expected=2,  # Default to 2 speakers, can be adjusted
            auto_highlights=True,
            entity_detection=True,
            sentiment_analysis=True,
            auto_chapters=True
        )
        
        # Initialize AssemblyAI client
        aai.settings.api_key = Config.ASSEMBLYAI_API_KEY
    
    def transcribe_audio(self, audio_path: str, meeting_id: str) -> MeetingTranscript:
        """
        Transcribe audio with speaker diarization
        
        Args:
            audio_path: Path to the local audio file
            meeting_id: Unique identifier for the meeting
            
        Returns:
            MeetingTranscript object with transcription and speaker information
        """
        try:
            print(f"Starting transcription for meeting: {meeting_id}")
            
            # Create transcription request (pass local file path directly)
            transcript = aai.Transcriber().transcribe(
                audio_path,
                config=self.config
            )
            
            if transcript.status == aai.TranscriptStatus.error:
                raise Exception(f"Transcription failed: {transcript.error}")
            
            print(f"Transcription completed successfully")
            
            # Extract unique speakers from utterances
            speaker_ids = set(utt.speaker for utt in transcript.utterances)
            speakers = [
                Speaker(
                    speaker_id=speaker_id,
                    role=SpeakerRole.PARTICIPANT,
                    confidence=1.0  # No per-speaker confidence in utterances
                )
                for speaker_id in speaker_ids
            ]
            
            # Extract segments
            segments = []
            for utterance in transcript.utterances:
                segments.append(TranscriptionSegment(
                    start=int(utterance.start),
                    end=int(utterance.end),
                    speaker=utterance.speaker,
                    text=utterance.text,
                    confidence=getattr(utterance, 'confidence', 1.0)
                ))
            
            # Create meeting transcript
            meeting_transcript = MeetingTranscript(
                meeting_id=meeting_id,
                audio_url=audio_path,  # Now this is the local path
                duration=int(transcript.audio_duration * 1000),  # Convert to milliseconds
                speakers=speakers,
                segments=segments
            )
            
            print(f"Processed {len(segments)} segments from {len(speakers)} speakers")
            return meeting_transcript
            
        except Exception as e:
            print(f"Error during transcription: {str(e)}")
            raise
    
    def get_transcription_status(self, transcript_id: str) -> Dict[str, Any]:
        """
        Get the status of a transcription job
        
        Args:
            transcript_id: ID of the transcription job
            
        Returns:
            Status information about the transcription
        """
        try:
            transcript = aai.Transcript.get_by_id(transcript_id)
            return {
                "status": transcript.status,
                "audio_duration": transcript.audio_duration,
                "confidence": transcript.confidence,
                "error": transcript.error if transcript.status == aai.TranscriptStatus.error else None
            }
        except Exception as e:
            print(f"Error getting transcription status: {str(e)}")
            raise
    
    def process_audio_file(self, audio_path: str, meeting_id: str) -> MeetingTranscript:
        """
        Complete audio processing pipeline: transcribe local file
        
        Args:
            audio_path: Path to the audio file
            meeting_id: Unique identifier for the meeting
            
        Returns:
            MeetingTranscript object
        """
        print(f"Starting audio processing for meeting: {meeting_id}")
        
        # Transcribe audio directly from local file
        transcript = self.transcribe_audio(audio_path, meeting_id)
        
        print(f"Audio processing completed for meeting: {meeting_id}")
        return transcript 