"""QUANT CLI — Theme definitions."""

THEMES = {
    "dark": {
        "name": "Dark Nebula",
        "bg": "#0f0a19",
        "panel": "#0d0117",
        "accent": "#9d4edd",
        "accent_bright": "#bf5fff",
        "accent_dark": "#6e40c9",
        "text": "#dce8ff",
        "text_muted": "#6e6a85",
        "ai_cyan": "#00f5d4",
        "success": "#50fa7b",
        "error": "#ff5555",
        "warning": "#f1fa8c",
        "pink": "#ff79c6",
        "sidebar_border": "#6e40c9",
        "status_bg": "#1a0a2e",
    },
    "purple": {
        "name": "Deep Purple",
        "bg": "#1a0a2e",
        "panel": "#150825",
        "accent": "#bf5fff",
        "accent_bright": "#d4a5ff",
        "accent_dark": "#9d4edd",
        "text": "#e8d5ff",
        "text_muted": "#8b6aae",
        "ai_cyan": "#00f5d4",
        "success": "#50fa7b",
        "error": "#ff5555",
        "warning": "#f1fa8c",
        "pink": "#ff79c6",
        "sidebar_border": "#9d4edd",
        "status_bg": "#251040",
    },
    "neon": {
        "name": "Neon Cyber",
        "bg": "#0a0a0a",
        "panel": "#050505",
        "accent": "#00f5d4",
        "accent_bright": "#00ffea",
        "accent_dark": "#00b4a0",
        "text": "#e0e0e0",
        "text_muted": "#666666",
        "ai_cyan": "#00f5d4",
        "success": "#50fa7b",
        "error": "#ff5555",
        "warning": "#f1fa8c",
        "pink": "#ff79c6",
        "sidebar_border": "#00b4a0",
        "status_bg": "#111111",
    },
}

_current_theme = "dark"

def get_theme(name: str = "") -> dict:
    return THEMES.get(name or _current_theme, THEMES["dark"])

def set_theme(name: str):
    global _current_theme
    if name in THEMES:
        _current_theme = name

def list_themes() -> list[str]:
    return list(THEMES.keys())
