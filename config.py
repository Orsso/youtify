"""
Configuration settings for Youtify - YouTube to Spotify Converter
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration - only contains actively used settings"""
    
    # App metadata
    APP_NAME = "Youtify"
    APP_VERSION = "2.0.0"
    APP_DESCRIPTION = "Convert YouTube playlists to Spotify format"
    
    # Required API Configuration
    YOUTUBE_API_KEY: Optional[str] = os.getenv('YOUTUBE_API_KEY')
    SPOTIFY_CLIENT_ID: Optional[str] = os.getenv('SPOTIFY_CLIENT_ID')
    SPOTIFY_CLIENT_SECRET: Optional[str] = os.getenv('SPOTIFY_CLIENT_SECRET')
    SPOTIFY_REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI', 'http://127.0.0.1:8501')
    
    # Processing Settings
    PROCESSING_DELAY_MS = int(os.getenv('PROCESSING_DELAY_MS', '100'))
    LOW_CONFIDENCE_THRESHOLD = float(os.getenv('LOW_CONFIDENCE_THRESHOLD', '0.3'))

# Streamlit page configuration
STREAMLIT_CONFIG = {
    'page_title': Config.APP_NAME,
    'page_icon': '♪',
    'layout': 'wide',
    'initial_sidebar_state': 'collapsed'
}