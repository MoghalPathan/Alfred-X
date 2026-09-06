"""
AlfredX: GUI Stylesheet — Cinematic Waynecore Theme
Gold/Cyan/Dark styling matching the HTML cinematic interface.
"""

MAIN_STYLESHEET = """
QWidget {
    background-color: #000000;
    color: #ffffff;
    font-family: 'Segoe UI', 'Consolas', monospace;
}

QScrollArea {
    border: none;
    background: transparent;
}
QScrollBar:vertical {
    background: rgba(0, 0, 0, 0.3);
    width: 4px;
}
QScrollBar::handle:vertical {
    background: #c9a227;
    border-radius: 2px;
    min-height: 30px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

QLabel {
    color: #ffffff;
    background: transparent;
    border: none;
}

QLineEdit {
    background: rgba(10, 10, 30, 0.8);
    border: 2px solid rgba(201, 162, 39, 0.3);
    color: #ffffff;
    padding: 8px 16px;
    border-radius: 3px;
}
QLineEdit:focus {
    border-color: #c9a227;
}

QPushButton {
    background: rgba(201, 162, 39, 0.1);
    border: 1px solid rgba(201, 162, 39, 0.3);
    color: #c9a227;
    border-radius: 3px;
}
QPushButton:hover {
    background: rgba(201, 162, 39, 0.25);
}

QFrame {
    background: transparent;
    border: none;
}
"""

