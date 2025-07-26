"""
Playlist Creation Components
"""
import streamlit as st
import logging
from typing import List, Dict, Optional
from utils.proper_oauth_manager import ProperOAuthManager
from utils.session import get_session_state, set_session_state
from config import Config
from ..conversion.preview import _reset_conversion_state

logger = logging.getLogger(__name__)

def render_playlist_creation_page(results: List[Dict], oauth_manager) -> Optional[str]:
    """Render the playlist creation page"""
    
    # Check if playlist was just created and show success feedback
    if st.session_state.get('playlist_created', False):
        playlist_name = st.session_state.get('created_playlist_name', 'Your Playlist')
        playlist_id = st.session_state.get('created_playlist_id', '')
        track_count = st.session_state.get('created_playlist_track_count', 0)
        
        # Show success message with clear visual feedback
        st.success(f"🎉 **Playlist Created Successfully!**")
        
        # Create a prominent success card
        playlist_url = f"https://open.spotify.com/playlist/{playlist_id}"
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #1DB954 0%, #1ed760 100%);
            padding: 2rem;
            border-radius: 16px;
            text-align: center;
            margin: 1rem 0 2rem 0;
            box-shadow: 0 8px 32px rgba(29, 185, 84, 0.3);
        ">
            <h2 style="color: white; margin: 0 0 1rem 0;">
                <div style="display: inline-flex; align-items: center; gap: 0.5rem;">
                    <div class="success-icon"></div>
                    {playlist_name}
                </div>
            </h2>
            <p style="color: rgba(255,255,255,0.9); margin: 0 0 1.5rem 0; font-size: 1.1rem;">
                {track_count} songs added successfully
            </p>
            <a href="{playlist_url}" target="_blank" style="
                display: inline-block;
                background: rgba(255,255,255,0.2);
                color: white;
                padding: 0.75rem 2rem;
                border-radius: 25px;
                text-decoration: none;
                font-weight: 500;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255,255,255,0.3);
                transition: all 0.3s ease;
            ">
                <div style="display: inline-flex; align-items: center; gap: 0.5rem;">
                    <div class="spotify-icon"></div>
                    Open in Spotify
                </div>
            </a>
        </div>
        """, unsafe_allow_html=True)
        
        # Action buttons after success
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col2:
            if st.button("Convert Another YouTube Playlist", type="primary"):
                # Clear all state and go back to landing
                st.session_state.playlist_created = False
                if 'created_playlist_name' in st.session_state:
                    del st.session_state.created_playlist_name
                if 'created_playlist_id' in st.session_state:
                    del st.session_state.created_playlist_id
                if 'created_playlist_track_count' in st.session_state:
                    del st.session_state.created_playlist_track_count
                _reset_conversion_state()
                st.rerun()
        
        return None  # Stay on this page
    
    st.markdown("## Create Spotify Playlist")

    # Filter successful matches and failed matches
    successful_matches = [r for r in results if r.get('found', False)]
    failed_matches = [r for r in results if not r.get('found', False)]
    total_songs = len(results)

    if not successful_matches:
        st.warning("No successful matches found. Cannot create playlist.")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Convert Another"):
                _reset_conversion_state()
                st.rerun()
        return None

    # Conversion Summary Section
    st.markdown("### Conversion Summary")
    
    # Create summary statistics with glassmorphism cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div style="
            background: var(--glass-bg);
            backdrop-filter: var(--glass-backdrop);
            border: 1px solid var(--glass-border);
            border-radius: var(--border-radius);
            padding: 1.5rem;
            text-align: center;
            box-shadow: var(--glass-shadow);
            margin: 0.5rem 0;
        ">
            <div style="font-size: 2rem; font-weight: 600; color: var(--text-primary); margin-bottom: 0.5rem;">
                {total_songs}
            </div>
            <div style="color: var(--text-secondary); font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.5px;">
                Total Songs
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        success_rate = (len(successful_matches) / total_songs * 100) if total_songs > 0 else 0
        st.markdown(f"""
        <div style="
            background: rgba(76, 175, 80, 0.1);
            backdrop-filter: var(--glass-backdrop);
            border: 1px solid rgba(76, 175, 80, 0.3);
            border-radius: var(--border-radius);
            padding: 1.5rem;
            text-align: center;
            box-shadow: var(--glass-shadow);
            margin: 0.5rem 0;
        ">
            <div style="font-size: 2rem; font-weight: 600; color: #4CAF50; margin-bottom: 0.5rem;">
                {len(successful_matches)}
            </div>
            <div style="color: var(--text-secondary); font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.5px;">
                Matched ({success_rate:.1f}%)
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="
            background: rgba(255, 68, 68, 0.1);
            backdrop-filter: var(--glass-backdrop);
            border: 1px solid rgba(255, 68, 68, 0.3);
            border-radius: var(--border-radius);
            padding: 1.5rem;
            text-align: center;
            box-shadow: var(--glass-shadow);
            margin: 0.5rem 0;
        ">
            <div style="font-size: 2rem; font-weight: 600; color: #FF4444; margin-bottom: 0.5rem;">
                {len(failed_matches)}
            </div>
            <div style="color: var(--text-secondary); font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.5px;">
                Missed
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"**{len(successful_matches)}** songs will be added to your playlist")

    # Playlist configuration
    col1, col2 = st.columns(2)

    with col1:
        # Get original playlist title for better default naming
        playlist_data = get_session_state('playlist_data', {})
        original_title = playlist_data.get('details', {}).get('title', 'YouTube Playlist')
        
        # Create a cleaner default name
        default_name = f"{original_title} (Spotify)"
        
        playlist_name = st.text_input(
            "Playlist Name",
            value=default_name,
            help="Name for your new Spotify playlist"
        )

    with col2:
        playlist_public = st.checkbox(
            "Make playlist public",
            value=False,
            help="Whether the playlist should be visible to other Spotify users"
        )

    playlist_description = st.text_area(
        "Description (optional)",
        value="Created with Youtify - YouTube to Spotify converter",
        help="Description for your playlist"
    )

    # Create playlist button
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        if st.button("Create Playlist", type="primary"):
            if not playlist_name.strip():
                st.error("Please enter a playlist name")
                return None

            # Create the playlist using the OAuth manager
            try:
                with st.spinner("Creating playlist..."):
                    # Get access token from OAuth manager
                    access_token = oauth_manager.get_access_token()
                    if not access_token:
                        st.error("Authentication token not available. Please try reconnecting.")
                        return None

                    # Create Spotify manager with the access token
                    from utils.spotify_manager import SpotifyManager
                    spotify_manager = SpotifyManager(
                        Config.SPOTIFY_CLIENT_ID,
                        Config.SPOTIFY_CLIENT_SECRET
                    )
                    
                    # Set the access token and token type for OAuth flow
                    spotify_manager.access_token = access_token
                    spotify_manager.token_type = "authorization_code"  # Required for user operations

                    # Get user info
                    user_info = spotify_manager.get_user_info()
                    if not user_info:
                        st.error("Failed to get user information from Spotify")
                        return None

                    user_id = user_info.get('id')
                    if not user_id:
                        st.error("Could not determine Spotify user ID")
                        return None

                    # Set the user_id in the manager
                    spotify_manager.user_id = user_id

                    # Create the playlist
                    playlist_id = spotify_manager.create_playlist(
                        name=playlist_name,
                        description=playlist_description,
                        public=playlist_public
                    )

                    if not playlist_id:
                        st.error("Failed to create playlist")
                        return None

                    # Add tracks to playlist
                    track_uris = [song.get('spotify_uri') for song in successful_matches if song.get('spotify_uri')]
                    # Filter out any None values
                    valid_track_uris = [uri for uri in track_uris if uri is not None]
                    
                    if valid_track_uris:
                        success = spotify_manager.add_tracks_to_playlist(playlist_id, valid_track_uris)
                        if success:
                            # Store success state
                            st.session_state.playlist_created = True
                            st.session_state.created_playlist_name = playlist_name
                            st.session_state.created_playlist_id = playlist_id
                            st.session_state.created_playlist_track_count = len(valid_track_uris)
                            st.rerun()
                        else:
                            st.error("Playlist created but failed to add some tracks")
                    else:
                        st.error("No valid track URIs found")

            except Exception as e:
                st.error(f"Error creating playlist: {str(e)}")
                logger.error(f"Playlist creation error: {e}")

    return None