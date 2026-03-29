"""
core/agents/reflection_agent.py — The Reflection Agent
Evaluates results, learns from failures, and updates memory.
"""

from core.agents.memory_agent import MemoryAgent
from core.sentinel import Sentinel

class ReflectionAgent:
    """
    Analyzes execution results and improves Vighna's performance.
    """

    def __init__(self, memory: MemoryAgent, brain=None):
        self.memory = memory
        self.sentinel = Sentinel(brain=brain)
        self.brain = brain

    def reflect(self, results: list[dict]):
        """
        Evaluate the outcome of the last execution plan.
        Updates memory with successes/failures.
        """
        successes = 0
        errors = []
        
        for res in results:
            if res["status"] == "success":
                successes += 1
                # Track successful patterns for future macros
                step = res["step"]
                self.memory.track_action(step["skill"], step["args"])
            else:
                errors.append(res)

        if not errors:
            return f"Task completed successfully with {successes} steps."

        # Handle errors via Sentinel or LLM
        err_msg = "\n".join([f"- {e['message']}" for e in errors])
        
        # If we have a serious error, log it via sentinel
        for err in errors:
            if "fail" in err["message"].lower() or "error" in err["message"].lower():
                self.sentinel.log_exception(Exception(err["message"]))

        # Use Brain (Groq) to provide a helpful reflection on the failure
        if self.brain:
            prompt = (
                "You are the Vighna Reflection Agent. The following tasks failed. "
                "Briefly explain why and what the user should try next.\n\n"
                f"ERRORS:\n{err_msg}"
            )
            return self.brain._ai_fallback(prompt)

        return f"Task had {len(errors)} errors: {err_msg}"
