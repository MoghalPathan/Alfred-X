"""
AlfredX — Global Hotkey: Summon Alfred from Anywhere (4pts)
===========================================================
Drop into core/ folder.
Requires: pip install keyboard
"""

import keyboard
from PyQt5.QtCore import QObject, pyqtSignal


class GlobalHotkey(QObject):
    """Listens for a global hotkey and emits a signal to summon the window."""
    
    summoned = pyqtSignal()

    def __init__(self, hotkey="ctrl+shift+a", parent=None):
        super().__init__(parent)
        self.hotkey = hotkey
        self._registered = False

    def start(self):
        """Register the global hotkey."""
        if not self._registered:
            keyboard.add_hotkey(self.hotkey, self._on_hotkey)
            self._registered = True

    def stop(self):
        """Unregister the global hotkey."""
        if self._registered:
            keyboard.remove_hotkey(self.hotkey)
            self._registered = False

    def _on_hotkey(self):
        """Called from keyboard listener thread — emit Qt signal."""
        self.summoned.emit()

    def change_hotkey(self, new_hotkey):
        """Change the hotkey at runtime."""
        was_active = self._registered
        if was_active:
            self.stop()
        self.hotkey = new_hotkey
        if was_active:
            self.start()
