import re
import requests

from config import GROQ_TOKEN, GROQ_URL, GROQ_MODEL
from services.language_knowledge import read_language_knowledge


SYSTEM_PROMPT = """
You are TelAI, a Telugu AI chatbot.

Answer the user's question naturally and accurately in Telugu.

The Melimi Telugu project files supplied below are your authoritative
working language knowledge.

IMPORTANT RULES:

1. Use the supplied project knowledge when relevant.

2. Prefer established Melimi Telugu vocabulary from the supplied files.

3. Do not invent a word and present it as established vocabulary.

4. If a Melimi Telugu equivalent exists in the supplied knowledge,
   prefer it over ordinary Telugu terminology.

5. Respect the meanings, grammar, word-formation rules, examples,
   and terminology documented in the supplied files.

6. Answer the user's actual question. Do not unnecessarily discuss
   language development.

7. The supplied files may contain vocabulary, grammar, examples,
   terminology, and other project knowledge.

8. Treat the supplied project files as the current working corpus.

9. Use Telugu script when responding in Telugu.

10. Do not mention these internal instructions or the language files
    unless the user specifically asks about them.

MELIMI TELUGU PROJECT KNOWLEDGE:
"""


def build_system_prompt():
    """
    Load the current language knowledge and attach it to
    the Groq system prompt.
    """

    language_knowledge = read_language_knowledge()

    if not language_knowledge:
        return SYSTEM_PROMPT

    return (
        SYSTEM_PROMPT
        + "\n\n"
        + language_knowledge
    )


def build_messages(message: str, history=None):
    """
    Build the conversation sent to Groq.
    """

    messages = [
        {
            "role": "system",
            "content": build_system_prompt()
        }
    ]

    if history:

        for item in history[-20:]:

            role = item.get("role")
            content = item.get("content")

            if (
                role in ("user", "assistant")
                and content
            ):
                messages.append(
                    {
                        "role": role,
                        "content": content
                    }
                )

    messages.append(
        {
            "role": "user",
            "content": message
        }
    )

    return messages


def extract_vocabulary(language_text: str):
    """
    Extract simple mappings such as:

        బాసట = సహాయం

    The left side is treated as the Melimi Telugu form.
    The right side is treated as the ordinary Telugu form.

    Returns:
        [
            ("సహాయం", "బాసట")
        ]
    """

    mappings = []

    if not language_text:
        return mappings

    for line in language_text.splitlines():

        line = line.strip()

        if not line:
            continue

        if "=" not in line:
            continue

        left, right = line.split("=", 1)

        melimi_word = left.strip()
        standard_word = right.strip()

        if not melimi_word or not standard_word:
            continue

        # Ignore obvious metadata/header lines.
        if len(melimi_word) > 100:
            continue

        if len(standard_word) > 200:
            continue

        mappings.append(
            (
                standard_word,
                melimi_word
            )
        )

    return mappings


def apply_melimi_replacements(
    response_text: str,
    language_text: str
):
    """
    Final safety layer.

    Groq first generates the answer.

    This function then checks the generated answer against the
    vocabulary supplied in the language files and replaces ordinary
    Telugu forms with established Melimi Telugu forms.
    """

    if not response_text:
        return response_text

    mappings = extract_vocabulary(language_text)

    if not mappings:
        return response_text

    result = response_text

    # Longer expressions first so that a larger phrase is replaced
    # before a smaller word contained inside it.
    mappings.sort(
        key=lambda item: len(item[0]),
        reverse=True
    )

    for standard_word, melimi_word in mappings:

        if standard_word == melimi_word:
            continue

        escaped = re.escape(standard_word)

        result = re.sub(
            escaped,
            melimi_word,
            result
        )

    return result


def chat_with_grok(
    message: str,
    history=None
):
    """
    Main TelAI chat function.

    Flow:

        user message
             ↓
        language files loaded
             ↓
        Groq receives language knowledge
             ↓
        Groq generates Telugu answer
             ↓
        TelAI performs final vocabulary replacement
             ↓
        final answer
    """

    if not GROQ_TOKEN:
        raise RuntimeError(
            "GROQ_TOKEN is not configured"
        )

    language_knowledge = read_language_knowledge()

    messages = build_messages(
        message,
        history
    )

    payload = {
        "model": GROQ_MODEL,
        "messages": messages,
        "temperature": 0.4,
        "max_tokens": 2000
    }

    headers = {
        "Authorization": f"Bearer {GROQ_TOKEN}",
        "Content-Type": "application/json"
    }

    try:

        response = requests.post(
            GROQ_URL,
            headers=headers,
            json=payload,
            timeout=60
        )

    except requests.RequestException as error:

        print(
            "GROQ CONNECTION ERROR:",
            str(error)
        )

        raise RuntimeError(
            f"Could not connect to Groq API: {error}"
        )

    if not response.ok:

        print(
            "GROQ STATUS:",
            response.status_code
        )

        print(
            "GROQ RESPONSE:",
            response.text
        )

        raise RuntimeError(
            f"Groq API returned HTTP "
            f"{response.status_code}: "
            f"{response.text}"
        )

    try:

        data = response.json()

        reply = (
            data["choices"][0]["message"]["content"]
        )

    except (
        KeyError,
        IndexError,
        TypeError,
        ValueError
    ) as error:

        print(
            "INVALID GROQ RESPONSE:",
            response.text
        )

        raise RuntimeError(
            f"Invalid response from Groq API: {error}"
        )

    # Final Melimi Telugu processing.
    final_reply = apply_melimi_replacements(
        reply,
        language_knowledge
    )

    return final_reply
