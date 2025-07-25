"""
Authentication Manager - Handles Spotify OAuth authentication
"""

import streamlit as st
import logging
from typing import Optional, Tuple, Dict
from .spotify_manager import SpotifyManager
from .youtube_extractor import YouTubeExtractor
from config import Config

logger = logging.getLogger(__name__)

class AuthManager:
    """Manages Spotify OAuth authentication"""
    
    def __init__(self):
        self.full_spotify = None
        self._initialize_managers()

    def _initialize_managers(self):
        """Initialize Spotify managers based on available credentials"""
        from config import Config

        # Initialize Spotify manager if credentials available
        if Config.SPOTIFY_CLIENT_ID and Config.SPOTIFY_CLIENT_SECRET:
            self.full_spotify = SpotifyManager(
                Config.SPOTIFY_CLIENT_ID,
                Config.SPOTIFY_CLIENT_SECRET,
                redirect_uri=Config.SPOTIFY_REDIRECT_URI
            )

    def get_spotify_auth_url(self) -> Optional[str]:
        """Get Spotify authorization URL"""
        if self.full_spotify:
            return self.full_spotify.get_authorization_url()
        return None

    def get_spotify_manager(self) -> Optional[SpotifyManager]:
        """Get the Spotify manager if authenticated"""
        if self.is_authenticated('full'):
            return self.full_spotify
        return None
        self.youtube = None
    

    
    def setup_full_mode(self, youtube_api_key: str, spotify_client_id: str, 
                       spotify_client_secret: str) -> Tuple[bool, str]:
        """
        Set up Full Mode with user-provided credentials
        
        Returns:
            Tuple of (success, error_message)
        """
        try:
            # Validate inputs
            if not youtube_api_key:
                return False, "YouTube API key is required"
            if not spotify_client_id:
                return False, "Spotify Client ID is required"
            if not spotify_client_secret:
                return False, "Spotify Client Secret is required"
            
            # Test YouTube API key
            youtube = YouTubeExtractor(youtube_api_key)
            if not youtube.test_api_key():
                return False, "Invalid YouTube API key"
            
            # Initialize Spotify manager
            self.full_spotify = SpotifyManager(
                spotify_client_id,
                spotify_client_secret,
                redirect_uri=self._get_redirect_uri()
            )
            
            # Store credentials in session state (temporarily)
            st.session_state.youtube_api_key = youtube_api_key
            st.session_state.spotify_client_id = spotify_client_id
            st.session_state.spotify_client_secret = spotify_client_secret
            st.session_state.youtube_manager = youtube
            st.session_state.spotify_manager = self.full_spotify
            st.session_state.auth_mode = "full"
            st.session_state.full_mode_setup = True
            
            logger.info("Full mode credentials validated")
            return True, ""
            
        except Exception as e:
            logger.error(f"Full mode setup failed: {e}")
            return False, f"Full mode setup failed: {str(e)}"
    
    def handle_spotify_oauth(self, authorization_code: str) -> Tuple[bool, str]:
        """
        Handle Spotify OAuth callback
        
        Returns:
            Tuple of (success, error_message)
        """
        try:
            if not self.full_spotify:
                return False, "Spotify manager not initialized"
            
            # Exchange code for token
            if not self.full_spotify.exchange_code_for_token(authorization_code):
                return False, "Failed to exchange authorization code for token"
            
            # Test connection
            if not self.full_spotify.test_connection():
                return False, "Spotify connection test failed"
            
            # Get user info
            user_info = self.full_spotify.get_user_info()
            if user_info:
                st.session_state.spotify_user_info = user_info
                st.session_state.spotify_user_id = user_info.get('id', '')
            
            st.session_state.spotify_authenticated = True
            
            logger.info("Spotify OAuth authentication successful")
            return True, ""
            
        except Exception as e:
            logger.error(f"Spotify OAuth failed: {e}")
            return False, f"Spotify OAuth failed: {str(e)}"
    
    def _get_redirect_uri(self) -> str:
        """Get appropriate redirect URI for current environment"""
        # In production, this would be the actual domain
        # For local development, use localhost
        return "http://localhost:8501"
    

    
    def render_full_mode_setup(self) -> bool:
        """
        Render Full Mode setup interface
        
        Returns:
            True if setup is successful
        """
        st.markdown("## Full Mode Setup")
        
        st.info("""
        **Full Mode** provides complete functionality including automatic playlist creation.
        You'll need to provide your own API credentials.
        """)
        
        # Instructions
        with st.expander("📋 How to get API credentials", expanded=False):
            st.markdown("""
            ### YouTube Data API v3 Key
            1. Go to [Google Cloud Console](https://console.cloud.google.com/)
            2. Create a new project or select existing one
            3. Enable YouTube Data API v3
            4. Create credentials (API Key)
            5. Copy the API key
            
            ### Spotify Web API Credentials
            1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/)
            2. Create a new app
            3. Add redirect URI: `http://localhost:8501`
            4. Copy Client ID and Client Secret
            """)
        
        # Credential inputs
        st.markdown("### Enter Your Credentials")
        
        youtube_api_key = st.text_input(
            "YouTube API Key",
            type="password",
            help="Your YouTube Data API v3 key"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            spotify_client_id = st.text_input(
                "Spotify Client ID",
                help="Your Spotify app's Client ID"
            )
        
        with col2:
            spotify_client_secret = st.text_input(
                "Spotify Client Secret",
                type="password",
                help="Your Spotify app's Client Secret"
            )
        
        # Setup button
        if st.button("Validate Credentials", type="primary"):
            if youtube_api_key and spotify_client_id and spotify_client_secret:
                with st.spinner("Validating credentials..."):
                    success, error = self.setup_full_mode(
                        youtube_api_key, spotify_client_id, spotify_client_secret
                    )
                    
                    if success:
                        st.success("Credentials validated successfully!")
                        st.info("Next, you'll need to authorize the app to access your Spotify account.")
                        return True
                    else:
                        st.error(f"Credential validation failed: {error}")
            else:
                st.warning("Please fill in all credential fields.")
        
        return False
    
    def render_spotify_oauth_flow(self) -> bool:
        """
        Render Spotify OAuth authorization flow
        
        Returns:
            True if authorization is successful
        """
        st.markdown("## Spotify Authorization")
        
        if 'spotify_authenticated' in st.session_state and st.session_state.spotify_authenticated:
            st.success("Spotify authorization completed!")
            return True
        
        st.info("""
        To create playlists in your Spotify account, you need to authorize this application.
        Click the button below to open Spotify's authorization page.
        """)
        
        # Generate authorization URL
        if self.full_spotify:
            auth_url = self.full_spotify.get_authorization_url()
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                if st.button("Authorize with Spotify", type="primary"):
                    st.markdown(f"[Click here to authorize]({auth_url})")
            
            with col2:
                st.markdown("After authorization, you'll be redirected to a URL starting with `http://localhost:8501`")
        
        # Handle callback
        st.markdown("### Enter Authorization Code")
        st.markdown("After authorizing, copy the `code` parameter from the redirect URL:")
        
        callback_url = st.text_input(
            "Paste the full redirect URL here:",
            placeholder="http://localhost:8501?code=AQC...",
            help="Copy the entire URL from your browser after authorization"
        )
        
        if st.button("Complete Authorization"):
            if callback_url and 'code=' in callback_url:
                try:
                    # Extract code from URL
                    code = callback_url.split('code=')[1].split('&')[0]
                    
                    with st.spinner("Completing authorization..."):
                        success, error = self.handle_spotify_oauth(code)
                        
                        if success:
                            st.success("Spotify authorization completed!")
                            st.rerun()
                        else:
                            st.error(f"Authorization failed: {error}")
                            
                except Exception as e:
                    st.error(f"Invalid callback URL: {str(e)}")
            else:
                st.warning("Please paste the complete redirect URL.")
        
        return False
    
    def is_authenticated(self, mode: str = 'full') -> bool:
        """Check if authentication is complete"""
        return (
            'spotify_manager' in st.session_state and
            'youtube_manager' in st.session_state and
            'spotify_authenticated' in st.session_state and
            st.session_state.spotify_authenticated and
            'auth_mode' in st.session_state and
            st.session_state.auth_mode == "full"
        )
    
    def clear_authentication(self):
        """Clear all authentication data"""
        keys_to_clear = [
            'spotify_manager', 'youtube_manager', 'auth_mode',
            'youtube_api_key', 'spotify_client_id', 'spotify_client_secret',
            'spotify_authenticated', 'spotify_user_info', 'spotify_user_id',
            'full_mode_setup'
        ]
        
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
