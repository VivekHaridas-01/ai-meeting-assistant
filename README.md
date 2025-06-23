# AI Agent for Meeting Processing and Calendar Management

An intelligent AI agent that listens to phone calls, generates meeting minutes, and automatically schedules events in Google Calendar based on meeting decisions.

## 🚀 Features

- **Audio Transcription**: High-quality speech-to-text using AssemblyAI with speaker diarization
- **Meeting Minutes Generation**: AI-powered extraction of key points, action items, and decisions
- **Calendar Integration**: Automatic event creation in Google Calendar
- **Speaker Name Inference**: LLM-powered identification of real speaker names from context
- **Local LLM Processing**: Uses Llama 3.2 via Ollama for privacy and cost-effectiveness
- **Modular Architecture**: Clean, extensible codebase with organized folder structure
- **Organized Outputs**: Automatic file organization in dedicated directories

## 🗂️ Project Structure

```
Project/
├── src/                          # Source code
│   ├── main.py                   # CLI entry point
│   ├── setup.py                  # Setup utilities
│   ├── ai_agent.py               # Main orchestrator
│   ├── audio_processor.py        # AssemblyAI transcription
│   ├── calendar_manager.py       # Google Calendar integration
│   ├── config.py                 # Configuration management
│   ├── llm_processor.py          # Ollama/Llama 3.2 processing
│   └── models.py                 # Data models
├── config/                       # Configuration files
│   ├── credentials.json          # Google Calendar credentials
│   └── token.json                # Google OAuth token
├── examples/                     # Example files
│   ├── example_transcript.txt
│   ├── example_with_names.txt
│   ├── env.example               # Environment template
│   └── sample_audio.mp3          # Test audio file
├── tests/                        # Test files
│   └── test_transcript_analysis.py
├── output/                       # Generated outputs
│   ├── minutes/                  # Meeting minutes (.docx files)
│   └── transcripts/              # Transcripts (.txt files)
├── docs/                         # Documentation
├── run.py                        # Main entry point
├── requirements.txt              # Dependencies
├── README.md                     # Main documentation
└── .env                          # Environment variables
```

## 📋 Requirements

- Python 3.8+
- AssemblyAI API key
- Google Cloud credentials
- Ollama with Llama 3.2 installed
- Audio files in supported formats (MP3, WAV, M4A, FLAC)

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai-meeting-agent
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your API keys and configuration
   ```

4. **Install and configure Ollama**
   ```bash
   # Install Ollama (https://ollama.ai/)
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Pull Llama 3.2 model
   ollama pull llama3.2
   
   # Start Ollama service
   ollama serve
   ```

5. **Set up Google Calendar API**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable Google Calendar API
   - Create credentials (OAuth 2.0 Client ID)
   - Download `credentials.json` and place it in the project root

6. **Get AssemblyAI API key**
   - Sign up at [AssemblyAI](https://www.assemblyai.com/)
   - Get your API key from the dashboard
   - Add it to your `.env` file

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# AssemblyAI Configuration
ASSEMBLYAI_API_KEY=your_assemblyai_api_key_here

# Google Calendar Configuration
GOOGLE_CREDENTIALS_FILE=credentials.json
GOOGLE_TOKEN_FILE=token.json

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

### Supported Audio Formats

- MP3 (.mp3)
- WAV (.wav)
- M4A (.m4a)
- FLAC (.flac)

## 📖 Usage

### Command Line Interface

The AI Agent provides a comprehensive CLI for different use cases:

#### Process Complete Meeting (Recommended)
```bash
python run.py process meeting_audio.wav --meeting-id "team-meeting-001"
```

#### Generate Meeting Minutes Only
```bash
python run.py minutes meeting_audio.wav --meeting-id "team-meeting-001"
```

#### Extract Calendar Events Only
```bash
python run.py events meeting_audio.wav
```

#### Generate Transcript Only
```bash
python run.py transcript meeting_audio.wav
```

#### Analyze Speaker Names from Transcript
```bash
python run.py analyze transcript.txt
```

#### Run Demo
```bash
python run.py demo
```

### Programmatic Usage

```python
from ai_agent import AIAgent

# Initialize the agent
agent = AIAgent()

# Process a meeting with full pipeline
result = agent.process_meeting("meeting_audio.wav", "meeting-001")

# Check results
if result.status.value == "completed":
    print(f"Processing completed in {result.processing_time:.2f} seconds")
    print(f"Generated {len(result.minutes.key_points)} key points")
    print(f"Created {len(result.calendar_events)} calendar events")
```

## 🔍 Troubleshooting

### Common Issues

1. **AssemblyAI API Error**
   - Verify your API key is correct
   - Check your account has sufficient credits
   - Ensure audio file format is supported

2. **Ollama Connection Error**
   - Make sure Ollama is running: `ollama serve`
   - Verify Llama 3.2 is installed: `ollama list`
   - Check the service URL in configuration

3. **Google Calendar Authentication**
   - Ensure `credentials.json` is in the project root
   - Complete OAuth flow on first run
   - Check API is enabled in Google Cloud Console

4. **Audio Processing Issues**
   - Verify audio file exists and is readable
   - Check file format is supported
   - Ensure file size is reasonable (< 1GB)

### Debug Mode

Enable verbose logging by setting environment variable:
```bash
export PYTHONPATH=.
python -u main.py process audio.wav
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [AssemblyAI](https://www.assemblyai.com/) for speech recognition
- [Ollama](https://ollama.ai/) for local LLM hosting
- [Google Calendar API](https://developers.google.com/calendar) for calendar integration

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the documentation
3. Open an issue on GitHub
4. Contact the development team

---

**Note**: This AI Agent processes audio files and may contain sensitive information. Ensure you have proper permissions and follow data privacy guidelines when using this tool. 