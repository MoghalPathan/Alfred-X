# AlfredX

![Python application](https://github.com/MoghalPathan/Alfred-X/actions/workflows/python-app.yml/badge.svg)

AlfredX is an AI desktop assistant for Windows, built with Python and PyQt5. It combines a HUD-style interface, voice conversation, system control and bilingual (English/Turkish) support. The assistant is inspired by Alfred Pennyworth (DC Comics) and JARVIS (Marvel).

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Command Reference](#command-reference)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Screenshots](#screenshots)
- [Author](#author)
- [Acknowledgments](#acknowledgments)

---

## Features

| Feature | Status |
|---------|--------|
| Voice input (speech-to-text) | Complete |
| Voice output (text-to-speech) | Complete |
| AI conversation (Groq / Llama 3) | Complete |
| Bilingual support (English / Turkish, manual toggle) | Complete |
| Voice and text login ("Winter Soldier Protocol") | Complete |
| HUD-style interface | Complete |
| Animated AI core | Complete |
| System monitor gauges | Complete |
| Voice waveform visualizer | Complete |
| Custom knowledge base | Complete |
| Timers and reminders | Complete |
| To-do list | Complete |
| Mobile companion control | In progress |

### Authentication (Winter Soldier Protocol)

There are two ways to log in.

**Option A: 10-word activation sequence.** Speak or type the words in order:

```
Thomas, Martha, Shadow, Legacy, Protocol,
Guardian, Vengeance, Justice, Batman, Activate
```

**Option B: Text password.** Type `MEZEYAT`.

### Bilingual Support

- **English:** British butler personality (formal, witty, addresses the user as "Sir" or "Master").
- **Turkish:** Casual, friendly assistant.
- **Language toggle:** Switch at any time with the EN/TR button. The language is not auto-detected mid-conversation.

### System Control

Open and close applications, take screenshots, view system information, lock the screen, shut down or restart, adjust brightness, access the clipboard, search for files and navigate folders.

### Media Control

Volume up, down and mute; play, pause and skip tracks; Spotify integration.

### AI Conversation and Memory

- Natural language understanding through the Groq API (Llama 3).
- Multi-turn context retention.
- Persistent memory of personal facts (name, birthday, favorite color and so on) stored in a local database.
- Custom knowledge base ("Alfred Codex") built from reference documents.

### Interface

Cyan/teal HUD layout with a rotating AI core animation, circular system gauges, a voice waveform visualizer and a real-time activity log.

### Mobile Control (In Progress)

Groundwork for a companion mobile interface built with FastAPI and WebSocket, styled to match the desktop theme. This feature is not yet fully functional.

### Additional Features

System tray with background running, global hotkey (`Ctrl+Shift+A`), wake word detection ("Alfred" / "Hey Alfred"), timers and reminders, to-do list, unit conversion, calculator, and weather and news (optional API keys).

---

## Installation

### Prerequisites

- Python 3.10 or later
- Windows 10 or 11
- Microphone
- Internet connection (required for AI features)

### 1. Clone the repository

```bash
git clone https://github.com/MoghalPathan/Alfred-X.git
cd Alfred-X
```

### 2. Create a virtual environment

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API keys

Copy the example environment file:

```bash
cp .env.example .env
```

Then edit `.env` and add your keys:

```
# Required: free key from https://console.groq.com
GROQ_API_KEY=your_groq_key_here

# Optional: free key from https://openweathermap.org/api
WEATHER_API_KEY=your_weather_key_here

# Optional: free key from https://newsapi.org
NEWS_API_KEY=your_news_key_here

# Optional: Gmail (must be an App Password, not your normal password)
GMAIL_ADDRESS=your.email@gmail.com
GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
```

> **Note:** Never commit your real `.env` file. It is listed in `.gitignore`; only `.env.example`, which contains placeholder values, is pushed to GitHub.

---

## Usage

Run the application:

```bash
python main.py
```

### Login options

1. **Voice activation:** speak the 10 activation words in order.
2. **Text password:** enter `MEZEYAT`.

---

## Command Reference

Anything that does not match a command below is passed to the AI, so you can ask it to write a poem, help with code, recommend a book, summarize text, or simply talk.

### Time and Date

```
what time is it
current time
what day is today
today's date
```

### Calculations and Conversions

```
calculate 25 * 4
what is 20% of 500
convert 5 km to miles
convert 100 fahrenheit to celsius
convert 10 kg to pounds
```

### Applications

```
open chrome
open notepad
open calculator
open file explorer
launch vscode
close notepad
open spotify
open discord
```

### Web and Knowledge

```
search for python tutorials
google machine learning
who is albert einstein
what is quantum computing
tell me about mars
```

### Media and Volume

```
volume up
volume down
mute
max volume
pause music
next track
play spotify imagine dragons
```

### System

```
system info
battery
my ip
wifi info
lock computer
empty recycle bin
sleep mode
```

### Files and Folders

```
open downloads
open desktop
take a screenshot
create folder TestFolder on desktop
find files named test
```

### Timers and Reminders

```
set timer for 10 seconds
remind me to drink water in 30 seconds
show reminders
```

### Memory and Personalization

```
my name is Bruce
what is my name?
remember that my favorite color is blue
what is my favorite color
forget my favorite color
```

### To-Do List

```
add todo buy groceries
show todos
complete task 1
delete task 2
```

### Fun

```
tell me a joke
give me a quote
flip a coin
roll a dice
generate password
```

### Turkish Examples

```
Chrome'u aç
Saat kaç?
Ekran görüntüsü al
Sesi aç
Hava durumu
```

---

## Tech Stack

| Component | Purpose |
|-----------|---------|
| PyQt5 | Desktop GUI framework |
| SpeechRecognition | Voice input (Google API, free) |
| Edge-TTS | Voice output (Microsoft, free, no key needed) |
| Groq API | LLM backend (Llama 3, free tier) |
| FastAPI + WebSocket | Mobile companion control (in progress) |
| psutil, pycaw | System and audio monitoring |
| SQLite | Persistent memory and conversation storage |
| PyInstaller | Windows executable packaging |
| OpenCV, spotipy, pywhatkit, yt-dlp | Media and automation extras |

---

## Project Structure

```
AlfredX/
├── main.py                     # Entry point
├── config.py                   # Configuration
├── requirements.txt            # Dependencies
├── .env.example                # API key template (safe to commit)
├── core/
│   ├── ai_engine.py            # Groq LLM integration
│   ├── tts_engine.py / tts.py  # Edge-TTS voice output
│   ├── speech_engine.py        # Speech recognition
│   ├── wake_word.py            # "Alfred" wake word detection
│   ├── global_hotkey.py        # Ctrl+Shift+A hotkey
│   ├── language_switcher.py    # EN/TR toggle
│   ├── memory.py               # Persistent memory system
│   ├── chat_history.py         # Conversation history
│   ├── commands.py             # Command parsing and routing
│   ├── music_service.py        # Media and Spotify control
│   └── embedded_server.py      # Mobile control backend (in progress)
├── gui/
│   ├── login_screen.py         # Login UI
│   ├── main_window.py          # Main HUD interface
│   ├── styles.py               # QSS stylesheet
│   └── widgets/                # AI orb, gauges, waveform, etc.
└── data/
    ├── alfred_memory.db        # AI conversation memory (gitignored)
    ├── codex/Alfred_Codex.pdf  # Knowledge base source document
    ├── knowledge/              # Custom knowledge JSON files
    └── music/                  # Local music files
```

---

## Screenshots

<img width="960" height="540" alt="1" src="https://github.com/user-attachments/assets/43fb8ee2-f797-4e92-8c47-b32b138a1e04" />
<img width="960" height="540" alt="2" src="https://github.com/user-attachments/assets/dae8f7d6-8b83-4aa7-b9aa-58dc75d9f187" />
<img width="960" height="540" alt="3" src="https://github.com/user-attachments/assets/cec9e760-6174-41b0-98ca-fde43c7031bb" />
<img width="960" height="540" alt="4" src="https://github.com/user-attachments/assets/c1ed11eb-2134-4f72-82ef-b8bf294f440e" />
<img width="960" height="540" alt="5" src="https://github.com/user-attachments/assets/5e0e101a-e85b-4f9c-851c-2a8ea5a2fdc7" />
<img width="960" height="540" alt="6" src="https://github.com/user-attachments/assets/489b6f6c-55fb-487b-95af-85acc4b2ad98" />

---

## Author

**Korabu Naved Arif**

- Final Year Computer Engineering Project, S.B. Patil College of Engineering, Pune
- Email: navedmoghalpathan@proton.me
- GitHub: [@MoghalPathan](https://github.com/MoghalPathan)

Built with teammates Bhagat, Mansi and Sayali.

## Acknowledgments

- JARVIS from Iron Man
- Alfred Pennyworth from DC Comics
- Winter Soldier activation sequence from Marvel
