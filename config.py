"""
Configuration settings for Youtify - YouTube to Spotify Converter
"""

import streamlit as st
from typing import Optional

class Config:
    """Application configuration using Streamlit secrets"""

    # App metadata
    APP_NAME = "Youtify"
    APP_VERSION = "2.0.0"
    APP_DESCRIPTION = "Convert YouTube playlists to Spotify format"

    @staticmethod
    def validate_secrets():
        """Validate that all required secrets are present"""
        required_secrets = [
            "spotify.client_id",
            "spotify.client_secret",
            "youtube.api_key"
        ]

        missing_secrets = [
            secret for secret in required_secrets
            if not st.secrets.get(secret)
        ]

        if missing_secrets:
            st.error(f"Missing required secrets: {', '.join(missing_secrets)}")
            st.stop()


    # Required API Configuration
    YOUTUBE_API_KEY: str = st.secrets["youtube"]["api_key"]
    SPOTIFY_CLIENT_ID: str = st.secrets["spotify"]["client_id"]
    SPOTIFY_CLIENT_SECRET: str = st.secrets["spotify"]["client_secret"]
    SPOTIFY_REDIRECT_URI = "http://127.0.0.1:8501"

    # Processing Settings
    PROCESSING_DELAY_MS = 100
    LOW_CONFIDENCE_THRESHOLD = 0.3

# Streamlit page configuration
STREAMLIT_CONFIG = {
    'page_title': Config.APP_NAME,
    'page_icon': '♪',
    'layout': 'wide',
    'initial_sidebar_state': 'collapsed'
}