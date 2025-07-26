#!/usr/bin/env python3
"""
Youtify - YouTube to Spotify Playlist Converter
A clean, simple application for converting YouTube playlists to Spotify format.
"""

import streamlit as st
import base64
import time
import logging
from pathlib import Path

# Import UI components
from ui.header import render_header
from ui.conversion.landing import render_landing_page
from ui.processing import render_processing_page
from ui.playlist.creation import render_playlist_creation_page
from core.processor import PlaylistProcessor
from utils.session import initialize_session, get_session_state, set_session_state
from utils.proper_oauth_manager import ProperOAuthManager
from config import Config

logger = logging.getLogger(__name__)

# Configure page
st.set_page_config(
    page_title="Youtify - YouTube to Spotify Converter",
    page_icon="♪",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def load_css():
    """Load custom CSS styling"""
    css_file = Path("styles/main.css")
    if css_file.exists():
        with open(css_file) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def get_logo_base64():
    """Get logo as base64 string"""
    try:
        with open("logo.png", "rb") as f:
            return base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        return ""

def handle_oauth_callback():
    """Handle Spotify OAuth callback if code parameter is present"""
    try:
        # Check for authorization code in URL parameters
        query_params = st.query_params

        # Handle OAuth success callback
        if 'code' in query_params:
            auth_code = query_params['code']
            state_param = query_params.get('state', '')

            # Initialize OAuth manager if not present
            if 'oauth_manager' not in st.session_state:
                st.session_state.oauth_manager = ProperOAuthManager()

            # Show processing message
            st.info("🔄 Completing Spotify authentication...")

            # Handle the OAuth callback
            success = st.session_state.oauth_manager.handle_oauth_callback(auth_code, state_param)

            if success:
                st.success("✅ Authentication successful!")
                
                # Check if user had pending playlist creation
                if get_session_state('pending_playlist_creation', False):
                    set_session_state('pending_playlist_creation', False)
                    set_session_state('app_state', 'playlist_creation')
                else:
                    # Check if they have existing results
                    existing_results = get_session_state('results', [])
                    if existing_results:
                        set_session_state('app_state', 'playlist_creation')
                    else:
                        set_session_state('app_state', 'landing')

                # Clear URL parameters
                st.query_params.clear()
                st.rerun()
            else:
                st.error("❌ Authentication failed. Please try again.")
                st.query_params.clear()
                set_session_state('app_state', 'landing')
                st.rerun()

        # Handle OAuth error callback
        elif 'error' in query_params:
            error_type = query_params.get('error', 'unknown_error')
            st.error(f"❌ Spotify authorization failed: {error_type}")
            
            if error_type == 'access_denied':
                st.info("You need to authorize the app to create playlists.")
            
            st.query_params.clear()
            set_session_state('app_state', 'landing')
            st.rerun()

    except Exception as e:
        logger.error(f"OAuth callback error: {e}")
        st.error(f"❌ Error handling authentication: {str(e)}")
        st.query_params.clear()
        set_session_state('app_state', 'landing')
        st.rerun()

def main():
    """Main application entry point"""
    # Load styling
    load_css()

    # Initialize session
    initialize_session()

    # Check for debug parameter to clear session state
    query_params = st.query_params
    if 'clear_session' in query_params:
        st.session_state.clear()
        st.query_params.clear()
        st.success("Session state cleared! Please refresh the page.")
        st.stop()

    # Handle OAuth callback first
    handle_oauth_callback()

    # Initialize OAuth manager
    if 'oauth_manager' not in st.session_state:
        st.session_state.oauth_manager = ProperOAuthManager()

    # Render header with logo
    render_header(get_logo_base64())

    # Get current state
    current_state = get_session_state('app_state', 'landing')

    # Route to appropriate page based on state
    if current_state == 'landing':
        # Landing page - input YouTube URL and integrated authentication
        youtube_url = render_landing_page(st.session_state.oauth_manager)

        if youtube_url:
            # User clicked convert - but stay on landing page and handle conversion there
            set_session_state('youtube_url', youtube_url)
            set_session_state('start_conversion', True)
            st.rerun()



    elif current_state == 'processing':
        # Legacy processing page (kept for compatibility)
        processor = PlaylistProcessor()
        results = render_processing_page(processor)

        if results:
            # Processing complete - go directly to playlist creation
            set_session_state('results', results)
            set_session_state('app_state', 'playlist_creation')
            st.rerun()

    elif current_state == 'playlist_creation':
        # Playlist creation page - requires Spotify authentication
        oauth_manager = st.session_state.oauth_manager

        if not oauth_manager.is_authenticated():
            # User needs to authenticate for playlist creation
            st.markdown("# Create Spotify Playlist")
            st.info("🔐 Spotify authentication is required to create playlists.")

            # Show authentication options
            oauth_manager.render_auth_interface()

            # Back button
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("Convert Another"):
                    from ui.conversion.preview import _reset_conversion_state
                    _reset_conversion_state()
                    st.rerun()
        else:
            # User is authenticated, show playlist creation
            playlist_result = render_playlist_creation_page(
                get_session_state('results', []),
                oauth_manager
            )

            # Note: All navigation is now handled within the playlist creation page itself

if __name__ == "__main__":
    main()
