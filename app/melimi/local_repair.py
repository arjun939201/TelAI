
"""Local deterministic Melimi repair. Never calls an LLM."""
from app.melimi.firewall import deterministic_repair, lexical_violations, reload_firewall

def validate(text: str):
    return lexical_violations(text)

def repair(text: str):
    return deterministic_repair(text)

def reload():
    reload_firewall()
