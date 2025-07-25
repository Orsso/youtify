"""
Data Models - Data structures for the YouTube to Spotify application
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum

class MatchStatus(Enum):
    """Status of song matching"""
    PENDING = "pending"
    FOUND = "found"
    NOT_FOUND = "not_found"
    LOW_CONFIDENCE = "low_confidence"
    ERROR = "error"
    MANUAL_REVIEW = "manual_review"

class ProcessingStatus(Enum):
    """Status of playlist processing"""
    NOT_STARTED = "not_started"
    EXTRACTING_YOUTUBE = "extracting_youtube"
    SEARCHING_SPOTIFY = "searching_spotify"
    CREATING_PLAYLIST = "creating_playlist"
    COMPLETED = "completed"
    ERROR = "error"

@dataclass
class Song:
    """Represents a song with metadata and matching information"""
    # Original YouTube data
    original_title: str
    channel_name: str = ""
    video_id: str = ""
    published_date: str = ""
    
    # Parsed information
    artist: str = ""
    title: str = ""
    features: List[str] = field(default_factory=list)
    
    # Spotify match data
    spotify_uri: str = ""
    spotify_id: str = ""
    spotify_artist: str = ""
    spotify_title: str = ""
    spotify_album: str = ""
    spotify_preview_url: str = ""
    spotify_external_url: str = ""
    
    # Matching metadata
    match_confidence: float = 0.0
    match_status: MatchStatus = MatchStatus.PENDING
    error: str = ""
    
    # Additional metadata
    processing_time: float = 0.0
    manual_selection: bool = False
    user_approved: bool = False
    
    @property
    def found(self) -> bool:
        """Check if song was successfully matched"""
        return self.match_status == MatchStatus.FOUND
    
    @property
    def confidence_level(self) -> str:
        """Get human-readable confidence level"""
        if self.match_confidence >= 0.8:
            return "High"
        elif self.match_confidence >= 0.5:
            return "Medium"
        elif self.match_confidence >= 0.3:
            return "Low"
        else:
            return "Very Low"
    
    @property
    def display_title(self) -> str:
        """Get display title for UI"""
        if self.title and self.artist:
            return f"{self.artist} - {self.title}"
        elif self.title:
            return self.title
        else:
            return self.original_title
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'original_title': self.original_title,
            'channel_name': self.channel_name,
            'video_id': self.video_id,
            'published_date': self.published_date,
            'artist': self.artist,
            'title': self.title,
            'features': self.features,
            'spotify_uri': self.spotify_uri,
            'spotify_id': self.spotify_id,
            'spotify_artist': self.spotify_artist,
            'spotify_title': self.spotify_title,
            'spotify_album': self.spotify_album,
            'spotify_preview_url': self.spotify_preview_url,
            'spotify_external_url': self.spotify_external_url,
            'match_confidence': self.match_confidence,
            'match_status': self.match_status.value,
            'error': self.error,
            'processing_time': self.processing_time,
            'manual_selection': self.manual_selection,
            'user_approved': self.user_approved
        }

@dataclass
class MigrationStats:
    """Migration statistics and metadata"""
    total_songs: int = 0
    successful_matches: int = 0
    not_found: int = 0
    low_confidence: int = 0
    errors: int = 0
    manual_reviews: int = 0
    
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    # Processing details
    youtube_extraction_time: float = 0.0
    spotify_search_time: float = 0.0
    playlist_creation_time: float = 0.0
    
    # Quality metrics
    average_confidence: float = 0.0
    high_confidence_count: int = 0
    medium_confidence_count: int = 0
    low_confidence_count: int = 0
    
    @property
    def duration(self) -> float:
        """Get total processing duration in seconds"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0
    
    @property
    def success_rate(self) -> float:
        """Get success rate as percentage"""
        if self.total_songs == 0:
            return 0.0
        return (self.successful_matches / self.total_songs) * 100
    
    @property
    def error_rate(self) -> float:
        """Get error rate as percentage"""
        if self.total_songs == 0:
            return 0.0
        return (self.errors / self.total_songs) * 100
    
    def update_confidence_stats(self, songs: List[Song]):
        """Update confidence statistics from song list"""
        confidences = [song.match_confidence for song in songs if song.found]
        
        if confidences:
            self.average_confidence = sum(confidences) / len(confidences)
            self.high_confidence_count = len([c for c in confidences if c >= 0.8])
            self.medium_confidence_count = len([c for c in confidences if 0.5 <= c < 0.8])
            self.low_confidence_count = len([c for c in confidences if c < 0.5])
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'total_songs': self.total_songs,
            'successful_matches': self.successful_matches,
            'not_found': self.not_found,
            'low_confidence': self.low_confidence,
            'errors': self.errors,
            'manual_reviews': self.manual_reviews,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'youtube_extraction_time': self.youtube_extraction_time,
            'spotify_search_time': self.spotify_search_time,
            'playlist_creation_time': self.playlist_creation_time,
            'average_confidence': self.average_confidence,
            'high_confidence_count': self.high_confidence_count,
            'medium_confidence_count': self.medium_confidence_count,
            'low_confidence_count': self.low_confidence_count,
            'duration': self.duration,
            'success_rate': self.success_rate,
            'error_rate': self.error_rate
        }

@dataclass
class PlaylistInfo:
    """Information about a YouTube playlist"""
    id: str
    title: str
    description: str = ""
    channel: str = ""
    published_date: str = ""
    video_count: int = 0
    url: str = ""

@dataclass
class SpotifyPlaylistInfo:
    """Information about a created Spotify playlist"""
    id: str
    name: str
    description: str = ""
    public: bool = True
    url: str = ""
    tracks_added: int = 0
    created_at: Optional[datetime] = None

@dataclass
class ProcessingProgress:
    """Progress information for UI updates"""
    status: ProcessingStatus = ProcessingStatus.NOT_STARTED
    current_step: str = ""
    current_song: str = ""
    processed_count: int = 0
    total_count: int = 0
    percentage: float = 0.0
    estimated_time_remaining: float = 0.0
    
    @property
    def is_complete(self) -> bool:
        """Check if processing is complete"""
        return self.status in [ProcessingStatus.COMPLETED, ProcessingStatus.ERROR]
    
    def update_progress(self, processed: int, total: int, current_song: str = ""):
        """Update progress information"""
        self.processed_count = processed
        self.total_count = total
        self.current_song = current_song
        
        if total > 0:
            self.percentage = (processed / total) * 100
        else:
            self.percentage = 0.0

@dataclass
class UserPreferences:
    """User preferences for the conversion process"""
    confidence_threshold: float = 0.5
    auto_approve_high_confidence: bool = True
    require_manual_review_low_confidence: bool = True
    include_features: bool = True
    public_playlist: bool = True
    playlist_description_template: str = "Migrated from YouTube playlist • {count} tracks"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'confidence_threshold': self.confidence_threshold,
            'auto_approve_high_confidence': self.auto_approve_high_confidence,
            'require_manual_review_low_confidence': self.require_manual_review_low_confidence,
            'include_features': self.include_features,
            'public_playlist': self.public_playlist,
            'playlist_description_template': self.playlist_description_template
        }
