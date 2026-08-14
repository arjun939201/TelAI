"""Compact Melimi retrieval context for the LLM.

The full Melimi corpus is stored locally. Only relevant evidence is sent to
Groq; the always-on constitution supplies the core language identity/rules.
This prevents the language contract itself from consuming the TPM budget.
"""
from app.config import settings
from app.melimi.firewall import subject_lexicon
from app.melimi.index import language_profile, relevant_language_context
from app.melimi.registry import lexical_inventory


def _relevant_mappings(user_message: str, limit: int = 12) -> str:
    lexicon = subject_lexicon()
    preferred = lexicon.get("preferred", {})
    text = user_message or ""
    hits = []
    for source, target in preferred.items():
        if source and source in text:
            hits.append((source, target))
    # Keep common high-value mappings available even when the exact source is
    # not in the current sentence; retrieval/profile remains the main source.
    for source in ("సమస్య", "సహాయం", "వ్యవస్థ", "సాంకేతికత", "ఆసక్తికరమైన", "సినిమా"):
        if source in preferred and (source, preferred[source]) not in hits:
            hits.append((source, preferred[source]))
    hits = hits[:limit]
    if not hits:
        return "(No direct lexical mapping retrieved for this turn.)"
    return "\n".join(f"- {a} => {b}" for a, b in hits)


def build_language_engine_context(
    *, user_message: str, conversation_context: str,
    linguistic_analysis: str, response_plan: str,
    max_profile_chars: int = None, max_relevant_chars: int = None,
) -> str:
    max_profile_chars = max_profile_chars or settings.melimi_profile_chars
    max_relevant_chars = max_relevant_chars or settings.melimi_relevant_chars
    profile = language_profile(max_chars=max_profile_chars)
    relevant = relevant_language_context(user_message, max_chars=max_relevant_chars)
    mappings = _relevant_mappings(user_message)
    return f"""MELIMI TURN EVIDENCE\n\nRelevant authoritative mappings:\n{mappings}\n\nConversation context:\n{conversation_context[:700]}\n\nLinguistic analysis:\n{linguistic_analysis[:700]}\n\nResponse plan:\n{response_plan[:450]}\n\nLanguage profile evidence:\n{profile}\n\nRelevant corpus evidence:\n{relevant}""".strip()


def strict_repair_prompt(reply: str, violations: list[dict], max_chars: int = 4200) -> str:
    inv = lexical_inventory()
    mappings = []
    for v in violations:
        if v.get("standard"):
            mappings.append(f"{v['standard']} -> {v.get('melimi', '')}")
        else:
            mappings.append(f"{v.get('loan', '')} -> no registered Melimi form")
    known = "\n".join(f"{k} -> {v}" for k, v in list(inv["standard_to_melimi"].items())[:60])
    return f"""MELIMI FINAL REPAIR — TARGETED EDIT ONLY

Fix the answer with the smallest possible edits. Preserve grammar, word order
and meaning. Output only the corrected answer.

Detected violations:\n{chr(10).join(mappings)}

Useful registered mappings:\n{known}

Original answer:\n{reply[:max_chars]}""".strip()
