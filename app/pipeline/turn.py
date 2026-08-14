from typing import Any, Dict

from app.conversation.state import ConversationState, infer_open_question
from app.conversation.understanding import build_understanding_context, understand_user_turn
from app.conversation.planner import plan_natural_response


def prepare_turn(
    user_text: str,
    history: list,
    state: ConversationState,
) -> Dict[str, Any]:
    """Prepare one turn locally before the single normal LLM request."""
    state.recent_turns = []

    for item in history[-8:]:
        if isinstance(item, dict):
            role = item.get("role")
            content = item.get("content")
            if role in {"user", "assistant"} and isinstance(content, str):
                state.add_turn(role, content)

    if state.recent_turns:
        last_assistant = next(
            (t.content for t in reversed(state.recent_turns) if t.role == "assistant"),
            "",
        )
        state.open_question = infer_open_question(last_assistant)

    understanding = understand_user_turn(user_text, state)
    state.last_user_intent = str(understanding.get("intent") or "")

    return {
        "understanding": understanding,
        "understanding_context": build_understanding_context(user_text, state),
        "response_plan": plan_natural_response(understanding),
        "state_context": state.context_text(),
    }
