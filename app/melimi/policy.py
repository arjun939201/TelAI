from typing import Iterable, Dict, List


def build_melimi_policy(
    vocabulary: Iterable[Dict],
    max_items: int = 40,
) -> str:
    """Build compact policy context from approved vocabulary.

    The policy does not blindly replace strings. It tells the model that
    approved Melimi forms are authoritative when they fit the intended
    meaning and grammar.
    """
    lines = [
        "MELIMI EXPRESSION POLICY:",
        "- In Melimi mode, use approved Melimi vocabulary wherever a suitable form exists.",
        "- Prefer established Melimi expressions over ordinary loan/standard alternatives.",
        "- Do not perform blind word-for-word substitution.",
        "- Preserve meaning, grammar, tense, person, number, case, and natural conversational flow.",
        "- If no approved Melimi form exists, do not invent one merely to avoid a loanword.",
        "- Do not make every answer sound like a dictionary conversion; compose a natural conversation first.",
        "- Avoid repetitive generic follow-up questions unless context calls for one.",
        "",
        "APPROVED MELIMI EXAMPLES:",
    ]

    count = 0
    for entry in vocabulary or []:
        if not isinstance(entry, dict):
            continue
        standard = str(entry.get("standard") or "").strip()
        melimi = str(entry.get("melimi") or "").strip()
        if not standard or not melimi:
            continue
        lines.append(f"- {standard} → {melimi}")
        count += 1
        if count >= max_items:
            break

    return "\n".join(lines)
