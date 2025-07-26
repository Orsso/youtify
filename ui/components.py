"""
UI Components - Consolidated, clean, reusable UI components
"""

import streamlit as st
import time
import csv
import io
import logging
from typing import List, Dict, Optional
from utils.proper_oauth_manager import ProperOAuthManager
from utils.session import get_session_state, set_session_state
from config import Config

logger = logging.getLogger(__name__)

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

def render_landing_page(oauth_manager) -> Optional[str]:
    """Render the landing page with YouTube URL input and in-place conversion"""
    
    # Check credentials first
    if not Config.SPOTIFY_CLIENT_ID or not Config.SPOTIFY_CLIENT_SECRET:
        st.error("Spotify credentials not configured. Please check your .env file.")
        return None

    # URL input - always visible
    youtube_url = st.text_input(
        "YouTube Playlist URL",
        placeholder="https://www.youtube.com/playlist?list=...",
        value=get_session_state('youtube_url', ''),
        help="Paste any public YouTube playlist URL"
    )

    # If URL is provided, parse playlist immediately and show details
    if youtube_url and youtube_url.strip():
        url_clean = youtube_url.strip()

        # Check if we already have parsed data for this URL
        cached_url = get_session_state('cached_playlist_url', '')
        if cached_url != url_clean:
            # Parse playlist immediately and store in session state
            with st.spinner("Parsing YouTube playlist..."):
                playlist_data = _parse_full_playlist(url_clean)
                if playlist_data:
                    set_session_state('playlist_data', playlist_data)
                    set_session_state('cached_playlist_url', url_clean)
                    # Reset conversion state when new URL is parsed
                    set_session_state('start_conversion', False)
                    set_session_state('conversion_active', False)
                    set_session_state('convert_button_clicked', False)  # Reset button clicked flag
                    if 'conversion_state' in st.session_state:
                        del st.session_state.conversion_state
                    st.rerun()
                else:
                    st.error("Could not parse playlist. Please check the URL and try again.")
                    return None

        # Add spacing
        st.markdown("<br>", unsafe_allow_html=True)

        # Display playlist details if available
        playlist_data = get_session_state('playlist_data', None)
        if playlist_data:
            # Show playlist preview - this handles all states internally
            _render_playlist_preview(playlist_data['details'], len(playlist_data['songs']))

            # Check if conversion should start
            start_conversion = get_session_state('start_conversion', False)
            conversion_active = get_session_state('conversion_active', False)

            # Center the convert button (moved above song list)
            st.markdown("<br>", unsafe_allow_html=True)
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if conversion_active:
                    # During active conversion, show empty space (playlist card shows "Converting")
                    st.markdown("<div style='height: 2.5rem;'></div>", unsafe_allow_html=True)
                elif get_session_state('conversion_completed', False):
                    # Show action buttons after conversion
                    _render_post_conversion_buttons(oauth_manager)
                elif get_session_state('start_conversion', False) or get_session_state('convert_button_clicked', False):
                    # Conversion is starting or button was clicked, show starting message
                    st.markdown("""
                    <div style='
                        height: 2.5rem; 
                        display: flex; 
                        align-items: center; 
                        justify-content: center; 
                        color: #FF6B35; 
                        font-style: italic; 
                        font-weight: 500;
                        background: rgba(255, 107, 53, 0.1);
                        border-radius: 0.5rem;
                        border: 1px solid rgba(255, 107, 53, 0.2);
                    '>
                        Starting conversion...
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # Show active convert button
                    convert_clicked = st.button("Convert to Spotify", type="primary")
                    if convert_clicked:
                        # Set flag to hide button on next render
                        set_session_state('convert_button_clicked', True)
                        set_session_state('start_conversion', True)
                        st.rerun()  # Force immediate rerun to hide button

            # Display individual song cards
            if not get_session_state('conversion_completed', False):
                # Before/during conversion - render normal YouTube song cards
                song_containers = render_youtube_songs(playlist_data['songs'])
                # Store containers in session state for later use during conversion
                set_session_state('song_containers', song_containers)
            else:
                # Conversion completed - render converted song cards with final states
                results = get_session_state('results', [])
                song_containers = render_converted_songs(playlist_data['songs'], results)
                # Store the converted containers
                set_session_state('song_containers', song_containers)

            # Handle conversion if it should start
            if start_conversion and not conversion_active:
                set_session_state('start_conversion', False)
                set_session_state('conversion_active', True)
                st.rerun()

            # Handle active conversion
            if conversion_active:
                _handle_in_place_conversion(playlist_data, song_containers, oauth_manager)

        else:
            st.warning("Could not parse playlist. Please check the URL and try again.")
            return None

    return None

def _parse_full_playlist(youtube_url: str) -> Optional[Dict]:
    """Parse complete playlist data immediately including all songs"""
    try:
        from utils.youtube_extractor import YouTubeExtractor
        from config import Config

        # Use configured API key
        api_key = Config.YOUTUBE_API_KEY
        if not api_key or api_key == 'your_youtube_api_key_here':
            return None

        extractor = YouTubeExtractor(api_key)

        # Extract playlist ID
        playlist_id = extractor.extract_playlist_id(youtube_url)
        if not playlist_id:
            return None

        # Get playlist info
        playlist_info = extractor.get_playlist_info(playlist_id)
        if not playlist_info:
            return None

        # Get all videos from playlist
        videos = extractor.get_playlist_videos(playlist_id)
        if not videos:
            return None

        # Get actual video count and thumbnail
        video_count = len(videos)
        thumbnail_url = _get_playlist_thumbnail(playlist_id, api_key)

        # Prepare playlist details
        playlist_details = {
            'title': playlist_info.get('title', 'Unknown Playlist'),
            'description': playlist_info.get('description', ''),
            'song_count': video_count,
            'thumbnail': thumbnail_url,
            'channel': playlist_info.get('channel', 'Unknown Channel')
        }

        # Return complete playlist data
        return {
            'details': playlist_details,
            'songs': videos,
            'playlist_id': playlist_id
        }
    except Exception as e:
        print(f"Error parsing full playlist: {e}")
        return None

def _get_playlist_thumbnail(playlist_id: str, api_key: str) -> Optional[str]:
    """Get playlist thumbnail URL"""
    try:
        import requests

        params = {
            'part': 'snippet',
            'id': playlist_id,
            'key': api_key
        }

        response = requests.get("https://www.googleapis.com/youtube/v3/playlists", params=params)
        response.raise_for_status()
        data = response.json()

        if data.get('items'):
            thumbnails = data['items'][0]['snippet'].get('thumbnails', {})
            # Try to get the best quality thumbnail available
            for quality in ['maxres', 'standard', 'high', 'medium', 'default']:
                if quality in thumbnails:
                    return thumbnails[quality]['url']
    except Exception:
        pass
    return None

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

def render_youtube_songs(songs: List[Dict]) -> List:
    """Render individual YouTube songs in compact cards with thumbnails"""
    if not songs:
        return []

    st.markdown("### Songs in Playlist")

    # Store containers for potential animation updates
    song_containers = []

    for i, song in enumerate(songs):
        title = song.get('title', 'Unknown Title')
        channel = song.get('channel', 'Unknown Channel')
        video_id = song.get('video_id', '')

        # Generate YouTube thumbnail URL
        thumbnail_url = f"https://img.youtube.com/vi/{video_id}/mqdefault.jpg" if video_id else ""

        # Create card with sequential animation delay
        delay_class = f"animate-delay-{min(i + 1, 10)}"

        # Create container that can be updated during conversion
        container = st.empty()
        song_containers.append(container)

        # Initial YouTube-only display
        with container:
            st.markdown(f"""
            <div class="youtube-song-card {delay_class}" id="song_container_{i}" style="
                display: flex;
                align-items: center;
                gap: 0.75rem;
                padding: 0.75rem;
                margin: 0.5rem 0;
                background: rgba(255, 255, 255, 0.05);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
            ">
                <img src="{thumbnail_url}" style="width: 60px; height: 45px; border-radius: 6px; object-fit: cover;" alt="Video thumbnail" />
                <div style="flex: 1; min-width: 0;">
                    <div style="font-weight: 500; color: #ffffff; margin-bottom: 0.25rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{title}</div>
                    <div style="font-size: 0.875rem; color: #cccccc; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{channel}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    return song_containers


def render_converted_songs(songs: List[Dict], results: List[Dict]) -> List:
    """Render converted song cards with their final states"""
    if not songs or not results:
        return []

    st.markdown("### Songs in Playlist")

    # Store containers for the converted songs
    song_containers = []

    for i, (song, result) in enumerate(zip(songs, results)):
        # Create container for each converted song
        container = st.empty()
        song_containers.append(container)

        # Render the song in its final converted state
        if result:
            status = 'found' if result.get('found', False) else 'not_found'
            _render_enhanced_conversion_card(container, song, i, status, result)
        else:
            # Fallback to original YouTube card if no result
            title = song.get('title', 'Unknown Title')
            channel = song.get('channel', 'Unknown Channel')
            video_id = song.get('video_id', '')
            thumbnail_url = f"https://img.youtube.com/vi/{video_id}/mqdefault.jpg" if video_id else ""

            with container:
                st.markdown(f"""
                <div class="youtube-song-card" id="song_container_{i}" style="
                    display: flex;
                    align-items: center;
                    gap: 0.75rem;
                    padding: 0.75rem;
                    margin: 0.5rem 0;
                    background: rgba(255, 255, 255, 0.05);
                    backdrop-filter: blur(10px);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 12px;
                    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
                ">
                    <img src="{thumbnail_url}" style="width: 60px; height: 45px; border-radius: 6px; object-fit: cover;" alt="Video thumbnail" />
                    <div style="flex: 1; min-width: 0;">
                        <div style="font-weight: 500; color: #ffffff; margin-bottom: 0.25rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{title}</div>
                        <div style="font-size: 0.875rem; color: #cccccc; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{channel}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    return song_containers


def _handle_in_place_conversion(playlist_data: Dict, song_containers: List, oauth_manager):
    """Handle the conversion process in place on the landing page"""
    from core.processor import PlaylistProcessor
    
    # Initialize conversion state if not exists
    if 'conversion_state' not in st.session_state:
        st.session_state.conversion_state = {
            'current_index': 0,
            'results': [],
            'completed': False,
            'started': False
        }

    songs = playlist_data['songs']
    conversion_state = st.session_state.conversion_state

    # Use the existing song containers
    if len(song_containers) != len(songs):
        st.error("Mismatch between song containers and songs. Please refresh the page.")
        set_session_state('conversion_active', False)
        return

    # Start conversion if not started
    if not conversion_state['started']:
        conversion_state['started'] = True
        conversion_state['results'] = [None] * len(songs)
        
        # Update the playlist card to converting state
        playlist_card_container = get_session_state('playlist_card_container', None)
        playlist_details = get_session_state('playlist_details', playlist_data['details'])
        if playlist_card_container:
            _update_playlist_card(playlist_card_container, playlist_details, "converting", 0, len(songs))

        # Initialize processor
        processor = PlaylistProcessor()

        # Process songs one by one with real-time display using existing containers
        for i, song in enumerate(songs):
            conversion_state['current_index'] = i

            # Transform existing container to processing state
            _render_enhanced_conversion_card(song_containers[i], song, i, 'processing', None)
            
            # Small delay to show processing animation
            time.sleep(0.5)

            # Parse song info
            parsed = processor._parse_video_title(song['title'])

            # Search for Spotify match
            spotify_match = None
            if processor.spotify_manager:
                try:
                    spotify_match = processor._find_spotify_match(parsed['artist'], parsed['title'])
                except Exception as e:
                    st.warning(f"Spotify search failed for '{song['title']}': {str(e)}")

            # Create result
            result = {
                'original_title': song['title'],
                'channel': song['channel'],
                'parsed_artist': parsed['artist'],
                'parsed_title': parsed['title'],
                'found': spotify_match is not None,
                'video_id': song.get('video_id', ''),
                'published': song.get('published', '')
            }

            if spotify_match:
                result.update({
                    'spotify_artist': spotify_match['artist'],
                    'spotify_title': spotify_match['title'],
                    'spotify_uri': spotify_match['uri'],
                    'confidence': spotify_match['confidence'],
                    'spotify_preview_url': spotify_match.get('preview_url', ''),
                    'album_art_url': spotify_match.get('album_art_url', '')
                })
            else:
                if not processor.spotify_manager:
                    result['reason'] = 'Spotify authentication required for matching'
                else:
                    result['reason'] = 'No match found on Spotify'

            conversion_state['results'][i] = result

            # Transform container to final state (found or not found)
            status = 'found' if result['found'] else 'not_found'
            _render_enhanced_conversion_card(song_containers[i], song, i, status, result)

            # Small delay for visual effect
            time.sleep(0.3)

    # Check if conversion is complete
    if conversion_state['current_index'] >= len(songs) - 1 and not conversion_state['completed']:
        conversion_state['completed'] = True

        # Store results for next step
        set_session_state('results', conversion_state['results'])
        found_songs = [r for r in conversion_state['results'] if r and r.get('found', False)]

        # Update the playlist card to show completion status
        playlist_card_container = get_session_state('playlist_card_container', None)
        playlist_details = get_session_state('playlist_details', playlist_data['details'])
        if playlist_card_container:
            _update_playlist_card(playlist_card_container, playlist_details, "completed", len(found_songs), len(songs))
        
        # Mark conversion as completed and inactive
        set_session_state('conversion_completed', True)
        set_session_state('conversion_active', False)
        
        # Store the final converted containers to preserve their state
        set_session_state('final_song_containers', song_containers)
        
        st.rerun()


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


def render_enhanced_realtime_conversion(playlist_data: Dict, processor, song_containers: List) -> Optional[List[Dict]]:
    """Legacy function - conversion now handled in landing page"""
    # This function is no longer used as conversion is handled in-place on the landing page
    st.error("This page should not be accessed. Please return to the main page.")
    if st.button("Return to Main Page"):
        set_session_state('app_state', 'landing')
        st.rerun()
    return None

def _render_enhanced_conversion_card(container, song: Dict, index: int, status: str, result: Optional[Dict]):
    """Render enhanced conversion card that transforms existing YouTube cards"""
    title = song.get('title', 'Unknown Title')
    channel = song.get('channel', 'Unknown Channel')
    video_id = song.get('video_id', '')

    # Generate YouTube thumbnail URL
    thumbnail_url = f"https://img.youtube.com/vi/{video_id}/mqdefault.jpg" if video_id else ""

    # Clean and escape any problematic characters in content
    safe_title = title.replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')
    safe_channel = channel.replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')

    with container:
        if status == 'processing':
            # Transform to processing state with split design
            st.markdown(f"""
            <div class="conversion-card processing-transform" id="song_container_{index}">
                <div class="conversion-card-content">
                    <div class="youtube-side">
                        <div style="display: flex; align-items: center; gap: 0.75rem;">
                            <img src="{thumbnail_url}" style="width: 60px; height: 45px; border-radius: 6px; object-fit: cover;" alt="Video thumbnail" />
                            <div style="flex: 1; min-width: 0;">
                                <div class="side-title">{safe_title}</div>
                                <div class="side-artist">{safe_channel}</div>
                            </div>
                        </div>
                    </div>
                    <div class="spotify-side loading">
                        <div class="loading-placeholder wide"></div>
                        <div class="loading-placeholder narrow"></div>
                        <div class="status-indicator processing">
                            <div class="status-icon processing-icon"></div>
                            Analyzing...
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        elif status == 'found' and result:
            # Transform to found state
            confidence = result.get('confidence', 0)
            confidence_class = 'high' if confidence >= 0.8 else 'medium' if confidence >= 0.5 else 'low'
            safe_spotify_title = result.get('spotify_title', 'Unknown').replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')
            safe_spotify_artist = result.get('spotify_artist', 'Unknown').replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')
            
            st.markdown(f"""
            <div class="conversion-card found-transform" id="song_container_{index}">
                <div class="conversion-card-content">
                    <div class="youtube-side">
                        <div style="display: flex; align-items: center; gap: 0.75rem;">
                            <img src="{thumbnail_url}" style="width: 60px; height: 45px; border-radius: 6px; object-fit: cover;" alt="Video thumbnail" />
                            <div style="flex: 1; min-width: 0;">
                                <div class="side-title">{safe_title}</div>
                                <div class="side-artist">{safe_channel}</div>
                            </div>
                        </div>
                    </div>
                    <div class="spotify-side loaded">
                        <div class="side-title">{safe_spotify_title}</div>
                        <div class="side-artist">{safe_spotify_artist}</div>
                        <div class="side-meta">
                            <span class="confidence-score {confidence_class}">{confidence:.0%} match</span>
                            <span class="status-indicator found">
                                <div class="status-icon found-icon"></div>
                                Matched
                            </span>
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        else:
            # Transform to not found state
            reason = result.get('reason', 'No match found') if result else 'No match found'
            safe_reason = reason.replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')
            
            st.markdown(f"""
            <div class="conversion-card not-found-transform" id="song_container_{index}">
                <div class="conversion-card-content">
                    <div class="youtube-side">
                        <div style="display: flex; align-items: center; gap: 0.75rem;">
                            <img src="{thumbnail_url}" style="width: 60px; height: 45px; border-radius: 6px; object-fit: cover;" alt="Video thumbnail" />
                            <div style="flex: 1; min-width: 0;">
                                <div class="side-title">{safe_title}</div>
                                <div class="side-artist">{safe_channel}</div>
                            </div>
                        </div>
                    </div>
                    <div class="spotify-side loaded">
                        <div class="side-title" style="color: var(--text-muted);">—</div>
                        <div class="side-artist" style="color: var(--text-muted); font-size: 0.8rem;">{safe_reason}</div>
                        <div class="side-meta">
                            <span class="status-indicator not-found">
                                <div class="status-icon not-found-icon"></div>
                                No Match
                            </span>
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

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
                    
                    if track_uris:
                        success = spotify_manager.add_tracks_to_playlist(playlist_id, track_uris)
                        if success:
                            # Store success state
                            st.session_state.playlist_created = True
                            st.session_state.created_playlist_name = playlist_name
                            st.session_state.created_playlist_id = playlist_id
                            st.session_state.created_playlist_track_count = len(track_uris)
                            st.rerun()
                        else:
                            st.error("Playlist created but failed to add some tracks")
                    else:
                        st.error("No valid track URIs found")

            except Exception as e:
                st.error(f"Error creating playlist: {str(e)}")
                logger.error(f"Playlist creation error: {e}")

    return None

def render_processing_page(processor) -> Optional[List[Dict]]:
    """Render enhanced processing page with detailed progress tracking"""

    # Header
    st.markdown("# Converting Playlist")

    # Show playlist info from pre-parsed data
    playlist_data = get_session_state('playlist_data', None)
    if playlist_data:
        details = playlist_data['details']
        st.markdown(f"**{details['title']}** • {details['song_count']} songs")

    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    current_song = st.empty()
    stats_container = st.empty()

    # Start processing
    if 'processing_started' not in st.session_state:
        st.session_state.processing_started = True
        st.session_state.conversion_stats = {'found': 0, 'not_found': 0, 'total': 0}

        try:
            # Use pre-parsed playlist data for processing
            youtube_url = get_session_state('youtube_url', '')
            results = processor.process_playlist_with_data(
                playlist_data,
                progress_callback=lambda current, total, song: _update_enhanced_progress(
                    progress_bar, status_text, current_song, stats_container, current, total, song
                )
            )

            # Processing complete
            del st.session_state.processing_started
            return results

        except Exception as e:
            st.error(f"Error: {str(e)}")
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("Try Again"):
                    if 'processing_started' in st.session_state:
                        del st.session_state.processing_started
                    st.rerun()

    return None

def _update_enhanced_progress(progress_bar, status_text, current_song, stats_container, current: int, total: int, song: str):
    """Update enhanced progress display"""
    # Update progress bar
    progress = current / total if total > 0 else 0
    progress_bar.progress(progress)

    # Update status
    status_text.markdown(f"**Processing {current} of {total} songs** ({progress:.1%} complete)")

    # Update current song
    current_song.markdown(f"**Currently processing:** {song}")

    # Update stats
    stats = get_session_state('conversion_stats', {'found': 0, 'not_found': 0, 'total': current})
    stats_container.markdown(f"**{stats['found']} found** • **{stats['not_found']} not found**")

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