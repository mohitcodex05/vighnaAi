"""
core/planner.py — Multi-step action planner
Converts compound commands like "start work" into an ordered action list.
"""

from core.memory import MemoryManager


class Planner:
    def __init__(self, memory: MemoryManager):
        self.memory = memory

    def plan(self, command: str) -> list[dict] | None:
        """
        Returns a list of {'action': str, 'args': dict} steps, or None if not a compound command.
        """
        clean = command.lower().strip()

        # Check user-defined work modes from knowledge.json
        work_modes = self.memory.list_work_modes()
        for mode_name, apps in work_modes.items():
            if mode_name in clean:
                steps = []
                for app in apps:
                    steps.append({"action": "open_app", "args": {"app_name": app}})
                steps.append({"action": "say", "args": {"message": f"{mode_name.title()} activated!"}})
                return steps

        # Built-in compound commands
        if "morning routine" in clean:
            return [
                {"action": "open_app", "args": {"app_name": "chrome"}},
                {"action": "web", "args": {"query": "open google"}},
                {"action": "say", "args": {"message": "Good morning! Your routine is set up."}},
            ]

        if "shutdown" in clean or "shut down computer" in clean:
            return [
                {"action": "say", "args": {"message": "Shutting down in 10 seconds. Goodbye!"}},
                {"action": "system", "args": {"command": "shutdown /s /t 10"}},
            ]

        if "restart" in clean and "computer" in clean:
            return [
                {"action": "say", "args": {"message": "Restarting your computer now."}},
                {"action": "system", "args": {"command": "shutdown /r /t 5"}},
            ]

        return None  # Not a compound command

    def add_work_mode(self, mode_name: str, apps: list) -> str:
        self.memory.learn_work_mode(mode_name, apps)
        return f"Work mode '{mode_name}' saved with apps: {', '.join(apps)}"
