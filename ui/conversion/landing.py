"""
Landing Page Components
"""
import streamlit as st
import time
import logging
from typing import List, Dict, Optional
from utils.proper_oauth_manager import ProperOAuthManager
from utils.session import get_session_state, set_session_state
from config import Config
from .preview import _render_playlist_preview, _update_playlist_card, _render_post_conversion_buttons
from .songs import render_youtube_songs, render_converted_songs, _render_enhanced_conversion_card

logger = logging.getLogger(__name__)

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