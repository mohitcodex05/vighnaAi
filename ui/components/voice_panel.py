"""
ui/components/voice_panel.py — Animated microphone button with visual states
States: idle | listening | thinking | speaking
"""

import math
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton
from PySide6.QtCore import Qt, QTimer, Signal, QRect, QRectF
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QLinearGradient, QRadialGradient

from ui.styles.theme import (
    ACCENT_PRIMARY, ACCENT_GLOW, ACCENT_GREEN, ACCENT_BLUE, ACCENT_ORANGE,
    TEXT_SECONDARY, FONT_FAMILY, FONT_SIZE_XS, BG_CARD, BORDER_COLOR
)

# State constants
STATE_IDLE      = "idle"
STATE_LISTENING = "listening"
STATE_THINKING  = "thinking"
STATE_SPEAKING  = "speaking"


class MicCanvas(QWidget):
    """Custom painted mic button with animated rings."""

    clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(90, 90)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._state = STATE_IDLE
        self._phase = 0.0
        self._hovered = False

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(40)  # 25fps animation

    def set_state(self, state: str):
        self._state = state
        self.update()

    def _tick(self):
        self._phase += 0.12
        if self._phase > 2 * math.pi:
            self._phase -= 2 * math.pi
        self.update()

    def enterEvent(self, e):
        self._hovered = True
        self.update()

    def leaveEvent(self, e):
        self._hovered = False
        self.update()

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        cx, cy = self.width() // 2, self.height() // 2
        r = 32

        state = self._state
        phase = self._phase

        # Draw animated outer rings
        if state == STATE_LISTENING:
            for i in range(3):
                alpha = int(180 * (0.5 + 0.5 * math.sin(phase - i * 0.8)))
                ring_r = r + 8 + i * 9 + 5 * math.sin(phase - i)
                color = QColor(ACCENT_GLOW)
                color.setAlpha(alpha)
                pen = QPen(color, 2)
                p.setPen(pen)
                p.setBrush(Qt.BrushStyle.NoBrush)
                p.drawEllipse(QRectF(cx - ring_r, cy - ring_r, ring_r * 2, ring_r * 2))

        elif state == STATE_THINKING:
            alpha = int(120 + 60 * math.sin(phase * 2))
            glow = QColor(ACCENT_PRIMARY)
            glow.setAlpha(alpha)
            pen = QPen(glow, 3)
            p.setPen(pen)
            p.setBrush(Qt.BrushStyle.NoBrush)
            ring_r = r + 14
            p.drawEllipse(QRectF(cx - ring_r, cy - ring_r, ring_r * 2, ring_r * 2))

        elif state == STATE_SPEAKING:
            for i in range(4):
                wave_r = r + 8 + i * 8
                alpha = int(150 * abs(math.sin(phase * 1.5 + i * 0.6)))
                color = QColor(ACCENT_GREEN)
                color.setAlpha(alpha)
                pen = QPen(color, 1.5)
                p.setPen(pen)
                p.setBrush(Qt.BrushStyle.NoBrush)
                p.drawEllipse(QRectF(cx - wave_r, cy - wave_r, wave_r * 2, wave_r * 2))

        # Main circle background
        if state == STATE_IDLE:
            base = QColor("#1E1E2E") if not self._hovered else QColor(ACCENT_PRIMARY)
        elif state == STATE_LISTENING:
            base = QColor(ACCENT_PRIMARY)
        elif state == STATE_THINKING:
            base = QColor("#2D1B69")
        else:  # speaking
            base = QColor("#0D3B26")

        grad = QRadialGradient(cx, cy, r)
        grad.setColorAt(0, base.lighter(130))
        grad.setColorAt(1, base)

        p.setPen(QPen(QColor(ACCENT_GLOW if state != STATE_IDLE else BORDER_COLOR), 2))
        p.setBrush(QBrush(grad))
        p.drawEllipse(QRectF(cx - r, cy - r, r * 2, r * 2))

        # Mic icon
        mic_color = QColor("white")
        p.setPen(QPen(mic_color, 2.5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        p.setBrush(Qt.BrushStyle.NoBrush)

        # Mic body (rounded rect)
        mic_w, mic_h = 12, 18
        mx = cx - mic_w // 2
        my = cy - mic_h // 2 - 4
        p.setBrush(QBrush(mic_color))
        p.drawRoundedRect(QRectF(mx, my, mic_w, mic_h), 6, 6)

        # Mic arc
        p.setBrush(Qt.BrushStyle.NoBrush)
        arc_rect = QRectF(cx - 14, cy - 4, 28, 26)
        p.drawArc(arc_rect, 0, 180 * 16)

        # Stand line
        p.drawLine(cx, cy + 19, cx, cy + 24)
        p.drawLine(cx - 8, cy + 24, cx + 8, cy + 24)

        p.end()


class VoicePanel(QWidget):
    """Full voice panel: mic button + state label."""

    mic_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._canvas = MicCanvas()
        self._canvas.clicked.connect(self.mic_clicked.emit)
        layout.addWidget(self._canvas, alignment=Qt.AlignmentFlag.AlignCenter)

        self._label = QLabel("Click to speak")
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._label.setFont(QFont(FONT_FAMILY, FONT_SIZE_XS))
        self._label.setStyleSheet(f"color: {TEXT_SECONDARY}; background: transparent;")
        layout.addWidget(self._label)

    def set_state(self, state: str):
        self._canvas.set_state(state)
        labels = {
            STATE_IDLE:      "Click to speak",
            STATE_LISTENING: "🎙 Listening…",
            STATE_THINKING:  "⚡ Thinking…",
            STATE_SPEAKING:  "🔊 Speaking…",
        }
        self._label.setText(labels.get(state, ""))
        color_map = {
            STATE_IDLE:      TEXT_SECONDARY,
            STATE_LISTENING: ACCENT_GLOW,
            STATE_THINKING:  ACCENT_PRIMARY,
            STATE_SPEAKING:  ACCENT_GREEN,
        }
        self._label.setStyleSheet(
            f"color: {color_map.get(state, TEXT_SECONDARY)}; background: transparent;"
        )
