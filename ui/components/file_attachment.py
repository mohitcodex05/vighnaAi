"""
ui/components/file_attachment.py — PDF / Image upload widget with drag-and-drop
"""

import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog,
    QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QDragEnterEvent, QDropEvent

from ui.styles.theme import (
    BG_CARD, BG_HOVER, BORDER_COLOR, ACCENT_PRIMARY, ACCENT_GLOW,
    TEXT_PRIMARY, TEXT_SECONDARY, FONT_FAMILY, FONT_SIZE_SM, FONT_SIZE_XS,
    RADIUS_MD, RADIUS_SM, ACCENT_ORANGE
)

ACCEPTED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".bmp", ".webp", ".tiff"}


class FileAttachmentZone(QFrame):
    """
    Drag-and-drop zone for attaching a PDF or image.
    Emits file_attached(path) when a file is selected.
    """
    file_attached = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self._current_file: str | None = None
        self._build()

    def _build(self):
        self.setStyleSheet(
            f"background: {BG_CARD}; border: 2px dashed {BORDER_COLOR};"
            f"border-radius: {RADIUS_MD}px;"
        )
        self.setFixedHeight(90)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._icon = QLabel("📎")
        self._icon.setFont(QFont(FONT_FAMILY, 20))
        self._icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._icon.setStyleSheet("background: transparent;")
        layout.addWidget(self._icon)

        self._label = QLabel("Drop a PDF or image here, or click to browse")
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._label.setFont(QFont(FONT_FAMILY, FONT_SIZE_XS))
        self._label.setStyleSheet(f"color: {TEXT_SECONDARY}; background: transparent;")
        layout.addWidget(self._label)

        btn_row = QHBoxLayout()
        btn_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        browse_btn = QPushButton("Browse File")
        browse_btn.setStyleSheet(
            f"background: transparent; color: {ACCENT_GLOW}; border: 1px solid {ACCENT_PRIMARY};"
            f"border-radius: {RADIUS_SM}px; padding: 4px 14px; font-size: {FONT_SIZE_XS}px;"
        )
        browse_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        browse_btn.clicked.connect(self._browse)
        btn_row.addWidget(browse_btn)

        self._clear_btn = QPushButton("✕ Clear")
        self._clear_btn.setVisible(False)
        self._clear_btn.setStyleSheet(
            f"background: transparent; color: #EF4444; border: 1px solid #EF4444;"
            f"border-radius: {RADIUS_SM}px; padding: 4px 10px; font-size: {FONT_SIZE_XS}px;"
        )
        self._clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._clear_btn.clicked.connect(self._clear)
        btn_row.addWidget(self._clear_btn)

        layout.addLayout(btn_row)

    def _browse(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select File", "",
            "PDF & Images (*.pdf *.png *.jpg *.jpeg *.bmp *.webp *.tiff)"
        )
        if path:
            self._set_file(path)

    def _set_file(self, path: str):
        ext = os.path.splitext(path)[1].lower()
        if ext not in ACCEPTED_EXTENSIONS:
            self._label.setText("⚠️  Unsupported file type.")
            return
        self._current_file = path
        basename = os.path.basename(path)
        icon = "📕" if ext == ".pdf" else "🖼️"
        self._icon.setText(icon)
        self._label.setText(basename)
        self._label.setStyleSheet(f"color: {TEXT_PRIMARY}; background: transparent; font-size: {FONT_SIZE_XS}px;")
        self._clear_btn.setVisible(True)
        self.setStyleSheet(
            f"background: {BG_CARD}; border: 2px dashed {ACCENT_PRIMARY};"
            f"border-radius: {RADIUS_MD}px;"
        )
        self.file_attached.emit(path)

    def _clear(self):
        self._current_file = None
        self._icon.setText("📎")
        self._label.setText("Drop a PDF or image here, or click to browse")
        self._label.setStyleSheet(f"color: {TEXT_SECONDARY}; background: transparent;")
        self._clear_btn.setVisible(False)
        self.setStyleSheet(
            f"background: {BG_CARD}; border: 2px dashed {BORDER_COLOR};"
            f"border-radius: {RADIUS_MD}px;"
        )

    @property
    def current_file(self) -> str | None:
        return self._current_file

    # ── Drag & drop ───────────────────────────────────────────────────────
    def dragEnterEvent(self, e: QDragEnterEvent):
        if e.mimeData().hasUrls():
            e.acceptProposedAction()
            self.setStyleSheet(
                f"background: {BG_HOVER}; border: 2px dashed {ACCENT_GLOW};"
                f"border-radius: {RADIUS_MD}px;"
            )

    def dragLeaveEvent(self, e):
        self.setStyleSheet(
            f"background: {BG_CARD}; border: 2px dashed {BORDER_COLOR};"
            f"border-radius: {RADIUS_MD}px;"
        )

    def dropEvent(self, e: QDropEvent):
        urls = e.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            self._set_file(path)
