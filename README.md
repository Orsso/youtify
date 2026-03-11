# Youtify [DEPRECATED]

> **This project is deprecated.** As of February 2026, Spotify requires a Premium subscription for the app owner to use the Web API in development mode. See [Spotify's announcement](https://developer.spotify.com/blog/2026-02-06-update-on-developer-access-and-platform-security) for details.

Convert YouTube playlists to Spotify playlists with intelligent song matching.

## Setup

1. Clone and install:
   ```bash
   git clone https://github.com/Orsso/youtify-poc.git
   cd youtify-poc
   pip install -r requirements.txt
   ```

2. Copy `.streamlit/secrets.example.toml` to `.streamlit/secrets.toml` and fill in your API credentials (YouTube Data API v3, Spotify Web API).

3. Run:
   ```bash
   streamlit run main.py
   ```

## License

MIT
