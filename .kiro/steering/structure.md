# Project Structure & Architecture

## Directory Organization

```
youtify/
├── main.py                 # Application entry point
├── config.py              # Centralized configuration
├── requirements.txt       # Python dependencies
├── setup_youtify.py      # Automated setup script
├── .env.example          # Environment template
├── core/                 # Core business logic
│   └── processor.py      # Main playlist processing
├── ui/                   # User interface components
│   └── components.py     # Reusable UI components
├── utils/                # Utility modules
│   ├── proper_oauth_manager.py # OAuth authentication
│   ├── oauth_state_manager.py # OAuth state persistence
│   ├── spotify_manager.py # Spotify API integration
│   ├── youtube_extractor.py # YouTube API integration
│   └── session.py        # Session state management
├── styles/               # CSS styling
│   └── main.css         # Main stylesheet
└── .streamlit/          # Streamlit configuration
    └── config.toml      # Streamlit settings
```

## Architecture Patterns

### Manager Pattern
- **AuthManager**: Handles OAuth flows and authentication state
- **SpotifyManager**: Encapsulates Spotify Web API operations
- **YouTubeExtractor**: Manages YouTube Data API interactions

### Session Management
- **Centralized State**: All state managed through `utils/session.py`
- **State Keys**: Consistent naming (`app_state`, `youtube_url`, `results`)
- **OAuth State**: Proper state preservation during authentication flows

### UI Components
- **Modular Design**: Reusable components in `ui/components.py`
- **Render Functions**: All UI functions prefixed with `render_`
- **State Transitions**: Clean state machine pattern for app flow

## Coding Conventions

### File Naming
- **Snake Case**: All Python files use snake_case
- **Descriptive Names**: Clear, purpose-driven naming
- **Manager Suffix**: API integration classes end with "Manager"

### Function Patterns
- **Private Methods**: Prefix with underscore (`_validate_credentials`)
- **Render Functions**: UI functions start with `render_`
- **Handler Functions**: Event handlers start with `handle_`

### Error Handling
- **Logging**: Use Python logging module throughout
- **Graceful Degradation**: Fallback options for API failures
- **User-Friendly Messages**: Clear error messages in UI

### Configuration
- **Environment First**: All config via environment variables
- **Centralized**: Single `Config` class in `config.py`
- **Validation**: Built-in credential validation methods