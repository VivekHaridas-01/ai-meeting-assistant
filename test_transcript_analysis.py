#!/usr/bin/env python3
"""
Test script for transcript analysis functionality

This script demonstrates how to:
1. Generate a transcript from an audio file
2. Save the transcript to a file
3. Analyze the transcript to infer speaker names
"""

import os
import sys
from ai_agent import AIAgent

def test_transcript_generation():
    """Test transcript generation and saving"""
    print("🧪 Testing Transcript Generation")
    print("=" * 50)
    
    # Initialize AI Agent
    agent = AIAgent()
    
    # Check if we have a test audio file
    test_audio = "demo_meeting.wav"
    if not os.path.exists(test_audio):
        print(f"❌ Test audio file not found: {test_audio}")
        print("Please provide an audio file for testing")
        return False
    
    try:
        # Generate transcript
        print(f"📝 Generating transcript from: {test_audio}")
        result = agent.generate_transcript_only(test_audio, "test-meeting-001")
        
        if result.status.value == "completed" and result.transcript:
            print("✅ Transcript generated successfully!")
            
            # Save transcript
            transcript_file = "test_transcript.txt"
            agent.save_transcript_to_file(result.transcript, transcript_file)
            
            print(f"📄 Transcript saved to: {transcript_file}")
            return transcript_file
        else:
            print(f"❌ Transcript generation failed: {result.error_message}")
            return False
            
    except Exception as e:
        print(f"❌ Error during transcript generation: {str(e)}")
        return False

def test_speaker_analysis(transcript_file):
    """Test speaker name analysis"""
    print("\n🔍 Testing Speaker Name Analysis")
    print("=" * 50)
    
    # Initialize AI Agent
    agent = AIAgent()
    
    try:
        # Analyze speaker names
        print(f"📖 Analyzing speaker names from: {transcript_file}")
        speaker_map = agent.analyze_transcript_file(transcript_file)
        
        if speaker_map:
            print("✅ Speaker analysis completed successfully!")
            print(f"\n📊 Inferred Speaker Names:")
            for speaker_label, inferred_name in speaker_map.items():
                print(f"   {speaker_label} → {inferred_name}")
            
            # Show a sample of the transcript
            print(f"\n📄 Sample from transcript file:")
            with open(transcript_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for i, line in enumerate(lines[:10]):  # Show first 10 lines
                    print(f"   {line.rstrip()}")
                if len(lines) > 10:
                    print(f"   ... ({len(lines) - 10} more lines)")
            
            return True
        else:
            print("ℹ️  No speaker names could be inferred")
            return False
            
    except Exception as e:
        print(f"❌ Error during speaker analysis: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🚀 AI Agent Transcript Analysis Test")
    print("=" * 60)
    
    # Test transcript generation
    transcript_file = test_transcript_generation()
    
    if transcript_file:
        # Test speaker analysis
        test_speaker_analysis(transcript_file)
        
        print("\n" + "=" * 60)
        print("✅ Test completed successfully!")
        print(f"📄 Transcript file: {transcript_file}")
        print("🔍 You can now analyze this transcript file using:")
        print(f"   python main.py analyze {transcript_file}")
    else:
        print("\n❌ Test failed")

if __name__ == "__main__":
    main() 