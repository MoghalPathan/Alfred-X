"""
AlfredX v2.1 — The Waynecore Assistant
Pure voice assistant. Moon background. Always listening.
"""

# ═══════════════════════════════════════════════════════
# STEP 1 — sys/os MUST be first
# ═══════════════════════════════════════════════════════
import sys
import os

# ═══════════════════════════════════════════════════════
# STEP 2 — Setup wizard check (before ANY other imports)
#           This ensures .env exists before config.py loads
# ═══════════════════════════════════════════════════════
from setup_wizard import env_exists, run_wizard, open_settings
if not env_exists():
    run_wizard()

# Reload .env into os.environ RIGHT NOW so config.py gets real values
from dotenv import load_dotenv

def _get_env_path():
    if getattr(sys, "frozen", False):
        app_data = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "AlfredX")
        os.makedirs(app_data, exist_ok=True)
        return os.path.join(app_data, ".env")
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")

load_dotenv(dotenv_path=_get_env_path(), override=True)

# ═══════════════════════════════════════════════════════
# STEP 3 — Qt environment settings
# ═══════════════════════════════════════════════════════
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
os.environ.setdefault("QT_SCALE_FACTOR", "1")

# ═══════════════════════════════════════════════════════
# STEP 4 — All other imports
# ═══════════════════════════════════════════════════════
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QStackedWidget, QDesktopWidget
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from gui.login_screen import LoginScreen
from gui.main_window import MainWindow
from gui.styles import MAIN_STYLESHEET
from config import AI_NAME, AI_TITLE


# ═══════════════════════════════════════════════════════
# MAIN APP CLASS
# ═══════════════════════════════════════════════════════
class AlfredXApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{AI_NAME} -- {AI_TITLE}")

        screen = QDesktopWidget().availableGeometry()
        width = min(1280, int(screen.width() * 0.85))
        height = min(800, int(screen.height() * 0.85))
        self.setMinimumSize(900, 600)
        self.resize(width, height)
        x = (screen.width() - width) // 2
        y = (screen.height() - height) // 2
        self.move(x, y)

        self.setStyleSheet(MAIN_STYLESHEET)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.login_screen = LoginScreen()
        self.login_screen.activated.connect(self._on_activated)
        self.stack.addWidget(self.login_screen)

        self.main_window = None
        self.stack.setCurrentWidget(self.login_screen)
        # NO menubar — settings are inside the app's ⚙ button

    def _on_activated(self):
        if self.main_window is None:
            self.main_window = MainWindow()
            self.stack.addWidget(self.main_window)

        self.stack.setCurrentWidget(self.main_window)
        self.menuBar().setVisible(True)   # ← show menu after login
        self.main_window.welcome_on_login()

    def _show_about(self):
        from PyQt5.QtWidgets import QMessageBox
        msg = QMessageBox(self)
        msg.setWindowTitle("About AlfredX")
        msg.setText(
            f"<b>AlfredX — The Waynecore Assistant</b><br>"
            f"Version 2.1.0<br><br>"
            f"<i>\"I shall attend to it, Master.\"</i><br><br>"
            f"Config: {_get_env_path()}"
        )
        msg.setStyleSheet("background:#0d1117; color:#e0e6ed;")
        msg.exec_()

    def closeEvent(self, event):
        """Fully quit the app when window is closed."""
        if self.main_window and hasattr(self.main_window, 'cleanup'):
            self.main_window.cleanup()
        event.accept()


# ═══════════════════════════════════════════════════════
# MAIN ENTRY POINT
# ═══════════════════════════════════════════════════════
def main():
    print("=" * 56)
    print(f"  {AI_NAME}: {AI_TITLE} v2.1")
    print('  "I shall attend to it, Master."')
    print("=" * 56)

    if not os.environ.get("GROQ_API_KEY"):
        print("\n  GROQ_API_KEY not set!")
        print("  Get free: https://console.groq.com")
        print("  Use Settings > Update API Keys to configure.\n")

    app = QApplication(sys.argv)
    app.setApplicationName(AI_NAME)
    app.setStyle("Fusion")
    app.setFont(QFont("Segoe UI", 10))
    app.setQuitOnLastWindowClosed(True)

    # Create window FIRST
    window = AlfredXApp()

    # ── Start embedded server AFTER window exists ────────────
    # (window must exist before on_phone_command can reference it)
    try:
        from core.embedded_server import start_embedded_server

        def on_phone_command(text: str) -> str:
            if window.main_window is None:
                return "AlfredX is not ready yet, Master."
            mw = window.main_window
            mw.add_message("MASTER WAYNE", f"\U0001f4f1 {text}", is_alfred=False)
            if mw._cmd_handler:
                try:
                    handled, response = mw._cmd_handler.process(text)
                    if handled:
                        mw.add_message("ALFRED", response, is_alfred=True, model_tag="MOBILE")
                        if mw._tts: mw._tts.speak(response)
                        return response
                except Exception as e:
                    print(f"[Server] Cmd error: {e}")
            reply = mw._ai.chat(text) if mw._ai else "AI engine not ready, Master."
            mw.add_message("ALFRED", reply, is_alfred=True, model_tag="MOBILE")
            if mw._tts: mw._tts.speak(reply)
            return reply

        start_embedded_server(on_phone_command, host="0.0.0.0", port=8000)
        print("  Embedded server started on port 8000.")
    except Exception as e:
        print(f"  Embedded server not started: {e}")

    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
