"""
ui/styles/theme.py — Vighna Dark Theme Constants
"""

# ── Palette ─────────────────────────────────────────────────────────────────
BG_DARK       = "#0D0D0F"
BG_PANEL      = "#13131A"
BG_CARD       = "#1A1A27"
BG_INPUT      = "#1E1E2E"
BG_HOVER      = "#252538"

ACCENT_PRIMARY   = "#7C3AED"   # Vivid purple
ACCENT_SECONDARY = "#6D28D9"
ACCENT_GLOW      = "#A855F7"
ACCENT_BLUE      = "#3B82F6"
ACCENT_GREEN     = "#10B981"
ACCENT_RED       = "#EF4444"
ACCENT_ORANGE    = "#F59E0B"

TEXT_PRIMARY   = "#F1F5F9"
TEXT_SECONDARY = "#94A3B8"
TEXT_MUTED     = "#475569"

BORDER_COLOR   = "#2D2D44"
BUBBLE_USER    = "#3B1F6B"
BUBBLE_BOT     = "#1E1E2E"

# ── Typography ───────────────────────────────────────────────────────────────
FONT_FAMILY = "Segoe UI"
FONT_MONO   = "Consolas"

FONT_SIZE_XS  = 9
FONT_SIZE_SM  = 11
FONT_SIZE_MD  = 13
FONT_SIZE_LG  = 15
FONT_SIZE_XL  = 18
FONT_SIZE_XXL = 24

# ── Geometry ─────────────────────────────────────────────────────────────────
RADIUS_SM = 8
RADIUS_MD = 12
RADIUS_LG = 18
RADIUS_XL = 24

# ── Animations ───────────────────────────────────────────────────────────────
ANIM_FAST   = 150
ANIM_NORMAL = 300
ANIM_SLOW   = 600

# ── App Stylesheet ────────────────────────────────────────────────────────────
GLOBAL_STYLESHEET = f"""
    QWidget {{
        background-color: {BG_DARK};
        color: {TEXT_PRIMARY};
        font-family: {FONT_FAMILY};
        font-size: {FONT_SIZE_MD}px;
    }}
    QScrollBar:vertical {{
        background: {BG_PANEL};
        width: 6px;
        border-radius: 3px;
    }}
    QScrollBar::handle:vertical {{
        background: {ACCENT_PRIMARY};
        border-radius: 3px;
        min-height: 30px;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0;
    }}
    QScrollArea {{
        border: none;
    }}
    QLineEdit {{
        background: {BG_INPUT};
        border: 1.5px solid {BORDER_COLOR};
        border-radius: {RADIUS_MD}px;
        padding: 10px 14px;
        color: {TEXT_PRIMARY};
        font-size: {FONT_SIZE_MD}px;
    }}
    QLineEdit:focus {{
        border-color: {ACCENT_PRIMARY};
    }}
    QPushButton {{
        background: {ACCENT_PRIMARY};
        color: white;
        border: none;
        border-radius: {RADIUS_SM}px;
        padding: 8px 18px;
        font-size: {FONT_SIZE_MD}px;
        font-weight: bold;
    }}
    QPushButton:hover {{
        background: {ACCENT_GLOW};
    }}
    QPushButton:pressed {{
        background: {ACCENT_SECONDARY};
    }}
    QLabel {{
        background: transparent;
    }}
    QTextEdit {{
        background: {BG_INPUT};
        border: 1.5px solid {BORDER_COLOR};
        border-radius: {RADIUS_MD}px;
        padding: 10px;
        color: {TEXT_PRIMARY};
        font-size: {FONT_SIZE_MD}px;
    }}
    QListWidget {{
        background: transparent;
        border: none;
    }}
"""
