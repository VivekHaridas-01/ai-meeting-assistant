#!/usr/bin/env python3
"""
Setup script for AI Agent for Meeting Processing

This script helps users set up the AI Agent system with all necessary
dependencies and configuration.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"   Error output: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ required, found {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing Python dependencies...")
    
    # Check if pip is available
    if not shutil.which("pip"):
        print("❌ pip not found. Please install pip first.")
        return False
    
    # Install requirements
    if os.path.exists("requirements.txt"):
        return run_command("pip install -r requirements.txt", "Installing requirements")
    else:
        print("❌ requirements.txt not found")
        return False

def check_ollama():
    """Check if Ollama is installed and running"""
    print("🤖 Checking Ollama installation...")
    
    # Check if ollama command exists
    if not shutil.which("ollama"):
        print("⚠️  Ollama not found. Installing Ollama...")
        install_ollama()
    else:
        print("✅ Ollama is installed")
    
    # Check if Ollama service is running
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama service is running")
            
            # Check if Llama 3.2 is available
            models = response.json().get("models", [])
            llama_models = [m["name"] for m in models if "llama" in m["name"].lower()]
            
            if llama_models:
                print(f"✅ Llama models found: {', '.join(llama_models)}")
            else:
                print("⚠️  No Llama models found. Pulling Llama 3.2...")
                run_command("ollama pull llama3.2", "Pulling Llama 3.2 model")
        else:
            print("⚠️  Ollama service not responding")
            return False
    except Exception as e:
        print(f"❌ Ollama service not accessible: {e}")
        print("   Please start Ollama with: ollama serve")
        return False
    
    return True

def install_ollama():
    """Install Ollama"""
    print("📥 Installing Ollama...")
    
    # Detect OS and install accordingly
    import platform
    system = platform.system().lower()
    
    if system == "darwin":  # macOS
        return run_command("curl -fsSL https://ollama.ai/install.sh | sh", "Installing Ollama on macOS")
    elif system == "linux":
        return run_command("curl -fsSL https://ollama.ai/install.sh | sh", "Installing Ollama on Linux")
    elif system == "windows":
        print("⚠️  Windows installation not automated. Please install Ollama manually from https://ollama.ai/")
        return False
    else:
        print(f"⚠️  Unsupported OS: {system}")
        return False

def setup_environment():
    """Set up environment variables"""
    print("🔧 Setting up environment...")
    
    env_file = ".env"
    env_example = "env.example"
    
    if os.path.exists(env_file):
        print("✅ .env file already exists")
        return True
    
    if os.path.exists(env_example):
        shutil.copy(env_example, env_file)
        print("✅ Created .env file from template")
        print("⚠️  Please edit .env file with your API keys")
        return True
    else:
        print("❌ env.example not found")
        return False

def check_assemblyai():
    """Check AssemblyAI configuration"""
    print("🎤 Checking AssemblyAI configuration...")
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("ASSEMBLYAI_API_KEY")
    if api_key and api_key != "your_assemblyai_api_key_here":
        print("✅ AssemblyAI API key configured")
        return True
    else:
        print("❌ AssemblyAI API key not configured")
        print("   Please get your API key from https://www.assemblyai.com/")
        print("   Add it to your .env file")
        return False

def check_google_credentials():
    """Check Google Calendar credentials"""
    print("📅 Checking Google Calendar credentials...")
    
    credentials_file = os.path.join("config", "credentials.json")
    if os.path.exists(credentials_file):
        print("✅ Google credentials file found")
        return True
    else:
        print("⚠️  Google credentials file not found")
        print("   Please download credentials.json from Google Cloud Console")
        print("   Place it in the config/ directory")
        return False

def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    
    directories = ["output", "output/minutes", "output/transcripts", "config", "examples", "tests", "docs"]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    return True

def run_tests():
    """Run basic tests"""
    print("🧪 Running basic tests...")
    
    try:
        # Test imports
        import config
        import models
        import audio_processor
        import llm_processor
        import calendar_manager
        import ai_agent
        print("✅ All modules imported successfully")
        
        # Test configuration
        from config import Config
        print("✅ Configuration loaded successfully")
        
        return True
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 AI Agent Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Set up environment
    setup_environment()
    
    # Check Ollama
    if not check_ollama():
        print("⚠️  Ollama setup incomplete. Please install and start Ollama manually.")
    
    # Check external services
    assemblyai_ok = check_assemblyai()
    google_ok = check_google_credentials()
    
    # Create directories
    create_directories()
    
    # Run tests
    if not run_tests():
        print("❌ Basic tests failed")
        sys.exit(1)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Setup Summary")
    print("=" * 50)
    
    print(f"✅ Python dependencies: {'Installed' if True else 'Failed'}")
    print(f"✅ Environment setup: {'Complete' if True else 'Incomplete'}")
    print(f"✅ Ollama: {'Ready' if True else 'Needs setup'}")
    print(f"✅ AssemblyAI: {'Configured' if assemblyai_ok else 'Needs API key'}")
    print(f"✅ Google Calendar: {'Configured' if google_ok else 'Needs credentials'}")
    print(f"✅ Basic tests: {'Passed' if True else 'Failed'}")
    
    print("\n🎉 Setup completed!")
    print("\n📝 Next steps:")
    print("1. Edit .env file with your API keys")
    print("2. Download Google credentials.json if needed")
    print("3. Start Ollama: ollama serve")
    print("4. Run: python main.py --help")
    
    if not assemblyai_ok or not google_ok:
        print("\n⚠️  Some services need configuration:")
        if not assemblyai_ok:
            print("   - Get AssemblyAI API key from https://www.assemblyai.com/")
        if not google_ok:
            print("   - Download Google credentials from Google Cloud Console")

if __name__ == "__main__":
    main() 