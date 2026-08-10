import os

from openai import OpenAI

from services.language_knowledge import (
    get_exact_vocabulary_meaning,
    get_relevant_knowledge,
    apply_melimi_replacements,
)


OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

OPENAI_MODEL = os.environ.get(
    "OPENAI_MODEL",
    "gpt-5-mini",
)

MAX_HISTORY_MESSAGES = 8
MAX_HISTORY_CHARS_PER_MSG = 1000


SYSTEM_PROMPT = """
You are TelAI, a general-purpose AI assistant.

You can answer questions about any subject.

When Telugu is used, follow the project's Melimi Telugu system.

IMPORTANT MELIMI RULES:

1. The project's language files are authoritative for Melimi Telugu.

2. vocabulary.txt contains established Melimi Telugu vocabulary
   and meanings.

3. If a Melimi word is defined by the project, its meaning is fixed.

4. NEVER replace an established Melimi meaning with your own
   Telugu interpretation.

5. NEVER invent a different meaning for an established Melimi word.

6. Example:

   హత్తరం = ప్రభావం

   Therefore:
   హత్తరం does NOT mean good, nice, beautiful, or well.

7. Example:

   ఎడాటం = విషయం

8. grammar.txt and basic-grammar.txt contain authoritative
   Melimi grammar and word-formation rules.

9. Follow the supplied grammar when forming Melimi words.

10. Do not invent unsupported Melimi vocabulary.

11. If the user asks for the meaning of an established Melimi
    word, use the project's documented meaning.

12. The supplied Melimi knowledge takes priority over your
    general pretrained Telugu vocabulary.

13. Understand Roman Telugu too.

14. Preserve names, numbers, URLs, code and technical identifiers
    when appropriate.

15. Answer naturally and directly.

The purpose of TelAI is to develop natural Melimi Telugu usage
based on the vocabulary, grammar, word-formation rules and
examples supplied by the project.
"""


class OpenAIRequestError(Exception):

    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message
        super().__init__(message)


def _trim_history(history):

    if not history:
        return []

    history = history[
        -MAX_HISTORY_MESSAGES:
    ]

    result = []

    for message in history:

        if not isinstance(message, dict):
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

        result.append({
            "role": role,
            "content": content[
                :MAX_HISTORY_CHARS_PER_MSG
            ]
        })

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

    result = get_exact_vocabulary_meaning(
        user_message
    )

    if not result:
        return None

    melimi_word, meaning = result

    return (
        f"{melimi_word} = {meaning}"
    )


def _create_client():

    if not OPENAI_API_KEY:

        raise OpenAIRequestError(
            500,
            "OPENAI_API_KEY is not configured."
        )

    return OpenAI(
        api_key=OPENAI_API_KEY
    )


def _call_openai(messages):

    client = _create_client()

    try:

        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            temperature=0.5,
        )

    except Exception as exc:

        raise OpenAIRequestError(
            502,
            f"OpenAI error: {exc}"
        )

    try:

        content = (
            response
            .choices[0]
            .message
            .content
        )

    except (
        AttributeError,
        IndexError,
        TypeError,
    ):

        raise OpenAIRequestError(
            502,
            "Unexpected response from OpenAI."
        )

    if not content:

        raise OpenAIRequestError(
            502,
            "OpenAI returned an empty response."
        )

    return content


def generate_reply(
    user_message,
    history=None
):

    user_message = (
        user_message or ""
    ).strip()

    if not user_message:

        raise OpenAIRequestError(
            400,
            "Message cannot be empty."
        )


    # ========================================================
    # DIRECT MELIMI VOCABULARY LOOKUP
    # ========================================================

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

AUTHORITATIVE PROJECT MELIMI KNOWLEDGE
FOR THIS REQUEST:

""" + knowledge


    # ========================================================
    # BUILD CONVERSATION
    # ========================================================

    messages = [
        {
            "role": "system",
            "content": system_prompt
        }
    ]

    messages.extend(
        _trim_history(history)
    )

    messages.append({
        "role": "user",
        "content": user_message
    })


    # ========================================================
    # OPENAI
    # ========================================================

    raw_reply = _call_openai(
        messages
    )


    # ========================================================
    # FINAL MELIMI SAFETY LAYER
    # ========================================================

    final_reply = (
        apply_melimi_replacements(
            raw_reply
        )
    )

    return final_reply.strip()
