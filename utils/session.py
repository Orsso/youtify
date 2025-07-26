"""
Session Management - Clean session state handling
"""

import streamlit as st
import time

def initialize_session():
    """Initialize session state with default values"""
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        st.session_state.app_state = 'landing'  # landing, authentication, processing, results, playlist_creation
        st.session_state.youtube_url = ''
        st.session_state.results = []
        st.session_state.processing_progress = 0
        st.session_state.current_song = ''
        st.session_state.session_id = f"session_{int(time.time())}"

        # OAuth state management
        st.session_state.spotify_oauth_in_progress = False
        st.session_state.spotify_oauth_completed = False
        st.session_state.pending_conversion = False
        st.session_state.pending_playlist_creation = False
        st.session_state.spotify_authenticated = False

def backup_session_data():
    """Backup critical session data before OAuth redirect"""
    backup_data = {
        'results': get_session_state('results', []),
        'playlist_data': get_session_state('playlist_data', None),
        'youtube_url': get_session_state('youtube_url', ''),
        'app_state': get_session_state('app_state', 'landing'),
        'conversion_state': get_session_state('conversion_state', None),
        'timestamp': int(time.time())
    }
    
    # Store backup in session state with a special key
    st.session_state.oauth_backup = backup_data
    return backup_data

def restore_session_data():
    """Restore session data after OAuth redirect"""
    if 'oauth_backup' in st.session_state:
        backup_data = st.session_state.oauth_backup
        
        # Restore critical data
        if backup_data.get('results'):
            set_session_state('results', backup_data['results'])
        if backup_data.get('playlist_data'):
            set_session_state('playlist_data', backup_data['playlist_data'])
        if backup_data.get('youtube_url'):
            set_session_state('youtube_url', backup_data['youtube_url'])
        if backup_data.get('conversion_state'):
            set_session_state('conversion_state', backup_data['conversion_state'])
            
        # Clean up backup
        del st.session_state.oauth_backup
        return True
    return False

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
        'processing_progress', 'current_song',
        'spotify_oauth_in_progress', 'spotify_oauth_completed', 'pending_conversion', 'pending_playlist_creation'
    ]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]

    # Reset to initial state
    st.session_state.app_state = 'landing'
    st.session_state.youtube_url = ''
    st.session_state.results = []
    st.session_state.spotify_oauth_in_progress = False
    st.session_state.spotify_oauth_completed = False
    st.session_state.pending_conversion = False
    st.session_state.pending_playlist_creation = False
