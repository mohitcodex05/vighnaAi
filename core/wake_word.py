"""
core/wake_word.py — "Hey Vighna" wake-word detector
Uses simple energy + keyword matching (no external API needed).
Runs in a background thread and emits a callback when wake word is heard.
"""

import threading
import numpy as np
import sounddevice as sd
import warnings
warnings.filterwarnings("ignore")

SAMPLE_RATE = 16000
CHUNK_DURATION = 1.5   # seconds per chunk
ENERGY_THRESHOLD = 0.008
WAKE_PHRASES = ["hey vighna", "vighna", "hey vigna", "hay vighna"]


class WakeWordDetector:
    """
    Listens continuously in background.
    Calls `on_wake()` when wake phrase is detected.
    Falls back to simple Whisper transcription with a tiny model.
    """

    def __init__(self, on_wake, whisper_model=None):
        self.on_wake = on_wake
        self.model = whisper_model      # can share the main Whisper model
        self._running = False
        self._thread = None

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._thread.start()
        print("[WakeWord] Listening for 'Hey Vighna'…")

    def stop(self):
        self._running = False

    def _listen_loop(self):
        while self._running:
            try:
                audio = sd.rec(
                    int(CHUNK_DURATION * SAMPLE_RATE),
                    samplerate=SAMPLE_RATE,
                    channels=1,
                    dtype="float32",
                    blocking=True
                )
                audio = audio.flatten()
                energy = float(np.mean(np.abs(audio)))

                if energy < ENERGY_THRESHOLD:
                    continue        # silence → skip transcription

                if self.model is None:
                    continue

                result = self.model.transcribe(audio, language="en", fp16=False)
                text = result.get("text", "").lower().strip()

                if any(phrase in text for phrase in WAKE_PHRASES):
                    print(f"[WakeWord] Detected: '{text}'")
                    self.on_wake()

            except Exception as e:
                print(f"[WakeWord] Error: {e}")
