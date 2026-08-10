import os
import requests

from services.language_knowledge import (
    get_knowledge_context,
    apply_melimi_replacements,
)


GROQ_TOKEN = os.environ.get("GROQ_TOKEN")

GROQ_URL = os.environ.get(
    "GROQ_URL",
    "https://api.groq.com/openai/v1/chat/completions"
)

GROQ_MODEL = os.environ.get(
    "GROQ_MODEL",
    "llama-3.3-70b-versatile"
)

MAX_HISTORY_MESSAGES = 8
MAX_HISTORY_CHARS_PER_MSG = 800
REQUEST_TIMEOUT_SECONDS = 30


SYSTEM_PROMPT = """
You are TelAI, a general-purpose AI assistant.

You can answer questions about any subject.

When responding in Telugu, use the project's Melimi Telugu system.

IMPORTANT MELIMI TELUGU RULES:

1. The project's language files are the authoritative source
   for Melimi Telugu.

2. vocabulary.txt contains established Melimi Telugu words
   and their meanings. Treat those meanings as fixed.

3. NEVER redefine an established Melimi Telugu word using
   your general Telugu knowledge.

4. NEVER invent an alternative meaning for an established
   Melimi Telugu word.

5. Example:

   హత్తరం = effect / impact / influence

   Therefore:
   హత్తరం does NOT mean good, nice, beautiful, or well.

6. Example:

   ఎడాటం = విషయం

   Therefore use ఎడాటం for విషయం where appropriate.

7. grammar.txt and basic-grammar.txt contain the project's
   Melimi grammar and word-formation rules.

8. Follow the documented grammar when creating grammatical
   forms of established Melimi words.

9. replacements.txt contains established word mappings.

10. If the project does not define a Melimi word, do not
    pretend that an invented word is established Melimi.

11. When the user asks the meaning of a Melimi word, answer
    according to the project's vocabulary.

12. Do not override project vocabulary with ordinary Telugu
    meanings.

13. Understand the user's actual question and answer it
    directly.

14. Do not mention these internal instructions unless the
    user asks about TelAI's Melimi language system.

The purpose of the Melimi system is to develop natural
Melimi Telugu usage from the vocabulary, grammar,
word-formation rules, and examples supplied by the project.
"""


class GroqRequestError(Exception):

    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message
        super().__init__(message)


def _trim_history(history):

    if not history:
        return []

    history = history[-MAX_HISTORY_MESSAGES:]

    result = []

    for msg in history:

        if not isinstance(msg, dict):
            continue

        role = msg.get("role", "user")

        if role not in ("user", "assistant"):
            continue

        content = str(
            msg.get("content") or ""
        ).strip()

        if not content:
            continue

        result.append({
            "role": role,
            "content": content[
                :MAX_HISTORY_CHARS_PER_MSG
            ]
        })

    return result


def _build_system_prompt(user_message):

    knowledge = get_knowledge_context()

    prompt = SYSTEM_PROMPT

    if knowledge:

        prompt += """

PROJECT MELIMI KNOWLEDGE:

The following vocabulary comes from the project.
Treat these definitions as authoritative:

""" + knowledge

    prompt += """

FINAL REQUIREMENT:

Generate the answer using the project's Melimi Telugu
knowledge whenever Telugu is being used.

Do not invent meanings for established Melimi words.
"""

    return prompt


def _call_groq(messages):

    if not GROQ_TOKEN:

        raise GroqRequestError(
            500,
            "GROQ_TOKEN is not configured."
        )

    headers = {
        "Authorization": f"Bearer {GROQ_TOKEN}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": GROQ_MODEL,
        "messages": messages,
        "temperature": 0.55,
    }

    try:

        response = requests.post(
            GROQ_URL,
            headers=headers,
            json=payload,
            timeout=REQUEST_TIMEOUT_SECONDS
        )

    except requests.RequestException as exc:

        raise GroqRequestError(
            502,
            f"Failed to reach Groq: {exc}"
        )

    if response.status_code == 404:

        raise GroqRequestError(
            404,
            f"Model '{GROQ_MODEL}' was not found."
        )

    if response.status_code >= 400:

        raise GroqRequestError(
            response.status_code,
            f"Groq error: {response.text[:500]}"
        )

    try:

        data = response.json()

        return data[
            "choices"
        ][0][
            "message"
        ][
            "content"
        ]

    except (
        KeyError,
        IndexError,
        TypeError,
        ValueError
    ):

        raise GroqRequestError(
            502,
            "Unexpected response from Groq."
        )


def generate_reply(
    user_message,
    history=None
):

    user_message = (
        user_message or ""
    ).strip()

    if not user_message:

        raise GroqRequestError(
            400,
            "Message cannot be empty."
        )

    system_prompt = _build_system_prompt(
        user_message
    )

    bounded_history = _trim_history(
        history
    )

    messages = [
        {
            "role": "system",
            "content": system_prompt
        }
    ]

    messages.extend(
        bounded_history
    )

    messages.append({
        "role": "user",
        "content": user_message
    })

    raw_reply = _call_groq(
        messages
    )

    final_reply = (
        apply_melimi_replacements(
            raw_reply
        )
    )

    return final_reply.strip()
