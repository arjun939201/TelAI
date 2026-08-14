
import re
from typing import Dict, List


TELUGU_RE = re.compile(r"[\u0C00-\u0C7F]+")

CASE_SUFFIXES = [
    "లతో", "లలో", "లకు", "లను", "లని", "లపై", "లకై",
    "నుంచి", "నుండి", "యొక్క", "తోటి", "తో", "లో", "లు", "ను",
    "ని", "కు", "కి", "గా", "పై", "పైన", "లోని", "కోసం", "వల్ల", "మధ్య", "గురించి",
    "ల",
]

# Longest-suffix-first order, precomputed once so callers doing repeated
# suffix stripping (e.g. per-token Melimi lexical substitution) don't have to
# re-sort on every call.
CASE_SUFFIXES_BY_LENGTH = sorted(CASE_SUFFIXES, key=len, reverse=True)


def analyze_surface_form(word: str) -> Dict:
    surface = (word or "").strip()
    result = {
        "surface": surface,
        "base_candidates": [surface] if surface else [],
        "number": "singular",
        "case": None,
    }
    if not surface:
        return result

    for suffix in sorted(CASE_SUFFIXES, key=len, reverse=True):
        if surface.endswith(suffix) and len(surface) > len(suffix) + 1:
            result["base_candidates"].append(surface[:-len(suffix)])
            result["case"] = suffix
            if suffix.startswith("ల"):
                result["number"] = "plural"
            break
    return result


def analyze_text(text: str, vocabulary: List[Dict]) -> List[Dict]:
    results = []
    for word in TELUGU_RE.findall(text or ""):
        analysis = analyze_surface_form(word)
        bases = set(analysis["base_candidates"])
        matches = []
        for entry in vocabulary:
            melimi = str(entry.get("melimi", "")).strip()
            if not melimi:
                continue
            if any(melimi == base or base.startswith(melimi) for base in bases):
                matches.append(entry)
        if matches:
            results.append({"surface": word, "matches": matches[:5]})
    return results
