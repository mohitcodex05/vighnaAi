"""
core/brain.py — Central Intent Router for Vighna
Receives text → classifies intent → dispatches to skills → returns response
Preserves all original jarvis_groq.py logic, now modular.
"""

import os
from core.skill_registry import SkillRegistry
from core.agents.memory_agent import MemoryAgent
from core.agents.planner_agent import PlannerAgent
from core.agents.executor_agent import ExecutorAgent
from core.agents.reflection_agent import ReflectionAgent
from database.db import save_message

class Brain:
    """
    Master Orchestrator.
    Coordinates specialized agents to solve user tasks.
    """

    SYSTEM_PROMPT = (
        "You are Vighna, an intelligent personal AI assistant — like ChatGPT meets Siri. "
        "You are helpful, friendly, and concise. You give short but complete answers unless "
        "the user wants details. You feel human, warm, and proactive."
    )

    def __init__(self, user_id: int = 0, conversation_id: int = 0,
                 tts_engine=None, on_action=None):
        self.user_id = user_id
        self.conversation_id = conversation_id
        self.tts = tts_engine
        self.on_action = on_action

        # Agent Initialization
        self.registry = SkillRegistry()
        self.memory = MemoryAgent(user_id=user_id)
        self.planner = PlannerAgent(self.registry, self.memory, brain=self)
        self.executor = ExecutorAgent(self.registry, tts_engine=tts_engine, on_action=on_action)
        self.reflection = ReflectionAgent(self.memory, brain=self)

        self._groq = None
        self._conversation_history = [
            {"role": "system", "content": self.SYSTEM_PROMPT}
        ]

    def _get_groq(self):
        if self._groq is None:
            api_key = os.getenv("GROQ_API_KEY", "")
            if api_key:
                from groq import Groq
                self._groq = Groq(api_key=api_key)
        return self._groq

    def _emit(self, msg: str):
        if self.on_action:
            self.on_action(msg)

    def _save(self, sender: str, content: str):
        if self.conversation_id:
            try:
                save_message(self.conversation_id, sender, content)
            except Exception:
                pass

    # ──────────────────────────────────────────────────────────────────────
    # MASTER ORCHESTRATION LOOP
    # ──────────────────────────────────────────────────────────────────────
    def process_text(self, user_text: str) -> str:
        """The Multi-Agent Workflow."""
        self._save("user", user_text)
        
        # 1. Context Resolution (Memory Agent)
        context_text = self.memory.resolve_context(user_text)
        if context_text != user_text:
            self._emit(f"🧠 Context resolved: '{context_text}'")

        # 2. Planning (Planner Agent)
        plan = self.planner.plan(context_text)
        
        if plan:
            # 3. Execution (Executor Agent)
            results = self.executor.run(plan)
            
            # 4. Reflection & Learning (Reflection Agent)
            response = self.reflection.reflect(results)
            
            # Update session stats
            if plan:
                main_step = plan[0]
                self.memory.update_session(intent=main_step["skill"], topic=main_step.get("args", {}).get("app_name"))
        else:
            # Fallback to pure conversation
            response = self._ai_fallback(user_text)

        self._save("assistant", response)
        self.memory.update_session(response=response)
        return response

    # ──────────────────────────────────────────────────────────────────────
    # AI FALLBACK & DOC SKILLS
    # ──────────────────────────────────────────────────────────────────────
    def _ai_fallback(self, user_text: str) -> str:
        groq = self._get_groq()
        if not groq:
            return "I didn't understand that. (Groq API key missing)"

        self._conversation_history.append({"role": "user", "content": user_text})
        try:
            resp = groq.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=self._conversation_history,
                max_tokens=512
            )
            reply = resp.choices[0].message.content
            self._conversation_history.append({"role": "assistant", "content": reply})
            return reply
        except Exception as e:
            return f"I ran into an issue: {e}"

    def answer_pdf(self, pdf_path: str, question: str) -> str:
        from skills.pdf_reader import execute as pdf_exec
        return pdf_exec("answer", {"path": pdf_path, "question": question, "groq_client": self._get_groq()})

    def analyze_image(self, image_path: str, question: str = "") -> str:
        from skills.image_reader import execute as img_exec
        return img_exec("analyze", {"path": image_path, "question": question, "groq_client": self._get_groq()})
