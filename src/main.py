#!/usr/bin/env python3
"""
AI Agent for Meeting Processing and Calendar Management

This script provides a command-line interface for processing meeting audio files,
generating meeting minutes, and creating calendar events.

Usage:
    python main.py process <audio_file> [--meeting-id <id>]
    python main.py minutes <audio_file> [--meeting-id <id>]
    python main.py events <audio_file> [--meeting-id <id>]
    python main.py transcript <audio_file> [--meeting-id <id>]
    python main.py analyze <transcript_file>
    python main.py demo
"""

import argparse
import sys
import os
from pathlib import Path

from ai_agent import AIAgent
from config import Config

def main():
    """Main entry point for the AI Agent"""
    parser = argparse.ArgumentParser(
        description="AI Agent for Meeting Processing and Calendar Management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Process command - full pipeline
    process_parser = subparsers.add_parser('process', help='Process meeting audio (transcript + minutes + calendar events)')
    process_parser.add_argument('audio_file', help='Path to audio file')
    process_parser.add_argument('--meeting-id', help='Meeting ID (optional)')
    
    # Minutes command - generate minutes only
    minutes_parser = subparsers.add_parser('minutes', help='Generate meeting minutes only')
    minutes_parser.add_argument('audio_file', help='Path to audio file')
    minutes_parser.add_argument('--meeting-id', help='Meeting ID (optional)')
    
    # Events command - extract calendar events only
    events_parser = subparsers.add_parser('events', help='Extract and create calendar events only')
    events_parser.add_argument('audio_file', help='Path to audio file')
    events_parser.add_argument('--meeting-id', help='Meeting ID (optional)')
    
    # Transcript command - save transcript only
    transcript_parser = subparsers.add_parser('transcript', help='Generate and save transcript only')
    transcript_parser.add_argument('audio_file', help='Path to audio file')
    transcript_parser.add_argument('--meeting-id', help='Meeting ID (optional)')
    
    # Analyze command - analyze speaker names from transcript file
    analyze_parser = subparsers.add_parser('analyze', help='Analyze speaker names from transcript file')
    analyze_parser.add_argument('transcript_file', help='Path to transcript file')
    
    # Demo command
    demo_parser = subparsers.add_parser('demo', help='Run demo with sample data')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        # Initialize AI Agent
        print("🚀 Initializing AI Agent...")
        agent = AIAgent()
        
        if args.command == 'process':
            process_meeting(agent, args.audio_file, args.meeting_id)
        elif args.command == 'minutes':
            generate_minutes(agent, args.audio_file, args.meeting_id)
        elif args.command == 'events':
            extract_events(agent, args.audio_file, args.meeting_id)
        elif args.command == 'transcript':
            generate_transcript(agent, args.audio_file, args.meeting_id)
        elif args.command == 'analyze':
            analyze_transcript(agent, args.transcript_file)
        elif args.command == 'demo':
            run_demo(agent)
            
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

def process_meeting(agent: AIAgent, audio_file: str, meeting_id: str = None):
    """Process a meeting with full pipeline"""
    print(f"🎯 Processing meeting: {audio_file}")
    
    # Validate audio file
    if not os.path.exists(audio_file):
        print(f"❌ Audio file not found: {audio_file}")
        return
    
    # Process the meeting
    result = agent.process_meeting(audio_file, meeting_id)
    
    # Print summary
    print(agent.get_processing_summary(result))
    
    # Save outputs to organized directories
    if result.transcript:
        agent.save_transcript_to_file(result.transcript)
    
    if result.minutes:
        agent.save_minutes_to_file(result.minutes)
    
    # Print results
    if result.status.value == "completed":
        print("✅ Meeting processing completed successfully!")
        
        if result.minutes:
            print("\n📝 Meeting Minutes Summary:")
            print(f"   Key Points: {len(result.minutes.key_points)}")
            print(f"   Action Items: {len(result.minutes.action_items)}")
            print(f"   Decisions: {len(result.minutes.decisions)}")
            print(f"   Next Steps: {len(result.minutes.next_steps)}")
        
        if result.calendar_events:
            print(f"\n📅 Calendar Events Created: {len(result.calendar_events)}")
            for event in result.calendar_events:
                print(f"   - {event.summary} ({event.start_time.strftime('%Y-%m-%d %H:%M')})")
    else:
        print(f"❌ Meeting processing failed: {result.error_message}")

def generate_minutes(agent: AIAgent, audio_file: str, meeting_id: str = None):
    """Generate meeting minutes only"""
    print(f"📝 Generating minutes for: {audio_file}")
    
    # Validate audio file
    if not os.path.exists(audio_file):
        print(f"❌ Audio file not found: {audio_file}")
        return
    
    # Generate minutes
    result = agent.generate_minutes_only(audio_file, meeting_id)
    
    # Print summary
    print(agent.get_processing_summary(result))
    
    # Save minutes to minutes directory
    if result.minutes:
        agent.save_minutes_to_file(result.minutes)
    
    # Print results
    if result.status.value == "completed" and result.minutes:
        print("✅ Meeting minutes generated successfully!")
        print("📄 Minutes saved to minutes directory")
        print(f"\n📝 Summary: {result.minutes.summary}")
    else:
        print(f"❌ Minutes generation failed: {result.error_message}")

def extract_events(agent: AIAgent, audio_file: str, meeting_id: str = None):
    """Extract calendar events only"""
    print(f"📅 Extracting events from: {audio_file}")
    
    # Validate audio file
    if not os.path.exists(audio_file):
        print(f"❌ Audio file not found: {audio_file}")
        return
    
    # Extract events
    result = agent.extract_events_only(audio_file, meeting_id)
    
    # Print summary
    print(agent.get_processing_summary(result))
    
    # Print results
    if result.status.value == "completed":
        print("✅ Event extraction completed successfully!")
        if result.calendar_events:
            print(f"\n📅 Calendar Events Created: {len(result.calendar_events)}")
            for event in result.calendar_events:
                print(f"   - {event.summary} ({event.start_time.strftime('%Y-%m-%d %H:%M')})")
        else:
            print("   No calendar events found in the meeting")
    else:
        print(f"❌ Event extraction failed: {result.error_message}")

def generate_transcript(agent: AIAgent, audio_file: str, meeting_id: str = None):
    """Generate and save transcript only"""
    print(f"📝 Generating transcript for: {audio_file}")
    
    # Validate audio file
    if not os.path.exists(audio_file):
        print(f"❌ Audio file not found: {audio_file}")
        return
    
    # Generate transcript
    result = agent.generate_transcript_only(audio_file, meeting_id)
    
    # Print summary
    print(agent.get_processing_summary(result))
    
    # Save transcript to transcripts directory
    if result.transcript:
        agent.save_transcript_to_file(result.transcript)
    
    # Print results
    if result.status.value == "completed" and result.transcript:
        print("✅ Transcript generated successfully!")
        print("📄 Transcript saved to transcripts directory")
    else:
        print(f"❌ Transcript generation failed: {result.error_message}")

def analyze_transcript(agent: AIAgent, transcript_file: str):
    """Analyze speaker names from transcript file"""
    print(f"🔍 Analyzing speaker names from: {transcript_file}")
    
    # Validate transcript file
    if not os.path.exists(transcript_file):
        print(f"❌ Transcript file not found: {transcript_file}")
        return
    
    try:
        # Analyze transcript
        speaker_map = agent.analyze_transcript_file(transcript_file)
        
        # Print results
        if speaker_map:
            print("✅ Speaker analysis completed successfully!")
            print(f"\n📊 Speaker Name Mapping:")
            for speaker_label, inferred_name in speaker_map.items():
                print(f"   {speaker_label} → {inferred_name}")
        else:
            print("ℹ️  No speaker names could be inferred from the transcript")
            
    except Exception as e:
        print(f"❌ Speaker analysis failed: {str(e)}")

def run_demo(agent: AIAgent):
    """Run a demo with sample data"""
    print("🎬 Running AI Agent Demo")
    print("=" * 50)
    
    # Check if demo audio file exists
    demo_audio = "demo_meeting.wav"
    if not os.path.exists(demo_audio):
        print(f"❌ Demo audio file not found: {demo_audio}")
        print("Please provide a demo audio file or use a real audio file with the process command")
        return
    
    print("📁 Using demo audio file")
    print("🔧 This will demonstrate the full pipeline:")
    print("   1. Audio transcription with speaker diarization")
    print("   2. Meeting minutes generation")
    print("   3. Calendar event extraction and creation")
    print()
    
    # Process the demo
    result = agent.process_meeting(demo_audio, "demo-meeting-001")
    
    # Print detailed results
    print("\n" + "=" * 50)
    print("📊 DEMO RESULTS")
    print("=" * 50)
    
    print(agent.get_processing_summary(result))
    
    if result.status.value == "completed":
        print("✅ Demo completed successfully!")
        
        # Save demo minutes
        demo_output = "demo_minutes.md"
        if result.minutes:
            if demo_output.lower().endswith('.docx'):
                agent.save_minutes_to_docx(result.minutes, demo_output)
            else:
                agent.save_minutes_to_file(result.minutes, demo_output)
            print(f"📄 Demo minutes saved to: {demo_output}")
    else:
        print(f"❌ Demo failed: {result.error_message}")

def check_requirements():
    """Check if all requirements are met"""
    print("🔍 Checking requirements...")
    
    # Check AssemblyAI API key
    if not Config.ASSEMBLYAI_API_KEY:
        print("❌ ASSEMBLYAI_API_KEY not found in environment variables")
        print("   Please set your AssemblyAI API key:")
        print("   export ASSEMBLYAI_API_KEY='your_api_key_here'")
        return False
    
    # Check Google credentials
    if not os.path.exists(Config.GOOGLE_CREDENTIALS_FILE):
        print(f"⚠️  Google credentials file not found: {Config.GOOGLE_CREDENTIALS_FILE}")
        print("   Calendar features will not work without Google credentials")
        print("   Download credentials.json from Google Cloud Console")
    
    # Check Ollama connection
    try:
        import requests
        response = requests.get(f"{Config.OLLAMA_BASE_URL}/api/tags", timeout=5)
        if response.status_code != 200:
            print("⚠️  Ollama service not accessible")
            print("   Make sure Ollama is running and Llama 3.2 is installed")
        else:
            print("✅ Ollama service is accessible")
    except Exception as e:
        print(f"⚠️  Ollama service not accessible: {str(e)}")
        print("   Make sure Ollama is running and Llama 3.2 is installed")
    
    print("✅ Requirements check completed")
    return True

if __name__ == "__main__":
    # Check requirements before running
    if not check_requirements():
        print("\n❌ Some requirements are not met. Please fix the issues above.")
        sys.exit(1)
    
    main()
