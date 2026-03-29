import whisper
import sounddevice as sd
import numpy as np
import datetime

model = whisper.load_model("base")

SAMPLE_RATE = 16000
DURATION = 3

while True:
    print("🎤 Speak...")
    audio = sd.rec(int(DURATION * SAMPLE_RATE),
                   samplerate=SAMPLE_RATE,
                   channels=1,
                   dtype='float32')
    sd.wait()

    audio = audio.flatten()
    result = model.transcribe(audio)

    text = result["text"].lower().strip()
    print("Vighna heard:", text)

    # Vighna brain
    if "hello" in text:
        print("Vighna:", "Hello human")

    elif "time" in text:
        now = datetime.datetime.now().strftime("%H:%M")
        print("Vighna:", "The time is", now)

    elif "exit" in text:
        print("Vighna:", "Goodbye")
        break
