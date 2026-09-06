"""
AlfredX: Text-to-Speech Engine v2.2
Edge-TTS (free) + pygame for audio playback.
Improved: pygame auto-reinit, retry logic, queue protection.
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

try:
    import pygame
    pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=4096)
    PYGAME_AVAILABLE = True
    print("[TTS] [OK] pygame audio ready")
except Exception:
    PYGAME_AVAILABLE = False
    print("[TTS] [X] pygame not available -- will try subprocess fallback")

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
        await communicate.save(output_path)

    def _reinit_pygame(self):
        """Reinitialize pygame mixer if it got stuck."""
        try:
            pygame.mixer.quit()
            time.sleep(0.2)
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
            # Prevent overlapping speech
            if not self._speak_lock.acquire(timeout=0.5):
                print("[TTS] Already speaking, skipping")
                if callback:
                    callback()
                return

            tmp_path = None
            try:
                tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
                tmp_path = tmp.name
                tmp.close()

                # Generate audio with retry
                for attempt in range(2):
                    try:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        loop.run_until_complete(self._generate_audio(text, tmp_path))
                        loop.close()
                        break
                    except Exception as e:
                        print(f"[TTS] Generation attempt {attempt+1} failed: {e}")
                        if attempt == 0:
                            time.sleep(1)
                        else:
                            raise

                if self._stop_event.is_set():
                    return

                # Verify file exists and has content
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

                    # Wait for playback with timeout (max 120s)
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
                    print(f"[TTS] pygame attempt {attempt+1} failed: {e}")
                    self._play_fail_count += 1
                    if attempt == 0:
                        self._reinit_pygame()
                        time.sleep(0.3)

        # Subprocess fallback
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
