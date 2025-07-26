"""
Proper OAuth Manager - Handles OAuth with robust file-based state preservation
Follows OAuth 2.0 RFC 6749 best practices for state management
"""

import streamlit as st
import time
import logging
from typing import Optional, Dict, Any
from config import Config
from .oauth_state_manager import get_state_manager

logger = logging.getLogger(__name__)

class ProperOAuthManager:
    """Manages Spotify OAuth with proper session state preservation"""
    
    def __init__(self):
        self.client_id = Config.SPOTIFY_CLIENT_ID
        self.client_secret = Config.SPOTIFY_CLIENT_SECRET
        self.redirect_uri = Config.SPOTIFY_REDIRECT_URI
        
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return 'spotify_token' in st.session_state and st.session_state.spotify_token is not None
    
    def get_auth_url(self, state_data: Optional[Dict] = None) -> str:
        """Generate Spotify authorization URL with file-based state persistence"""
        base_url = "https://accounts.spotify.com/authorize"
        scope = "playlist-modify-public playlist-modify-private"
        
        # Get the state manager
        state_manager = get_state_manager()
        
        # Generate secure state token
        state_token = state_manager.generate_state_token()
        
        # Save session data to temporary file
        if state_data:
            success = state_manager.save_state(state_token, state_data)
            if not success:
                logger.error("Failed to save OAuth state to file")
                # Fallback to a basic token without state data
                state_token = state_manager.generate_state_token()
        
        # Log the redirect URI for debugging
        print(f"DEBUG: Using redirect_uri in auth URL: {self.redirect_uri}")
        
        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_uri': self.redirect_uri,
            'scope': scope,
            'state': state_token,  # Secure random token
            'show_dialog': 'true'
        }
        
        param_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        return f"{base_url}?{param_string}"
    
    def handle_oauth_callback(self, auth_code: str, state_param: Optional[str] = None) -> bool:
        """Handle OAuth callback and exchange code for token with file-based state restoration"""
        try:
            import requests
            
            # Exchange code for token
            token_url = "https://accounts.spotify.com/api/token"
            
            data = {
                'grant_type': 'authorization_code',
                'code': auth_code,
                'redirect_uri': self.redirect_uri,
                'client_id': self.client_id,
                'client_secret': self.client_secret
            }
            
            response = requests.post(token_url, data=data)
            
            if response.status_code == 200:
                token_data = response.json()
                st.session_state.spotify_token = token_data
                st.session_state.spotify_authenticated = True
                
                # Restore state data from file using state token
                if state_param:
                    try:
                        state_manager = get_state_manager()
                        state_data = state_manager.load_state(state_param)
                        
                        if state_data:
                            # Restore session state from file data
                            for key, value in state_data.items():
                                if key != 'timestamp':  # Skip timestamp
                                    st.session_state[key] = value
                            
                            # Clean up the state file
                            state_manager.delete_state(state_param)
                            
                            logger.info(f"Restored session state from file: {list(state_data.keys())}")
                        else:
                            logger.warning(f"No stored state data found in file for token: {state_param}")
                    except Exception as e:
                        logger.warning(f"Failed to restore state from file: {e}")
                
                return True
            else:
                logger.error(f"Token exchange failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"OAuth callback handling failed: {e}")
            return False
    
    def get_access_token(self) -> Optional[str]:
        """Get the current access token"""
        if 'spotify_token' in st.session_state:
            token = st.session_state.spotify_token
            if isinstance(token, dict) and 'access_token' in token:
                return token['access_token']
        return None
    
    def render_auth_interface(self) -> None:
        """Render complete authentication interface"""
        if self.is_authenticated():
            st.success("✅ Connected to Spotify!")
            
            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button("Disconnect", type="secondary"):
                    self.clear_authentication()
                    st.rerun()
        else:
            st.info("🔐 Connect to Spotify to create playlists in your account.")
            self.render_auth_button()
    
    def render_auth_button(self, button_text: str = "Connect to Spotify") -> None:
        """Render authentication button with proper Spotify green styling"""
        
        # Store current session state before OAuth
        session_backup = {
            'results': st.session_state.get('results', []),
            'playlist_data': st.session_state.get('playlist_data', None),
            'youtube_url': st.session_state.get('youtube_url', ''),
            'app_state': st.session_state.get('app_state', 'landing'),
            'pending_playlist_creation': True,
            'timestamp': int(time.time())
        }
        
        # Generate auth URL with minimal state (CSRF protection only)
        auth_url = self.get_auth_url(session_backup)
        
        # Custom styled button with Spotify green color and proper hover
        st.markdown(f"""
        <style>
        .spotify-auth-button {{
            display: inline-block;
            width: 100%;
            text-decoration: none;
        }}
        .spotify-auth-button button {{
            background-color: #1DB954 !important;
            color: white !important;
            border: 1px solid #1DB954 !important;
            border-radius: 0.5rem;
            padding: 0.5rem 0.75rem;
            font-size: 1rem;
            font-weight: 400;
            line-height: 1.6;
            width: 100%;
            min-height: 2.5rem;
            cursor: pointer;
            transition: all 0.2s ease;
            font-family: inherit;
        }}
        .spotify-auth-button button:hover {{
            background-color: #1ed760 !important;
            border-color: #1ed760 !important;
            transform: translateY(-1px);
        }}
        .spotify-auth-button button:focus {{
            box-shadow: 0 0 0 3px rgba(29, 185, 84, 0.3) !important;
            outline: none !important;
        }}
        </style>
        <a href="{auth_url}" target="_blank" class="spotify-auth-button" id="spotify-auth-link">
            <button type="button">{button_text}</button>
        </a>
        <script>
        // Add click handler to ensure the link opens properly
        document.addEventListener('DOMContentLoaded', function() {{
            var link = document.getElementById('spotify-auth-link');
            if (link) {{
                link.addEventListener('click', function(e) {{
                    e.preventDefault();
                    window.open(this.href, '_blank');
                }});
            }}
        }});
        </script>
        """, unsafe_allow_html=True)
    
    def clear_authentication(self):
        """Clear authentication data"""
        keys_to_clear = ['spotify_token', 'spotify_authenticated']
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]