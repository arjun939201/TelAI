from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

LANGUAGE_DIR = BASE_DIR / "language"


ALLOWED_EXTENSIONS = {
    ".txt",
    ".md",
    ".json",
    ".csv"
}


# Maximum language knowledge sent to Groq
# This keeps the request comfortably below
# Groq's token-per-day/request limits.
MAX_KNOWLEDGE_CHARS = 60000


def get_language_files():

    if not LANGUAGE_DIR.exists():
        return []

    return sorted(
        file.name
        for file in LANGUAGE_DIR.iterdir()
        if file.is_file()
        and file.suffix.lower() in ALLOWED_EXTENSIONS
    )


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


def read_language_knowledge():

    if not LANGUAGE_DIR.exists():
        return ""


    files = []

    for file in sorted(
        LANGUAGE_DIR.iterdir()
    ):

        if not file.is_file():
            continue

        if file.suffix.lower() not in ALLOWED_EXTENSIONS:
            continue

        files.append(file)


    if not files:
        return ""


    # Put smaller/high-priority files first.
    files.sort(
        key=lambda file: (
            file.name not in {
                "notes.txt",
                "suggestions.txt",
                "grammar.txt"
            },
            file.name
        )
    )


    sections = []

    remaining =
        MAX_KNOWLEDGE_CHARS


    for file in files:

        if remaining <= 0:
            break


        content = read_file(file).strip()


        if not content:
            continue


        header = (
            f"\n--- {file.name} ---\n"
        )


        available =
            remaining - len(header)


        if available <= 0:
            break


        # Keep the beginning of each file.
        # This prevents enormous requests.
        content = content[:available]


        sections.append(
            header + content
        )


        remaining -= (
            len(header) +
            len(content)
        )


    return "\n".join(sections)


def append_suggestion(text: str):

    LANGUAGE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )


    file =
        LANGUAGE_DIR / "suggestions.txt"


    with file.open(
        "a",
        encoding="utf-8"
    ) as handle:

        handle.write(
            f"\n{text.strip()}\n"
        )
