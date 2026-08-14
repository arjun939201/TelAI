
"""Melimi knowledge layer.

It retrieves linguistic evidence. It does not compose or mechanically rewrite
responses. Generation belongs to the LLM under the Melimi language contract.
"""
from app.knowledge import retrieve, format_knowledge, load_vocabulary


VOCABULARY = load_vocabulary()


def retrieve_conversation_context(message: str, limit: int = 6, max_chars: int = 1400) -> str:
    return format_knowledge(retrieve(message, limit=limit), max_chars=max_chars)
