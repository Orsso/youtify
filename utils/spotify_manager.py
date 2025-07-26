"""
Spotify Manager - Handles Spotify Web API operations
Optimized for web application use with both OAuth and Client Credentials flows.
"""

import base64
import time
import logging
from typing import List, Dict, Optional, Callable
import requests

logger = logging.getLogger(__name__)

class SpotifyManager:
    """Handles Spotify Web API operations"""

    def __init__(self, client_id: str, client_secret: str, user_id: str = "",
                 redirect_uri: str = "http://127.0.0.1:8501"):
        self.client_id = client_id
        self.client_secret = client_secret
        self.user_id = user_id
        self.redirect_uri = redirect_uri
        self.access_token = None
        self.token_type = None  # 'authorization_code' or 'client_credentials'
        self.base_url = "https://api.spotify.com/v1"
    
    def authenticate_client_credentials(self) -> bool:
        """
        Authenticate using Client Credentials flow (for search only)
        This is used for search functionality without user authentication.
        """
        token_url = "https://accounts.spotify.com/api/token"
        
        # Encode credentials
        credentials = f"{self.client_id}:{self.client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        data = {
            "grant_type": "client_credentials"
        }
        
        try:
            response = requests.post(token_url, headers=headers, data=data)
            response.raise_for_status()
            token_data = response.json()
            
            self.access_token = token_data["access_token"]
            self.token_type = "client_credentials"
            logger.info("Successfully authenticated with Spotify (Client Credentials)")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Client credentials authentication failed: {e}")
            return False
    
    def get_authorization_url(self, state: str = None) -> str:
        """
        Get authorization URL for OAuth flow
        Used for full mode where user needs to grant permissions.
        """
        auth_url = "https://accounts.spotify.com/authorize"
        scope = "playlist-modify-public playlist-modify-private"
        
        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_uri': self.redirect_uri,
            'scope': scope,
            'show_dialog': 'true'
        }
        
        if state:
            params['state'] = state
        
        query_string = '&'.join([f"{k}={requests.utils.quote(str(v))}" for k, v in params.items()])
        return f"{auth_url}?{query_string}"
    
    def exchange_code_for_token(self, code: str) -> bool:
        """Exchange authorization code for access token"""
        token_url = "https://accounts.spotify.com/api/token"
        
        # Encode credentials
        credentials = f"{self.client_id}:{self.client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri
        }
        
        try:
            response = requests.post(token_url, headers=headers, data=data)
            response.raise_for_status()
            token_data = response.json()
            
            self.access_token = token_data["access_token"]
            self.token_type = "authorization_code"
            logger.info("Successfully authenticated with Spotify (Authorization Code)")
            
            # Auto-detect user ID if not provided
            if not self.user_id:
                self.user_id = self._get_current_user_id()
            
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Token exchange failed: {e}")
            return False
    
    def _get_current_user_id(self) -> str:
        """Get current user ID using the authenticated token"""
        user_data = self._make_request('GET', 'me')
        if user_data and 'id' in user_data:
            return user_data['id']
        return ""
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict]:
        """Make authenticated request to Spotify API with retry logic"""
        if not self.access_token:
            logger.error("No access token available")
            return None
        
        url = f"{self.base_url}/{endpoint}"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        for attempt in range(3):
            try:
                response = requests.request(method, url, headers=headers, **kwargs)
                
                if response.status_code == 429:  # Rate limited
                    retry_after = int(response.headers.get('Retry-After', 1))
                    logger.warning(f"Rate limited, waiting {retry_after} seconds")
                    time.sleep(retry_after)
                    continue
                
                response.raise_for_status()
                return response.json() if response.content else {}
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request attempt {attempt + 1} failed: {e}")
                if attempt == 2:  # Last attempt
                    logger.error(f"All attempts failed for {endpoint}")
                    return None
                time.sleep(2 ** attempt)  # Exponential backoff
        
        return None
    
    def search_track(self, artist: str, title: str, limit: int = 10) -> Optional[List[Dict]]:
        """
        Search for tracks on Spotify with intelligent search strategies
        Returns list of tracks instead of just the first one for better matching
        """
        if not title:
            return None
        
        search_queries = []
        
        # Strategy 1: Exact artist and track search
        if artist and title:
            search_queries.append(f'artist:"{artist}" track:"{title}"')
        
        # Strategy 2: General search with both artist and title
        if artist and title:
            search_queries.append(f'"{artist}" "{title}"')
        
        # Strategy 3: Search with just the title
        search_queries.append(f'"{title}"')
        
        # Strategy 4: Broader search without quotes
        if artist and title:
            search_queries.append(f'{artist} {title}')
        else:
            search_queries.append(title)
        
        # Try each search strategy
        for query in search_queries:
            tracks = self._search_with_query(query, limit)
            if tracks:
                return tracks
        
        return None
    
    def _search_with_query(self, query: str, limit: int = 10) -> Optional[List[Dict]]:
        """Execute search query and return tracks"""
        params = {
            'q': query,
            'type': 'track',
            'limit': limit
        }
        
        data = self._make_request('GET', 'search', params=params)
        if not data or 'tracks' not in data:
            return None
        
        tracks = data['tracks']['items']
        return tracks if tracks else None
    
    def get_track_details(self, track_id: str) -> Optional[Dict]:
        """Get detailed information about a track"""
        return self._make_request('GET', f'tracks/{track_id}')
    
    def create_playlist(self, name: str, description: str = "", public: bool = True) -> Optional[str]:
        """Create a new Spotify playlist (requires authorization_code token)"""
        if self.token_type != "authorization_code":
            logger.error("Playlist creation requires user authorization")
            return None
        
        if not self.user_id:
            logger.error("User ID required for playlist creation")
            return None
        
        data = {
            'name': name,
            'description': description,
            'public': public
        }
        
        result = self._make_request('POST', f'users/{self.user_id}/playlists', json=data)
        if result:
            logger.info(f"Created playlist: {name}")
            return result['id']
        return None
    
    def add_tracks_to_playlist(self, playlist_id: str, track_uris: List[str],
                             progress_callback: Optional[Callable[[int, int], None]] = None) -> bool:
        """Add tracks to a Spotify playlist in batches"""
        if self.token_type != "authorization_code":
            logger.error("Adding tracks to playlist requires user authorization")
            return False
        
        # Spotify allows max 100 tracks per request
        batch_size = 100
        total_tracks = len(track_uris)
        
        for i in range(0, len(track_uris), batch_size):
            batch = track_uris[i:i + batch_size]
            data = {'uris': batch}
            
            result = self._make_request('POST', f'playlists/{playlist_id}/tracks', json=data)
            if not result:
                return False
            
            # Report progress
            if progress_callback:
                progress_callback(min(i + batch_size, total_tracks), total_tracks)
            
            time.sleep(0.1)  # Small delay between batches
        
        logger.info(f"Added {len(track_uris)} tracks to playlist")
        return True
    
    def test_connection(self) -> bool:
        """Test if the Spotify connection is working"""
        try:
            # Try a simple search
            result = self._search_with_query("test", 1)
            return result is not None
        except Exception:
            return False
    
    def get_user_info(self) -> Optional[Dict]:
        """Get current user information (requires authorization_code token)"""
        if self.token_type != "authorization_code":
            return None
        return self._make_request('GET', 'me')

class SpotifyError(Exception):
    """Custom exception for Spotify-related errors"""
    pass

class AuthenticationError(SpotifyError):
    """Raised when authentication fails"""
    pass

class RateLimitError(SpotifyError):
    """Raised when rate limit is exceeded"""
    pass
