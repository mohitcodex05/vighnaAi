"""
ui/components/activity_timeline.py — Scrollable recent-action history panel
"""

from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from ui.styles.theme import (
    BG_CARD, BG_PANEL, BG_HOVER, BORDER_COLOR,
    ACCENT_PRIMARY, ACCENT_GREEN, ACCENT_ORANGE, TEXT_PRIMARY, TEXT_SECONDARY,
    FONT_FAMILY, FONT_SIZE_SM, FONT_SIZE_XS, RADIUS_MD, RADIUS_SM
)

# Map keyword → emoji icon
ACTION_ICONS = {
    "open":   "🚀",
    "close":  "❌",
    "web":    "🌐",
    "search": "🔍",
    "file":   "📄",
    "folder": "📁",
    "pdf":    "📕",
    "image":  "🖼️",
    "volume": "🔊",
    "plan":   "📋",
    "ai":     "🤖",
    "lock":   "🔒",
    "sleep":  "💤",
    "shot":   "📸",
}


def _icon_for(action: str) -> str:
    lc = action.lower()
    for kw, icon in ACTION_ICONS.items():
        if kw in lc:
            return icon
    return "⚡"


class ActivityItem(QFrame):
    def __init__(self, action: str, timestamp: str, parent=None):
        super().__init__(parent)
        self.setStyleSheet(
            f"background: {BG_CARD}; border-radius: {RADIUS_SM}px;"
            f"border: 1px solid {BORDER_COLOR};"
        )
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 7, 10, 7)
        layout.setSpacing(10)

        icon = QLabel(_icon_for(action))
        icon.setFixedWidth(24)
        icon.setFont(QFont(FONT_FAMILY, 14))
        icon.setStyleSheet("background: transparent;")
        layout.addWidget(icon)

        text = QLabel(action)
        text.setFont(QFont(FONT_FAMILY, FONT_SIZE_SM))
        text.setStyleSheet(f"color: {TEXT_PRIMARY}; background: transparent;")
        text.setWordWrap(True)
        text.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        layout.addWidget(text)

        ts = QLabel(timestamp)
        ts.setFont(QFont(FONT_FAMILY, FONT_SIZE_XS - 1))
        ts.setStyleSheet(f"color: {TEXT_SECONDARY}; background: transparent;")
        ts.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(ts)


class ActivityTimeline(QWidget):
    """
    Left-sidebar panel showing the last N actions taken by Vighna.
    Call add_action(text) to push a new entry to the top.
    """

    MAX_ITEMS = 50

    def __init__(self, parent=None):
        super().__init__(parent)
        self._items: list[ActivityItem] = []
        self._build()

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        header = QLabel("  📋  Activity")
        header.setFont(QFont(FONT_FAMILY, FONT_SIZE_SM, QFont.Weight.Bold))
        header.setStyleSheet(
            f"color: {TEXT_SECONDARY}; background: {BG_PANEL};"
            f"padding: 8px 6px; border-bottom: 1px solid {BORDER_COLOR};"
        )
        outer.addWidget(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("background: transparent; border: none;")

        self._container = QWidget()
        self._container.setStyleSheet("background: transparent;")
        self._list = QVBoxLayout(self._container)
        self._list.setContentsMargins(6, 6, 6, 6)
        self._list.setSpacing(4)
        self._list.addStretch()

        scroll.setWidget(self._container)
        outer.addWidget(scroll)

        # Empty state label
        self._empty = QLabel("No actions yet")
        self._empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty.setFont(QFont(FONT_FAMILY, FONT_SIZE_SM))
        self._empty.setStyleSheet(f"color: {TEXT_SECONDARY}; background: transparent; padding: 20px;")
        self._list.insertWidget(0, self._empty)

    def add_action(self, action: str):
        ts = datetime.now().strftime("%H:%M")
        item = ActivityItem(action, ts)

        # Remove empty label once we have items
        if not self._items:
            self._empty.setVisible(False)

        # Insert at top (before stretch)
        self._list.insertWidget(0, item)
        self._items.insert(0, item)

        # Prune old items
        while len(self._items) > self.MAX_ITEMS:
            old = self._items.pop()
            self._list.removeWidget(old)
            old.deleteLater()

    def clear(self):
        for item in self._items:
            self._list.removeWidget(item)
            item.deleteLater()
        self._items.clear()
        self._empty.setVisible(True)
