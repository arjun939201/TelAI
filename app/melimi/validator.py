
"""Local Melimi output validator. No Groq calls."""
from app.melimi.firewall import lexical_violations

def validate_melimi(text: str):
    violations=lexical_violations(text)
    return {"valid": not violations, "violations": violations}

def audit_melimi(text: str):
    """Backward-compatible validator API used by app.main."""
    return validate_melimi(text)
