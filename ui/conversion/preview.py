"""
Playlist Preview and Conversion Components
"""
import streamlit as st
from typing import Dict
from utils.session import get_session_state, set_session_state

def _render_playlist_preview(details: Dict, song_count: int):
    """Render clean, centered playlist preview card that can be updated during conversion"""
    # Create a centered container
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        # Create an updateable container and store it in session state
        playlist_card_container = st.empty()
        set_session_state('playlist_card_container', playlist_card_container)
        # Store playlist details for later use
        set_session_state('playlist_details', details)
        
        # Check if conversion is completed and render appropriate state
        if get_session_state('conversion_completed', False):
            results = get_session_state('results', [])
            found_songs = [r for r in results if r and r.get('found', False)]
            _update_playlist_card(playlist_card_container, details, "completed", len(found_songs), song_count)
        elif get_session_state('conversion_active', False):
            # During conversion - show breathing animation
            _update_playlist_card(playlist_card_container, details, "converting", 0, song_count)
        else:
            # Render initial state
            _update_playlist_card(playlist_card_container, details, "ready", song_count, song_count)

def _render_playlist_preview_completed(details: Dict):
    """Render the completed playlist preview with green contouring"""
    # Create a centered container
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        # Get the results to show found count
        results = get_session_state('results', [])
        found_songs = [r for r in results if r and r.get('found', False)]
        
        # Create the completed playlist card directly
        thumbnail_url = details.get('thumbnail', '')
        title = details['title']
        
        st.markdown(f"""
        <div id="playlist-card" style="
            background: rgba(29, 185, 84, 0.1);
            backdrop-filter: blur(10px);
            border: 2px solid #1DB954;
            border-radius: 16px;
            padding: 2rem;
            text-align: center;
            box-shadow: 0 8px 32px rgba(29, 185, 84, 0.4);
            margin: 1rem 0;
        ">
            <div style="display: flex; justify-content: center; margin-bottom: 1rem;">
                <img src="{thumbnail_url}" width="100" style="border-radius: 8px;" />
            </div>
            <h3 style="text-align: center; margin: 1rem 0 0.5rem 0; color: #ffffff;">{title}</h3>
            <p style="text-align: center; margin: 0.5rem 0; color: #cccccc;"><strong>{len(found_songs)} songs</strong> are ready to be added to your Spotify account</p>
        </div>
        """, unsafe_allow_html=True)

def _update_playlist_card(container, details: Dict, status: str, found_count: int, total_count: int):
    """Update the playlist card with different visual states"""
    thumbnail_url = details.get('thumbnail', '')
    title = details['title']
    channel = details['channel']
    
    if status == "ready":
        # Initial ready state
        with container:
            st.markdown(f"""
            <div id="playlist-card" style="
                background: rgba(255, 107, 53, 0.1);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 107, 53, 0.2);
                border-radius: 16px;
                padding: 2rem;
                text-align: center;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                margin: 1rem 0;
            ">
                <div style="display: flex; justify-content: center; margin-bottom: 1rem;">
                    <img src="{thumbnail_url}" width="100" style="border-radius: 8px;" />
                </div>
                <h3 style="text-align: center; margin: 1rem 0 0.5rem 0; color: #ffffff;">{title}</h3>
                <p style="text-align: center; margin: 0.5rem 0; color: #cccccc;"><strong>{total_count} songs</strong> • {channel}</p>
                <p style="text-align: center; margin: 1rem 0 0.5rem 0; color: #4CAF50;">Ready to convert</p>
            </div>
            """, unsafe_allow_html=True)
    
    elif status == "converting":
        # During conversion - breathing animation
        with container:
            st.markdown(f"""
            <div id="playlist-card" style="
                background: rgba(255, 107, 53, 0.1);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 107, 53, 0.2);
                border-radius: 16px;
                padding: 2rem;
                text-align: center;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                margin: 1rem 0;
                animation: breathe 2s ease-in-out infinite;
            ">
                <div style="display: flex; justify-content: center; margin-bottom: 1rem;">
                    <img src="{thumbnail_url}" width="100" style="border-radius: 8px;" />
                </div>
                <h3 style="text-align: center; margin: 1rem 0 0.5rem 0; color: #ffffff;">{title}</h3>
                <p style="text-align: center; margin: 0.5rem 0; color: #cccccc;"><strong>{total_count} songs</strong> • {channel}</p>
                <p style="text-align: center; margin: 1rem 0 0.5rem 0; color: #FF6B35;">Converting</p>
            </div>
            <style>
            @keyframes breathe {{
                0%, 100% {{ transform: scale(1); opacity: 0.8; }}
                50% {{ transform: scale(1.02); opacity: 1; }}
            }}
            </style>
            """, unsafe_allow_html=True)
    
    elif status == "completed":
        # After completion - green contouring
        with container:
            st.markdown(f"""
            <div id="playlist-card" style="
                background: rgba(29, 185, 84, 0.1);
                backdrop-filter: blur(10px);
                border: 2px solid #1DB954;
                border-radius: 16px;
                padding: 2rem;
                text-align: center;
                box-shadow: 0 8px 32px rgba(29, 185, 84, 0.4);
                margin: 1rem 0;
            ">
                <div style="display: flex; justify-content: center; margin-bottom: 1rem;">
                    <img src="{thumbnail_url}" width="100" style="border-radius: 8px;" />
                </div>
                <h3 style="text-align: center; margin: 1rem 0 0.5rem 0; color: #ffffff;">{title}</h3>
                <p style="text-align: center; margin: 0.5rem 0; color: #cccccc;"><strong>{found_count} songs</strong> are ready to be added to your Spotify account</p>
            </div>
            """, unsafe_allow_html=True)

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

def _reset_conversion_state():
    """Reset all conversion-related state"""
    set_session_state('start_conversion', False)
    set_session_state('conversion_active', False)
    set_session_state('conversion_completed', False)
    set_session_state('convert_button_clicked', False)  # Reset button clicked flag
    set_session_state('youtube_url', '')
    set_session_state('cached_playlist_url', '')
    if 'conversion_state' in st.session_state:
        del st.session_state.conversion_state
    if 'playlist_data' in st.session_state:
        del st.session_state.playlist_data
    if 'results' in st.session_state:
        del st.session_state.results