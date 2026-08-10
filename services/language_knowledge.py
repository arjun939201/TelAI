"""
services/language_knowledge.py

Loads Melimi Telugu vocabulary mappings from language/*.txt files.

File format:

    బాసట = సహాయం

Meaning:

    Melimi word = standard Telugu word
"""

import os
import re
import glob
import threading


# ============================================================
# CONFIGURATION
# ============================================================

LANGUAGE_DIR = os.path.join(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    ),
    "language"
)

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
    Return all .txt vocabulary files inside language/.
    """

    if not os.path.isdir(LANGUAGE_DIR):
        return []

    return sorted(
        glob.glob(
            os.path.join(
                LANGUAGE_DIR,
                "*.txt"
            )
        )
    )


def get_language_files():
    """
    Return language files for the language API.

    This is used by routes/language.py.
    """

    files = _language_files()

    result = []

    for path in files:

        try:

            result.append(
                {
                    "name": os.path.basename(path),
                    "path": os.path.relpath(
                        path,
                        os.path.dirname(LANGUAGE_DIR)
                    ),
                }
            )

        except OSError:
            continue

    return result


# ============================================================
# FILE CHANGE DETECTION
# ============================================================

def _current_mtime_signature(files):
    """
    Create a signature from file path, modification time,
    and file size.

    This lets us reload vocabulary only when files change.
    """

    signature = []

    for file_path in files:

        try:

            stat = os.stat(file_path)

            signature.append(
                (
                    file_path,
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
    """
    Read one language file.

    Expected format:

        బాసట = సహాయం

    Returns:

        (standard_word, melimi_word)
    """

    pairs = []

    try:

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as file:

            for raw_line in file:

                line = raw_line.strip()

                # Ignore empty lines.
                if not line:
                    continue

                # Ignore comments.
                if line.startswith("#"):
                    continue

                # Ignore malformed lines.
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
    """
    Load mappings from every language/*.txt file.

    If the same standard Telugu word occurs more than once,
    the later file wins.
    """

    files = _language_files()

    merged = {}

    for file_path in files:

        pairs = _parse_file(
            file_path
        )

        for standard_word, melimi_word in pairs:

            merged[standard_word] = melimi_word


    mappings = list(
        merged.items()
    )


    # Longer phrases first.
    #
    # Example:
    #
    # "సహాయం చేయు"
    #
    # before:
    #
    # "సహాయం"

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
    """
    Build a very small vocabulary sample for Groq.

    IMPORTANT:

    We intentionally do NOT send the entire language corpus
    to Groq because that previously caused the 413 error.
    """

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
    """
    Return the current vocabulary mappings.

    Automatically reloads the language files if they changed.
    """

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
    """
    Return the small vocabulary sample
    intended for Groq.
    """

    get_mappings()

    with _lock:

        return _cache[
            "knowledge_context"
        ]


def reload_now():
    """
    Force vocabulary reload on the next request.
    """

    with _lock:

        _cache[
            "mtime_signature"
        ] = None


# ============================================================
# PROTECTED SEGMENTS
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
# PROTECT SEGMENTS
# ============================================================

def _protect_segments(text):
    """
    Protect URLs, code and file paths from vocabulary replacement.
    """

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
# RESTORE SEGMENTS
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
# WORD MATCHING
# ============================================================

def _build_word_pattern(
    standard_word
):
    """
    Build a Unicode-aware whole-word pattern.
    """

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
    """
    Replace established standard Telugu vocabulary
    with established Melimi Telugu vocabulary.

    Only words present in language/*.txt are used.

    No new words are invented here.
    """

    if not response_text:

        return response_text


    mappings = get_mappings()

    if not mappings:

        return response_text


    # Protect code, URLs and paths.

    masked_text, store = _protect_segments(
        response_text
    )


    # Replace standard Telugu → Melimi Telugu.

    for (
        standard_word,
        melimi_word
    ) in mappings:

        pattern = _build_word_pattern(
            standard_word
        )

        masked_text = pattern.sub(
            melimi_word,
            masked_text
        )


    # Restore protected content.

    return _restore_segments(
        masked_text,
        store
    )
