"""
core/memory.py — Persistent Memory Manager
Combines: SQLite key-value store + memory/knowledge.json
"""

import json
import os
from database.db import memory_set, memory_get

KNOWLEDGE_PATH = os.path.join(os.path.dirname(__file__), "..", "memory", "knowledge.json")


def _load_knowledge() -> dict:
    if os.path.exists(KNOWLEDGE_PATH):
        with open(KNOWLEDGE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _save_knowledge(data: dict):
    os.makedirs(os.path.dirname(KNOWLEDGE_PATH), exist_ok=True)
    with open(KNOWLEDGE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


class MemoryManager:
    def __init__(self):
        self._knowledge = _load_knowledge()

    def reload(self):
        self._knowledge = _load_knowledge()

    # ── Knowledge JSON helpers ──────────────────────────────────────────────
    def get_app_alias(self, name: str) -> str | None:
        aliases = self._knowledge.get("app_aliases", {})
        return aliases.get(name.lower())

    def get_work_mode(self, mode_name: str) -> list:
        modes = self._knowledge.get("work_modes", {})
        return modes.get(mode_name.lower(), [])

    def get_folder_shortcut(self, name: str) -> str | None:
        shortcuts = self._knowledge.get("folder_shortcuts", {})
        raw = shortcuts.get(name.lower())
        if raw:
            return os.path.expandvars(raw)
        return None

    def get_preference(self, key: str, default=None):
        return self._knowledge.get("preferences", {}).get(key, default)

    def set_preference(self, key: str, value):
        if "preferences" not in self._knowledge:
            self._knowledge["preferences"] = {}
        self._knowledge["preferences"][key] = value
        _save_knowledge(self._knowledge)

    def learn_app(self, alias: str, app_key: str):
        """Teach Vighna a new app alias."""
        if "app_aliases" not in self._knowledge:
            self._knowledge["app_aliases"] = {}
        self._knowledge["app_aliases"][alias.lower()] = app_key.lower()
        _save_knowledge(self._knowledge)
        memory_set(f"alias:{alias}", app_key)

    def learn_work_mode(self, mode_name: str, apps: list):
        """Define or update a work mode."""
        if "work_modes" not in self._knowledge:
            self._knowledge["work_modes"] = {}
        self._knowledge["work_modes"][mode_name.lower()] = apps
        _save_knowledge(self._knowledge)

    # ── SQLite key-value ────────────────────────────────────────────────────
    def remember(self, key: str, value: str):
        memory_set(key, value)

    def recall(self, key: str, default=None) -> str | None:
        return memory_get(key, default)

    def list_work_modes(self) -> dict:
        return self._knowledge.get("work_modes", {})
