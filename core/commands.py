"""
AlfredX: Command Handler v2.1 — PEAK EDITION
All local commands -- instant response, no AI needed.
45+ command categories with smart synonym matching.
"""
import os
import re
import sys
import glob
import json
import math
import socket
import random
import string
import hashlib
import subprocess
import platform
import threading
import webbrowser
import time
import base64
import struct
import sched
import colorsys
import smtplib
import imaplib
import email as email_lib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from pathlib import Path
from config import WEATHER_API_KEY, NEWS_API_KEY, GMAIL_ADDRESS, GMAIL_APP_PASSWORD, \
                   SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI

# ── Poetry ──
POETRY_FILE = Path("data/naved_poetry.json")
POETRY_STATE = Path("data/poetry_state.json")



try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

try:
    import spotipy
    from spotipy.oauth2 import SpotifyOAuth
    SPOTIPY_AVAILABLE = True
except ImportError:
    SPOTIPY_AVAILABLE = False


try:
    import wikipedia
    WIKI_AVAILABLE = True
except ImportError:
    WIKI_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class CommandHandler:
    def __init__(self):
        self.timers = []
        self.reminders = []
        self.todos = []
        self.memories = {}
        self.command_history = []
        self._reminder_callback = None
        self.system = platform.system()

        # Music (isolated process so TTS can't stop playback)
        self._music_proc = None
        self._sp = None

        self.app_map = {
            "chrome": "chrome", "google chrome": "chrome", "browser": "chrome",
            "firefox": "firefox", "notepad": "notepad", "notes": "notepad",
            "calculator": "calc", "calc": "calc",
            "explorer": "explorer", "file explorer": "explorer",
            "this pc": "explorer shell:MyComputerFolder",
            "my computer": "explorer shell:MyComputerFolder",
            "my pc": "explorer shell:MyComputerFolder",
            "terminal": "cmd", "command prompt": "cmd", "cmd": "cmd",
            "powershell": "powershell",
            "vscode": "code", "visual studio code": "code", "vs code": "code",
            "spotify": "spotify", "discord": "discord", "steam": "steam",
            "word": "winword", "excel": "excel", "powerpoint": "powerpnt",
            "paint": "mspaint", "task manager": "taskmgr",
            "control panel": "control", "settings": "ms-settings:",
            "snipping tool": "snippingtool", "snip": "snippingtool",
            "brave": "brave", "edge": "msedge", "microsoft edge": "msedge",
            "vlc": "vlc", "obs": "obs64",
            "photos": "ms-photos:", "camera": "microsoft.windows.camera:",
            "maps": "bingmaps:", "store": "ms-windows-store:",
            "clock": "ms-clock:", "alarm": "ms-clock:",
            "mail": "outlookmail:", "calendar": "outlookcal:",
            "weather app": "bingweather:",
            "whatsapp": "whatsapp", "telegram": "telegram",
            "zoom": "zoom", "teams": "msteams",
        }

        self.website_map = {
            "youtube": "https://www.youtube.com",
            "google": "https://www.google.com",
            "gmail": "https://mail.google.com",
            "github": "https://github.com",
            "stackoverflow": "https://stackoverflow.com",
            "stack overflow": "https://stackoverflow.com",
            "reddit": "https://www.reddit.com",
            "twitter": "https://twitter.com",
            "x": "https://x.com",
            "facebook": "https://www.facebook.com",
            "instagram": "https://www.instagram.com",
            "linkedin": "https://www.linkedin.com",
            "whatsapp web": "https://web.whatsapp.com",
            "netflix": "https://www.netflix.com",
            "amazon": "https://www.amazon.com",
            "wikipedia": "https://www.wikipedia.org",
            "chatgpt": "https://chat.openai.com",
            "claude": "https://claude.ai",
            "spotify web": "https://open.spotify.com",
            "maps": "https://maps.google.com",
            "google maps": "https://maps.google.com",
            "google drive": "https://drive.google.com",
            "google docs": "https://docs.google.com",
            "outlook": "https://outlook.live.com",
            "yahoo": "https://www.yahoo.com",
            "bing": "https://www.bing.com",
            "pinterest": "https://www.pinterest.com",
            "twitch": "https://www.twitch.tv",
            "discord": "https://discord.com/app",
            "canva": "https://www.canva.com",
            "figma": "https://www.figma.com",
            "notion": "https://www.notion.so",
            "trello": "https://trello.com",
            "medium": "https://medium.com",
        }

        self._load_persistent_data()

    def _load_persistent_data(self):
        data_file = os.path.join(os.path.expanduser("~"), ".alfredx_data.json")
        try:
            if os.path.exists(data_file):
                with open(data_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.todos = data.get("todos", [])
                    self.memories = data.get("memories", {})
        except Exception:
            pass

    def _save_persistent_data(self):
        data_file = os.path.join(os.path.expanduser("~"), ".alfredx_data.json")
        try:
            with open(data_file, "w", encoding="utf-8") as f:
                json.dump({"todos": self.todos, "memories": self.memories}, f, indent=2)
        except Exception:
            pass

    def set_reminder_callback(self, callback):
        self._reminder_callback = callback

    def process(self, text):
        if not text or not str(text).strip():
            return False, ""

        cmd = str(text).lower().strip()
        self.command_history.append({
            "cmd": str(text),
            "time": datetime.now().strftime("%H:%M:%S")
        })

        check_names = [
            "_check_poetry", "_check_time", "_check_date", "_check_reminder",
            "_check_windows_settings","_check_email",
            "_check_weather", "_check_news",
            "_check_spotify", "_check_local_music", "_check_youtube",
            "_check_open_website",
            "_check_open_folder", "_check_close_folder",
            "_check_open_app", "_check_close_app",
            "_check_web_search", "_check_wikipedia",
            "_check_volume", "_check_media",
            "_check_system_control", "_check_timer",
            "_check_ocr", "_check_screenshot",
            "_check_todo", "_check_calculator", "_check_dictionary",
            "_check_translate", 
            "_check_internet_speed", "_check_process_list", "_check_kill_all",
            "_check_file_operations", "_check_file_search",
            "_check_scheduled_shutdown", "_check_disk_space",
            "_check_jokes", "_check_quotes", "_check_coin_dice",
            "_check_password_generator", "_check_unit_converter",
            "_check_currency", "_check_location",
            "_check_learning_mode", "_check_command_history",
            "_check_system_info", "_check_battery", "_check_ip_address",
            "_check_wifi_info", "_check_clipboard", "_check_brightness",
            "_check_webcam", "_check_screen_record",
            "_check_qr_code", "_check_text_to_pdf",
            "_check_whatsapp", "_check_google_maps",
            "_check_startup_apps", "_check_hash",
            "_check_typing_speed", "_check_color_picker",
            "_check_task_scheduler", "_check_smart_home",
            "_check_google_calendar",
        ]

        friendly = {
            "ConnectionError": "No internet connection detected, Master.",
            "TimeoutError": "That request timed out, Master.",
            "FileNotFoundError": "I couldn't find that file/app, Master.",
            "PermissionError": "Permission denied, Master. Try running as administrator.",
            "OSError": "A system error occurred, Master.",
            "ImportError": "A required module is missing, Master. Try: pip install <module_name>",
        }

        for name in check_names:
            fn = getattr(self, name, None)
            if not callable(fn):
                continue
            try:
                out = fn(cmd)
                if not out:
                    continue
                if isinstance(out, (tuple, list)) and len(out) >= 2:
                    handled, response = out[0], out[1]
                    if handled:
                        return True, response if str(response).strip() else "Done, Master."
                else:
                    continue
            except Exception as e:
                et = type(e).__name__
                msg = friendly.get(et, f"Something went wrong, Master: {str(e)[:120]}")
                return True, msg

        return False, ""
    
    # ===================== POETRY =====================

    def _check_poetry(self, cmd):
        triggers = ["poetry", "poem", "shayari", "nazm", "sher", "gazal"]
        if not any(t in cmd for t in triggers):
            return False, ""
        try:
            poems = json.loads(POETRY_FILE.read_text(encoding="utf-8"))
        except Exception:
            return True, "Poetry file not found, Master. Make sure data/naved_poetry.json exists."
        try:
            state = json.loads(POETRY_STATE.read_text(encoding="utf-8"))
        except Exception:
            state = {"index": -1}
        idx = (state.get("index", -1) + 1) % len(poems)
        POETRY_STATE.write_text(json.dumps({"index": idx}), encoding="utf-8")
        p = poems[idx]
        return True, f"{p['content']}\n\n— {p['author']}"

    
    # ===================== TIME & DATE =====================
    def _check_time(self, cmd):
        triggers = ["what time", "current time", "tell me the time", "time now",
                    "what's the time", "whats the time", "show time", "saat kac",
                    "time please", "give me the time", "tell time", "kitna baj"]
        if any(t in cmd for t in triggers):
            now = datetime.now()
            return True, f"The current time is {now.strftime('%I:%M %p')}, Master."
        return False, ""

    def _check_date(self, cmd):
        triggers = ["what day", "what date", "today's date", "what is today",
                    "whats today", "todays date", "current date", "tell me the date",
                    "date today", "show date", "bugun ne", "give me the date",
                    "aaj ka din", "aaj kya hai"]
        if any(t in cmd for t in triggers):
            now = datetime.now()
            return True, f"Today is {now.strftime('%A, %B %d, %Y')}, Master."
        return False, ""

    # ===================== REMINDERS =====================
    def _check_reminder(self, cmd):
        text = (cmd or "").strip()

        p_task_first = r"(?:set\s+(?:a\s+)?)?remind(?:er)?\s*(?:me\s*)?(?:to\s*)?(?P<task>.+?)\s+(?:in|after)\s+(?P<num>\d+)\s*(?P<unit>seconds?|secs?|sec|minutes?|mins?|min|hours?|hrs?|hr)\b"
        m = re.search(p_task_first, text, re.I)

        if not m:
            p_time_first = r"(?:set\s+(?:a\s+)?)?remind(?:er)?\s*(?:me\s*)?(?:in|after)\s+(?P<num>\d+)\s*(?P<unit>seconds?|secs?|sec|minutes?|mins?|min|hours?|hrs?|hr)\s*(?:to\s*)?(?P<task>.+)"
            m = re.search(p_time_first, text, re.I)

        if m:
            task = (m.group('task') or '').strip(" .,")
            amount = int(m.group('num'))
            unit = (m.group('unit') or '').lower()

            if unit.startswith('min'):
                seconds = amount * 60
                unit_label = 'minute'
            elif unit.startswith('hr') or unit.startswith('hour'):
                seconds = amount * 3600
                unit_label = 'hour'
            else:
                seconds = amount
                unit_label = 'second'

            trigger_time = datetime.now() + timedelta(seconds=seconds)
            self._start_reminder(seconds, task)
            self.reminders.append({"task": task, "time": trigger_time.strftime("%H:%M")})
            return True, f"Reminder set, Master. I'll remind you to '{task}' in {amount} {unit_label}(s)."

        pattern2 = r"remind (?:me )?(?:to )?(.+?)(?:\s+at\s+)(\d{1,2}):?(\d{2})?\s*(am|pm)?"
        match2 = re.search(pattern2, text, re.I)
        if match2:
            task = match2.group(1).strip()
            hour = int(match2.group(2))
            minute = int(match2.group(3) or 0)
            period = (match2.group(4) or "").lower()

            if period == "pm" and hour < 12:
                hour += 12
            elif period == "am" and hour == 12:
                hour = 0

            now = datetime.now()
            target = now.replace(hour=hour, minute=minute, second=0)
            if target <= now:
                target += timedelta(days=1)

            self._start_reminder(int((target - now).total_seconds()), task)
            self.reminders.append({"task": task, "time": target.strftime("%H:%M")})
            return True, f"Reminder set for {target.strftime('%I:%M %p')}, Master."

        low = text.lower()
        if any(t in low for t in ["show reminder", "my reminder", "list reminder",
                                   "show reminders", "my reminders", "list reminders",
                                   "what reminders", "any reminders"]):
            if not self.reminders:
                return True, "No active reminders, Master."
            lines = ["Active reminders:"]
            for i, r in enumerate(self.reminders, 1):
                lines.append(f"{i}. {r['task']} -- at {r['time']}")
            return True, "\n".join(lines)

        return False, ""

    def _start_reminder(self, seconds, task):
        def _alert():
            print(f"[Reminder] {task}")
            if self._reminder_callback:
                try:
                    self._reminder_callback(task)
                except Exception:
                    pass
            try:
                if self.system == "Windows":
                    import winsound
                    winsound.Beep(800, 300)
                    winsound.Beep(1000, 300)
            except Exception:
                pass
        timer = threading.Timer(seconds, _alert)
        timer.daemon = False
        timer.start()
        self.timers.append(timer)

    # ===================== WINDOWS SETTINGS =====================
    def _check_windows_settings(self, cmd):
        if self.system != "Windows":
            return False, ""

        settings_map = {
            ("night light", "night mode", "blue light", "nightlight", "eye comfort"):
                ("ms-settings:nightlight", "Night Light"),
            ("hotspot", "mobile hotspot", "hot spot", "tethering", "share internet"):
                ("ms-settings:network-mobilehotspot", "Mobile Hotspot"),
            ("bluetooth", "blue tooth", "bt device", "pair device"):
                ("ms-settings:bluetooth", "Bluetooth"),
            ("airplane", "flight mode", "aeroplane"):
                ("ms-settings:network-airplanemode", "Airplane mode"),
            ("display settings", "screen settings", "monitor settings"):
                ("ms-settings:display", "Display"),
            ("sound settings", "audio settings", "speaker settings"):
                ("ms-settings:sound", "Sound"),
            ("focus mode", "do not disturb", "dnd", "focus assist"):
                ("ms-settings:quiethours", "Focus"),
            ("wallpaper", "background", "theme", "personalization"):
                ("ms-settings:personalization", "Personalization"),
            ("privacy settings", "privacy"):
                ("ms-settings:privacy", "Privacy"),
            ("update", "windows update", "check for updates"):
                ("ms-settings:windowsupdate", "Windows Update"),
            ("storage", "storage settings", "disk cleanup"):
                ("ms-settings:storagesense", "Storage"),
            ("default apps", "default programs"):
                ("ms-settings:defaultapps", "Default Apps"),
            ("mouse settings", "cursor settings"):
                ("ms-settings:mousetouchpad", "Mouse"),
            ("keyboard settings",):
                ("ms-settings:keyboard", "Keyboard"),
            ("battery settings", "power settings", "power plan"):
                ("ms-settings:batterysaver", "Battery/Power"),
        }

        for triggers, (uri, name) in settings_map.items():
            if any(t in cmd for t in triggers):
                subprocess.Popen(f"start {uri}", shell=True)
                return True, f"Opening {name} settings, Master."

        if ("wifi" in cmd or "wi-fi" in cmd or "wireless" in cmd) and any(
                t in cmd for t in ["turn on", "turn off", "enable", "disable",
                                   "connect", "disconnect", "settings"]):
            subprocess.Popen("start ms-settings:network-wifi", shell=True)
            return True, "Opening WiFi settings, Master."

        return False, ""

    # ===================== YOUTUBE =====================
    def _check_youtube(self, cmd):
        yt_play = re.search(r"(?:play|watch)\s+(?:on\s+)?(?:youtube\s+)?(.+?)(?:\s+on\s+youtube)?$", cmd)
        play_on_yt = re.search(r"play\s+(.+?)\s+on\s+youtube", cmd)

        # Determine if this is a PLAY command
        is_play = (("youtube" in cmd and yt_play) or play_on_yt)

        if is_play:
            query = ""
            if play_on_yt:
                query = play_on_yt.group(1).strip()
            elif yt_play:
                query = yt_play.group(1).strip()
                query = re.sub(r"\s*on\s+youtube\s*$", "", query).strip()
                query = re.sub(r"^youtube\s+", "", query).strip()

            if query:
                return self._youtube_play_first(query)

        # SEARCH only (no auto-play)
        yt_search = re.search(r"(?:search|find)\s+(?:on\s+)?youtube\s+(?:for\s+)?(.+)", cmd)
        if not yt_search:
            yt_search = re.search(r"youtube\s+(?:search|find)\s+(?:for\s+)?(.+)", cmd)
        if yt_search:
            query = yt_search.group(1).strip()
            webbrowser.open(f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}")
            return True, f"Searching YouTube for '{query}', Master."

        # DOWNLOAD
        if any(t in cmd for t in ["download youtube", "youtube download", "download video",
                               "download from youtube", "yt download"]):
            url_match = re.search(r"(https?://\S+)", cmd)
            if url_match:
                return self._youtube_download(url_match.group(1))
            return True, "Please provide the YouTube URL, Master."

        return False, ""

    def _youtube_play_first(self, query):
        """Fetch first YouTube result using yt-dlp and open it directly."""
        try:
            result = subprocess.run(
                ["yt-dlp", "--get-id", f"ytsearch1:{query}"],
                capture_output=True, text=True, timeout=15
            )
            video_id = result.stdout.strip()
            if video_id:
                url = f"https://www.youtube.com/watch?v={video_id}"
                webbrowser.open(url)
                return True, f"Playing '{query}' on YouTube, Master."
            else:
                # Fallback to search if yt-dlp fails
                webbrowser.open(f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}")
                return True, f"Couldn't auto-play, searching YouTube for '{query}', Master."
        except FileNotFoundError:
            # yt-dlp not installed, fallback
            webbrowser.open(f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}")
            return True, f"Install yt-dlp for auto-play. Searching instead, Master."
        except Exception as e:
            webbrowser.open(f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}")
            return True, f"Searching YouTube for '{query}', Master."

    def _youtube_download(self, url):
        downloads = os.path.join(os.path.expanduser("~"), "Downloads")
        try:
            result = subprocess.run(["yt-dlp", "--version"], capture_output=True, text=True, timeout=5)
            if result.returncode != 0:
                raise FileNotFoundError
        except Exception:
            return True, "yt-dlp not installed, Master. Run: pip install yt-dlp"

        def _download():
            try:
                subprocess.run([
                    "yt-dlp", "-o", os.path.join(downloads, "%(title)s.%(ext)s"),
                    "--no-playlist", url
                ], timeout=300)
                if self._reminder_callback:
                    self._reminder_callback("YouTube download complete!")
            except Exception as e:
                print(f"[YT Download] Error: {e}")

            threading.Thread(target=_download, daemon=True).start()
            return True, f"Downloading from YouTube, Master.\nSaving to: {downloads}"
    
    # ===================== OPEN WEBSITE =====================
    def _check_open_website(self, cmd):
        for p in [r"(?:open|go to|visit|browse|launch)\s+(.+?)(?:\s+website)?$"]:
            m = re.search(p, cmd)
            if m:
                site = m.group(1).strip().rstrip(".")
                url = self.website_map.get(site.lower())
                if url:
                    webbrowser.open(url)
                    return True, f"Opening {site}, Master."
                if "." in site and " " not in site:
                    if not site.startswith("http"):
                        site = "https://" + site
                    webbrowser.open(site)
                    return True, f"Opening {site}, Master."
        return False, ""

    # ===================== SPOTIFY =====================
#  ─────────────────────────────────────────────────────────
#  "play [song/artist] on spotify"      → search & play
#  "play spotify [song]"                → search & play
#  "pause spotify"                      → pause playback
#  "resume spotify"                     → resume playback
#  "next spotify" / "skip spotify"      → skip to next track
#  "previous spotify" / "back spotify"  → go to previous track
#  "what's playing on spotify"          → show current track
#  "spotify volume 70"                  → set volume (0–100)
#  "shuffle spotify on/off"             → toggle shuffle
#  "repeat spotify on/off"              → toggle repeat
#  "open spotify"                       → open Spotify app
# ============================================================

    def _get_sp(self):
        """
        Lazy-initialise spotipy client with OAuth.
        Returns (client, error_string). If error, client is None.
        First call opens a browser for Spotify login (one-time only).
        """
        if self._sp is not None:
            return self._sp, None

        if not SPOTIPY_AVAILABLE:
            return None, "spotipy not installed. Run: pip install spotipy"

        if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
            return None, (
                "Spotify credentials missing, Master.\n"
                "Add to your .env file:\n"
                "  SPOTIFY_CLIENT_ID=your_id\n"
                "  SPOTIFY_CLIENT_SECRET=your_secret\n"
                "  SPOTIFY_REDIRECT_URI=https://localhost:8888/callback"
            )

        scopes = (
            "user-read-playback-state "
            "user-modify-playback-state "
            "user-read-currently-playing "
            "streaming "
            "playlist-read-private "
            "user-library-read"
        )

        try:
            auth = SpotifyOAuth(
                client_id=SPOTIFY_CLIENT_ID,
                client_secret=SPOTIFY_CLIENT_SECRET,
                redirect_uri=SPOTIFY_REDIRECT_URI,
                scope=scopes,
                cache_path=".spotify_cache",
                open_browser=True,
            )
            self._sp = spotipy.Spotify(auth_manager=auth)
            # Quick check that auth worked
            self._sp.current_user()
            return self._sp, None
        except Exception as e:
            self._sp = None
            return None, f"Spotify auth failed: {str(e)[:120]}"



    def _check_spotify(self, cmd):
        """Full Spotify control via spotipy."""

        # ── Trigger guard ────────────────────────────────────────
        spotify_keywords = [
            "spotify", "play song", "play track", "play artist",
            "play playlist", "skip spotify", "next spotify",
            "pause spotify", "resume spotify", "previous spotify",
            "shuffle spotify", "repeat spotify", "what's playing",
            "whats playing", "spotify volume", "back spotify",
        ]
        if not any(k in cmd for k in spotify_keywords):
            return False, ""

        # ── Helper: get active device ────────────────────────────
        def _get_device_id(sp):
            """Return the first active device id, or None."""
            try:
                devices = sp.devices().get("devices", [])
                if not devices:
                   return None
                # Prefer the currently active device
                for d in devices:
                    if d.get("is_active"):
                        return d["id"]
                return devices[0]["id"]
            except Exception:
                return None

        # ── Helper: ensure Spotify app is running ────────────────
        def _ensure_spotify_open():
            """Open Spotify desktop app if no devices found."""
            try:
                if self.system == "Windows":
                    # Check if already running
                    if PSUTIL_AVAILABLE:
                        for proc in psutil.process_iter(["name"]):
                            try:
                                if "spotify" in proc.info["name"].lower():
                                    return
                            except Exception:
                                pass
                    subprocess.Popen("start spotify", shell=True)
                    time.sleep(4)  # Give Spotify time to register as a device
            except Exception:
                pass

        # ══════════════════════════════════════════════════════════
        #  OPEN SPOTIFY (no auth needed)
        # ══════════════════════════════════════════════════════════
        if any(t in cmd for t in ["open spotify", "launch spotify", "start spotify"]):
            try:
                if self.system == "Windows":
                    subprocess.Popen("start spotify", shell=True)
                return True, "Opening Spotify, Master."
            except Exception:
                return True, "Couldn't open Spotify, Master."

        # ══════════════════════════════════════════════════════════
        #  AUTH
        # ══════════════════════════════════════════════════════════
        sp, err = self._get_sp()
        if not sp:
            return True, err

        # ══════════════════════════════════════════════════════════
        #  WHAT'S PLAYING
        # ══════════════════════════════════════════════════════════
        if any(t in cmd for t in ["what's playing", "whats playing", "now playing",
                                   "current song", "current track", "what song"]):
            try:
                pb = sp.current_playback()
                if not pb or not pb.get("item"):
                    return True, "Nothing is playing on Spotify right now, Master."
                item = pb["item"]
                track = item["name"]
                artist = ", ".join(a["name"] for a in item["artists"])
                album = item["album"]["name"]
                is_playing = pb["is_playing"]
                state = "▶ Playing" if is_playing else "⏸ Paused"
                duration_ms = item["duration_ms"]
                progress_ms = pb["progress_ms"]
                mins_total = duration_ms // 60000
                secs_total = (duration_ms % 60000) // 1000
                mins_prog = progress_ms // 60000
                secs_prog = (progress_ms % 60000) // 1000
                return True, (
                    f"{state}: {track}\n"
                    f"Artist: {artist}\n"
                    f"Album: {album}\n"
                    f"Time: {mins_prog}:{secs_prog:02d} / {mins_total}:{secs_total:02d}"
                )
            except Exception as e:
                return True, f"Couldn't get current track: {str(e)[:80]}"

        # ══════════════════════════════════════════════════════════
        #  PLAY  (search + play first result)
        # ══════════════════════════════════════════════════════════
        play_match = (
            re.search(r"play\s+(.+?)\s+on\s+spotify", cmd) or
            re.search(r"play\s+spotify\s+(.+)", cmd) or
            re.search(r"play\s+(?:song|track|music|artist|playlist)\s+(.+?)(?:\s+on\s+spotify)?$", cmd)
        )
        if play_match:
            query = play_match.group(1).strip()

            # Ensure Spotify is open as a device
            _ensure_spotify_open()
            device_id = _get_device_id(sp)
            if not device_id:
                time.sleep(3)
                device_id = _get_device_id(sp)
            if not device_id:
                return True, (
                    "No active Spotify device found, Master.\n"
                    "Please open Spotify on your computer or phone first."
                )

            try:
                # Search: try track first, then artist
                results = sp.search(q=query, type="track", limit=1)
                tracks = results.get("tracks", {}).get("items", [])

                if not tracks:
                    # Try artist search as fallback
                    results = sp.search(q=query, type="artist", limit=1)
                    artists = results.get("artists", {}).get("items", [])
                    if artists:
                        artist_uri = artists[0]["uri"]
                        sp.start_playback(device_id=device_id, context_uri=artist_uri)
                        return True, f"Playing music by {artists[0]['name']} on Spotify, Master."
                    return True, f"Couldn't find '{query}' on Spotify, Master."

                track = tracks[0]
                track_name = track["name"]
                artist_name = ", ".join(a["name"] for a in track["artists"])
                track_uri = track["uri"]

                sp.start_playback(device_id=device_id, uris=[track_uri])
                return True, f"Now playing: {track_name} by {artist_name} on Spotify, Master."

            except spotipy.exceptions.SpotifyException as e:
                if "premium" in str(e).lower():
                    return True, "Spotify Premium is required for playback control, Master."
                return True, f"Spotify error: {str(e)[:100]}"
            except Exception as e:
                return True, f"Playback failed: {str(e)[:100]}"

        # ══════════════════════════════════════════════════════════
        #  PAUSE
        # ══════════════════════════════════════════════════════════
        if any(t in cmd for t in ["pause spotify", "stop spotify", "pause music"]):
            try:
                sp.pause_playback()
                return True, "Paused Spotify, Master."
            except spotipy.exceptions.SpotifyException as e:
                if "not playing" in str(e).lower() or "403" in str(e):
                    return True, "Nothing is playing on Spotify right now, Master."
                return True, f"Pause failed: {str(e)[:80]}"

        # ══════════════════════════════════════════════════════════
        #  RESUME
        # ══════════════════════════════════════════════════════════
        if any(t in cmd for t in ["resume spotify", "unpause spotify", "continue spotify",
                                   "play spotify", "resume music"]):
            try:
                device_id = _get_device_id(sp)
                sp.start_playback(device_id=device_id)
                return True, "Resumed Spotify, Master."
            except Exception as e:
                return True, f"Resume failed: {str(e)[:80]}"

        # ══════════════════════════════════════════════════════════
        #  NEXT / SKIP
        # ══════════════════════════════════════════════════════════
        if any(t in cmd for t in ["next spotify", "skip spotify", "next song spotify",
                                   "skip track", "next track spotify", "forward spotify"]):
            try:
                sp.next_track()
                time.sleep(0.5)
                pb = sp.current_playback()
                if pb and pb.get("item"):
                    name = pb["item"]["name"]
                    artist = pb["item"]["artists"][0]["name"]
                    return True, f"Skipped! Now playing: {name} by {artist}, Master."
                return True, "Skipped to next track, Master."
            except Exception as e:
                return True, f"Skip failed: {str(e)[:80]}"

        # ══════════════════════════════════════════════════════════
        #  PREVIOUS / BACK
        # ══════════════════════════════════════════════════════════
        if any(t in cmd for t in ["previous spotify", "back spotify", "prev spotify",
                                   "last song spotify", "go back spotify", "rewind spotify"]):
            try:
                sp.previous_track()
                time.sleep(0.5)
                pb = sp.current_playback()
                if pb and pb.get("item"):
                    name = pb["item"]["name"]
                    artist = pb["item"]["artists"][0]["name"]
                    return True, f"Going back! Now playing: {name} by {artist}, Master."
                return True, "Went to previous track, Master."
            except Exception as e:
                return True, f"Previous track failed: {str(e)[:80]}"

        # ══════════════════════════════════════════════════════════
        #  VOLUME
        # ══════════════════════════════════════════════════════════
        vol_match = re.search(r"spotify\s+volume\s+(\d+)", cmd) or \
                    re.search(r"volume\s+(\d+)\s+spotify", cmd)
        if vol_match:
            level = max(0, min(100, int(vol_match.group(1))))
            try:
                sp.volume(level)
                return True, f"Spotify volume set to {level}%, Master."
            except Exception as e:
                return True, f"Volume control failed: {str(e)[:80]}"

        # ══════════════════════════════════════════════════════════
        #  SHUFFLE
        # ══════════════════════════════════════════════════════════
        if "shuffle spotify" in cmd:
            state = "off" not in cmd  # True = on, False = off
            try:
                sp.shuffle(state)
                return True, f"Shuffle {'enabled' if state else 'disabled'} on Spotify, Master."
            except Exception as e:
                return True, f"Shuffle failed: {str(e)[:80]}"

        # ══════════════════════════════════════════════════════════
        #  REPEAT
        # ══════════════════════════════════════════════════════════
        if "repeat spotify" in cmd:
            if "off" in cmd:
                mode = "off"
            elif "track" in cmd or "song" in cmd:
                mode = "track"
            else:
                mode = "context"  # repeat playlist/album
            try:
                sp.repeat(mode)
                mode_label = {"off": "off", "track": "track (looping song)", "context": "playlist"}[mode]
                return True, f"Repeat set to {mode_label} on Spotify, Master."
            except Exception as e:
                return True, f"Repeat failed: {str(e)[:80]}"

        return False, ""

    # ===================== LOCAL MUSIC =====================
    def _check_local_music(self, cmd):
        triggers = ["play local music", "play my music", "play music from",
                    "play music folder", "local music", "play music",
                    "play some music", "play songs", "play my songs"]
        if not any(t in cmd for t in triggers):
            return False, ""
        if "spotify" in cmd or "youtube" in cmd:
            return False, ""

        music_dir = self._resolve_music_dir()
        if not music_dir:
            return True, "Music folder not found, Master. Create: data/music and put songs inside."

        ok, msg = self._music_ensure_service()
        if not ok:
            return True, msg

        r = self._music_send({"action": "LOAD_DIR", "dir": music_dir})
        if not r.get("ok"):
            return True, r.get("error", "Music load failed, Master.")

        r = self._music_send({"action": "PLAY"})
        if not r.get("ok"):
            return True, r.get("error", "Music play failed, Master.")

        now = r.get("now_playing") or ""
        total = r.get("total", 0)
        return True, f"Playing: {now}, Master. ({total} track(s))" if now else f"Playing music, Master. ({total} track(s))"

    # ===================== MUSIC HELPERS =====================
    def _resolve_music_dir(self):
        candidates = [
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "music"),
            os.path.join(os.path.expanduser("~"), "Music"),
            os.path.join(os.path.expanduser("~"), "Downloads"),
        ]
        exts = (".mp3", ".wav", ".ogg", ".flac", ".aac", ".wma", ".m4a")
        for path in candidates:
            if os.path.isdir(path):
                for ext in exts:
                    if glob.glob(os.path.join(path, "**", f"*{ext}"), recursive=True):
                        return path
        return None

    def _readline_with_timeout(self, stream, timeout=2.0):
        line_box = {"line": None}
        def _reader():
            try:
                line_box["line"] = stream.readline()
            except Exception:
                line_box["line"] = ""
        t = threading.Thread(target=_reader, daemon=True)
        t.start()
        t.join(timeout)
        return line_box["line"]

    def _music_ensure_service(self):
        if getattr(self, "_music_proc", None) and self._music_proc.poll() is None:
            return True, ""

        service_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "music_service.py"
        )
        if not os.path.exists(service_path):
            return False, "music_service.py not found, Master. Place it in the same folder as command_handler.py."

        try:
            env = os.environ.copy()
            env.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

            self._music_proc = subprocess.Popen(
                [sys.executable, service_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                env=env,
            )

            deadline = time.time() + 6.0
            last_err = None

            while time.time() < deadline:
                resp = self._music_send({"action": "PING"}, _skip_ensure=True, _timeout=2.0, _max_skip_lines=6)
                if isinstance(resp, dict) and resp.get("ok") is True:
                    return True, ""

                if self._music_proc.poll() is not None:
                    err = ""
                    try:
                        if self._music_proc.stderr:
                            err = (self._music_proc.stderr.read() or "").strip()
                    except Exception:
                        pass
                    if err:
                        return False, f"Music service crashed: {err[:240]}"
                    return False, "Music service failed to start, Master."

                last_err = resp.get("error") if isinstance(resp, dict) else str(resp)
                time.sleep(0.25)

            err = ""
            try:
                if self._music_proc and self._music_proc.stderr:
                    err = (self._music_proc.stderr.read() or "").strip()
            except Exception:
                pass

            if err:
                return False, f"Music service not ready: {err[:240]}"
            return False, f"Music service not ready, Master. ({(last_err or 'no response')[:120]})"

        except FileNotFoundError:
            return False, "Python not found on PATH, Master."
        except Exception as e:
            return False, f"Music service error: {str(e)[:160]}"

    def _music_send(self, payload, _skip_ensure=False, _timeout=2.0, _max_skip_lines=4):
        if not _skip_ensure:
            ok, msg = self._music_ensure_service()
            if not ok:
                return {"ok": False, "error": msg}

        if not getattr(self, "_music_proc", None) or self._music_proc.poll() is not None:
            return {"ok": False, "error": "Music service not running, Master."}

        try:
            if not self._music_proc.stdin or not self._music_proc.stdout:
                return {"ok": False, "error": "Music service pipes missing, Master."}

            self._music_proc.stdin.write(json.dumps(payload) + "\n")
            self._music_proc.stdin.flush()

            for _ in range(max(1, int(_max_skip_lines))):
                response_line = self._readline_with_timeout(self._music_proc.stdout, timeout=_timeout)
                if response_line is None:
                    continue
                response_line = response_line.strip()
                if not response_line:
                    continue
                try:
                    return json.loads(response_line)
                except json.JSONDecodeError:
                    continue

            return {"ok": False, "error": "Bad/empty response from music service, Master."}

        except BrokenPipeError:
            self._music_proc = None
            return {"ok": False, "error": "Music service pipe broken. Will restart on next command."}
        except Exception as e:
            return {"ok": False, "error": str(e)[:160]}

    # ===================== TODO =====================
    def _check_todo(self, cmd):
        add_match = re.search(r"(?:add|create|new)\s+(?:a\s+)?(?:todo|task|note)\s+(.+)", cmd)
        if add_match:
            task = add_match.group(1).strip()
            self.todos.append({"task": task, "done": False, "time": datetime.now().strftime("%Y-%m-%d %H:%M")})
            self._save_persistent_data()
            return True, f"Added to your list: '{task}'\nTotal tasks: {len(self.todos)}"

        if any(t in cmd for t in ["show todo", "show tasks", "my todos", "my tasks",
                                  "list todo", "list tasks", "show notes", "my notes",
                                  "what are my tasks", "pending tasks", "show my list",
                                  "task list", "todo list"]):
            if not self.todos:
                return True, "Your task list is empty, Master."
            lines = ["Your tasks:"]
            for i, t in enumerate(self.todos, 1):
                status = "DONE" if t["done"] else "PENDING"
                lines.append(f"{i}. [{status}] {t['task']} ({t['time']})")
            return True, "\n".join(lines)

        done_match = re.search(r"(?:complete|done|finish|check)\s+(?:todo|task|note)\s+(\d+)", cmd)
        if done_match:
            idx = int(done_match.group(1)) - 1
            if 0 <= idx < len(self.todos):
                self.todos[idx]["done"] = True
                self._save_persistent_data()
                return True, f"Marked task {idx+1} as done: '{self.todos[idx]['task']}'"
            return True, "Invalid task number, Master."

        del_match = re.search(r"(?:delete|remove|clear)\s+(?:todo|task|note)\s+(\d+)", cmd)
        if del_match:
            idx = int(del_match.group(1)) - 1
            if 0 <= idx < len(self.todos):
                removed = self.todos.pop(idx)
                self._save_persistent_data()
                return True, f"Removed task: '{removed['task']}'"
            return True, "Invalid task number, Master."

        if any(t in cmd for t in ["clear all todos", "clear all tasks", "delete all todos",
                                  "delete all tasks", "clear todo list", "clear task list",
                                  "empty todo", "empty tasks"]):
            count = len(self.todos)
            self.todos = []
            self._save_persistent_data()
            return True, f"Cleared {count} task(s), Master."

        return False, ""

    # ===================== CALCULATOR =====================
    def _check_calculator(self, cmd):
        pct_match = re.search(r"(?:what is|what's|whats|calculate)\s+(\d+(?:\.\d+)?)\s*%\s*of\s+(\d+(?:\.\d+)?)", cmd)
        if pct_match:
            pct = float(pct_match.group(1))
            val = float(pct_match.group(2))
            result = (pct / 100) * val
            if result == int(result):
                result = int(result)
            return True, f"{pct:.0f}% of {val:.0f} = {result}"

        calc_match = re.search(r"(?:calculate|calc|compute|solve|math)\s+([\d\s\+\-\*/\.\^\(\)]+)", cmd)
        if not calc_match:
            calc_match = re.search(r"(?:what is|what's|whats)\s+([\d][\d\s\+\-\*/\.\^\(\)]*[\d\)])", cmd)
        if calc_match:
            expr = calc_match.group(1).strip()
            expr = expr.replace("^", "**").replace("x", "*")
            try:
                allowed = {"__builtins__": {}, "math": math,
                           "sqrt": math.sqrt, "sin": math.sin, "cos": math.cos,
                           "tan": math.tan, "pi": math.pi, "e": math.e,
                           "log": math.log, "abs": abs, "round": round, "pow": pow}
                result = eval(expr, allowed)
                if isinstance(result, float) and result == int(result):
                    result = int(result)
                return True, f"{expr.replace('**', '^')} = {result}"
            except Exception:
                return True, f"Couldn't calculate: {expr}"

        return False, ""

    # ===================== DICTIONARY =====================
    def _check_dictionary(self, cmd):
        dict_match = re.search(r"(?:define|definition of|meaning of|dictionary|what does .+ mean)\s+(.+)", cmd)
        if not dict_match:
            dict_match = re.search(r"what does\s+(.+?)\s+mean", cmd)
        if dict_match:
            word = dict_match.group(1).strip()
            if not REQUESTS_AVAILABLE:
                return True, "Need 'requests' library for dictionary."
            try:
                resp = requests.get(
                    f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}", timeout=10
                ).json()
                if isinstance(resp, list) and len(resp) > 0:
                    entry = resp[0]
                    word_name = entry.get("word", word)
                    meanings = entry.get("meanings", [])
                    lines = [f"Definition of '{word_name}':"]
                    for m in meanings[:3]:
                        pos = m.get("partOfSpeech", "")
                        defs = m.get("definitions", [])
                        if defs:
                            lines.append(f"\n({pos}): {defs[0].get('definition', '')}")
                            if defs[0].get("example"):
                                lines.append(f"  Example: \"{defs[0]['example']}\"")
                    phonetics = entry.get("phonetics", [])
                    for p in phonetics:
                        if p.get("text"):
                            lines.insert(1, f"Pronunciation: {p['text']}")
                            break
                    return True, "\n".join(lines)
                return True, f"No definition found for '{word}', Master."
            except Exception as e:
                return True, f"Dictionary error: {str(e)[:60]}"
        return False, ""

    # ===================== TRANSLATE =====================
    def _check_translate(self, cmd):
        trans_match = re.search(r"translate\s+['\"]?(.+?)['\"]?\s+(?:to|in|into)\s+(\w+)", cmd)
        if trans_match:
            text = trans_match.group(1).strip()
            target_lang = trans_match.group(2).strip().lower()
            if not REQUESTS_AVAILABLE:
                return True, "Need 'requests' library for translation."

            lang_codes = {
                "spanish": "es", "french": "fr", "german": "de", "italian": "it",
                "portuguese": "pt", "russian": "ru", "japanese": "ja", "chinese": "zh",
                "korean": "ko", "arabic": "ar", "hindi": "hi", "turkish": "tr",
                "dutch": "nl", "swedish": "sv", "polish": "pl", "thai": "th",
                "vietnamese": "vi", "indonesian": "id", "malay": "ms", "tamil": "ta",
                "urdu": "ur", "bengali": "bn", "marathi": "mr", "telugu": "te",
                "gujarati": "gu", "kannada": "kn", "malayalam": "ml", "punjabi": "pa",
            }
            code = lang_codes.get(target_lang, target_lang)

            try:
                resp = requests.get(
                    f"https://api.mymemory.translated.net/get?q={text}&langpair=en|{code}",
                    timeout=10
                ).json()
                translated = resp.get("responseData", {}).get("translatedText", "")
                if translated and translated.lower() != text.lower():
                    return True, f"Translation ({target_lang}):\n'{text}' -> '{translated}'"
                return True, f"Couldn't translate to {target_lang}. Try a different language."
            except Exception as e:
                return True, f"Translation error: {str(e)[:60]}"
        return False, ""

    # ===================== EMAIL =====================
    def _check_email(self, cmd):
        send_match = re.search(r"(?:send|compose|write)\s+(?:an?\s+)?email", cmd)
        if send_match:
            if not GMAIL_ADDRESS or not GMAIL_APP_PASSWORD:
                return True, ("Email not configured, Master. Add to your .env file:\n"
                              "GMAIL_ADDRESS=your.email@gmail.com\n"
                              "GMAIL_APP_PASSWORD=your_app_password")

            to_match = re.search(r"to\s+([\w\.\-]+@[\w\.\-]+)", cmd)
            subj_match = re.search(r"subject\s+(.+?)(?:\s+body|\s+message|$)", cmd)
            body_match = re.search(r"(?:body|message)\s+(.+)", cmd)

            if not to_match:
                return True, "Format: send email to user@email.com subject Hello body Your message"

            to_addr = to_match.group(1)
            subject = subj_match.group(1).strip() if subj_match else "Message from AlfredX"
            body = body_match.group(1).strip() if body_match else "Sent via AlfredX Assistant"

            try:
                msg = MIMEMultipart()
                msg['From'] = GMAIL_ADDRESS
                msg['To'] = to_addr
                msg['Subject'] = subject
                msg.attach(MIMEText(body, 'plain'))
                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
                server.send_message(msg)
                server.quit()
                return True, f"Email sent to {to_addr}, Master.\nSubject: {subject}"
            except Exception as e:
                return True, f"Email failed: {str(e)[:100]}"

        if any(t in cmd for t in ["check email", "read email", "show email", "my email",
                                  "check mail", "read mail", "show mail", "inbox",
                                  "unread email", "new email", "any emails", "any mail"]):
            if not GMAIL_ADDRESS or not GMAIL_APP_PASSWORD:
                return True, "Email not configured. Say 'open gmail' to check in browser."
            try:
                mail = imaplib.IMAP4_SSL("imap.gmail.com")
                mail.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
                mail.select("inbox")
                _, data = mail.search(None, "UNSEEN")
                email_ids = data[0].split()
                if not email_ids:
                    mail.logout()
                    return True, "No unread emails, Master."
                lines = [f"You have {len(email_ids)} unread email(s):"]
                for eid in email_ids[-5:]:
                    _, msg_data = mail.fetch(eid, "(RFC822)")
                    msg = email_lib.message_from_bytes(msg_data[0][1])
                    sender = re.sub(r'<.*?>', '', msg.get("From", "Unknown")).strip().strip('"')
                    lines.append(f"\nFrom: {sender}\nSubject: {msg.get('Subject', 'No Subject')}")
                mail.logout()
                return True, "\n".join(lines)
            except Exception as e:
                return True, f"Email check failed: {str(e)[:100]}"

        if any(t in cmd for t in ["open gmail", "open email", "open mail"]):
            webbrowser.open("https://mail.google.com")
            return True, "Opening Gmail, Master."

        return False, ""

    # ===================== INTERNET SPEED =====================
    def _check_internet_speed(self, cmd):
        triggers = ["internet speed", "speed test", "speedtest", "net speed",
                    "check speed", "test speed", "connection speed", "bandwidth",
                    "how fast is my internet", "wifi speed", "download speed", "upload speed"]
        if not any(t in cmd for t in triggers):
            return False, ""
        if not REQUESTS_AVAILABLE:
            return True, "Need 'requests' library for speed test."
        try:
            start = time.time()
            resp = requests.get("http://speedtest.tele2.net/1MB.zip", timeout=15, stream=True)
            size = sum(len(chunk) for chunk in resp.iter_content(chunk_size=8192))
            elapsed = time.time() - start
            download_mbps = (size * 8) / (elapsed * 1_000_000)
            ping_start = time.time()
            requests.get("https://www.google.com", timeout=5)
            ping = (time.time() - ping_start) * 1000
            return True, (f"Internet Speed:\nDownload: {download_mbps:.1f} Mbps\nPing: {ping:.0f} ms")
        except requests.exceptions.ConnectionError:
            return True, "No internet connection detected, Master."
        except Exception as e:
            return True, f"Speed test failed: {str(e)[:80]}"

    # ===================== PROCESS LIST =====================
    def _check_process_list(self, cmd):
        triggers = ["running apps", "running programs", "running processes",
                    "show processes", "list processes", "active apps",
                    "what's running", "whats running", "open apps",
                    "show running", "active programs", "task list"]
        if not any(t in cmd for t in triggers):
            return False, ""
        if not PSUTIL_AVAILABLE:
            return True, "Need psutil."
        apps = []
        for proc in psutil.process_iter(['name', 'memory_percent']):
            try:
                name = proc.info['name']
                mem = proc.info['memory_percent']
                if mem and mem > 0.1 and name not in [p[0] for p in apps]:
                    apps.append((name, mem))
            except Exception:
                pass
        apps.sort(key=lambda x: x[1], reverse=True)
        lines = [f"Top {min(15, len(apps))} running processes:"]
        for name, mem in apps[:15]:
            lines.append(f"  {name:<30} {mem:.1f}% RAM")
        lines.append(f"\nTotal processes: {len(list(psutil.process_iter()))}")
        return True, "\n".join(lines)

    # ===================== KILL ALL =====================
    def _check_kill_all(self, cmd):
        if not any(t in cmd for t in ["kill all", "close all apps", "close all programs",
                                      "terminate all", "close everything", "kill all background"]):
            return False, ""
        return True, ("For safety, I can't kill all processes at once, Master.\n"
                      "Use 'close <app_name>' to close specific apps.")

    # ===================== FILE OPERATIONS =====================
    def _check_file_operations(self, cmd):
        home = os.path.expanduser("~")

        create_match = re.search(r"(?:create|make|new)\s+folder\s+(.+?)(?:\s+(?:on|in|at)\s+(.+))?$", cmd)
        if create_match:
            name = create_match.group(1).strip()
            location = create_match.group(2)
            if location:
                folder_map = {"desktop": "Desktop", "downloads": "Downloads",
                              "documents": "Documents", "home": ""}
                loc = folder_map.get(location.strip().lower(), location.strip())
                base = os.path.join(home, loc) if loc else home
            else:
                base = os.path.join(home, "Desktop")
            path = os.path.join(base, name)
            try:
                os.makedirs(path, exist_ok=True)
                return True, f"Created folder: {path}"
            except Exception as e:
                return True, f"Couldn't create folder: {str(e)[:60]}"

        create_file = re.search(r"(?:create|make|new)\s+file\s+(.+?)(?:\s+(?:on|in|at)\s+(.+))?$", cmd)
        if create_file:
            name = create_file.group(1).strip()
            location = create_file.group(2)
            if location:
                folder_map = {"desktop": "Desktop", "downloads": "Downloads", "documents": "Documents"}
                loc = folder_map.get(location.strip().lower(), location.strip())
                base = os.path.join(home, loc)
            else:
                base = os.path.join(home, "Desktop")
            path = os.path.join(base, name)
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write("")
                return True, f"Created file: {path}"
            except Exception as e:
                return True, f"Couldn't create file: {str(e)[:60]}"

        rename_match = re.search(r"rename\s+(?:file|folder)?\s*(.+?)\s+to\s+(.+)", cmd)
        if rename_match:
            old_name = rename_match.group(1).strip()
            new_name = rename_match.group(2).strip()
            search_dirs = [os.path.join(home, d) for d in ["Desktop", "Documents", "Downloads"]]
            for d in search_dirs:
                for f in glob.iglob(os.path.join(d, f"**/*{old_name}*"), recursive=True):
                    new_path = os.path.join(os.path.dirname(f), new_name)
                    try:
                        os.rename(f, new_path)
                        return True, f"Renamed: {os.path.basename(f)} -> {new_name}"
                    except Exception as e:
                        return True, f"Couldn't rename: {str(e)[:60]}"
            return True, f"Couldn't find '{old_name}' to rename."

        del_match = re.search(r"delete\s+(?:file|folder)?\s*(.+)", cmd)
        if del_match and "todo" not in cmd and "task" not in cmd and "note" not in cmd:
            name = del_match.group(1).strip()
            search_dirs = [os.path.join(home, d) for d in ["Desktop", "Documents", "Downloads"]]
            for d in search_dirs:
                for f in glob.iglob(os.path.join(d, f"**/*{name}*"), recursive=True):
                    return True, f"Found: {f}\nFor safety, please delete manually."

        return False, ""

    # ===================== SCHEDULED SHUTDOWN =====================
    def _check_scheduled_shutdown(self, cmd):
        shut_match = re.search(r"shutdown\s+in\s+(\d+)\s*(minute|hour|min|hr|second|sec)s?", cmd)
        if shut_match:
            amt = int(shut_match.group(1))
            unit = shut_match.group(2).lower()
            secs = amt * 60 if unit in ("minute", "min") else amt * 3600 if unit in ("hour", "hr") else amt
            if self.system == "Windows":
                subprocess.run(f"shutdown /s /t {secs}", shell=True)
                return True, f"System will shutdown in {amt} {unit}(s), Master.\nTo cancel: 'cancel shutdown'"

        if any(t in cmd for t in ["cancel shutdown", "abort shutdown", "stop shutdown"]):
            if self.system == "Windows":
                subprocess.run("shutdown /a", shell=True)
            return True, "Scheduled shutdown cancelled, Master."

        rest_match = re.search(r"restart\s+in\s+(\d+)\s*(minute|hour|min|hr)s?", cmd)
        if rest_match:
            amt = int(rest_match.group(1))
            unit = rest_match.group(2).lower()
            secs = amt * 60 if unit in ("minute", "min") else amt * 3600
            if self.system == "Windows":
                subprocess.run(f"shutdown /r /t {secs}", shell=True)
                return True, f"System will restart in {amt} {unit}(s), Master."

        return False, ""

    # ===================== DISK SPACE =====================
    def _check_disk_space(self, cmd):
        triggers = ["disk space", "storage space", "free space", "drive space",
                    "how much space", "disk usage", "storage left", "c drive"]
        if not any(t in cmd for t in triggers):
            return False, ""
        if not PSUTIL_AVAILABLE:
            return True, "Need psutil."
        lines = ["Disk Space:"]
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                total_gb = usage.total / (1024**3)
                used_gb = usage.used / (1024**3)
                free_gb = usage.free / (1024**3)
                lines.append(f"\n{partition.device} ({partition.mountpoint})")
                lines.append(f"  Total: {total_gb:.1f} GB | Used: {used_gb:.1f} GB | Free: {free_gb:.1f} GB ({100-usage.percent:.0f}% free)")
            except Exception:
                pass
        return True, "\n".join(lines)

    # ===================== JOKES =====================
    def _check_jokes(self, cmd):
        triggers = ["tell me a joke", "joke", "make me laugh", "say something funny",
                    "tell a joke", "funny", "humor", "comedy"]
        if not any(t in cmd for t in triggers):
            return False, ""
        jokes = [
            "Why do programmers prefer dark mode? Because light attracts bugs.",
            "I told my wife she was drawing her eyebrows too high. She looked surprised.",
            "Why don't scientists trust atoms? Because they make up everything.",
            "I'm reading a book about anti-gravity. It's impossible to put down.",
            "Why did the scarecrow win an award? He was outstanding in his field.",
            "I would tell you a UDP joke, but you might not get it.",
            "There are only 10 types of people in the world: those who understand binary and those who don't.",
            "Why was the JavaScript developer sad? Because he didn't Node how to Express himself.",
            "A SQL query walks into a bar and asks two tables... 'Can I JOIN you?'",
            "Why do Java developers wear glasses? Because they can't C#.",
            "A programmer's wife says: 'Buy a loaf of bread. If they have eggs, buy a dozen.' He returns with 12 loaves.",
            "Debugging: Being the detective in a crime movie where you are also the murderer.",
        ]
        return True, random.choice(jokes)

    # ===================== QUOTES =====================
    def _check_quotes(self, cmd):
        triggers = ["motivational quote", "inspire me", "motivation", "quote",
                    "inspirational", "give me a quote", "motivate me"]
        if not any(t in cmd for t in triggers):
            return False, ""
        quotes = [
            '"The only way to do great work is to love what you do." - Steve Jobs',
            '"Stay hungry, stay foolish." - Steve Jobs',
            '"The future belongs to those who believe in the beauty of their dreams." - Eleanor Roosevelt',
            '"It does not matter how slowly you go as long as you do not stop." - Confucius',
            '"Success is not final, failure is not fatal: it is the courage to continue that counts." - Winston Churchill',
            '"Believe you can and you\'re halfway there." - Theodore Roosevelt',
            '"In the middle of difficulty lies opportunity." - Albert Einstein',
            '"The master has failed more times than the beginner has tried." - Stephen McCranie',
        ]
        return True, random.choice(quotes)

    # ===================== COIN / DICE =====================
    def _check_coin_dice(self, cmd):
        if any(t in cmd for t in ["flip a coin", "coin flip", "toss a coin", "heads or tails", "flip coin"]):
            return True, f"Coin flip result: {random.choice(['Heads', 'Tails'])}!"

        if any(t in cmd for t in ["roll a dice", "roll dice", "throw dice", "dice roll", "roll a die", "roll die"]):
            sides = 6
            m = re.search(r"(\d+)\s*sided", cmd)
            if m:
                sides = int(m.group(1))
            return True, f"Dice roll ({sides}-sided): {random.randint(1, sides)}!"

        if any(t in cmd for t in ["random number", "pick a number", "generate number"]):
            m = re.search(r"(?:between|from)\s+(\d+)\s+(?:to|and)\s+(\d+)", cmd)
            low, high = (int(m.group(1)), int(m.group(2))) if m else (1, 100)
            return True, f"Random number ({low}-{high}): {random.randint(low, high)}"

        return False, ""

    # ===================== PASSWORD GENERATOR =====================
    def _check_password_generator(self, cmd):
        triggers = ["generate password", "create password", "random password",
                    "new password", "password generator", "make password",
                    "strong password", "secure password"]
        if not any(t in cmd for t in triggers):
            return False, ""

        length = 16
        m = re.search(r"(\d+)\s*(?:character|char|digit|length|long)", cmd)
        if m:
            length = max(8, min(64, int(m.group(1))))

        chars = string.ascii_letters + string.digits + "!@#$%&*-_=+"
        password = list(''.join(random.SystemRandom().choice(chars) for _ in range(length)))
        password[0] = random.choice(string.ascii_uppercase)
        password[1] = random.choice(string.ascii_lowercase)
        password[2] = random.choice(string.digits)
        password[3] = random.choice("!@#$%&*-_=+")
        random.shuffle(password)
        password = ''.join(password)

        if self.system == "Windows":
            try:
                subprocess.run(["powershell", "-Command", f"Set-Clipboard -Value '{password}'"],
                               capture_output=True, timeout=5)
            except Exception:
                pass

        return True, f"Generated password ({length} chars):\n{password}\n(Copied to clipboard)"

    # ===================== UNIT CONVERTER =====================
    def _check_unit_converter(self, cmd):
        conv_match = re.search(r"(?:convert\s+)?(\d+(?:\.\d+)?)\s*(\w+)\s+(?:to|in|into)\s+(\w+)", cmd)
        if not conv_match:
            return False, ""

        val = float(conv_match.group(1))
        from_unit = conv_match.group(2).lower()
        to_unit = conv_match.group(3).lower()

        conversions = {
            ("km", "miles"): lambda x: x * 0.621371,
            ("miles", "km"): lambda x: x * 1.60934,
            ("m", "feet"): lambda x: x * 3.28084,
            ("feet", "m"): lambda x: x / 3.28084,
            ("cm", "inches"): lambda x: x * 0.393701,
            ("inches", "cm"): lambda x: x * 2.54,
            ("m", "cm"): lambda x: x * 100,
            ("cm", "m"): lambda x: x / 100,
            ("km", "m"): lambda x: x * 1000,
            ("m", "km"): lambda x: x / 1000,
            ("kg", "pounds"): lambda x: x * 2.20462,
            ("kg", "lbs"): lambda x: x * 2.20462,
            ("pounds", "kg"): lambda x: x / 2.20462,
            ("lbs", "kg"): lambda x: x / 2.20462,
            ("g", "oz"): lambda x: x * 0.035274,
            ("oz", "g"): lambda x: x / 0.035274,
            ("kg", "g"): lambda x: x * 1000,
            ("g", "kg"): lambda x: x / 1000,
            ("fahrenheit", "celsius"): lambda x: (x - 32) * 5 / 9,
            ("f", "c"): lambda x: (x - 32) * 5 / 9,
            ("celsius", "fahrenheit"): lambda x: (x * 9 / 5) + 32,
            ("c", "f"): lambda x: (x * 9 / 5) + 32,
            ("celsius", "kelvin"): lambda x: x + 273.15,
            ("kelvin", "celsius"): lambda x: x - 273.15,
            ("liters", "gallons"): lambda x: x * 0.264172,
            ("l", "gallons"): lambda x: x * 0.264172,
            ("gallons", "liters"): lambda x: x * 3.78541,
            ("ml", "cups"): lambda x: x / 236.588,
            ("cups", "ml"): lambda x: x * 236.588,
            ("mph", "kmh"): lambda x: x * 1.60934,
            ("kmh", "mph"): lambda x: x / 1.60934,
            ("gb", "mb"): lambda x: x * 1024,
            ("mb", "gb"): lambda x: x / 1024,
            ("tb", "gb"): lambda x: x * 1024,
            ("gb", "tb"): lambda x: x / 1024,
            ("mb", "kb"): lambda x: x * 1024,
            ("kb", "mb"): lambda x: x / 1024,
            ("hours", "minutes"): lambda x: x * 60,
            ("minutes", "hours"): lambda x: x / 60,
            ("hours", "seconds"): lambda x: x * 3600,
            ("seconds", "hours"): lambda x: x / 3600,
            ("days", "hours"): lambda x: x * 24,
            ("hours", "days"): lambda x: x / 24,
        }

        key = (from_unit, to_unit)
        if key in conversions:
            result = conversions[key](val)
            return True, f"{val} {from_unit} = {result:.4f} {to_unit}"

        return False, ""

    # ===================== LOCATION =====================
    def _check_location(self, cmd):
        triggers = ["my location", "where am i", "current location",
                    "what city am i in", "location info"]
        if not any(t in cmd for t in triggers):
            return False, ""
        if not REQUESTS_AVAILABLE:
            return True, "Need 'requests' library."
        try:
            resp = requests.get("http://ip-api.com/json/", timeout=10).json()
            if resp.get("status") == "success":
                return True, (f"Your approximate location:\n"
                              f"City: {resp.get('city', 'Unknown')}\n"
                              f"Region: {resp.get('regionName', 'Unknown')}\n"
                              f"Country: {resp.get('country', 'Unknown')}\n"
                              f"ISP: {resp.get('isp', 'Unknown')}\n"
                              f"Coordinates: {resp.get('lat', '')}, {resp.get('lon', '')}")
            return True, "Couldn't determine location."
        except Exception:
            return True, "Location lookup failed. Check internet connection."

    # ===================== LEARNING MODE =====================
    def _check_learning_mode(self, cmd):
        rem_match = re.search(r"remember\s+(?:that\s+)?(.+?)\s+is\s+(.+)", cmd)
        if rem_match:
            key = rem_match.group(1).strip()
            value = rem_match.group(2).strip()
            self.memories[key.lower()] = value
            self._save_persistent_data()
            return True, f"I'll remember that {key} is {value}, Master."

        recall_match = re.search(r"(?:what is|recall|tell me|do you remember)\s+(.+)", cmd)
        if recall_match:
            key = recall_match.group(1).strip().lower()
            if key in self.memories:
                return True, f"{key.title()} is {self.memories[key]}, Master."
            for k, v in self.memories.items():
                if key in k or k in key:
                    return True, f"{k.title()} is {v}, Master."

        forget_match = re.search(r"forget\s+(?:about\s+)?(.+)", cmd)
        if forget_match:
            key = forget_match.group(1).strip().lower()
            if key in self.memories:
                del self.memories[key]
                self._save_persistent_data()
                return True, f"I've forgotten about {key}, Master."
            return True, f"I don't have any memory about '{key}'."

        if any(t in cmd for t in ["show memories", "what do you remember",
                                  "show what you remember", "your memories", "list memories"]):
            if not self.memories:
                return True, "I don't have any saved memories yet, Master."
            lines = ["Things I remember:"]
            for k, v in self.memories.items():
                lines.append(f"  - {k.title()} is {v}")
            return True, "\n".join(lines)

        return False, ""

    # ===================== COMMAND HISTORY =====================
    def _check_command_history(self, cmd):
        if any(t in cmd for t in ["command history", "show history", "my history",
                                  "recent commands", "last commands", "what did i say"]):
            if not self.command_history:
                return True, "No command history yet, Master."
            lines = ["Recent commands:"]
            for h in self.command_history[-10:]:
                lines.append(f"  [{h['time']}] {h['cmd']}")
            return True, "\n".join(lines)
        return False, ""

    # ===================== WEATHER =====================
    def _check_weather(self, cmd):
        triggers = ["weather", "temperature", "hava durumu", "sicaklik",
                    "how hot", "how cold", "forecast", "is it raining",
                    "will it rain", "is it sunny", "mausam"]
        if not any(t in cmd for t in triggers):
            return False, ""
        if not REQUESTS_AVAILABLE:
            return True, "Need 'requests' library."
        if not WEATHER_API_KEY:
            return True, "Need WEATHER_API_KEY in .env -- get free at openweathermap.org/api"
        city = "Istanbul"
        for p in [r"weather (?:in |for |at |of )(.+)", r"temperature (?:in |for |at |of )(.+)",
                  r"(?:how hot|how cold) (?:in |is it in )(.+)", r"forecast (?:in |for )(.+)"]:
            m = re.search(p, cmd)
            if m:
                city = m.group(1).strip()
                break
        try:
            data = requests.get(
                f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric",
                timeout=10
            ).json()
            if data.get("cod") != 200:
                return True, f"Couldn't find weather for '{city}'."
            w = data['weather'][0]['description'].capitalize()
            t = data['main']['temp']
            fl = data['main']['feels_like']
            h = data['main']['humidity']
            ws = data['wind']['speed']
            return True, f"Weather in {data['name']}: {w}, {t:.1f}C (feels {fl:.1f}C). Humidity: {h}%, Wind: {ws} m/s."
        except Exception as e:
            return True, f"Weather unavailable: {str(e)[:80]}"

    # ===================== NEWS =====================
    def _check_news(self, cmd):
        triggers = ["news", "headlines", "haberler", "gundem", "latest news",
                    "current events", "whats happening", "what's happening"]
        if not any(t in cmd for t in triggers):
            return False, ""
        if not REQUESTS_AVAILABLE:
            return True, "Need 'requests'."
        if not NEWS_API_KEY:
            return True, "Need NEWS_API_KEY in .env -- get free at newsapi.org"
        try:
            topic = None
            m = re.search(r"news (?:about |on |for |regarding )(.+)", cmd)
            if m:
                topic = m.group(1).strip()
            if topic:
                url = f"https://newsapi.org/v2/everything?q={topic}&sortBy=publishedAt&pageSize=5&apiKey={NEWS_API_KEY}"
            else:
                url = f"https://newsapi.org/v2/top-headlines?country=us&pageSize=5&apiKey={NEWS_API_KEY}"
            articles = requests.get(url, timeout=10).json().get("articles", [])
            if not articles:
                return True, "No news found, Master."
            lines = ["Latest headlines:"]
            for i, a in enumerate(articles[:5], 1):
                lines.append(f"{i}. {a.get('title','')} -- {a.get('source',{}).get('name','')}")
            return True, "\n".join(lines)
        except Exception as e:
            return True, f"News unavailable: {str(e)[:80]}"

    # ===================== FOLDERS =====================
    def _check_open_folder(self, cmd):
        fmap = {
            "downloads": "Downloads", "download": "Downloads",
            "desktop": "Desktop",
            "documents": "Documents", "document": "Documents", "docs": "Documents",
            "pictures": "Pictures", "picture": "Pictures", "photos": "Pictures", "images": "Pictures",
            "music": "Music", "songs": "Music",
            "videos": "Videos", "video": "Videos", "movies": "Videos"
        }
        for trigger, folder in fmap.items():
            if trigger in cmd and any(t in cmd for t in ["open", "show", "go to", "navigate"]):
                path = os.path.join(os.path.expanduser("~"), folder)
                if os.path.exists(path):
                    try:
                        if self.system == "Windows":
                            subprocess.Popen(["explorer", path])
                        elif self.system == "Darwin":
                            subprocess.Popen(["open", path])
                        else:
                            subprocess.Popen(["xdg-open", path])
                        return True, f"Opening {folder}, Master."
                    except Exception as e:
                        return True, f"Couldn't open {folder}: {str(e)[:60]}"
                return True, f"Folder not found: {path}"
        return False, ""

    def _check_close_folder(self, cmd):
        if "close" not in cmd:
            return False, ""
        fmap = {
            "downloads": "Downloads", "download": "Downloads", "desktop": "Desktop",
            "documents": "Documents", "document": "Documents", "docs": "Documents",
            "pictures": "Pictures", "picture": "Pictures", "photos": "Pictures",
            "music": "Music", "videos": "Videos", "video": "Videos"
        }
        target_folder = None
        for trigger, folder in fmap.items():
            if trigger in cmd:
                target_folder = folder
                break

        if self.system == "Windows":
            if target_folder:
                try:
                    subprocess.run([
                        "powershell", "-Command",
                        f'(New-Object -ComObject Shell.Application).Windows() | Where-Object {{ $_.LocationURL -like "*{target_folder}*" -or $_.LocationName -like "*{target_folder}*" }} | ForEach-Object {{ $_.Quit() }}'
                    ], capture_output=True, timeout=10)
                    return True, f"Closing {target_folder} window, Master."
                except Exception:
                    return True, f"Couldn't close {target_folder} window."

            if any(t in cmd for t in ["folder", "folders", "explorer", "all folders", "all windows", "file explorer"]):
                try:
                    subprocess.run([
                        "powershell", "-Command",
                        "(New-Object -ComObject Shell.Application).Windows() | ForEach-Object { $_.Quit() }"
                    ], capture_output=True, timeout=10)
                    return True, "Closing all Explorer windows, Master."
                except Exception:
                    pass

            m = re.search(r"close (?:folder |file |directory )?(.+)", cmd)
            if m:
                name = m.group(1).strip()
                if name and name not in ["it", "that", "this", "the"]:
                    try:
                        subprocess.run([
                            "powershell", "-Command",
                            f'(New-Object -ComObject Shell.Application).Windows() | Where-Object {{ $_.LocationURL -like "*{name}*" -or $_.LocationName -like "*{name}*" }} | ForEach-Object {{ $_.Quit() }}'
                        ], capture_output=True, timeout=10)
                    except Exception:
                        pass
                    try:
                        subprocess.run([
                            "powershell", "-Command",
                            f'Get-Process | Where-Object {{$_.MainWindowTitle -like "*{name}*"}} | ForEach-Object {{ $_.CloseMainWindow() | Out-Null }}'
                        ], capture_output=True, timeout=10)
                    except Exception:
                        pass
                    return True, f"Closing '{name}', Master."
        return False, ""

    # ===================== APP LAUNCH =====================
    def _check_open_app(self, cmd):
        folder_words = ["downloads", "download", "desktop", "documents", "document",
                        "pictures", "picture", "photos", "music", "videos", "video",
                        "docs", "images", "songs", "movies"]
        for fw in folder_words:
            if fw in cmd and "folder" not in cmd.replace(fw, ""):
                return False, ""

        if any(t in cmd for t in ["night light", "hotspot", "bluetooth", "airplane",
                                  "night mode", "blue light", "nightlight", "tethering",
                                  "focus mode", "do not disturb", "wallpaper", "theme",
                                  "display settings", "sound settings", "privacy",
                                  "windows update", "storage settings"]):
            return False, ""

        for p in [r"open (.+)", r"launch (.+)", r"start (.+)", r"run (.+)", r"(.+) ac"]:
            m = re.search(p, cmd)
            if m:
                app = m.group(1).strip().rstrip(".")
                if app in ["it", "that", "this", "the", "a", "my", "up", ""]:
                    return False, ""
                if "youtube" in app or "gmail" in app:
                    return False, ""

                exe = self.app_map.get(app.lower())
                if exe is None:
                    url = self.website_map.get(app.lower())
                    if url:
                        webbrowser.open(url)
                        return True, f"Opening {app} in browser, Master."
                    found = self._find_and_open_file(app)
                    if found:
                        return True, found
                    exe = app.lower()
                try:
                    if self.system == "Windows":
                        if exe.startswith("ms-") or exe.endswith(":"):
                            os.startfile(exe)
                        elif "shell:" in exe or exe.startswith("explorer "):
                            subprocess.Popen(exe, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        elif exe == "code":
                            subprocess.Popen(["cmd", "/c", "code"], shell=False,
                                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                             creationflags=0x08000000)
                        else:
                            subprocess.Popen(f"start \"\" \"{exe}\"", shell=True,
                                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    elif self.system == "Darwin":
                        subprocess.Popen(["open", "-a", exe])
                    else:
                        subprocess.Popen([exe], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    return True, f"Opening {app}, Master."
                except Exception:
                    return True, f"Couldn't open {app}, Master."
        return False, ""

    def _find_and_open_file(self, name):
        clean_name = name
        for prefix in ["folder ", "file ", "directory "]:
            if clean_name.lower().startswith(prefix):
                clean_name = clean_name[len(prefix):]

        search_dirs = [
            os.path.join(os.path.expanduser("~"), d)
            for d in ["Desktop", "Documents", "Downloads", "Pictures", "Music", "Videos"]
        ]
        search_dirs.append(os.path.expanduser("~"))

        for folder in search_dirs:
            if not os.path.exists(folder):
                continue
            try:
                for f in glob.iglob(os.path.join(folder, f"**/*{clean_name}*"), recursive=True):
                    try:
                        if self.system == "Windows":
                            os.startfile(f)
                        elif self.system == "Darwin":
                            subprocess.Popen(["open", f])
                        else:
                            subprocess.Popen(["xdg-open", f])
                        ftype = "folder" if os.path.isdir(f) else "file"
                        return f"Opening {ftype}: {os.path.basename(f)}\nPath: {f}"
                    except Exception as e:
                        return f"Found but couldn't open: {f}\nError: {str(e)[:60]}"
            except Exception:
                continue
        return None

    # ===================== APP KILLER =====================
    def _check_close_app(self, cmd):
        for p in [r"close (.+)", r"kill (.+)", r"quit (.+)", r"exit (.+)",
                  r"terminate (.+)", r"end (.+)", r"(.+) kapat"]:
            m = re.search(p, cmd)
            if m:
                app = m.group(1).strip().rstrip(".")
                if app in ["it", "that", "this", "the", ""]:
                    return False, ""
                clean_app = app
                for prefix in ["folder ", "file ", "directory ", "app ", "application "]:
                    if clean_app.lower().startswith(prefix):
                        clean_app = clean_app[len(prefix):]
                app = clean_app

                if not PSUTIL_AVAILABLE:
                    return True, "Need psutil."

                pmap = {
                    "chrome": "chrome", "google chrome": "chrome", "browser": "chrome",
                    "firefox": "firefox", "notepad": "notepad",
                    "spotify": "spotify", "discord": "discord", "word": "winword",
                    "excel": "excel", "vscode": "code", "vs code": "code", "steam": "steam",
                    "edge": "msedge", "brave": "brave", "vlc": "vlc",
                    "whatsapp": "whatsapp", "telegram": "telegram",
                }
                target = pmap.get(app.lower(), app.lower())
                killed = 0
                for proc in psutil.process_iter(['name']):
                    try:
                        if target in proc.info['name'].lower():
                            proc.terminate()
                            killed += 1
                    except Exception:
                        pass
                if killed:
                    return True, f"Terminated {killed} {app} process(es)."

                if self.system == "Windows":
                    try:
                        subprocess.run([
                            "powershell", "-Command",
                            f'(New-Object -ComObject Shell.Application).Windows() | Where-Object {{ $_.LocationName -like "*{app}*" -or $_.LocationURL -like "*{app}*" }} | ForEach-Object {{ $_.Quit() }}'
                        ], capture_output=True, text=True, timeout=10)
                    except Exception:
                        pass
                    try:
                        result = subprocess.run(
                            ["powershell", "-Command",
                             f'Get-Process | Where-Object {{$_.MainWindowTitle -like "*{app}*"}} | ForEach-Object {{ $_.CloseMainWindow() }}'],
                            capture_output=True, text=True, timeout=10
                        )
                        if "True" in result.stdout:
                            return True, f"Closed window matching '{app}', Master."
                    except Exception:
                        pass
                return True, f"Closing '{app}', Master."
        return False, ""

    # ===================== WEB SEARCH =====================
    def _check_web_search(self, cmd):
        personal_words = ["my name", "my age", "my birthday", "about me", "who am i",
                          "do you remember", "do you know me", "what is my", "what's my", "whats my"]
        if any(t in cmd for t in personal_words):
            return False, ""

        for p in [r"^search (?:for |about )?(.+)", r"^google (.+)", r"^look up (.+)",
                  r"^look for (.+)", r"^browse (.+)"]:
            m = re.search(p, cmd)
            if m:
                q = m.group(1).strip()
                webbrowser.open(f"https://www.google.com/search?q={q.replace(' ','+')}")
                return True, f"Searching for '{q}', Master."
        return False, ""

    # ===================== WIKIPEDIA =====================
    def _check_wikipedia(self, cmd):
        personal_words = ["my name", "my age", "my birthday", "about me", "who am i",
                          "my favorite", "my job", "my work", "do you remember",
                          "do you know me", "my email", "my phone", "my address",
                          "what is my", "what's my", "whats my"]
        if any(t in cmd for t in personal_words):
            return False, ""

        triggers = ["who is ", "what is ", "tell me about ", "explain ", "define ",
                    "who was ", "what was ", "what are ", "who are ", "what does ", "meaning of "]
        if not any(cmd.startswith(t) for t in triggers):
            return False, ""
        if not WIKI_AVAILABLE:
            return True, "Need wikipedia library."

        topic = cmd
        for prefix in triggers:
            if cmd.startswith(prefix):
                topic = cmd[len(prefix):]
                break
        if len(topic) < 3:
            return False, ""

        try:
            summary = wikipedia.summary(topic, sentences=3, auto_suggest=True)
            return True, f"According to my research:\n\n{summary}"
        except wikipedia.DisambiguationError as e:
            return True, f"Multiple results found. Did you mean: {', '.join(e.options[:5])}?"
        except wikipedia.PageError:
            try:
                results = wikipedia.search(topic, results=3)
                if results:
                    summary = wikipedia.summary(results[0], sentences=3)
                    return True, f"I found info about '{results[0]}':\n\n{summary}"
            except Exception:
                pass
            return False, ""
        except Exception:
            return False, ""

    # ===================== VOLUME =====================
    def _check_volume(self, cmd):
        if any(t in cmd for t in ["volume up", "ses ac", "turn up", "louder",
                                  "increase volume", "raise volume", "volume increase",
                                  "make it louder", "sound up", "awaz badha"]):
            self._vol("up")
            return True, "Volume increased, Master."
        if any(t in cmd for t in ["volume down", "ses kis", "turn down", "quieter",
                                  "decrease volume", "lower volume", "volume decrease",
                                  "make it quieter", "sound down", "awaz kam"]):
            self._vol("down")
            return True, "Volume decreased, Master."
        if any(t in cmd for t in ["mute", "sessiz", "silence", "unmute"]):
            self._vol("mute")
            return True, "Toggled mute, Master."
        if any(t in cmd for t in ["max volume", "full volume", "volume max",
                                  "maximum volume", "volume 100", "blast it"]):
            self._vol("max")
            return True, "Volume set to maximum, Master."
        if any(t in cmd for t in ["min volume", "minimum volume", "volume min",
                                  "volume 0", "volume zero"]):
            self._vol("min")
            return True, "Volume set to minimum, Master."

        vol_match = re.search(r"(?:set )?volume (?:to |at )?(\d+)(?:%)?", cmd)
        if vol_match:
            level = max(0, min(100, int(vol_match.group(1))))
            self._vol_set(level)
            return True, f"Volume set to {level}%, Master."

        return False, ""

    def _vol(self, d):
        if self.system != "Windows":
            return
        try:
            from ctypes import cast, POINTER
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            dev = AudioUtilities.GetSpeakers()
            iface = dev.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            v = cast(iface, POINTER(IAudioEndpointVolume))
            if d == "mute":
                v.SetMute(not v.GetMute(), None)
            elif d == "max":
                v.SetMasterVolumeLevelScalar(1.0, None)
            elif d == "min":
                v.SetMasterVolumeLevelScalar(0.05, None)
            else:
                current = v.GetMasterVolumeLevelScalar()
                delta = 0.15 if d == "up" else -0.15
                v.SetMasterVolumeLevelScalar(max(0.0, min(1.0, current + delta)), None)
        except Exception:
            try:
                import ctypes
                if d == "max":
                    for _ in range(50):
                        ctypes.windll.user32.keybd_event(0xAF, 0, 0, 0)
                        ctypes.windll.user32.keybd_event(0xAF, 0, 2, 0)
                elif d == "min":
                    for _ in range(50):
                        ctypes.windll.user32.keybd_event(0xAE, 0, 0, 0)
                        ctypes.windll.user32.keybd_event(0xAE, 0, 2, 0)
                else:
                    k = {"up": 0xAF, "down": 0xAE, "mute": 0xAD}.get(d)
                    if k:
                        count = 5 if d != "mute" else 1
                        for _ in range(count):
                            ctypes.windll.user32.keybd_event(k, 0, 0, 0)
                            ctypes.windll.user32.keybd_event(k, 0, 2, 0)
            except Exception:
                pass

    def _vol_set(self, level):
        if self.system != "Windows":
            return
        try:
            from ctypes import cast, POINTER
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            dev = AudioUtilities.GetSpeakers()
            iface = dev.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            v = cast(iface, POINTER(IAudioEndpointVolume))
            v.SetMasterVolumeLevelScalar(level / 100.0, None)
        except Exception:
            # Fallback — use keyboard volume keys
            import ctypes
            current_presses = level // 2
            for _ in range(50):
                ctypes.windll.user32.keybd_event(0xAE, 0, 0, 0)
                ctypes.windll.user32.keybd_event(0xAE, 0, 2, 0)
            for _ in range(current_presses):
                ctypes.windll.user32.keybd_event(0xAF, 0, 0, 0)
                ctypes.windll.user32.keybd_event(0xAF, 0, 2, 0)

    # ===================== MEDIA =====================
    def _check_media(self, cmd):
        if any(t in cmd for t in ["pause music", "pause song"]):
            if self._music_proc:
                r = self._music_send({"action": "PAUSE"})
                return True, ("Paused, Master." if r.get("ok") else r.get("error", "Pause failed, Master."))
            self._media_key(0xB3)
            return True, "Toggled playback, Master."

        if any(t in cmd for t in ["resume music", "resume song", "unpause", "resume"]):
            if self._music_proc:
                r = self._music_send({"action": "RESUME"})
                return True, ("Resumed, Master." if r.get("ok") else r.get("error", "Resume failed, Master."))
            self._media_key(0xB3)
            return True, "Toggled playback, Master."

        if any(t in cmd for t in ["next track", "next song", "skip song", "skip track",
                                  "skip", "play next", "next one", "agla gaana"]):
            if self._music_proc:
                r = self._music_send({"action": "NEXT"})
                if r.get("ok"):
                    now = r.get("now_playing") or ""
                    return True, f"Next track, Master. {now}" if now else "Next track, Master."
                return True, r.get("error", "Next track failed, Master.")
            self._media_key(0xB0)
            return True, "Next track, Master."

        if any(t in cmd for t in ["previous track", "previous song", "last song",
                                  "last track", "go back", "play previous"]):
            if self._music_proc:
                r = self._music_send({"action": "PREV"})
                if r.get("ok"):
                    now = r.get("now_playing") or ""
                    return True, f"Previous track, Master. {now}" if now else "Previous track, Master."
                return True, r.get("error", "Previous track failed, Master.")
            self._media_key(0xB1)
            return True, "Previous track, Master."

        if any(t in cmd for t in ["stop music", "stop song", "stop playing", "stop playback"]):
            if self._music_proc:
                r = self._music_send({"action": "STOP"})
                return True, ("Stopped, Master." if r.get("ok") else r.get("error", "Stop failed, Master."))
            self._media_key(0xB2)
            return True, "Stopping playback, Master."

        if cmd in ["play music", "play", "resume"]:
            if self._music_proc:
                r = self._music_send({"action": "PLAY"})
                return True, ("Playing, Master." if r.get("ok") else r.get("error", "Play failed, Master."))
            self._media_key(0xB3)
            return True, "Toggled playback, Master."

        return False, ""

    def _media_key(self, k):
        if self.system == "Windows":
            import ctypes
            ctypes.windll.user32.keybd_event(k, 0, 0, 0)
            ctypes.windll.user32.keybd_event(k, 0, 2, 0)

    # ===================== SYSTEM =====================
    def _check_system_control(self, cmd):
        if any(t in cmd for t in ["lock computer", "lock screen", "lock pc", "lock my pc", "lock my computer"]):
            if self.system == "Windows":
                subprocess.run("rundll32.exe user32.dll,LockWorkStation", shell=True)
            return True, "Locking system, Master."
        if any(t in cmd for t in ["sleep mode", "go to sleep", "sleep computer", "sleep pc", "put to sleep"]):
            if self.system == "Windows":
                subprocess.run("rundll32.exe powrprof.dll,SetSuspendState 0,1,0", shell=True)
            return True, "Sleep mode, Master."
        if any(t in cmd for t in ["empty recycle", "empty trash", "clear recycle", "clear trash", "empty bin"]):
            subprocess.run(["powershell", "-Command", "Clear-RecycleBin -Force -ErrorAction SilentlyContinue"],
                           capture_output=True)
            return True, "Recycle bin emptied, Master."
        if "shutdown" in cmd and any(t in cmd for t in ["computer", "pc", "system"]):
            if "in " in cmd:
                return False, ""
            return True, "For safety, please shutdown manually, Master."
        if "restart" in cmd and any(t in cmd for t in ["computer", "pc", "system"]):
            if "in " in cmd:
                return False, ""
            return True, "For safety, please restart manually, Master."
        return False, ""

    # ===================== TIMER =====================
    def _check_timer(self, cmd):
        for p in [
            r"(?:set )?(?:a )?timer (?:for |of )?(\d+)\s*(second|minute|hour|min|sec|hr)s?",
            r"(\d+)\s*(second|minute|hour|min|sec|hr)s?\s*timer"
        ]:
            m = re.search(p, cmd)
            if m:
                amt = int(m.group(1))
                unit = m.group(2).lower()
                secs = amt * 60 if unit in ("minute", "min") else amt * 3600 if unit in ("hour", "hr") else amt

                def beep():
                    try:
                        if self.system == "Windows":
                            import winsound
                            for _ in range(3):
                                winsound.Beep(1000, 500)
                    except Exception:
                        pass

                t = threading.Timer(secs, beep)
                t.daemon = True
                t.start()
                self.timers.append(t)
                return True, f"Timer set for {amt} {unit}(s), Master."
        return False, ""

    # ===================== SCREENSHOT =====================
    def _check_screenshot(self, cmd):
        triggers = ["screenshot", "screen capture", "print screen", "screen shot",
                    "capture screen", "take a screenshot", "take screenshot",
                    "grab screen", "snap screen"]
        if cmd.strip() == "ss":
            pass
        elif not any(t in cmd for t in triggers):
            return False, ""

        screenshots_dir = os.path.join(os.path.expanduser("~"), "Pictures", "Screenshots")
        os.makedirs(screenshots_dir, exist_ok=True)
        filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        sp = os.path.join(screenshots_dir, filename)

        try:
            if self.system == "Windows":
                sp_ps = sp.replace("'", "''")
                ps_script = (
                    "Add-Type -AssemblyName System.Windows.Forms;"
                    "Add-Type -AssemblyName System.Drawing;"
                    "Add-Type -TypeDefinition '"
                    "using System.Runtime.InteropServices;"
                    "public class DPI {"
                    "  [DllImport(\"user32.dll\")]"
                    "  public static extern bool SetProcessDPIAware();"
                    "}';"
                    "[DPI]::SetProcessDPIAware();"
                    "$left = [System.Windows.Forms.SystemInformation]::VirtualScreen.Left;"
                    "$top = [System.Windows.Forms.SystemInformation]::VirtualScreen.Top;"
                    "$width = [System.Windows.Forms.SystemInformation]::VirtualScreen.Width;"
                    "$height = [System.Windows.Forms.SystemInformation]::VirtualScreen.Height;"
                    "$bmp = New-Object System.Drawing.Bitmap($width, $height);"
                    "$g = [System.Drawing.Graphics]::FromImage($bmp);"
                    "$g.CopyFromScreen($left, $top, 0, 0, (New-Object System.Drawing.Size($width, $height)));"
                    f"$bmp.Save('{sp_ps}');"
                    "$g.Dispose();"
                    "$bmp.Dispose()"
                )
                result = subprocess.run(
                    ["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
                    capture_output=True, text=True, timeout=15
                )
                if os.path.exists(sp) and os.path.getsize(sp) > 1000:
                    size_kb = os.path.getsize(sp) // 1024
                    return True, f"Screenshot saved, Master!\nFile: {filename}\nPath: {sp}\nSize: {size_kb} KB"
                else:
                    if os.path.exists(sp):
                        os.remove(sp)
                    import ctypes
                    ctypes.windll.user32.keybd_event(0x2C, 0, 0, 0)
                    ctypes.windll.user32.keybd_event(0x2C, 0, 2, 0)
                    return True, "Pressed Print Screen. Image is in clipboard."
            return True, "Screenshots only supported on Windows currently."
        except Exception as e:
            return True, f"Screenshot failed: {str(e)[:100]}"

    # ===================== SYSTEM INFO =====================
    def _check_system_info(self, cmd):
        triggers = ["system info", "system status", "pc info", "computer info",
                    "system details", "my system", "pc status", "pc details",
                    "specs", "system specs", "hardware info"]
        if not any(t in cmd for t in triggers):
            return False, ""
        if not PSUTIL_AVAILABLE:
            return True, "Need psutil."
        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        boot = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot
        hours, remainder = divmod(int(uptime.total_seconds()), 3600)
        minutes = remainder // 60
        return True, (
            f"CPU: {cpu}% | RAM: {ram.percent}% ({ram.used//(1024**3):.1f}/{ram.total//(1024**3):.1f}GB)\n"
            f"Disk: {disk.percent}% | {platform.system()} {platform.release()}\n"
            f"Uptime: {hours}h {minutes}m | Processor: {platform.processor()[:50]}"
        )

    def _check_battery(self, cmd):
        triggers = ["battery", "charge", "battery level", "how much battery", "battery status", "power"]
        if not any(t in cmd for t in triggers):
            return False, ""
        if not PSUTIL_AVAILABLE:
            return True, "Need psutil."
        b = psutil.sensors_battery()
        if not b:
            return True, "No battery -- desktop system."
        status = "charging" if b.power_plugged else "on battery"
        time_left = ""
        if b.secsleft > 0 and not b.power_plugged:
            hrs = b.secsleft // 3600
            mins = (b.secsleft % 3600) // 60
            time_left = f" | Time left: {hrs}h {mins}m"
        return True, f"Battery: {b.percent}%, {status}{time_left}."

    def _check_ip_address(self, cmd):
        triggers = ["my ip", "ip address", "what is my ip", "show ip", "whats my ip", "what's my ip"]
        if not any(t in cmd for t in triggers):
            return False, ""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            r = f"Local: {ip}"
            if REQUESTS_AVAILABLE:
                try:
                    r += f" | Public: {requests.get('https://api.ipify.org', timeout=5).text}"
                except Exception:
                    pass
            return True, r
        except Exception:
            return True, "Could not get IP."

    def _check_wifi_info(self, cmd):
        triggers = ["wifi info", "wi-fi info", "network info", "wifi status",
                    "wifi details", "connected to", "what wifi", "which wifi",
                    "which network", "network status"]
        if not any(t in cmd for t in triggers):
            return False, ""
        try:
            if self.system == "Windows":
                r = subprocess.run(["netsh", "wlan", "show", "interfaces"],
                                   capture_output=True, text=True, timeout=10)
                ssid = signal = state = ""
                for line in r.stdout.split("\n"):
                    line = line.strip()
                    if "SSID" in line and "BSSID" not in line:
                        ssid = line.split(":")[-1].strip()
                    elif "Signal" in line:
                        signal = line.split(":")[-1].strip()
                    elif "State" in line:
                        state = line.split(":")[-1].strip()
                if ssid:
                    return True, f"WiFi: {ssid} | Signal: {signal} | {state}"
                return True, "No WiFi detected."
        except Exception:
            return True, "WiFi info unavailable."
        return False, ""

    def _check_clipboard(self, cmd):
        triggers = ["clipboard", "what did i copy", "paste", "pano",
                    "show clipboard", "whats in clipboard", "what's in clipboard",
                    "what's copied", "whats copied"]
        if not any(t in cmd for t in triggers):
            return False, ""
        if "copy " in cmd:
            text = re.sub(r"^.*?copy\s+", "", cmd).strip()
            if text:
                try:
                    if self.system == "Windows":
                        subprocess.run(["powershell", "-Command", f"Set-Clipboard -Value '{text}'"],
                                       capture_output=True)
                except Exception:
                    pass
                return True, "Copied to clipboard."
        try:
            if self.system == "Windows":
                c = subprocess.run(["powershell", "-Command", "Get-Clipboard"],
                                   capture_output=True, text=True, timeout=5).stdout.strip()
            else:
                c = ""
            if c:
                return True, f"Clipboard:\n{c[:500]}"
            return True, "Clipboard empty."
        except Exception:
            return True, "Can't read clipboard."
        

    def _check_brightness(self, cmd):
        triggers = ["brightness", "parlaklik", "screen brightness", "display brightness"]
        if not any(t in cmd for t in triggers):
            return False, ""
        if self.system != "Windows":
            return True, "Brightness: Windows only."

        try:
            import screen_brightness_control as sbc

            if any(t in cmd for t in ["up", "increase", "higher", "more", "brighter"]):
                current = sbc.get_brightness(display=0)
                current = current[0] if isinstance(current, list) else current
                new_val = min(100, current + 20)
                sbc.set_brightness(new_val, display=0)
                return True, f"Brightness increased to {new_val}%, Master."

            elif any(t in cmd for t in ["down", "decrease", "lower", "less", "dimmer", "dim"]):
                current = sbc.get_brightness(display=0)
                current = current[0] if isinstance(current, list) else current
                new_val = max(0, current - 20)
                sbc.set_brightness(new_val, display=0)
                return True, f"Brightness decreased to {new_val}%, Master."

            # Set exact brightness e.g. "set brightness to 70"
            val_match = re.search(r"(\d+)", cmd)
            if val_match:
                level = max(0, min(100, int(val_match.group(1))))
                sbc.set_brightness(level, display=0)
                return True, f"Brightness set to {level}%, Master."

            # Just show current brightness
            current = sbc.get_brightness(display=0)
            current = current[0] if isinstance(current, list) else current
            return True, f"Current brightness: {current}%, Master."

        except Exception as e:
            return True, f"Brightness control failed: {str(e)[:80]}\n(May not work on external/desktop monitors)"

    # ===================== FILE SEARCH =====================
    def _check_file_search(self, cmd):
        patterns = [
            r"find (?:files?|documents?) (?:named |called )?(.+?)(?:\s+(?:on|in)\s+(.+))?$",
            r"search (?:for )?(?:files?|documents?) (.+?)(?:\s+(?:on|in)\s+(.+))?$",
            r"locate (?:files?|documents?) (.+?)(?:\s+(?:on|in)\s+(.+))?$",
            r"where is (?:the )?(?:file |document )?(.+?)(?:\s+(?:on|in)\s+(.+))?$",
        ]
        for pattern in patterns:
            match = re.search(pattern, cmd)
            if match:
                name = match.group(1).strip()
                if name in ["file", "files", "document", "documents", "it", "that", "this"]:
                    return False, ""
                location = match.group(2)
                if location:
                    folder_map = {
                        "desktop": "Desktop", "downloads": "Downloads",
                        "documents": "Documents", "pictures": "Pictures",
                        "music": "Music", "videos": "Videos"
                    }
                    folder = folder_map.get(location.strip().lower(), location.strip())
                    search_path = os.path.join(os.path.expanduser("~"), folder)
                else:
                    search_path = os.path.expanduser("~")
                if not os.path.exists(search_path):
                    return True, "Folder not found, Master."
                results = []
                try:
                    for f in glob.iglob(os.path.join(search_path, f"**/*{name}*"), recursive=True):
                        results.append(f)
                        if len(results) >= 15:
                            break
                except Exception:
                    pass
                if not results:
                    return True, f"No files matching '{name}' found, Master."
                lines = [f"Found {len(results)} file(s):"]
                for r in results:
                    lines.append(f"  - {os.path.basename(r)} -- {r}")
                return True, "\n".join(lines)
        return False, ""

    # ===================== WEBCAM =====================
    def _check_webcam(self, cmd):
        triggers = ["take photo", "take a photo", "webcam", "take selfie",
                    "capture photo", "take picture", "take a picture",
                    "camera photo", "photo please", "click photo", "click a photo", "snap a photo"]
        if not any(t in cmd for t in triggers):
            return False, ""

        photos_dir = os.path.join(os.path.expanduser("~"), "Pictures", "Webcam")
        os.makedirs(photos_dir, exist_ok=True)
        filename = f"photo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(photos_dir, filename)

        try:
            import cv2
        except ImportError:
            return True, "Need opencv-python. Run: pip install opencv-python"

        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                return True, "No webcam detected, Master."
            time.sleep(1)
            ret, frame = cap.read()
            cap.release()
            if ret:
                cv2.imwrite(filepath, frame)
                return True, f"Photo captured, Master!\nSaved: {filepath}"
            return True, "Couldn't capture photo from webcam."
        except Exception as e:
            return True, f"Webcam error: {str(e)[:80]}"

    # ===================== SCREEN RECORD =====================
    def _check_screen_record(self, cmd):
        if any(t in cmd for t in ["start recording", "record screen", "screen record",
                                  "start screen record", "begin recording", "record my screen"]):
            try:
                import cv2
                import numpy as np
            except ImportError:
                return True, "Need opencv-python and numpy. Run: pip install opencv-python numpy"

            videos_dir = os.path.join(os.path.expanduser("~"), "Videos", "Recordings")
            os.makedirs(videos_dir, exist_ok=True)
            filename = f"recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}.avi"
            filepath = os.path.join(videos_dir, filename)

            if self.system == "Windows":
                import ctypes
                ctypes.windll.user32.SetProcessDPIAware()
                width = ctypes.windll.user32.GetSystemMetrics(0)
                height = ctypes.windll.user32.GetSystemMetrics(1)
            else:
                width, height = 1920, 1080

            def _record():
                import cv2
                import numpy as np
                fourcc = cv2.VideoWriter_fourcc(*'XVID')
                out = cv2.VideoWriter(filepath, fourcc, 10.0, (width, height))
                recording_flag = os.path.join(os.path.expanduser("~"), ".alfredx_recording")
                with open(recording_flag, "w") as f:
                    f.write("1")
                try:
                    from PIL import ImageGrab
                except ImportError:
                    out.release()
                    return
                while os.path.exists(recording_flag):
                    try:
                        img = ImageGrab.grab()
                        frame = np.array(img)
                        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                        frame = cv2.resize(frame, (width, height))
                        out.write(frame)
                    except Exception:
                        break
                out.release()

            threading.Thread(target=_record, daemon=True).start()
            return True, f"Recording started, Master!\nSay 'stop recording' to stop.\nSaving to: {filepath}"

        if any(t in cmd for t in ["stop recording", "end recording", "stop screen record", "finish recording"]):
            flag = os.path.join(os.path.expanduser("~"), ".alfredx_recording")
            if os.path.exists(flag):
                os.remove(flag)
                return True, "Recording stopped and saved, Master!"
            return True, "No active recording found."

        return False, ""

    # ===================== QR CODE =====================
    def _check_qr_code(self, cmd):
        qr_match = re.search(r"(?:generate|create|make)\s+(?:a\s+)?(?:qr code|qrcode|qr)\s+(?:for\s+|of\s+)?(.+)", cmd)
        if not qr_match:
            return False, ""

        data = qr_match.group(1).strip()
        pictures_dir = os.path.join(os.path.expanduser("~"), "Pictures", "QR Codes")
        os.makedirs(pictures_dir, exist_ok=True)
        filename = f"qr_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(pictures_dir, filename)

        try:
            import qrcode
        except ImportError:
            return True, "Need qrcode library. Run: pip install qrcode[pil]"

        try:
            qr = qrcode.make(data)
            qr.save(filepath)
            if self.system == "Windows":
                os.startfile(filepath)
            return True, f"QR code generated, Master!\nData: {data}\nSaved: {filepath}"
        except Exception as e:
            return True, f"QR code error: {str(e)[:80]}"

    # ===================== TEXT TO PDF =====================
    def _check_text_to_pdf(self, cmd):
        pdf_match = re.search(r"(?:create|make|generate)\s+(?:a\s+)?pdf\s+(?:with\s+)?(?:text\s+)?(.+)", cmd)
        if not pdf_match:
            pdf_match = re.search(r"(?:convert|save)\s+(?:text\s+)?(?:to|as)\s+pdf\s+(.+)", cmd)
        if not pdf_match:
            return False, ""

        content = pdf_match.group(1).strip()
        docs_dir = os.path.join(os.path.expanduser("~"), "Documents")
        filename = f"alfredx_doc_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(docs_dir, filename)

        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4
        except ImportError:
            try:
                self._create_simple_pdf(filepath, content)
                if os.path.exists(filepath):
                    if self.system == "Windows":
                        os.startfile(filepath)
                    return True, f"PDF created, Master!\nSaved: {filepath}"
            except Exception:
                pass
            return True, "Need reportlab. Run: pip install reportlab"

        try:
            c = canvas.Canvas(filepath, pagesize=A4)
            width, height = A4
            c.setFont("Helvetica", 12)
            y = height - 50
            for line in content.split("\\n"):
                if y < 50:
                    c.showPage()
                    c.setFont("Helvetica", 12)
                    y = height - 50
                c.drawString(50, y, line)
                y -= 20
            c.save()
            if self.system == "Windows":
                os.startfile(filepath)
            return True, f"PDF created, Master!\nSaved: {filepath}"
        except Exception as e:
            return True, f"PDF creation failed: {str(e)[:80]}"

    def _create_simple_pdf(self, filepath, text):
        lines = text.split("\\n") if "\\n" in text else [text]
        stream_lines = []
        y = 750
        for line in lines:
            safe = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
            stream_lines.append(f"BT /F1 12 Tf 50 {y} Td ({safe}) Tj ET")
            y -= 20
        stream = "\n".join(stream_lines)
        stream_bytes = stream.encode("latin-1", errors="replace")
        pdf = b"%PDF-1.4\n"
        offsets = []
        offsets.append(len(pdf))
        pdf += b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
        offsets.append(len(pdf))
        pdf += b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
        offsets.append(len(pdf))
        pdf += b"3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]/Contents 4 0 R/Resources<</Font<</F1 5 0 R>>>>>>endobj\n"
        offsets.append(len(pdf))
        pdf += f"4 0 obj<</Length {len(stream_bytes)}>>stream\n".encode() + stream_bytes + b"\nendstream endobj\n"
        offsets.append(len(pdf))
        pdf += b"5 0 obj<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>endobj\n"
        xref_pos = len(pdf)
        pdf += b"xref\n0 6\n0000000000 65535 f \n"
        for off in offsets:
            pdf += f"{off:010d} 00000 n \n".encode()
        pdf += f"trailer<</Size 6/Root 1 0 R>>\nstartxref\n{xref_pos}\n%%EOF".encode()
        with open(filepath, "wb") as f:
            f.write(pdf)

    # ===================== WHATSAPP =====================
    def _check_whatsapp(self, cmd):
        wa_match = re.search(r"(?:send\s+)?whatsapp\s+(?:to\s+)?(\+?\d{10,15})\s+(?:message\s+)?(.+)", cmd)
        if not wa_match:
            wa_match = re.search(r"(?:send\s+)?(?:message|msg)\s+(?:on\s+)?whatsapp\s+(?:to\s+)?(\+?\d{10,15})\s+(.+)", cmd)
        if wa_match:
            phone = wa_match.group(1).strip()
            message = wa_match.group(2).strip()
            try:
                import pywhatkit
                now = datetime.now()
                hour = now.hour
                minute = now.minute + 1
                if minute >= 60:
                    hour += 1
                    minute -= 60
                pywhatkit.sendwhatmsg(phone, message, hour, minute, wait_time=15)
                return True, f"WhatsApp message scheduled to {phone}, Master."
            except ImportError:
                encoded_msg = message.replace(" ", "%20")
                webbrowser.open(f"https://wa.me/{phone}?text={encoded_msg}")
                return True, f"Opening WhatsApp Web to send message to {phone}, Master."
            except Exception:
                encoded_msg = message.replace(" ", "%20")
                webbrowser.open(f"https://wa.me/{phone}?text={encoded_msg}")
                return True, f"Opening WhatsApp Web to send to {phone}, Master."

        if any(t in cmd for t in ["open whatsapp", "launch whatsapp"]):
            webbrowser.open("https://web.whatsapp.com")
            return True, "Opening WhatsApp Web, Master."

        return False, ""

    # ===================== GOOGLE MAPS =====================
    def _check_google_maps(self, cmd):
        dir_match = re.search(r"(?:directions?|navigate|route)\s+(?:from\s+)?(.+?)\s+to\s+(.+)", cmd)
        if dir_match:
            origin = dir_match.group(1).strip()
            dest = dir_match.group(2).strip()
            webbrowser.open(f"https://www.google.com/maps/dir/{origin.replace(' ', '+')}/{dest.replace(' ', '+')}")
            return True, f"Opening directions from {origin} to {dest}, Master."

        map_match = re.search(r"(?:show\s+)?(?:map|maps)\s+(?:of\s+|for\s+)?(.+)", cmd)
        if map_match:
            place = map_match.group(1).strip()
            webbrowser.open(f"https://www.google.com/maps/search/{place.replace(' ', '+')}")
            return True, f"Opening map of {place}, Master."

        nearby_match = re.search(r"(?:find|search|show|nearby)\s+(.+?)(?:\s+near\s+me|\s+nearby)", cmd)
        if not nearby_match:
            nearby_match = re.search(r"nearby\s+(.+)", cmd)
        if nearby_match:
            query = nearby_match.group(1).strip()
            webbrowser.open(f"https://www.google.com/maps/search/{query.replace(' ', '+')}+near+me")
            return True, f"Searching for {query} nearby, Master."

        return False, ""

    # ===================== STARTUP APPS =====================
    def _check_startup_apps(self, cmd):
        if not any(t in cmd for t in ["startup apps", "startup programs", "startup applications",
                                      "show startup", "list startup", "boot apps",
                                      "programs at startup", "auto start apps"]):
            return False, ""
        if self.system != "Windows":
            return True, "Startup apps: Windows only."

        lines = ["Startup Programs:"]
        try:
            result = subprocess.run([
                "powershell", "-Command",
                "Get-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Run' | "
                "ForEach-Object { $_.PSObject.Properties } | "
                "Where-Object { $_.Name -notlike 'PS*' } | "
                "ForEach-Object { $_.Name }"
            ], capture_output=True, text=True, timeout=10)
            if result.stdout.strip():
                lines.append("\nRegistry (Current User):")
                for app in result.stdout.strip().split("\n"):
                    if app.strip():
                        lines.append(f"  - {app.strip()}")
        except Exception:
            pass

        startup_folder = os.path.join(os.environ.get("APPDATA", ""),
                                      "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
        if os.path.exists(startup_folder):
            items = os.listdir(startup_folder)
            if items:
                lines.append("\nStartup Folder:")
                for item in items:
                    lines.append(f"  - {item}")

        if len(lines) == 1:
            lines.append("  No startup items found.")
        lines.append(f"\nStartup folder: {startup_folder}")
        return True, "\n".join(lines)

    # ===================== HASH =====================
    def _check_hash(self, cmd):
        hash_match = re.search(r"(?:hash|checksum)\s+(md5|sha1|sha256|sha512)\s+(?:of\s+)?(.+)", cmd)
        if not hash_match:
            hash_match = re.search(r"(md5|sha1|sha256|sha512)\s+(?:of\s+|hash\s+)?(.+)", cmd)
        if hash_match:
            algo = hash_match.group(1).lower()
            text = hash_match.group(2).strip()
            h = hashlib.new(algo)
            h.update(text.encode("utf-8"))
            result = h.hexdigest()
            if self.system == "Windows":
                try:
                    subprocess.run(["powershell", "-Command", f"Set-Clipboard -Value '{result}'"],
                                   capture_output=True, timeout=5)
                except Exception:
                    pass
            return True, f"{algo.upper()} hash of '{text}':\n{result}\n(Copied to clipboard)"
        return False, ""

    # ===================== CURRENCY =====================
    def _check_currency(self, cmd):
        currency_names = {
            "dollars": "USD", "dollar": "USD", "usd": "USD",
            "euros": "EUR", "euro": "EUR", "eur": "EUR",
            "pounds": "GBP", "pound": "GBP", "gbp": "GBP",
            "rupees": "INR", "rupee": "INR", "inr": "INR",
            "yen": "JPY", "jpy": "JPY", "yuan": "CNY", "cny": "CNY",
            "won": "KRW", "krw": "KRW", "lira": "TRY", "try": "TRY", "tl": "TRY",
            "ruble": "RUB", "rubles": "RUB", "rub": "RUB",
            "aud": "AUD", "cad": "CAD", "chf": "CHF",
            "sgd": "SGD", "aed": "AED", "sar": "SAR",
            "pkr": "PKR", "bdt": "BDT", "myr": "MYR",
        }

        curr_match = re.search(r"(?:convert\s+)?(\d+(?:\.\d+)?)\s*(\w+)\s+(?:to|in|into)\s+(\w+)", cmd)
        if not curr_match:
            return False, ""

        amount = float(curr_match.group(1))
        from_curr = curr_match.group(2).lower()
        to_curr = curr_match.group(3).lower()
        from_code = currency_names.get(from_curr, from_curr.upper())
        to_code = currency_names.get(to_curr, to_curr.upper())

        if len(from_code) != 3 or len(to_code) != 3:
            return False, ""
        if not from_code.isalpha() or not to_code.isalpha():
            return False, ""

        unit_words = ["km", "miles", "kg", "pounds", "lbs", "celsius", "fahrenheit",
                      "cm", "inches", "feet", "gallons", "liters", "mb", "gb",
                      "hours", "minutes", "seconds", "mph", "kmh", "oz"]
        if from_curr in unit_words or to_curr in unit_words:
            return False, ""

        if not REQUESTS_AVAILABLE:
            return True, "Need 'requests' library."

        try:
            resp = requests.get(f"https://api.exchangerate-api.com/v4/latest/{from_code}", timeout=10).json()
            rate = resp.get("rates", {}).get(to_code)
            if rate:
                result = amount * rate
                return True, f"{amount:.2f} {from_code} = {result:.2f} {to_code}\nRate: 1 {from_code} = {rate:.4f} {to_code}"
            return True, f"Couldn't find exchange rate for {to_code}."
        except Exception as e:
            return True, f"Currency conversion failed: {str(e)[:80]}"

    # ===================== TYPING SPEED =====================
    def _check_typing_speed(self, cmd):
        if any(t in cmd for t in ["typing test", "typing speed", "type test", "speed typing"]):
            webbrowser.open("https://www.typingtest.com")
            return True, "Opening typing speed test, Master. Good luck!"
        return False, ""

    # ===================== OCR =====================
    def _check_ocr(self, cmd):
        ocr_match = re.search(r"(?:read text|extract text|ocr|scan text)\s+(?:from\s+)?(?:image\s+|photo\s+|picture\s+|file\s+)?(.+)", cmd)
        if not ocr_match:
            return False, ""

        image_name = ocr_match.group(1).strip()

        try:
            from PIL import Image
        except ImportError:
            return True, "Need Pillow. Run: pip install Pillow"

        try:
            import pytesseract
        except ImportError:
            return True, "Need pytesseract. Run: pip install pytesseract"

        search_dirs = [
            os.path.join(os.path.expanduser("~"), d)
            for d in ["Desktop", "Documents", "Downloads", "Pictures",
                      os.path.join("Pictures", "Screenshots"),
                      os.path.join("Pictures", "Webcam")]
        ]

        found_path = None
        for d in search_dirs:
            if not os.path.exists(d):
                continue
            for f in glob.iglob(os.path.join(d, f"**/*{image_name}*"), recursive=True):
                if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.gif')):
                    found_path = f
                    break
            if found_path:
                break

        if not found_path:
            if os.path.exists(image_name):
                found_path = image_name
            else:
                return True, f"Image '{image_name}' not found, Master."

        try:
            img = Image.open(found_path)
            text = pytesseract.image_to_string(img).strip()
            if text:
                if self.system == "Windows":
                    try:
                        safe_text = text.replace("'", "''")[:500]
                        subprocess.run(["powershell", "-Command", f"Set-Clipboard -Value '{safe_text}'"],
                                       capture_output=True, timeout=5)
                    except Exception:
                        pass
                return True, f"Text extracted from {os.path.basename(found_path)}:\n\n{text[:1000]}\n\n(Copied to clipboard)"
            return True, f"No text found in {os.path.basename(found_path)}."
        except Exception as e:
            return True, f"OCR failed: {str(e)[:100]}"

    # ===================== COLOR PICKER =====================
    def _check_color_picker(self, cmd):
        if any(t in cmd for t in ["color picker", "pick a color", "pick color",
                                  "colour picker", "open color picker"]):
            if self.system == "Windows":
                try:
                    ps_script = (
                        "Add-Type -AssemblyName System.Windows.Forms;"
                        "$d = New-Object System.Windows.Forms.ColorDialog;"
                        "$d.FullOpen = $true;"
                        "if($d.ShowDialog() -eq 'OK'){"
                        "$c = $d.Color;"
                        "Write-Output \"RGB: $($c.R),$($c.G),$($c.B) | HEX: #$($c.R.ToString('X2'))$($c.G.ToString('X2'))$($c.B.ToString('X2'))\"}"
                    )
                    result = subprocess.run(["powershell", "-Command", ps_script],
                                            capture_output=True, text=True, timeout=30)
                    if result.stdout.strip():
                        hex_match = re.search(r"(#[A-Fa-f0-9]{6})", result.stdout)
                        if hex_match:
                            try:
                                subprocess.run(["powershell", "-Command",
                                               f"Set-Clipboard -Value '{hex_match.group(1)}'"],
                                               capture_output=True, timeout=5)
                            except Exception:
                                pass
                        return True, f"Color selected:\n{result.stdout.strip()}\n(HEX copied to clipboard)"
                    return True, "Color picker cancelled."
                except Exception as e:
                    return True, f"Color picker error: {str(e)[:80]}"
            return True, "Color picker: Windows only."

        hex_match = re.search(r"(?:hex to rgb|hex2rgb)\s+#?([A-Fa-f0-9]{6})", cmd)
        if hex_match:
            h = hex_match.group(1)
            r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
            return True, f"#{h.upper()} = RGB({r}, {g}, {b})"

        rgb_match = re.search(r"(?:rgb to hex|rgb2hex)\s+(\d{1,3})\s+(\d{1,3})\s+(\d{1,3})", cmd)
        if rgb_match:
            r, g, b = int(rgb_match.group(1)), int(rgb_match.group(2)), int(rgb_match.group(3))
            if all(0 <= c <= 255 for c in [r, g, b]):
                return True, f"RGB({r}, {g}, {b}) = #{r:02X}{g:02X}{b:02X}"
            return True, "RGB values must be 0-255."

        return False, ""

    # ===================== TASK SCHEDULER =====================
    def _check_task_scheduler(self, cmd):
        sched_match = re.search(r"schedule\s+(?:task\s+)?(.+?)\s+every\s+(\d+)\s*(minute|hour|min|hr|second|sec)s?", cmd)
        if sched_match:
            task = sched_match.group(1).strip()
            interval = int(sched_match.group(2))
            unit = sched_match.group(3).lower()
            seconds = interval * 60 if unit in ("minute", "min") else interval * 3600 if unit in ("hour", "hr") else interval

            def _repeat_task():
                while True:
                    time.sleep(seconds)
                    flag = os.path.join(os.path.expanduser("~"), f".alfredx_sched_{task.replace(' ', '_')}")
                    if not os.path.exists(flag):
                        break
                    msg = f"Scheduled task: {task}"
                    print(f"[Scheduler] {msg}")
                    if self._reminder_callback:
                        self._reminder_callback(msg)
                    try:
                        if self.system == "Windows":
                            import winsound
                            winsound.Beep(600, 200)
                    except Exception:
                        pass

            flag = os.path.join(os.path.expanduser("~"), f".alfredx_sched_{task.replace(' ', '_')}")
            with open(flag, "w") as f:
                f.write("1")
            threading.Thread(target=_repeat_task, daemon=True).start()
            return True, f"Scheduled: '{task}' every {interval} {unit}(s), Master.\nSay 'stop schedule {task}' to cancel."

        stop_match = re.search(r"(?:stop|cancel|remove)\s+schedule\s+(.+)", cmd)
        if stop_match:
            task = stop_match.group(1).strip()
            flag = os.path.join(os.path.expanduser("~"), f".alfredx_sched_{task.replace(' ', '_')}")
            if os.path.exists(flag):
                os.remove(flag)
                return True, f"Stopped scheduled task: '{task}'"
            return True, f"No scheduled task named '{task}' found."

        if any(t in cmd for t in ["show schedule", "list schedule", "my schedule",
                                  "scheduled tasks", "show tasks scheduled", "active schedules"]):
            home = os.path.expanduser("~")
            tasks = [f.replace(".alfredx_sched_", "").replace("_", " ")
                     for f in os.listdir(home) if f.startswith(".alfredx_sched_")]
            if not tasks:
                return True, "No active scheduled tasks, Master."
            lines = ["Active scheduled tasks:"]
            for i, t in enumerate(tasks, 1):
                lines.append(f"  {i}. {t}")
            return True, "\n".join(lines)

        return False, ""

    # ===================== SMART HOME =====================
    def _check_smart_home(self, cmd):
        smart_triggers = {
            ("turn on lights", "lights on", "switch on lights", "light on"):
                "Lights ON command sent. (Connect your smart home hub in settings to enable)",
            ("turn off lights", "lights off", "switch off lights", "light off"):
                "Lights OFF command sent. (Connect your smart home hub in settings to enable)",
            ("dim lights", "dim the lights", "lower lights"):
                "Lights dimmed. (Connect your smart home hub in settings to enable)",
            ("turn on fan", "fan on", "switch on fan"):
                "Fan ON command sent. (Connect your smart home hub in settings to enable)",
            ("turn off fan", "fan off", "switch off fan"):
                "Fan OFF command sent. (Connect your smart home hub in settings to enable)",
            ("turn on ac", "ac on", "air conditioner on", "start ac"):
                "AC ON command sent. (Connect your smart home hub in settings to enable)",
            ("turn off ac", "ac off", "air conditioner off", "stop ac"):
                "AC OFF command sent. (Connect your smart home hub in settings to enable)",
            ("set thermostat", "thermostat"):
                "Thermostat command received. (Connect your smart home hub in settings to enable)",
            ("lock door", "lock the door", "lock doors"):
                "Door lock command sent. (Connect your smart home hub in settings to enable)",
            ("unlock door", "unlock the door", "unlock doors"):
                "Door unlock command sent. (Connect your smart home hub in settings to enable)",
        }
        for triggers, response in smart_triggers.items():
            if any(t in cmd for t in triggers):
                return True, response
        return False, ""

    # ===================== GOOGLE CALENDAR =====================
    def _check_google_calendar(self, cmd):
        if any(t in cmd for t in ["open calendar", "show calendar", "my calendar",
                                  "google calendar", "open google calendar"]):
            webbrowser.open("https://calendar.google.com")
            return True, "Opening Google Calendar, Master."

        event_match = re.search(r"(?:create|add|new|schedule)\s+(?:a\s+)?(?:calendar\s+)?event\s+(.+?)(?:\s+on\s+(.+?))?(?:\s+at\s+(.+))?$", cmd)
        if event_match:
            title = event_match.group(1).strip()
            date = event_match.group(2)
            time_str = event_match.group(3)
            url = f"https://calendar.google.com/calendar/render?action=TEMPLATE&text={title.replace(' ', '+')}"
            if date:
                url += f"&details=Date: {date}"
            if time_str:
                url += f"&details=Time: {time_str}"
            webbrowser.open(url)
            return True, f"Opening Google Calendar to create event: '{title}', Master."

        if any(t in cmd for t in ["today's events", "todays events", "my events",
                                  "what's on my calendar", "whats on my calendar",
                                  "calendar events", "upcoming events"]):
            webbrowser.open("https://calendar.google.com")
            return True, "Opening Google Calendar to show your events, Master."

        return False, ""
