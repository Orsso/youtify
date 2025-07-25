"""
UI Components - Clean, reusable UI components
"""

import streamlit as st
import time
import csv
import io
from typing import List, Dict, Optional
from utils.auth_manager import AuthManager
from config import Config

def render_header(logo_base64: str):
    """Render the application header with logo"""
    if logo_base64:
        st.markdown(f"""
        <div class="main-header">
            <div class="logo-container">
                <img src="data:image/png;base64,{logo_base64}" class="logo" alt="Youtify Logo">
                <div>
                    <h1>Youtify</h1>
                    <p>Convert YouTube playlists to Spotify format</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="main-header">
            <div class="logo-container">
                <div>
                    <h1>Youtify</h1>
                    <p>Convert YouTube playlists to Spotify format</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def render_landing_page() -> Optional[str]:
    """Render the landing page and return YouTube URL if provided"""
    st.markdown("""
    <div class="landing-container">
        <h1 class="landing-title">Convert YouTube Playlists to Spotify</h1>
        <p class="landing-subtitle">
            Transform your favorite YouTube playlists into Spotify format with intelligent song matching.
            Simply paste a YouTube playlist URL below.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # URL input
    youtube_url = st.text_input(
        "YouTube Playlist URL",
        placeholder="https://www.youtube.com/playlist?list=...",
        key="youtube_url_input",
        label_visibility="collapsed"
    )
    
    # Convert button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Convert Playlist", type="primary", use_container_width=True):
            if youtube_url.strip():
                return youtube_url.strip()
            else:
                st.error("Please enter a valid YouTube playlist URL")
    
    # Help text
    st.markdown("""
    <div style="text-align: center; margin-top: 2rem; color: var(--text-secondary); font-size: 0.9rem;">
        <p>Paste any public YouTube playlist URL to get started.<br>
        We'll find matching songs on Spotify and show you the results.</p>
    </div>
    """, unsafe_allow_html=True)
    
    return None

def render_processing_page(processor) -> Optional[List[Dict]]:
    """Render the processing page and return results when complete"""
    st.markdown("""
    <div class="processing-container">
        <h2>Converting Your Playlist</h2>
        <p>Please wait while we match your YouTube songs with Spotify tracks...</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Show current URL being processed
    youtube_url = st.session_state.get('youtube_url', '')
    if youtube_url:
        st.markdown(f"""
        <div style="background: var(--background-secondary); padding: 1rem; border-radius: 8px; margin: 1rem 0;">
            <strong>Processing:</strong> {youtube_url}
        </div>
        """, unsafe_allow_html=True)
    
    # Progress container
    progress_container = st.empty()
    status_container = st.empty()
    
    # Start processing if not already started
    if 'processing_started' not in st.session_state:
        st.session_state.processing_started = True
        
        # Process the playlist
        try:
            results = processor.process_playlist(
                youtube_url,
                progress_callback=lambda current, total, song: update_progress(
                    progress_container, status_container, current, total, song
                )
            )
            
            # Processing complete
            del st.session_state.processing_started
            return results
            
        except Exception as e:
            st.error(f"Error processing playlist: {str(e)}")
            if st.button("Try Again"):
                if 'processing_started' in st.session_state:
                    del st.session_state.processing_started
                st.rerun()
    
    return None

def update_progress(progress_container, status_container, current: int, total: int, current_song: str):
    """Update the progress display"""
    progress_percent = (current / total * 100) if total > 0 else 0
    
    with progress_container:
        st.markdown(f"""
        <div class="progress-bar-container">
            <div class="progress-bar">
                <div class="progress-fill" style="width: {progress_percent}%"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with status_container:
        st.markdown(f"""
        <div class="current-song">{current_song}</div>
        <div style="text-align: center; margin-top: 0.5rem; color: var(--text-secondary);">
            {current} of {total} songs processed
        </div>
        """, unsafe_allow_html=True)

def render_results_page(results: List[Dict]) -> Optional[str]:
    """Render the results page and return action if any"""
    st.markdown("## Conversion Results")
    
    if not results:
        st.warning("No results to display.")
        if st.button("Start New Conversion"):
            return 'new_conversion'
        return None
    
    # Summary stats
    total_songs = len(results)
    found_songs = len([r for r in results if r.get('found', False)])
    success_rate = (found_songs / total_songs * 100) if total_songs > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Songs", total_songs)
    with col2:
        st.metric("Found on Spotify", found_songs)
    with col3:
        st.metric("Success Rate", f"{success_rate:.1f}%")
    
    # Results grid
    st.markdown("### Song Matches")
    
    for i, song in enumerate(results, 1):
        render_song_card(song, i)
    
    # Action buttons
    st.markdown("---")

    # Check if we can create playlists
    successful_matches = [r for r in results if r.get('found', False)]
    can_create_playlist = len(successful_matches) > 0

    if can_create_playlist:
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button("🎵 Create Playlist", type="primary"):
                return 'create_playlist'
    else:
        col1, col2, col3 = st.columns(3)

    with col2 if can_create_playlist else col1:
        if st.button("Download CSV Report"):
            csv_data = generate_csv_report(results)
            st.download_button(
                label="Download",
                data=csv_data,
                file_name=f"youtify_results_{int(time.time())}.csv",
                mime="text/csv"
            )

    with col3 if can_create_playlist else col2:
        if st.button("Copy Spotify URIs"):
            uris = [r.get('spotify_uri', '') for r in results if r.get('found', False)]
            if uris:
                uri_text = "\n".join(uris)
                st.text_area("Spotify URIs:", uri_text, height=200)
            else:
                st.warning("No Spotify URIs available")

    with col4 if can_create_playlist else col3:
        if st.button("Start New Conversion"):
            return 'new_conversion'
    
    return None


def render_authentication_page(auth_manager: AuthManager) -> Optional[str]:
    """Render the authentication page"""
    st.markdown("## Spotify Authentication Required")

    st.markdown("""
    To create playlists in your Spotify account, you need to authenticate with Spotify.
    This is a one-time setup that allows the app to create playlists on your behalf.
    """)

    # Check if we have credentials
    if not Config.SPOTIFY_CLIENT_ID or not Config.SPOTIFY_CLIENT_SECRET:
        st.error("Spotify credentials not configured. Please check your .env file.")

        with st.expander("📋 Setup Instructions", expanded=True):
            st.markdown("""
            1. Copy `.env.example` to `.env`
            2. Get Spotify credentials from [Developer Dashboard](https://developer.spotify.com/dashboard/)
            3. Add your credentials to the `.env` file
            4. Restart the application
            """)



        if st.button("← Back"):
            return 'back'

        return None

    # Show authentication options
    st.markdown("### 🎵 Spotify Authentication")
    st.markdown("Connect your Spotify account to create playlists")

    if st.button("Authenticate with Spotify", type="primary"):
        auth_url = auth_manager.get_spotify_auth_url()
        if auth_url:
            st.markdown(f"[Click here to authenticate with Spotify]({auth_url})")
            st.markdown("After authentication, paste the redirect URL below:")

            callback_url = st.text_input("Redirect URL:", placeholder="http://localhost:8501/?code=...")

            if st.button("Complete Authentication"):
                if callback_url and 'code=' in callback_url:
                    try:
                        code = callback_url.split('code=')[1].split('&')[0]
                        success, error = auth_manager.handle_spotify_oauth(code)

                        if success:
                            st.success("Authentication successful!")
                            return 'authenticated'
                        else:
                            st.error(f"Authentication failed: {error}")
                    except Exception as e:
                        st.error(f"Invalid URL: {str(e)}")
                else:
                    st.warning("Please paste the complete redirect URL.")

    if st.button("← Back to URL Input"):
        return 'back'

    return None


def render_playlist_creation_page(results: List[Dict], auth_manager: AuthManager) -> Optional[str]:
    """Render the playlist creation page"""
    st.markdown("## Create Spotify Playlist")

    # Filter successful matches
    successful_matches = [r for r in results if r.get('found', False)]

    if not successful_matches:
        st.warning("No successful matches found. Cannot create playlist.")
        if st.button("← Back to Results"):
            return 'back'
        return None

    st.markdown(f"**{len(successful_matches)}** songs will be added to your playlist")

    # Playlist configuration
    col1, col2 = st.columns(2)

    with col1:
        playlist_name = st.text_input(
            "Playlist Name",
            value=f"Youtify Playlist {int(time.time())}",
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

    # Preview songs that will be added
    with st.expander(f"Preview Songs ({len(successful_matches)} tracks)", expanded=False):
        for i, song in enumerate(successful_matches, 1):
            st.markdown(f"**{i}.** {song.get('spotify_artist', 'Unknown')} - {song.get('spotify_title', 'Unknown')}")

    # Create playlist button
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        if st.button("🎵 Create Playlist", type="primary", use_container_width=True):
            if not playlist_name.strip():
                st.error("Please enter a playlist name")
                return None

            with st.spinner("Creating playlist..."):
                try:
                    # Create playlist using auth manager
                    spotify_manager = auth_manager.get_spotify_manager()
                    if not spotify_manager:
                        st.error("Spotify authentication required")
                        return None

                    # Create the playlist
                    playlist_id = spotify_manager.create_playlist(
                        name=playlist_name.strip(),
                        description=playlist_description.strip(),
                        public=playlist_public
                    )

                    if not playlist_id:
                        st.error("Failed to create playlist")
                        return None

                    # Add tracks to playlist
                    track_uris = [song.get('spotify_uri', '') for song in successful_matches if song.get('spotify_uri')]

                    if track_uris:
                        success = spotify_manager.add_tracks_to_playlist(playlist_id, track_uris)

                        if success:
                            st.success(f"✅ Playlist '{playlist_name}' created successfully!")
                            st.markdown(f"**{len(track_uris)}** songs added to your Spotify account")

                            # Show playlist link
                            playlist_url = f"https://open.spotify.com/playlist/{playlist_id}"
                            st.markdown(f"[Open in Spotify]({playlist_url})")

                            return 'success'
                        else:
                            st.error("Playlist created but failed to add some tracks")
                    else:
                        st.error("No valid Spotify URIs found")

                except Exception as e:
                    st.error(f"Error creating playlist: {str(e)}")

    if st.button("← Back to Results"):
        return 'back'

    return None

def render_song_card(song: Dict, index: int):
    """Render a single song result card"""
    # Determine status
    if song.get('found', False):
        confidence = song.get('confidence', 0.0)
        if confidence >= 0.8:
            status_class = "status-validated"
            status_text = "VALIDATED"
        else:
            status_class = "status-pending"
            status_text = "PENDING"
    else:
        status_class = "status-not-found"
        status_text = "NOT FOUND"
    
    # Render card
    st.markdown(f"""
    <div class="modern-song-card">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem;">
            <div>
                <h4 style="margin: 0 0 0.5rem 0; color: var(--text-primary);">{index}. {song.get('original_title', 'Unknown')}</h4>
                <span class="status-indicator {status_class}">{status_text}</span>
            </div>
            <div class="song-thumbnail">♪</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Song details
    if song.get('found', False):
        spotify_artist = song.get('spotify_artist', 'Unknown Artist')
        spotify_title = song.get('spotify_title', 'Unknown')
        confidence = song.get('confidence', 0.0)
        
        st.markdown(f"""
        <div style="margin-top: 1rem;">
            <p style="margin: 0; color: var(--text-secondary); font-size: 0.9rem;">
                <strong>Matched:</strong> {spotify_title} by {spotify_artist}
            </p>
            <div style="margin-top: 0.5rem;">
                <div style="background: var(--border); height: 4px; border-radius: 2px; overflow: hidden;">
                    <div style="background: var(--validated); height: 100%; width: {int(confidence * 100)}%; transition: width 0.3s ease;"></div>
                </div>
                <p style="margin: 0.25rem 0 0 0; font-size: 0.8rem; color: var(--text-muted);">
                    Confidence: {int(confidence * 100)}%
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="margin-top: 1rem;">
            <p style="margin: 0; color: var(--text-secondary); font-size: 0.9rem;">
                No match found on Spotify
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

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
