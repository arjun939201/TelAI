
from app.melimi.local_repair import repair, validate

def test_melimi_violation_repaired_without_llm():
    text="మీకు ఏమైనా సహాయం కావాలా?"
    assert validate(text)
    fixed=repair(text)
    assert "సహాయం" not in fixed
    assert "బాసట" in fixed

def test_unknown_telugu_untouched():
    text="ఏమిటి అనుకుంటున్నారు?"
    assert repair(text)==text
