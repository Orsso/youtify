"""
Header Component
"""
import streamlit as st
from typing import Optional

def render_header(logo_base64: str):
    """Render the application header with logo"""
    if logo_base64:
        st.markdown(f"""
        <div class="main-header">
            <div class="logo-container">
                <img src="data:image/png;base64,{logo_base64}" class="logo" alt="Youtify Logo">
                <div>
                    <h1>Youtify</h1>
                    <p>Convert YouTube playlists to Spotify format</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="main-header">
            <div class="logo-container">
                <div>
                    <h1>Youtify</h1>
                    <p>Convert YouTube playlists to Spotify format</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)