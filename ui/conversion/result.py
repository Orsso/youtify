"""
Conversion Result Components
"""
import streamlit as st
import io
import csv
from typing import List, Dict
from utils.session import get_session_state, set_session_state
from ui.conversion.preview import _reset_conversion_state

def _render_post_conversion_buttons(oauth_manager):
    """Render action buttons after conversion is complete"""
    found_songs = [r for r in get_session_state('results', []) if r and r.get('found', False)]
    
    if found_songs:
        if oauth_manager and oauth_manager.is_authenticated():
            # User is authenticated - show create playlist button
            if st.button("Create Spotify Playlist", type="primary"):
                set_session_state('app_state', 'playlist_creation')
                st.rerun()
        else:
            # User is not authenticated - show centered Import to Spotify button
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if oauth_manager:
                    oauth_manager.render_auth_button("Import to Spotify")
    else:
        # No songs found - show convert another option
        st.warning("No songs could be matched on Spotify")
        if st.button("Convert Another Playlist", type="primary"):
            _reset_conversion_state()
            st.rerun()

def generate_csv_report(results: List[Dict]) -> str:
    """Generate CSV report of results"""
    import io
    import csv
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow([
        'Index', 'Original Title', 'Original Channel', 
        'Spotify Artist', 'Spotify Title', 'Confidence', 
        'Status', 'Spotify URI'
    ])
    
    # Data
    for i, song in enumerate(results, 1):
        writer.writerow([
            i,
            song.get('original_title', ''),
            song.get('channel_name', ''),
            song.get('spotify_artist', '') if song.get('found') else '',
            song.get('spotify_title', '') if song.get('found') else '',
            f"{song.get('confidence', 0.0):.2f}" if song.get('found') else '',
            'Found' if song.get('found') else 'Not Found',
            song.get('spotify_uri', '') if song.get('found') else ''
        ])
    
    return output.getvalue()