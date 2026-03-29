"""
core/agents/planner_agent.py — The Planner Agent
Intelligently decomposes user intent into a sequence of skill-based steps.
"""

import json
from core.skill_registry import SkillRegistry
from core.agents.memory_agent import MemoryAgent

class PlannerAgent:
    """
    Analyzes intent and creates a multi-step plan.
    """

    def __init__(self, registry: SkillRegistry, memory: MemoryAgent, brain=None):
        self.registry = registry
        self.memory = memory
        self.brain = brain # Access to Groq via Brain Orchestrator

    def plan(self, user_text: str) -> list[dict]:
        """
        Main planning logic. Returns a list of steps.
        Each step: {'skill': str, 'action': str, 'args': dict}
        """
        clean = user_text.lower().strip()
        
        # 1. Check for simple, known intent patterns
        simple_skill = self.registry.find_by_intent(clean)
        if simple_skill:
            return [{"skill": simple_skill, "action": "default", "args": {"query": user_text}}]

        # 2. Check for compound work modes or learned macros
        work_modes = self.memory.manager.list_work_modes()
        for mode_name, apps in work_modes.items():
            if mode_name in clean:
                if mode_name.startswith("macro_"):
                   return [{"skill": "macro", "action": mode_name, "args": {"apps": apps}}]
                
                # Default legacy work mode (opening apps)
                steps = []
                for app in apps:
                    steps.append({"skill": "open_app", "action": "open", "args": {"app_name": app}})
                return steps

        # 3. LLM-based intelligent decomposition (Slow path)
        if self.brain:
            return self._llm_plan(user_text)

        return []

    def _llm_plan(self, user_text: str) -> list[dict]:
        """Use Groq to decompose complex prompts into steps."""
        skills_summary = "\n".join([
            f"- {s['name']}: {s['description']}" for s in self.registry.list_skills()
        ])
        
        prompt = (
            "You are the Vighna Planner Agent. Your job is to take a user prompt and "
            "break it into a list of JSON-formatted steps using the available skills.\n\n"
            f"AVAILABLE SKILLS:\n{skills_summary}\n\n"
            "Respond ONLY with a JSON list of steps. Format: "
            '[{"skill": "name", "action": "name", "args": {"key": "value"}}]\n\n'
            f"USER PROMPT: '{user_text}'"
        )
        
        try:
            # Call Brain's _ai_fallback or similar
            raw_json = self.brain._ai_fallback(prompt)
            # Basic sanitization
            if "```json" in raw_json:
                raw_json = raw_json.split("```json")[1].split("```")[0].strip()
            
            return json.loads(raw_json)
        except Exception as e:
            print(f"[PlannerAgent] LLM Planning failed: {e}")
            return []
