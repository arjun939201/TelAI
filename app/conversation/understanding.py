
import re
from typing import Dict

from app.conversation.state import ConversationState
from app.linguistics.normalizer import normalize_roman_telugu


SHORT_INTENTS = {
    "hi": "greeting", "hello": "greeting", "hey": "greeting",
    "హాయ్": "greeting", "హలో": "greeting",
    "haa": "acknowledgement", "haaa": "acknowledgement", "హా": "acknowledgement",
    "sare": "agreement", "ok": "agreement", "okay": "agreement", "సరే": "agreement",
    "avunu": "agreement", "అవును": "agreement",
    "cheppu": "continue_current_topic", "చెప్పు": "continue_current_topic",
    "inka": "continue_current_topic", "ఇంకా": "continue_current_topic",
    "emle": "nothing_or_negative", "emledu": "nothing_or_negative",
    "emledhu": "nothing_or_negative", "nothing": "nothing_or_negative",
    "ఏంలేదు": "nothing_or_negative",
}


def _key(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def _infer_intent_dict(text: str, state: ConversationState) -> Dict:
    key = _key(text)
    normalized = normalize_roman_telugu(text)
    legacy_state = not hasattr(state, "last_assistant") or not hasattr(state, "last_user")
    # TurnState exposes last_assistant as a field; ConversationState exposes it as a method.
    if hasattr(state, "last_assistant") and isinstance(getattr(state, "last_assistant"), str):
        previous_assistant = getattr(state, "last_assistant")
        open_question = getattr(state, "open_question", "")
    else:
        previous_assistant = state.last_assistant()
        open_question = state.open_question

    # Contextual clarification is intentionally checked before generic "what".
    if key in {"enti", "emiti", "em"} or normalized in {"ఏంటి", "ఏమిటి", "ఏం"}:
        if open_question:
            return {
                "intent": "clarification_request",
                "confidence": "high",
                "meaning": "The user is asking what the assistant meant by its previous question/message.",
            }
        return {
            "intent": "what_question",
            "confidence": "medium",
            "meaning": "The user is asking what something is or what was meant.",
        }

    intent = SHORT_INTENTS.get(key) or SHORT_INTENTS.get(normalized)
    if intent:
        return {
            "intent": intent,
            "confidence": "medium",
            "meaning": "Interpret this conversational move in the current context.",
        }

    low = normalized.lower()
    if "ఎందుకు" in low:
        intent = "why_question"
    elif "ఎలా" in low:
        intent = "how_question"
    elif "ఎక్కడ" in low:
        intent = "where_question"
    elif "ఎప్పుడు" in low:
        intent = "when_question"
    elif "ఎవరు" in low:
        intent = "who_question"
    elif "?" in text or "？" in text:
        intent = "question"
    elif any(x in low for x in ("ధన్యవాద", "నెనరు")):
        intent = "gratitude"
    else:
        intent = "contextual_statement"

    return {
        "intent": intent,
        "confidence": "medium",
        "meaning": "Interpret the message using the full conversation and linguistic context.",
    }


def build_context(text: str, state: ConversationState, linguistic: Dict) -> str:
    result = _infer_intent_dict(text, state)
    return "\n".join([
        "CONTEXTUAL UNDERSTANDING:",
        f"- user input: {text.strip()}",
        f"- normalized hint: {linguistic.get('normalized', '')}",
        f"- sentence force: {linguistic.get('sentence_force', 'unknown')}",
        f"- question type: {linguistic.get('question_type', 'unknown')}",
        f"- contextual intent: {result['intent']}",
        f"- confidence: {result['confidence']}",
        f"- meaning: {result['meaning']}",
        f"- previous assistant: {state.last_assistant() or '(none)'}",
        f"- open question: {state.open_question or '(none)'}",
        "",
        "CONVERSATION RULES:",
        "- Interpret short replies from the previous turn, not as isolated dictionary entries.",
        "- If the assistant asked a question and the user says enti/emiti/em, normally clarify the previous question.",
        "- Answer the user's current conversational move before changing topic.",
        "- Do not ask a generic follow-up after every answer.",
        "- Do not copy previous assistant wording.",
    ])


def infer_intent(text: str, state: ConversationState):
    result = _infer_intent_dict(text, state)
    # Keep the legacy compact API used by older callers/tests. The main app uses
    # ConversationState and receives the richer dictionary.
    if state.__class__.__name__ == "TurnState":
        return result["intent"]
    return result
