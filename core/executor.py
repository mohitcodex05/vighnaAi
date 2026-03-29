"""
core/executor.py — Executes planned action steps sequentially
Emits progress via an optional callback (used by UI)
"""

import subprocess
import time
from skills.open_app import open_app
from skills.web_actions import handle_web_intent, open_youtube, open_browser


class Executor:
    def __init__(self, tts_engine=None, on_action=None):
        """
        tts_engine: pyttsx3 engine (optional, for speaking results)
        on_action: callback(message: str) for UI activity timeline
        """
        self.tts = tts_engine
        self.on_action = on_action  # UI hook

    def _emit(self, message: str):
        if self.on_action:
            self.on_action(message)

    def _speak(self, text: str):
        if self.tts:
            try:
                self.tts.say(text)
                self.tts.runAndWait()
            except Exception:
                pass

    def run(self, steps: list[dict]) -> list[str]:
        """Execute a list of planned steps. Returns list of results."""
        results = []
        for step in steps:
            action = step.get("action")
            args = step.get("args", {})

            if action == "open_app":
                result = open_app(args.get("app_name", ""))
                self._emit(f"🚀 {result}")
                self._speak(result)
                results.append(result)
                time.sleep(1.2)  # brief pause between app launches

            elif action == "web":
                query = args.get("query", "")
                result = handle_web_intent(query) or open_browser()
                self._emit(f"🌐 {result}")
                results.append(result)

            elif action == "say":
                msg = args.get("message", "")
                self._emit(f"💬 {msg}")
                self._speak(msg)
                results.append(msg)

            elif action == "system":
                cmd = args.get("command", "")
                try:
                    subprocess.Popen(cmd, shell=True)
                    result = f"Executed: {cmd}"
                except Exception as e:
                    result = f"Error: {e}"
                self._emit(f"⚙️ {result}")
                results.append(result)

        return results
