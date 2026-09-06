"""
AlfredX: Wake Word Detector v2.2
Listens continuously for "Alfred" keyword using speech recognition.
Improved: periodic recalibration, fuzzy matching, auto-recovery, mic reset.
"""
import threading
import time

try:
    import speech_recognition as sr
    SR_OK = True
except ImportError:
    SR_OK = False


class WakeWordDetector:
    """Listens for 'Alfred' wake word in background with auto-recovery."""

    WAKE_WORDS = [
        "alfred", "hey alfred", "alfredx", "ok alfred",
        "alfred x", "hey alfred x", "alfred ex",
    ]

    # Fuzzy matches — words that sound like "alfred" in noisy environments
    FUZZY_WORDS = [
        "offered", "altered", "albert", "elfrid", "alford",
        "ulfred", "alferd", "alfret", "hey offer",
    ]

    def __init__(self):
        self._running = False
        self._thread = None
        self._callback = None
        self._error_count = 0

        if SR_OK:
            self._init_recognizer()
        else:
            self.recognizer = None

    def _init_recognizer(self):
        """Create a fresh recognizer instance."""
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.dynamic_energy_adjustment_damping = 0.15
        self.recognizer.dynamic_energy_ratio = 1.5
        self.recognizer.pause_threshold = 0.8
        self.recognizer.phrase_threshold = 0.2
        self.recognizer.non_speaking_duration = 0.3

    def start(self, callback):
        """Start listening for wake word. callback() is called when detected."""
        if not SR_OK or self._running:
            return
        self._callback = callback
        self._running = True
        self._error_count = 0
        self._thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._thread.start()
        print("[WakeWord] Listening for 'Alfred'...")

    def stop(self):
        self._running = False
        print("[WakeWord] Stopped")

    @property
    def is_running(self):
        return self._running

    def _is_wake_word(self, text):
        """Check if text contains wake word (exact or fuzzy)."""
        text = text.lower().strip()

        # Exact match
        if any(w in text for w in self.WAKE_WORDS):
            return True

        # Fuzzy match
        if any(w in text for w in self.FUZZY_WORDS):
            print(f"[WakeWord] Fuzzy match: '{text}'")
            return True

        return False

    def _listen_loop(self):
        cycle = 0
        recalibrate_every = 20  # Re-calibrate every 20 cycles

        while self._running:
            try:
                with sr.Microphone() as source:
                    # Calibrate periodically to adapt to changing environment
                    if cycle % recalibrate_every == 0:
                        self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                        self.recognizer.energy_threshold = max(
                            150, min(self.recognizer.energy_threshold, 4000)
                        )
                        if cycle == 0:
                            print(f"[WakeWord] Threshold: {self.recognizer.energy_threshold:.0f}")

                    audio = self.recognizer.listen(
                        source, timeout=5, phrase_time_limit=3
                    )

                if not self._running:
                    break

                try:
                    text = self.recognizer.recognize_google(
                        audio, language="en-US"
                    ).lower().strip()
                    print(f"[WakeWord] Heard: {text}")
                    self._error_count = 0

                    if self._is_wake_word(text):
                        print("[WakeWord] WAKE WORD DETECTED!")
                        self._running = False
                        if self._callback:
                            self._callback()
                        return

                except sr.UnknownValueError:
                    pass
                except sr.RequestError:
                    self._error_count += 1
                    time.sleep(min(2 * self._error_count, 10))

            except sr.WaitTimeoutError:
                pass
            except OSError as e:
                print(f"[WakeWord] Mic error: {e}")
                self._error_count += 1
                if self._error_count >= 3:
                    print("[WakeWord] Resetting recognizer...")
                    self._init_recognizer()
                    self._error_count = 0
                time.sleep(2)
            except Exception as e:
                print(f"[WakeWord] Error: {e}")
                self._error_count += 1
                time.sleep(1)

            cycle += 1

            # Full reset after too many errors
            if self._error_count >= 5:
                print("[WakeWord] Too many errors, full reset...")
                self._init_recognizer()
                self._error_count = 0
                time.sleep(3)
