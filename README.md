# 🎵 Youtify

Transform any YouTube playlist into Spotify playlists with intelligent song matching and a beautiful, modern interface.

## ✨ Features

- **🎯 Smart Matching** - Advanced fuzzy matching algorithms for accurate song identification
- **🔐 Spotify Integration** - Full OAuth authentication for playlist creation
- **🎨 Modern UI** - Spotify-inspired dark theme with smooth animations
- **📊 Interactive Results** - Accept/reject matches with preview functionality
- **⚡ Real-time Progress** - Live progress tracking during conversion
- **📱 Mobile-Friendly** - Responsive design that works on all devices

- **📈 Detailed Analytics** - Confidence scores and match statistics
- **🎧 Audio Previews** - 30-second preview clips for better matching decisions
- **📋 Export Options** - CSV reports and Spotify URI lists

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)
```bash
# Clone the repository
git clone https://github.com/Orsso/youtify-poc.git
cd youtify-poc

# Run the setup script
python setup_youtify.py
```

The setup script will:
- ✅ Check Python version compatibility
- 📦 Install all required dependencies
- 🔧 Create configuration files
- 🔑 Guide you through API credential setup
- 🧪 Test your installation

### Option 2: Manual Setup
1. **Clone and install dependencies**
   ```bash
   git clone https://github.com/Orsso/youtify-poc.git
   cd youtify-poc
   pip install -r requirements.txt
   ```

2. **Configure credentials**
   ```bash
   cp .env.example .env
   # Edit .env with your API credentials
   ```

3. **Get API credentials**
   - **YouTube**: [Google Cloud Console](https://console.cloud.google.com/) → Enable YouTube Data API v3
   - **Spotify**: [Developer Dashboard](https://developer.spotify.com/dashboard/) → Create app
     - ⚠️ **Important**: Add `http://localhost:8501` to your Spotify app's redirect URIs

4. **Run the application**
   ```bash
   streamlit run main.py
   ```

2. **Configure credentials**
   - Click "Start Full Mode" in the app
   - Enter your API credentials
   - Authorize with Spotify
   - Create playlists directly in your account

## 🔄 How It Works

1. **🔗 URL Processing** - Extracts playlist ID from YouTube URL
2. **📹 Video Extraction** - Fetches all video titles and metadata using YouTube API
3. **🎵 Title Parsing** - Intelligent parsing to identify artist and song names
4. **🔍 Smart Search** - Multi-strategy Spotify search:
   - Exact artist + song matching
   - Fuzzy string matching for variations
   - Fallback searches for maximum coverage
5. **🎯 Interactive Matching** - Review and approve uncertain matches
6. **🎧 Audio Previews** - Listen to 30-second clips before deciding
7. **📋 Playlist Creation** - Automatically creates playlist in your Spotify account
8. **📊 Detailed Reports** - Comprehensive analytics and export options

## 🆕 What's New in v2.0

### 🔐 Enhanced Authentication
- **Full Spotify OAuth Integration** - Secure authentication flow
- **Automatic Token Management** - Handles token refresh automatically

### 🎯 Interactive Match Approval
- **Pending Match Review** - Manually approve uncertain matches
- **Multiple Match Options** - Choose from several potential matches
- **Audio Preview Integration** - Listen before deciding
- **Manual Search** - Search for songs that weren't found automatically

### 🎨 Modern UI/UX
- **Spotify-Inspired Design** - Dark theme with green accents
- **Smooth Animations** - Micro-interactions and transitions
- **Album Artwork** - Visual song identification
- **Loading States** - Skeleton screens and progress indicators
- **Mobile Responsive** - Works perfectly on all devices

### ⚡ Performance Improvements
- **Real API Integration** - No more demo data limitations
- **Rate Limiting** - Respects API quotas and limits
- **Error Handling** - Graceful fallbacks and recovery
- **Caching System** - Faster repeated operations

### 📊 Enhanced Analytics
- **Confidence Scoring** - Know how certain each match is
- **Match Statistics** - Detailed conversion metrics
- **Export Options** - CSV reports and Spotify URI lists
- **Processing Insights** - See exactly what happened

## 📋 Requirements

- **Python 3.8+** - Modern Python version
- **YouTube Data API v3 Key** - Free from Google Cloud Console
- **Spotify Web API Credentials** - Free from Spotify Developer Dashboard

## ⚙️ Configuration

The application uses environment variables for configuration. Copy `.env.example` to `.env` and fill in your credentials:

```env
# Required API Credentials
YOUTUBE_API_KEY=your_youtube_api_key_here
SPOTIFY_CLIENT_ID=your_spotify_client_id_here
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret_here

# Optional Settings
HIGH_CONFIDENCE_THRESHOLD=0.8
MEDIUM_CONFIDENCE_THRESHOLD=0.5
LOW_CONFIDENCE_THRESHOLD=0.3
```

## License

MIT License - see LICENSE file for details.
# youtube-to-spotify
