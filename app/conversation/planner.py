
from typing import Dict


def plan_response(understanding: Dict) -> str:
    intent = understanding.get("intent", "")

    plans = {
        "clarification_request": "Clarify the immediately previous question or statement. Do not invent a new subject.",
        "agreement": "Acknowledge agreement naturally. Continue the current topic only if it has a natural next step.",
        "acknowledgement": "Treat the reply as context-dependent acknowledgement and react to the previous turn.",
        "continue_current_topic": "Continue or explain the current topic. Do not restart with a generic question.",
        "nothing_or_negative": "Accept the user's response naturally. Do not force an unrelated activity or topic.",
        "greeting": "Return a natural greeting appropriate to the current tone.",
    }
    return plans.get(
        intent,
        "Respond directly to the user's meaning and context. Introduce a question only when conversationally useful.",
    )
