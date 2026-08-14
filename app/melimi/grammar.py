from typing import Dict, List


# Melimi derivational suffixes are category-sensitive.  These are policy
# metadata used to guide generation; the full authoritative examples remain
# in melimi_telugu/corpus and word_formation rules.
NOUN_SUFFIXES = {
    "కాను": "noun-based characterizing/agentive formation; meaning depends on the base noun",
    "కాన్": "noun-based characterizing/agentive formation; meaning depends on the base noun",
    "మారి": "noun-based quality/characteristic formation; meaning depends on the base noun",
    "వాను": "noun-based having/related-to formation; meaning depends on the base noun",
    "వాన్": "noun-based having/related-to formation; meaning depends on the base noun",
    "పాదు": "noun-based worthy/suitable-for formation; meaning depends on the base noun",
    "పఱ": "noun-based unsuitable/not-worthy-of formation; meaning depends on the base noun",
    "మాలు": "noun-based absence/lacking formation",
    "కము": "noun-based abstract/nominal formation",
    "ఇకము": "noun-based abstract/nominal formation",
    "గము": "noun-based whole/group formation",
    "ఓరు": "noun-based institution/system formation",
    "ఆది": "noun-based whole/collection/group formation",
    "ఓలి": "noun-based sequence/series formation",
    "ఓజ": "noun/verb-based method/style/order formation where the corpus supports it",
    "అంగి": "noun/root-based derivational family; meaning depends on the documented base",
}

VERB_SUFFIXES = {
    "అలవి": "verb-based doable/possible/suitable/worthy-of formation",
    "అల్వి": "verb-based doable/possible/suitable/worthy-of formation",
    "అరిది": "verb-based not-doable/not-possible/not-suitable formation",
    "అర్ది": "verb-based not-doable/not-possible/not-suitable formation",
}

# Some Melimi lexical forms are deliberately invariant between nominal and
# adjectival use.  In particular, a form that does not end in the Telugu
# nasal/am ending ("ం") can function directly as an adjective when the
# corpus supports that lexical item.
INVARIANT_NOUN_ADJECTIVE_RULE = (
    "Relevant Melimi lexical forms that do NOT end in ం (the am/nasal ending) "
    "may function directly as both nouns and adjectives without adding a new "
    "adjective suffix. Example: హాళికాను = ఆసక్తికరం / ఆసక్తికరమైన. The same "
    "Melimi surface form remains హాళికాను in predicate and attributive use. "
    "Do not mechanically add ము, పు, మైన, or another adjective suffix."
)

# Retained as a compatibility view for callers that only need a flat list.
DERIVATIONAL_MARKERS = {**NOUN_SUFFIXES, **VERB_SUFFIXES}


def grammar_policy() -> str:
    lines = [
        "MELIMI GRAMMAR/WORD-FORMATION POLICY:",
        "- Use native Telugu lexical material for Melimi expression and prefer established Melimi forms.",
        "- Do not invent a Melimi word merely to avoid a Standard Telugu word when the corpus has no supported equivalent.",
        "- Noun-based suffixes attach to nouns/nominal bases and change the whole meaning according to the base word; do not interpret them as independent word replacements.",
        "- Verb-based suffixes such as అలవి/అల్వి and అరిది/అర్ది attach to verb bases; do not attach them indiscriminately to nouns.",
        "- Productive derivation is valid only where the supplied Melimi corpus/rules support the formation.",
        "- Preserve ordinary Telugu grammar, word order, tense, case, number, person and agreement.",
        f"- NOUN-BASED SUFFIXES: {', '.join(NOUN_SUFFIXES)}",
        f"- VERB-BASED SUFFIXES: {', '.join(VERB_SUFFIXES)}",
        f"- NOUN/ADJECTIVE DUAL-FUNCTION RULE: {INVARIANT_NOUN_ADJECTIVE_RULE}",
        "- A Standard Telugu adjective ending in -మైన may correspond to the same invariant Melimi lexical form when that Melimi form is a supported non-ం/nasal-ending adjective-capable form; do not manufacture a separate -మైన form.",
        "- Do not treat every non-ం/nasal-ending word as automatically adjective-capable; use the corpus/lexical evidence for the relevant word.",
    ]
    return "\n".join(lines)


def audit_derivational_surface(text: str) -> List[Dict]:
    return [
        {"form": suffix, "rule": meaning}
        for suffix, meaning in DERIVATIONAL_MARKERS.items()
        if suffix in (text or "")
    ]


def is_non_am_ending_melimi(word: str) -> bool:
    """Return whether a Melimi surface form is not ended by Telugu ం.

    The project describes this as the non-'am' ending class. This helper is
    intentionally lexical/surface-only; it does not claim that every such
    word is automatically adjective-capable.
    """
    word = (word or "").strip()
    return bool(word) and not word.endswith("ం")
