"""
AlfredX: Embedded Server v2.2
==============================
- Serves mobile control panel at  GET /
- WebSocket command channel at    WS  /ws
- Health check at                 GET /status

HOW TO CONNECT FROM PHONE:
  1. Make sure phone and PC are on the same WiFi
  2. Find your PC's local IP (run: ipconfig → IPv4 Address)
  3. Open  http://<PC-IP>:8000  on your phone's browser
  4. That's it — voice + text control ready.
"""
import asyncio
import os
import threading
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn

_HERE = os.path.dirname(os.path.abspath(__file__))
MOBILE_UI_PATH = os.path.join(_HERE, "..", "data", "mobile_ui.html")


def build_app(on_command):
    app = FastAPI(title="AlfredX", docs_url=None, redoc_url=None)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/", response_class=HTMLResponse)
    async def mobile_ui():
        """Serve the mobile control panel."""
        try:
            with open(MOBILE_UI_PATH, "r", encoding="utf-8") as f:
                return HTMLResponse(f.read())
        except FileNotFoundError:
            return HTMLResponse(
                "<body style='background:#000;color:#c9a227;font-family:monospace;padding:40px'>"
                "<h2>⚠ Mobile UI not found</h2>"
                "<p>Expected: <code>data/mobile_ui.html</code></p>"
                "</body>"
            )

    @app.get("/status")
    async def status():
        """Health check — mobile app polls this to verify connectivity."""
        return JSONResponse({"status": "online", "system": "AlfredX", "version": "2.1"})

    @app.websocket("/ws")
    async def ws_endpoint(ws: WebSocket):
        await ws.accept()
        # Welcome handshake
        await ws.send_json({
            "type": "connected",
            "text": "Connected to AlfredX, Master. All systems online."
        })
        try:
            while True:
                data = await ws.receive_json()
                text = (data.get("text") or "").strip()
                if not text:
                    continue

                # Run the command in a thread (blocking call to AI/command handler)
                reply = await asyncio.get_running_loop().run_in_executor(
                    None, on_command, text
                )

                # Reply only to this client
                await ws.send_json({"type": "reply", "text": reply})

        except WebSocketDisconnect:
            pass
        except Exception as e:
            print(f"[Server] WS error: {e}")

    return app


def start_embedded_server(on_command, host="0.0.0.0", port=8000):
    """Start embedded server in a background daemon thread."""
    app = build_app(on_command)

    def _run():
        uvicorn.run(app, host=host, port=port, log_level="warning")

    t = threading.Thread(target=_run, daemon=True)
    t.start()
    print(f"[Server] ✓ Mobile UI → http://<your-PC-IP>:{port}")
    return t
