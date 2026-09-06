#!/usr/bin/env python3
"""
AlfredX Music Service — JSON-over-stdin/stdout
Only JSON is written to stdout (one line per request).
Errors go to stderr.
"""

import os
import sys
import json
import glob
import platform

# Prevent pygame from printing its support prompt.
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

# Try to pick a sane default audio driver (helps first-run crashes).
# You can override by setting SDL_AUDIODRIVER in your environment.
if "SDL_AUDIODRIVER" not in os.environ:
    if platform.system().lower().startswith("win"):
        os.environ["SDL_AUDIODRIVER"] = "directsound"
    elif platform.system().lower() == "darwin":
        os.environ["SDL_AUDIODRIVER"] = "coreaudio"
    else:
        os.environ["SDL_AUDIODRIVER"] = "alsa"

try:
    import pygame
except Exception as e:
    sys.stderr.write(f"pygame import failed: {e}\n")
    sys.stderr.flush()
    raise

AUDIO_EXTS = (".mp3", ".wav", ".ogg", ".flac", ".aac", ".wma", ".m4a")


class MusicService:
    def __init__(self):
        # Mixer init can fail if no audio device; keep message on stderr.
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        except Exception as e:
            sys.stderr.write(f"pygame.mixer.init failed: {e}\n")
            sys.stderr.flush()
            raise

        self.queue = []
        self.index = 0
        self.volume = 0.8
        pygame.mixer.music.set_volume(self.volume)

    def _scan_dir(self, d):
        d = d or ""
        files = []
        for ext in AUDIO_EXTS:
            files.extend(glob.glob(os.path.join(d, "**", f"*{ext}"), recursive=True))
        files = [f for f in files if os.path.isfile(f)]
        files.sort()
        return files

    def _now(self):
        if not self.queue:
            return ""
        try:
            return os.path.basename(self.queue[self.index])
        except Exception:
            return ""

    def load_dir(self, d):
        self.queue = self._scan_dir(d)
        self.index = 0
        return {"ok": True, "total": len(self.queue), "dir": d}

    def play(self):
        if not self.queue:
            return {"ok": False, "error": "No tracks loaded."}
        path = self.queue[self.index]
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.play()
        except Exception as e:
            return {"ok": False, "error": f"Play failed: {str(e)[:160]}"}
        return {"ok": True, "now_playing": self._now(), "total": len(self.queue)}

    def pause(self):
        pygame.mixer.music.pause()
        return {"ok": True}

    def resume(self):
        pygame.mixer.music.unpause()
        return {"ok": True}

    def stop(self):
        pygame.mixer.music.stop()
        return {"ok": True}

    def next(self):
        if not self.queue:
            return {"ok": False, "error": "No tracks loaded."}
        self.index = (self.index + 1) % len(self.queue)
        return self.play()

    def prev(self):
        if not self.queue:
            return {"ok": False, "error": "No tracks loaded."}
        self.index = (self.index - 1) % len(self.queue)
        return self.play()

    def set_volume(self, v):
        try:
            v = float(v)
        except Exception:
            return {"ok": False, "error": "Volume must be a number (0.0 to 1.0)."}
        v = max(0.0, min(1.0, v))
        self.volume = v
        pygame.mixer.music.set_volume(self.volume)
        return {"ok": True, "volume": self.volume}

    def status(self):
        return {
            "ok": True,
            "now_playing": self._now(),
            "playing": bool(pygame.mixer.music.get_busy()),
            "volume": self.volume,
            "total": len(self.queue),
            "index": self.index,
        }


def main():
    svc = MusicService()

    # Read line-delimited JSON requests from stdin, write JSON response to stdout.
    for raw in sys.stdin:
        raw = raw.strip()
        if not raw:
            continue

        try:
            req = json.loads(raw)
            action = (req.get("action") or "").upper()

            if action == "PING":
                resp = {"ok": True}
            elif action == "LOAD_DIR":
                resp = svc.load_dir(req.get("dir") or "")
            elif action == "PLAY":
                resp = svc.play()
            elif action == "PAUSE":
                resp = svc.pause()
            elif action == "RESUME":
                resp = svc.resume()
            elif action == "STOP":
                resp = svc.stop()
            elif action == "NEXT":
                resp = svc.next()
            elif action == "PREV":
                resp = svc.prev()
            elif action == "VOLUME":
                resp = svc.set_volume(req.get("value", 0.8))
            elif action == "STATUS":
                resp = svc.status()
            else:
                resp = {"ok": False, "error": f"Unknown action: {action}"}

        except Exception as e:
            resp = {"ok": False, "error": str(e)[:200]}

        sys.stdout.write(json.dumps(resp) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
