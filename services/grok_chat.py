import re
import requests

from config import GROQ_TOKEN, GROQ_URL, GROQ_MODEL
from services.language_knowledge import read_language_knowledge


# ============================================================
# TELAI SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are TelAI, a Telugu AI chatbot.

Answer the user's question naturally and accurately in Telugu.

IMPORTANT:

1. Answer the user's actual question.
2. Use Telugu for normal conversation.
3. Do not unnecessarily discuss language development.
4. Do not invent Melimi Telugu vocabulary.
5. Do not attempt to perform vocabulary replacement yourself.
6. A separate TelAI language-processing layer will convert
   established Telugu vocabulary into the project's Melimi Telugu
   vocabulary after your response is generated.

Your job is ONLY to generate the best natural Telugu response.

The final response will be processed automatically by TelAI.
"""


# ============================================================
# READ MELIMI VOCABULARY MAPPINGS
# ============================================================

def get_replacement_mappings():
    """
    Read the language files and extract mappings such as:

        బాసట = సహాయం
        హత్తరం = ప్రభావం
        ముప్పు = ప్రమాదం

    Meaning:

        ordinary Telugu -> Melimi Telugu

    Example:

        సహాయం -> బాసట
    """

    try:

        language_text = read_language_knowledge()

    except Exception as error:

        print(
            "LANGUAGE KNOWLEDGE ERROR:",
            str(error)
        )

        return []


    mappings = []


    # --------------------------------------------------------
    # Read line by line
    # --------------------------------------------------------

    for line in language_text.splitlines():

        line = line.strip()


        if not line:
            continue


        # Ignore comments/headings

        if line.startswith("#"):
            continue


        # ----------------------------------------------------
        # Expected format:
        #
        # మేలిమి పదం = సాధారణ పదం
        #
        # Example:
        #
        # బాసట = సహాయం
        # ----------------------------------------------------

        if "=" not in line:
            continue


        left, right = line.split(
            "=",
            1
        )


        melimi_word = left.strip()

        standard_word = right.strip()


        if not melimi_word:
            continue


        if not standard_word:
            continue


        # Remove optional explanation after /
        #
        # Example:
        #
        # బాసట = సహాయం / help
        #
        # We only want:
        #
        # సహాయం
        #

        standard_word = (
            standard_word
            .split("/", 1)[0]
            .strip()
        )


        # Avoid extremely long entries

        if (
            len(melimi_word) > 100
            or len(standard_word) > 100
        ):
            continue


        mappings.append(
            (
                standard_word,
                melimi_word
            )
        )


    return mappings


# ============================================================
# REPLACE WORDS
# ============================================================

def replace_melimi_words(text):
    """
    Replace established ordinary Telugu vocabulary with
    Melimi Telugu vocabulary.

    Example:

        నాకు సహాయం కావాలి.

    becomes:

        నాకు బాసట కావాలి.
    """

    if not text:
        return text


    mappings = get_replacement_mappings()


    if not mappings:
        return text


    # --------------------------------------------------------
    # Longest words first.
    #
    # This prevents a short mapping from replacing part of
    # a longer mapping.
    # --------------------------------------------------------

    mappings.sort(
        key=lambda item: len(item[0]),
        reverse=True
    )


    result = text


    for standard_word, melimi_word in mappings:

        # Escape the vocabulary for regex

        escaped = re.escape(standard_word)


        # ----------------------------------------------------
        # Telugu does not have the same whitespace rules as
        # English, so use a conservative boundary approach.
        #
        # Do not replace if the word is embedded inside
        # another Telugu word.
        # ----------------------------------------------------

        pattern = re.compile(
            rf"(?<![\u0C00-\u0C7F])"
            rf"{escaped}"
            rf"(?![\u0C00-\u0C7F])"
        )


        result = pattern.sub(
            melimi_word,
            result
        )


    return result


# ============================================================
# GENERATE TELUGU RESPONSE
# ============================================================

def generate_response(
    message: str,
    history=None
):

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]


    # --------------------------------------------------------
    # Add recent conversation
    # --------------------------------------------------------

    if history:

        for item in history[-10:]:

            role = item.get("role")
            content = item.get("content")


            if (
                role in (
                    "user",
                    "assistant"
                )
                and content
            ):

                messages.append(
                    {
                        "role": role,
                        "content": content
                    }
                )


    # --------------------------------------------------------
    # Current user message
    # --------------------------------------------------------

    messages.append(
        {
            "role": "user",
            "content": message
        }
    )


    payload = {
        "model": GROQ_MODEL,
        "messages": messages,
        "temperature": 0.4,
        "max_tokens": 1500
    }


    headers = {
        "Authorization":
            f"Bearer {GROQ_TOKEN}",

        "Content-Type":
            "application/json"
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


    # --------------------------------------------------------
    # API error
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # Read Groq response
    # --------------------------------------------------------

    try:

        data = response.json()


        reply = (
            data["choices"][0]
            ["message"]
            ["content"]
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


# ============================================================
# MAIN TELAI CHAT FUNCTION
# ============================================================

def chat_with_grok(
    message: str,
    history=None
):

    if not GROQ_TOKEN:

        raise RuntimeError(
            "GROQ_TOKEN is not configured"
        )


    # --------------------------------------------------------
    # STEP 1
    #
    # AI generates a normal Telugu response.
    # --------------------------------------------------------

    generated_reply = generate_response(
        message,
        history
    )


    print(
        "GROQ ORIGINAL:",
        generated_reply
    )


    # --------------------------------------------------------
    # STEP 2
    #
    # Match generated words against the language files.
    # --------------------------------------------------------

    final_reply = replace_melimi_words(
        generated_reply
    )


    # --------------------------------------------------------
    # STEP 3
    #
    # Return the processed response.
    # --------------------------------------------------------

    print(
        "TELAI FINAL:",
        final_reply
    )


    return final_reply
