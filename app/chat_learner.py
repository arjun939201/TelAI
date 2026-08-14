"""Extract explicit user-provided learning from chat without teaching the model blindly."""
from __future__ import annotations

import re
from typing import Any

from app.learner_store import add_learning, approved_for_query

ARROWS = "→➜⇒"


def _equivalence(text: str) -> tuple[str, str] | None:
    # Explicit user knowledge: "సమస్య = చిక్కు" / "సమస్య → చిక్కు".
    m = re.search(r"([^=→➜⇒\n]{1,80})\s*(?:=|→|➜|⇒)\s*([^=→➜⇒\n]{1,80})", text)
    if not m:
        return None
    left, right = m.group(1).strip(" .:-—>"), m.group(2).strip(" .:-—>")
    if not left or not right or len(left) > 80 or len(right) > 80:
        return None
    return left, right


def learn_from_user_message(message: str) -> list[dict[str, Any]]:
    """Store explicit user knowledge as approved, because it is user-authored.

    The master corpus is never modified here. Anything inferred from ordinary
    conversation remains unlearned unless the user states an explicit mapping.
    """
    pair = _equivalence(message)
    if not pair:
        return []
    standard, melimi = pair
    # Avoid treating normal prose containing an equals sign as a language rule.
    if len(standard.split()) > 8 or len(melimi.split()) > 8:
        return []
    item = add_learning(
        kind="vocabulary",
        standard=standard,
        melimi=melimi,
        meaning=standard,
        evidence=message.strip(),
        source="user_explicit",
        status="approved",
        confidence=1.0,
        metadata={"method": "explicit_equivalence"},
    )
    return [item]


def format_learned(query: str, limit: int = 6) -> str:
    rows = approved_for_query(query, limit=limit)
    if not rows:
        return "No approved chat-time learning is relevant."
    lines = []
    for row in rows:
        if row["kind"] == "vocabulary":
            lines.append(f"- {row['standard']} → {row['melimi']}")
        elif row["kind"] == "rule":
            lines.append(f"- Rule: {row['rule']} — {row['meaning']}")
    return "\n".join(lines)
