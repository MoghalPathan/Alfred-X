"""
AlfredX — Language Switcher (EN/TR)
===================================
Drop into core/ folder.
Switches all UI labels + TTS/STT + AI system prompt language.
"""


TRANSLATIONS = {
    "en": {
        # Header
        "ALFREDX": "ALFREDX",
        "SUBTITLE": ">>  WAYNECORE ASSISTANT SYSTEM v2.1",
        "SYSTEM_ONLINE": "SYSTEM ONLINE",
        "SYSTEM_OFFLINE": "SYSTEM OFFLINE",
        "SHUTTING_DOWN": "SHUTTING DOWN",

        # Left Panel - AI Core
        "AI_CORE_STATUS": "AI CORE STATUS",
        "ONLINE": "ONLINE",
        "PRIMARY_AI": "PRIMARY AI",
        "LOCAL_AI": "LOCAL AI",
        "MEMORY_SYSTEM": "MEMORY SYSTEM",
        "VOICE_ENGINE": "VOICE ENGINE",
        "CONNECTED": "CONNECTED",
        "DISCONNECTED": "DISCONNECTED",
        "ACTIVE": "ACTIVE",
        "INACTIVE": "INACTIVE",

        # Center Panel - Chat
        "COMMUNICATION_TERMINAL": "COMMUNICATION TERMINAL",
        "ENCRYPTED": "ENCRYPTED",
        "TYPE_COMMAND": "Command Alfred, Master Wayne...",
        "LISTENING": "● LISTENING...",
        "VOICE_ACTIVE": "● VOICE RECOGNITION ACTIVE",
        "MASTER_NAME": "MASTER WAYNE",
        "ALFRED_NAME": "ALFRED",

        # Right Panel
        "QUICK_COMMANDS": "QUICK COMMANDS",
        "SYSTEM_LOG": "SYSTEM LOG",
        "BROWSER": "BROWSER",
        "VS_CODE": "VS CODE",
        "MUSIC": "MUSIC",
        "FILES": "FILES",
        "VISION": "VISION",
        "SEARCH": "SEARCH",

        # Footer
        "SUCCESS_RATE": "SUCCESS RATE",
        "UPTIME": "UPTIME",

        # Settings
        "SETTINGS_TITLE": "ALFREDX SETTINGS",
        "VOICE_RECOGNITION": "VOICE RECOGNITION",
        "TTS_RESPONSES": "TTS RESPONSES",
        "PARTICLE_EFFECTS": "PARTICLE EFFECTS",
        "SCANLINE_OVERLAY": "SCANLINE OVERLAY",
        "SOUND_EFFECTS": "SOUND EFFECTS",

        # Notifications
        "NOTIFICATIONS": "NOTIFICATIONS",
        "NO_NOTIFICATIONS": "No active notifications, Master.",

        # Messages
        "WELCOME": "Welcome back, Master Wayne. All systems operational. How may I serve you today?",
        "SHUTDOWN_MSG": "Initiating shutdown sequence, Master Wayne. All active sessions will be saved. Goodnight, sir.",
        "TRAY_MSG": "Alfred is running in background. Ctrl+Shift+A to summon.",
        "FILE_RECEIVED": "File received and scanned, Master Wayne.",
        "OFFLINE_MSG": "I'm offline, Master. Please set GROQ_API_KEY in .env for AI responses. Local commands work — try 'open browser' or 'what time is it'.",

        # Power dialog
        "POWER_QUESTION": "Initiate system shutdown sequence?",

        # AI system prompt hint
        "AI_LANG_HINT": "Respond in English.",

        # STT/TTS language
        "STT_LANG": "en",
        "TTS_LANG": "en",
    },

    "tr": {
        # Header
        "ALFREDX": "ALFREDX",
        "SUBTITLE": ">>  WAYNECORE ASISTAN SİSTEMİ v2.1",
        "SYSTEM_ONLINE": "SİSTEM AKTİF",
        "SYSTEM_OFFLINE": "SİSTEM KAPALI",
        "SHUTTING_DOWN": "KAPATILIYOR",

        # Left Panel - AI Core
        "AI_CORE_STATUS": "AI ÇEKİRDEK DURUMU",
        "ONLINE": "AKTİF",
        "PRIMARY_AI": "ANA AI",
        "LOCAL_AI": "YEREL AI",
        "MEMORY_SYSTEM": "HAFIZA SİSTEMİ",
        "VOICE_ENGINE": "SES MOTORU",
        "CONNECTED": "BAĞLI",
        "DISCONNECTED": "BAĞLI DEĞİL",
        "ACTIVE": "AKTİF",
        "INACTIVE": "KAPALI",

        # Center Panel - Chat
        "COMMUNICATION_TERMINAL": "İLETİŞİM TERMİNALİ",
        "ENCRYPTED": "ŞİFRELİ",
        "TYPE_COMMAND": "Alfred'e komut verin, Usta Wayne...",
        "LISTENING": "● DİNLİYOR...",
        "VOICE_ACTIVE": "● SES TANIMA AKTİF",
        "MASTER_NAME": "USTA WAYNE",
        "ALFRED_NAME": "ALFRED",

        # Right Panel
        "QUICK_COMMANDS": "HIZLI KOMUTLAR",
        "SYSTEM_LOG": "SİSTEM KAYDI",
        "BROWSER": "TARAYICI",
        "VS_CODE": "VS CODE",
        "MUSIC": "MÜZİK",
        "FILES": "DOSYALAR",
        "VISION": "GÖRÜNTÜ",
        "SEARCH": "ARAMA",

        # Footer
        "SUCCESS_RATE": "BAŞARI ORANI",
        "UPTIME": "ÇALIŞMA SÜRESİ",

        # Settings
        "SETTINGS_TITLE": "ALFREDX AYARLAR",
        "VOICE_RECOGNITION": "SES TANIMA",
        "TTS_RESPONSES": "SES YANITLARI",
        "PARTICLE_EFFECTS": "PARTİKÜL EFEKTLERİ",
        "SCANLINE_OVERLAY": "TARAMA ÇİZGİLERİ",
        "SOUND_EFFECTS": "SES EFEKTLERİ",

        # Notifications
        "NOTIFICATIONS": "BİLDİRİMLER",
        "NO_NOTIFICATIONS": "Aktif bildirim yok, Usta.",

        # Messages
        "WELCOME": "Tekrar hoş geldiniz, Usta Wayne. Tüm sistemler çalışıyor. Size nasıl yardımcı olabilirim?",
        "SHUTDOWN_MSG": "Kapatma sırası başlatılıyor, Usta Wayne. Tüm oturumlar kaydedilecek. İyi geceler, efendim.",
        "TRAY_MSG": "Alfred arka planda çalışıyor. Çağırmak için Ctrl+Shift+A.",
        "FILE_RECEIVED": "Dosya alındı ve tarandı, Usta Wayne.",
        "OFFLINE_MSG": "Çevrimdışıyım, Usta. AI yanıtları için .env'de GROQ_API_KEY ayarlayın. Yerel komutlar çalışır — 'tarayıcı aç' veya 'saat kaç' deneyin.",

        # Power dialog
        "POWER_QUESTION": "Sistem kapatma sırası başlatılsın mı?",

        # AI system prompt hint
        "AI_LANG_HINT": "Türkçe yanıt ver.",

        # STT/TTS language
        "STT_LANG": "tr",
        "TTS_LANG": "tr",
    }
}


class LanguageSwitcher:
    """Manages language state and provides translations."""

    def __init__(self, default="en"):
        self.current = default
        self._callbacks = []

    def get(self, key):
        """Get translated string for current language."""
        return TRANSLATIONS.get(self.current, TRANSLATIONS["en"]).get(key, key)

    def toggle(self):
        """Toggle between EN and TR. Returns new language code."""
        self.current = "tr" if self.current == "en" else "en"
        for cb in self._callbacks:
            try:
                cb(self.current)
            except Exception as e:
                print(f"[Lang] Callback error: {e}")
        return self.current

    def set_language(self, lang):
        """Set specific language."""
        if lang in TRANSLATIONS:
            self.current = lang
            for cb in self._callbacks:
                try:
                    cb(self.current)
                except Exception as e:
                    print(f"[Lang] Callback error: {e}")

    def on_change(self, callback):
        """Register a callback for language changes. callback(lang_code)."""
        self._callbacks.append(callback)

    @property
    def is_english(self):
        return self.current == "en"

    @property
    def is_turkish(self):
        return self.current == "tr"

    @property
    def flag(self):
        return "🇬🇧" if self.current == "en" else "🇹🇷"

    @property
    def label(self):
        return "EN" if self.current == "en" else "TR"