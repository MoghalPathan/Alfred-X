#!/usr/bin/env python3
"""
AlfredX: Waynecore Assistant System v2.0 - Cinematic Interface
Full PyQt5 implementation with all working features
"""

import sys
import os
import math
import random
import time
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QPushButton, QLineEdit, QScrollArea,
    QFrame, QSizePolicy, QTextEdit, QFileDialog, QMessageBox,
    QGraphicsDropShadowEffect, QSpacerItem, QDialog, QCheckBox
)
from PyQt5.QtCore import (
    Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtSignal,
    QPoint, QRect, QSize, QRectF, pyqtProperty, QObject
)
from PyQt5.QtGui import (
    QPainter, QColor, QFont, QFontDatabase, QPen, QBrush,
    QLinearGradient, QRadialGradient, QPainterPath, QPixmap,
    QConicalGradient, QPalette, QCursor, QPolygon, QPolygonF
)

# ============================================
# COLOR CONSTANTS (exact match)
# ============================================
GOLD = QColor(201, 162, 39)
GOLD_BRIGHT = QColor(255, 215, 0)
GOLD_DIM = QColor(139, 105, 20)
BLUE = QColor(0, 212, 255)
BLUE_DIM = QColor(0, 136, 170)
RED = QColor(255, 51, 51)
GREEN = QColor(0, 255, 136)
DARK = QColor(0, 0, 0)
DARK_BLUE = QColor(10, 10, 26)
PANEL_BG = QColor(5, 10, 25, 217)
WHITE = QColor(255, 255, 255)
WHITE_DIM = QColor(255, 255, 255, 100)
WHITE_FAINT = QColor(255, 255, 255, 40)

# ============================================
# STYLE CONSTANTS
# ============================================
FONT_DISPLAY = "Segoe UI"  # Fallback for Audiowide
FONT_MONO = "Consolas"     # Fallback for Share Tech Mono
FONT_BODY = "Segoe UI"     # Fallback for Rajdhani
FONT_HEADER = "Segoe UI"   # Fallback for Orbitron


def gold_rgba(alpha=255):
    return QColor(201, 162, 39, alpha)

def blue_rgba(alpha=255):
    return QColor(0, 212, 255, alpha)

def green_rgba(alpha=255):
    return QColor(0, 255, 136, alpha)

def red_rgba(alpha=255):
    return QColor(255, 51, 51, alpha)

def white_rgba(alpha=255):
    return QColor(255, 255, 255, alpha)


# ============================================
# GLOBAL STYLESHEET
# ============================================
MAIN_STYLESHEET = """
QMainWindow {
    background: #000000;
}
QWidget {
    background: transparent;
    color: #ffffff;
}
QScrollArea {
    border: none;
    background: transparent;
}
QScrollBar:vertical {
    background: rgba(0,0,0,0.3);
    width: 4px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: #c9a227;
    border-radius: 2px;
    min-height: 20px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none;
}
QLineEdit {
    background: rgba(10, 10, 30, 200);
    border: 2px solid rgba(201, 162, 39, 77);
    color: #ffffff;
    font-family: 'Segoe UI';
    font-size: 14px;
    padding: 12px 18px;
    selection-background-color: rgba(201, 162, 39, 100);
}
QLineEdit:focus {
    border-color: #c9a227;
}
QLineEdit::placeholder {
    color: rgba(255,255,255,77);
}
"""


# ============================================
# AI RESPONSE ENGINE
# ============================================
class AlfredAI:
    responses = {
        'greeting': [
            "Good evening, Master Wayne. All systems are operational and Wayne Tower security protocols are active. How may I assist you?",
            "Welcome back, sir. I've been maintaining all systems in your absence. What would you like me to attend to?",
            "At your service, Master Wayne. All diagnostics are green across the board."
        ],
        'diagnostic': [
            "Running full diagnostic sequence now, sir... All core systems nominal. CPU operating at optimal temperature. Memory allocation within parameters. Network uplink stable at 2.4 Gbps. No anomalies detected.",
            "Diagnostic complete, Master Wayne. All 847 subsystems reporting green. The Batcomputer mainframe is running at peak efficiency."
        ],
        'security': [
            "Wayne Tower perimeter is secure, sir. All 42 entry points monitored. Biometric scanners active on floors 1-85. I've flagged 2 minor access anomalies for your review.",
            "Security sweep complete. No unauthorized access detected in the last 24 hours. The vault systems are operating under Protocol Delta."
        ],
        'weather': [
            "Current conditions in Gotham: 42°F with overcast skies. Wind from the northwest at 12 mph. There's a 60% chance of rain after midnight.",
            "Gotham weather report: partly cloudy, 38°F. Visibility is good at 8 miles. No severe weather warnings in effect."
        ],
        'schedule': [
            "Tomorrow's itinerary: Wayne Enterprises board meeting at 10:00 AM, lunch with Lucius Fox at 12:30 PM, R&D lab review at 14:00, and the Gotham City charity gala at 19:00 hours.",
            "Your schedule is clear until 10:00 AM, sir. After that, you have back-to-back meetings until 16:00."
        ],
        'crime': [
            "Crime statistics for Gotham this week: major incidents down 12%. There were 3 reported break-ins in the Diamond District, and Arkham reports all inmates accounted for.",
            "Pulling up the latest data now... Overall crime is trending downward. However, there's been unusual activity near the docks — specifically Pier 14."
        ],
        'browser': [
            "Opening the secure Waynecore browser, sir. All traffic will be routed through our encrypted proxy network.",
            "Browser module activated. I've loaded your default workspace — Wayne Enterprises intranet, market feeds, and the GCPD dispatch scanner."
        ],
        'vscode': [
            "Launching VS Code with the Batcomputer development environment. Your last session has been restored.",
            "VS Code is ready, sir. I've pre-loaded the AlfredX codebase. There are 3 pending pull requests."
        ],
        'music': [
            "Music module activated, Master Wayne. Your 'Late Night Operations' playlist is queued. Volume set to 30%.",
            "Loading your music library, sir. Last played: Bach's Cello Suite No. 1. Shall I continue?"
        ],
        'files': [
            "File manager open, sir. Displaying the Wayne Industries secure vault. Total storage: 48.2 TB used of 100 TB.",
            "Accessing the file system. Your recent documents are ready."
        ],
        'vision': [
            "Vision module online. All surveillance feeds are operational — 342 cameras active across Gotham.",
            "Activating vision systems, sir. Satellite uplink established. Real-time thermal imaging available."
        ],
        'search': [
            "Search module ready, Master Wayne. I have access to all Wayne Industries databases, public records, and the Batcomputer intelligence archive.",
            "Search systems online. Cross-referencing capabilities across 47 databases. What are we looking for, sir?"
        ],
        'fallback': [
            "Understood, sir. I'm processing your request through the neural engine. Is there anything else you need?",
            "Very well, Master Wayne. I've logged that and will act accordingly.",
            "Noted, sir. I'll take care of it. The system is at your disposal.",
            "Processing your command now... Complete. How else may I be of service?",
            "Acknowledged, Master Wayne. I've updated the system logs accordingly."
        ]
    }

    @staticmethod
    def get_response(text):
        lower = text.lower()
        import re
        if re.search(r'hello|hi|hey|good\s*(morning|evening|night)|greet', lower):
            return random.choice(AlfredAI.responses['greeting'])
        if re.search(r'diagnos|scan|check\s*system|status|health', lower):
            return random.choice(AlfredAI.responses['diagnostic'])
        if re.search(r'secur|perimeter|camera|surveillance|guard|vault', lower):
            return random.choice(AlfredAI.responses['security'])
        if re.search(r'weather|temperature|rain|forecast', lower):
            return random.choice(AlfredAI.responses['weather'])
        if re.search(r'schedule|calendar|meeting|tomorrow|appointment', lower):
            return random.choice(AlfredAI.responses['schedule'])
        if re.search(r'crime|criminal|gotham|police|gcpd|arkham', lower):
            return random.choice(AlfredAI.responses['crime'])
        if re.search(r'browser|web|internet', lower):
            return random.choice(AlfredAI.responses['browser'])
        if re.search(r'code|vs\s*code|program|develop', lower):
            return random.choice(AlfredAI.responses['vscode'])
        if re.search(r'music|play|song|playlist', lower):
            return random.choice(AlfredAI.responses['music'])
        if re.search(r'file|folder|document|storage', lower):
            return random.choice(AlfredAI.responses['files'])
        if re.search(r'vision|camera|watch|monitor', lower):
            return random.choice(AlfredAI.responses['vision'])
        if re.search(r'search|find|look\s*up|query|locate', lower):
            return random.choice(AlfredAI.responses['search'])
        return random.choice(AlfredAI.responses['fallback'])


# ============================================
# ANIMATED BACKGROUND WIDGET
# ============================================
class AnimatedBackground(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.particles = []
        self.grid_offset = 0
        self.scan_opacity = 0.3

        for _ in range(30):
            self.particles.append({
                'x': random.random(),
                'y': random.random(),
                'speed': 0.001 + random.random() * 0.002,
                'size': 1 + random.random() * 2,
                'opacity': 0.3 + random.random() * 0.4
            })

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._animate)
        self.timer.start(50)

    def _animate(self):
        self.grid_offset = (self.grid_offset + 0.5) % 50
        for p in self.particles:
            p['y'] -= p['speed']
            if p['y'] < -0.05:
                p['y'] = 1.05
                p['x'] = random.random()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()

        # Deep space gradient
        grad = QRadialGradient(w * 0.2, 0, w * 0.5)
        grad.setColorAt(0, QColor(201, 162, 39, 25))
        grad.setColorAt(1, QColor(0, 0, 0, 0))
        painter.fillRect(0, 0, w, h, QBrush(grad))

        grad2 = QRadialGradient(w * 0.8, h, w * 0.5)
        grad2.setColorAt(0, QColor(0, 212, 255, 20))
        grad2.setColorAt(1, QColor(0, 0, 0, 0))
        painter.fillRect(0, 0, w, h, QBrush(grad2))

        # Particles
        for p in self.particles:
            px = int(p['x'] * w)
            py = int(p['y'] * h)
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(201, 162, 39, int(p['opacity'] * 255)))
            painter.drawEllipse(px, py, int(p['size']), int(p['size']))

        # Subtle grid lines
        painter.setPen(QPen(QColor(201, 162, 39, 8), 1))
        spacing = 50
        for x in range(0, w, spacing):
            painter.drawLine(x, 0, x, h)
        for y in range(0, h, spacing):
            painter.drawLine(0, y, w, y)

        # Scanlines
        painter.setPen(QPen(QColor(0, 0, 0, 25), 1))
        for y in range(0, h, 2):
            painter.drawLine(0, y, w, y)

        painter.end()


# ============================================
# CORNER DECORATIONS
# ============================================
class CornerDecor(QWidget):
    def __init__(self, corner='top-left', parent=None):
        super().__init__(parent)
        self.corner = corner
        self.setFixedSize(150, 150)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        pen = QPen(GOLD, 2)
        painter.setPen(pen)

        if self.corner == 'top-left':
            painter.drawLine(0, 0, 150, 0)
            painter.drawLine(0, 0, 0, 150)
            painter.fillRect(10, 10, 10, 10, GOLD)
        elif self.corner == 'top-right':
            painter.drawLine(0, 0, 150, 0)
            painter.drawLine(150, 0, 150, 150)
            painter.fillRect(130, 10, 10, 10, GOLD)
        elif self.corner == 'bottom-left':
            painter.drawLine(0, 150, 150, 150)
            painter.drawLine(0, 0, 0, 150)
            painter.fillRect(10, 130, 10, 10, GOLD)
        elif self.corner == 'bottom-right':
            painter.drawLine(0, 150, 150, 150)
            painter.drawLine(150, 0, 150, 150)
            painter.fillRect(130, 130, 10, 10, GOLD)
        painter.end()


# ============================================
# PANEL WIDGET (reusable styled container)
# ============================================
class Panel(QFrame):
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.title = title
        self.layout_main = QVBoxLayout(self)
        self.layout_main.setContentsMargins(0, 0, 0, 0)
        self.layout_main.setSpacing(0)

        if title:
            header = QWidget()
            header.setFixedHeight(42)
            header.setStyleSheet("""
                background: rgba(201, 162, 39, 13);
                border-bottom: 1px solid rgba(201, 162, 39, 26);
            """)
            hl = QHBoxLayout(header)
            hl.setContentsMargins(15, 0, 15, 0)

            lbl = QLabel(f"◆  {title}")
            lbl.setFont(QFont(FONT_HEADER, 9, QFont.Bold))
            lbl.setStyleSheet("color: #c9a227; letter-spacing: 3px;")
            hl.addWidget(lbl)
            hl.addStretch()

            self.header_widget = header
            self.layout_main.addWidget(header)

        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.layout_main.addWidget(self.content_widget)

    def paintEvent(self, event):
        painter = QPainter(self)
        w, h = self.width(), self.height()

        # Panel background
        painter.fillRect(0, 0, w, h, PANEL_BG)

        # Border
        painter.setPen(QPen(gold_rgba(51), 1))
        painter.drawRect(0, 0, w - 1, h - 1)

        # Top glow line
        grad = QLinearGradient(0, 0, w, 0)
        grad.setColorAt(0, QColor(201, 162, 39, 0))
        grad.setColorAt(0.5, QColor(201, 162, 39, 200))
        grad.setColorAt(1, QColor(201, 162, 39, 0))
        painter.setPen(QPen(QBrush(grad), 1))
        painter.drawLine(0, 0, w, 0)

        painter.end()


# ============================================
# MODULE WIDGET (right panel style)
# ============================================
class Module(Panel):
    def __init__(self, title="", status_text="", parent=None):
        super().__init__(title, parent)
        if status_text and hasattr(self, 'header_widget'):
            status = QLabel(status_text)
            status.setFont(QFont(FONT_MONO, 8))
            status.setStyleSheet("""
                color: #00ff88;
                background: rgba(0, 255, 136, 51);
                border: 1px solid rgba(0, 255, 136, 77);
                padding: 2px 8px;
            """)
            self.header_widget.layout().addWidget(status)


# ============================================
# HEX AVATAR
# ============================================
class HexAvatar(QWidget):
    def __init__(self, letter='A', color=GOLD, size=50, parent=None):
        super().__init__(parent)
        self.letter = letter
        self.color = color
        self.setFixedSize(size, size)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        cx, cy = w / 2, h / 2
        r = min(w, h) / 2 - 2

        # Hexagon path
        path = QPainterPath()
        for i in range(6):
            angle = math.radians(60 * i - 90)
            x = cx + r * math.cos(angle)
            y = cy + r * math.sin(angle)
            if i == 0:
                path.moveTo(x, y)
            else:
                path.lineTo(x, y)
        path.closeSubpath()

        # Fill
        grad = QLinearGradient(0, 0, w, h)
        grad.setColorAt(0, QColor(self.color.red(), self.color.green(), self.color.blue(), 77))
        grad.setColorAt(1, QColor(self.color.red(), self.color.green(), self.color.blue(), 25))
        painter.fillPath(path, QBrush(grad))

        # Border
        painter.setPen(QPen(self.color, 1))
        painter.drawPath(path)

        # Letter
        painter.setPen(self.color)
        painter.setFont(QFont(FONT_DISPLAY, 16, QFont.Bold))
        painter.drawText(QRectF(0, 0, w, h), Qt.AlignCenter, self.letter)
        painter.end()


# ============================================
# AI CORE WIDGET (animated hex + orbits)
# ============================================
class AICoreWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(240, 300)
        self.angle1 = 0
        self.angle2 = 0
        self.angle3 = 0
        self.pulse = 0
        self.data_offsets = [0, 10, 20, 30]

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._animate)
        self.timer.start(50)

    def _animate(self):
        self.angle1 += 2
        self.angle2 -= 1.5
        self.angle3 += 0.8
        self.pulse = (self.pulse + 3) % 360
        for i in range(len(self.data_offsets)):
            self.data_offsets[i] = (self.data_offsets[i] + 2) % 80
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        cx, cy = w / 2, 130

        # Data streams
        stream_positions = [0.2, 0.4, 0.6, 0.8]
        for i, sx in enumerate(stream_positions):
            x = int(sx * w)
            off = self.data_offsets[i]
            grad = QLinearGradient(x, cy - 80 + off, x, cy - 40 + off)
            grad.setColorAt(0, gold_rgba(0))
            grad.setColorAt(0.5, gold_rgba(200))
            grad.setColorAt(1, gold_rgba(0))
            painter.setPen(QPen(QBrush(grad), 2))
            painter.drawLine(x, int(cy - 80 + off), x, int(cy - 40 + off))

        # Orbit ring 3 (dashed)
        painter.setPen(QPen(gold_rgba(51), 1, Qt.DashLine))
        painter.save()
        painter.translate(cx, cy)
        painter.rotate(self.angle3)
        painter.drawEllipse(-100, -100, 200, 200)
        painter.restore()

        # Orbit ring 2
        painter.setPen(QPen(blue_rgba(77), 1))
        painter.save()
        painter.translate(cx, cy)
        painter.rotate(self.angle2)
        painter.drawEllipse(-90, -90, 180, 180)
        # Orbit dot
        painter.setPen(Qt.NoPen)
        painter.setBrush(BLUE)
        painter.drawEllipse(86, -4, 8, 8)
        painter.restore()

        # Orbit ring 1
        painter.setPen(QPen(gold_rgba(102), 1))
        painter.save()
        painter.translate(cx, cy)
        painter.rotate(self.angle1)
        painter.drawEllipse(-80, -80, 160, 160)
        # Orbit dot
        painter.setPen(Qt.NoPen)
        painter.setBrush(GOLD)
        painter.drawEllipse(-4, -84, 8, 8)
        painter.restore()

        # Hex core
        pulse_scale = 1.0 + 0.03 * math.sin(math.radians(self.pulse))
        hex_r = 60 * pulse_scale
        path = QPainterPath()
        for i in range(6):
            angle = math.radians(60 * i - 90)
            x = cx + hex_r * math.cos(angle)
            y = cy + hex_r * math.sin(angle)
            if i == 0:
                path.moveTo(x, y)
            else:
                path.lineTo(x, y)
        path.closeSubpath()

        grad = QLinearGradient(cx - hex_r, cy - hex_r, cx + hex_r, cy + hex_r)
        grad.setColorAt(0, QColor(201, 162, 39, 77))
        grad.setColorAt(1, QColor(0, 212, 255, 25))
        painter.fillPath(path, QBrush(grad))

        # AI text
        painter.setPen(GOLD)
        font = QFont(FONT_DISPLAY, 24, QFont.Bold)
        painter.setFont(font)
        painter.drawText(QRectF(cx - 40, cy - 20, 80, 40), Qt.AlignCenter, "AI")

        # ALFRED text
        painter.setPen(WHITE)
        font2 = QFont(FONT_DISPLAY, 18, QFont.Bold)
        painter.setFont(font2)
        painter.drawText(QRectF(0, cy + 110, w, 30), Qt.AlignCenter, "ALFRED")

        # Version
        painter.setPen(BLUE)
        font3 = QFont(FONT_MONO, 9)
        painter.setFont(font3)
        painter.drawText(QRectF(0, cy + 140, w, 20), Qt.AlignCenter, "NEURAL ENGINE v3.2.1")

        painter.end()


# ============================================
# STAT BAR WIDGET
# ============================================
class StatBar(QWidget):
    def __init__(self, label, icon, value=50, color=GREEN, parent=None):
        super().__init__(parent)
        self.label_text = label
        self.icon_text = icon
        self.value = value
        self.color = color
        self.setFixedHeight(50)

    def set_value(self, v):
        self.value = v
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()

        # Icon box
        painter.setPen(QPen(gold_rgba(77), 1))
        painter.setBrush(QBrush(gold_rgba(25)))
        painter.drawRect(0, 8, 32, 32)
        painter.setPen(WHITE)
        painter.setFont(QFont(FONT_BODY, 12))
        painter.drawText(QRectF(0, 8, 32, 32), Qt.AlignCenter, self.icon_text)

        # Label
        x_off = 47
        painter.setPen(white_rgba(153))
        painter.setFont(QFont(FONT_MONO, 9))
        painter.drawText(x_off, 20, self.label_text)

        # Value
        painter.setPen(GOLD)
        val_text = f"{self.value}%"
        fm = painter.fontMetrics()
        painter.drawText(w - fm.horizontalAdvance(val_text) - 5, 20, val_text)

        # Bar background
        bar_y = 30
        bar_h = 4
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(255, 255, 255, 25))
        painter.drawRect(x_off, bar_y, w - x_off - 5, bar_h)

        # Bar fill
        fill_w = int((w - x_off - 5) * self.value / 100)
        grad = QLinearGradient(x_off, 0, x_off + fill_w, 0)
        grad.setColorAt(0, self.color)
        c2 = QColor(self.color)
        c2.setAlpha(180)
        grad.setColorAt(1, c2)
        painter.setBrush(QBrush(grad))
        painter.drawRect(x_off, bar_y, fill_w, bar_h)

        painter.end()


# ============================================
# ARC GAUGE WIDGET
# ============================================
class ArcGauge(QWidget):
    def __init__(self, label, value=50, color=GREEN, parent=None):
        super().__init__(parent)
        self.label_text = label
        self.value = value
        self.color = color
        self.setFixedSize(80, 95)

    def set_value(self, v):
        self.value = v
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        cx, cy = w / 2, 38
        r = 28

        # Background circle
        painter.setPen(QPen(QColor(255, 255, 255, 25), 4))
        painter.drawArc(int(cx - r), int(cy - r), int(r * 2), int(r * 2), 0, 360 * 16)

        # Value arc
        painter.setPen(QPen(self.color, 4, cap=Qt.RoundCap))
        span = int(-self.value * 360 / 100 * 16)
        painter.drawArc(int(cx - r), int(cy - r), int(r * 2), int(r * 2), 90 * 16, span)

        # Value text
        painter.setPen(self.color)
        painter.setFont(QFont(FONT_MONO, 11, QFont.Bold))
        painter.drawText(QRectF(0, cy - 10, w, 20), Qt.AlignCenter, f"{self.value}%")

        # Label
        painter.setPen(white_rgba(153))
        painter.setFont(QFont(FONT_MONO, 8))
        painter.drawText(QRectF(0, 75, w, 15), Qt.AlignCenter, self.label_text)

        painter.end()


# ============================================
# VOICE VISUALIZER WIDGET
# ============================================
class VoiceVisualizer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(100)
        self.bar_count = 25
        self.bar_heights = [10] * self.bar_count
        self.active = True
        self.status_text = "● VOICE RECOGNITION ACTIVE"

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._animate)
        self.timer.start(80)

    def _animate(self):
        if self.active:
            for i in range(self.bar_count):
                center = self.bar_count / 2
                dist = abs(i - center) / center
                max_h = 45 * (1 - dist * 0.5)
                self.bar_heights[i] = random.randint(8, int(max_h))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()

        # Background
        painter.fillRect(0, 0, w, h, QColor(0, 0, 0, 128))

        # Top/bottom borders
        painter.setPen(QPen(gold_rgba(51), 1))
        painter.drawLine(0, 0, w, 0)
        painter.drawLine(0, h - 1, w, h - 1)

        # Bars
        bar_w = 4
        total_w = self.bar_count * (bar_w + 3)
        start_x = (w - total_w) / 2
        cy = 40

        for i in range(self.bar_count):
            bh = self.bar_heights[i]
            x = int(start_x + i * (bar_w + 3))
            y = int(cy - bh / 2)

            grad = QLinearGradient(x, y, x, y + bh)
            grad.setColorAt(0, GOLD_BRIGHT)
            grad.setColorAt(0.5, GOLD)
            grad.setColorAt(1, GOLD_DIM)
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(grad))
            painter.drawRoundedRect(x, y, bar_w, bh, 2, 2)

        # Status text
        painter.setPen(GOLD if "ACTIVE" in self.status_text else GREEN)
        painter.setFont(QFont(FONT_MONO, 9))
        painter.drawText(QRectF(0, 70, w, 20), Qt.AlignCenter, self.status_text)

        painter.end()


# ============================================
# MESSAGE BUBBLE
# ============================================
class MessageBubble(QWidget):
    def __init__(self, sender, text, timestamp, parent=None):
        super().__init__(parent)
        self.sender = sender  # 'alfred' or 'user'
        self.text = text
        self.timestamp = timestamp
        self.is_user = sender == 'user'

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(12)

        avatar = HexAvatar(
            'W' if self.is_user else 'A',
            BLUE if self.is_user else GOLD,
            44
        )

        # Content
        content = QWidget()
        cl = QVBoxLayout(content)
        cl.setContentsMargins(0, 0, 0, 0)
        cl.setSpacing(5)

        # Header
        header = QWidget()
        hl = QHBoxLayout(header)
        hl.setContentsMargins(0, 0, 0, 0)
        hl.setSpacing(10)

        name_lbl = QLabel("MASTER WAYNE" if self.is_user else "ALFRED")
        name_lbl.setFont(QFont(FONT_HEADER, 9, QFont.Bold))
        name_lbl.setStyleSheet(f"color: {'#00d4ff' if self.is_user else '#c9a227'}; letter-spacing: 2px;")

        time_lbl = QLabel(self.timestamp)
        time_lbl.setFont(QFont(FONT_MONO, 8))
        time_lbl.setStyleSheet("color: rgba(255,255,255,0.4);")

        hl.addWidget(name_lbl)
        hl.addWidget(time_lbl)
        hl.addStretch()

        # Bubble
        bubble = QLabel(self.text)
        bubble.setWordWrap(True)
        bubble.setFont(QFont(FONT_BODY, 11))
        bubble.setMinimumWidth(200)
        bubble.setMaximumWidth(500)

        if self.is_user:
            bubble.setStyleSheet("""
                QLabel {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 rgba(0, 212, 255, 25), stop:1 rgba(0, 212, 255, 13));
                    border: 1px solid rgba(0, 212, 255, 77);
                    border-right: 3px solid #00d4ff;
                    padding: 12px 16px;
                    color: #ffffff;
                }
            """)
        else:
            bubble.setStyleSheet("""
                QLabel {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 rgba(201, 162, 39, 25), stop:1 rgba(201, 162, 39, 13));
                    border: 1px solid rgba(201, 162, 39, 77);
                    border-left: 3px solid #c9a227;
                    padding: 12px 16px;
                    color: #ffffff;
                }
            """)

        cl.addWidget(header)
        cl.addWidget(bubble)
        content.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        if self.is_user:
            layout.addStretch()
            layout.addWidget(content)
            layout.addWidget(avatar)
        else:
            layout.addWidget(avatar)
            layout.addWidget(content)
            layout.addStretch()


# ============================================
# TYPING INDICATOR
# ============================================
class TypingIndicator(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(60)
        self.dot_phase = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._animate)
        self.timer.start(100)

    def _animate(self):
        self.dot_phase = (self.dot_phase + 1) % 30
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Avatar
        cx, cy = 35, 30
        r = 18
        path = QPainterPath()
        for i in range(6):
            angle = math.radians(60 * i - 90)
            x = cx + r * math.cos(angle)
            y = cy + r * math.sin(angle)
            if i == 0:
                path.moveTo(x, y)
            else:
                path.lineTo(x, y)
        path.closeSubpath()
        painter.fillPath(path, QBrush(gold_rgba(50)))
        painter.setPen(QPen(GOLD, 1))
        painter.drawPath(path)
        painter.setFont(QFont(FONT_DISPLAY, 13, QFont.Bold))
        painter.drawText(QRectF(cx - 15, cy - 10, 30, 20), Qt.AlignCenter, "A")

        # Dots
        for i in range(3):
            phase = (self.dot_phase - i * 3) % 15
            scale = 1.0 if 3 < phase < 8 else 0.6
            alpha = 255 if 3 < phase < 8 else 100
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(201, 162, 39, alpha))
            dot_size = int(8 * scale)
            painter.drawEllipse(70 + i * 16, 30 - dot_size // 2, dot_size, dot_size)

        painter.end()


# ============================================
# QUICK COMMAND BUTTON
# ============================================
class QuickCommandBtn(QPushButton):
    command_clicked = pyqtSignal(str)

    def __init__(self, icon, label, cmd_key, parent=None):
        super().__init__(parent)
        self.icon_text = icon
        self.label_text = label
        self.cmd_key = cmd_key
        self.setFixedSize(140, 70)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self._hovered = False
        self._active = False
        self.clicked.connect(lambda: self.command_clicked.emit(self.cmd_key))

    def enterEvent(self, event):
        self._hovered = True
        self.update()

    def leaveEvent(self, event):
        self._hovered = False
        self.update()

    def set_active(self, v):
        self._active = v
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()

        # Background
        bg_alpha = 64 if self._active else (38 if self._hovered else 13)
        painter.fillRect(0, 0, w, h, gold_rgba(bg_alpha))

        # Border
        border_color = GOLD_BRIGHT if self._active else (GOLD if self._hovered else gold_rgba(51))
        painter.setPen(QPen(border_color, 1))
        painter.drawRect(0, 0, w - 1, h - 1)

        # Icon
        painter.setPen(WHITE)
        painter.setFont(QFont(FONT_BODY, 20))
        painter.drawText(QRectF(0, 5, w, 35), Qt.AlignCenter, self.icon_text)

        # Label
        painter.setPen(white_rgba(204))
        painter.setFont(QFont(FONT_MONO, 9))
        painter.drawText(QRectF(0, 42, w, 20), Qt.AlignCenter, self.label_text)

        painter.end()


# ============================================
# LOG ITEM
# ============================================
class LogItem(QWidget):
    def __init__(self, action, log_type='success', timestamp=None, parent=None):
        super().__init__(parent)
        self.action = action
        self.log_type = log_type
        self.timestamp = timestamp or datetime.now().strftime("%H:%M:%S")
        self.setFixedHeight(45)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w = self.width()

        # Icon
        icons = {'success': '✓', 'pending': '⏳', 'error': '✗'}
        colors = {'success': GREEN, 'pending': GOLD, 'error': RED}
        color = colors.get(self.log_type, GREEN)

        painter.setPen(QPen(color, 1))
        painter.setBrush(QBrush(QColor(color.red(), color.green(), color.blue(), 25)))
        painter.drawRect(5, 8, 28, 28)

        painter.setFont(QFont(FONT_BODY, 10))
        painter.drawText(QRectF(5, 8, 28, 28), Qt.AlignCenter, icons.get(self.log_type, '✓'))

        # Action text
        painter.setPen(white_rgba(230))
        painter.setFont(QFont(FONT_BODY, 10))
        text = self.action if len(self.action) < 35 else self.action[:32] + "..."
        painter.drawText(43, 22, text)

        # Time
        painter.setPen(white_rgba(100))
        painter.setFont(QFont(FONT_MONO, 8))
        painter.drawText(43, 38, self.timestamp)

        # Bottom border
        painter.setPen(QPen(QColor(255, 255, 255, 13), 1))
        painter.drawLine(0, 44, w, 44)

        painter.end()


# ============================================
# HEADER BUTTON
# ============================================
class HeaderButton(QPushButton):
    def __init__(self, icon, tooltip="", parent=None):
        super().__init__(parent)
        self.icon_text = icon
        self.setFixedSize(45, 45)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setToolTip(tooltip)
        self._hovered = False

    def enterEvent(self, event):
        self._hovered = True
        self.update()

    def leaveEvent(self, event):
        self._hovered = False
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()

        bg = gold_rgba(77) if self._hovered else gold_rgba(25)
        painter.fillRect(0, 0, w, h, bg)
        painter.setPen(QPen(gold_rgba(77), 1))
        painter.drawRect(0, 0, w - 1, h - 1)

        painter.setPen(GOLD)
        painter.setFont(QFont(FONT_BODY, 14))
        painter.drawText(QRectF(0, 0, w, h), Qt.AlignCenter, self.icon_text)
        painter.end()


# ============================================
# BAT LOGO WIDGET
# ============================================
class BatLogo(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(80, 80)
        self.ring_angle1 = 0
        self.ring_angle2 = 0
        self.pulse = 0

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._animate)
        self.timer.start(50)

    def _animate(self):
        self.ring_angle1 += 1.5
        self.ring_angle2 -= 1.0
        self.pulse = (self.pulse + 2) % 360
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        cx, cy = w / 2, h / 2

        # Outer ring 2
        painter.save()
        painter.translate(cx, cy)
        painter.rotate(self.ring_angle2)
        painter.setPen(QPen(blue_rgba(77), 1))
        painter.drawEllipse(-38, -38, 76, 76)
        painter.restore()

        # Outer ring 1 (dashed)
        painter.save()
        painter.translate(cx, cy)
        painter.rotate(self.ring_angle1)
        painter.setPen(QPen(gold_rgba(77), 1, Qt.DashLine))
        painter.drawEllipse(-32, -32, 64, 64)
        painter.restore()

        # Bat symbol (simplified)
        pulse_s = 1.0 + 0.03 * math.sin(math.radians(self.pulse))
        painter.save()
        painter.translate(cx, cy)
        painter.scale(pulse_s, pulse_s)

        path = QPainterPath()
        # Simplified bat shape
        path.moveTo(0, -12)
        path.cubicTo(-5, -12, -10, -7, -12, -2)
        path.cubicTo(-15, -7, -25, -12, -30, -7)
        path.cubicTo(-25, -2, -27, 8, -30, 13)
        path.cubicTo(-27, 18, -15, 28, -5, 31)
        path.cubicTo(-2, 33, -1, 33, 0, 33)
        path.cubicTo(1, 33, 2, 33, 5, 31)
        path.cubicTo(15, 28, 27, 18, 30, 13)
        path.cubicTo(27, 8, 25, -2, 30, -7)
        path.cubicTo(25, -12, 15, -7, 12, -2)
        path.cubicTo(10, -7, 5, -12, 0, -12)
        path.closeSubpath()

        painter.setPen(Qt.NoPen)
        painter.setBrush(GOLD)
        painter.scale(0.65, 0.65)
        painter.translate(0, -5)
        painter.drawPath(path)

        painter.restore()
        painter.end()


# ============================================
# NOTIFICATION DIALOG
# ============================================
class NotificationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Notifications")
        self.setFixedSize(450, 350)
        self.setStyleSheet(f"""
            QDialog {{
                background: rgb(5, 10, 25);
                border: 1px solid rgba(201, 162, 39, 100);
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)

        title = QLabel("⚡ NOTIFICATIONS")
        title.setFont(QFont(FONT_HEADER, 12, QFont.Bold))
        title.setStyleSheet("color: #c9a227; letter-spacing: 3px;")
        layout.addWidget(title)

        notifs = [
            ("🔴", "ALERT:", "Unusual network activity detected on Port 443 — resolved.", "#ff3333"),
            ("🟡", "PENDING:", "Wayne Enterprises quarterly report due in 3 days.", "#c9a227"),
            ("🟢", "INFO:", "System backup completed successfully.", "#00ff88"),
            ("🟢", "INFO:", "All security protocols updated to latest version.", "#00ff88"),
        ]
        for emoji, tag, msg, color in notifs:
            lbl = QLabel(f"{emoji} <span style='color:{color};font-weight:bold'>{tag}</span> {msg}")
            lbl.setWordWrap(True)
            lbl.setFont(QFont(FONT_BODY, 11))
            lbl.setStyleSheet("color: rgba(255,255,255,200); padding: 8px 0;")
            layout.addWidget(lbl)

        layout.addStretch()

        btn = QPushButton("DISMISS")
        btn.setFont(QFont(FONT_HEADER, 10, QFont.Bold))
        btn.setStyleSheet("""
            QPushButton {
                background: rgba(201, 162, 39, 51);
                border: 1px solid #c9a227;
                color: #c9a227;
                padding: 10px 30px;
                letter-spacing: 2px;
            }
            QPushButton:hover {
                background: rgba(201, 162, 39, 102);
            }
        """)
        btn.setCursor(QCursor(Qt.PointingHandCursor))
        btn.clicked.connect(self.accept)
        layout.addWidget(btn, alignment=Qt.AlignCenter)


# ============================================
# SETTINGS DIALOG
# ============================================
class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setFixedSize(420, 380)
        self.setStyleSheet(f"""
            QDialog {{
                background: rgb(5, 10, 25);
                border: 1px solid rgba(201, 162, 39, 100);
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(5)

        title = QLabel("⚙️  SYSTEM SETTINGS")
        title.setFont(QFont(FONT_HEADER, 12, QFont.Bold))
        title.setStyleSheet("color: #c9a227; letter-spacing: 3px;")
        layout.addWidget(title)
        layout.addSpacing(15)

        settings = [
            "VOICE RECOGNITION",
            "PARTICLE EFFECTS",
            "SCANLINE OVERLAY",
            "AUTO-SCROLL CHAT",
            "DARK MODE",
        ]
        self.toggles = {}
        for s in settings:
            row = QWidget()
            rl = QHBoxLayout(row)
            rl.setContentsMargins(0, 8, 0, 8)
            lbl = QLabel(s)
            lbl.setFont(QFont(FONT_MONO, 10))
            lbl.setStyleSheet("color: rgba(255,255,255,180);")
            cb = QCheckBox()
            cb.setChecked(True)
            cb.setStyleSheet("""
                QCheckBox::indicator {
                    width: 36px; height: 18px;
                    border-radius: 9px;
                    background: rgba(0, 255, 136, 77);
                    border: 1px solid rgba(0, 255, 136, 120);
                }
                QCheckBox::indicator:unchecked {
                    background: rgba(255,255,255,25);
                    border: 1px solid rgba(255,255,255,50);
                }
            """)
            rl.addWidget(lbl)
            rl.addStretch()
            rl.addWidget(cb)
            self.toggles[s] = cb

            sep = QFrame()
            sep.setFixedHeight(1)
            sep.setStyleSheet("background: rgba(255,255,255,13);")

            layout.addWidget(row)
            layout.addWidget(sep)

        layout.addStretch()

        btn = QPushButton("CLOSE")
        btn.setFont(QFont(FONT_HEADER, 10, QFont.Bold))
        btn.setStyleSheet("""
            QPushButton {
                background: rgba(201, 162, 39, 51);
                border: 1px solid #c9a227;
                color: #c9a227;
                padding: 10px 30px;
                letter-spacing: 2px;
            }
            QPushButton:hover {
                background: rgba(201, 162, 39, 102);
            }
        """)
        btn.setCursor(QCursor(Qt.PointingHandCursor))
        btn.clicked.connect(self.accept)
        layout.addWidget(btn, alignment=Qt.AlignCenter)


# ============================================
# MAIN WINDOW
# ============================================
class AlfredXWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AlfredX: Waynecore Assistant - Cinematic Interface")
        self.setMinimumSize(1280, 800)
        self.showMaximized()

        self.command_count = 0
        self.success_count = 0
        self.start_time = time.time()
        self.is_processing = False
        self.mic_active = False

        # Central widget with background
        central = QWidget()
        self.setCentralWidget(central)
        central_layout = QVBoxLayout(central)
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_layout.setSpacing(0)

        # Background
        self.bg = AnimatedBackground(central)
        self.bg.lower()

        # Scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        central_layout.addWidget(scroll)

        # Main content
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        scroll.setWidget(main_widget)

        # ===== HEADER =====
        self._build_header(main_layout)

        # ===== BODY (3 columns) =====
        body = QWidget()
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(15)

        # Left panel
        left = self._build_left_panel()
        body_layout.addWidget(left)

        # Center panel
        center = self._build_center_panel()
        body_layout.addWidget(center, 1)

        # Right panel
        right = self._build_right_panel()
        body_layout.addWidget(right)

        main_layout.addWidget(body, 1)

        # ===== FOOTER =====
        self._build_footer(main_layout)

        # ===== TIMERS =====
        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self._update_clock)
        self.clock_timer.start(1000)
        self._update_clock()

        self.stats_timer = QTimer(self)
        self.stats_timer.timeout.connect(self._update_stats)
        self.stats_timer.start(2000)

        self.uptime_timer = QTimer(self)
        self.uptime_timer.timeout.connect(self._update_uptime)
        self.uptime_timer.start(1000)

        # Initial greeting
        QTimer.singleShot(800, self._initial_greeting)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'bg'):
            self.bg.setGeometry(0, 0, self.width(), self.height())

    # =========== HEADER ===========
    def _build_header(self, parent_layout):
        header = QWidget()
        header.setFixedHeight(90)
        header.setStyleSheet("""
            background: rgba(5, 10, 25, 217);
            border: 1px solid rgba(201, 162, 39, 77);
        """)
        hl = QHBoxLayout(header)
        hl.setContentsMargins(20, 10, 20, 10)
        hl.setSpacing(15)

        # Logo
        self.bat_logo = BatLogo()
        hl.addWidget(self.bat_logo)

        # Title
        title_w = QWidget()
        tl = QVBoxLayout(title_w)
        tl.setContentsMargins(0, 0, 0, 0)
        tl.setSpacing(3)

        main_title = QLabel("ALFREDX")
        main_title.setFont(QFont(FONT_DISPLAY, 26, QFont.Bold))
        main_title.setStyleSheet("color: #c9a227; letter-spacing: 8px;")
        tl.addWidget(main_title)

        subtitle = QLabel(">>  WAYNECORE ASSISTANT SYSTEM v2.0")
        subtitle.setFont(QFont(FONT_MONO, 9))
        subtitle.setStyleSheet("color: #00d4ff; letter-spacing: 4px;")
        tl.addWidget(subtitle)

        hl.addWidget(title_w)
        hl.addStretch()

        # Status indicator
        status_w = QWidget()
        status_w.setStyleSheet("""
            background: rgba(0, 255, 136, 25);
            border: 1px solid rgba(0, 255, 136, 77);
            padding: 5px 15px;
        """)
        sl = QHBoxLayout(status_w)
        sl.setContentsMargins(15, 5, 15, 5)
        sl.setSpacing(8)

        self.status_dot = QLabel("●")
        self.status_dot.setFont(QFont(FONT_BODY, 8))
        self.status_dot.setStyleSheet("color: #00ff88;")
        sl.addWidget(self.status_dot)

        self.status_label = QLabel("SYSTEM ONLINE")
        self.status_label.setFont(QFont(FONT_MONO, 10))
        self.status_label.setStyleSheet("color: #00ff88; letter-spacing: 2px;")
        sl.addWidget(self.status_label)

        hl.addWidget(status_w)
        hl.addSpacing(20)

        # Clock
        clock_w = QWidget()
        clock_l = QVBoxLayout(clock_w)
        clock_l.setContentsMargins(0, 0, 0, 0)
        clock_l.setSpacing(0)
        clock_l.setAlignment(Qt.AlignRight)

        self.time_label = QLabel("00:00:00")
        self.time_label.setFont(QFont(FONT_MONO, 20, QFont.Bold))
        self.time_label.setStyleSheet("color: #c9a227;")
        self.time_label.setAlignment(Qt.AlignRight)
        clock_l.addWidget(self.time_label)

        self.date_label = QLabel("LOADING...")
        self.date_label.setFont(QFont(FONT_MONO, 9))
        self.date_label.setStyleSheet("color: rgba(201, 162, 39, 180);")
        self.date_label.setAlignment(Qt.AlignRight)
        clock_l.addWidget(self.date_label)

        hl.addWidget(clock_w)
        hl.addSpacing(20)

        # Header buttons
        btn_notif = HeaderButton("🔔", "Notifications")
        btn_notif.clicked.connect(self._show_notifications)
        hl.addWidget(btn_notif)

        btn_stats = HeaderButton("📊", "System Stats")
        btn_stats.clicked.connect(lambda: self._send_command_text("Run full system diagnostic"))
        hl.addWidget(btn_stats)

        btn_settings = HeaderButton("⚙️", "Settings")
        btn_settings.clicked.connect(self._show_settings)
        hl.addWidget(btn_settings)

        btn_power = HeaderButton("⏻", "Power")
        btn_power.clicked.connect(self._power_off)
        hl.addWidget(btn_power)

        parent_layout.addWidget(header)

    # =========== LEFT PANEL ===========
    def _build_left_panel(self):
        left = QWidget()
        left.setFixedWidth(320)
        ll = QVBoxLayout(left)
        ll.setContentsMargins(0, 0, 0, 0)
        ll.setSpacing(15)

        # AI Core
        core_panel = Panel("AI CORE STATUS")
        self.ai_core = AICoreWidget()
        core_panel.content_layout.addWidget(self.ai_core, alignment=Qt.AlignCenter)
        ll.addWidget(core_panel)

        # System Resources
        res_panel = Panel("SYSTEM RESOURCES")
        res_content = QWidget()
        rc_layout = QVBoxLayout(res_content)
        rc_layout.setContentsMargins(15, 15, 15, 15)
        rc_layout.setSpacing(8)

        self.cpu_bar = StatBar("CPU USAGE", "⚡", 45, GREEN)
        self.mem_bar = StatBar("MEMORY", "🧠", 62, BLUE)
        self.net_bar = StatBar("NETWORK", "📡", 78, GOLD)

        rc_layout.addWidget(self.cpu_bar)
        rc_layout.addWidget(self.mem_bar)
        rc_layout.addWidget(self.net_bar)

        res_panel.content_layout.addWidget(res_content)
        ll.addWidget(res_panel)
        ll.addStretch()

        return left

    # =========== CENTER PANEL ===========
    def _build_center_panel(self):
        center_panel = Panel("COMMAND INTERFACE")

        # Messages area
        self.messages_scroll = QScrollArea()
        self.messages_scroll.setWidgetResizable(True)
        self.messages_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.messages_scroll.setMinimumHeight(400)
        self.messages_scroll.setMaximumHeight(500)

        self.messages_widget = QWidget()
        self.messages_layout = QVBoxLayout(self.messages_widget)
        self.messages_layout.setContentsMargins(0, 0, 0, 0)
        self.messages_layout.setSpacing(5)
        self.messages_layout.addStretch()
        self.messages_scroll.setWidget(self.messages_widget)

        center_panel.content_layout.addWidget(self.messages_scroll)

        # Voice Visualizer
        self.voice_viz = VoiceVisualizer()
        center_panel.content_layout.addWidget(self.voice_viz)

        # Input area
        input_w = QWidget()
        input_w.setFixedHeight(70)
        il = QHBoxLayout(input_w)
        il.setContentsMargins(15, 10, 15, 10)
        il.setSpacing(10)

        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("Enter command or speak to Alfred...")
        self.command_input.setFont(QFont(FONT_BODY, 13))
        self.command_input.returnPressed.connect(self._send_command)
        il.addWidget(self.command_input)

        attach_btn = QPushButton("📎")
        attach_btn.setFixedSize(40, 40)
        attach_btn.setCursor(QCursor(Qt.PointingHandCursor))
        attach_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #c9a227, stop:1 #8b6914);
                border: none;
                font-size: 16px;
                color: white;
            }
            QPushButton:hover { background: #ffd700; }
        """)
        attach_btn.clicked.connect(self._attach_file)
        il.addWidget(attach_btn)

        self.mic_btn = QPushButton("🎤")
        self.mic_btn.setFixedSize(40, 40)
        self.mic_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.mic_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #ff3333, stop:1 #cc0000);
                border: none;
                font-size: 16px;
                color: white;
            }
            QPushButton:hover { background: #ff5555; }
        """)
        self.mic_btn.clicked.connect(self._toggle_mic)
        il.addWidget(self.mic_btn)

        send_btn = QPushButton("➤")
        send_btn.setFixedSize(55, 45)
        send_btn.setCursor(QCursor(Qt.PointingHandCursor))
        send_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #00d4ff, stop:1 #0088aa);
                border: none;
                font-size: 18px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover { background: #00eeff; }
        """)
        send_btn.clicked.connect(self._send_command)
        il.addWidget(send_btn)

        center_panel.content_layout.addWidget(input_w)

        return center_panel

    # =========== RIGHT PANEL ===========
    def _build_right_panel(self):
        right = QWidget()
        right.setFixedWidth(350)
        rl = QVBoxLayout(right)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.setSpacing(15)

        # Quick Commands
        cmd_module = Module("QUICK COMMANDS", "READY")
        grid_w = QWidget()
        grid_l = QGridLayout(grid_w)
        grid_l.setSpacing(8)
        grid_l.setContentsMargins(10, 10, 10, 10)

        commands = [
            ("🌐", "BROWSER", "browser"), ("💻", "VS CODE", "vscode"),
            ("🎵", "MUSIC", "music"), ("📁", "FILES", "files"),
            ("📷", "VISION", "vision"), ("🔍", "SEARCH", "search"),
        ]
        self.cmd_buttons = {}
        for i, (icon, label, key) in enumerate(commands):
            btn = QuickCommandBtn(icon, label, key)
            btn.command_clicked.connect(self._quick_command)
            grid_l.addWidget(btn, i // 2, i % 2)
            self.cmd_buttons[key] = btn

        cmd_module.content_layout.addWidget(grid_w)
        rl.addWidget(cmd_module)

        # Performance
        perf_module = Module("PERFORMANCE")
        arcs_w = QWidget()
        arcs_l = QHBoxLayout(arcs_w)
        arcs_l.setContentsMargins(10, 10, 10, 10)

        self.arc_cpu = ArcGauge("CPU", 45, GREEN)
        self.arc_ram = ArcGauge("RAM", 62, BLUE)
        self.arc_gpu = ArcGauge("GPU", 23, GOLD)

        arcs_l.addWidget(self.arc_cpu)
        arcs_l.addWidget(self.arc_ram)
        arcs_l.addWidget(self.arc_gpu)

        perf_module.content_layout.addWidget(arcs_w)
        rl.addWidget(perf_module)

        # Activity Log
        log_module = Module("ACTIVITY LOG")
        self.log_scroll = QScrollArea()
        self.log_scroll.setWidgetResizable(True)
        self.log_scroll.setMaximumHeight(200)

        self.log_widget = QWidget()
        self.log_layout = QVBoxLayout(self.log_widget)
        self.log_layout.setContentsMargins(0, 0, 0, 0)
        self.log_layout.setSpacing(0)
        self.log_layout.addStretch()
        self.log_scroll.setWidget(self.log_widget)

        log_module.content_layout.addWidget(self.log_scroll)
        rl.addWidget(log_module)
        rl.addStretch()

        # Initial logs
        self._add_log("System initialized", "success")
        self._add_log("Neural engine online", "success")
        self._add_log("Voice module ready", "success")

        return right

    # =========== FOOTER ===========
    def _build_footer(self, parent_layout):
        footer = QWidget()
        footer.setFixedHeight(45)
        footer.setStyleSheet("""
            background: rgba(5, 10, 25, 217);
            border: 1px solid rgba(201, 162, 39, 51);
        """)
        fl = QHBoxLayout(footer)
        fl.setContentsMargins(25, 0, 25, 0)

        def make_stat(label, value_id):
            w = QWidget()
            l = QHBoxLayout(w)
            l.setContentsMargins(0, 0, 0, 0)
            l.setSpacing(6)
            lbl = QLabel(label)
            lbl.setFont(QFont(FONT_MONO, 9))
            lbl.setStyleSheet("color: rgba(255,255,255,128);")
            val = QLabel("0")
            val.setObjectName(value_id)
            val.setFont(QFont(FONT_MONO, 9))
            val.setStyleSheet("color: #c9a227;")
            l.addWidget(lbl)
            l.addWidget(val)
            return w

        def make_divider():
            d = QFrame()
            d.setFixedSize(1, 20)
            d.setStyleSheet("background: rgba(201, 162, 39, 77);")
            return d

        fl.addWidget(make_stat("UPTIME:", "uptime_val"))
        fl.addWidget(make_divider())
        fl.addWidget(make_stat("COMMANDS:", "cmd_count"))
        fl.addWidget(make_divider())
        fl.addWidget(make_stat("SUCCESS RATE:", "success_rate"))

        fl.addStretch()

        fl.addWidget(make_stat("MODEL:", "model_val"))
        # Set model value
        fl.addWidget(make_divider())

        ver = QLabel("ALFREDX WAYNECORE v2.0.0 | WAYNE INDUSTRIES")
        ver.setFont(QFont(FONT_MONO, 8))
        ver.setStyleSheet("color: rgba(255,255,255,77); letter-spacing: 2px;")
        fl.addWidget(ver)

        parent_layout.addWidget(footer)

        # Set initial values
        QTimer.singleShot(100, lambda: self._set_footer_val("model_val", "LLAMA-3.1"))
        QTimer.singleShot(100, lambda: self._set_footer_val("success_rate", "100%"))

    # =========== HELPERS ===========
    def _set_footer_val(self, obj_name, text):
        w = self.findChild(QLabel, obj_name)
        if w:
            w.setText(text)

    def _update_clock(self):
        now = datetime.now()
        self.time_label.setText(now.strftime("%H:%M:%S"))
        self.date_label.setText(now.strftime("%A, %b %d, %Y").upper())

    def _update_uptime(self):
        elapsed = int(time.time() - self.start_time)
        h = elapsed // 3600
        m = (elapsed % 3600) // 60
        s = elapsed % 60
        self._set_footer_val("uptime_val", f"{h}H {m}M {s}S")

    def _update_stats(self):
        cpu = max(5, min(99, 45 + random.randint(-5, 5)))
        mem = max(5, min(99, 62 + random.randint(-3, 3)))
        net = max(5, min(99, 78 + random.randint(-4, 4)))
        gpu = max(5, min(99, 23 + random.randint(-4, 4)))

        self.cpu_bar.set_value(cpu)
        self.mem_bar.set_value(mem)
        self.net_bar.set_value(net)

        self.arc_cpu.set_value(cpu)
        self.arc_ram.set_value(mem)
        self.arc_gpu.set_value(gpu)

    def _add_log(self, action, log_type='success'):
        item = LogItem(action, log_type)
        # Insert at top (newest first)
        self.log_layout.insertWidget(0, item)
        count = self.log_layout.count()
        if count > 21:
            w = self.log_layout.itemAt(count - 2)
            if w and w.widget():
                w.widget().deleteLater()

    def _add_message(self, sender, text):
        ts = datetime.now().strftime("%H:%M:%S")
        msg = MessageBubble(sender, text, ts)
        count = self.messages_layout.count()
        self.messages_layout.insertWidget(count - 1, msg)
        QTimer.singleShot(50, lambda: self.messages_scroll.verticalScrollBar().setValue(
            self.messages_scroll.verticalScrollBar().maximum()))

    def _show_typing(self):
        self.typing = TypingIndicator()
        count = self.messages_layout.count()
        self.messages_layout.insertWidget(count - 1, self.typing)
        QTimer.singleShot(50, lambda: self.messages_scroll.verticalScrollBar().setValue(
            self.messages_scroll.verticalScrollBar().maximum()))

    def _remove_typing(self):
        if hasattr(self, 'typing') and self.typing:
            self.typing.deleteLater()
            self.typing = None

    def _send_command(self):
        text = self.command_input.text().strip()
        if not text or self.is_processing:
            return
        self.command_input.clear()
        self._process_command(text)

    def _send_command_text(self, text):
        self._process_command(text)

    def _process_command(self, text):
        self.is_processing = True
        self.command_count += 1
        self._set_footer_val("cmd_count", str(self.command_count))

        self._add_message('user', text)
        self._add_log(f"Command: {text[:30]}...", 'pending')

        self._show_typing()

        delay = 1200 + random.randint(0, 1500)
        QTimer.singleShot(delay, lambda: self._deliver_response(text))

    def _deliver_response(self, text):
        self._remove_typing()
        response = AlfredAI.get_response(text)
        self._add_message('alfred', response)

        self.success_count += 1
        rate = f"{(self.success_count / self.command_count * 100):.1f}%"
        self._set_footer_val("success_rate", rate)
        self._add_log("Response delivered", 'success')
        self.is_processing = False

    def _quick_command(self, cmd_key):
        cmd_map = {
            'browser': 'Open the secure browser',
            'vscode': 'Launch VS Code',
            'music': 'Play my music',
            'files': 'Open file manager',
            'vision': 'Activate vision systems',
            'search': 'Initialize search module'
        }

        # Visual feedback
        for k, btn in self.cmd_buttons.items():
            btn.set_active(k == cmd_key)
        QTimer.singleShot(2000, lambda: self.cmd_buttons[cmd_key].set_active(False))

        self._send_command_text(cmd_map.get(cmd_key, cmd_key))

    def _toggle_mic(self):
        self.mic_active = not self.mic_active
        if self.mic_active:
            self.mic_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #00ff88, stop:1 #00cc6a);
                    border: none; font-size: 16px; color: white;
                }
            """)
            self.voice_viz.status_text = "● LISTENING..."
            self._add_log("Microphone activated", 'success')
        else:
            self.mic_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #ff3333, stop:1 #cc0000);
                    border: none; font-size: 16px; color: white;
                }
            """)
            self.voice_viz.status_text = "● VOICE RECOGNITION ACTIVE"
            self._add_log("Microphone deactivated", 'pending')

    def _attach_file(self):
        self._add_log("File attachment dialog opened", 'pending')
        path, _ = QFileDialog.getOpenFileName(self, "Attach File")
        if path:
            name = os.path.basename(path)
            self._add_log(f"File attached: {name}", 'success')
            self._add_message('user', f"📎 Attached file: {name}")
            QTimer.singleShot(1500, lambda: self._file_response(name))

    def _file_response(self, name):
        self._add_message('alfred', f'File "{name}" received, Master Wayne. I\'ve stored it in the secure vault and initiated a scan. The file appears clean. Would you like me to process it further?')
        self._add_log(f"File processed: {name}", 'success')

    def _show_notifications(self):
        self._add_log("Notifications panel opened", 'success')
        dlg = NotificationDialog(self)
        dlg.exec_()

    def _show_settings(self):
        self._add_log("Settings panel opened", 'success')
        dlg = SettingsDialog(self)
        dlg.exec_()

    def _power_off(self):
        reply = QMessageBox.question(self, "AlfredX", "Initiate system shutdown sequence?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self._add_log("Shutdown sequence initiated", 'error')
            self.status_dot.setStyleSheet("color: #ff3333;")
            self.status_label.setText("SHUTTING DOWN")
            self.status_label.setStyleSheet("color: #ff3333; letter-spacing: 2px;")
            self._add_message('alfred', "Initiating shutdown sequence, Master Wayne. All active sessions will be saved. Goodnight, sir.")
            QTimer.singleShot(3000, self._complete_shutdown)

    def _complete_shutdown(self):
        self.status_label.setText("SYSTEM OFFLINE")
        self._add_log("System offline", 'error')

    def _initial_greeting(self):
        self._add_message('alfred',
            "Good evening, Master Wayne. All systems are operational and Wayne Tower security protocols are active. I've detected 3 pending items requiring your attention. How may I assist you this evening?")
        self._add_log("Alfred AI initialized", 'success')


# ============================================
# ENTRY POINT
# ============================================
def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(MAIN_STYLESHEET)
    app.setStyle('Fusion')

    # Dark palette
    palette = QPalette()
    palette.setColor(QPalette.Window, DARK)
    palette.setColor(QPalette.WindowText, WHITE)
    palette.setColor(QPalette.Base, DARK_BLUE)
    palette.setColor(QPalette.AlternateBase, DARK)
    palette.setColor(QPalette.ToolTipBase, DARK)
    palette.setColor(QPalette.ToolTipText, WHITE)
    palette.setColor(QPalette.Text, WHITE)
    palette.setColor(QPalette.Button, DARK_BLUE)
    palette.setColor(QPalette.ButtonText, WHITE)
    palette.setColor(QPalette.Highlight, GOLD)
    palette.setColor(QPalette.HighlightedText, DARK)
    app.setPalette(palette)

    window = AlfredXWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
