
from typing import Dict, List


def extract_memory_candidates(history: List[Dict], limit: int = 12) -> List[Dict]:
    """Extract only explicit, low-risk conversational facts.

    This is deliberately conservative. It does not persist sensitive data or
    silently turn arbitrary model output into user memory.
    """
    result = []
    for item in (history or [])[-20:]:
        if not isinstance(item, dict) or item.get("role") != "user":
            continue
        text = str(item.get("content", "")).strip()
        if not text:
            continue
        # Keep only explicit preference/identity-like statements as candidates.
        if any(marker in text for marker in ("నా పేరు", "నాకు ఇష్టం", "నాకు నచ్చదు", "నేను")):
            result.append({"text": text, "status": "candidate"})
    return result[-limit:]


def format_memory(candidates: List[Dict]) -> str:
    if not candidates:
        return "CONVERSATION MEMORY: none"
    lines = ["CONVERSATION MEMORY (candidate facts, use cautiously):"]
    for item in candidates:
        lines.append(f"- {item['text']}")
    return "\n".join(lines)
