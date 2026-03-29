import webbrowser
import subprocess
import psutil
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

import whisper
import sounddevice as sd
import numpy as np
from groq import Groq
import pyttsx3

from core.session_memory import SessionMemory
from core.context_resolver import is_follow_up


# =====================
# CONFIG
# =====================
AI_NAME = "Vighna"
persona = "friend"

SAMPLE_RATE = 16000
DURATION = 5


# =====================
# UTILITIES
# =====================
def detect_mood(audio):
    energy = np.mean(np.abs(audio))
    if energy < 0.01:
        return "calm"
    elif energy < 0.03:
        return "normal"
    elif energy < 0.06:
        return "excited"
    else:
        return "stressed"


def normalize_app_name(text):
    text = text.lower().strip()
    for word in ["app", "application", "program", "software"]:
        text = text.replace(word, "")
    return " ".join(text.split())


def resolve_app(user_app, registry):
    user_app = normalize_app_name(user_app)

    if user_app in registry:
        return user_app

    for key in registry:
        if user_app.replace(" ", "") in key or key in user_app.replace(" ", ""):
            return key

    return None


# =====================
# APP REGISTRY (SAFE)
# =====================
APP_REGISTRY = {
    "chrome": {
        "path": "chrome.exe",
        "process": "chrome.exe"
    },
    "notepad": {
        "path": "notepad.exe",
        "process": "notepad.exe"
    },
    "vscode": {
        "path": "C:\\Users\\ACER\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe",
        "process": "code.exe"
    },
    "calculator": {
        "path": "calc.exe",
        "process": "CalculatorApp.exe",
        "type": "uwp"
    }
}


# =====================
# INIT SYSTEMS
# =====================
import os
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


model = whisper.load_model("base")

engine = pyttsx3.init()
engine.setProperty("rate", 170)

memory = SessionMemory()

conversation = [
    {
        "role": "system",
        "content": "You are Vighna, a helpful voice assistant. Respond clearly and concisely."
    }
]

print("🤖 Vighna is online. Say something!")
    # Normalize common Windows names


def open_any_app(app_name):
    # Try normal Windows start
    try:
        subprocess.Popen(
            ["cmd", "/c", "start", "", app_name],
            shell=True
        )
        return True
    except Exception:
        pass

    # Try explorer (for file explorer, folders)
    try:
        subprocess.Popen(["explorer", app_name])
        return True
    except Exception:
        pass

    # Try UWP AppsFolder (Store apps like WhatsApp)
    try:
        subprocess.Popen(
            ["cmd", "/c", "start", "shell:AppsFolder"],
            shell=True
        )
        return True
    except Exception:
        pass

    return False


# =====================
# MAIN LOOP
# =====================
while True:
    print("🎤 Listening...")

    audio = sd.rec(
        int(DURATION * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="float32",
        blocking=True
    )

    audio = audio.flatten()
    result = model.transcribe(audio, language="en")
    user_text = result["text"].strip()

    if len(user_text) < 2:
        print("❌ Too quiet")
        continue

    print("You:", user_text)
    clean_text = user_text.lower().strip(" .!?")

    # =====================
    # FOLLOW-UP
    # =====================
    if is_follow_up(clean_text) and memory.last_response:
        print(f"{AI_NAME}:", memory.last_response)
        engine.say(memory.last_response)
        engine.runAndWait()
        continue
    # =====================
    # WEB INTENTS (browser / youtube)
    # =====================

    # Open browser / Google
    if "open browser" in clean_text or "open google" in clean_text:
        webbrowser.open("https://www.google.com")
        response = "Opening browser"

        print(f"{AI_NAME}:", response)
        engine.say(response)
        engine.runAndWait()
        continue


    # Open YouTube
    if "open youtube" in clean_text:
        webbrowser.open("https://www.youtube.com")
        response = "Opening YouTube"

        print(f"{AI_NAME}:", response)
        engine.say(response)
        engine.runAndWait()
        continue
# =====================
# PLAY ON YOUTUBE (natural speech)
# =====================
    if "play" in clean_text and "youtube" in clean_text:
        query = clean_text.replace("play", "").replace("on youtube", "").replace("youtube", "").strip()

        if query == "":
            webbrowser.open("https://www.youtube.com")
            response = "Opening YouTube"
        else:
            url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
            webbrowser.open(url)
            response = f"Playing {query} on YouTube"

        print(f"{AI_NAME}:", response)
        engine.say(response)
        engine.runAndWait()
        continue
    if clean_text in ["exit", "quit", "stop", "goodbye"]:
        print(f"{AI_NAME}: Goodbye 👋")
        engine.say("Goodbye")
        engine.runAndWait()
        break
    # =====================
    # CLOSE LAST OPENED APP
    # =====================
    if clean_text in ["close it", "close that", "close this"]:
        if not memory.topic:
            response = "I don't know what to close"
        else:
            app_name = memory.topic

            try:
                subprocess.Popen(
                    ["cmd", "/c", "taskkill", "/IM", app_name, "/F"],
                    shell=True
                )
                response = f"Closed {app_name}"
            except Exception:
                response = f"Couldn't close {app_name}"

        print(f"{AI_NAME}:", response)
        engine.say(response)
        engine.runAndWait()
        continue

    # =====================
    # UNIVERSAL APP OPEN (NO JUDGMENT)
    # =====================
    if clean_text.startswith("open ") and len(clean_text.split()) > 1:
        app_name = clean_text.replace("open ", "", 1).strip()

        # normalize common Windows names
        if app_name == "file explorer":
            app_name = "explorer"

        if app_name == "":
            continue

        opened = open_any_app(app_name)

        if opened:
            response = f"Opening {app_name}"
        else:
            response = f"Couldn't open {app_name}"

        print(f"{AI_NAME}:", response)
        engine.say(response)
        engine.runAndWait()
        continue




    # =====================
    # CLOSE APP (REAL)
    # =====================
    if clean_text.startswith("close "):
        raw_app = clean_text.replace("close ", "").strip()
        app = resolve_app(raw_app, APP_REGISTRY)

        if not app:
            response = f"I don't have permission to close {raw_app}"

        else:
            app_info = APP_REGISTRY[app]

            # UWP app (Calculator)
            if app_info.get("type") == "uwp":
                subprocess.run(
                    ["taskkill", "/IM", app_info["process"], "/F"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    shell=True
                )
                subprocess.run(
                    ["taskkill", "/IM", "ApplicationFrameHost.exe", "/F"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    shell=True
                )
                response = f"{app} closed"

            # Normal apps
            else:
                closed = False
                for proc in psutil.process_iter(["name"]):
                    try:
                        if proc.info["name"] and app_info["process"] in proc.info["name"].lower():
                            proc.terminate()
                            closed = True
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass

                response = f"{app} closed" if closed else f"{app} is not running"

            memory.update(intent="close_app", topic=app, response=response)

        print(f"{AI_NAME}:", response)
        engine.say(response)
        engine.runAndWait()
        continue

    # =====================
    
    # =====================
# NATURAL BROWSER / YOUTUBE INTENTS
# =====================

    # Play something on YouTube
    if "play" in clean_text:
        query = clean_text.replace("play", "").strip()

        if query == "" or query == "youtube":
            webbrowser.open("https://www.youtube.com")
            response = "Opening YouTube"
        else:
            url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
            webbrowser.open(url)
            response = f"Playing {query} on YouTube"

            print(f"{AI_NAME}:", response)
            engine.say(response)
            engine.runAndWait()
            continue


    # Open browser / google
    if "open browser" in clean_text or "open google" in clean_text:
        webbrowser.open("https://www.google.com")
        response = "Opening browser"

        print(f"{AI_NAME}:", response)
        engine.say(response)
        engine.runAndWait()
        continue

    # =====================
    # AI FALLBACK
    # =====================
    conversation.append({"role": "user", "content": user_text})

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=conversation
    )

    reply = response.choices[0].message.content
    conversation.append({"role": "assistant", "content": reply})

    print(f"{AI_NAME}:", reply)
    engine.say(reply)
    engine.runAndWait()

    memory.update(response=reply)
