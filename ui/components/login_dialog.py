"""
ui/components/login_dialog.py — Login & Signup Modal Dialog for Vighna
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTabWidget, QWidget, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve, QRect
from PySide6.QtGui import QFont, QColor, QPainter, QLinearGradient

from auth.auth import login, signup
from ui.styles.theme import (
    BG_DARK, BG_PANEL, BG_CARD, BG_INPUT, ACCENT_PRIMARY, ACCENT_GLOW,
    TEXT_PRIMARY, TEXT_SECONDARY, BORDER_COLOR, FONT_FAMILY,
    FONT_SIZE_MD, FONT_SIZE_LG, FONT_SIZE_XL, FONT_SIZE_XXL,
    RADIUS_MD, RADIUS_LG, ACCENT_RED, ACCENT_GREEN
)


class LoginDialog(QDialog):
    """
    Shown at startup. Emits login_success(user_id, username) on success.
    """
    login_success = Signal(int, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Vighna — Sign In")
        self.setFixedSize(420, 540)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._drag_pos = None
        self._build_ui()

    # ── drag support ──────────────────────────────────────────────────────
    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = e.globalPosition().toPoint()

    def mouseMoveEvent(self, e):
        if self._drag_pos:
            delta = e.globalPosition().toPoint() - self._drag_pos
            self.move(self.pos() + delta)
            self._drag_pos = e.globalPosition().toPoint()

    def mouseReleaseEvent(self, e):
        self._drag_pos = None

    # ── UI ────────────────────────────────────────────────────────────────
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        card = QFrame()
        card.setStyleSheet(
            f"background: {BG_PANEL}; border-radius: {RADIUS_LG}px;"
            f"border: 1.5px solid {BORDER_COLOR};"
        )
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(36, 36, 36, 36)
        card_layout.setSpacing(16)

        # Close button
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(28, 28)
        close_btn.setStyleSheet(
            f"background: transparent; color: {TEXT_SECONDARY}; border: none; font-size: 14px;"
            f"border-radius: 14px;"
        )
        close_btn.clicked.connect(self.reject)
        close_row = QHBoxLayout()
        close_row.addStretch()
        close_row.addWidget(close_btn)
        card_layout.addLayout(close_row)

        # Logo / title
        logo = QLabel("✦ Vighna")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setFont(QFont(FONT_FAMILY, FONT_SIZE_XXL, QFont.Weight.Bold))
        logo.setStyleSheet(f"color: {ACCENT_GLOW}; background: transparent;")
        card_layout.addWidget(logo)

        tagline = QLabel("Your intelligent AI assistant")
        tagline.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tagline.setFont(QFont(FONT_FAMILY, FONT_SIZE_MD))
        tagline.setStyleSheet(f"color: {TEXT_SECONDARY}; background: transparent;")
        card_layout.addWidget(tagline)
        card_layout.addSpacing(8)

        # Tab widget
        tabs = QTabWidget()
        tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: none;
                background: transparent;
            }}
            QTabBar::tab {{
                background: {BG_CARD};
                color: {TEXT_SECONDARY};
                padding: 10px 28px;
                font-size: {FONT_SIZE_MD}px;
                font-family: {FONT_FAMILY};
                border-radius: 8px 8px 0 0;
                margin-right: 4px;
            }}
            QTabBar::tab:selected {{
                background: {ACCENT_PRIMARY};
                color: white;
            }}
        """)
        tabs.addTab(self._make_login_tab(), "Sign In")
        tabs.addTab(self._make_signup_tab(), "Create Account")
        card_layout.addWidget(tabs)

        root.addWidget(card)

    def _field(self, placeholder: str, echo: bool = False) -> QLineEdit:
        f = QLineEdit()
        f.setPlaceholderText(placeholder)
        f.setFixedHeight(44)
        if echo:
            f.setEchoMode(QLineEdit.EchoMode.Password)
        f.setStyleSheet(
            f"background: {BG_INPUT}; border: 1.5px solid {BORDER_COLOR};"
            f"border-radius: {RADIUS_MD}px; padding: 0 14px;"
            f"color: {TEXT_PRIMARY}; font-size: {FONT_SIZE_MD}px;"
            f"font-family: {FONT_FAMILY};"
        )
        return f

    def _btn(self, text: str) -> QPushButton:
        b = QPushButton(text)
        b.setFixedHeight(46)
        b.setStyleSheet(
            f"background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            f"stop:0 {ACCENT_PRIMARY}, stop:1 {ACCENT_GLOW});"
            f"color: white; border: none; border-radius: {RADIUS_MD}px;"
            f"font-size: {FONT_SIZE_MD}px; font-weight: bold; font-family: {FONT_FAMILY};"
        )
        b.setCursor(Qt.CursorShape.PointingHandCursor)
        return b

    def _make_login_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(12)
        layout.setContentsMargins(0, 16, 0, 0)

        self._login_user = self._field("Username")
        self._login_pass = self._field("Password", echo=True)
        self._login_err = QLabel()
        self._login_err.setStyleSheet(f"color: {ACCENT_RED}; background: transparent; font-size: 11px;")
        self._login_err.setWordWrap(True)
        login_btn = self._btn("Sign In")
        login_btn.clicked.connect(self._do_login)

        layout.addWidget(self._login_user)
        layout.addWidget(self._login_pass)
        layout.addWidget(self._login_err)
        layout.addWidget(login_btn)
        layout.addStretch()
        return w

    def _make_signup_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(12)
        layout.setContentsMargins(0, 16, 0, 0)

        self._signup_user = self._field("Choose a username")
        self._signup_pass = self._field("Choose a password", echo=True)
        self._signup_pass2 = self._field("Confirm password", echo=True)
        self._signup_err = QLabel()
        self._signup_err.setStyleSheet(f"color: {ACCENT_RED}; background: transparent; font-size: 11px;")
        self._signup_err.setWordWrap(True)
        signup_btn = self._btn("Create Account")
        signup_btn.clicked.connect(self._do_signup)

        layout.addWidget(self._signup_user)
        layout.addWidget(self._signup_pass)
        layout.addWidget(self._signup_pass2)
        layout.addWidget(self._signup_err)
        layout.addWidget(signup_btn)
        layout.addStretch()
        return w

    # ── Auth actions ──────────────────────────────────────────────────────
    def _do_login(self):
        self._login_err.clear()
        result = login(self._login_user.text(), self._login_pass.text())
        if result["ok"]:
            self.login_success.emit(result["user_id"], result["username"])
            self.accept()
        else:
            self._login_err.setText(result["error"])

    def _do_signup(self):
        self._signup_err.clear()
        if self._signup_pass.text() != self._signup_pass2.text():
            self._signup_err.setText("Passwords do not match.")
            return
        result = signup(self._signup_user.text(), self._signup_pass.text())
        if result["ok"]:
            self.login_success.emit(result["user_id"], result["username"])
            self.accept()
        else:
            self._signup_err.setText(result["error"])
