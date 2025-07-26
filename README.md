# Youtify

Convert YouTube playlists to Spotify playlists with intelligent song matching.

## Features

- Smart song matching with confidence scoring
- Spotify OAuth integration for playlist creation
- Modern dark theme UI with responsive design
- Audio previews for better matching decisions
- CSV export options for match results

## Quick Start

### Automated Setup (Recommended)

```bash
git clone https://github.com/Orsso/youtify-poc.git
cd youtify-poc
python setup_youtify.py
```

The setup script will:
- Check Python version compatibility
- Install dependencies
- Guide you through API credential setup

### Manual Setup

1. Clone and install dependencies:
   ```bash
   git clone https://github.com/Orsso/youtify-poc.git
   cd youtify-poc
   pip install -r requirements.txt
   ```

2. Configure credentials:
   - Copy `.streamlit/secrets.example.toml` to `.streamlit/secrets.toml`
   - Fill in your actual API credentials

3. Get API credentials:
   - YouTube: Enable YouTube Data API v3 in Google Cloud Console
   - Spotify: Create an app in Spotify Developer Dashboard
     - For local development: Add `http://127.0.0.1:8501/` to redirect URIs
     - For production: Add your app's URL (e.g., `https://your-app.streamlit.app/`) to redirect URIs

4. Run the application:
   ```bash
   streamlit run main.py
   ```

## How It Works

1. URL Processing - Extracts playlist ID from YouTube URL
2. Video Extraction - Fetches video titles and metadata using YouTube API
3. Title Parsing - Identifies artist and song names
4. Smart Search - Multi-strategy Spotify search for accurate matching
5. Interactive Matching - Review and approve uncertain matches with audio previews
6. Playlist Creation - Automatically creates playlist in your Spotify account

## OAuth Authentication

The app features seamless OAuth flow integrated directly into the main interface:

1. Enter YouTube URL
2. Click "Import to Spotify" 
3. Authorize the app on Spotify's page
4. Automatically redirected back to continue

Key features:
- Single-click authentication
- State preservation during OAuth flow
- No manual URL copying required
- Industry-standard OAuth 2.0 flow

## Configuration

Copy `.streamlit/secrets.example.toml` to `.streamlit/secrets.toml` and fill in your actual API credentials:

```toml
[spotify]
client_id = "your_spotify_client_id"
client_secret = "your_spotify_client_secret"

[youtube]
api_key = "your_youtube_api_key"
```

For production deployments (e.g., Streamlit Cloud), configure the redirect URI:
```toml
[spotify]
client_id = "your_spotify_client_id"
client_secret = "your_spotify_client_secret"
redirect_uri = "https://your-app.streamlit.app/"  # Required for production
```

## Requirements

- Python 3.8+
- YouTube Data API v3 Key
- Spotify Web API Credentials

## License

MIT License - see LICENSE file for details.
