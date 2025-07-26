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
    
    # Spotify Redirect URI - configurable via secrets or auto-detected
    # Auto-detect the app's base URL for development environments
    try:
        # For Streamlit >= 1.31.0, we can use st.context.url
        import urllib.parse
        context_url = st.context.url
        # Log the context URL for debugging
        print(f"DEBUG: st.context.url = {context_url}")
        if context_url:
            # Get the base URL by removing any path/query parameters
            parsed_url = urllib.parse.urlparse(context_url)
            # Use 127.0.0.1 instead of localhost for consistency with Spotify app configuration
            if parsed_url.hostname in ['localhost', '127.0.0.1']:
                base_url = f"{parsed_url.scheme}://127.0.0.1:{parsed_url.port}/"
            else:
                base_url = f"{parsed_url.scheme}://{parsed_url.netloc}/"
            
            # Check if this is a localhost URL (development environment)
            if parsed_url.hostname in ['localhost', '127.0.0.1']:
                # Use auto-detected localhost URL for development
                SPOTIFY_REDIRECT_URI: str = base_url
                print(f"DEBUG: Using detected localhost URL: {base_url}")
            else:
                # For production environments, check if a redirect_uri is configured
                if "spotify" in st.secrets and "redirect_uri" in st.secrets["spotify"]:
                    configured_uri = st.secrets["spotify"]["redirect_uri"]
                    # Validate that the configured URI matches the detected domain
                    configured_parsed = urllib.parse.urlparse(configured_uri)
                    if configured_parsed.hostname == parsed_url.hostname:
                        SPOTIFY_REDIRECT_URI: str = configured_uri
                        print(f"DEBUG: Using configured production redirect URI: {configured_uri}")
                    else:
                        # Fallback to auto-detected URL if configured URI doesn't match
                        SPOTIFY_REDIRECT_URI: str = base_url
                        print(f"DEBUG: Configured URI doesn't match domain, using detected URL: {base_url}")
                else:
                    # No configured URI, use auto-detected URL
                    SPOTIFY_REDIRECT_URI: str = base_url
                    print(f"DEBUG: Using detected production URL: {base_url}")
        else:
            # Fallback to localhost for development - use the actual server port
            try:
                # Try to get the actual server port from Streamlit config
                import streamlit.config
                port = streamlit.config.get_option("server.port") or 8501
                SPOTIFY_REDIRECT_URI: str = f"http://127.0.0.1:{port}/"
                print(f"DEBUG: st.context.url is None, using localhost with port {port}")
            except:
                # Final fallback to default port
                SPOTIFY_REDIRECT_URI: str = "http://127.0.0.1:8501/"
                print("DEBUG: st.context.url is None, using localhost fallback with default port")
    except Exception as e:
        # Fallback to localhost for development - use the actual server port
        try:
            # Try to get the actual server port from Streamlit config
            import streamlit.config
            port = streamlit.config.get_option("server.port") or 8501
            SPOTIFY_REDIRECT_URI: str = f"http://127.0.0.1:{port}/"
            print(f"DEBUG: Exception in redirect URI detection: {e}, using localhost with port {port}")
        except:
            # Final fallback to default port
            SPOTIFY_REDIRECT_URI: str = "http://127.0.0.1:8501/"
            print(f"DEBUG: Exception in redirect URI detection: {e}, using localhost fallback with default port")

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