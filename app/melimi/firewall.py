
from __future__ import annotations
import re
from functools import lru_cache
from app.melimi.index import build_index
from app.morphology import CASE_SUFFIXES_BY_LENGTH
from app.melimi.grammar import is_non_am_ending_melimi

TOKEN_RE = re.compile(r"[\u0C00-\u0C7F]+|[A-Za-z]+(?:['’-][A-Za-z]+)*")

# Accepted field-name aliases in a vocabulary entry, so richer/varied source
# data (synonym lists, alternate key names) is still picked up. This is a
# deterministic, file-derived list only — it never invents a mapping.
_STANDARD_KEYS = ("standard", "standard_or_source", "source_word")
_MELIMI_KEYS = ("melimi", "word", "headword")


def _as_list(value):
    if isinstance(value, list):
        return [str(x).strip() for x in value if str(x).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


@lru_cache(maxsize=1)
def subject_lexicon():
    forbidden = {}
    preferred = {}
    registered = set()
    adjective_capable = set()
    for doc in build_index():
        if doc.kind != "vocabulary":
            continue
        for entry in doc.entries:
            standards = []
            for key in _STANDARD_KEYS:
                standards.extend(_as_list(entry.get(key)))
            melimis = []
            for key in _MELIMI_KEYS:
                melimis.extend(_as_list(entry.get(key)))
            if not standards or not melimis:
                continue
            # The canonical Melimi form is the first supplied one; any
            # additional standard-side variants (synonyms) all map to it.
            m = melimis[0]
            registered.add(m)
            if entry.get("adjective_invariant") is True or (
                isinstance(entry.get("functions"), list)
                and "adjective" in [str(x).strip().lower() for x in entry.get("functions", [])]
                and is_non_am_ending_melimi(m)
            ):
                for s in standards:
                    adjective_capable.add((s, m))
            for s in standards:
                forbidden[s] = m
                preferred[s] = m
    return {"forbidden": forbidden, "preferred": preferred, "registered": registered, "adjective_capable": adjective_capable}


def reload_firewall():
    subject_lexicon.cache_clear()


def _match_root(token: str, forbidden: dict, adjective_capable=None):
    """Decompose a surface Telugu token into (root, suffix) against the
    authoritative Standard->Melimi root mapping.

    This is a root-level lookup, not a substring/global replace: the token is
    only ever split using a real Telugu case/plural suffix (from the shared
    morphology suffix table), and the remaining root must be an EXACT,
    file-registered Standard Telugu word. Nothing is guessed or invented.

    Returns (root, suffix, melimi_root) or None if the token (as a whole, or
    as root+suffix) isn't a registered mapping.
    """
    # 1) Exact, unsuffixed match (e.g. "సమస్య" -> "చిక్కు").
    if token in forbidden:
        return token, "", forbidden[token]

    # 2) root + known grammatical suffix (plural/case), longest suffix first
    #    so e.g. "లను" is preferred over stripping just "ను".
    for suffix in CASE_SUFFIXES_BY_LENGTH:
        if not token.endswith(suffix):
            continue
        root = token[: -len(suffix)]
        if root and root in forbidden:
            return root, suffix, forbidden[root]

    # 3) Predicative/adverbial adjective surface form. A Standard Telugu
    #    form such as ఆసక్తికరంగా is related to the headword ఆసక్తికరం. For
    #    an invariant non-ం Melimi adjective, retain the ordinary -గా
    #    grammatical ending: హాళికరంగా -> (headword) -> హాళికానుగా.
    if token.endswith("గా") and len(token) > 3:
        stem = token[:-2]
        headword = stem + "ం"
        if headword in forbidden:
            melimi_root = forbidden[headword]
            capable = adjective_capable or set()
            if (headword, melimi_root) in capable and is_non_am_ending_melimi(melimi_root):
                return headword, "గా", melimi_root

    # 3) Attributive adjective surface form.  A Standard Telugu adjective
    #    such as ఆసక్తికరమైన is related to the dictionary headword ఆసక్తికరం.
    #    When that headword maps to a Melimi form that belongs to the
    #    non-"am"/non-ం ending class, the Melimi form itself can serve as the
    #    adjective without adding -మైన/-ము/-పు.  This is deliberately
    #    conservative: only a real registered headword is considered.
    if token.endswith("మైన") and len(token) > 3:
        headword = token[:-3] + "ం"
        if headword in forbidden:
            melimi_root = forbidden[headword]
            capable = adjective_capable or set()
            if (headword, melimi_root) in capable and is_non_am_ending_melimi(melimi_root):
                return headword, "", melimi_root
    return None


def lexical_violations(text: str):
    lex = subject_lexicon()
    forbidden = lex["forbidden"]
    found = []
    seen = set()
    for token in TOKEN_RE.findall(text or ""):
        match = _match_root(token, forbidden, lex.get("adjective_capable"))
        if not match:
            continue
        root, suffix, melimi_root = match
        key = (token, melimi_root + suffix)
        if key in seen:
            continue
        seen.add(key)
        found.append({
            "source": token,
            "preferred": melimi_root + suffix,
            "root": root,
            "suffix": suffix,
        })
    return found


def deterministic_repair(text: str) -> str:
    """Final safety net for lexical items explicitly defined by files.

    This performs targeted, root-aware word substitution: each Standard
    Telugu word — in its bare form or with a Telugu grammatical suffix
    (plural, case marker, etc.) attached — is swapped for its registered
    Melimi root with that same suffix reattached, in place. The suffix is
    never invented; it is the exact suffix already present on the word in
    the model's own output, so grammatical case/number is preserved exactly.
    Every other word, and the sentence's grammar/word order, is left
    completely untouched. It is deliberately limited to exact,
    file-registered vocabulary roots — it is not a general/global
    word-replacement engine.
    """
    lex = subject_lexicon()
    forbidden = lex["forbidden"]

    def _replace(match: re.Match) -> str:
        token = match.group(0)
        invariant = None
        # Only forms explicitly marked adjective-capable are eligible.
        for _, melimi in lex.get("adjective_capable", set()):
            if token in {melimi + "మైన", melimi + "ము", melimi + "పు"}:
                invariant = melimi
                break
        if invariant:
            return invariant
        result = _match_root(token, forbidden, lex.get("adjective_capable"))
        if not result:
            return token
        root, suffix, melimi_root = result
        return melimi_root + suffix

    return TOKEN_RE.sub(_replace, text)
