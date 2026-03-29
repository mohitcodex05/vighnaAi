"""
ui/vighna_ui.py — Main Window: ChatGPT-style chat with sidebar, voice panel, quick actions
"""

import os
import threading
from datetime import datetime

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QPushButton, QScrollArea, QFrame, QLineEdit, QSizePolicy,
    QSplitter, QToolButton, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt, Signal, QThread, QObject, QTimer, Slot
from PySide6.QtGui import QFont, QKeyEvent, QPixmap, QIcon

from ui.styles.theme import (
    GLOBAL_STYLESHEET, BG_DARK, BG_PANEL, BG_CARD, BG_INPUT, BG_HOVER,
    ACCENT_PRIMARY, ACCENT_GLOW, ACCENT_GREEN, TEXT_PRIMARY, TEXT_SECONDARY,
    BORDER_COLOR, FONT_FAMILY, FONT_SIZE_SM, FONT_SIZE_MD, FONT_SIZE_LG,
    FONT_SIZE_XL, FONT_SIZE_XXL, RADIUS_MD, RADIUS_LG, RADIUS_XL, ANIM_NORMAL
)
from ui.components.chat_bubble import ChatBubble, TypingIndicator
from ui.components.voice_panel import VoicePanel, STATE_IDLE, STATE_LISTENING, STATE_THINKING, STATE_SPEAKING
from ui.components.activity_timeline import ActivityTimeline
from ui.components.quick_actions import QuickActionsBar
from ui.components.file_attachment import FileAttachmentZone
from ui.components.system_monitor import SystemMonitor
from core.brain import Brain
from database.db import create_conversation


# ── Worker thread for Brain (keeps UI responsive) ─────────────────────────────
class BrainWorker(QObject):
    response_ready = Signal(str)
    action_emitted = Signal(str)
    error_raised   = Signal(str)

    def __init__(self, brain: Brain):
        super().__init__()
        self.brain = brain

    @Slot(str)
    def run(self, text: str):
        try:
            result = self.brain.process_text(text)
            self.response_ready.emit(result)
        except Exception as e:
            self.error_raised.emit(str(e))


# ── Voice worker (whisper in a background thread) ─────────────────────────────
class VoiceWorker(QObject):
    transcription_ready = Signal(str)
    finished            = Signal()

    def run(self):
        try:
            import sounddevice as sd
            import numpy as np
            import whisper

            model = whisper.load_model("base")
            samplerate = 16000
            duration = 5  # seconds

            audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype="float32")
            sd.wait()
            audio_flat = audio.flatten()
            result = model.transcribe(audio_flat, language="en")
            text = result.get("text", "").strip()
            if text:
                self.transcription_ready.emit(text)
        except Exception as e:
            self.transcription_ready.emit(f"[Voice error: {e}]")
        finally:
            self.finished.emit()


# ── Main Window ───────────────────────────────────────────────────────────────
class VighnaUI(QMainWindow):
    
    _run_brain = Signal(str)
    
    def __init__(self, user_id: int = 0, username: str = "User"):
        super().__init__()
        self.user_id = user_id
        self.username = username
        self._attached_file: str | None = None

        self.setWindowTitle("✦ Vighna")
        self.setMinimumSize(1100, 720)
        self.resize(1280, 800)
        self.setStyleSheet(GLOBAL_STYLESHEET)

        # Init DB conversation
        self.conversation_id = create_conversation(user_id) if user_id else 0

        # Brain
        self.brain = Brain(
            user_id=user_id,
            conversation_id=self.conversation_id,
            on_action=self._on_brain_action
        )

        # Brain worker thread
        self._brain_thread = QThread()
        self._brain_worker = BrainWorker(self.brain)
        self._brain_worker.moveToThread(self._brain_thread)
        self._run_brain.connect(self._brain_worker.run)
        self._brain_worker.response_ready.connect(self._on_response)
        self._brain_worker.error_raised.connect(lambda e: self._on_response(f"⚠️ {e}"))
        self._brain_thread.start()

        # Voice worker
        self._voice_thread: QThread | None = None
        self._voice_worker: VoiceWorker | None = None

        self._build_ui()

    # ─────────────────────────────────────────────────────────────────────
    # UI CONSTRUCTION
    # ─────────────────────────────────────────────────────────────────────
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Left Sidebar
        sidebar = self._make_sidebar()
        sidebar.setFixedWidth(230)
        root.addWidget(sidebar)

        # Main content area
        content = self._make_content()
        root.addWidget(content, stretch=1)

    # ── Sidebar ────────────────────────────────────────────────────────────
    def _make_sidebar(self) -> QWidget:
        sidebar = QWidget()
        sidebar.setStyleSheet(f"background: {BG_PANEL}; border-right: 1px solid {BORDER_COLOR};")
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Logo / brand
        brand = QLabel("✦ Vighna")
        brand.setAlignment(Qt.AlignmentFlag.AlignCenter)
        brand.setFont(QFont(FONT_FAMILY, FONT_SIZE_XL, QFont.Weight.Bold))
        brand.setStyleSheet(
            f"color: {ACCENT_GLOW}; padding: 20px 10px 10px 10px; background: transparent;"
        )
        layout.addWidget(brand)

        # User greeting
        self._user_label = QLabel(f"👤  {self.username}")
        self._user_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._user_label.setFont(QFont(FONT_FAMILY, FONT_SIZE_SM))
        self._user_label.setStyleSheet(f"color: {TEXT_SECONDARY}; padding: 4px; background: transparent;")
        layout.addWidget(self._user_label)

        sep = self._sep()
        layout.addWidget(sep)

        # Voice panel
        self._voice_panel = VoicePanel()
        self._voice_panel.mic_clicked.connect(self._toggle_voice)
        layout.addWidget(self._voice_panel)

        sep2 = self._sep()
        layout.addWidget(sep2)

        # Status badge
        self._status_badge = QLabel("🟢  Ready")
        self._status_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._status_badge.setFont(QFont(FONT_FAMILY, FONT_SIZE_XS if hasattr(self, 'FONT_SIZE_XS') else 10))
        self._status_badge.setStyleSheet(f"color: {ACCENT_GREEN}; padding: 6px; background: transparent;")
        layout.addWidget(self._status_badge)

        sep3 = self._sep()
        layout.addWidget(sep3)

        # System HUD
        self._hud = SystemMonitor()
        layout.addWidget(self._hud, alignment=Qt.AlignmentFlag.AlignCenter)

        sep4 = self._sep()
        layout.addWidget(sep4)

        # Activity timeline fills remaining space
        self._timeline = ActivityTimeline()
        layout.addWidget(self._timeline, stretch=1)

        # New chat button
        new_btn = QPushButton("＋  New Chat")
        new_btn.setStyleSheet(
            f"background: {BG_CARD}; color: {TEXT_PRIMARY}; border: 1px solid {BORDER_COLOR};"
            f"border-radius: 0; padding: 12px; font-size: {FONT_SIZE_SM}px; font-family: {FONT_FAMILY};"
        )
        new_btn.clicked.connect(self._new_chat)
        layout.addWidget(new_btn)

        return sidebar

    # ── Main content ────────────────────────────────────────────────────────
    def _make_content(self) -> QWidget:
        content = QWidget()
        content.setStyleSheet(f"background: {BG_DARK};")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Top bar
        topbar = self._make_topbar()
        layout.addWidget(topbar)

        # Chat scroll area
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setStyleSheet(f"background: {BG_DARK}; border: none;")

        self._chat_container = QWidget()
        self._chat_container.setStyleSheet(f"background: {BG_DARK};")
        self._chat_layout = QVBoxLayout(self._chat_container)
        self._chat_layout.setContentsMargins(0, 16, 0, 16)
        self._chat_layout.setSpacing(4)
        self._chat_layout.addStretch()

        self._scroll.setWidget(self._chat_container)
        layout.addWidget(self._scroll, stretch=1)

        # File attachment (hidden by default, shown when attach button is toggled)
        self._attach_zone = FileAttachmentZone()
        self._attach_zone.setVisible(False)
        self._attach_zone.file_attached.connect(self._on_file_attached)
        layout.addWidget(self._attach_zone)

        # Quick actions
        self._quick = QuickActionsBar()
        self._quick.action_triggered.connect(self._send_text)
        layout.addWidget(self._quick)

        # Input area
        input_bar = self._make_input_bar()
        layout.addWidget(input_bar)

        # Welcome message
        self._add_bubble("Hey! I'm **Vighna**, your AI assistant. Type a message, use voice, or attach a file to get started.", "assistant")

        return content

    def _make_topbar(self) -> QWidget:
        bar = QWidget()
        bar.setFixedHeight(52)
        bar.setStyleSheet(
            f"background: {BG_PANEL}; border-bottom: 1px solid {BORDER_COLOR};"
        )
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(20, 0, 20, 0)

        title = QLabel("Conversation")
        title.setFont(QFont(FONT_FAMILY, FONT_SIZE_LG, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {TEXT_PRIMARY}; background: transparent;")
        layout.addWidget(title)
        layout.addStretch()

        heal_btn = QPushButton("🩹 Self-Heal")
        heal_btn.setStyleSheet(
            f"background: transparent; color: {ACCENT_GLOW}; border: 1px solid {ACCENT_PRIMARY};"
            f"border-radius: 6px; padding: 6px 14px; font-size: 11px; font-family: {FONT_FAMILY};"
        )
        heal_btn.clicked.connect(self._do_self_heal)
        layout.addWidget(heal_btn)

        export_btn = QPushButton("📤 Export PDF")
        export_btn.setStyleSheet(
            f"background: transparent; color: {TEXT_SECONDARY}; border: 1px solid {BORDER_COLOR};"
            f"border-radius: 6px; padding: 6px 14px; font-size: 11px; font-family: {FONT_FAMILY};"
        )
        export_btn.clicked.connect(self._export_chat)
        layout.addWidget(export_btn)

        clear_btn = QPushButton("🗑 Clear")
        clear_btn.setStyleSheet(
            f"background: transparent; color: {TEXT_SECONDARY}; border: 1px solid {BORDER_COLOR};"
            f"border-radius: 6px; padding: 6px 14px; font-size: 11px; font-family: {FONT_FAMILY};"
        )
        clear_btn.clicked.connect(self._clear_chat)
        layout.addWidget(clear_btn)

        return bar

    def _make_input_bar(self) -> QWidget:
        bar = QWidget()
        bar.setStyleSheet(
            f"background: {BG_PANEL}; border-top: 1px solid {BORDER_COLOR};"
        )
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(16, 10, 16, 10)
        layout.setSpacing(8)

        # Attach toggle
        self._attach_btn = QToolButton()
        self._attach_btn.setText("📎")
        self._attach_btn.setFixedSize(44, 44)
        self._attach_btn.setCheckable(True)
        self._attach_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._attach_btn.setStyleSheet(
            f"QToolButton {{ background: {BG_CARD}; border: 1px solid {BORDER_COLOR};"
            f"border-radius: 22px; font-size: 18px; }}"
            f"QToolButton:checked {{ background: {ACCENT_PRIMARY}; border-color: {ACCENT_GLOW}; }}"
        )
        self._attach_btn.toggled.connect(self._attach_zone.setVisible)
        layout.addWidget(self._attach_btn)

        # Text input
        self._input = QLineEdit()
        self._input.setPlaceholderText("Ask Vighna anything… (Enter to send, Shift+Enter for new line)")
        self._input.setFixedHeight(44)
        self._input.setStyleSheet(
            f"background: {BG_INPUT}; border: 1.5px solid {BORDER_COLOR};"
            f"border-radius: 22px; padding: 0 18px; color: {TEXT_PRIMARY};"
            f"font-size: {FONT_SIZE_MD}px; font-family: {FONT_FAMILY};"
        )
        self._input.returnPressed.connect(self._on_enter)
        layout.addWidget(self._input, stretch=1)

        # Send button
        send_btn = QPushButton("➤")
        send_btn.setFixedSize(44, 44)
        send_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        send_btn.setStyleSheet(
            f"background: qlineargradient(x1:0,y1:0,x2:1,y2:1,"
            f"stop:0 {ACCENT_PRIMARY}, stop:1 {ACCENT_GLOW});"
            f"color: white; border: none; border-radius: 22px; font-size: 16px;"
        )
        send_btn.clicked.connect(self._on_enter)
        layout.addWidget(send_btn)

        return bar

    def _sep(self) -> QFrame:
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet(f"background: {BORDER_COLOR}; max-height: 1px; border: none;")
        return line

    # ─────────────────────────────────────────────────────────────────────
    # CHAT LOGIC
    # ─────────────────────────────────────────────────────────────────────
    def _on_enter(self):
        text = self._input.text().strip()
        if not text and not self._attached_file:
            return
        self._input.clear()
        self._send_text(text)

    def _send_text(self, text: str):
        if not text and not self._attached_file:
            return

        # If file attached, prepend context
        if self._attached_file:
            file_basename = os.path.basename(self._attached_file)
            display_text = f"[📎 {file_basename}] {text}" if text else f"Analyze this file: {file_basename}"
            self._add_bubble(display_text, "user")
            self._run_brain_with_file(self._attached_file, text or "Tell me about this file.")
            self._attached_file = None
            self._attach_zone._clear()
            self._attach_btn.setChecked(False)
        else:
            self._add_bubble(text, "user")
            self._set_thinking(True)
            self._run_brain.emit(text)

    def _run_brain_with_file(self, path: str, question: str):
        self._set_thinking(True)
        ext = os.path.splitext(path)[1].lower()
        def worker():
            try:
                if ext == ".pdf":
                    result = self.brain.answer_pdf(path, question)
                else:
                    result = self.brain.analyze_image(path, question)
                self._on_response(result)
            except Exception as e:
                self._on_response(f"⚠️ Could not process file: {e}")
        threading.Thread(target=worker, daemon=True).start()

    @Slot(str)
    def _on_response(self, text: str):
        self._set_thinking(False)
        if text == "VIGHNA_EXIT":
            self.close()
            return
        self._add_bubble(text, "assistant")
        self._timeline.add_action(text[:60] + ("…" if len(text) > 60 else ""))

    def _on_brain_action(self, action: str):
        """Called from brain's on_action callback (may be from non-GUI thread)."""
        QTimer.singleShot(0, lambda: self._timeline.add_action(action))
        QTimer.singleShot(0, lambda: self._set_status(action))

    def _add_bubble(self, text: str, sender: str):
        ts = datetime.now().strftime("%H:%M")
        bubble = ChatBubble(text, sender, ts)
        self._chat_layout.insertWidget(self._chat_layout.count() - 1, bubble)
        QTimer.singleShot(50, self._scroll_to_bottom)

    def _scroll_to_bottom(self):
        self._scroll.verticalScrollBar().setValue(
            self._scroll.verticalScrollBar().maximum()
        )

    def _set_thinking(self, thinking: bool):
        if thinking:
            self._typing = TypingIndicator()
            self._chat_layout.insertWidget(self._chat_layout.count() - 1, self._typing)
            QTimer.singleShot(50, self._scroll_to_bottom)
            self._status_badge.setText("🟡  Thinking…")
            self._status_badge.setStyleSheet(f"color: #F59E0B; padding: 6px; background: transparent;")
            self._voice_panel.set_state(STATE_THINKING)
        else:
            if hasattr(self, "_typing") and self._typing:
                self._typing.stop()
                self._chat_layout.removeWidget(self._typing)
                self._typing.deleteLater()
                self._typing = None
            self._set_status("Ready")
            self._voice_panel.set_state(STATE_IDLE)

    def _set_status(self, msg: str):
        self._status_badge.setText(f"🟢  {msg}")
        self._status_badge.setStyleSheet(f"color: {ACCENT_GREEN}; padding: 6px; background: transparent;")

    # ─────────────────────────────────────────────────────────────────────
    # VOICE
    # ─────────────────────────────────────────────────────────────────────
    def _toggle_voice(self):
        if self._voice_thread and self._voice_thread.isRunning():
            return  # already recording
        self._voice_panel.set_state(STATE_LISTENING)
        self._set_status("Listening…")

        self._voice_thread = QThread()
        self._voice_worker = VoiceWorker()
        self._voice_worker.moveToThread(self._voice_thread)
        self._voice_thread.started.connect(self._voice_worker.run)
        self._voice_worker.transcription_ready.connect(self._on_transcription)
        self._voice_worker.finished.connect(self._voice_thread.quit)
        self._voice_thread.start()

    @Slot(str)
    def _on_transcription(self, text: str):
        self._voice_panel.set_state(STATE_SPEAKING)
        if text and not text.startswith("[Voice error"):
            self._input.setText(text)
            self._send_text(text)
        else:
            self._set_thinking(False)
            if text:
                self._add_bubble(text, "assistant")

    # ─────────────────────────────────────────────────────────────────────
    # FILE ATTACHMENT
    # ─────────────────────────────────────────────────────────────────────
    def _on_file_attached(self, path: str):
        self._attached_file = path
        self._input.setPlaceholderText(f"Ask about: {os.path.basename(path)}")

    # ─────────────────────────────────────────────────────────────────────
    # UTILITIES
    # ─────────────────────────────────────────────────────────────────────
    def _new_chat(self):
        # Clear chat bubbles
        for i in reversed(range(self._chat_layout.count() - 1)):
            item = self._chat_layout.itemAt(i)
            if item and item.widget():
                item.widget().deleteLater()
        self._timeline.clear()
        self.conversation_id = create_conversation(self.user_id) if self.user_id else 0
        self.brain.conversation_id = self.conversation_id
        self._add_bubble("New chat started. How can I help?", "assistant")

    def _clear_chat(self):
        self._new_chat()

    def _do_self_heal(self):
        """Ask Sentinel to analyze the last error and try to fix it."""
        from core.sentinel import Sentinel
        sentinel = Sentinel(brain=self.brain)
        analysis = sentinel.analyze_last_error()
        
        reply = QMessageBox.question(
            self, "Vighna Sentinel Analysis",
            f"Sentinel found this issue:\n\n{analysis}\n\nShould I attempt a self-repair?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            from skills.self_fix import handle_module_error
            # Try to fix if it's a module error
            # In a real app, we'd read the log again or pass the traceback
            with open(os.path.join(os.path.dirname(__file__), "..", "logs", "vighna.log"), "r") as f:
                logs = f.read()
            
            result = handle_module_error(logs)
            if result:
                self._add_bubble(f"🛡️ Sentinel: {result}", "assistant")
            else:
                self._add_bubble("🛡️ Sentinel: I couldn't find an automatic fix for this issue.", "assistant")

    def _export_chat(self):
        try:
            from reportlab.pdfgen import canvas as rl_canvas
            from reportlab.lib.pagesizes import A4

            path, _ = QFileDialog.getSaveFileName(self, "Save Chat as PDF", "vighna_chat.pdf", "PDF (*.pdf)")
            if not path:
                return

            c = rl_canvas.Canvas(path, pagesize=A4)
            w, h = A4
            y = h - 50
            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, y, "Vighna Chat Export")
            y -= 30
            c.setFont("Helvetica", 11)

            # Walk all chat bubbles
            for i in range(self._chat_layout.count()):
                item = self._chat_layout.itemAt(i)
                if item and isinstance(item.widget(), ChatBubble):
                    bubble: ChatBubble = item.widget()
                    # Get text from the QLabel inside
                    sender = "You" if bubble.sender == "user" else "Vighna"
                    try:
                        inner_layout = bubble.layout().itemAt(0).widget().layout()
                        msg_widget = inner_layout.itemAt(1).widget()
                        text = msg_widget.text()
                    except Exception:
                        text = ""
                    line = f"[{sender}]: {text}"
                    # Word wrap
                    words = line.split()
                    row = ""
                    for word in words:
                        if c.stringWidth(row + word + " ", "Helvetica", 11) < w - 100:
                            row += word + " "
                        else:
                            c.drawString(50, y, row.strip())
                            y -= 16
                            if y < 60:
                                c.showPage()
                                y = h - 50
                                c.setFont("Helvetica", 11)
                            row = word + " "
                    if row.strip():
                        c.drawString(50, y, row.strip())
                        y -= 24
                    if y < 60:
                        c.showPage()
                        y = h - 50
                        c.setFont("Helvetica", 11)

            c.save()
            self._add_bubble(f"✅ Chat exported to: {path}", "assistant")
        except ImportError:
            self._add_bubble("⚠️ Install `reportlab` to export PDFs: `pip install reportlab`", "assistant")
        except Exception as e:
            self._add_bubble(f"⚠️ Export failed: {e}", "assistant")

    def closeEvent(self, e):
        if self._brain_thread.isRunning():
            self._brain_thread.quit()
            self._brain_thread.wait(2000)
        super().closeEvent(e)
