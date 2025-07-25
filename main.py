#!/usr/bin/env python3
"""
Youtify - YouTube to Spotify Playlist Converter
A clean, simple application for converting YouTube playlists to Spotify format.
"""

import streamlit as st
import base64
from pathlib import Path

# Import our clean modules
from ui.components import (
    render_header, render_landing_page, render_processing_page,
    render_results_page, render_authentication_page, render_playlist_creation_page
)
from core.processor import PlaylistProcessor
from utils.session import initialize_session, get_session_state, set_session_state
from utils.auth_manager import AuthManager
from config import Config

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

def main():
    """Main application entry point"""
    # Load styling
    load_css()

    # Initialize session
    initialize_session()

    # Initialize auth manager
    if 'auth_manager' not in st.session_state:
        st.session_state.auth_manager = AuthManager()

    # Render header with logo
    render_header(get_logo_base64())

    # Get current state
    current_state = get_session_state('app_state', 'landing')

    # Route to appropriate page based on state
    if current_state == 'landing':
        # Landing page - input YouTube URL and authentication
        youtube_url = render_landing_page()

        if youtube_url:
            # Check if we need authentication
            if not st.session_state.auth_manager.is_authenticated('full'):
                set_session_state('youtube_url', youtube_url)
                set_session_state('app_state', 'authentication')
                st.rerun()
            else:
                # Start processing
                set_session_state('youtube_url', youtube_url)
                set_session_state('app_state', 'processing')
                st.rerun()

    elif current_state == 'authentication':
        # Authentication page - handle Spotify OAuth
        auth_result = render_authentication_page(st.session_state.auth_manager)

        if auth_result == 'authenticated':
            set_session_state('app_state', 'processing')
            st.rerun()
        elif auth_result == 'back':
            set_session_state('app_state', 'landing')
            st.rerun()

    elif current_state == 'processing':
        # Processing page - show progress
        processor = PlaylistProcessor()
        results = render_processing_page(processor)

        if results:
            # Processing complete
            set_session_state('results', results)
            set_session_state('app_state', 'results')
            st.rerun()

    elif current_state == 'results':
        # Results page - show converted songs
        results = get_session_state('results', [])
        action = render_results_page(results)

        if action == 'create_playlist':
            set_session_state('app_state', 'playlist_creation')
            st.rerun()
        elif action == 'new_conversion':
            # Start over
            set_session_state('app_state', 'landing')
            set_session_state('youtube_url', '')
            set_session_state('results', [])
            st.rerun()

    elif current_state == 'playlist_creation':
        # Playlist creation page
        playlist_result = render_playlist_creation_page(
            get_session_state('results', []),
            st.session_state.auth_manager
        )

        if playlist_result == 'success':
            st.success("Playlist created successfully!")
            set_session_state('app_state', 'results')
            st.rerun()
        elif playlist_result == 'back':
            set_session_state('app_state', 'results')
            st.rerun()

if __name__ == "__main__":
    main()
