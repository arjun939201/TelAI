
import re


def clean_response(text: str) -> str:
    value = str(text or "").strip()
    value = re.sub(r"^\s*(assistant|teluai)\s*:\s*", "", value, flags=re.I)
    value = re.sub(r"\n{3,}", "\n\n", value)
    return value.strip()
