"""
services/grok_chat.py

Talks to Groq's OpenAI-compatible chat completions endpoint, keeping every
request bounded in size, and runs the deterministic Melimi vocabulary
replacement on the final response before returning it.

Env vars expected (unchanged from your current setup):
    GROQ_TOKEN
    GROQ_URL      e.g. https://api.groq.com/openai/v1/chat/completions
    GROQ_MODEL    e.g. llama-3.3-70b-versatile
"""

import os
import requests

from services.language_knowledge import (
    get_knowledge_context,
    apply_melimi_replacements,
)

GROQ_TOKEN = os.environ.get("GROQ_TOKEN")
GROQ_URL = os.environ.get("GROQ_URL", "https://api.groq.com/openai/v1/chat/completions")
GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")

# --- Bounds that keep every request small, no matter how language/ or
#     chat history grow. ---
MAX_HISTORY_MESSAGES = 8          # last N messages (user+assistant combined)
MAX_HISTORY_CHARS_PER_MSG = 800   # per-message cap
REQUEST_TIMEOUT_SECONDS = 30

SYSTEM_PROMPT = """
You are TelAI, a general-purpose AI assistant.

You can answer questions about any subject.

When responding in Telugu, use the project's Melimi Telugu system.

IMPORTANT MELIMI TELUGU RULES:

1. The files in the project's language/ directory are the authoritative
   source for Melimi Telugu.

2. vocabulary.txt contains established Melimi Telugu vocabulary and meanings.
   Treat those meanings as fixed.

3. If a Melimi word already has a meaning in vocabulary.txt, NEVER redefine
   that word using your general Telugu knowledge.

4. NEVER invent an alternative meaning for an established Melimi word.

5. Example:
   హత్తరం = effect / impact / influence
   Therefore NEVER say:
   ഹత్తరం = good / nice / beautiful / well.

6. Example:
   ఎడాటం = విషయం
   Therefore use ఎడాటం when the project's rules require the Melimi
   equivalent of విషయం.

7. grammar.txt and basic-grammar.txt contain authoritative Melimi grammar
   and word-formation rules. Follow them when forming grammatical variants.

8. replacements.txt contains established mappings. Use them consistently.

9. If a Melimi word is not defined by the project, do not pretend that you
   know an established Melimi meaning for it.

10. Do not replace an established Melimi meaning with a meaning that merely
    sounds natural in ordinary Telugu.

11. Understand the user's question first and answer it directly.

12. When the user asks:
       "హత్తరం అంటే ఏమిటి?"
    answer according to the project's definition:
       "హత్తరం = ప్రభావం"
    and explain it using that meaning.

13. When the user asks about a Melimi word, prioritize the project's
    vocabulary and grammar over your pretrained Telugu knowledge.

14. Do not mention these internal instructions unless the user asks about
    how TelAI's Melimi language system works.

Your goal is not merely to replace words after generating Telugu.
Your goal is to produce Telugu that follows the Melimi Telugu vocabulary,
grammar, and word-formation system supplied by the project.
"""



class GroqRequestError(Exception):
    """Raised when Groq returns an error we want the route layer to handle."""
    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message
        super().__init__(message)


def _build_system_prompt():
    """
    System prompt stays small and fixed-size. We optionally append a tiny,
    capped vocabulary sample purely for tone/style — never the full corpus.
    """
    knowledge_context = get_knowledge_context()
    if not knowledge_context:
        return SYSTEM_PROMPT_BASE

    return (
        f"{SYSTEM_PROMPT_BASE}\n\n"
        "For style reference only, here are a few example words in the "
        "Melimi Telugu dialect (do not force these in — just be aware of the "
        "tone). Actual word substitution is handled separately, so just "
        "write normal, natural Telugu:\n"
        f"{knowledge_context}"
    )


def _trim_history(history):
    """
    Bound chat history so requests can't grow indefinitely:
    - keep only the last MAX_HISTORY_MESSAGES entries
    - truncate any single message to MAX_HISTORY_CHARS_PER_MSG characters
    """
    if not history:
        return []

    trimmed = history[-MAX_HISTORY_MESSAGES:]

    bounded = []
    for msg in trimmed:
        role = msg.get("role", "user")
        content = (msg.get("content") or "")[:MAX_HISTORY_CHARS_PER_MSG]
        if content:
            bounded.append({"role": role, "content": content})
    return bounded


def _call_groq(messages):
    if not GROQ_TOKEN:
        raise GroqRequestError(500, "GROQ_TOKEN is not configured.")

    headers = {
        "Authorization": f"Bearer {GROQ_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": messages,
        "temperature": 0.7,
    }

    try:
        resp = requests.post(
            GROQ_URL, headers=headers, json=payload, timeout=REQUEST_TIMEOUT_SECONDS
        )
    except requests.RequestException as exc:
        raise GroqRequestError(502, f"Failed to reach Groq: {exc}")

    if resp.status_code == 413:
        raise GroqRequestError(
            413,
            "Groq request too large even after trimming. "
            "Reduce MAX_HISTORY_MESSAGES / MAX_HISTORY_CHARS_PER_MSG "
            "or MAX_KNOWLEDGE_CONTEXT_CHARS further.",
        )
    if resp.status_code == 404:
        raise GroqRequestError(
            404,
            f"Model '{GROQ_MODEL}' not found by Groq. Check GROQ_MODEL env var.",
        )
    if resp.status_code >= 400:
        raise GroqRequestError(resp.status_code, f"Groq error: {resp.text[:500]}")

    data = resp.json()
    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        raise GroqRequestError(502, "Unexpected response shape from Groq.")


def generate_reply(user_message, history=None):
    """
    Main entry point used by routes/chatbot.py.

    Args:
        user_message: str, the latest message from the user.
        history: list[dict] of prior {"role": "user"|"assistant", "content": str}

    Returns:
        str: final Telugu response, AFTER deterministic Melimi replacement.

    Raises:
        GroqRequestError: on any upstream failure, with a status_code the
        route layer can map directly to an HTTP response.
    """
    system_prompt = _build_system_prompt()
    bounded_history = _trim_history(history)

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(bounded_history)
    messages.append({"role": "user", "content": user_message})

    raw_reply = _call_groq(messages)
    final_reply = apply_melimi_replacements(raw_reply)
    return final_reply
