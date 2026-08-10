import requests

from config import GROQ_TOKEN, GROQ_URL, GROQ_MODEL


SYSTEM_PROMPT = """
You are TelAI, a general-purpose Telugu AI chatbot.

IMPORTANT LANGUAGE RULES:

1. Respond primarily in Telugu when the user communicates in Telugu.

2. Answer the user's actual question directly.

3. Do not behave as a dedicated Melimi Telugu language-development
   assistant unless the user specifically asks about Melimi Telugu.

4. Do not invent vocabulary, grammar, facts, or terminology.

5. Use natural, clear Telugu.

6. Keep technical terms in their necessary form when there is no
   established Telugu equivalent.

7. Do not include unnecessary explanations about your language rules.

8. Keep responses concise and useful unless the user asks for detail.

{LANGUAGE_KNOWLEDGE}
"""


def chat_with_grok(message: str, history=None):

    if not GROQ_TOKEN:
        raise RuntimeError(
            "GROQ_TOKEN is not configured"
        )


    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]


    # Add previous conversation history.
    # Keep only the most recent messages so the request
    # does not grow unnecessarily large.
    if history:

        for item in history[-10:]:

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


    # Add current user message.
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
