"""
AlfredX: Login Screen — Winter Soldier Protocol
Sunburst circle logo with pulsing rays.
All elements are layout widgets — no overlap.
Echo Auth = real microphone listening with waveform bars.
Text Auth = buttons spread, password in center.
Fully centered + scrollable so nothing gets cut off.
"""
import math
import random
import threading
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QScrollArea, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QRectF, QPointF
from PyQt5.QtGui import (
    QFont, QColor, QPainter, QPainterPath,
    QRadialGradient, QPen
)

from config import ACTIVATION_WORDS, TEXT_PASSWORD, AI_NAME, WORD_VARIANTS

CYAN = QColor(0, 224, 255)
BLACK = QColor(0, 0, 0)

# Try to import speech_recognition for real voice auth
try:
    import speech_recognition as sr
    HAS_SPEECH = True
except ImportError:
    HAS_SPEECH = False


# ══════════════════════════════════════════════════════
# Waveform Widget
# ══════════════════════════════════════════════════════

class WaveformWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(50)
        self._angle = 0.0
        self._active = False
        self._amplitude = 0.0  # For real mic amplitude

    def start(self):
        self._active = True

    def stop(self):
        self._active = False
        self._amplitude = 0.0

    def set_angle(self, a):
        self._angle = a
        if self._active:
            self.update()

    def set_amplitude(self, amp):
        """Set amplitude from mic input (0.0 to 1.0)"""
        self._amplitude = min(1.0, amp)

    def paintEvent(self, event):
        if not self._active:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w = self.width()
        h = self.height()
        cx = w / 2
        cy = h / 2
        pulse = 0.6 + 0.4 * math.sin(self._angle)
        # Mix base animation with real mic amplitude
        amp_factor = max(0.3, self._amplitude) if self._amplitude > 0.05 else (0.3 + 0.2 * pulse)
        n_bars = 40
        bar_w = 4
        gap = 2
        total = n_bars * (bar_w + gap)
        sx = cx - total / 2
        painter.setPen(Qt.NoPen)
        for i in range(n_bars):
            bx = sx + i * (bar_w + gap)
            base_h = 4 + 26 * abs(math.sin(self._angle * 3 + i * 0.4)) * amp_factor
            bh = max(3, base_h)
            alpha = int(min(255, 160 * pulse + 60 * self._amplitude))
            painter.setBrush(QColor(0, 224, 255, alpha))
            painter.drawRoundedRect(QRectF(bx, cy - bh / 2, bar_w, bh), 1, 1)
        painter.end()


# ══════════════════════════════════════════════════════
# Dash Progress
# ══════════════════════════════════════════════════════

class DashProgress(QWidget):
    def __init__(self, total=10, parent=None):
        super().__init__(parent)
        self.setFixedHeight(16)
        self._total = total
        self._done = 0
        self._angle = 0.0

    def set_done(self, n):
        self._done = n
        self.update()

    def set_angle(self, a):
        self._angle = a
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w = self.width()
        h = self.height()
        pulse = 0.6 + 0.4 * math.sin(self._angle)
        dw, dg = 22, 6
        tw = self._total * (dw + dg) - dg
        sx = (w - tw) / 2
        cy = h / 2
        painter.setPen(Qt.NoPen)
        for i in range(self._total):
            dx = sx + i * (dw + dg)
            if i < self._done:
                g = QRadialGradient(dx + dw / 2, cy, dw)
                g.setColorAt(0, QColor(0, 224, 255, int(40 * pulse)))
                g.setColorAt(1, QColor(0, 0, 0, 0))
                painter.setBrush(g)
                painter.drawRect(QRectF(dx - 4, cy - 7, dw + 8, 14))
                painter.setBrush(QColor(0, 224, 255, int(230 * pulse)))
            else:
                painter.setBrush(QColor(0, 224, 255, 30))
            painter.drawRoundedRect(QRectF(dx, cy - 2, dw, 4), 2, 2)
        painter.end()


# ══════════════════════════════════════════════════════
# Sunburst Logo
# ══════════════════════════════════════════════════════

class SunburstLogo(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(180)
        self._angle = 0.0
        random.seed(99)
        self._rays = []
        for i in range(360):
            a = i * math.pi / 180
            self._rays.append({
                'angle': a,
                'base_len': random.uniform(0.5, 1.0),
                'thickness': random.uniform(0.5, 2.0),
                'alpha': random.randint(40, 140),
                'phase': random.uniform(0, 2 * math.pi),
                'speed': random.uniform(0.8, 1.5),
            })

    def set_angle(self, a):
        self._angle = a
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w = self.width()
        h = self.height()
        cx = w / 2
        cy = h / 2
        pulse = 0.6 + 0.4 * math.sin(self._angle)

        circle_r = min(int(h * 0.35), 65)
        ray_inner = circle_r + 4
        ray_max = int(circle_r * 0.55)

        for ray in self._rays:
            angle = ray['angle']
            pf = 0.6 + 0.4 * math.sin(self._angle * ray['speed'] + ray['phase'])
            r_out = ray_inner + ray_max * ray['base_len'] * pf
            x1 = cx + ray_inner * math.cos(angle)
            y1 = cy + ray_inner * math.sin(angle)
            x2 = cx + r_out * math.cos(angle)
            y2 = cy + r_out * math.sin(angle)
            pen = QPen(QColor(0, 200, 240, int(ray['alpha'] * pf)), ray['thickness'])
            pen.setCapStyle(Qt.RoundCap)
            painter.setPen(pen)
            painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))

        painter.setPen(Qt.NoPen)
        ext = ray_inner + ray_max + 20
        amb = QRadialGradient(cx, cy, ext)
        amb.setColorAt(0, QColor(0, 224, 255, int(10 * pulse)))
        amb.setColorAt(0.6, QColor(0, 200, 230, int(4 * pulse)))
        amb.setColorAt(1, QColor(0, 0, 0, 0))
        painter.setBrush(amb)
        painter.drawEllipse(QRectF(cx - ext, cy - ext, ext * 2, ext * 2))

        cp = QPainterPath()
        cp.addEllipse(QRectF(cx - circle_r, cy - circle_r, circle_r * 2, circle_r * 2))
        cf = QRadialGradient(cx, cy, circle_r)
        cf.setColorAt(0, QColor(8, 18, 28, 240))
        cf.setColorAt(0.8, QColor(5, 12, 22, 250))
        cf.setColorAt(1, QColor(0, 8, 16, 255))
        painter.fillPath(cp, cf)

        painter.setPen(QPen(QColor(0, 224, 255, int(100 * pulse)), 2))
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(QRectF(cx - circle_r, cy - circle_r, circle_r * 2, circle_r * 2))

        painter.setPen(QPen(QColor(0, 200, 230, int(40 * pulse)), 1))
        ir = circle_r - 6
        painter.drawEllipse(QRectF(cx - ir, cy - ir, ir * 2, ir * 2))

        painter.setPen(QColor(0, 224, 255, int(220 * pulse)))
        painter.setFont(QFont("Segoe UI", 18, QFont.Bold))
        painter.drawText(QRectF(cx - circle_r, cy - 14, circle_r * 2, 28),
                         Qt.AlignCenter, "ALFREDX")

        painter.setPen(QColor(0, 180, 210, int(140 * pulse)))
        painter.setFont(QFont("Segoe UI", 7))
        painter.drawText(QRectF(cx - 30, cy + 12, 60, 14),
                         Qt.AlignCenter, "ONLINE")
        painter.end()


# ══════════════════════════════════════════════════════
# MAIN LOGIN SCREEN
# ══════════════════════════════════════════════════════

class LoginScreen(QWidget):
    activated = pyqtSignal()
    # Signal for voice recognition results (thread-safe)
    _voice_result = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._anim_angle = 0.0
        self._mode = None
        self._listening = False
        self._current_word = 0
        self._voice_thread = None
        self._stop_listening = False

        self._setup_ui()

        # Connect voice result signal
        self._voice_result.connect(self._handle_voice_result)

        self._timer = QTimer()
        self._timer.timeout.connect(self._animate)
        self._timer.start(33)

    def _animate(self):
        self._anim_angle += 0.015
        pulse = 0.6 + 0.4 * math.sin(self._anim_angle)
        self._logo.set_angle(self._anim_angle)
        self._dash.set_angle(self._anim_angle)
        self._waveform.set_angle(self._anim_angle)
        a = int(230 * pulse)
        self._title.setStyleSheet(f"color: rgba(0,224,255,{a}); background: transparent;")

    def _setup_ui(self):
        self.setStyleSheet("background: black;")

        # ── Main outer layout ──
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # ── Scroll Area wrapping everything ──
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setStyleSheet(
            "QScrollArea { background: black; border: none; }"
            "QScrollBar:vertical { background: rgba(0,0,0,0.5); width: 6px; }"
            "QScrollBar::handle:vertical { background: rgba(0,224,255,0.3); "
            "border-radius: 3px; min-height: 30px; }"
            "QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }"
            "QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }"
        )

        # ── Content widget inside scroll ──
        content = QWidget()
        content.setStyleSheet("background: black;")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(0)

        # Top stretch — pushes content to vertical center
        layout.addStretch(1)

        # ── ALFREDX ──
        self._title = QLabel("A L F R E D X")
        self._title.setFont(QFont("Segoe UI", 36, QFont.Bold))
        self._title.setStyleSheet("color: #00e0ff; background: transparent;")
        self._title.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._title)

        # ── WAYNECORE ASSISTANT ──
        sub = QLabel("W A Y N E C O R E   A S S I S T A N T")
        sub.setFont(QFont("Segoe UI", 10))
        sub.setStyleSheet("color: rgba(0,180,210,130); background: transparent;")
        sub.setAlignment(Qt.AlignCenter)
        layout.addWidget(sub)

        layout.addSpacing(6)

        # ── Sunburst Logo ──
        self._logo = SunburstLogo()
        layout.addWidget(self._logo)

        layout.addSpacing(6)

        # ── WINTER SOLDIER PROTOCOL ──
        proto = QLabel("W I N T E R   S O L D I E R   P R O T O C O L")
        proto.setFont(QFont("Segoe UI", 11, QFont.Bold))
        proto.setStyleSheet("color: rgba(0,224,255,180); background: transparent;")
        proto.setAlignment(Qt.AlignCenter)
        layout.addWidget(proto)

        layout.addSpacing(4)

        # ── Dash Progress ──
        self._dash = DashProgress(total=len(ACTIVATION_WORDS))
        layout.addWidget(self._dash)

        layout.addSpacing(16)

        # ══════════════════════════════════════════
        # DEFAULT VIEW: buttons side by side
        # ══════════════════════════════════════════
        self._default_section = QFrame()
        self._default_section.setStyleSheet("background: transparent; border: none;")
        ds = QVBoxLayout(self._default_section)
        ds.setContentsMargins(0, 0, 0, 0)
        ds.setSpacing(10)

        auth_row = QHBoxLayout()
        auth_row.setAlignment(Qt.AlignCenter)
        auth_row.setSpacing(14)

        self.voice_btn = QPushButton("▎▌█▌▎  ECHO AUTH")
        self.voice_btn.setFixedSize(200, 44)
        self.voice_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.voice_btn.setCursor(Qt.PointingHandCursor)
        self.voice_btn.setStyleSheet(self._cyan_btn())
        self.voice_btn.clicked.connect(self._select_voice)
        auth_row.addWidget(self.voice_btn)

        self.text_btn = QPushButton(">_  TEXT AUTH")
        self.text_btn.setFixedSize(200, 44)
        self.text_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.text_btn.setCursor(Qt.PointingHandCursor)
        self.text_btn.setStyleSheet(self._gold_btn())
        self.text_btn.clicked.connect(self._select_text)
        auth_row.addWidget(self.text_btn)

        ds.addLayout(auth_row)

        reset_row = QHBoxLayout()
        reset_row.setAlignment(Qt.AlignCenter)
        self.reset_btn_default = QPushButton("↺ RESET")
        self.reset_btn_default.setFixedSize(140, 40)
        self.reset_btn_default.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.reset_btn_default.setCursor(Qt.PointingHandCursor)
        self.reset_btn_default.setStyleSheet(self._gold_btn())
        self.reset_btn_default.clicked.connect(self._on_reset)
        reset_row.addWidget(self.reset_btn_default)
        ds.addLayout(reset_row)

        layout.addWidget(self._default_section)

        # ══════════════════════════════════════════
        # ECHO AUTH VIEW: waveform + voice listening
        # ══════════════════════════════════════════
        self._echo_section = QFrame()
        self._echo_section.setStyleSheet("background: transparent; border: none;")
        self._echo_section.setVisible(False)  # Hidden by default
        es = QVBoxLayout(self._echo_section)
        es.setContentsMargins(0, 0, 0, 0)
        es.setSpacing(8)
        es.setAlignment(Qt.AlignCenter)

        # Listening status label
        self._listen_label = QLabel("LISTENING...")
        self._listen_label.setFont(QFont("Segoe UI", 9, QFont.Bold))
        self._listen_label.setStyleSheet("color: rgba(0,224,255,0.6); background: transparent; letter-spacing: 3px;")
        self._listen_label.setAlignment(Qt.AlignCenter)
        es.addWidget(self._listen_label)

        es.addSpacing(2)

        self._waveform = WaveformWidget()
        es.addWidget(self._waveform)

        es.addSpacing(4)

        # Word progress hint
        self._word_hint = QLabel("")
        self._word_hint.setFont(QFont("Consolas", 10))
        self._word_hint.setStyleSheet("color: rgba(0,224,255,0.4); background: transparent;")
        self._word_hint.setAlignment(Qt.AlignCenter)
        es.addWidget(self._word_hint)

        es.addSpacing(4)

        # Fallback text input (hidden, shown only if no mic)
        self.word_input = QLineEdit()
        self.word_input.setFixedSize(300, 46)
        self.word_input.setAlignment(Qt.AlignCenter)
        self.word_input.setFont(QFont("Consolas", 13))
        self.word_input.setPlaceholderText("Type word (no mic detected)")
        self.word_input.setStyleSheet(self._input_style())
        self.word_input.returnPressed.connect(self._check_word)
        self.word_input.setVisible(False)  # Only show if no speech_recognition
        es.addWidget(self.word_input, alignment=Qt.AlignCenter)

        # Back + Reset row
        echo_btns = QHBoxLayout()
        echo_btns.setAlignment(Qt.AlignCenter)
        echo_btns.setSpacing(12)

        back1 = QPushButton("← BACK")
        back1.setFixedSize(120, 38)
        back1.setFont(QFont("Segoe UI", 9, QFont.Bold))
        back1.setCursor(Qt.PointingHandCursor)
        back1.setStyleSheet(self._cyan_btn())
        back1.clicked.connect(self._on_reset)
        echo_btns.addWidget(back1)

        reset1 = QPushButton("↺ RESET")
        reset1.setFixedSize(120, 38)
        reset1.setFont(QFont("Segoe UI", 9, QFont.Bold))
        reset1.setCursor(Qt.PointingHandCursor)
        reset1.setStyleSheet(self._gold_btn())
        reset1.clicked.connect(self._on_reset)
        echo_btns.addWidget(reset1)

        es.addLayout(echo_btns)

        layout.addWidget(self._echo_section)

        # ══════════════════════════════════════════
        # TEXT AUTH VIEW: spread buttons + password
        # ══════════════════════════════════════════
        self._text_section = QFrame()
        self._text_section.setStyleSheet("background: transparent; border: none;")
        self._text_section.setVisible(False)  # Hidden by default
        txs = QVBoxLayout(self._text_section)
        txs.setContentsMargins(0, 0, 0, 0)
        txs.setSpacing(8)
        txs.setAlignment(Qt.AlignCenter)

        # Spread row: ECHO AUTH (left) ---- TEXT AUTH (right)
        spread_row = QHBoxLayout()
        spread_row.setContentsMargins(40, 0, 40, 0)

        self.voice_btn2 = QPushButton("▎▌█▌▎  ECHO AUTH")
        self.voice_btn2.setFixedSize(180, 40)
        self.voice_btn2.setFont(QFont("Segoe UI", 9, QFont.Bold))
        self.voice_btn2.setCursor(Qt.PointingHandCursor)
        self.voice_btn2.setStyleSheet(self._cyan_btn())
        self.voice_btn2.clicked.connect(self._select_voice)
        spread_row.addWidget(self.voice_btn2)

        spread_row.addStretch()

        self.text_btn2 = QPushButton(">_  TEXT AUTH")
        self.text_btn2.setFixedSize(180, 40)
        self.text_btn2.setFont(QFont("Segoe UI", 9, QFont.Bold))
        self.text_btn2.setCursor(Qt.PointingHandCursor)
        self.text_btn2.setStyleSheet(self._gold_active())
        spread_row.addWidget(self.text_btn2)

        txs.addLayout(spread_row)

        txs.addSpacing(6)

        # Password input centered
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setAlignment(Qt.AlignCenter)
        self.password_input.setFont(QFont("Consolas", 13))
        self.password_input.setFixedSize(320, 46)
        self.password_input.setStyleSheet(self._input_style())
        self.password_input.returnPressed.connect(self._check_password)
        txs.addWidget(self.password_input, alignment=Qt.AlignCenter)

        txs.addSpacing(4)

        # LOGIN button
        login_btn = QPushButton("L O G I N")
        login_btn.setFixedSize(320, 44)
        login_btn.setFont(QFont("Segoe UI", 12, QFont.Bold))
        login_btn.setCursor(Qt.PointingHandCursor)
        login_btn.setStyleSheet(
            "QPushButton { background: rgba(0, 224, 255, 0.1); "
            "border: 2px solid rgba(0, 224, 255, 0.5); "
            "border-radius: 6px; color: #00e0ff; letter-spacing: 4px; }"
            "QPushButton:hover { background: rgba(0, 224, 255, 0.2); }"
        )
        login_btn.clicked.connect(self._check_password)
        txs.addWidget(login_btn, alignment=Qt.AlignCenter)

        txs.addSpacing(4)

        # RESET button
        reset2 = QPushButton("↺ RESET")
        reset2.setFixedSize(140, 38)
        reset2.setFont(QFont("Segoe UI", 10, QFont.Bold))
        reset2.setCursor(Qt.PointingHandCursor)
        reset2.setStyleSheet(self._gold_btn())
        reset2.clicked.connect(self._on_reset)
        txs.addWidget(reset2, alignment=Qt.AlignCenter)

        layout.addWidget(self._text_section)

        # ── Status ──
        self.status = QLabel("")
        self.status.setFont(QFont("Segoe UI", 10))
        self.status.setStyleSheet("background: transparent;")
        self.status.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status)

        # Bottom stretch — balances vertical centering
        layout.addStretch(1)

        # Set content into scroll area
        scroll.setWidget(content)
        outer.addWidget(scroll)

    # ── Styles ──

    def _cyan_btn(self):
        return (
            "QPushButton { background: rgba(0, 224, 255, 0.12); "
            "border: 1.5px solid rgba(0, 224, 255, 0.5); "
            "border-radius: 5px; color: #00e0ff; letter-spacing: 1px; }"
            "QPushButton:hover { background: rgba(0, 224, 255, 0.22); }"
        )

    def _cyan_active(self):
        return (
            "QPushButton { background: rgba(0, 224, 255, 0.2); "
            "border: 2px solid rgba(0, 224, 255, 0.7); "
            "border-radius: 5px; color: #00e0ff; letter-spacing: 1px; }"
            "QPushButton:hover { background: rgba(0, 224, 255, 0.3); }"
        )

    def _gold_btn(self):
        return (
            "QPushButton { background: rgba(200, 170, 80, 0.06); "
            "border: 1.5px solid rgba(200, 170, 80, 0.4); "
            "border-radius: 5px; color: #c8aa50; letter-spacing: 1px; }"
            "QPushButton:hover { background: rgba(200, 170, 80, 0.15); }"
        )

    def _gold_active(self):
        return (
            "QPushButton { background: rgba(200, 170, 80, 0.2); "
            "border: 2px solid rgba(200, 170, 80, 0.7); "
            "border-radius: 5px; color: #c8aa50; letter-spacing: 1px; }"
            "QPushButton:hover { background: rgba(200, 170, 80, 0.3); }"
        )

    def _input_style(self):
        return (
            "QLineEdit { background: rgba(0, 20, 30, 0.9); "
            "border: 2px solid rgba(0, 224, 255, 0.3); "
            "border-radius: 6px; padding: 0 16px; color: #00e0ff; }"
            "QLineEdit:focus { border-color: rgba(0, 224, 255, 0.7); }"
        )

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), BLACK)
        painter.end()

    # ══════════════════════════════════════════════════
    # VOICE RECOGNITION (runs in background thread)
    # ══════════════════════════════════════════════════

    def _start_voice_listener(self):
        """Start continuous voice listening in a background thread."""
        if not HAS_SPEECH:
            # Fallback: show text input if speech_recognition not installed
            self.word_input.setVisible(True)
            self._listen_label.setText("NO MIC — TYPE WORDS BELOW")
            return

        self._stop_listening = False
        self._voice_thread = threading.Thread(target=self._voice_loop, daemon=True)
        self._voice_thread.start()

    def _stop_voice_listener(self):
        """Stop the voice listening thread."""
        self._stop_listening = True

    def _voice_loop(self):
        """Background thread: continuously listen for words."""
        recognizer = sr.Recognizer()
        recognizer.energy_threshold = 300
        recognizer.dynamic_energy_threshold = True
        recognizer.pause_threshold = 1.0

        try:
            mic = sr.Microphone()
        except (OSError, AttributeError):
            # No microphone available — fallback to text input
            self._voice_result.emit("__NO_MIC__")
            return

        with mic as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)

        while not self._stop_listening:
            try:
                with mic as source:
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=4)
                    # Simulate amplitude for waveform
                    self._waveform.set_amplitude(0.8)

                try:
                    text = recognizer.recognize_google(audio).strip().lower()
                    self._voice_result.emit(text)
                except sr.UnknownValueError:
                    self._waveform.set_amplitude(0.1)
                except sr.RequestError:
                    self._voice_result.emit("__NET_ERR__")
                    break

            except sr.WaitTimeoutError:
                self._waveform.set_amplitude(0.1)
                continue
            except Exception:
                break

        self._waveform.set_amplitude(0.0)

    def _handle_voice_result(self, text):
        """Handle voice recognition result on the main thread."""
        if text == "__NO_MIC__":
            self.word_input.setVisible(True)
            self._listen_label.setText("NO MIC — TYPE WORDS BELOW")
            return
        if text == "__NET_ERR__":
            self.word_input.setVisible(True)
            self._listen_label.setText("NETWORK ERROR — TYPE WORDS BELOW")
            return

        # Check if any recognized word matches (with variant/fuzzy matching)
        expected = ACTIVATION_WORDS[self._current_word].lower()
        variants = WORD_VARIANTS.get(expected, [expected])
        words = text.split()

        matched = False
        for word in words:
            # Exact variant match
            if word in variants:
                matched = True
                break
            # Fuzzy: accept if word starts with same 4+ chars
            if len(word) >= 4 and len(expected) >= 4:
                if word[:4] == expected[:4]:
                    matched = True
                    break
            # Fuzzy: accept if edit distance is small (1-2 chars off)
            if abs(len(word) - len(expected)) <= 2 and len(expected) >= 4:
                common = sum(1 for a, b in zip(word, expected) if a == b)
                if common >= len(expected) * 0.6:
                    matched = True
                    break

        if matched:
            self._current_word += 1
            self._dash.set_done(self._current_word)
            self._update_word_hint()

            if self._current_word >= len(ACTIVATION_WORDS):
                self.status.setStyleSheet("color: #00dd66; background: transparent;")
                self.status.setText("ACCESS GRANTED")
                self._listening = False
                self._waveform.stop()
                self._stop_voice_listener()
                self._listen_label.setText("IDENTITY CONFIRMED")
                QTimer.singleShot(1500, self._activate)
            else:
                self.status.setStyleSheet("color: rgba(0,224,255,0.8); background: transparent;")
                self.status.setText(f'✓ "{expected}" Accepted')
                QTimer.singleShot(1000, lambda: self.status.setText(""))
        else:
            self.status.setStyleSheet("color: #ff4455; background: transparent;")
            self.status.setText(f'✗ Heard: "{text}"')
            QTimer.singleShot(1500, lambda: self.status.setText(""))

    def _update_word_hint(self):
        """Show progress: which word we're waiting for next."""
        if self._current_word < len(ACTIVATION_WORDS):
            done = self._current_word
            total = len(ACTIVATION_WORDS)
            self._word_hint.setText(f"Word {done + 1} of {total}")
        else:
            self._word_hint.setText("All words confirmed")

    # ══════════════════════════════════════════════════
    # ACTIONS
    # ══════════════════════════════════════════════════

    def _select_voice(self):
        self._mode = "voice"
        self._listening = True
        # Hide default + text, show echo
        self._default_section.setVisible(False)
        self._text_section.setVisible(False)
        self._echo_section.setVisible(True)
        self._waveform.start()
        self._update_word_hint()
        self.status.setText("")
        # Start real voice listener
        self._start_voice_listener()

    def _select_text(self):
        self._mode = "text"
        self._listening = False
        self._waveform.stop()
        self._stop_voice_listener()
        # Hide default + echo, show text
        self._default_section.setVisible(False)
        self._echo_section.setVisible(False)
        self._text_section.setVisible(True)
        self.password_input.setFocus()
        self.status.setText("")

    def _on_reset(self):
        self._current_word = 0
        self._listening = False
        self._waveform.stop()
        self._stop_voice_listener()
        self._mode = None
        # Show default, hide others
        self._default_section.setVisible(True)
        self._echo_section.setVisible(False)
        self._text_section.setVisible(False)
        self.word_input.clear()
        self.word_input.setVisible(False)
        self.word_input.setEnabled(True)
        self.password_input.clear()
        self.status.setText("")
        self._dash.set_done(0)
        self._word_hint.setText("")
        self._listen_label.setText("LISTENING...")

    def _check_word(self):
        """Fallback: manual word entry when no mic is available."""
        text = self.word_input.text().strip().lower()
        self.word_input.clear()
        if not text:
            return
        expected = ACTIVATION_WORDS[self._current_word].lower()
        if text == expected:
            self._current_word += 1
            self._dash.set_done(self._current_word)
            self._update_word_hint()
            if self._current_word >= len(ACTIVATION_WORDS):
                self.status.setStyleSheet("color: #00dd66; background: transparent;")
                self.status.setText("ACCESS GRANTED")
                self._listening = False
                self._waveform.stop()
                self.word_input.setEnabled(False)
                QTimer.singleShot(1500, self._activate)
            else:
                self.status.setStyleSheet("color: rgba(0,224,255,0.8); background: transparent;")
                self.status.setText("✓ Accepted")
                QTimer.singleShot(800, lambda: self.status.setText(""))
        else:
            self.status.setStyleSheet("color: #ff4455; background: transparent;")
            self.status.setText("✗ Incorrect")
            QTimer.singleShot(1200, lambda: self.status.setText(""))

    def _check_password(self):
        text = self.password_input.text().strip()
        if not text:
            return
        if text.upper() == TEXT_PASSWORD:
            self.status.setStyleSheet("color: #00dd66; background: transparent;")
            self.status.setText("ACCESS GRANTED")
            QTimer.singleShot(1500, self._activate)
        else:
            self.status.setStyleSheet("color: #ff4455; background: transparent;")
            self.status.setText("ACCESS DENIED")
            self.password_input.clear()
            QTimer.singleShot(2000, lambda: self.status.setText(""))

    def _activate(self):
        self._timer.stop()
        self._stop_voice_listener()
        self.activated.emit()