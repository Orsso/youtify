"""
YouTube Extractor - Handles YouTube playlist extraction using YouTube Data API v3
Optimized for web application use with better error handling and progress tracking.
"""

import re
import time
import logging
from typing import List, Dict, Optional, Callable
import requests

logger = logging.getLogger(__name__)

class YouTubeExtractor:
    """Handles YouTube playlist extraction using YouTube Data API v3"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://www.googleapis.com/youtube/v3"
        
    def extract_playlist_id(self, url: str) -> Optional[str]:
        """Extract playlist ID from various YouTube URL formats"""
        patterns = [
            r'list=([a-zA-Z0-9_-]+)',
            r'playlist\?list=([a-zA-Z0-9_-]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def validate_url(self, url: str) -> bool:
        """Validate if the URL is a valid YouTube playlist URL"""
        if not url:
            return False
        
        # Check if it's a YouTube URL
        if 'youtube.com' not in url and 'youtu.be' not in url:
            return False
        
        # Check if it contains playlist identifier
        if 'playlist' not in url and 'list=' not in url:
            return False
        
        # Try to extract playlist ID
        playlist_id = self.extract_playlist_id(url)
        return playlist_id is not None
    
    def get_playlist_info(self, playlist_id: str) -> Optional[Dict[str, str]]:
        """Get basic playlist information"""
        params = {
            'part': 'snippet',
            'id': playlist_id,
            'key': self.api_key
        }
        
        try:
            response = requests.get(f"{self.base_url}/playlists", params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get('items'):
                item = data['items'][0]
                return {
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'],
                    'channel': item['snippet']['channelTitle'],
                    'published': item['snippet']['publishedAt']
                }
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching playlist info: {e}")
        
        return None
    
    def get_playlist_videos(self, playlist_id: str, 
                          progress_callback: Optional[Callable[[int, int], None]] = None) -> List[Dict[str, str]]:
        """
        Get all video titles and channel names from a YouTube playlist with pagination
        
        Args:
            playlist_id: YouTube playlist ID
            progress_callback: Optional callback function to report progress (current, total)
        
        Returns:
            List of video dictionaries with title and channel information
        """
        videos = []
        next_page_token = None
        total_processed = 0
        
        # First, get the total count for progress tracking
        total_videos = self._get_playlist_video_count(playlist_id)
        
        while True:
            params = {
                'part': 'snippet',
                'playlistId': playlist_id,
                'maxResults': 50,
                'key': self.api_key
            }

            if next_page_token:
                params['pageToken'] = next_page_token

            try:
                response = requests.get(f"{self.base_url}/playlistItems", params=params)
                response.raise_for_status()
                data = response.json()

                for item in data.get('items', []):
                    title = item['snippet']['title']
                    channel_name = item['snippet'].get('videoOwnerChannelTitle', '').replace(' - Topic', '')

                    if title not in ["Deleted video", "Private video"]:
                        videos.append({
                            'title': title,
                            'channel': channel_name,
                            'video_id': item['snippet']['resourceId']['videoId'],
                            'published': item['snippet']['publishedAt']
                        })
                    
                    total_processed += 1
                    
                    # Report progress if callback provided
                    if progress_callback:
                        progress_callback(total_processed, total_videos or total_processed)

                next_page_token = data.get('nextPageToken')
                if not next_page_token:
                    break

                # Rate limiting - YouTube allows 100 requests per 100 seconds
                time.sleep(1)

            except requests.exceptions.RequestException as e:
                logger.error(f"Error fetching playlist videos: {e}")
                if "quotaExceeded" in str(e):
                    raise Exception("YouTube API quota exceeded. Please try again later.")
                elif "playlistNotFound" in str(e):
                    raise Exception("Playlist not found or is private.")
                else:
                    raise Exception(f"Error accessing YouTube API: {str(e)}")

        logger.info(f"Extracted {len(videos)} videos from YouTube playlist")
        return videos
    
    def _get_playlist_video_count(self, playlist_id: str) -> Optional[int]:
        """Get the total number of videos in a playlist for progress tracking"""
        try:
            params = {
                'part': 'contentDetails',
                'id': playlist_id,
                'key': self.api_key
            }
            
            response = requests.get(f"{self.base_url}/playlists", params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get('items'):
                return data['items'][0]['contentDetails']['itemCount']
        except Exception as e:
            logger.warning(f"Could not get playlist video count: {e}")
        
        return None
    
    def test_api_key(self) -> bool:
        """Test if the API key is valid"""
        try:
            params = {
                'part': 'snippet',
                'chart': 'mostPopular',
                'maxResults': 1,
                'key': self.api_key
            }
            
            response = requests.get(f"{self.base_url}/videos", params=params)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException:
            return False

class YouTubeError(Exception):
    """Custom exception for YouTube-related errors"""
    pass

class QuotaExceededError(YouTubeError):
    """Raised when YouTube API quota is exceeded"""
    pass

class PlaylistNotFoundError(YouTubeError):
    """Raised when playlist is not found or private"""
    pass

class InvalidAPIKeyError(YouTubeError):
    """Raised when API key is invalid"""
    pass
