# 🦇 AlfredX: The Waynecore Assistant

> *"I shall be your guide through the digital night, Master Wayne."*

A sophisticated AI desktop assistant inspired by **Alfred Pennyworth** (DC Comics) and **JARVIS** (Marvel). Built with Python + PyQt5, featuring a JARVIS-style HUD interface, voice conversation, and bilingual support.

<p align="center">
  <a href="#features">Features</a> •
  <a href="#installation">Installation</a> •
  <a href="#usage">Usage</a> •
  <a href="#command-reference">Commands</a> •
  <a href="#tech-stack">Tech Stack</a> •
  <a href="#project-structure">Structure</a>
</p>

---

## 🎯 Features

### 🎤 Winter Soldier Protocol (Voice/Text Login)
Two ways to authenticate:

**Option A — 10-Word Activation Sequence** (speak or type in order):
```
Thomas → Martha → Shadow → Legacy → Protocol →
Guardian → Vengeance → Justice → Batman → Activate
```

**Option B — Text Password:** Type `MEZEYAT`

### 🌐 Bilingual Support
- **English**: British butler personality (formal, witty, "Sir/Master")
- **Turkish**: Casual friendly assistant
- **Manual toggle**: Switch languages anytime via the EN/TR button (does not auto-detect mid-conversation)

### 💻 System Control
Open/close apps, screenshots, system info, lock screen, shutdown/restart, brightness, clipboard, file search, folder navigation

### 🎵 Media Control
Volume up/down/mute, play/pause/skip tracks, Spotify integration

### 🧠 AI Conversation & Memory
- Natural language understanding via Groq API (Llama 3)
- Full multi-turn context retention
- Remembers personal facts you tell it (name, birthday, favorite color, etc.) permanently in its database
- Custom knowledge base ("Alfred Codex") built from reference documents

### 🎨 JARVIS-Style GUI
Cyan/teal HUD interface, rotating AI core animation, circular system gauges, voice waveform visualization, real-time activity log

### 📱 Mobile Control (In Progress)
Companion mobile UI groundwork built via FastAPI + WebSocket, styled to match the cinematic Alfred theme — not yet fully functional

### 🔧 Extras
System tray with background running, global hotkey (`Ctrl+Shift+A`), wake word detection ("Alfred" / "Hey Alfred"), timers & reminders, to-do list, unit conversion, calculator, weather & news (optional API keys)

| Feature | Status |
|---------|--------|
| 🎤 Voice Input (Speech-to-Text) | ✅ |
| 🔊 Voice Output (Text-to-Speech) | ✅ |
| 🧠 AI Conversation (Groq/Llama 3) | ✅ |
| 🌐 Bilingual (English/Turkish, manual toggle) | ✅ |
| 🔐 Winter Soldier Protocol Login | ✅ |
| 🎨 JARVIS-style HUD Interface | ✅ |
| 💠 Animated AI Orb | ✅ |
| 📊 System Monitor Gauges | ✅ |
| 🌊 Voice Waveform Visualizer | ✅ |
| 📚 Custom Knowledge Base | ✅ |
| ⏰ Timers & Reminders | ✅ |
| 🗒️ To-Do List | ✅ |
| 📱 Mobile Companion Control | 🚧 In Progress |

---

## 📦 Installation

### Prerequisites
- Python 3.10+
- Windows 10/11
- Microphone
- Internet connection (for AI features)

### 1. Clone Repository
```bash
git clone https://github.com/MoghalPathan/Alfred-X.git
cd Alfred-X
```

### 2. Create Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure API Keys
```bash
cp .env.example .env
```
Edit `.env` and add your keys:
```
# REQUIRED — Get free at https://console.groq.com
GROQ_API_KEY=your_groq_key_here

# OPTIONAL — Get free at https://openweathermap.org/api
WEATHER_API_KEY=your_weather_key_here

# OPTIONAL — Get free at https://newsapi.org
NEWS_API_KEY=your_news_key_here

# OPTIONAL — Gmail (must be an App Password, not your normal password)
GMAIL_ADDRESS=your.email@gmail.com
GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
```
> ⚠️ Never commit your real `.env` file — it's gitignored. Only `.env.example` (with placeholder values) is pushed to GitHub.

---

## 🚀 Usage

### Run the Application
```bash
python main.py
```

### Login Options
1. **Voice Activation**: Speak the 10 activation words
2. **Text Password**: Enter `MEZEYAT`

---

## 📋 Command Reference

### Time & Date
`what time is it` • `current time` • `what day is today` • `today's date`

### Calculations & Conversions
`calculate 25 * 4` • `what is 20% of 500` • `convert 5 km to miles` • `convert 100 fahrenheit to celsius` • `convert 10 kg to pounds`

### Apps
`open chrome` • `open notepad` • `open calculator` • `open file explorer` • `launch vscode` • `close notepad` • `open spotify` • `open discord`

### Web & Knowledge
`search for python tutorials` • `google machine learning` • `who is albert einstein` • `what is quantum computing` • `tell me about mars`

### Media & Volume
`volume up` • `volume down` • `mute` • `max volume` • `pause music` • `next track` • `play spotify imagine dragons`

### System
`system info` • `battery` • `my ip` • `wifi info` • `lock computer` • `empty recycle bin` • `sleep mode`

### Files & Folders
`open downloads` • `open desktop` • `take a screenshot` • `create folder TestFolder on desktop` • `find files named test`

### Timers & Reminders
`set timer for 10 seconds` • `remind me to drink water in 30 seconds` • `show reminders`

### Memory & Personalization
`my name is Bruce` • `what is my name?` • `remember that my favorite color is blue` • `what is my favorite color` • `forget my favorite color`

### To-Do List
`add todo buy groceries` • `show todos` • `complete task 1` • `delete task 2`

### Fun
`tell me a joke` • `give me a quote` • `flip a coin` • `roll a dice` • `generate password`

### Turkish Examples
`Chrome'u aç` • `Saat kaç?` • `Ekran görüntüsü al` • `Sesi aç` • `Hava durumu`

### AI Conversation (anything else)
Anything that doesn't match a command goes to the AI — write a poem, help with code, get a book recommendation, ask it to summarize something, or just talk.

---

## 🛠 Tech Stack

- **PyQt5** — Desktop GUI framework
- **SpeechRecognition** — Voice input (Google API, free)
- **Edge-TTS** — Voice output (Microsoft, free, no key needed)
- **Groq API** — LLM brain (Llama 3, free tier)
- **FastAPI + WebSocket** — Mobile companion control (in progress)
- **psutil, pycaw** — System & audio monitoring
- **SQLite** — Persistent memory/conversation storage
- **PyInstaller** — Windows executable packaging
- **OpenCV, spotipy, pywhatkit, yt-dlp** — Media & automation extras

---

## 📁 Project Structure

```
AlfredX/
├── main.py                    # Entry point
├── config.py                  # All configuration
├── requirements.txt           # Dependencies
├── .env.example                # API key template (safe to push)
├── core/
│   ├── ai_engine.py            # Groq LLM integration
│   ├── tts_engine.py / tts.py  # Edge-TTS voice output
│   ├── speech_engine.py        # Speech recognition
│   ├── wake_word.py            # "Alfred" wake word detection
│   ├── global_hotkey.py        # Ctrl+Shift+A hotkey
│   ├── language_switcher.py    # EN/TR toggle
│   ├── memory.py                # Persistent memory system
│   ├── chat_history.py          # Conversation history
│   ├── commands.py              # Command parsing/routing
│   ├── music_service.py         # Media/Spotify control
│   └── embedded_server.py       # Mobile control backend (in progress)
├── gui/
│   ├── login_screen.py          # Winter Soldier Protocol login UI
│   ├── main_window.py           # Main HUD interface
│   ├── styles.py                # QSS stylesheet
│   └── widgets/                 # AI orb, gauges, waveform, etc.
└── data/
    ├── alfred_memory.db          # AI conversation memory (gitignored)
    ├── codex/Alfred_Codex.pdf    # Knowledge base source document
    ├── knowledge/                 # Custom knowledge JSON files
    └── music/                     # Local music files
```

---

## 👨‍💻 Author

**Korabu Naved Arif**
- Final Year Computer Engineering Project
- S.B. Patil College of Engineering, Pune
- Email: navedmoghalpathan@proton.me
- GitHub: [@MoghalPathan](https://github.com/MoghalPathan)

Built with teammates Bhagat, Mansi, and Sayali.

---

## 🙏 Acknowledgments

- Inspired by JARVIS from Iron Man
- Alfred Pennyworth from DC Comics
- Winter Soldier activation sequence from Marvel

---

<p align="center">
  <strong>🦇 "I shall be your guide through the digital night, Master Wayne." 🦇</strong>
</p>
