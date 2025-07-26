# Technology Stack & Build System

## Core Technologies

- **Python 3.8+**: Primary language with modern features
- **Streamlit**: Web framework for the user interface
- **YouTube Data API v3**: Playlist extraction and video metadata
- **Spotify Web API**: Song search and playlist creation
- **OAuth 2.0**: Secure authentication flow

## Key Dependencies

```
streamlit>=1.28.0,<2.0.0
requests>=2.31.0,<3.0.0
python-dotenv>=1.0.0,<2.0.0
fuzzywuzzy>=0.18.0,<1.0.0
python-levenshtein>=0.21.0,<1.0.0
```

## Configuration

- **Environment Variables**: All configuration via `.env` files
- **Config Class**: Centralized configuration in `config.py`
- **API Credentials**: YouTube API key, Spotify client ID/secret required
- **Default Redirect URI**: `http://127.0.0.1:8501` for OAuth

## Common Commands

### Setup & Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your API credentials

# Automated setup (recommended)
python setup_youtify.py
```

### Development
```bash
# Run the application
streamlit run main.py

# Run with debug mode
DEBUG_MODE=true streamlit run main.py

# Clear session state (for debugging)
streamlit run main.py?clear_session=true
```

### Testing
```bash
# Run the application
streamlit run main.py

# Test with debug mode
DEBUG_MODE=true streamlit run main.py
```

## API Rate Limits

- **YouTube API**: 10,000 quota units per day
- **Spotify API**: 100 requests per minute
- **Built-in rate limiting**: Automatic delays and retry logic