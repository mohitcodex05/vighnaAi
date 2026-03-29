"""
core/skill_registry.py — Dynamic Skill Discovery System
Scans the skills/ directory and loads metadata + execute functions.
"""

import os
import importlib.util
import inspect


class SkillRegistry:
    """
    Automated registry that discovers and manages Vighna's capabilities.
    """

    def __init__(self, skills_dir: str = None):
        if skills_dir is None:
            skills_dir = os.path.join(os.path.dirname(__file__), "..", "skills")
        self.skills_dir = os.path.abspath(skills_dir)
        self.registry = {}
        self.refresh()

    def refresh(self):
        """Scan skills folder and import modules."""
        self.registry = {}
        if not os.path.exists(self.skills_dir):
            return

        for filename in os.listdir(self.skills_dir):
            if filename.endswith(".py") and not filename.startswith("__"):
                skill_name = filename[:-3]
                self._load_skill(skill_name, os.path.join(self.skills_dir, filename))

    def _load_skill(self, name: str, path: str):
        try:
            spec = importlib.util.spec_from_file_location(name, path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Metadata discovery
            # Skills can define a METADATA dict, or we use defaults
            meta = getattr(module, "METADATA", {
                "name": name,
                "intents": [name.replace("_", " ")],
                "description": f"Skill for {name}"
            })

            # Execution point
            # We look for a function named 'execute' or 'handle_intent'
            exec_fn = getattr(module, "execute", 
                      getattr(module, "handle_intent", None))

            # Fallback for old skills that don't have a single entry point
            # We wrap them in a generic dispatcher if needed (TBD)

            self.registry[name] = {
                "module": module,
                "metadata": meta,
                "execute": exec_fn
            }
        except Exception as e:
            print(f"[SkillRegistry] Error loading {name}: {e}")

    def list_skills(self) -> list:
        return [meta["metadata"] for meta in self.registry.values()]

    def get_skill(self, name: str):
        return self.registry.get(name)

    def find_by_intent(self, intent_text: str):
        """Simple keyword matching for intent fallback."""
        for name, data in self.registry.items():
            for pattern in data["metadata"].get("intents", []):
                if pattern in intent_text.lower():
                    return name
        return None
