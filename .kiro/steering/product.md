# Youtify - Product Overview

Youtify is a YouTube to Spotify playlist converter that transforms YouTube playlists into Spotify playlists using intelligent song matching algorithms.

## Core Features

- **Smart Song Matching**: Uses fuzzy matching algorithms (fuzzywuzzy) to accurately identify songs across platforms
- **Spotify OAuth Integration**: Full OAuth 2.0 flow for secure playlist creation in user accounts
- **Interactive Match Review**: Users can approve/reject uncertain matches with audio previews
- **Real-time Processing**: Live progress tracking during conversion with modern UI
- **Modern Interface**: Spotify-inspired dark theme with responsive design

## User Flow

1. User enters YouTube playlist URL
2. App extracts video titles using YouTube Data API v3
3. Intelligent parsing identifies artist and song names
4. Multi-strategy Spotify search with confidence scoring
5. Interactive review of uncertain matches
6. OAuth authentication for playlist creation
7. Automatic playlist creation in user's Spotify account

## Key Value Propositions

- No manual song-by-song conversion needed
- High accuracy through intelligent matching
- Seamless OAuth experience with state preservation
- Professional-grade error handling and rate limiting
- Export options for analytics and reporting