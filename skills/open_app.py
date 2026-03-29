"""
skills/open_app.py — App open/close skill
Migrated & extended from jarvis_groq.py
"""

import os
import subprocess
import psutil


# ── App Registry (extend as needed) ────────────────────────────────────────
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
        "path": r"C:\Users\ACER\AppData\Local\Programs\Microsoft VS Code\Code.exe",
        "process": "code.exe"
    },
    "calculator": {
        "path": "calc.exe",
        "process": "CalculatorApp.exe",
        "type": "uwp"
    },
    "explorer": {
        "path": "explorer.exe",
        "process": "explorer.exe"
    },
    "spotify": {
        "path": r"C:\Users\ACER\AppData\Roaming\Spotify\Spotify.exe",
        "process": "Spotify.exe"
    },
    "discord": {
        "path": r"C:\Users\ACER\AppData\Local\Discord\app-*\Discord.exe",
        "process": "Discord.exe"
    },
    "paint": {
        "path": "mspaint.exe",
        "process": "mspaint.exe"
    },
    "word": {
        "path": "winword.exe",
        "process": "WINWORD.EXE"
    },
    "excel": {
        "path": "excel.exe",
        "process": "EXCEL.EXE"
    },
    "task manager": {
        "path": "taskmgr.exe",
        "process": "Taskmgr.exe"
    },
    "whatsapp": {
        "path": "shell:AppsFolder\\WhatsApp",
        "process": "WhatsApp.exe",
        "type": "uwp"
    },
}

FOLDER_SHORTCUTS = {
    "downloads": os.path.expandvars(r"%USERPROFILE%\Downloads"),
    "desktop":   os.path.expandvars(r"%USERPROFILE%\Desktop"),
    "documents": os.path.expandvars(r"%USERPROFILE%\Documents"),
    "pictures":  os.path.expandvars(r"%USERPROFILE%\Pictures"),
    "music":     os.path.expandvars(r"%USERPROFILE%\Music"),
    "videos":    os.path.expandvars(r"%USERPROFILE%\Videos"),
}


def normalize_app_name(text: str) -> str:
    text = text.lower().strip()
    for word in ["app", "application", "program", "software", "the"]:
        text = text.replace(word, "")
    return " ".join(text.split())


def resolve_app(user_app: str, extra_aliases: dict = None) -> str | None:
    """Find the registry key for a user-supplied app name."""
    user_app = normalize_app_name(user_app)

    # Direct match
    if user_app in APP_REGISTRY:
        return user_app

    # Alias table from knowledge.json
    if extra_aliases and user_app in extra_aliases:
        mapped = extra_aliases[user_app]
        if mapped in APP_REGISTRY:
            return mapped

    # Fuzzy substring match
    for key in APP_REGISTRY:
        clean_key = key.replace(" ", "")
        clean_user = user_app.replace(" ", "")
        if clean_user in clean_key or clean_key in clean_user:
            return key

    return None


def open_app(app_name: str, extra_aliases: dict = None) -> str:
    """Open an app. Returns status message."""
    # Check folder shortcuts first
    lower = app_name.lower().strip()
    if lower in FOLDER_SHORTCUTS:
        subprocess.Popen(["explorer", FOLDER_SHORTCUTS[lower]])
        return f"Opening {app_name} folder"

    # Try registry
    key = resolve_app(app_name, extra_aliases)

    if key:
        info = APP_REGISTRY[key]
        try:
            if info.get("type") == "uwp":
                subprocess.Popen(["cmd", "/c", "start", "", info["path"]], shell=True)
            else:
                subprocess.Popen(info["path"], shell=True)
            return f"Opening {key}"
        except Exception as e:
            pass

    # Generic Windows start fallback (original jarvis_groq behaviour)
    try:
        subprocess.Popen(["cmd", "/c", "start", "", app_name], shell=True)
        return f"Opening {app_name}"
    except Exception:
        pass

    return f"Couldn't open {app_name}"


def close_app(app_name: str, extra_aliases: dict = None) -> str:
    """Close a running app. Returns status message."""
    key = resolve_app(app_name, extra_aliases)

    if not key:
        # Try generic taskkill
        try:
            subprocess.run(
                ["taskkill", "/IM", app_name, "/F"],
                shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            return f"Closed {app_name}"
        except Exception:
            return f"Couldn't find or close {app_name}"

    info = APP_REGISTRY[key]

    if info.get("type") == "uwp":
        subprocess.run(["taskkill", "/IM", info["process"], "/F"],
                       shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["taskkill", "/IM", "ApplicationFrameHost.exe", "/F"],
                       shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return f"Closed {key}"

    closed = False
    for proc in psutil.process_iter(["name"]):
        try:
            if proc.info["name"] and info["process"].lower() in proc.info["name"].lower():
                proc.terminate()
                closed = True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

METADATA = {
    "name": "open_app",
    "description": "Opens or closes desktop applications and folders.",
    "intents": ["open", "close", "launch", "start", "kill", "terminate"]
}

def execute(action: str, args: dict) -> str:
    """Unified entry point for Skill Registry."""
    app_name = args.get("app_name", args.get("query", ""))
    if action == "close":
        return close_app(app_name)
    return open_app(app_name)
