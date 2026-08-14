
from dataclasses import dataclass
from typing import List, Optional
import re

from app.language import normalize_roman_telugu, tokens


@dataclass
class TurnState:
    last_assistant: str = ""
    last_user: str = ""
    open_question: str = ""
    topic: str = ""
    last_intent: str = ""
    tone: str = "casual"


def build_state(history: List[dict]) -> TurnState:
    state = TurnState()
    clean = [
        x for x in history
        if isinstance(x, dict)
        and x.get("role") in {"user", "assistant"}
        and isinstance(x.get("content"), str)
    ][-10:]

    for item in reversed(clean):
        if item["role"] == "assistant":
            state.last_assistant = item["content"].strip()
            break

    for item in reversed(clean):
        if item["role"] == "user":
            state.last_user = item["content"].strip()
            break

    if state.last_assistant and ("?" in state.last_assistant or "？" in state.last_assistant):
        state.open_question = state.last_assistant

    return state


SHORT_MEANINGS = {
    "enti": "clarification_request",
    "emiti": "clarification_request",
    "em": "clarification_request",
    "haa": "acknowledgement",
    "haaa": "acknowledgement",
    "sare": "agreement",
    "ok": "agreement",
    "okay": "agreement",
    "avunu": "agreement",
    "cheppu": "continue_current_topic",
    "inka": "continue_current_topic",
    "emle": "nothing_or_negative",
    "emledu": "nothing_or_negative",
    "emledhu": "nothing_or_negative",
    "nothing": "nothing_or_negative",
    "hi": "greeting",
    "hello": "greeting",
    "hey": "greeting",
}


def infer_intent(user_text: str, state: TurnState) -> str:
    raw = user_text.strip().lower()
    compact = re.sub(r"\s+", " ", raw)
    if compact in SHORT_MEANINGS:
        intent = SHORT_MEANINGS[compact]
        if intent == "clarification_request" and state.last_assistant:
            return "clarification_request"
        return intent

    normalized = normalize_roman_telugu(user_text)
    low = normalized.lower()

    if "ఎందుకు" in low or "ఎందుక" in low:
        return "why_question"
    if "ఎలా" in low:
        return "how_question"
    if "ఎక్కడ" in low:
        return "where_question"
    if "ఎప్పుడు" in low:
        return "when_question"
    if "ఎవరు" in low or "ఎవరు" in normalized:
        return "who_question"
    if "?" in user_text or "？" in user_text:
        return "question"
    if any(x in low for x in ["ధన్యవాద", "నెనరు"]):
        return "gratitude"
    return "contextual_statement"


def understanding_context(user_text: str, state: TurnState) -> str:
    intent = infer_intent(user_text, state)

    lines = [
        "CONVERSATION UNDERSTANDING:",
        f"- current user input: {user_text.strip()}",
        f"- normalized hint: {normalize_roman_telugu(user_text)}",
        f"- inferred conversational intent: {intent}",
        f"- previous assistant turn: {state.last_assistant or '(none)'}",
        f"- open question: {state.open_question or '(none)'}",
        "",
        "CONTEXT RULES:",
        "- Interpret the current turn in relation to the previous turn.",
        "- Short replies such as enti, haa, sare, em, and cheppu are context-sensitive.",
        "- If the assistant asked a question and the user says enti/emiti, treat it as a clarification request unless the surrounding context strongly indicates another meaning.",
        "- Answer the user's actual conversational move before introducing a new subject.",
        "- Do not automatically append a generic question to every answer.",
        "- Do not copy previous assistant wording just because it exists in history.",
    ]
    return "\n".join(lines)
