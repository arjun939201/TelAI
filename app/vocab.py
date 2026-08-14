import json
import os
import re
from typing import Any, Dict, List


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DATA_DIR = os.path.join(
    BASE_DIR,
    "data",
)

VOCABULARY_FILE = os.path.join(
    DATA_DIR,
    "vocabulary.json",
)


# ============================================================
# TELUGU TOKENIZATION
# ============================================================

TELUGU_WORD_RE = re.compile(
    r"[\u0C00-\u0C7F]+",
    re.UNICODE,
)


def tokenize(
    text: str,
) -> List[str]:

    return TELUGU_WORD_RE.findall(
        text or ""
    )


# ============================================================
# NORMALIZATION
# ============================================================

def normalize(
    text: str,
) -> str:

    return re.sub(
        r"\s+",
        " ",
        str(text or "")
        .strip()
        .lower(),
    )


# ============================================================
# LOAD VOCABULARY
# ============================================================

def load_vocabulary() -> List[Dict[str, Any]]:

    if not os.path.exists(
        VOCABULARY_FILE
    ):

        raise FileNotFoundError(
            "vocabulary.json was not found at: "
            + VOCABULARY_FILE
        )

    with open(
        VOCABULARY_FILE,
        "r",
        encoding="utf-8",
    ) as file:

        data = json.load(
            file
        )

    # --------------------------------------------------------
    # Supported structures
    # --------------------------------------------------------

    if isinstance(
        data,
        list,
    ):

        return data

    if isinstance(
        data,
        dict,
    ):

        if isinstance(
            data.get("vocabulary"),
            list,
        ):

            return data[
                "vocabulary"
            ]

        if isinstance(
            data.get("words"),
            list,
        ):

            return data[
                "words"
            ]

    raise ValueError(
        "vocabulary.json must contain "
        "a JSON list or a 'vocabulary'/'words' list."
    )


VOCABULARY = load_vocabulary()


# ============================================================
# ALTERNATIVE STANDARD FORMS
# ============================================================

def split_alternatives(
    value: Any,
) -> List[str]:

    if value is None:

        return []

    if isinstance(
        value,
        list,
    ):

        return [
            normalize(
                item
            )
            for item in value
            if str(item).strip()
        ]

    text = str(
        value
    ).strip()

    if not text:

        return []

    # --------------------------------------------------------
    # Examples supported:
    #
    # స్వంతం, సొంతం
    # swantham, sontham
    # స్వంతం / సొంతం
    # స్వంతం; సొంతం
    # స్వంతం | సొంతం
    # --------------------------------------------------------

    parts = re.split(
        r"\s*(?:,|/|;|\||\s+లేదా\s+)\s*",
        text,
        flags=re.IGNORECASE,
    )

    return [
        normalize(
            part
        )
        for part in parts
        if part.strip()
    ]


# ============================================================
# ENTRY HELPERS
# ============================================================

def standard_forms(
    entry: Dict[str, Any],
) -> List[str]:

    return split_alternatives(
        entry.get(
            "standard",
            "",
        )
    )


def melimi_forms(
    entry: Dict[str, Any],
) -> List[str]:

    return split_alternatives(
        entry.get(
            "melimi",
            "",
        )
    )


def searchable_fields(
    entry: Dict[str, Any],
) -> str:

    fields = []

    for key in (
        "standard",
        "melimi",
        "note",
        "meaning",
        "definition",
        "english",
        "gloss",
        "description",
        "example",
        "examples",
        "related",
        "synonyms",
        "tags",
    ):

        value = entry.get(
            key,
            "",
        )

        if isinstance(
            value,
            list,
        ):

            fields.extend(
                str(item)
                for item in value
            )

        elif isinstance(
            value,
            dict,
        ):

            fields.extend(
                str(item)
                for item in value.values()
            )

        else:

            fields.append(
                str(value)
            )

    return normalize(
        " ".join(fields)
    )


# ============================================================
# MATCHING
# ============================================================

def contains_phrase(
    text: str,
    phrase: str,
) -> bool:

    text = normalize(
        text
    )

    phrase = normalize(
        phrase
    )

    if not text or not phrase:

        return False

    return phrase in text


def exact_word_match(
    query_words: set,
    candidate: str,
) -> bool:

    candidate_words = set(
        tokenize(
            candidate
        )
    )

    if not candidate_words:

        return False

    return candidate_words.issubset(
        query_words
    )


# ============================================================
# VOCABULARY RETRIEVAL
# ============================================================

def retrieve_vocab(
    message: str,
    limit: int = 18,
) -> List[Dict[str, Any]]:

    message = normalize(
        message
    )

    if not message:

        return []

    query_words = set(
        tokenize(
            message
        )
    )

    if not query_words:

        return []

    scored = []

    for index, entry in enumerate(
        VOCABULARY
    ):

        if not isinstance(
            entry,
            dict,
        ):

            continue

        score = 0

        standards = (
            standard_forms(
                entry
            )
        )

        melimis = (
            melimi_forms(
                entry
            )
        )

        searchable = (
            searchable_fields(
                entry
            )
        )

        # ----------------------------------------------------
        # STANDARD ALTERNATIVES
        # ----------------------------------------------------

        for standard in standards:

            if contains_phrase(
                message,
                standard,
            ):

                score += 200

            if exact_word_match(
                query_words,
                standard,
            ):

                score += 150

        # ----------------------------------------------------
        # MELIMI WORDS
        # ----------------------------------------------------

        for melimi in melimis:

            if contains_phrase(
                message,
                melimi,
            ):

                score += 250

            if exact_word_match(
                query_words,
                melimi,
            ):

                score += 180

        # ----------------------------------------------------
        # WORD-LEVEL SEARCH
        # ----------------------------------------------------

        for word in query_words:

            if len(word) < 2:

                continue

            if word in searchable:

                score += 8

        # ----------------------------------------------------
        # MEANING / ENGLISH SEARCH
        # ----------------------------------------------------

        for key in (
            "meaning",
            "definition",
            "english",
            "gloss",
        ):

            value = normalize(
                entry.get(
                    key,
                    "",
                )
            )

            if not value:

                continue

            if (
                value in message
                or message in value
            ):

                score += 50

        if score > 0:

            scored.append(
                (
                    score,
                    index,
                    entry,
                )
            )

    scored.sort(
        key=lambda item: (
            -item[0],
            item[1],
        )
    )

    return [
        entry
        for _, _, entry
        in scored[:limit]
    ]


# ============================================================
# PHRASE RETRIEVAL
# ============================================================

def retrieve_phrase_entries(
    message: str,
    limit: int = 10,
) -> List[Dict[str, Any]]:

    message = normalize(
        message
    )

    if not message:

        return []

    scored = []

    for index, entry in enumerate(
        VOCABULARY
    ):

        if not isinstance(
            entry,
            dict,
        ):

            continue

        standards = (
            standard_forms(
                entry
            )
        )

        melimis = (
            melimi_forms(
                entry
            )
        )

        best_score = 0

        for standard in standards:

            word_count = len(
                tokenize(
                    standard
                )
            )

            if word_count < 2:

                continue

            if contains_phrase(
                message,
                standard,
            ):

                best_score = max(
                    best_score,
                    500 + (
                        word_count * 50
                    ),
                )

        for melimi in melimis:

            word_count = len(
                tokenize(
                    melimi
                )
            )

            if word_count < 2:

                continue

            if contains_phrase(
                message,
                melimi,
            ):

                best_score = max(
                    best_score,
                    600 + (
                        word_count * 50
                    ),
                )

        if best_score:

            scored.append(
                (
                    best_score,
                    index,
                    entry,
                )
            )

    scored.sort(
        key=lambda item: (
            -item[0],
            item[1],
        )
    )

    return [
        entry
        for _, _, entry
        in scored[:limit]
    ]


# ============================================================
# FORMAT VOCABULARY FOR GROQ
# ============================================================

def format_vocab_context(
    entries: List[Dict[str, Any]],
    max_chars: int = 6000,
) -> str:

    lines = []

    for entry in entries:

        standard = str(
            entry.get(
                "standard",
                "",
            )
        ).strip()

        melimi = str(
            entry.get(
                "melimi",
                "",
            )
        ).strip()

        note = str(
            entry.get(
                "note",
                "",
            )
        ).strip()

        meaning = str(
            entry.get(
                "meaning",
                entry.get(
                    "definition",
                    entry.get(
                        "english",
                        "",
                    ),
                ),
            )
        ).strip()

        if not (
            standard
            or melimi
        ):

            continue

        line = (
            f"- {standard} "
            f"→ {melimi}"
        )

        if meaning:

            line += (
                f" | meaning: {meaning}"
            )

        if note:

            line += (
                f" | note: {note}"
            )

        lines.append(
            line
        )

    context = "\n".join(
        lines
    )

    if len(context) > max_chars:

        context = context[
            :max_chars
        ]

    return context


# ============================================================
# COMPLETE CONTEXT RETRIEVAL
# ============================================================

def retrieve_context(
    message: str,
) -> Dict[str, Any]:

    vocabulary = retrieve_vocab(
        message,
        limit=18,
    )

    phrases = retrieve_phrase_entries(
        message,
        limit=8,
    )

    # --------------------------------------------------------
    # Avoid duplicate entries
    # --------------------------------------------------------

    seen = set()

    combined = []

    for entry in (
        phrases
        + vocabulary
    ):

        marker = (
            str(
                entry.get(
                    "standard",
                    "",
                )
            ),
            str(
                entry.get(
                    "melimi",
                    "",
                )
            ),
        )

        if marker in seen:

            continue

        seen.add(
            marker
        )

        combined.append(
            entry
        )

    return {
        "entries": combined,
        "text": format_vocab_context(
            combined
        ),
    }


# ============================================================
# GET VOCABULARY CONTEXT
# ============================================================

def get_examples(
    message: str,
) -> str:

    context = retrieve_context(
        message
    )

    return context[
        "text"
    ]


# ============================================================
# FIND STANDARD TERMS IN GENERATED RESPONSE
# ============================================================

def find_standard_terms(
    response: str,
    limit: int = 20,
) -> List[Dict[str, Any]]:

    response = normalize(
        response
    )

    if not response:

        return []

    matches = []

    for index, entry in enumerate(
        VOCABULARY
    ):

        if not isinstance(
            entry,
            dict,
        ):

            continue

        standards = (
            standard_forms(
                entry
            )
        )

        melimis = (
            melimi_forms(
                entry
            )
        )

        if not standards:
            continue

        if not melimis:
            continue

        for standard in standards:

            if not contains_phrase(
                response,
                standard,
            ):

                continue

            # ------------------------------------------------
            # If the Melimi equivalent is already present,
            # this is not necessarily an error.
            # ------------------------------------------------

            melimi_present = False

            for melimi in melimis:

                if contains_phrase(
                    response,
                    melimi,
                ):

                    melimi_present = True
                    break

            if melimi_present:

                continue

            matches.append(
                (
                    len(standard),
                    index,
                    entry,
                )
            )

            break

    matches.sort(
        key=lambda item: (
            -item[0],
            item[1],
        )
    )

    return [
        entry
        for _, _, entry
        in matches[:limit]
    ]


# ============================================================
# VOCABULARY STATISTICS
# ============================================================

def get_vocabulary_stats() -> Dict[str, int]:

    return {
        "entries": len(
            VOCABULARY
        ),

        "standard_forms": sum(
            len(
                standard_forms(
                    entry
                )
            )
            for entry
            in VOCABULARY
            if isinstance(
                entry,
                dict,
            )
        ),

        "melimi_forms": sum(
            len(
                melimi_forms(
                    entry
                )
            )
            for entry
            in VOCABULARY
            if isinstance(
                entry,
                dict,
            )
        ),
    }
