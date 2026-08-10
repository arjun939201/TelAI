from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

LANGUAGE_DIR = BASE_DIR / "language"


ALLOWED_EXTENSIONS = {
    ".txt",
    ".md",
    ".json",
    ".csv"
}


def get_language_files():

    if not LANGUAGE_DIR.exists():
        return []

    return sorted(
        file.name
        for file in LANGUAGE_DIR.iterdir()
        if file.is_file()
        and file.suffix.lower() in ALLOWED_EXTENSIONS
    )


def read_language_knowledge():

    if not LANGUAGE_DIR.exists():
        return ""

    sections = []

    for file in sorted(LANGUAGE_DIR.iterdir()):

        if not file.is_file():
            continue

        if file.suffix.lower() not in ALLOWED_EXTENSIONS:
            continue

        try:

            content = file.read_text(
                encoding="utf-8"
            )

            if content.strip():

                sections.append(
                    f"\n--- {file.name} ---\n"
                    f"{content}"
                )

        except Exception as error:

            print(
                f"Could not read {file.name}: {error}"
            )

    return "\n".join(sections)


def append_suggestion(text: str):

    LANGUAGE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    file = LANGUAGE_DIR / "suggestions.txt"

    with file.open(
        "a",
        encoding="utf-8"
    ) as handle:

        handle.write(
            f"\n{text.strip()}\n"
        )
