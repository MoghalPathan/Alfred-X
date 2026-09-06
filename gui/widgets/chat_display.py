"""
AlfredX: Chat Display Widget
Scrollable message bubbles with timestamps.
"""
from datetime import datetime
from PyQt5.QtWidgets import (
    QScrollArea, QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont


class ChatDisplay(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setStyleSheet("background: transparent; border: none;")

        self._container = QWidget()
        self._container.setStyleSheet("background: transparent;")
        self._layout = QVBoxLayout(self._container)
        self._layout.setContentsMargins(20, 20, 20, 20)
        self._layout.setSpacing(12)
        self._layout.addStretch()

        self.setWidget(self._container)

    def _get_engine_mode(self) -> str:
        """Best-effort: walk up parents to find ai_engine.mode/current_model."""
        w = self.parent()
        while w is not None:
            engine = getattr(w, "ai_engine", None) or getattr(w, "_ai_engine", None)
            if engine is not None:
                mode = getattr(engine, "mode", None) or getattr(engine, "current_model", None)
                if isinstance(mode, str) and mode.strip():
                    return mode.strip().upper()
            # sometimes stored directly on window
            mode2 = getattr(w, "current_model", None) or getattr(w, "_current_model", None)
            if isinstance(mode2, str) and mode2.strip():
                return mode2.strip().upper()
            w = w.parent()
        return "GROQ"

    def add_message(self, text, is_user=False, model_label=None):
        bubble = QFrame()
        bubble_layout = QVBoxLayout(bubble)
        bubble_layout.setContentsMargins(16, 10, 16, 10)
        bubble_layout.setSpacing(6)

        # Header (who is speaking)
        header = QLabel()
        header.setFont(QFont("Consolas", 9))
        header.setStyleSheet("background: transparent; letter-spacing: 1px;")

        if is_user:
            header.setText("YOU")
            header.setAlignment(Qt.AlignRight)
            header.setStyleSheet("color: rgba(176, 208, 255, 0.65); background: transparent;")
        else:
            mode = self._get_engine_mode()
            header.setText(f"ALFRED • {mode}")
            header.setAlignment(Qt.AlignLeft)
            header.setStyleSheet("color: rgba(224, 216, 192, 0.65); background: transparent;")

        model_tag = None
        if model_label and not is_user:
            model_tag = QLabel(model_label)
            model_tag.setFont(QFont("Consolas", 8))
            model_tag.setStyleSheet("color: #00ffcc; background: transparent;")    

        # Message text
        msg = QLabel(text)
        msg.setWordWrap(True)
        msg.setTextInteractionFlags(Qt.TextSelectableByMouse)
        msg.setFont(QFont("Segoe UI", 11))

        # Timestamp
        time_label = QLabel(datetime.now().strftime("%H:%M"))
        time_label.setFont(QFont("Consolas", 8))

        if is_user:
            bubble.setStyleSheet("""
                QFrame {
                    background-color: rgba(30, 90, 160, 0.25);
                    border: 1px solid rgba(30, 144, 255, 0.2);
                    border-radius: 12px;
                }
            """)
            msg.setStyleSheet("color: #b0d0ff; background: transparent;")
            time_label.setStyleSheet("color: rgba(176, 208, 255, 0.5); background: transparent;")
            time_label.setAlignment(Qt.AlignRight)
        else:
            bubble.setStyleSheet("""
                QFrame {
                    background-color: rgba(40, 40, 20, 0.3);
                    border: 1px solid rgba(255, 215, 0, 0.15);
                    border-radius: 12px;
                }
            """)
            msg.setStyleSheet("color: #e0d8c0; background: transparent;")
            time_label.setStyleSheet("color: rgba(224, 216, 192, 0.4); background: transparent;")
            time_label.setAlignment(Qt.AlignLeft)

        bubble_layout.addWidget(header)
        bubble_layout.addWidget(msg)
        if model_tag:
            bubble_layout.insertWidget(0, model_tag)
        bubble_layout.addWidget(time_label)

        # Wrap in alignment layout
        row = QHBoxLayout()
        if is_user:
            row.addStretch()
            row.addWidget(bubble, stretch=0)
            bubble.setMaximumWidth(600)
        else:
            row.addWidget(bubble, stretch=0)
            row.addStretch()
            bubble.setMaximumWidth(650)

        wrapper = QWidget()
        wrapper.setStyleSheet("background: transparent;")
        wrapper.setLayout(row)

        # Insert before the stretch
        count = self._layout.count()
        self._layout.insertWidget(count - 1, wrapper)

        # Auto-scroll to bottom
        QTimer.singleShot(50, self._scroll_bottom)

    def add_system_message(self, text):
        label = QLabel(text)
        label.setAlignment(Qt.AlignCenter)
        label.setFont(QFont("Consolas", 9))
        label.setStyleSheet("color: rgba(0, 212, 255, 0.6); background: transparent; padding: 8px;")

        count = self._layout.count()
        self._layout.insertWidget(count - 1, label)
        QTimer.singleShot(50, self._scroll_bottom)

    def clear(self):
        while self._layout.count() > 1:
            item = self._layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _scroll_bottom(self):
        sb = self.verticalScrollBar()
        sb.setValue(sb.maximum())
