"""
AlfredX: AI Orb Widget
Animated orb showing AI state: IDLE (blue pulse), LISTENING (red glow),
THINKING (orange spin), SPEAKING (green pulse).
"""
import math
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPainter, QRadialGradient, QColor, QPen


class AIOrb(QWidget):
    IDLE = 0
    LISTENING = 1
    THINKING = 2
    SPEAKING = 3

    STATE_COLORS = {
        IDLE: (0, 212, 255),       # Cyan
        LISTENING: (255, 51, 51),   # Red
        THINKING: (255, 170, 0),    # Orange
        SPEAKING: (0, 255, 136),    # Green
    }

    def __init__(self, size=180, parent=None):
        super().__init__(parent)
        self._size = size
        self._state = self.IDLE
        self._phase = 0.0
        self.setFixedSize(size, size)

        self._timer = QTimer()
        self._timer.timeout.connect(self._tick)
        self._timer.start(33)  # ~30fps

    def set_state(self, state):
        self._state = state

    def _tick(self):
        self._phase += 0.05
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        cx, cy = self._size // 2, self._size // 2
        r, g, b = self.STATE_COLORS.get(self._state, (0, 212, 255))

        # Pulse factor
        pulse = 0.7 + 0.3 * math.sin(self._phase * 2)
        if self._state == self.THINKING:
            pulse = 0.6 + 0.4 * abs(math.sin(self._phase * 3))

        base_radius = int(self._size * 0.32 * pulse)

        # Outer glow
        glow_radius = int(base_radius * 1.8)
        grad = QRadialGradient(cx, cy, glow_radius)
        grad.setColorAt(0.0, QColor(r, g, b, 60))
        grad.setColorAt(0.5, QColor(r, g, b, 20))
        grad.setColorAt(1.0, QColor(r, g, b, 0))
        painter.setBrush(grad)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(cx - glow_radius, cy - glow_radius, glow_radius * 2, glow_radius * 2)

        # Core orb
        grad2 = QRadialGradient(cx - base_radius * 0.3, cy - base_radius * 0.3, base_radius)
        grad2.setColorAt(0.0, QColor(min(255, r + 80), min(255, g + 80), min(255, b + 80), 220))
        grad2.setColorAt(0.5, QColor(r, g, b, 180))
        grad2.setColorAt(1.0, QColor(r // 2, g // 2, b // 2, 120))
        painter.setBrush(grad2)
        painter.setPen(QPen(QColor(r, g, b, 100), 1))
        painter.drawEllipse(cx - base_radius, cy - base_radius, base_radius * 2, base_radius * 2)

        # Inner highlight
        highlight_r = int(base_radius * 0.4)
        grad3 = QRadialGradient(cx - base_radius * 0.2, cy - base_radius * 0.3, highlight_r)
        grad3.setColorAt(0.0, QColor(255, 255, 255, 80))
        grad3.setColorAt(1.0, QColor(255, 255, 255, 0))
        painter.setBrush(grad3)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(
            int(cx - base_radius * 0.2 - highlight_r),
            int(cy - base_radius * 0.3 - highlight_r),
            highlight_r * 2, highlight_r * 2
        )

        # Ring for THINKING state (spinning dots)
        if self._state == self.THINKING:
            ring_r = int(base_radius * 1.4)
            for i in range(8):
                angle = self._phase * 4 + i * (math.pi / 4)
                dx = cx + int(ring_r * math.cos(angle))
                dy = cy + int(ring_r * math.sin(angle))
                alpha = int(255 * (1 - i / 8))
                painter.setBrush(QColor(r, g, b, alpha))
                dot_size = 4 - i * 0.3
                painter.drawEllipse(dx - int(dot_size), dy - int(dot_size),
                                    int(dot_size * 2), int(dot_size * 2))

        painter.end()
