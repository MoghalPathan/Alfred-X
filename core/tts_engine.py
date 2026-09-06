"""
AlfredX: Text-to-Speech Engine v2.3
Edge-TTS (free) + pygame for audio playback.
FIXES:
  - Lock timeout increased from 0.5s → 8s (was silently dropping speech)
  - pygame.init() added before mixer init (fixes silent failure on some Windows setups)
  - asyncio timeout on edge_tts generation (prevents hung network calls holding the lock forever)
  - Deferred pygame init so a failure at import time doesn't permanently disable TTS
"""
import asyncio
import os
import tempfile
import threading
import time

try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
    print("[TTS] [OK] edge-tts loaded")
except ImportError:
    EDGE_TTS_AVAILABLE = False
    print("[TTS] [X] edge-tts not found")

PYGAME_AVAILABLE = False
try:
    import pygame
    # pygame.init() MUST come before pygame.mixer.init()
    # Without it, mixer silently fails on some Windows audio drivers
    if not pygame.get_init():
        pygame.init()
    pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=4096)
    PYGAME_AVAILABLE = True
    print("[TTS] [OK] pygame audio ready")
except Exception as e:
    print(f"[TTS] [X] pygame not available ({e}) -- will use subprocess fallback")

from config import LANGUAGES


class TTSEngine:
    def __init__(self):
        self.language = "en"
        self.is_speaking = False
        self._stop_event = threading.Event()
        self._speak_lock = threading.Lock()
        self._play_fail_count = 0

    def set_language(self, lang_code):
        self.language = lang_code

    def get_voice(self):
        return LANGUAGES.get(self.language, LANGUAGES["en"])["tts_voice"]

    async def _generate_audio(self, text, output_path):
        voice = self.get_voice()
        communicate = edge_tts.Communicate(text, voice, rate="+5%", pitch="-2Hz")
        # Timeout prevents a slow/stalled network call from holding the lock forever
        await asyncio.wait_for(communicate.save(output_path), timeout=20)

    def _reinit_pygame(self):
        """Reinitialize pygame mixer if it got stuck."""
        try:
            pygame.mixer.quit()
            time.sleep(0.2)
            if not pygame.get_init():
                pygame.init()
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=4096)
            print("[TTS] pygame mixer reinitialized")
            return True
        except Exception as e:
            print(f"[TTS] pygame reinit failed: {e}")
            return False

    def speak(self, text, callback=None):
        if not EDGE_TTS_AVAILABLE:
            print("[TTS] [X] Cannot speak -- edge-tts not installed")
            if callback:
                callback()
            return

        if not text or not text.strip():
            if callback:
                callback()
            return

        self._stop_event.clear()
        self.is_speaking = True

        def _worker():
            # BUG FIX: was 0.5s — far too short when edge_tts is mid-generation (1–3s network call).
            # The old timeout caused the lock to fail silently: callback fired but no audio played.
            # 8s gives the previous worker time to finish or abort cleanly.
            if not self._speak_lock.acquire(timeout=8):
                print("[TTS] Lock timeout — skipping (previous TTS still running after 8s)")
                self.is_speaking = False
                if callback:
                    callback()
                return

            tmp_path = None
            try:
                tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
                tmp_path = tmp.name
                tmp.close()

                # Generate audio with retry + asyncio timeout
                for attempt in range(2):
                    try:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        loop.run_until_complete(self._generate_audio(text, tmp_path))
                        loop.close()
                        break
                    except asyncio.TimeoutError:
                        print(f"[TTS] Generation timed out (attempt {attempt + 1})")
                        if loop and not loop.is_closed():
                            loop.close()
                        if attempt == 1:
                            print("[TTS] [X] Both generation attempts timed out")
                            return
                    except Exception as e:
                        print(f"[TTS] Generation attempt {attempt + 1} failed: {e}")
                        if loop and not loop.is_closed():
                            loop.close()
                        if attempt == 0:
                            time.sleep(1)
                        else:
                            return

                if self._stop_event.is_set():
                    return

                if not os.path.exists(tmp_path) or os.path.getsize(tmp_path) < 100:
                    print("[TTS] [X] Generated file empty or missing")
                    return

                print("[TTS] Playing...")
                self._play_audio(tmp_path)
                print("[TTS] [OK] Done")

            except Exception as e:
                print(f"[TTS] [X] Error: {e}")
            finally:
                self.is_speaking = False
                self._speak_lock.release()
                if tmp_path:
                    try:
                        time.sleep(0.3)
                        os.unlink(tmp_path)
                    except Exception:
                        pass
                if callback:
                    callback()

        thread = threading.Thread(target=_worker, daemon=True)
        thread.start()

    def _play_audio(self, filepath):
        """Play audio with auto-recovery."""
        if PYGAME_AVAILABLE:
            for attempt in range(2):
                try:
                    if not pygame.mixer.get_init():
                        self._reinit_pygame()

                    pygame.mixer.music.load(filepath)
                    pygame.mixer.music.play()

                    # Small delay: pygame needs a moment before get_busy() returns True
                    time.sleep(0.1)

                    start = time.time()
                    while pygame.mixer.music.get_busy():
                        if self._stop_event.is_set():
                            pygame.mixer.music.stop()
                            break
                        if time.time() - start > 120:
                            print("[TTS] Playback timeout, stopping")
                            pygame.mixer.music.stop()
                            break
                        time.sleep(0.1)

                    self._play_fail_count = 0
                    return

                except Exception as e:
                    print(f"[TTS] pygame attempt {attempt + 1} failed: {e}")
                    self._play_fail_count += 1
                    if attempt == 0:
                        self._reinit_pygame()
                        time.sleep(0.3)

        self._play_fallback(filepath)

    def _play_fallback(self, filepath):
        """Fallback audio playback."""
        import subprocess
        import platform
        system = platform.system()
        try:
            if system == "Windows":
                try:
                    subprocess.run(
                        ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", filepath],
                        capture_output=True, timeout=60
                    )
                    return
                except FileNotFoundError:
                    pass
                ps_cmd = (
                    f'Add-Type -AssemblyName presentationCore; '
                    f'$p = New-Object System.Windows.Media.MediaPlayer; '
                    f'$p.Open([Uri]"{filepath}"); $p.Play(); '
                    f'Start-Sleep -Seconds ([math]::Ceiling($p.NaturalDuration.TimeSpan.TotalSeconds + 1)); '
                    f'$p.Close()'
                )
                subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True, timeout=60)
            elif system == "Darwin":
                subprocess.run(["afplay", filepath], capture_output=True, timeout=60)
            else:
                for player in ["mpv", "ffplay", "aplay"]:
                    try:
                        args = [player]
                        if player == "mpv":
                            args += ["--no-video", "--really-quiet"]
                        elif player == "ffplay":
                            args += ["-nodisp", "-autoexit", "-loglevel", "quiet"]
                        args.append(filepath)
                        subprocess.run(args, capture_output=True, timeout=60)
                        return
                    except FileNotFoundError:
                        continue
        except Exception as e:
            print(f"[TTS] Playback error: {e}")

    def stop(self):
        self._stop_event.set()
        self.is_speaking = False
        if PYGAME_AVAILABLE:
            try:
                pygame.mixer.music.stop()
            except Exception:
                pass
