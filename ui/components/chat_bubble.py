"""
ui/components/chat_bubble.py — Message bubble widgets (ChatGPT-style)
"""

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QSizePolicy, QFrame
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QColor, QPalette
from ui.styles.theme import (
    BUBBLE_USER, BUBBLE_BOT, TEXT_PRIMARY, TEXT_SECONDARY,
    ACCENT_PRIMARY, BG_CARD, FONT_FAMILY, FONT_SIZE_MD, FONT_SIZE_XS,
    RADIUS_LG, RADIUS_MD
)


class ChatBubble(QWidget):
    def __init__(self, text: str, sender: str, timestamp: str = "", parent=None):
        super().__init__(parent)
        self.sender = sender   # "user" or "assistant"
        self._build(text, sender, timestamp)

    def _build(self, text: str, sender: str, timestamp: str):
        outer = QHBoxLayout(self)
        outer.setContentsMargins(12, 4, 12, 4)
        outer.setSpacing(0)

        bubble = QFrame()
        bubble.setObjectName("chatBubble")
        inner = QVBoxLayout(bubble)
        inner.setContentsMargins(14, 10, 14, 10)
        inner.setSpacing(4)

        # Sender label
        sender_label = QLabel("You" if sender == "user" else "✦ Vighna")
        sender_font = QFont(FONT_FAMILY, FONT_SIZE_XS, QFont.Weight.Bold)
        sender_label.setFont(sender_font)
        sender_label.setStyleSheet(
            f"color: {'#A78BFA' if sender == 'user' else '#10B981'};"
        )
        inner.addWidget(sender_label)

        # Message text
        msg = QLabel(text)
        msg.setWordWrap(True)
        msg.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        msg.setFont(QFont(FONT_FAMILY, FONT_SIZE_MD))
        msg.setStyleSheet(f"color: {TEXT_PRIMARY};")
        msg.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        inner.addWidget(msg)

        # Timestamp
        if timestamp:
            ts = QLabel(timestamp)
            ts.setFont(QFont(FONT_FAMILY, FONT_SIZE_XS - 1))
            ts.setStyleSheet(f"color: {TEXT_SECONDARY};")
            inner.addWidget(ts)

        # Style bubble
        if sender == "user":
            bubble.setStyleSheet(
                f"background-color: {BUBBLE_USER}; "
                f"border-radius: {RADIUS_LG}px {RADIUS_LG}px 4px {RADIUS_LG}px;"
                f"border: 1px solid #4C1D95;"
            )
            outer.addStretch()
            outer.addWidget(bubble)
        else:
            bubble.setStyleSheet(
                f"background-color: {BUBBLE_BOT}; "
                f"border-radius: {RADIUS_LG}px {RADIUS_LG}px {RADIUS_LG}px 4px;"
                f"border: 1px solid #2D2D44;"
            )
            outer.addWidget(bubble)
            outer.addStretch()

        bubble.setMaximumWidth(600)


class TypingIndicator(QWidget):
    """Animated '...' typing dots shown while Vighna is thinking."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)

        self._label = QLabel("✦ Vighna is thinking")
        self._label.setFont(QFont(FONT_FAMILY, FONT_SIZE_MD))
        self._label.setStyleSheet("color: #6D28D9;")
        layout.addWidget(self._label)
        layout.addStretch()

        self._dots = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(500)

    def _tick(self):
        self._dots = (self._dots + 1) % 4
        self._label.setText("✦ Vighna is thinking" + "." * self._dots)

    def stop(self):
        self._timer.stop()
