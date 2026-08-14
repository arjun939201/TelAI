from pathlib import Path

ROOT = Path(__file__).resolve().parent
APP = ROOT / "app"
MAIN = APP / "main.py"
GROQ = APP / "groq_client.py"


def patch_once(path: Path, old: str, new: str, label: str):
    text = path.read_text(encoding="utf-8")
    if new in text:
        return
    if old not in text:
        raise RuntimeError(f"Patch anchor not found in {path}: {label}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")
    print("patched:", path, "-", label)


# Add local language analysis to the FastAPI layer.
patch_once(
    MAIN,
    """from app.groq_client import (
    call_groq,
)""",
    """from app.groq_client import (
    call_groq,
)

from app.language import (
    build_language_context,
)""",
    "language import",
)

patch_once(
    MAIN,
    """    system_prompt = build_system_prompt(
        vocabulary_context=vocabulary_context,
        learned_context=learned_context,
        mode=mode,
    )""",
    """    system_prompt = build_system_prompt(
        vocabulary_context=vocabulary_context,
        learned_context=learned_context,
        mode=mode,
    )

    if mode == "melimi":
        system_prompt += "\\n\\n" + build_language_context(message)""",
    "language context",
)

# Add the same local hint directly before Groq message construction.
patch_once(
    GROQ,
    """from app.melimi_engine import (
    retrieve_conversation_context,
)""",
    """from app.melimi_engine import (
    retrieve_conversation_context,
)

from app.language import build_language_context
from app.response_guard import clean_model_output""",
    "language/guard imports",
)

patch_once(
    GROQ,
    """    # ========================================================
    # MESSAGES
    # ========================================================""",
    """    # ========================================================
    # LOCAL LANGUAGE HINT
    # ========================================================

    if is_melimi:
        system_prompt += "\\n\\n" + build_language_context(user_message)

    # ========================================================
    # MESSAGES
    # ========================================================""",
    "local language hint",
)

patch_once(
    GROQ,
    """    answer = (
        answer.strip()
    )""",
    """    answer = clean_model_output(answer)""",
    "safe output cleanup",
)

print("TeluAI update package applied successfully.")
