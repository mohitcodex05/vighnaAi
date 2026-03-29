"""
core/session_memory.py — In-process short-term memory (extended from original)
"""

from datetime import datetime


class SessionMemory:
    def __init__(self):
        self.last_intent = None
        self.last_topic = None
        self.last_skill = None
        self.last_response = None
        self.entities = {}
        self.last_updated = None

    # ── backward compat: jarvis_groq.py used memory.topic ──
    @property
    def topic(self):
        return self.last_topic

    @topic.setter
    def topic(self, value):
        self.last_topic = value

    def update(self, intent=None, topic=None, skill=None, response=None, entities=None):
        if intent:
            self.last_intent = intent
        if topic:
            self.last_topic = topic
        if skill:
            self.last_skill = skill
        if response:
            self.last_response = response
        if entities:
            self.entities.update(entities)
        self.last_updated = datetime.now()

    def clear(self):
        self.__init__()

    def summary(self) -> dict:
        return {
            "intent": self.last_intent,
            "topic": self.last_topic,
            "skill": self.last_skill,
            "response": self.last_response,
            "entities": self.entities,
        }
