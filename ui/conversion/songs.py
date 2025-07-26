"""
Song Rendering Components
"""
import streamlit as st
from typing import List, Dict, Optional
from utils.session import get_session_state, set_session_state

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

def _render_enhanced_conversion_card(container, song: Dict, index: int, status: str, result: Optional[Dict]):
    """Render enhanced conversion card that transforms existing YouTube cards"""
    title = song.get('title', 'Unknown Title')
    channel = song.get('channel', 'Unknown Channel')
    video_id = song.get('video_id', '')

    # Generate YouTube thumbnail URL
    thumbnail_url = f"https://img.youtube.com/vi/{video_id}/mqdefault.jpg" if video_id else ""

    # Clean and escape any problematic characters in content
    safe_title = title.replace('"', '"').replace('<', '<').replace('>', '>')
    safe_channel = channel.replace('"', '"').replace('<', '<').replace('>', '>')

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
            safe_spotify_title = result.get('spotify_title', 'Unknown').replace('"', '"').replace('<', '<').replace('>', '>')
            safe_spotify_artist = result.get('spotify_artist', 'Unknown').replace('"', '"').replace('<', '<').replace('>', '>')
            
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
            safe_reason = reason.replace('"', '"').replace('<', '<').replace('>', '>')
            
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