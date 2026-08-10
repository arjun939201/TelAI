import os
import requests

from services.language_knowledge import (
    get_exact_vocabulary_meaning,
    get_relevant_knowledge,
    apply_melimi_replacements,
)


GROQ_TOKEN = os.environ.get(
    "GROQ_TOKEN"
)

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

When Telugu is used, follow the project's Melimi Telugu system.

IMPORTANT:

The project's language files are authoritative.

If the project defines a Melimi Telugu word,
its meaning is fixed.

Never redefine an established Melimi word using
ordinary Telugu knowledge.

Never invent another meaning for an established
Melimi word.

For example:

హత్తరం = ప్రభావం

Therefore NEVER say:

హత్తరం = బాగుండటం
హత్తరం = చక్కగా ఉండటం
హత్తరం = అందంగా ఉండటం
హత్తరం = good
హత్తరం = nice
హత్తరం = beautiful

Another example:

ఎడాటం = విషయం

When the user asks the meaning of an established
Melimi word, use the project's definition.

The grammar files are authoritative for Melimi
word formation and grammar.

Do not invent unsupported Melimi vocabulary.

The purpose of the Melimi system is to develop
natural Melimi Telugu usage based on the vocabulary,
grammar, word-formation rules, and examples supplied
by the project.
"""


class GroqRequestError(Exception):

    def __init__(
        self,
        status_code,
        message
    ):

        self.status_code = status_code
        self.message = message

        super().__init__(
            message
        )


def _trim_history(history):

    if not history:
        return []

    history = history[
        -MAX_HISTORY_MESSAGES:
    ]

    result = []

    for message in history:

        if not isinstance(
            message,
            dict
        ):
            continue

        role = message.get(
            "role",
            "user"
        )

        if role not in (
            "user",
            "assistant"
        ):
            continue

        content = str(
            message.get(
                "content",
                ""
            )
        ).strip()

        if not content:
            continue

        result.append(
            {
                "role": role,
                "content": content[
                    :MAX_HISTORY_CHARS_PER_MSG
                ]
            }
        )

    return result


def _is_meaning_question(text):

    text = (
        text or ""
    ).strip().lower()

    patterns = [
        "అంటే ఏమిటి",
        "అంటే ఏంటి",
        "అర్థం ఏమిటి",
        "అర్థం ఏంటి",
        "అర్థమేమిటి",
        "అర్థమేంటి",

        "meaning",
        "ante emiti",
        "ante enti",
        "artham emiti",
        "artham enti",
        "artham",
    ]

    return any(
        pattern in text
        for pattern in patterns
    )


def _direct_vocabulary_answer(
    user_message
):

    if not _is_meaning_question(
        user_message
    ):
        return None

    result = (
        get_exact_vocabulary_meaning(
            user_message
        )
    )

    if not result:
        return None

    melimi_word, meaning = result

    return (
        f"{melimi_word} = {meaning}"
    )


def _call_groq(messages):

    if not GROQ_TOKEN:

        raise GroqRequestError(
            500,
            "GROQ_TOKEN is not configured."
        )

    headers = {
        "Authorization":
            f"Bearer {GROQ_TOKEN}",

        "Content-Type":
            "application/json",
    }

    payload = {
        "model": GROQ_MODEL,
        "messages": messages,
        "temperature": 0.5,
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

        return (
            data["choices"][0]
            ["message"]["content"]
        )

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


    # ========================================================
    # DIRECT MELIMI VOCABULARY LOOKUP
    # ========================================================
    #
    # If the user asks for the meaning of an established
    # Melimi word, DO NOT ask the LLM.
    #
    # The project vocabulary is authoritative.
    #

    direct_answer = (
        _direct_vocabulary_answer(
            user_message
        )
    )

    if direct_answer:

        return direct_answer


    # ========================================================
    # RETRIEVE RELEVANT MELIMI KNOWLEDGE
    # ========================================================

    knowledge = get_relevant_knowledge(
        user_message
    )


    system_prompt = SYSTEM_PROMPT


    if knowledge:

        system_prompt += """

AUTHORITATIVE PROJECT KNOWLEDGE
FOR THIS REQUEST:

""" + knowledge


    # ========================================================
    # BUILD MESSAGES
    # ========================================================

    messages = [
        {
            "role": "system",
            "content": system_prompt
        }
    ]

    messages.extend(
        _trim_history(
            history
        )
    )

    messages.append(
        {
            "role": "user",
            "content": user_message
        }
    )


    # ========================================================
    # GROQ
    # ========================================================

    raw_reply = _call_groq(
        messages
    )


    # ========================================================
    # FINAL MELIMI SAFETY REPLACEMENT
    # ========================================================

    final_reply = (
        apply_melimi_replacements(
            raw_reply
        )
    )


    return final_reply.strip()
