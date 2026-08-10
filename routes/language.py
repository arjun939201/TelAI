"""
services/language_knowledge.py

Loads Melimi Telugu vocabulary mappings from language/*.txt files.

File format:

    బాసట = సహాయం

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
