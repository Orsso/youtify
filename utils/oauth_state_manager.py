"""
OAuth State Manager - Robust file-based session state persistence
Follows OAuth 2.0 RFC 6749 best practices for state management
"""

import os
import json
import time
import secrets
import tempfile
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class OAuthStateManager:
    """
    Manages OAuth state persistence using temporary files.
    
    This is a standard approach for OAuth implementations that need to
    persist state across redirects. Follows KISS and DRY principles.
    """
    
    def __init__(self, state_dir: Optional[str] = None, cleanup_interval: int = 3600):
        """
        Initialize the OAuth state manager.
        
        Args:
            state_dir: Directory to store state files (defaults to system temp)
            cleanup_interval: How often to cleanup old files (seconds)
        """
        # Use system temp directory if not specified
        if state_dir is None:
            self.state_dir = Path(tempfile.gettempdir()) / "youtify_oauth_states"
        else:
            self.state_dir = Path(state_dir)
        
        # Create directory if it doesn't exist
        self.state_dir.mkdir(parents=True, exist_ok=True)
        
        self.cleanup_interval = cleanup_interval
        self.max_state_age = 1800  # 30 minutes max age for state files
        
        # Cleanup old files on initialization
        self._cleanup_old_states()
    
    def generate_state_token(self) -> str:
        """
        Generate a cryptographically secure state token.
        
        Returns:
            A URL-safe random token for CSRF protection
        """
        return secrets.token_urlsafe(32)  # 256 bits of entropy
    
    def save_state(self, state_token: str, state_data: Dict[str, Any]) -> bool:
        """
        Save state data to a temporary file.
        
        Args:
            state_token: The state token to use as filename
            state_data: The data to persist
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Add metadata
            state_with_meta = {
                'data': state_data,
                'created_at': time.time(),
                'token': state_token
            }
            
            # Create secure filename
            state_file = self.state_dir / f"state_{state_token}.json"
            
            # Write atomically using temporary file
            temp_file = state_file.with_suffix('.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(state_with_meta, f, indent=2, default=str)
            
            # Atomic rename
            temp_file.rename(state_file)
            
            logger.info(f"Saved OAuth state: {state_token}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save OAuth state {state_token}: {e}")
            return False
    
    def load_state(self, state_token: str) -> Optional[Dict[str, Any]]:
        """
        Load state data from temporary file.
        
        Args:
            state_token: The state token to load
            
        Returns:
            The state data if found and valid, None otherwise
        """
        try:
            state_file = self.state_dir / f"state_{state_token}.json"
            
            if not state_file.exists():
                logger.warning(f"OAuth state file not found: {state_token}")
                return None
            
            # Load the state data
            with open(state_file, 'r', encoding='utf-8') as f:
                state_with_meta = json.load(f)
            
            # Check if state is too old
            created_at = state_with_meta.get('created_at', 0)
            if time.time() - created_at > self.max_state_age:
                logger.warning(f"OAuth state expired: {state_token}")
                self._delete_state_file(state_file)
                return None
            
            # Verify token matches
            if state_with_meta.get('token') != state_token:
                logger.error(f"OAuth state token mismatch: {state_token}")
                self._delete_state_file(state_file)
                return None
            
            logger.info(f"Loaded OAuth state: {state_token}")
            return state_with_meta.get('data', {})
            
        except Exception as e:
            logger.error(f"Failed to load OAuth state {state_token}: {e}")
            return None
    
    def delete_state(self, state_token: str) -> bool:
        """
        Delete a state file after successful OAuth callback.
        
        Args:
            state_token: The state token to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            state_file = self.state_dir / f"state_{state_token}.json"
            return self._delete_state_file(state_file)
        except Exception as e:
            logger.error(f"Failed to delete OAuth state {state_token}: {e}")
            return False
    
    def _delete_state_file(self, state_file: Path) -> bool:
        """Delete a state file safely."""
        try:
            if state_file.exists():
                state_file.unlink()
                logger.debug(f"Deleted state file: {state_file.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete state file {state_file}: {e}")
            return False
    
    def _cleanup_old_states(self) -> None:
        """
        Clean up old state files to prevent disk bloat.
        This is called automatically but can be called manually.
        """
        try:
            current_time = time.time()
            cleaned_count = 0
            
            for state_file in self.state_dir.glob("state_*.json"):
                try:
                    # Check file age
                    file_age = current_time - state_file.stat().st_mtime
                    
                    if file_age > self.max_state_age:
                        self._delete_state_file(state_file)
                        cleaned_count += 1
                        
                except Exception as e:
                    logger.warning(f"Error checking state file {state_file}: {e}")
            
            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} old OAuth state files")
                
        except Exception as e:
            logger.error(f"Error during OAuth state cleanup: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about stored states (for debugging).
        
        Returns:
            Dictionary with statistics
        """
        try:
            state_files = list(self.state_dir.glob("state_*.json"))
            current_time = time.time()
            
            stats = {
                'total_states': len(state_files),
                'state_dir': str(self.state_dir),
                'max_age_seconds': self.max_state_age,
                'states': []
            }
            
            for state_file in state_files:
                try:
                    file_age = current_time - state_file.stat().st_mtime
                    stats['states'].append({
                        'filename': state_file.name,
                        'age_seconds': int(file_age),
                        'expired': file_age > self.max_state_age
                    })
                except Exception:
                    pass
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting OAuth state stats: {e}")
            return {'error': str(e)}

# Global instance for easy access
_state_manager = None

def get_state_manager() -> OAuthStateManager:
    """Get the global OAuth state manager instance."""
    global _state_manager
    if _state_manager is None:
        _state_manager = OAuthStateManager()
    return _state_manager