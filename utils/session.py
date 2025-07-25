"""
Session Management - Clean session state handling
"""

import streamlit as st
import time

def initialize_session():
    """Initialize session state with default values"""
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        st.session_state.app_state = 'landing'  # landing, processing, results
        st.session_state.youtube_url = ''
        st.session_state.results = []
        st.session_state.processing_progress = 0
        st.session_state.current_song = ''
        st.session_state.session_id = f"session_{int(time.time())}"

def get_session_state(key, default=None):
    """Get a value from session state"""
    return st.session_state.get(key, default)

def set_session_state(key, value):
    """Set a value in session state"""
    st.session_state[key] = value

def clear_session():
    """Clear all session data"""
    keys_to_clear = [
        'app_state', 'youtube_url', 'results', 
        'processing_progress', 'current_song'
    ]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    
    # Reset to initial state
    st.session_state.app_state = 'landing'
    st.session_state.youtube_url = ''
    st.session_state.results = []
