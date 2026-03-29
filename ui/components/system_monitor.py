"""
ui/components/system_monitor.py — Minimalist HUD for CPU/RAM usage
"""

import psutil
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

from ui.styles.theme import (
    BG_CARD, BORDER_COLOR, TEXT_PRIMARY, TEXT_SECONDARY,
    ACCENT_PRIMARY, ACCENT_BLUE, FONT_FAMILY, FONT_SIZE_XS, RADIUS_SM
)


class SystemMonitor(QWidget):
    """
    A small widget for the sidebar to show system health.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(210)
        self._build()
        
        # Update every 3 seconds
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_stats)
        self._timer.start(3000)
        self._update_stats()

    def _build(self):
        self.setStyleSheet(
            f"background: {BG_CARD}; border: 1px solid {BORDER_COLOR};"
            f"border-radius: {RADIUS_SM}px; padding: 6px;"
        )
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(6)

        header = QLabel("⚡ System HUD")
        header.setFont(QFont(FONT_FAMILY, FONT_SIZE_XS, QFont.Weight.Bold))
        header.setStyleSheet(f"color: {TEXT_SECONDARY}; background: transparent; border: none;")
        layout.addWidget(header)

        # CPU
        self._cpu_lbl = QLabel("CPU: 0%")
        self._cpu_lbl.setFont(QFont(FONT_FAMILY, 9))
        self._cpu_lbl.setStyleSheet("color: white; background: transparent; border: none;")
        layout.addWidget(self._cpu_lbl)

        self._cpu_bar = QProgressBar()
        self._cpu_bar.setTextVisible(False)
        self._cpu_bar.setFixedHeight(4)
        self._cpu_bar.setStyleSheet(self._bar_style(ACCENT_BLUE))
        layout.addWidget(self._cpu_bar)

        # RAM
        self._ram_lbl = QLabel("RAM: 0%")
        self._ram_lbl.setFont(QFont(FONT_FAMILY, 9))
        self._ram_lbl.setStyleSheet("color: white; background: transparent; border: none;")
        layout.addWidget(self._ram_lbl)

        self._ram_bar = QProgressBar()
        self._ram_bar.setTextVisible(False)
        self._ram_bar.setFixedHeight(4)
        self._ram_bar.setStyleSheet(self._bar_style(ACCENT_PRIMARY))
        layout.addWidget(self._ram_bar)

    def _bar_style(self, color: str) -> str:
        return f"""
            QProgressBar {{
                background: #1E1E2E;
                border: none;
                border-radius: 2px;
            }}
            QProgressBar::chunk {{
                background: {color};
                border-radius: 2px;
            }}
        """

    def _update_stats(self):
        try:
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            
            self._cpu_lbl.setText(f"CPU: {cpu}%")
            self._cpu_bar.setValue(int(cpu))
            
            self._ram_lbl.setText(f"RAM: {ram}%")
            self._ram_bar.setValue(int(ram))
        except Exception:
            pass
