"""
core/agents/memory_agent.py — The Memory Agent
Handles context resolution, pattern detection (macros), and structured knowledge access.
"""

from core.memory import MemoryManager
from core.session_memory import SessionMemory
from database.db import memory_set, memory_get
import json
import collections

class MemoryAgent:
    """
    Manages short-term context and long-term knowledge.
    Learns from user patterns to self-evolve.
    """

    def __init__(self, user_id=0):
        self.user_id = user_id
        self.manager = MemoryManager()
        self.session = SessionMemory()
        self._action_history = collections.deque(maxlen=10) # Track last 10 actions for optimization

    def resolve_context(self, user_text: str) -> str:
        """
        Replaces ambiguous pronouns with known topics.
        E.g., "close it" → "close notepad".
        """
        lower = user_text.lower().strip()
        last_topic = self.session.last_topic
        
        if not last_topic:
            return user_text

        pronouns = [" it", " that", " this"]
        for p in pronouns:
            if p in lower or lower == p.strip():
                return user_text.replace(p.strip(), last_topic)
        
        return user_text

    def track_action(self, action_name: str, args: dict):
        """Record an action to detect repetitive patterns."""
        self._action_history.append((action_name, json.dumps(args, sort_keys=True)))
        self._detect_evolving_macro()

    def _detect_evolving_macro(self):
        if len(self._action_history) < 6:
            return

        h = list(self._action_history)
        last_3 = h[-3:]
        prev_3 = h[-6:-3]
        
        if last_3 == prev_3:
            # Generate a name like "macro_open_app_open_app"
            skill_names = [a[0] for a in last_3]
            name = "macro_" + "_".join(skill_names)
            
            # Logic to extract the actual arguments
            # (In a simplified version, we just store the list of apps)
            apps = []
            for action_tuple in last_3:
                args = json.loads(action_tuple[1])
                app = args.get("app_name") or args.get("query")
                if app: apps.append(app)
            
            if apps:
                print(f"[MemoryAgent] Evolution! Learned new macro: {name} -> {apps}")
                self.manager.learn_work_mode(name, apps)
                # Notify Reflection that we learned something
                return True
        return False

    def update_session(self, intent: str = None, topic: str = None, response: str = None):
        self.session.update(intent, topic, response)

    def get_preference(self, key: str, default=None):
        return self.manager.get_preference(key, default)

    def set_preference(self, key: str, value):
        self.manager.set_preference(key, value)
