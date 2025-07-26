"""
Shared UI Styles and Constants
"""

# CSS Variables for consistent styling
GLASSMORPHISM_CSS = """
<style>
:root {
    --glass-bg: rgba(255, 255, 255, 0.05);
    --glass-backdrop: blur(10px);
    --glass-border: rgba(255, 255, 255, 0.1);
    --glass-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
    --border-radius: 12px;
    --text-primary: #ffffff;
    --text-secondary: #cccccc;
    --text-muted: #888888;
}

.conversion-card {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    padding: 1rem;
    margin: 0.5rem 0;
    background: var(--glass-bg);
    backdrop-filter: var(--glass-backdrop);
    border: 1px solid var(--glass-border);
    border-radius: var(--border-radius);
    box-shadow: var(--glass-shadow);
}

.conversion-card-content {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.youtube-side, .spotify-side {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.side-title {
    font-weight: 500;
    color: var(--text-primary);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.side-artist {
    font-size: 0.875rem;
    color: var(--text-secondary);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.side-meta {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 0.5rem;
}

.status-indicator {
    display: inline-flex;
    align-items: center;
    gap: 0.25rem;
    padding: 0.25rem 0.5rem;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 500;
}

.status-indicator.processing {
    background: rgba(255, 107, 53, 0.2);
    color: #FF6B35;
}

.status-indicator.found {
    background: rgba(29, 185, 84, 0.2);
    color: #1DB954;
}

.status-indicator.not-found {
    background: rgba(255, 68, 68, 0.2);
    color: #FF4444;
}

.status-icon {
    width: 8px;
    height: 8px;
    border-radius: 50%;
}

.processing-icon {
    background: #FF6B35;
    animation: pulse 1.5s ease-in-out infinite;
}

.found-icon {
    background: #1DB954;
}

.not-found-icon {
    background: #FF4444;
}

.confidence-score {
    font-size: 0.75rem;
    font-weight: 500;
    padding: 0.25rem 0.5rem;
    border-radius: 12px;
}

.confidence-score.high {
    background: rgba(29, 185, 84, 0.2);
    color: #1DB954;
}

.confidence-score.medium {
    background: rgba(255, 193, 7, 0.2);
    color: #FFC107;
}

.confidence-score.low {
    background: rgba(255, 68, 68, 0.2);
    color: #FF4444;
}

.spotify-side.loading {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.loading-placeholder {
    background: linear-gradient(90deg, rgba(255,255,255,0.1) 25%, rgba(255,255,255,0.2) 50%, rgba(255,255,255,0.1) 75%);
    background-size: 200% 100%;
    animation: loading 1.5s ease-in-out infinite;
    border-radius: 4px;
}

.loading-placeholder.wide {
    height: 1.2rem;
    width: 80%;
}

.loading-placeholder.narrow {
    height: 0.9rem;
    width: 60%;
}

@keyframes loading {
    0% { background-position: 200% 0; }
    100% { background-position: -200% 0; }
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

.youtube-song-card {
    opacity: 0;
    animation: fadeIn 0.3s ease-out forwards;
}

@keyframes fadeIn {
    to { opacity: 1; transform: translateY(0); }
}

.conversion-card.processing-transform {
    animation: transformProcessing 0.5s ease-out forwards;
}

.conversion-card.found-transform {
    animation: transformFound 0.5s ease-out forwards;
}

.conversion-card.not-found-transform {
    animation: transformNotFound 0.5s ease-out forwards;
}

@keyframes transformProcessing {
    0% { border-color: var(--glass-border); }
    100% { border-color: rgba(255, 107, 53, 0.5); }
}

@keyframes transformFound {
    0% { border-color: var(--glass-border); }
    100% { border-color: rgba(29, 185, 84, 0.5); }
}

@keyframes transformNotFound {
    0% { border-color: var(--glass-border); }
    100% { border-color: rgba(255, 68, 68, 0.5); }
}

@media (min-width: 768px) {
    .conversion-card-content {
        flex-direction: row;
        gap: 1.5rem;
    }
    
    .youtube-side, .spotify-side {
        flex: 1;
    }
}
</style>
"""

# Common styling constants
CARD_STYLES = {
    "background": "rgba(255, 255, 255, 0.05)",
    "backdrop_filter": "blur(10px)",
    "border": "1px solid rgba(255, 255, 255, 0.1)",
    "border_radius": "12px",
    "box_shadow": "0 4px 16px rgba(0, 0, 0, 0.2)",
    "padding": "0.75rem",
    "margin": "0.5rem 0"
}

PLAYLIST_CARD_STYLES = {
    "background": "rgba(255, 107, 53, 0.1)",
    "backdrop_filter": "blur(10px)",
    "border": "1px solid rgba(255, 107, 53, 0.2)",
    "border_radius": "16px",
    "padding": "2rem",
    "text_align": "center",
    "box_shadow": "0 8px 32px rgba(0, 0, 0, 0.3)",
    "margin": "1rem 0"
}

SUCCESS_CARD_STYLES = {
    "background": "linear-gradient(135deg, #1DB954 0%, #1ed760 100%)",
    "padding": "2rem",
    "border_radius": "16px",
    "text_align": "center",
    "margin": "1rem 0 2rem 0",
    "box_shadow": "0 8px 32px rgba(29, 185, 84, 0.3)"
}