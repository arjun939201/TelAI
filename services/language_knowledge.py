"""
services/language_knowledge.py

Responsibilities:
1. Load Melimi <-> standard Telugu vocabulary mappings from language/*.txt files.
2. Cache the parsed mappings in memory, invalidating the cache only when the
   underlying files change (so we don't re-parse on every request).
3. Provide a SMALL, capped "knowledge context" string that can optionally be
   given to Groq for style/tone purposes (NOT the full corpus — this is what
   was causing your 413 errors).
4. Provide a deterministic, safe replacement function that swaps established
   standard Telugu words for their Melimi equivalents in a generated response,
   without touching URLs, code, file paths, or inventing new words.

File format expected in language/*.txt (one mapping per line):
    బాసట = సహాయం
i.e.  MelimiWord = StandardWord
Blank lines and lines starting with '#' are ignored.
"""

import os
import re
import glob
import threading

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

LANGUAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "language")

# Hard cap on how much vocabulary text we ever hand to Groq as "context".
# This is a STYLE SAMPLE only, not the mapping table used for replacement.
MAX_KNOWLEDGE_CONTEXT_CHARS = 1200

# How many sample mappings to show Groq (kept tiny on purpose).
MAX_KNOWLEDGE_CONTEXT_ENTRIES = 25

_lock = threading.Lock()
_cache = {
    "mtime_signature": None,
    "mappings": [],          # list of (standard_word, melimi_word), longest standard first
    "knowledge_context": "",  # small capped sample string for Groq
}


# ---------------------------------------------------------------------------
# Loading & caching
# ---------------------------------------------------------------------------

def _language_files():
    if not os.path.isdir(LANGUAGE_DIR):
        return []
    return sorted(glob.glob(os.path.join(LANGUAGE_DIR, "*.txt")))


def _current_mtime_signature(files):
    """A cheap signature of (path, mtime, size) so we know when to reload."""
    sig = []
    for f in files:
        try:
            stat = os.stat(f)
            sig.append((f, stat.st_mtime_ns, stat.st_size))
        except OSError:
            continue
    return tuple(sig)


def _parse_file(path):
    """Parse a single vocabulary file into (standard, melimi) pairs."""
    pairs = []
    try:
        with open(path, "r", encoding="utf-8") as fh:
            for raw_line in fh:
                line = raw_line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    continue
                melimi_part, standard_part = line.split("=", 1)
                melimi_word = melimi_part.strip()
                standard_word = standard_part.strip()
                if melimi_word and standard_word:
                    pairs.append((standard_word, melimi_word))
    except OSError:
        pass
    return pairs


def _load_all_mappings():
    """
    Load and merge mappings from every file in language/.
    De-duplicates by standard_word (last file wins on conflict).
    Sorts longest standard_word first so multi-word phrases are replaced
    before shorter/overlapping single-word mappings.
    """
    files = _language_files()
    merged = {}
    for f in files:
        for standard_word, melimi_word in _parse_file(f):
            merged[standard_word] = melimi_word

    mappings = list(merged.items())
    # Longer phrases (by character length, then word count) processed first.
    mappings.sort(key=lambda pair: (len(pair[0]), pair[0].count(" ")), reverse=True)
    return mappings, files


def _build_knowledge_context(mappings):
    """
    Build a SMALL sample of vocabulary to optionally give Groq for tone/style
    purposes. This is intentionally capped and is NEVER the full corpus.
    """
    if not mappings:
        return ""

    sample = mappings[:MAX_KNOWLEDGE_CONTEXT_ENTRIES]
    lines = [f"{melimi} = {standard}" for standard, melimi in sample]
    context = "\n".join(lines)

    if len(context) > MAX_KNOWLEDGE_CONTEXT_CHARS:
        context = context[:MAX_KNOWLEDGE_CONTEXT_CHARS]
        # Trim back to the last full line so we don't cut a mapping in half.
        last_newline = context.rfind("\n")
        if last_newline > 0:
            context = context[:last_newline]

    return context


def get_mappings():
    """Return the cached (standard, melimi) mapping list, reloading if files changed."""
    files = _language_files()
    sig = _current_mtime_signature(files)

    with _lock:
        if _cache["mtime_signature"] != sig:
            mappings, _ = _load_all_mappings()
            _cache["mappings"] = mappings
            _cache["knowledge_context"] = _build_knowledge_context(mappings)
            _cache["mtime_signature"] = sig
        return _cache["mappings"]


def get_knowledge_context():
    """
    Return the small, capped vocabulary sample suitable for inclusion in a
    Groq system prompt. Guaranteed to stay under MAX_KNOWLEDGE_CONTEXT_CHARS
    regardless of how large language/ grows.
    """
    get_mappings()  # ensures cache is fresh
    with _lock:
        return _cache["knowledge_context"]


def reload_now():
    """Force a reload on next access (useful after deploying new vocab files)."""
    with _lock:
        _cache["mtime_signature"] = None


# ---------------------------------------------------------------------------
# Deterministic replacement layer
# ---------------------------------------------------------------------------

# Segments we must never touch during replacement.
_PROTECT_PATTERNS = [
    re.compile(r"```.*?```", re.DOTALL),          # fenced code blocks
    re.compile(r"`[^`\n]+`"),                       # inline code
    re.compile(r"https?://\S+"),                    # URLs
    re.compile(r"www\.\S+"),                         # URLs without scheme
    re.compile(r"(?:[./\\][\w.\-]+){2,}"),           # file paths like a/b/c.py
    re.compile(r"\b[\w.\-]+/[\w./\-]+\b"),           # generic path-like tokens
]

_PLACEHOLDER_TEMPLATE = "\x00PROTECT{}\x00"


def _protect_segments(text):
    """
    Replace protected segments (URLs, code, paths) with placeholders so the
    vocabulary substitution never touches them. Returns (masked_text, store).
    """
    store = []

    def _mask(match):
        idx = len(store)
        store.append(match.group(0))
        return _PLACEHOLDER_TEMPLATE.format(idx)

    masked = text
    for pattern in _PROTECT_PATTERNS:
        masked = pattern.sub(_mask, masked)

    return masked, store


def _restore_segments(text, store):
    for idx, original in enumerate(store):
        text = text.replace(_PLACEHOLDER_TEMPLATE.format(idx), original)
    return text


def _build_word_pattern(standard_word):
    """
    Build a regex that matches `standard_word` as a whole word/phrase,
    correctly handling Telugu script and adjacent punctuation.
    """
    escaped = re.escape(standard_word)
    # \b works with Telugu letters in Python's unicode-aware re engine,
    # since Telugu characters are classified as word characters.
    return re.compile(r"(?<!\w)" + escaped + r"(?!\w)")


def apply_melimi_replacements(response_text):
    """
    Deterministically replace established standard Telugu words/phrases in
    `response_text` with their corresponding Melimi words, using ONLY the
    mappings found in language/*.txt.

    Guarantees:
    - Only established mappings are used (never invents new Melimi words).
    - Longer/multi-word mappings are applied before shorter ones.
    - URLs, code, and file paths are left untouched.
    - Words with no mapping are left unchanged.
    - Punctuation adjacent to a replaced word is preserved.
    """
    if not response_text:
        return response_text

    mappings = get_mappings()
    if not mappings:
        return response_text

    masked_text, store = _protect_segments(response_text)

    for standard_word, melimi_word in mappings:
        pattern = _build_word_pattern(standard_word)
        masked_text = pattern.sub(melimi_word, masked_text)

    return _restore_segments(masked_text, store)
