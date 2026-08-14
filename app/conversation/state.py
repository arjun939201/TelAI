
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class Turn:
    role: str
    content: str


@dataclass
class ConversationState:
    topic: str = ""
    open_question: str = ""
    last_user_intent: str = ""
    last_assistant_intent: str = ""
    tone: str = "casual"
    recent: List[Turn] = field(default_factory=list)

    def add(self, role: str, content: str, limit: int = 10):
        self.recent.append(Turn(role, content))
        self.recent = self.recent[-limit:]

    def last_assistant(self) -> str:
        for turn in reversed(self.recent):
            if turn.role == "assistant":
                return turn.content
        return ""

    def last_user(self) -> str:
        for turn in reversed(self.recent):
            if turn.role == "user":
                return turn.content
        return ""

    def context_text(self) -> str:
        return "\n".join([
            "CONVERSATION STATE:",
            f"- topic: {self.topic or '(not established)'}",
            f"- open question: {self.open_question or '(none)'}",
            f"- last user intent: {self.last_user_intent or '(unknown)'}",
            f"- tone: {self.tone}",
        ])


def from_history(history: List[Dict]) -> ConversationState:
    state = ConversationState()
    for item in (history or [])[-10:]:
        if not isinstance(item, dict):
            continue
        if item.get("role") in {"user", "assistant"} and isinstance(item.get("content"), str):
            state.add(item["role"], item["content"].strip())

    assistant = state.last_assistant()
    if assistant and (
        "?" in assistant or "？" in assistant
        or any(x in assistant for x in ("ఏంటి", "ఏమి", "ఎలా", "ఎందుకు", "ఎక్కడ", "ఎప్పుడు"))
    ):
        state.open_question = assistant
    return state


@dataclass
class TurnState:
    """Small compatibility/context object used by tests and short-turn intent detection."""
    last_assistant: str = ""
    open_question: str = ""

    def last_assistant_text(self) -> str:
        return self.last_assistant


