"""
Processing Page Components
"""
import streamlit as st
from typing import List, Dict, Optional, Callable
from utils.session import get_session_state, set_session_state

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