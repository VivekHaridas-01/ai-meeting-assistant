import os
from dotenv import load_dotenv
from typing import Optional
from pathlib import Path

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for the AI Agent"""
    
    # Base directory
    BASE_DIR = Path(__file__).parent.parent
    
    # AssemblyAI Configuration
    ASSEMBLYAI_API_KEY = os.getenv('ASSEMBLYAI_API_KEY')
    ASSEMBLYAI_BASE_URL: str = "https://api.assemblyai.com/v2"
    
    # Google Calendar Configuration
    GOOGLE_CREDENTIALS_FILE = os.path.join(BASE_DIR, 'config', 'credentials.json')
    GOOGLE_TOKEN_FILE = os.path.join(BASE_DIR, 'config', 'token.json')
    GOOGLE_SCOPES: list = [
        "https://www.googleapis.com/auth/calendar",
        "https://www.googleapis.com/auth/calendar.events"
    ]
    GOOGLE_CALENDAR_TIMEZONE: str = os.getenv("GOOGLE_CALENDAR_TIMEZONE", "America/New_York")
    
    # Ollama Configuration
    OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama3.2')
    
    # Audio Processing Configuration
    SUPPORTED_AUDIO_FORMATS: list = [".mp3", ".wav", ".m4a", ".flac"]
    MAX_AUDIO_DURATION: int = 3600  # 1 hour in seconds
    
    # Meeting Minutes Configuration
    MINUTES_TEMPLATE: str = """
    # Meeting Minutes
    
    **Date:** {date}
    **Duration:** {duration}
    **Participants:** {participants}
    
    ## Key Points Discussed
    {key_points}
    
    ## Action Items
    {action_items}
    
    ## Decisions Made
    {decisions}
    
    ## Next Steps
    {next_steps}
    """
    
    # Output directories
    OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
    TRANSCRIPTS_DIR = os.path.join(OUTPUT_DIR, 'transcripts')
    MINUTES_DIR = os.path.join(OUTPUT_DIR, 'minutes')
    
    # Create output directories if they don't exist
    @classmethod
    def ensure_directories(cls):
        """Ensure all output directories exist"""
        for directory in [cls.OUTPUT_DIR, cls.TRANSCRIPTS_DIR, cls.MINUTES_DIR]:
            os.makedirs(directory, exist_ok=True)
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate that required configuration is present"""
        cls.ensure_directories()
        
        missing = []
        
        if not cls.ASSEMBLYAI_API_KEY:
            missing.append("ASSEMBLYAI_API_KEY")
        
        if not os.path.exists(cls.GOOGLE_CREDENTIALS_FILE):
            missing.append("Google credentials file")
        
        if missing:
            print(f"Warning: Missing configuration: {', '.join(missing)}")
            return False
        
        return True 
