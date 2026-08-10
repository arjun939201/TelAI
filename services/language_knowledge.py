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

    sections = []

    for file in sorted(LANGUAGE_DIR.iterdir()):

        if not file.is_file():
            continue

        if file.suffix.lower() not in ALLOWED_EXTENSIONS:
            continue

        content = read_file(file).strip()

        if not content:
            continue

        sections.append(
            f"\n--- {file.name} ---\n{content}"
        )

    return "\n".join(sections)


def append_suggestion(text: str):

    LANGUAGE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    file_path = LANGUAGE_DIR / "suggestions.txt"

    with file_path.open(
        "a",
        encoding="utf-8"
    ) as handle:

        handle.write(
            f"\n{text.strip()}\n"
        )
