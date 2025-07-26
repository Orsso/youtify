"""
Core Processing Logic - Handles YouTube to Spotify conversion
"""

import re
import time
from typing import List, Dict, Callable, Optional
from fuzzywuzzy import fuzz
from utils.youtube_extractor import YouTubeExtractor
from utils.spotify_manager import SpotifyManager
from config import Config
import streamlit as st

class PlaylistProcessor:
    """Main processor for converting YouTube playlists to Spotify format"""

    def __init__(self):
        # Initialize YouTube extractor (always required)
        if not Config.YOUTUBE_API_KEY:
            raise ValueError("Missing YouTube API key. Please check your .env file.")

        self.youtube_extractor = YouTubeExtractor(Config.YOUTUBE_API_KEY)

        # Initialize Spotify manager (optional - depends on authentication)
        self.spotify_manager = self._get_spotify_manager()

    def _validate_credentials(self) -> bool:
        """Validate that required API credentials are available"""
        # Check if we have required credentials
        if not Config.YOUTUBE_API_KEY or not Config.SPOTIFY_CLIENT_ID or not Config.SPOTIFY_CLIENT_SECRET:
            return False

        # Check if user is authenticated
        if 'auth_manager' in st.session_state:
            auth_manager = st.session_state.auth_manager
            return auth_manager.is_authenticated('full')

        return False

    def _get_spotify_manager(self) -> Optional[SpotifyManager]:
        """Get the Spotify manager - try user auth first, fallback to client credentials"""
        # First try to get authenticated user manager (for playlist creation)
        if 'auth_manager' in st.session_state:
            auth_manager = st.session_state.auth_manager
            if auth_manager.is_authenticated('full'):
                return auth_manager.get_spotify_manager()

        # Fallback to client credentials for search-only operations
        try:
            from utils.spotify_manager import SpotifyManager
            spotify_manager = SpotifyManager(
                Config.SPOTIFY_CLIENT_ID,
                Config.SPOTIFY_CLIENT_SECRET
            )

            if spotify_manager.authenticate_client_credentials():
                return spotify_manager
            else:
                return None

        except Exception as e:
            st.warning(f"Failed to create client credentials manager: {str(e)}")
            return None
    
    def process_playlist(self, youtube_url: str, progress_callback: Optional[Callable] = None) -> List[Dict]:
        """
        Process a YouTube playlist and return Spotify matches

        Args:
            youtube_url: YouTube playlist URL
            progress_callback: Function to call with progress updates (current, total, song_name)

        Returns:
            List of song dictionaries with match results
        """
        try:
            # Extract playlist ID
            playlist_id = self.youtube_extractor.extract_playlist_id(youtube_url)
            if not playlist_id:
                raise ValueError("Invalid YouTube playlist URL")

            # Get videos from playlist with progress tracking
            def youtube_progress(current, total):
                if progress_callback:
                    progress_callback(current, total, f"Extracting videos from YouTube... ({current}/{total})")

            videos = self.youtube_extractor.get_playlist_videos(playlist_id, youtube_progress)
            if not videos:
                raise ValueError("No videos found in playlist or playlist is private")

            results = []
            total_videos = len(videos)

            for i, video in enumerate(videos):
                # Update progress
                if progress_callback:
                    progress_callback(i, total_videos, f"Processing: {video['title']}")

                # Parse song info
                parsed = self._parse_video_title(video['title'])

                # Search for Spotify match
                spotify_match = self._find_spotify_match(parsed['artist'], parsed['title'])

                # Create result
                result = {
                    'original_title': video['title'],
                    'channel': video['channel'],
                    'parsed_artist': parsed['artist'],
                    'parsed_title': parsed['title'],
                    'found': spotify_match is not None,
                    'spotify_artist': spotify_match.get('artist', '') if spotify_match else '',
                    'spotify_title': spotify_match.get('title', '') if spotify_match else '',
                    'spotify_uri': spotify_match.get('uri', '') if spotify_match else '',
                    'confidence': spotify_match.get('confidence', 0.0) if spotify_match else 0.0,
                    'spotify_preview_url': spotify_match.get('preview_url', '') if spotify_match else '',
                    'album_art_url': spotify_match.get('album_art_url', '') if spotify_match else ''
                }

                results.append(result)

                # Small delay for rate limiting
                time.sleep(Config.PROCESSING_DELAY_MS / 1000.0)

            # Final progress update
            if progress_callback:
                progress_callback(total_videos, total_videos, "Processing complete!")

            return results

        except Exception as e:
            # Show error to user
            st.error(f"API error occurred: {str(e)}")
            raise ValueError(f"Failed to process playlist: {str(e)}")

    def process_playlist_with_data(self, playlist_data: Dict,
                                 progress_callback: Optional[Callable[[int, int, str], None]] = None) -> List[Dict[str, str]]:
        """
        Process playlist using pre-parsed playlist data

        Args:
            playlist_data: Pre-parsed playlist data containing songs list
            progress_callback: Function to call with progress updates (current, total, song_name)

        Returns:
            List of song dictionaries with match results
        """
        try:
            videos = playlist_data.get('songs', [])
            if not videos:
                raise ValueError("No songs found in playlist data")

            results = []
            total_videos = len(videos)

            for i, video in enumerate(videos):
                # Update progress
                if progress_callback:
                    progress_callback(i, total_videos, f"Processing: {video['title']}")

                # Parse song info
                parsed = self._parse_video_title(video['title'])

                # Search for song on Spotify
                spotify_result = self._search_spotify(parsed['artist'], parsed['title'])

                # Store result
                result = {
                    'youtube_title': video['title'],
                    'youtube_channel': video['channel'],
                    'parsed_artist': parsed['artist'],
                    'parsed_title': parsed['title'],
                    'found': spotify_result is not None,
                    'video_id': video.get('video_id', ''),
                    'published': video.get('published', '')
                }

                if spotify_result:
                    result.update({
                        'spotify_id': spotify_result['id'],
                        'spotify_uri': spotify_result['uri'],
                        'spotify_artist': spotify_result['artists'][0]['name'],
                        'spotify_title': spotify_result['name'],
                        'confidence': self._calculate_confidence(parsed, spotify_result)
                    })
                else:
                    result['reason'] = 'No match found on Spotify'

                results.append(result)

                # Small delay for rate limiting
                time.sleep(Config.PROCESSING_DELAY_MS / 1000.0)

            # Final progress update
            if progress_callback:
                progress_callback(total_videos, total_videos, "Processing complete!")

            return results

        except Exception as e:
            # Show error to user
            st.error(f"API error occurred: {str(e)}")
            raise ValueError(f"Failed to process playlist: {str(e)}")

    def _parse_video_title(self, title: str) -> Dict[str, str]:
        """Parse video title to extract artist and song name"""


        # Common patterns for YouTube music videos (improved to handle hyphenated names)
        patterns = [
            # Pattern for "Artist - Song" but avoid splitting on hyphens within words
            r'^(.+?)\s+[-–—]\s+(.+?)(?:\s*\(.*\))?(?:\s*\[.*\])?$',  # Artist - Song (with spaces around dash)
            r'^(.+?)\s*[:|]\s*(.+?)(?:\s*\(.*\))?(?:\s*\[.*\])?$',   # Artist : Song
            r'^(.+?)\s*"(.+?)"',  # Artist "Song"
            # Fallback: if there's a dash with spaces, split there
            r'^(.+?)\s+-\s+(.+?)(?:\s*\(.*\))?(?:\s*\[.*\])?$',  # Artist - Song (fallback)
        ]

        for pattern in patterns:
            match = re.match(pattern, title.strip())
            if match:
                artist = match.group(1).strip()
                song = match.group(2).strip()

                # Clean up common suffixes
                for suffix in ['(Official Video)', '(Official Music Video)', '(Lyric Video)',
                              '(Audio)', '[Official Video]', '[Official Music Video]']:
                    song = song.replace(suffix, '').strip()
                    artist = artist.replace(suffix, '').strip()


                return {'artist': artist, 'title': song}

        # If no pattern matches, return the title as song name

        return {'artist': '', 'title': title}

    def _find_spotify_match(self, artist: str, title: str) -> Optional[Dict]:
        """Find best Spotify match for a song"""
        if not self.spotify_manager:
            return None

        try:
            tracks = self.spotify_manager.search_track(artist, title, limit=10)
            if not tracks:
                return None

            # Find best match using fuzzy matching
            best_match = None
            best_score = 0.0

            search_string = f"{artist} {title}".lower()

            for track in tracks:
                track_artists = ", ".join([a['name'] for a in track['artists']])
                track_string = f"{track_artists} {track['name']}".lower()

                # Calculate similarity score
                score = fuzz.ratio(search_string, track_string) / 100.0

                if score > best_score:
                    best_score = score
                    best_match = {
                        'artist': track_artists,
                        'title': track['name'],
                        'uri': track['uri'],
                        'confidence': score,
                        'preview_url': track.get('preview_url', ''),
                        'album_art_url': track['album']['images'][0]['url'] if track['album']['images'] else ''
                    }

            # Only return matches above minimum threshold
            if best_match and best_match['confidence'] >= Config.LOW_CONFIDENCE_THRESHOLD:
                return best_match

            return None

        except Exception as e:
            st.warning(f"Spotify search error: {str(e)}")
            return None


