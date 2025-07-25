"""
Configuration settings for YouTube to Spotify Web Application
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""
    
    # App settings
    APP_NAME = "Youtify"
    APP_VERSION = "2.0.0"
    APP_DESCRIPTION = "Transform YouTube playlists into Spotify playlists with intelligent song matching"
    
    # API Configuration
    YOUTUBE_API_KEY: Optional[str] = os.getenv('YOUTUBE_API_KEY')
    SPOTIFY_CLIENT_ID: Optional[str] = os.getenv('SPOTIFY_CLIENT_ID')
    SPOTIFY_CLIENT_SECRET: Optional[str] = os.getenv('SPOTIFY_CLIENT_SECRET')
    SPOTIFY_USER_ID: Optional[str] = os.getenv('SPOTIFY_USER_ID')
    SPOTIFY_REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI', 'http://localhost:8501')

    # Application Settings
    DEBUG_MODE: bool = os.getenv('DEBUG_MODE', 'false').lower() == 'true'

    # API endpoints
    YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"
    SPOTIFY_API_BASE = "https://api.spotify.com/v1"
    SPOTIFY_AUTH_BASE = "https://accounts.spotify.com"
    
    # Default credentials for immediate functionality (personal API credentials)
    # These allow the app to work without user setup
    DEFAULT_YOUTUBE_API_KEY: str = os.getenv('DEFAULT_YOUTUBE_API_KEY', 'your_default_youtube_api_key_here')
    DEFAULT_SPOTIFY_CLIENT_ID: str = os.getenv('DEFAULT_SPOTIFY_CLIENT_ID', 'your_default_spotify_client_id_here')
    DEFAULT_SPOTIFY_CLIENT_SECRET: str = os.getenv('DEFAULT_SPOTIFY_CLIENT_SECRET', 'your_default_spotify_client_secret_here')
    
    # Matching settings
    HIGH_CONFIDENCE_THRESHOLD = float(os.getenv('HIGH_CONFIDENCE_THRESHOLD', '0.8'))
    MEDIUM_CONFIDENCE_THRESHOLD = float(os.getenv('MEDIUM_CONFIDENCE_THRESHOLD', '0.5'))
    LOW_CONFIDENCE_THRESHOLD = float(os.getenv('LOW_CONFIDENCE_THRESHOLD', '0.3'))

    # Rate Limiting
    YOUTUBE_REQUESTS_PER_MINUTE = int(os.getenv('YOUTUBE_REQUESTS_PER_MINUTE', '60'))
    SPOTIFY_REQUESTS_PER_MINUTE = int(os.getenv('SPOTIFY_REQUESTS_PER_MINUTE', '100'))

    # Cache Settings
    ENABLE_CACHING = os.getenv('ENABLE_CACHING', 'true').lower() == 'true'
    CACHE_DURATION_HOURS = int(os.getenv('CACHE_DURATION_HOURS', '24'))

    # Processing Settings
    MAX_PLAYLIST_SIZE = int(os.getenv('MAX_PLAYLIST_SIZE', '500'))
    BATCH_SIZE = int(os.getenv('BATCH_SIZE', '50'))
    PROCESSING_DELAY_MS = int(os.getenv('PROCESSING_DELAY_MS', '100'))

    # UI Settings
    THEME = os.getenv('THEME', 'dark')
    ENABLE_ANIMATIONS = os.getenv('ENABLE_ANIMATIONS', 'true').lower() == 'true'
    SHOW_ALBUM_ART = os.getenv('SHOW_ALBUM_ART', 'true').lower() == 'true'
    
    # API limits and timeouts
    YOUTUBE_API_QUOTA_LIMIT = 10000  # Daily quota limit
    SPOTIFY_RATE_LIMIT_DELAY = 0.1   # Seconds between requests
    REQUEST_TIMEOUT = 30             # Seconds
    MAX_RETRIES = 3
    
    # Playlist settings
    MAX_PLAYLIST_SIZE = 10000        # Maximum songs per playlist
    BATCH_SIZE = 50                  # Songs to process in one batch
    SPOTIFY_ADD_TRACKS_BATCH_SIZE = 100  # Spotify API limit
    
    # UI settings
    ITEMS_PER_PAGE = 20              # Pagination
    PROGRESS_UPDATE_INTERVAL = 1     # Seconds
    
    # File paths
    STYLES_DIR = "styles"
    ASSETS_DIR = "assets"
    LOGS_DIR = "logs"
    REPORTS_DIR = "reports"
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    @classmethod
    def validate_default_credentials(cls) -> bool:
        """Check if default credentials are available"""
        return bool(
            cls.DEFAULT_YOUTUBE_API_KEY and
            cls.DEFAULT_SPOTIFY_CLIENT_ID and
            cls.DEFAULT_SPOTIFY_CLIENT_SECRET and
            cls.DEFAULT_YOUTUBE_API_KEY != 'your_default_youtube_api_key_here' and
            cls.DEFAULT_SPOTIFY_CLIENT_ID != 'your_default_spotify_client_id_here' and
            cls.DEFAULT_SPOTIFY_CLIENT_SECRET != 'your_default_spotify_client_secret_here'
        )
    
    @classmethod
    def validate_full_mode(cls) -> bool:
        """Check if full mode credentials are available"""
        return bool(
            cls.YOUTUBE_API_KEY and 
            cls.SPOTIFY_CLIENT_ID and 
            cls.SPOTIFY_CLIENT_SECRET
        )
    
    @classmethod
    def get_missing_credentials(cls) -> list:
        """Get list of missing credentials for full mode"""
        missing = []
        if not cls.YOUTUBE_API_KEY:
            missing.append('YOUTUBE_API_KEY')
        if not cls.SPOTIFY_CLIENT_ID:
            missing.append('SPOTIFY_CLIENT_ID')
        if not cls.SPOTIFY_CLIENT_SECRET:
            missing.append('SPOTIFY_CLIENT_SECRET')
        return missing

# Streamlit configuration
STREAMLIT_CONFIG = {
    'page_title': Config.APP_NAME,
    'page_icon': '♪',
    'layout': 'wide',
    'initial_sidebar_state': 'collapsed',
    'menu_items': {
        'Get Help': 'https://github.com/yourusername/youtube-to-spotify',
        'Report a bug': 'https://github.com/yourusername/youtube-to-spotify/issues',
        'About': f"{Config.APP_DESCRIPTION} v{Config.APP_VERSION}"
    }
}

# Youtify Color Scheme - Yellow/Orange Theme
COLORS = {
    'primary_yellow': '#FFD700',
    'primary_orange': '#FF8C00',
    'gradient_start': '#FFD700',
    'gradient_end': '#FF8C00',
    'accent_light': '#FFF4E6',
    'accent_dark': '#CC6600',
    'success': '#32CD32',
    'warning': '#FF8C00',
    'error': '#FF4444',
    'info': '#4169E1',
    'high_confidence': '#32CD32',
    'medium_confidence': '#FF8C00',
    'low_confidence': '#FF4444',
    'background_light': '#FFFAF0',
    'text_primary': '#2C1810',
    'text_secondary': '#8B4513'
}

# URL patterns for validation
URL_PATTERNS = {
    'youtube_playlist': [
        r'(?:https?://)?(?:www\.)?youtube\.com/playlist\?list=([a-zA-Z0-9_-]+)',
        r'(?:https?://)?(?:www\.)?youtube\.com/watch\?.*list=([a-zA-Z0-9_-]+)',
        r'(?:https?://)?youtu\.be/.*\?.*list=([a-zA-Z0-9_-]+)'
    ]
}

# Error messages
ERROR_MESSAGES = {
    'invalid_youtube_url': "Please enter a valid YouTube playlist URL",
    'empty_playlist': "The YouTube playlist appears to be empty or private",
    'api_quota_exceeded': "YouTube API quota exceeded. Please try again later",
    'spotify_auth_failed': "Spotify authentication failed. Please check your credentials",
    'network_error': "Network error occurred. Please check your connection and try again",
    'rate_limit': "Rate limit exceeded. Please wait a moment and try again",
    'unknown_error': "An unexpected error occurred. Please try again"
}

# Success messages
SUCCESS_MESSAGES = {
    'playlist_created': "Playlist created successfully!",
    'songs_matched': "Songs matched and ready for review",
    'export_complete': "Results exported successfully"
}

# Help text
HELP_TEXT = {
    'youtube_url': "Paste the URL of any public YouTube playlist. Example: https://www.youtube.com/playlist?list=...",
    'playlist_name': "Choose a name for your new Spotify playlist",
    'confidence_threshold': "Minimum confidence score for automatic matching. Lower values include more uncertain matches",
    'public_playlist': "Whether the created Spotify playlist should be public or private"
}
