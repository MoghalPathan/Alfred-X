"""
AlfredX: AI Conversation Engine
Groq API (free) with Llama 3 for intelligent responses.
Integrates memory system for persistent context.
"""
import json
import os
import re
from datetime import datetime

try:
    import requests
    REQUESTS_OK = True
except ImportError:
    REQUESTS_OK = False

try:
    from groq import Groq
    GROQ_AVAILABLE = True
    print("[AIEngine] [OK] Groq library loaded")
except ImportError:
    GROQ_AVAILABLE = False
    print("[AIEngine] [X] Groq library not found")

from config import (
    GROQ_API_KEY, GROQ_MODEL, MAX_TOKENS, TEMPERATURE,
    LANGUAGES, AI_NAME, AI_TITLE, KNOWLEDGE_DIR
)


class AIEngine:
    def __init__(self):
        self.client = None
        self.language = "en"
        self.conversation_history = []
        self.knowledge_base = {}
        self.memory = None
        self.ollama_model = "llama3.2:3b"
        self.ollama_url = "http://localhost:11434/api/chat"
        self._online = True  # Set externally by MainWindow
        self._load_knowledge_base()
        self._init_client()

    def _init_client(self):
        print(f"[AIEngine] API Key present: {bool(GROQ_API_KEY)}")
        if GROQ_AVAILABLE and GROQ_API_KEY:
            try:
                self.client = Groq(api_key=GROQ_API_KEY)
                print("[AIEngine] [OK] Client ready")
            except Exception as e:
                print(f"[AIEngine] [X] Init failed: {e}")
        else:
            print("[AIEngine] [X] Offline mode")

    def _check_online(self):
        """Quick check — can we reach Groq?"""
        if not self.client:
            return False
        if not REQUESTS_OK:
            return True  # assume online, let it fail naturally
        try:
            requests.get("https://api.groq.com", timeout=2)
            return True
        except:
            return False        

    def set_language(self, lang_code):
        self.language = lang_code
        self.conversation_history.clear()

    def _build_system_prompt(self):
        lang = LANGUAGES.get(self.language, LANGUAGES["en"])
        timestamp = datetime.now().strftime("%A, %B %d, %Y -- %H:%M")

        # Knowledge base context
        kb_context = ""
        if self.knowledge_base:
            entries = []
            for cat, items in self.knowledge_base.items():
                for item in items:
                    entries.append(f"[{cat}] {item.get('title','')}: {item.get('content','')}")
            if entries:
                kb_context = "\n\nPrivate knowledge base:\n" + "\n".join(entries[:20])

        # Memory context
        mem_context = ""
        if self.memory:
            facts = self.memory.get_all_facts()
            if facts:
                mem_lines = [f"- {f['category']}/{f['key']}: {f['value']}" for f in facts]
                mem_context = "\n\nRemembered facts about the user:\n" + "\n".join(mem_lines[:30])

            recent = self.memory.get_recent_conversations(limit=10)
            if recent:
                conv_lines = [f"{m['role']}: {m['content'][:100]}" for m in recent]
                mem_context += "\n\nRecent conversation context:\n" + "\n".join(conv_lines)

        memory_instructions = (
            "\n\nMEMORY INSTRUCTIONS: If the user tells you personal info, respond with a hidden tag "
            "[REMEMBER:category:key:value] to save it. Categories: user, preferences, work, location. "
            "Example: if user says 'My name is Bruce', include [REMEMBER:user:name:Bruce] in your response. "
            "If user says to forget something, use [FORGET:category:key]."
        )

        return (
            f"{lang['persona']}\n\n"
            f"Date: {timestamp}\nName: {AI_NAME} -- {AI_TITLE}\n"
            f"Language: {lang['name']}"
            f"{kb_context}{mem_context}{memory_instructions}"
        )

    def chat(self, user_message):
        print(f"[AIEngine] >>> {user_message}")
        if not self.client:
            # No Groq — try Ollama directly
            ollama_reply = self._ollama_chat(user_message)
            if ollama_reply:
                if self.memory:
                    self.memory.log_message("user", user_message, self.language)
                    self.memory.log_message("assistant", ollama_reply, self.language)
                return ollama_reply
            return self._offline_response()

        # Log to memory
        if self.memory:
            self.memory.log_message("user", user_message, self.language)

        messages = [
            {"role": "system", "content": self._build_system_prompt()}
        ] + self.conversation_history[-20:]

        try:
            print(f"[AIEngine] Calling {GROQ_MODEL}...")
            resp = self.client.chat.completions.create(
                model=GROQ_MODEL, messages=messages,
                max_tokens=MAX_TOKENS, temperature=TEMPERATURE
            )
            reply = resp.choices[0].message.content.strip()
            print(f"[AIEngine] <<< {reply[:80]}...")

            # Process memory tags
            clean_reply = self._process_memory_tags(reply)

            self.conversation_history.append({"role": "assistant", "content": clean_reply})

            # Log to memory
            if self.memory:
                self.memory.log_message("assistant", clean_reply, self.language)

            return clean_reply

        except Exception as e:
            print(f"[AIEngine] [X] Groq failed: {e}")
            # Fallback to Ollama
            ollama_reply = self._ollama_chat(user_message)
            if ollama_reply:
                return ollama_reply
            err = str(e)
            if "rate_limit" in err.lower():
                return "I require a moment, Master. The channels are briefly congested."
            return f"Apologies Master, technical difficulty: {err[:120]}"

    def _process_memory_tags(self, text):
        """Extract and process [REMEMBER:...] and [FORGET:...] tags."""
        if not self.memory:
            return text

        # Process REMEMBER tags
        remember_pattern = r'\[REMEMBER:([^:]+):([^:]+):([^\]]+)\]'
        for match in re.finditer(remember_pattern, text):
            cat, key, value = match.group(1), match.group(2), match.group(3)
            self.memory.remember(cat.strip(), key.strip(), value.strip())
            print(f"[AIEngine] Remembered: {cat}/{key} = {value}")

        # Process FORGET tags
        forget_pattern = r'\[FORGET:([^:]+):([^\]]+)\]'
        for match in re.finditer(forget_pattern, text):
            cat, key = match.group(1), match.group(2)
            self.memory.forget(cat.strip(), key.strip())
            print(f"[AIEngine] Forgot: {cat}/{key}")

        # Remove tags from visible response
        clean = re.sub(remember_pattern, '', text)
        clean = re.sub(forget_pattern, '', clean)
        return clean.strip()

    def _offline_response(self):
        if self.language == "tr":
            return "Efendim, cevrimdisiyim. .env dosyaniza GROQ_API_KEY ekleyin."
        return "I'm offline, Master. Please add GROQ_API_KEY to your .env file. Get one free at console.groq.com"
    
    def _ollama_chat(self, user_message):
        """Offline fallback using local Ollama model."""
        try:
            import requests as req
            payload = {
                "model": self.ollama_model,
                "messages": [
                    {"role": "system", "content": self._build_system_prompt()},
                    {"role": "user", "content": user_message}
                ],
                "stream": False
            }
            resp = req.post(self.ollama_url, json=payload, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                reply = data.get("message", {}).get("content", "").strip()
                if reply:
                    clean_reply = self._process_memory_tags(reply)
                    self.conversation_history.append({"role": "assistant", "content": clean_reply})
                    print(f"[AIEngine] <<< Ollama: {clean_reply[:80]}...")
                    return clean_reply
        except Exception as e:"""
AlfredX: AI Conversation Engine
Groq API (free) with Llama 3 for intelligent responses.
Integrates memory system for persistent context.
"""
import json
import os
import re
from datetime import datetime

try:
    import requests
    REQUESTS_OK = True
except ImportError:
    REQUESTS_OK = False

try:
    from groq import Groq
    GROQ_AVAILABLE = True
    print("[AIEngine] [OK] Groq library loaded")
except ImportError:
    GROQ_AVAILABLE = False
    print("[AIEngine] [X] Groq library not found")

from config import (
    GROQ_API_KEY, GROQ_MODEL, MAX_TOKENS, TEMPERATURE,
    LANGUAGES, AI_NAME, AI_TITLE, KNOWLEDGE_DIR
)


class AIEngine:
    # NOTE: `provider` kept for backward compatibility with older UI code.
    # Valid values: "groq" | "ollama".
    def __init__(self, provider=None, mode=None):
        self.client = None
        self.language = "en"
        self.conversation_history = []
        self.knowledge_base = {}
        self.memory = None
        self.ollama_model = "llama3.2:3b"
        self.ollama_url = "http://localhost:11434/api/chat"
        self._online = True  # Set externally by MainWindow
        # Routing mode (what backend to use for chat)
        self.mode = (provider or mode or "auto").lower()
        self._load_knowledge_base()
        self._init_client()

        # Resolve "auto" after client init
        if self.mode not in ("groq", "ollama"):
            self.mode = "groq" if self.client else "ollama"

    def set_mode(self, mode: str):
        mode = (mode or "").lower().strip()
        if mode in ("groq", "ollama"):
            self.mode = mode

    def get_mode(self) -> str:
        return getattr(self, "mode", "groq")

    def _init_client(self):
        print(f"[AIEngine] API Key present: {bool(GROQ_API_KEY)}")
        if GROQ_AVAILABLE and GROQ_API_KEY:
            try:
                self.client = Groq(api_key=GROQ_API_KEY)
                print("[AIEngine] [OK] Client ready")
            except Exception as e:
                print(f"[AIEngine] [X] Init failed: {e}")
        else:
            print("[AIEngine] [X] Offline mode")

    def _check_online(self):
        """Quick check — can we reach Groq?"""
        if not self.client:
            return False
        if not REQUESTS_OK:
            return True  # assume online, let it fail naturally
        try:
            requests.get("https://api.groq.com", timeout=2)
            return True
        except:
            return False        

    def set_language(self, lang_code):
        self.language = lang_code
        self.conversation_history.clear()

    def _build_system_prompt(self):
        lang = LANGUAGES.get(self.language, LANGUAGES["en"])
        timestamp = datetime.now().strftime("%A, %B %d, %Y -- %H:%M")

        # Knowledge base context
        kb_context = ""
        if self.knowledge_base:
            entries = []
            for cat, items in self.knowledge_base.items():
                for item in items:
                    entries.append(f"[{cat}] {item.get('title','')}: {item.get('content','')}")
            if entries:
                kb_context = "\n\nPrivate knowledge base:\n" + "\n".join(entries[:20])

        # Memory context
        mem_context = ""
        if self.memory:
            facts = self.memory.get_all_facts()
            if facts:
                mem_lines = [f"- {f['category']}/{f['key']}: {f['value']}" for f in facts]
                mem_context = "\n\nRemembered facts about the user:\n" + "\n".join(mem_lines[:30])

            recent = self.memory.get_recent_conversations(limit=10)
            if recent:
                conv_lines = [f"{m['role']}: {m['content'][:100]}" for m in recent]
                mem_context += "\n\nRecent conversation context:\n" + "\n".join(conv_lines)

        memory_instructions = (
            "\n\nMEMORY INSTRUCTIONS: If the user tells you personal info, respond with a hidden tag "
            "[REMEMBER:category:key:value] to save it. Categories: user, preferences, work, location. "
            "Example: if user says 'My name is Bruce', include [REMEMBER:user:name:Bruce] in your response. "
            "If user says to forget something, use [FORGET:category:key]."
        )

        safety_instructions = (
            "\n\nOUTPUT RULES: Never display or speak internal tags (REMEMBER/FORGET/conversation_status) to the user. "
            "Do not mention backend/provider names like Groq or Ollama. If asked about the model, reply generically as "
            "'cloud model' or 'local model' based on context, without naming vendors."
        )

        return (
            f"{lang['persona']}\n\n"
            f"Date: {timestamp}\nName: {AI_NAME} -- {AI_TITLE}\n"
            f"Language: {lang['name']}"
            f"{kb_context}{mem_context}{memory_instructions}{safety_instructions}"
        )

    def chat(self, user_message):
        print(f"[AIEngine] >>> {user_message}")
        # Force Ollama mode (even if Groq client exists)
        if self.get_mode() == "ollama":
            if self.memory:
                self.memory.log_message("user", user_message, self.language)
            ollama_reply = self._ollama_chat(user_message)
            if ollama_reply:
                if self.memory:
                    self.memory.log_message("assistant", ollama_reply, self.language)
                return ollama_reply
            return "Ollama is not responding, Master. Please ensure it is running (ollama serve) and the model is pulled."

        # Groq mode
        if not self.client:
            # No Groq client available — fallback to Ollama
            ollama_reply = self._ollama_chat(user_message)
            if ollama_reply:
                if self.memory:
                    self.memory.log_message("user", user_message, self.language)
                    self.memory.log_message("assistant", ollama_reply, self.language)
                return ollama_reply
            return self._offline_response()

        # Log to memory
        if self.memory:
            self.memory.log_message("user", user_message, self.language)

        messages = [
            {"role": "system", "content": self._build_system_prompt()}
        ] + self.conversation_history[-20:]

        try:
            print(f"[AIEngine] Calling {GROQ_MODEL}...")
            resp = self.client.chat.completions.create(
                model=GROQ_MODEL, messages=messages,
                max_tokens=MAX_TOKENS, temperature=TEMPERATURE
            )
            reply = resp.choices[0].message.content.strip()
            print(f"[AIEngine] <<< {reply[:80]}...")

            # Process memory tags
            clean_reply = self._process_memory_tags(reply)

            self.conversation_history.append({"role": "assistant", "content": clean_reply})

            # Log to memory
            if self.memory:
                self.memory.log_message("assistant", clean_reply, self.language)

            return clean_reply

        except Exception as e:
            print(f"[AIEngine] [X] Groq failed: {e}")
            # Fallback to Ollama
            ollama_reply = self._ollama_chat(user_message)
            if ollama_reply:
                return ollama_reply
            err = str(e)
            if "rate_limit" in err.lower():
                return "I require a moment, Master. The channels are briefly congested."
            return f"Apologies Master, technical difficulty: {err[:120]}"

    def _process_memory_tags(self, text):
        """Extract and process [REMEMBER:...] and [FORGET:...] tags."""
        if not self.memory:
            return text

        # Process REMEMBER tags (bracketed and unbracketed)
        remember_pattern = r'\[REMEMBER:([^:]+):([^:]+):([^\]]+)\]'
        remember_pattern2 = r'\bREMEMBER\s*:?\s*([^:]+):([^:]+):([^\n\r\]]+)' 
        for match in re.finditer(remember_pattern, text):
            cat, key, value = match.group(1), match.group(2), match.group(3)
            self.memory.remember(cat.strip(), key.strip(), value.strip())
            print(f"[AIEngine] Remembered: {cat}/{key} = {value}")

        for match in re.finditer(remember_pattern2, text, flags=re.IGNORECASE):
            cat, key, value = match.group(1), match.group(2), match.group(3)
            self.memory.remember(cat.strip(), key.strip(), value.strip())
            print(f"[AIEngine] Remembered: {cat}/{key} = {value}")

        # Process FORGET tags
        forget_pattern = r'\[FORGET:([^:]+):([^\]]+)\]'
        for match in re.finditer(forget_pattern, text):
            cat, key = match.group(1), match.group(2)
            self.memory.forget(cat.strip(), key.strip())
            print(f"[AIEngine] Forgot: {cat}/{key}")

        # Remove tags / internal markers from visible response
        clean = re.sub(remember_pattern, '', text)
        clean = re.sub(forget_pattern, '', clean)
        clean = re.sub(remember_pattern2, '', clean, flags=re.IGNORECASE)
        clean = re.sub(r'\bconversation_status\s*:?\s*[^\n\r]+', '', clean, flags=re.IGNORECASE)
        return clean.strip()

    def _offline_response(self):
        if self.language == "tr":
            return "Efendim, cevrimdisiyim. .env dosyaniza GROQ_API_KEY ekleyin."
        return "I'm offline, Master. Please add GROQ_API_KEY to your .env file. Get one free at console.groq.com"
    
    def _ollama_chat(self, user_message):
        """Offline fallback using local Ollama model."""
        try:
            import requests as req
            payload = {
                "model": self.ollama_model,
                "messages": [
                    {"role": "system", "content": self._build_system_prompt()},
                    {"role": "user", "content": user_message}
                ],
                "stream": False
            }
            resp = req.post(self.ollama_url, json=payload, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                reply = data.get("message", {}).get("content", "").strip()
                if reply:
                    clean_reply = self._process_memory_tags(reply)
                    self.conversation_history.append({"role": "assistant", "content": clean_reply})
                    print(f"[AIEngine] <<< Ollama: {clean_reply[:80]}...")
                    return clean_reply
        except Exception as e:
            print(f"[AIEngine] [X] Ollama failed: {e}")
        return None

    def _load_knowledge_base(self):
        self.knowledge_base = {}
        if not os.path.exists(KNOWLEDGE_DIR):
            return
        for f in os.listdir(KNOWLEDGE_DIR):
            if f.endswith(".json"):
                try:
                    with open(os.path.join(KNOWLEDGE_DIR, f), "r", encoding="utf-8") as fh:
                        self.knowledge_base[f.replace(".json", "")] = json.load(fh)
                        print(f"[AIEngine] [OK] Knowledge: {f}")
                except Exception:
                    pass

    def add_knowledge(self, category, title, content):
        if category not in self.knowledge_base:
            self.knowledge_base[category] = []
        self.knowledge_base[category].append({
            "title": title, "content": content,
            "added": datetime.now().isoformat()
        })
        with open(os.path.join(KNOWLEDGE_DIR, f"{category}.json"), "w", encoding="utf-8") as f:
            json.dump(self.knowledge_base[category], f, indent=2, ensure_ascii=False)

    def clear_history(self):
        self.conversation_history.clear()

        print(f"[AIEngine] [X] Ollama failed: {e}")
        return None

    def _load_knowledge_base(self):
        self.knowledge_base = {}
        if not os.path.exists(KNOWLEDGE_DIR):
            return
        for f in os.listdir(KNOWLEDGE_DIR):
            if f.endswith(".json"):
                try:
                    with open(os.path.join(KNOWLEDGE_DIR, f), "r", encoding="utf-8") as fh:
                        self.knowledge_base[f.replace(".json", "")] = json.load(fh)
                        print(f"[AIEngine] [OK] Knowledge: {f}")
                except Exception:
                    pass

    def add_knowledge(self, category, title, content):
        if category not in self.knowledge_base:
            self.knowledge_base[category] = []
        self.knowledge_base[category].append({
            "title": title, "content": content,
            "added": datetime.now().isoformat()
        })
        with open(os.path.join(KNOWLEDGE_DIR, f"{category}.json"), "w", encoding="utf-8") as f:
            json.dump(self.knowledge_base[category], f, indent=2, ensure_ascii=False)

    def clear_history(self):
        self.conversation_history.clear()
