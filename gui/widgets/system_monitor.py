"""
AlfredX: System Monitor Widget
Live display of CPU, RAM, and disk usage.
"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QFont

try:
    import psutil
    PSUTIL_OK = True
except ImportError:
    PSUTIL_OK = False


class SystemMonitor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        title = QLabel("SYSTEM MONITOR")
        title.setFont(QFont("Consolas", 8))
        title.setStyleSheet("color: rgba(0, 212, 255, 0.5); letter-spacing: 2px;")
        layout.addWidget(title)

        self.bars = {}
        for name, color in [("CPU", "#00d4ff"), ("RAM", "#00ffcc"), ("DISK", "#ffd700")]:
            lbl = QLabel(f"{name}: --")
            lbl.setFont(QFont("Consolas", 9))
            lbl.setStyleSheet(f"color: {color};")

            bar = QProgressBar()
            bar.setFixedHeight(6)
            bar.setTextVisible(False)
            bar.setStyleSheet(f"""
                QProgressBar {{
                    background-color: rgba(255,255,255,0.05);
                    border: none;
                    border-radius: 3px;
                }}
                QProgressBar::chunk {{
                    background-color: {color};
                    border-radius: 3px;
                }}
            """)

            layout.addWidget(lbl)
            layout.addWidget(bar)
            self.bars[name] = (lbl, bar)

        # Update timer
        self._timer = QTimer()
        self._timer.timeout.connect(self._update)
        self._timer.start(3000)
        self._update()

    def _update(self):
        if not PSUTIL_OK:
            return

        try:
            cpu = psutil.cpu_percent(interval=0)
            ram = psutil.virtual_memory().percent
            disk = psutil.disk_usage('/').percent

            self.bars["CPU"][0].setText(f"CPU: {cpu:.0f}%")
            self.bars["CPU"][1].setValue(int(cpu))

            self.bars["RAM"][0].setText(f"RAM: {ram:.0f}%")
            self.bars["RAM"][1].setValue(int(ram))

            self.bars["DISK"][0].setText(f"DISK: {disk:.0f}%")
            self.bars["DISK"][1].setValue(int(disk))
        except Exception:
            pass
