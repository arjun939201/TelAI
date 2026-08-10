"""
services/language_knowledge.py

Loads Melimi Telugu vocabulary mappings from language/*.txt files.

File format:

    బాసట = సహాయం
from pathlib import Path
import re
import threading

BASE_DIR = Path(__file__).resolve().parent.parent
LANGUAGE_DIR = BASE_DIR / "language"

MAX_CONTEXT_CHARS = 7000
MAX_HISTORY_CHARS = 6000

_lock = threading.Lock()

_cache = {
    "signature": None,
    "vocabulary": [],
    "grammar": "",
    "basic_grammar": "",
    "replacements": [],
    "suggestions": "",
}


def _read_file(filename):
    path = LANGUAGE_DIR / filename

    if not path.exists() or not path.is_file():
        return ""

    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _parse_mappings(text):
    result = []

    for line in text.splitlines():
        line = line.strip()

        if not line or line.startswith("#") or "=" not in line:
            continue

        left, right = line.split("=", 1)

        left = left.strip()
        right = right.strip()

        if left and right:
            result.append((left, right))

    return result


def _signature():
    files = [
        LANGUAGE_DIR / "vocabulary.txt",
        LANGUAGE_DIR / "grammar.txt",
        LANGUAGE_DIR / "basic-grammar.txt",
        LANGUAGE_DIR / "replacements.txt",
        LANGUAGE_DIR / "suggestions.txt",
    ]

    result = []

    for path in files:
        try:
            stat = path.stat()
            result.append((str(path), stat.st_mtime_ns, stat.st_size))
        except OSError:
            result.append((str(path), 0, 0))

    return tuple(result)


def _load():
    vocabulary_text = _read_file("vocabulary.txt")
    grammar_text = _read_file("grammar.txt")
    basic_grammar_text = _read_file("basic-grammar.txt")
    replacements_text = _read_file("replacements.txt")
    suggestions_text = _read_file("suggestions.txt")

    _cache["vocabulary"] = _parse_mappings(vocabulary_text)
    _cache["grammar"] = grammar_text
    _cache["basic_grammar"] = basic_grammar_text
    _cache["replacements"] = _parse_mappings(replacements_text)
    _cache["suggestions"] = suggestions_text


def _ensure_loaded():
    signature = _signature()

    with _lock:
        if _cache["signature"] != signature:
            _load()
            _cache["signature"] = signature


def get_vocabulary():
    _ensure_loaded()
    return list(_cache["vocabulary"])


def get_replacements():
    _ensure_loaded()
    return list(_cache["replacements"])


def get_grammar():
    _ensure_loaded()
    return _cache["grammar"]


def get_basic_grammar():
    _ensure_loaded()
    return _cache["basic_grammar"]


def _keywords(text):
    words = re.findall(r"[\u0C00-\u0C7F]+", text or "")
    return {word for word in words if len(word) >= 2}


def _score_line(line, keywords):
    if not keywords:
        return 0

    score = 0

    for word in keywords:
        if word in line:
            score += 1

    return score


def _relevant_lines(text, query, limit=80):
    if not text:
        return []

    keywords = _keywords(query)

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
        and not line.strip().startswith("#")
    ]

    if not keywords:
        return lines[:limit]

    scored = []

    for index, line in enumerate(lines):
        score = _score_line(line, keywords)

        if score:
            scored.append((score, index, line))

    scored.sort(
        key=lambda item: (item[0], -item[1]),
        reverse=True,
    )

    selected = [item[2] for item in scored[:limit]]

    if len(selected) < limit:
        for line in lines:
            if line not in selected:
                selected.append(line)

            if len(selected) >= limit:
                break

    return selected[:limit]


def _relevant_vocabulary(query, limit=80):
    vocabulary = get_vocabulary()
    replacements = get_replacements()

    combined = vocabulary + replacements

    keywords = _keywords(query)

    if not keywords:
        return combined[:limit]

    scored = []

    for index, (melimi, meaning) in enumerate(combined):
        score = 0

        for keyword in keywords:
            if keyword in melimi or keyword in meaning:
                score += 1

        if score:
            scored.append((score, index, melimi, meaning))

    scored.sort(
        key=lambda item: (item[0], -item[1]),
        reverse=True,
    )

    result = [
        (item[2], item[3])
        for item in scored[:limit]
    ]

    if len(result) < limit:
        for item in combined:
            if item not in result:
                result.append(item)

            if len(result) >= limit:
                break

    return result[:limit]


def get_relevant_knowledge(query):
    _ensure_loaded()

    vocabulary = _relevant_vocabulary(query, 80)
    grammar = _relevant_lines(
        _cache["grammar"],
        query,
        45,
    )
    basic_grammar = _relevant_lines(
        _cache["basic_grammar"],
        query,
        30,
    )

    parts = []

    if vocabulary:
        parts.append("APPROVED MELIMI VOCABULARY:")

        for melimi, meaning in vocabulary:
            parts.append(f"{melimi} = {meaning}")

    if grammar:
        parts.append("")
        parts.append("MELIMI GRAMMAR RULES:")
        parts.extend(grammar)

    if basic_grammar:
        parts.append("")
        parts.append("BASIC MELIMI GRAMMAR:")
        parts.extend(basic_grammar)

    context = "\n".join(parts)

    if len(context) > MAX_CONTEXT_CHARS:
        context = context[:MAX_CONTEXT_CHARS]

        last_break = context.rfind("\n")

        if last_break > 0:
            context = context[:last_break]

    return context


_PROTECT_PATTERNS = [
    re.compile(r"```.*?```", re.DOTALL),
    re.compile(r"`[^`\n]+`"),
    re.compile(r"https?://\S+"),
    re.compile(r"www\.\S+"),
]


def _protect(text):
    stored = []

    def replace(match):
        index = len(stored)
        stored.append(match.group(0))
        return f"\x00TELAI_PROTECTED_{index}\x00"

    result = text

    for pattern in _PROTECT_PATTERNS:
        result = pattern.sub(replace, result)

    return result, stored


def _restore(text, stored):
    for index, value in enumerate(stored):
        text = text.replace(
            f"\x00TELAI_PROTECTED_{index}\x00",
            value,
        )

    return text


def _word_pattern(word):
    return re.compile(
        r"(?<![\u0C00-\u0C7F\w])"
        + re.escape(word)
        + r"(?![\u0C00-\u0C7F\w])"
    )


def apply_melimi_replacements(text):
    if not text:
        return text

    replacements = get_replacements()

    if not replacements:
        return text

    masked, stored = _protect(text)

    replacements = sorted(
        replacements,
        key=lambda item: len(item[1]),
        reverse=True,
    )

    for melimi, standard in replacements:
        pattern = _word_pattern(standard)
        masked = pattern.sub(melimi, masked)

    return _restore(masked, stored)


def reload_now():
    with _lock:
        _cache["signature"] = None
Meaning:

    Melimi word = standard Telugu word
"""

from pathlib import Path
import re
import threading


# ============================================================
# LANGUAGE DIRECTORY
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

LANGUAGE_DIR = BASE_DIR / "language"


# ============================================================
# CONFIGURATION
# ============================================================

MAX_KNOWLEDGE_CONTEXT_CHARS = 1200

MAX_KNOWLEDGE_CONTEXT_ENTRIES = 25


_lock = threading.Lock()


_cache = {
    "mtime_signature": None,
    "mappings": [],
    "knowledge_context": "",
}


# ============================================================
# LANGUAGE FILES
# ============================================================

def _language_files():
    """
    Return all supported language text files.
    """

    if not LANGUAGE_DIR.exists():
        return []

    return sorted(
        LANGUAGE_DIR.glob("*.txt")
    )


def get_language_files():
    """
    Return available language files.

    Used by routes/language.py.
    """

    files = _language_files()

    result = []

    for file_path in files:

        try:

            result.append(
                {
                    "name": file_path.name,
                    "path": file_path.name,
                }
            )

        except OSError:
            continue

    return result


# ============================================================
# FILE CHANGE DETECTION
# ============================================================

def _current_mtime_signature(files):

    signature = []

    for file_path in files:

        try:

            stat = file_path.stat()

            signature.append(
                (
                    str(file_path),
                    stat.st_mtime_ns,
                    stat.st_size,
                )
            )

        except OSError:
            continue

    return tuple(signature)


# ============================================================
# FILE PARSER
# ============================================================

def _parse_file(path):

    pairs = []

    try:

        with path.open(
            "r",
            encoding="utf-8"
        ) as file:

            for raw_line in file:

                line = raw_line.strip()

                if not line:
                    continue

                if line.startswith("#"):
                    continue

                if "=" not in line:
                    continue

                melimi_part, standard_part = line.split(
                    "=",
                    1
                )

                melimi_word = melimi_part.strip()

                standard_word = standard_part.strip()

                if not melimi_word:
                    continue

                if not standard_word:
                    continue

                pairs.append(
                    (
                        standard_word,
                        melimi_word
                    )
                )

    except OSError:
        pass

    return pairs


# ============================================================
# LOAD ALL MAPPINGS
# ============================================================

def _load_all_mappings():

    files = _language_files()

    merged = {}

    for file_path in files:

        for standard_word, melimi_word in _parse_file(
            file_path
        ):

            merged[standard_word] = melimi_word


    mappings = list(
        merged.items()
    )


    # Longer phrases first.

    mappings.sort(
        key=lambda pair: (
            len(pair[0]),
            pair[0].count(" ")
        ),
        reverse=True
    )


    return mappings, files


# ============================================================
# GROQ KNOWLEDGE SAMPLE
# ============================================================

def _build_knowledge_context(mappings):

    if not mappings:
        return ""

    sample = mappings[
        :MAX_KNOWLEDGE_CONTEXT_ENTRIES
    ]

    lines = []

    for standard_word, melimi_word in sample:

        lines.append(
            f"{melimi_word} = {standard_word}"
        )

    context = "\n".join(
        lines
    )


    if len(context) > MAX_KNOWLEDGE_CONTEXT_CHARS:

        context = context[
            :MAX_KNOWLEDGE_CONTEXT_CHARS
        ]

        last_newline = context.rfind(
            "\n"
        )

        if last_newline > 0:

            context = context[
                :last_newline
            ]

    return context


# ============================================================
# CACHE
# ============================================================

def get_mappings():

    files = _language_files()

    signature = _current_mtime_signature(
        files
    )


    with _lock:

        if (
            _cache["mtime_signature"]
            != signature
        ):

            mappings, _ = _load_all_mappings()

            _cache["mappings"] = mappings

            _cache[
                "knowledge_context"
            ] = _build_knowledge_context(
                mappings
            )

            _cache[
                "mtime_signature"
            ] = signature


        return _cache[
            "mappings"
        ]


def get_knowledge_context():

    get_mappings()

    with _lock:

        return _cache[
            "knowledge_context"
        ]


def reload_now():

    with _lock:

        _cache[
            "mtime_signature"
        ] = None


# ============================================================
# PROTECTED CONTENT
# ============================================================

_PROTECT_PATTERNS = [

    # Markdown code blocks
    re.compile(
        r"```.*?```",
        re.DOTALL
    ),

    # Inline code
    re.compile(
        r"`[^`\n]+`"
    ),

    # URLs
    re.compile(
        r"https?://\S+"
    ),

    re.compile(
        r"www\.\S+"
    ),

    # File paths
    re.compile(
        r"(?:[./\\][\w.\-]+){2,}"
    ),

    # Generic paths
    re.compile(
        r"\b[\w.\-]+/[\w./\-]+\b"
    ),
]


_PLACEHOLDER_TEMPLATE = (
    "\x00PROTECT{}\x00"
)


# ============================================================
# PROTECT
# ============================================================

def _protect_segments(text):

    store = []

    def mask(match):

        index = len(store)

        store.append(
            match.group(0)
        )

        return _PLACEHOLDER_TEMPLATE.format(
            index
        )


    masked = text

    for pattern in _PROTECT_PATTERNS:

        masked = pattern.sub(
            mask,
            masked
        )


    return masked, store


# ============================================================
# RESTORE
# ============================================================

def _restore_segments(
    text,
    store
):

    for index, original in enumerate(store):

        text = text.replace(
            _PLACEHOLDER_TEMPLATE.format(
                index
            ),
            original
        )

    return text


# ============================================================
# WORD PATTERN
# ============================================================

def _build_word_pattern(
    standard_word
):

    escaped = re.escape(
        standard_word
    )

    return re.compile(
        r"(?<!\w)"
        + escaped
        + r"(?!\w)"
    )


# ============================================================
# MELIMI REPLACEMENT
# ============================================================

def apply_melimi_replacements(
    response_text
):

    if not response_text:
        return response_text


    mappings = get_mappings()

    if not mappings:
        return response_text


    masked_text, store = _protect_segments(
        response_text
    )


    for standard_word, melimi_word in mappings:

        pattern = _build_word_pattern(
            standard_word
        )

        masked_text = pattern.sub(
            melimi_word,
            masked_text
        )


    return _restore_segments(
        masked_text,
        store
    )
