
from app.melimi.firewall import lexical_violations, deterministic_repair

def test_help_mapping_is_file_authoritative():
    violations=lexical_violations("మీకు ఏమైనా సహాయం కావాలా?")
    assert any(x["source"]=="సహాయం" for x in violations)

def test_exact_file_mapping_is_never_allowed_to_survive():
    repaired=deterministic_repair("మీకు ఏమైనా సహాయం కావాలా?")
    assert "సహాయం" not in repaired
    assert "బాసట" in repaired
