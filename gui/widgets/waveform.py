"""
AlfredX: Waveform Visualizer
Animated frequency bars for voice activity display.
"""
import random
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPainter, QColor, QLinearGradient


class WaveformVisualizer(QWidget):
    def __init__(self, bar_count=24, parent=None):
        super().__init__(parent)
        self.bar_count = bar_count
        self._bars = [0.0] * bar_count
        self._targets = [0.0] * bar_count
        self._active = False
        self._color = QColor(0, 212, 255)
        self.setFixedHeight(60)
        self.setMinimumWidth(100)

        self._timer = QTimer()
        self._timer.timeout.connect(self._tick)
        self._timer.start(50)

    def set_active(self, active):
        self._active = active
        if not active:
            self._targets = [0.0] * self.bar_count

    def set_color(self, color):
        self._color = color

    def _tick(self):
        if self._active:
            for i in range(self.bar_count):
                center = self.bar_count / 2
                dist = abs(i - center) / center
                max_h = 1.0 - dist * 0.5
                self._targets[i] = random.uniform(0.1, max_h)

        # Smooth towards targets
        for i in range(self.bar_count):
            diff = self._targets[i] - self._bars[i]
            self._bars[i] += diff * 0.3

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()
        bar_w = max(2, (w - (self.bar_count - 1) * 2) // self.bar_count)
        gap = 2

        r, g, b = self._color.red(), self._color.green(), self._color.blue()

        for i in range(self.bar_count):
            bar_h = max(2, int(self._bars[i] * h * 0.9))
            x = i * (bar_w + gap)
            y = (h - bar_h) // 2

            grad = QLinearGradient(x, y, x, y + bar_h)
            grad.setColorAt(0.0, QColor(r, g, b, 200))
            grad.setColorAt(0.5, QColor(r, g, b, 140))
            grad.setColorAt(1.0, QColor(r, g, b, 80))

            painter.setBrush(grad)
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(x, y, bar_w, bar_h, 2, 2)

        painter.end()
