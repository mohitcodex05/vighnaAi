"""
skills/file_system.py — File & folder operations
"""

import os
import shutil


def create_file(path: str) -> str:
    path = os.path.expandvars(os.path.expanduser(path))
    try:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write("")
        return f"Created file: {path}"
    except Exception as e:
        return f"Error creating file: {e}"


def delete_file(path: str) -> str:
    path = os.path.expandvars(os.path.expanduser(path))
    try:
        if os.path.isfile(path):
            os.remove(path)
            return f"Deleted file: {path}"
        elif os.path.isdir(path):
            shutil.rmtree(path)
            return f"Deleted folder: {path}"
        return f"Path not found: {path}"
    except Exception as e:
        return f"Error deleting: {e}"


def rename_file(old_path: str, new_name: str) -> str:
    old_path = os.path.expandvars(os.path.expanduser(old_path))
    directory = os.path.dirname(old_path)
    new_path = os.path.join(directory, new_name)
    try:
        os.rename(old_path, new_path)
        return f"Renamed to: {new_name}"
    except Exception as e:
        return f"Error renaming: {e}"


def create_folder(path: str) -> str:
    path = os.path.expandvars(os.path.expanduser(path))
    try:
        os.makedirs(path, exist_ok=True)
        return f"Created folder: {path}"
    except Exception as e:
        return f"Error creating folder: {e}"


def list_folder(path: str = ".") -> str:
    path = os.path.expandvars(os.path.expanduser(path))
    try:
        items = os.listdir(path)
        if not items:
            return f"{path} is empty"
        return f"Contents of {path}:\n" + "\n".join(f"  {'📁' if os.path.isdir(os.path.join(path,i)) else '📄'} {i}" for i in items)
    except Exception as e:
        return f"Error listing folder: {e}"


def open_folder(path: str) -> str:
    import subprocess
    path = os.path.expandvars(os.path.expanduser(path))
    try:
        subprocess.Popen(["explorer", path])
        return f"Opened folder: {path}"
    except Exception as e:
        return f"Error opening folder: {e}"

METADATA = {
    "name": "file_system",
    "description": "Create, delete, rename, and list files or folders.",
    "intents": ["file", "folder", "directory", "create", "delete", "rename", "list"]
}

def execute(action: str, args: dict) -> str:
    path = args.get("path", "")
    if action == "create_file": return create_file(path)
    if action == "delete": return delete_file(path)
    if action == "rename": return rename_file(path, args.get("new_name", ""))
    if action == "create_folder": return create_folder(path)
    if action == "list": return list_folder(path)
    if action == "open": return open_folder(path)
    return "Unknown file system action."
