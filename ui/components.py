"""
UI Components - Main entry point that imports from modular structure
"""
from .header import render_header
from .conversion.landing import render_landing_page
from .conversion.preview import _render_playlist_preview_completed
from .conversion.songs import render_youtube_songs, render_converted_songs
from .playlist.creation import render_playlist_creation_page
from .processing import render_processing_page, _update_enhanced_progress
from .conversion.result import generate_csv_report
from .shared.styles import GLASSMORPHISM_CSS
from .shared.utils import safe_escape_text

# For backward compatibility, re-export all functions
__all__ = [
    "render_header",
    "render_landing_page",
    "render_playlist_creation_page",
    "render_processing_page",
    "render_youtube_songs",
    "render_converted_songs",
    "generate_csv_report",
    "GLASSMORPHISM_CSS",
    "safe_escape_text"
]