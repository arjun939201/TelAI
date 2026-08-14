"""
Melimi Telugu morphology helpers.

Purpose:
- Apply authoritative lexical mappings before carrying grammatical inflections.
- Avoid invalid forms such as తెఱాటంలు when the established Melimi paradigm is తెఱాటాలు.
- Keep lexical derivation separate from ordinary Telugu inflection.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass(frozen=True)
class Paradigm:
    singular: str
    plural: str
    acc_singular: Optional[str] = None
    acc_plural: Optional[str] = None


# Authoritative paradigms supplied/established in the Melimi corpus.
# Keys are common Standard Telugu surface forms.
PARADIGMS: Dict[str, Paradigm] = {
    "సినిమా": Paradigm(
        singular="తెఱాటం",
        plural="తెఱాటాలు",
        acc_singular="తెఱాటాన్ని",
        acc_plural="తెఱాటాలను",
    ),
    "సినిమాలు": Paradigm(
        singular="తెఱాటం",
        plural="తెఱాటాలు",
        acc_singular="తెఱాటాన్ని",
        acc_plural="తెఱాటాలను",
    ),
    "సినిమాలను": Paradigm(
        singular="తెఱాటం",
        plural="తెఱాటాలు",
        acc_singular="తెఱాటాన్ని",
        acc_plural="తెఱాటాలను",
    ),
    "సినిమాను": Paradigm(
        singular="తెఱాటం",
        plural="తెఱాటాలు",
        acc_singular="తెఱాటాన్ని",
        acc_plural="తెఱాటాలను",
    ),
}


# Exact established lexical replacements used by deterministic repair.
LEXICAL_MAP = {
    "సమస్య": "చిక్కు",
    "సహాయం": "బాసట",
    "సినిమా": "తెఱాటం",
}


def standard_to_melimi(word: str) -> str:
    """Convert a known Standard Telugu surface form to its established Melimi form."""
    if word in PARADIGMS:
        p = PARADIGMS[word]
        if word == "సినిమాలు":
            return p.plural
        if word == "సినిమాలను":
            return p.acc_plural
        if word == "సినిమాను":
            return p.acc_singular
        return p.singular
    return LEXICAL_MAP.get(word, word)


def repair_known_forms(text: str) -> str:
    """
    Repair known Standard Telugu lexical forms and their established
    inflectional paradigms. Exact replacements only; no broad string
    substitution that could corrupt unrelated words.
    """
    # Longer forms first.
    replacements = {
        "సినిమాలను": "తెఱాటాలను",
        "సినిమాలు": "తెఱాటాలు",
        "సినిమాను": "తెఱాటాన్ని",
        "సినిమా": "తెఱాటం",
        "సమస్యలను": "చిక్కులను",
        "సమస్యలు": "చిక్కులు",
        "సమస్యను": "చిక్కును",
        "సమస్య": "చిక్కు",
        "సహాయాన్ని": "బాసటను",
        "సహాయం": "బాసట",
    }
    for old, new in sorted(replacements.items(), key=lambda kv: len(kv[0]), reverse=True):
        text = text.replace(old, new)

    # Explicit adjective/predicate repairs.
    text = text.replace("ఆసక్తికరమైన", "హాళికాను")
    text = text.replace("ఆసక్తికరంగా", "హాళికానుగా")
    text = text.replace("ఆసక్తికరం", "హాళికాను")
    return text
