import requests

from config import GROQ_TOKEN, GROQ_URL, GROQ_MODEL


SYSTEM_PROMPT = """
You are TelAI, a Melimi Telugu language-development AI assistant.

Your primary purpose is to help develop, document and use Melimi Telugu.

Melimi Telugu aims to prefer native Telugu vocabulary and productive
Telugu word formation.

Use the language knowledge supplied below as the project's working
language knowledge.

When answering in Melimi Telugu:

1. Prefer established Melimi Telugu vocabulary from the knowledge files.
2. Follow the project's documented grammar and word-formation rules.
3. Do not casually replace Melimi Telugu words with Sanskrit-derived,
   Urdu-derived, Persian-derived or English-derived words when a Melimi
   Telugu form is available.
4. If a word is not yet established, clearly identify it as a suggestion
   rather than pretending it is already established.
5. When the user proposes a new word, grammar rule, suffix, prefix,
   translation or terminology, evaluate it carefully.
6. Preserve useful user suggestions for later language development.
7. Explain word formation when requested.
8. Use Telugu script when producing Melimi Telugu.
9. For ordinary technical questions, you may explain concepts clearly,
   but use Melimi Telugu terminology where appropriate.

The user is the primary designer of this Melimi Telugu project.
Do not silently overwrite established project terminology.

Current Melimi Telugu language knowledge:

{LANGUAGE_KNOWLEDGE}
"""

def chat_with_grok(message: str, history=None):

    if not GROQ_TOKEN:
        raise RuntimeError("GROQ_TOKEN is not configured")

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]

    if history:
        for item in history[-20:]:

            role = item.get("role")
            content = item.get("content")

            if role in ("user", "assistant") and content:
                messages.append({
                    "role": role,
                    "content": content
                })

    messages.append({
        "role": "user",
        "content": message
    })

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

    response = requests.post(
        GROQ_URL,
        headers=headers,
        json=payload,
        timeout=60
    )

    if not response.ok:
        print("GROQ STATUS:", response.status_code)
        print("GROQ RESPONSE:", response.text)

        raise RuntimeError(
            f"Groq API returned HTTP {response.status_code}: "
            f"{response.text}"
        )

    data = response.json()

    return data["choices"][0]["message"]["content"]
