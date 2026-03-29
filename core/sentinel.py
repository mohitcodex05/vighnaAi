"""
core/sentinel.py — Vighna Sentinel (Self-Debugging AI)
Watches logs/vighna.log and analyzes tracebacks.
"""

import os
import re
import traceback
from datetime import datetime

LOG_FILE = os.path.join(os.path.dirname(__file__), "..", "logs", "vighna.log")


class Sentinel:
    """
    Background monitor that watches for exceptions.
    """

    def __init__(self, brain=None):
        self.brain = brain
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

    def log_exception(self, exc: Exception):
        """Append a traceback to the log file."""
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        tb = traceback.format_exc()
        entry = f"\n[{ts}] ERROR: {exc}\n{tb}\n{'='*60}\n"
        
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(entry)
        
        print(f"[Sentinel] Exception logged: {exc}")
        return tb

    def analyze_last_error(self) -> str:
        """Read the last error from the log and ask Groq for a fix."""
        if not os.path.exists(LOG_FILE):
            return "No errors found in logs."

        with open(LOG_FILE, "r", encoding="utf-8") as f:
            content = f.read()

        # Split by separator and get the last one
        errors = content.split('='*60)
        if len(errors) < 2:
            return "No detailed tracebacks found."
        
        last_error = errors[-2].strip()

        # Ask the brain (Groq) to analyze
        prompt = (
            "You are the Vighna Sentinel, a self-debugging AI system. "
            "I will provide an error traceback. Analyze it and tell me exactly what's wrong "
            "and how to fix it in 2-3 sentences. If it's a missing dependency, say so clearly.\n\n"
            f"ERROR TRACEBACK:\n{last_error}"
        )

        if self.brain:
            return self.brain._ai_fallback(prompt)
        return "Brain not connected to Sentinel."


def simulate_crash():
    """Test function for sentinel."""
    raise ValueError("Sentinel Test: This is a simulated crash.")
