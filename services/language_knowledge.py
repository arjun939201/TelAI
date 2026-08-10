from pathlib import Path
import re
import threading


BASE_DIR = Path(__file__).resolve().parent.parent
LANGUAGE_DIR = BASE_DIR / "language"

def get_language_files():
    """Return available Melimi language files."""

    if not LANGUAGE_DIR.exists():
        return []

    files = []

    for path in sorted(LANGUAGE_DIR.glob("*.txt")):

        files.append({
            "name": path.name,
            "path": path.name
        })

    return files
MAX_KNOWLEDGE_CONTEXT_CHARS = 7000
MAX_RELEVANT_ENTRIES = 40

_lock = threading.Lock()

_cache = {
    "signature": None,
    "vocabulary": [],
    "replacements": [],
    "grammar": "",
    "basic_grammar": "",
}


def _read_file(filename):
    path = LANGUAGE_DIR / filename

    if not path.exists():
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
        LANGUAGE_DIR / "replacements.txt",
        LANGUAGE_DIR / "grammar.txt",
        LANGUAGE_DIR / "basic-grammar.txt",
    ]

    result = []

    for path in files:
        try:
            stat = path.stat()

            result.append(
                (
                    str(path),
                    stat.st_mtime_ns,
                    stat.st_size,
                )
            )

        except OSError:
            result.append(
                (
                    str(path),
                    0,
                    0,
                )
            )

    return tuple(result)


def _load():
    _cache["vocabulary"] = _parse_mappings(
        _read_file("vocabulary.txt")
    )

    _cache["replacements"] = _parse_mappings(
        _read_file("replacements.txt")
    )

    _cache["grammar"] = _read_file(
        "grammar.txt"
    )

    _cache["basic_grammar"] = _read_file(
        "basic-grammar.txt"
    )


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


# ============================================================
# ROMAN TELUGU
# ============================================================

def _normalize_roman(text):
    text = (text or "").lower().strip()

    text = text.replace("’", "'")
    text = text.replace("ʼ", "'")

    text = re.sub(
        r"[^a-z0-9\s]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


_TELUGU_TO_ROMAN = {
    "అ": "a",
    "ఆ": "aa",
    "ఇ": "i",
    "ఈ": "ee",
    "ఉ": "u",
    "ఊ": "oo",
    "ఋ": "ru",
    "ఎ": "e",
    "ఏ": "ee",
    "ఐ": "ai",
    "ఒ": "o",
    "ఓ": "oo",
    "ఔ": "au",

    "క": "ka",
    "ఖ": "kha",
    "గ": "ga",
    "ఘ": "gha",
    "ఙ": "nga",

    "చ": "cha",
    "ఛ": "chha",
    "జ": "ja",
    "ఝ": "jha",
    "ఞ": "nya",

    "ట": "ta",
    "ఠ": "tha",
    "డ": "da",
    "ఢ": "dha",
    "ణ": "na",

    "త": "ta",
    "థ": "tha",
    "ద": "da",
    "ధ": "dha",
    "న": "na",

    "ప": "pa",
    "ఫ": "pha",
    "బ": "ba",
    "భ": "bha",
    "మ": "ma",

    "య": "ya",
    "ర": "ra",
    "ల": "la",
    "వ": "va",

    "శ": "sha",
    "ష": "sha",
    "స": "sa",
    "హ": "ha",

    "ళ": "la",
    "ఱ": "ra",

    "ం": "m",
    "ః": "h",
    "ఁ": "n",
}


_VOWEL_SIGNS = {
    "ా": "aa",
    "ి": "i",
    "ీ": "ee",
    "ు": "u",
    "ూ": "oo",
    "ృ": "ru",
    "ె": "e",
    "ే": "ee",
    "ై": "ai",
    "ొ": "o",
    "ో": "oo",
    "ౌ": "au",
}


def _telugu_to_roman(text):
    result = []

    i = 0

    while i < len(text):

        char = text[i]

        if char in _VOWEL_SIGNS:
            result.append(
                _VOWEL_SIGNS[char]
            )

            i += 1
            continue

        if char == "్":
            i += 1
            continue

        if char in _TELUGU_TO_ROMAN:

            value = _TELUGU_TO_ROMAN[char]

            if (
                i + 1 < len(text)
                and text[i + 1] == "్"
            ):
                value = value[:-1]

            result.append(value)

        else:
            result.append(char)

        i += 1

    return "".join(result)


def _roman_variants(word):

    roman = _normalize_roman(
        _telugu_to_roman(word)
    )

    variants = {roman}

    replacements = [
        ("aa", "a"),
        ("ee", "e"),
        ("oo", "o"),
        ("th", "t"),
        ("dh", "d"),
        ("ph", "f"),
        ("bh", "b"),
        ("kh", "k"),
        ("gh", "g"),
        ("chh", "ch"),
        ("sha", "sa"),
    ]

    for source, target in replacements:

        variants.add(
            _normalize_roman(
                roman.replace(
                    source,
                    target
                )
            )
        )

    return {
        value
        for value in variants
        if value
    }


def _query_tokens(query):

    telugu_words = re.findall(
        r"[\u0C00-\u0C7F]+",
        query or ""
    )

    roman_words = re.findall(
        r"[A-Za-z]+",
        query or ""
    )

    return [
        word
        for word in (
            telugu_words +
            roman_words
        )
        if len(word) >= 2
    ]


# ============================================================
# EXACT VOCABULARY LOOKUP
# ============================================================

def get_exact_vocabulary_meaning(query):

    _ensure_loaded()

    vocabulary = _cache["vocabulary"]

    query = (query or "").strip()

    # Remove question phrases.

    cleaned = re.sub(
        r"అంటే\s*ఏమిటి|"
        r"అంటే\s*ఏంటి|"
        r"అర్థం\s*ఏమిటి|"
        r"అర్థం\s*ఏంటి",
        "",
        query,
    )

    cleaned = re.sub(
        r"\b"
        r"(ante\s+emiti|"
        r"ante\s+enti|"
        r"artham\s+emiti|"
        r"artham\s+enti|"
        r"meaning)"
        r"\b",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )

    cleaned = cleaned.strip(
        " ?!.,"
    )

    if not cleaned:
        return None

    # Exact Telugu match.

    for melimi, meaning in vocabulary:

        if cleaned == melimi.strip():

            return (
                melimi,
                meaning
            )

    # Exact Roman Telugu match.

    normalized_query = _normalize_roman(
        cleaned
    )

    for melimi, meaning in vocabulary:

        if (
            normalized_query
            in _roman_variants(melimi)
        ):

            return (
                melimi,
                meaning
            )

    return None


# ============================================================
# RELEVANT VOCABULARY
# ============================================================

def _relevant_vocabulary(
    query,
    limit=MAX_RELEVANT_ENTRIES
):

    vocabulary = get_vocabulary()

    exact = get_exact_vocabulary_meaning(
        query
    )

    result = []

    if exact:
        result.append(exact)

    tokens = _query_tokens(query)

    for melimi, meaning in vocabulary:

        if (
            melimi,
            meaning
        ) in result:
            continue

        score = 0

        for token in tokens:

            if token == melimi:
                score += 20

            if token in melimi:
                score += 5

            if token in meaning:
                score += 3

            normalized_token = (
                _normalize_roman(token)
            )

            if normalized_token in _roman_variants(
                melimi
            ):
                score += 20

        if score > 0:
            result.append(
                (
                    melimi,
                    meaning
                )
            )

        if len(result) >= limit:
            break

    return result[:limit]


# ============================================================
# GRAMMAR SEARCH
# ============================================================

def _relevant_lines(
    text,
    query,
    limit=30
):

    if not text:
        return []

    tokens = _query_tokens(query)

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
        and not line.strip().startswith("#")
    ]

    scored = []

    for index, line in enumerate(lines):

        score = 0

        for token in tokens:

            if token in line:
                score += 1

        if score:
            scored.append(
                (
                    score,
                    index,
                    line
                )
            )

    scored.sort(
        key=lambda item: (
            item[0],
            -item[1]
        ),
        reverse=True
    )

    return [
        item[2]
        for item in scored[:limit]
    ]


# ============================================================
# RELEVANT MELIMI KNOWLEDGE
# ============================================================

def get_relevant_knowledge(query):

    _ensure_loaded()

    vocabulary = _relevant_vocabulary(
        query
    )

    grammar = _relevant_lines(
        _cache["grammar"],
        query,
        25
    )

    basic_grammar = _relevant_lines(
        _cache["basic_grammar"],
        query,
        15
    )

    parts = []

    if vocabulary:

        parts.append(
            "AUTHORITATIVE MELIMI VOCABULARY:"
        )

        for melimi, meaning in vocabulary:

            roman = _telugu_to_roman(
                melimi
            )

            parts.append(
                f"{melimi} = {meaning} "
                f"(Roman: {roman})"
            )

    if grammar:

        parts.append("")
        parts.append(
            "AUTHORITATIVE MELIMI GRAMMAR:"
        )

        parts.extend(grammar)

    if basic_grammar:

        parts.append("")
        parts.append(
            "AUTHORITATIVE BASIC MELIMI GRAMMAR:"
        )

        parts.extend(basic_grammar)

    context = "\n".join(parts)

    if len(context) > MAX_KNOWLEDGE_CONTEXT_CHARS:

        context = context[
            :MAX_KNOWLEDGE_CONTEXT_CHARS
        ]

        last_break = context.rfind(
            "\n"
        )

        if last_break > 0:
            context = context[
                :last_break
            ]

    return context


# ============================================================
# GENERAL KNOWLEDGE CONTEXT
# ============================================================

def get_knowledge_context():

    _ensure_loaded()

    vocabulary = get_vocabulary()

    lines = [
        "AUTHORITATIVE MELIMI VOCABULARY:"
    ]

    for melimi, meaning in vocabulary:

        lines.append(
            f"{melimi} = {meaning}"
        )

    context = "\n".join(lines)

    return context[
        :MAX_KNOWLEDGE_CONTEXT_CHARS
    ]


# ============================================================
# PROTECTED CONTENT
# ============================================================

_PROTECT_PATTERNS = [
    re.compile(
        r"```.*?```",
        re.DOTALL
    ),

    re.compile(
        r"`[^`\n]+`"
    ),

    re.compile(
        r"https?://\S+"
    ),

    re.compile(
        r"www\.\S+"
    ),
]


def _protect(text):

    stored = []

    def replace(match):

        index = len(stored)

        stored.append(
            match.group(0)
        )

        return (
            f"\x00TELAI_PROTECTED_{index}\x00"
        )

    result = text

    for pattern in _PROTECT_PATTERNS:

        result = pattern.sub(
            replace,
            result
        )

    return result, stored


def _restore(
    text,
    stored
):

    for index, value in enumerate(stored):

        text = text.replace(
            f"\x00TELAI_PROTECTED_{index}\x00",
            value
        )

    return text


# ============================================================
# REPLACEMENTS
# ============================================================

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
        key=lambda item: len(
            item[1]
        ),
        reverse=True
    )

    for melimi, standard in replacements:

        pattern = _word_pattern(
            standard
        )

        masked = pattern.sub(
            melimi,
            masked
        )

    return _restore(
        masked,
        stored
    )


# ============================================================
# RELOAD
# ============================================================

def reload_now():

    with _lock:
        _cache["signature"] = None
