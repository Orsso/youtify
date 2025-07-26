"""
Shared UI Utilities and Helpers
"""
import streamlit as st
from typing import Any, Optional

def render_spotify_icon():
    """Render a Spotify icon"""
    return '<div class="spotify-icon"></div>'

def render_success_icon():
    """Render a success icon"""
    return '<div class="success-icon"></div>'

def safe_escape_text(text: str) -> str:
    """Safely escape text for HTML rendering"""
    if not text:
        return ""
    return text.replace('"', '"').replace('<', '<').replace('>', '>')

def create_styled_container(styles: dict, content: str) -> str:
    """Create a styled HTML container with the given styles and content"""
    style_str = "; ".join([f"{key.replace('_', '-')}: {value}" for key, value in styles.items()])
    return f'<div style="{style_str}">{content}</div>'

def render_glassmorphism_card(content: str, additional_styles: Optional[dict] = None) -> str:
    """Render content in a glassmorphism-style card"""
    base_styles = {
        "background": "var(--glass-bg)",
        "backdrop_filter": "var(--glass-backdrop)",
        "border": "1px solid var(--glass-border)",
        "border_radius": "var(--border-radius)",
        "padding": "1.5rem",
        "text_align": "center",
        "box_shadow": "var(--glass-shadow)",
        "margin": "0.5rem 0"
    }
    
    if additional_styles:
        base_styles.update(additional_styles)
    
    return create_styled_container(base_styles, content)

def render_animated_song_card(index: int, content: str, delay_multiplier: int = 1) -> str:
    """Render a song card with animation delay"""
    delay_class = f"animate-delay-{min(index * delay_multiplier + 1, 10)}"
    return f'<div class="youtube-song-card {delay_class}" id="song_container_{index}">{content}</div>'

def get_playlist_thumbnail_url(video_id: str) -> str:
    """Generate YouTube thumbnail URL from video ID"""
    if not video_id:
        return ""
    return f"https://img.youtube.com/vi/{video_id}/mqdefault.jpg"

def format_confidence_score(confidence: float) -> str:
    """Format confidence score as a percentage string"""
    return f"{confidence:.0%}"

def get_confidence_class(confidence: float) -> str:
    """Get CSS class based on confidence score"""
    if confidence >= 0.8:
        return "high"
    elif confidence >= 0.5:
        return "medium"
    else:
        return "low"