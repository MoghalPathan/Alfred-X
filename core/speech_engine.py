"""
AlfredX: Speech-to-Text Engine v2.2
Uses Google Speech Recognition (free, no API key).
Improved: auto-recovery, mic restart, better thresholds, retry logic.
"""
import threading
import time

try:
    import speech_recognition as sr
    SR_AVAILABLE = True
    print("[STT] SpeechRecognition loaded")
except ImportError:
    SR_AVAILABLE = False
    print("[STT] SpeechRecognition not found")


class SpeechEngine:
    def __init__(self):
        self.language = "en"
        self.is_listening = False
        self._stop_event = threading.Event()
        self._continuous = False
        self._continuous_callback = None
        self._continuous_error_callback = None
        self._mic_fail_count = 0
        self._max_mic_retries = 3

        if SR_AVAILABLE:
            self.recognizer = sr.Recognizer()
            self.recognizer.energy_threshold = 300
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.dynamic_energy_adjustment_damping = 0.15
            self.recognizer.dynamic_energy_ratio = 1.5
            self.recognizer.pause_threshold = 1.5
            self.recognizer.phrase_threshold = 0.2
            self.recognizer.non_speaking_duration = 0.3
        else:
            self.recognizer = None

    def set_language(self, lang_code):
        self.language = lang_code

    def _get_lang_code(self):
        lang_map = {
            "en": "en-US", "tr": "tr-TR", "hi": "hi-IN",
            "es": "es-ES", "fr": "fr-FR", "de": "de-DE",
        }
        return lang_map.get(self.language, "en-US")

    def _fresh_recognizer(self):
        """Reset recognizer to fix stuck state."""
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.dynamic_energy_adjustment_damping = 0.15
        self.recognizer.dynamic_energy_ratio = 1.5
        self.recognizer.pause_threshold = 1.5
        self.recognizer.phrase_threshold = 0.2
        self.recognizer.non_speaking_duration = 0.3
        print("[STT] Recognizer reset")

    def listen_once(self, callback=None, error_callback=None):
        """Listen for one phrase with retry logic."""
        if not SR_AVAILABLE:
            if error_callback:
                error_callback("SpeechRecognition not installed")
            return

        self._stop_event.clear()
        self.is_listening = True

        def _worker():
            retries = 0
            while retries < self._max_mic_retries:
                try:
                    with sr.Microphone() as source:
                        print("[STT] Calibrating...")
                        self.recognizer.adjust_for_ambient_noise(source, duration=0.8)
                        self.recognizer.energy_threshold = max(
                            150, min(self.recognizer.energy_threshold, 4000)
                        )
                        print(f"[STT] Threshold: {self.recognizer.energy_threshold:.0f}")
                        print("[STT] Listening...")

                        audio = self.recognizer.listen(
                            source, timeout=15, phrase_time_limit=30
                        )

                    if self._stop_event.is_set():
                        return

                    print("[STT] Recognizing...")
                    text = self.recognizer.recognize_google(
                        audio, language=self._get_lang_code()
                    )
                    print(f"[STT] Heard: {text}")
                    self._mic_fail_count = 0
                    if callback:
                        callback(text)
                    return

                except sr.WaitTimeoutError:
                    print("[STT] Timeout - no speech")
                    if error_callback:
                        error_callback("No speech detected")
                    return
                except sr.UnknownValueError:
                    print("[STT] Could not understand")
                    if error_callback:
                        error_callback("Could not understand audio")
                    return
                except sr.RequestError as e:
                    print(f"[STT] API error: {e}")
                    retries += 1
                    if retries < self._max_mic_retries:
                        print(f"[STT] Retrying... ({retries}/{self._max_mic_retries})")
                        time.sleep(1)
                    else:
                        if error_callback:
                            error_callback("Recognition service error")
                except OSError as e:
                    print(f"[STT] Microphone error: {e}")
                    self._mic_fail_count += 1
                    retries += 1
                    if self._mic_fail_count >= 2:
                        self._fresh_recognizer()
                        self._mic_fail_count = 0
                    if retries < self._max_mic_retries:
                        print(f"[STT] Mic retry in 2s... ({retries}/{self._max_mic_retries})")
                        time.sleep(2)
                    else:
                        if error_callback:
                            error_callback("Microphone not found or busy")
                except Exception as e:
                    print(f"[STT] Error: {e}")
                    if error_callback:
                        error_callback(str(e)[:80])
                    return
                finally:
                    self.is_listening = False

        thread = threading.Thread(target=_worker, daemon=True)
        thread.start()

    def start_continuous(self, callback=None, error_callback=None):
        """Start continuous listening with auto-recovery."""
        if not SR_AVAILABLE or self._continuous:
            return
        self._continuous = True
        self._continuous_callback = callback
        self._continuous_error_callback = error_callback
        self._stop_event.clear()

        def _loop():
            consecutive_errors = 0
            recalibrate_every = 30  # Re-calibrate every 30 cycles
            cycle = 0

            while self._continuous and not self._stop_event.is_set():
                self.is_listening = True
                try:
                    with sr.Microphone() as source:
                        # Re-calibrate periodically to adapt to environment changes
                        if cycle % recalibrate_every == 0:
                            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                            self.recognizer.energy_threshold = max(
                                150, min(self.recognizer.energy_threshold, 4000)
                            )
                            print(f"[STT-Cont] Re-calibrated: {self.recognizer.energy_threshold:.0f}")

                        audio = self.recognizer.listen(
                            source, timeout=10, phrase_time_limit=20
                        )

                    if self._stop_event.is_set() or not self._continuous:
                        break

                    text = self.recognizer.recognize_google(
                        audio, language=self._get_lang_code()
                    )
                    print(f"[STT-Cont] Heard: {text}")
                    consecutive_errors = 0
                    if self._continuous_callback:
                        self._continuous_callback(text)

                except sr.WaitTimeoutError:
                    pass
                except sr.UnknownValueError:
                    pass
                except sr.RequestError:
                    consecutive_errors += 1
                    if self._continuous_error_callback:
                        self._continuous_error_callback("Recognition service error")
                    time.sleep(min(2 * consecutive_errors, 10))
                except OSError:
                    consecutive_errors += 1
                    if consecutive_errors >= 3:
                        print("[STT-Cont] Too many mic errors, resetting...")
                        self._fresh_recognizer()
                        consecutive_errors = 0
                    if self._continuous_error_callback:
                        self._continuous_error_callback("Microphone error")
                    time.sleep(min(2 * consecutive_errors, 10))
                except Exception as e:
                    print(f"[STT-Cont] Error: {e}")
                    consecutive_errors += 1
                    time.sleep(1)

                cycle += 1

                # If too many consecutive errors, full reset
                if consecutive_errors >= 5:
                    print("[STT-Cont] Too many errors, full reset...")
                    self._fresh_recognizer()
                    consecutive_errors = 0
                    time.sleep(3)

            self.is_listening = False
            self._continuous = False
            print("[STT-Cont] Stopped")

        thread = threading.Thread(target=_loop, daemon=True)
        thread.start()
        print("[STT-Cont] Continuous listening started")

    def stop_continuous(self):
        self._continuous = False
        self._stop_event.set()

    def stop(self):
        self._stop_event.set()
        self._continuous = False
        self.is_listening = False