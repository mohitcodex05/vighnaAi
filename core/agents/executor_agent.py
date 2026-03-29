"""
core/agents/executor_agent.py — The Executor Agent
Sequential execution of planned steps with error handling and HUD feedback.
"""

import time
from core.skill_registry import SkillRegistry

class ExecutorAgent:
    """
    Executes a plan via the SkillRegistry.
    """

    def __init__(self, registry: SkillRegistry, tts_engine=None, on_action=None):
        self.registry = registry
        self.tts = tts_engine
        self.on_action = on_action

    def _emit(self, msg: str):
        if self.on_action:
            self.on_action(msg)

    def _speak(self, text: str):
        if self.tts:
            try:
                self.tts.say(text)
                self.tts.runAndWait()
            except Exception:
                pass

    def run(self, plan: list[dict]) -> list[dict]:
        """
        Execute the plan.
        Returns a list of result dicts: {'step': dict, 'status': str, 'message': str}
        """
        results = []
        for step in plan:
            skill_name = step.get("skill")
            action = step.get("action", "default")
            args = step.get("args", {})
            
            self._emit(f"🎬 Executing: {skill_name} ({action})")
            
            skill_data = self.registry.get_skill(skill_name)
            if not skill_data:
                res = {"step": step, "status": "error", "message": f"Skill '{skill_name}' not found."}
                results.append(res)
                self._emit(f"❌ {res['message']}")
                continue

            exec_fn = skill_data["execute"]
            if not exec_fn:
                res = {"step": step, "status": "error", "message": f"Skill '{skill_name}' has no execute function."}
                results.append(res)
                self._emit(f"❌ {res['message']}")
                continue

            try:
                # Skill execution
                msg = exec_fn(action, args)
                res = {"step": step, "status": "success", "message": str(msg)}
                self._emit(f"✅ {msg}")
                self._speak(str(msg))
            except Exception as e:
                res = {"step": step, "status": "error", "message": f"Execution failed: {e}"}
                self._emit(f"⚠️ Error: {e}")

            results.append(res)
            time.sleep(1.0) # Brief pause between sequential tasks

        return results
