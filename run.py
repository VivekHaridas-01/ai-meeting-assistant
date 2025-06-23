#!/usr/bin/env python3
"""
Entry point for AI Agent for Meeting Processing and Calendar Management

This script serves as the main entry point for the AI Agent CLI.
"""

import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import and run main
from main import main

if __name__ == "__main__":
    main() 