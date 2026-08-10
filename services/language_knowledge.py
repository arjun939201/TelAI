from pathlib import Path


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

LANGUAGE_DIR = BASE_DIR / "language"


# ============================================================
# SUPPORTED FILE TYPES
# ============================================================

ALLOWED_EXTENSIONS = {
    ".txt",
    ".md",
    ".json",
    ".csv"
}


# ============================================================
# KNOWLEDGE LIMIT
# ============================================================

# Prevent the complete language corpus from becoming so large
# that the Groq request is rejected.
#
# This is a CHARACTER limit, not a token limit.
#
# 100,000 characters is roughly tens of thousands of tokens,
# depending on the language and content.

MAX_KNOWLEDGE_CHARACTERS = 100_000


# ============================================================
# GET LANGUAGE FILES
# ============================================================

def get_language_files():

    if not LANGUAGE_DIR.exists():
        return []

    return sorted(
        file.name
        for file in LANGUAGE_DIR.iterdir()
        if (
            file.is_file()
            and file.suffix.lower()
            in ALLOWED_EXTENSIONS
        )
    )


# ============================================================
# READ ONE FILE
# ============================================================

def read_file(file_path):

    try:

        return file_path.read_text(
            encoding="utf-8"
        )

    except Exception as error:

        print(
            f"Could not read {file_path.name}: {error}"
        )

        return ""


# ============================================================
# READ ALL LANGUAGE KNOWLEDGE
# ============================================================

def read_language_knowledge():

    if not LANGUAGE_DIR.exists():
        return ""

    sections = []

    total_characters = 0


    # --------------------------------------------------------
    # Read files in stable alphabetical order.
    # --------------------------------------------------------

    for file in sorted(LANGUAGE_DIR.iterdir()):

        if not file.is_file():
            continue

        if file.suffix.lower() not in ALLOWED_EXTENSIONS:
            continue


        content = read_file(file).strip()

        if not content:
            continue


        section = (
            f"\n--- {file.name} ---\n"
            f"{content}\n"
        )


        # ----------------------------------------------------
        # Check knowledge-size limit.
        # ----------------------------------------------------

        remaining = (
            MAX_KNOWLEDGE_CHARACTERS
            - total_characters
        )


        if remaining <= 0:

            print(
                "LANGUAGE KNOWLEDGE LIMIT REACHED."
            )

            break


        # ----------------------------------------------------
        # Entire file fits.
        # ----------------------------------------------------

        if len(section) <= remaining:

            sections.append(section)

            total_characters += len(section)

            continue


        # ----------------------------------------------------
        # File is too large to fit completely.
        #
        # Include only the remaining amount.
        # ----------------------------------------------------

        truncated = section[:remaining]

        sections.append(
            truncated
            + "\n[FILE TRUNCATED]\n"
        )

        total_characters += len(truncated)

        print(
            f"Language file truncated: {file.name}"
        )

        break


    knowledge = "\n".join(sections)


    print(
        "LANGUAGE KNOWLEDGE FILES:",
        len(sections)
    )

    print(
        "LANGUAGE KNOWLEDGE CHARACTERS:",
        len(knowledge)
    )


    return knowledge


# ============================================================
# APPEND USER SUGGESTION
# ============================================================

def append_suggestion(text: str):

    LANGUAGE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )


    file_path = (
        LANGUAGE_DIR
        / "suggestions.txt"
    )


    with file_path.open(
        "a",
        encoding="utf-8"
    ) as handle:

        handle.write(
            f"\n{text.strip()}\n"
        )
