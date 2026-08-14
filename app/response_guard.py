import re
from typing import Any, Dict, List


def clean_model_output(text: str) -> str:
    """Minimal cleanup only; never rewrites Telugu or Melimi vocabulary."""
    text = str(text or "").strip()
    text = re.sub(r"^\s*(assistant|teluai)\s*:\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def collect_vocab_labels(entries: List[Dict[str, Any]]) -> List[str]:
    result = []
    for entry in entries or []:
        if isinstance(entry, dict):
            value = str(entry.get("standard") or entry.get("melimi") or "").strip()
            if value:
                result.append(value)
    return result
