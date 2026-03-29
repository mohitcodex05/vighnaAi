"""
ui/components/quick_actions.py — Row of quick-action shortcut buttons
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QSizePolicy, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from ui.styles.theme import (
    BG_CARD, BG_HOVER, BORDER_COLOR, ACCENT_PRIMARY, ACCENT_GLOW,
    TEXT_PRIMARY, TEXT_SECONDARY, FONT_FAMILY, FONT_SIZE_SM, FONT_SIZE_XS,
    RADIUS_MD, RADIUS_SM, ACCENT_GREEN, ACCENT_BLUE, ACCENT_ORANGE
)


ACTIONS = [
    ("🌐 Browser",       "open chrome",        ACCENT_BLUE),
    ("📁 Files",         "open downloads",     ACCENT_PRIMARY),
    ("💻 VS Code",       "open vscode",        ACCENT_ORANGE),
    ("⚡ Start Work",   "start work",          ACCENT_GREEN),
    ("🔒 Lock",          "lock screen",         "#EF4444"),
    ("📸 Screenshot",    "take a screenshot",   TEXT_SECONDARY),
]


class QuickActionButton(QPushButton):
    def __init__(self, label: str, command: str, color: str, parent=None):
        super().__init__(parent)
        self.command = command
        self.setText(label)
        self.setToolTip(f'Runs: "{command}"')
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFont(QFont(FONT_FAMILY, FONT_SIZE_SM, QFont.Weight.Bold))
        self.setFixedHeight(38)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setStyleSheet(f"""
            QPushButton {{
                background: {BG_CARD};
                color: {TEXT_PRIMARY};
                border: 1.5px solid {BORDER_COLOR};
                border-radius: {RADIUS_SM}px;
                padding: 0 12px;
                font-size: {FONT_SIZE_SM}px;
                font-family: {FONT_FAMILY};
            }}
            QPushButton:hover {{
                background: {color};
                border-color: {color};
                color: white;
            }}
            QPushButton:pressed {{
                background: {BG_HOVER};
                border-color: {ACCENT_PRIMARY};
            }}
        """)


class QuickActionsBar(QWidget):
    """
    Emits action_triggered(command_str) when a button is clicked.
    """
    action_triggered = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(4)

        lbl = QLabel("Quick Actions")
        lbl.setFont(QFont(FONT_FAMILY, FONT_SIZE_XS, QFont.Weight.Bold))
        lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; background: transparent;")
        outer.addWidget(lbl)

        row = QHBoxLayout()
        row.setSpacing(6)
        for label, command, color in ACTIONS:
            btn = QuickActionButton(label, command, color)
            btn.clicked.connect(lambda checked=False, cmd=command: self.action_triggered.emit(cmd))
            row.addWidget(btn)
        outer.addLayout(row)
