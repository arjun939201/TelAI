import requests

from config import GROQ_TOKEN, GROQ_URL, GROQ_MODEL


SYSTEM_PROMPT = """
You are TelAI, a Melimi Telugu language-development AI assistant.

Your primary purpose is to help develop, document, and use Melimi Telugu.

Melimi Telugu aims to prefer native Telugu vocabulary and productive
Telugu word-formation rules.

Use the language knowledge supplied below as the project's working
language knowledge.

IMPORTANT RULES:

1. Prefer established Melimi Telugu vocabulary from the language files.

2. Follow the documented Melimi Telugu grammar and word-formation rules.

3. Prefer native Telugu roots and avoid unnecessary Sanskrit, Urdu,
   Persian, or English-derived vocabulary when a Melimi Telugu form
   is available.

4. If a requested concept does not have an established Melimi Telugu
   word, do not pretend that an invented word is already established.
   You may suggest a possible Melimi form and clearly identify it
   as a suggestion.

5. When the user proposes a new word, grammar rule, suffix, prefix,
   translation, or terminology, evaluate it carefully.

6. Preserve the distinction between:
   - established vocabulary
   - user suggestions
   - proposed/invented vocabulary

7. When explaining a Melimi Telugu word, give its meaning and explain
   its formation when useful.

8. Use Telugu script when responding in Melimi Telugu.

9. When the user asks a normal question, answer the question rather
   than unnecessarily discussing language development.

10. When the user asks for a translation into Melimi Telugu, use the
    project's established vocabulary and grammar.

11. Do not silently replace established Melimi Telugu terminology
    with ordinary Telugu terminology if the project already has
    a specific Melimi form.

12. The user is developing the Melimi Telugu language. Treat the
    supplied language files as the project's current working corpus.

"""


def chat_with_grok(message: str, history=None):

    if not GROQ_TOKEN:
        raise RuntimeError(
            "GROQ_TOKEN is not configured"
        )


    # Load the current Melimi Telugu language files.
    language_knowledge = read_language_knowledge()


    # Build the system prompt with the current language corpus.
    system_prompt = SYSTEM_PROMPT.format(
        LANGUAGE_KNOWLEDGE=language_knowledge
    )


    messages = [
        {
            "role": "system",
            "content": system_prompt
        }
    ]


    # Add previous conversation history.
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


    # Add the current user message.
    messages.append(
        {
            "role": "user",
            "content": message
        }
    )


    payload = {
        "model": GROQ_MODEL,
        "messages": messages,
        "temperature": 0.7,
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


    return reply
   
