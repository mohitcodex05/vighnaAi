"""
main.py — Vighna Entry Point
Bootstrap: DB init → Login dialog → Launch UI → Background voice thread
"""

import sys
import os

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from database.db import init_db
from ui.components.login_dialog import LoginDialog
from ui.vighna_ui import VighnaUI
from ui.styles.theme import GLOBAL_STYLESHEET, FONT_FAMILY
from core.sentinel import Sentinel

def main():
    # ── Sentinel & Logging Setup ───────────────────────────────────────────
    log_dir = os.path.join(os.path.dirname(__file__), "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, "vighna.log")
    
    sentinel = Sentinel()
    
    # Redirect stdout/stderr to file for sentinel to watch
    log_file = open(log_path, "a", encoding="utf-8")
    # sys.stdout = log_file # Keep stdout for console visibility during dev
    sys.stderr = log_file

    try:
        # ── Bootstrapping ──────────────────────────────────────────────────────
        try:
            init_db()
        except Exception as e:
            sentinel.log_exception(e)
            print(f"[ERROR] Failed to initialize database: {e}")
            sys.exit(1)

        # ── Qt App ─────────────────────────────────────────────────────────────
        app = QApplication(sys.argv)
        app.setApplicationName("Vighna")
        app.setOrganizationName("Vighna AI")
        app.setStyleSheet(GLOBAL_STYLESHEET)

        # Set default font
        font = QFont(FONT_FAMILY, 13)
        app.setFont(font)

        # ── Login / Signup ─────────────────────────────────────────────────────
        user_id   = 0
        username  = "User"
        
        dialog = LoginDialog()
        
        # Center on screen
        screen = app.primaryScreen().availableGeometry()
        dialog.move(
            screen.center().x() - dialog.width()  // 2,
            screen.center().y() - dialog.height() // 2
        )

        result_holder = {}
        def on_login(uid: int, uname: str):
            result_holder["user_id"]  = uid
            result_holder["username"] = uname

        dialog.login_success.connect(on_login)

        rc = dialog.exec()

        # User closed dialog without logging in — allow guest mode
        if rc != LoginDialog.DialogCode.Accepted:
            reply = QMessageBox.question(
                None, "Continue as Guest?",
                "No account selected. Continue as a guest?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                sys.exit(0)
        else:
            user_id  = result_holder.get("user_id", 0)
            username = result_holder.get("username", "User")

        # ── Main Window ────────────────────────────────────────────────────────
        window = VighnaUI(user_id=user_id, username=username)
        window.show()

        sys.exit(app.exec())
    
    except Exception as e:
        sentinel.log_exception(e)
        raise e
    finally:
        log_file.close()

if __name__ == "__main__":
    main()
