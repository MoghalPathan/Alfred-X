from dotenv import load_dotenv
import os

load_dotenv()

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS", "")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID", "")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI", "https://localhost:8888/callback")

"""
AlfredX: The Waynecore Assistant — Configuration
"""
import os
from dotenv import load_dotenv
load_dotenv()

# ─── IDENTITY ──────────────────────────────────────────
AI_NAME = "AlfredX"
AI_TITLE = "The Waynecore Assistant"
AI_VERSION = "2.1.0"

# ─── WINTER SOLDIER PROTOCOL ──────────────────────────
ACTIVATION_WORDS = [
    "Thomas",  "Martha","Shadow", "Legacy", "Protocol",
    
    "Guardian", "Vengeance", "Justice", "Batman", "Activate"
]

# Accepted pronunciations / similar-sounding words for each activation word
WORD_VARIANTS = {
    "thomas": ["thomas", "tomas", "tomas", "thomis", "thomus","tom", "tommus", "thomaz", "thomes", "toma","thama", "thammas", "tomis", "thoms","tomaz", "thomaa", "tomasz", "thomar", "thomarz", "thomar"],
    "shadow":     ["shadow", "shado", "shadoe", "shadows"],
    "martha": ["martha", "martha", "marta", "marthah", "marhta","marthaa", "martah", "martaah", "marth","maartha", "marthaa", "marthaah", "mardha", "marza","martae", "marta", "marthae", "marthae", "marthaan", "marthaas"],
    "legacy":     ["legacy", "legasy", "legaci", "legacee"],
    "protocol":   ["protocol", "protocal", "proto", "protokol", "protocols"],
    "guardian":   ["guardian", "gardian", "guardin", "garden"],
    "vengeance":  ["vengeance", "vengence", "vengance", "vengens", "venjance"],
    "justice":    ["justice", "justis", "justus", "justise"],
    "batman":     ["batman", "batmen", "bat man", "badman", "batsman", "back man"],
    "activate":   ["activate", "activat", "activeit", "activated"],
}
TEXT_PASSWORD = "MEZEYAT"

# ─── LANGUAGE ──────────────────────────────────────────
LANGUAGES = {
    "en": {
        "name": "English",
        "tts_voice": "en-GB-RyanNeural",
        "greeting": "Good evening, Master. AlfredX at your service.",
        "persona": (
            "You are AlfredX, the Waynecore Assistant — a supremely intelligent, "
            "loyal AI butler inspired by Alfred Pennyworth from DC Comics and JARVIS from Marvel. "
            "You speak in formal British English with dry wit, elegance, and unwavering composure. "
            "You address the user as 'Master' or 'Sir'. You are resourceful, discreet, and always prepared. "
            "Keep responses concise but insightful. Never break character."
        ),
    },
    "tr": {
        "name": "Turkce",
        "tts_voice": "tr-TR-AhmetNeural",
        "greeting": "Iyi aksamlar, Efendim. AlfredX hizmetinizde.",
        "persona": (
            "Sen AlfredX, Waynecore Asistanisin — DC Comics'teki Alfred Pennyworth ve "
            "Marvel'daki JARVIS'ten ilham alan son derece zeki ve sadik bir yapay zeka usagisin. "
            "Samimi ama saygili bir Turkce kullan. Kullaniciya 'Efendim' diye hitap et. "
            "Kisa ama oz cevaplar ver. Karakterinden cikma."
        ),
    },
}
DEFAULT_LANGUAGE = "en"

# ─── AI ENGINE ─────────────────────────────────────────
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_MODEL = "llama-3.3-70b-versatile"
MAX_TOKENS = 1024
TEMPERATURE = 0.7

# ─── OLLAMA (LOCAL) ────────────────────────────────────
OLLAMA_MODEL = "llama3.2:3b"
OLLAMA_BASE_URL = "http://localhost:11434"

# ─── FREE API KEYS ─────────────────────────────────────
WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY", "")
NEWS_API_KEY = os.environ.get("NEWS_API_KEY", "")

# ─── EMAIL ─────────────────────────────────────────
GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS", "")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")

# ─── GUI THEME ─────────────────────────────────────────
COLORS = {
    "bg_primary": "#0a0a0f",
    "bg_secondary": "#0d1117",
    "bg_panel": "#111827",
    "bg_input": "#1a1a2e",
    "accent_cyan": "#00d4ff",
    "accent_teal": "#00ffcc",
    "accent_blue": "#1e90ff",
    "accent_gold": "#ffd700",
    "text_primary": "#e0e6ed",
    "text_secondary": "#8899aa",
    "text_dim": "#4a5568",
    "border": "#1e3a5f",
    "danger": "#ff3333",
    "success": "#00ff88",
    "warning": "#ffaa00",
}

# ─── PATHS ─────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
KNOWLEDGE_DIR = os.path.join(DATA_DIR, "knowledge")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

os.makedirs(KNOWLEDGE_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)
