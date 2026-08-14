
from app.melimi.registry import lexical_inventory, audit_response, strict_violations

def test_normal_telugu_is_not_a_loan_by_absence():
    rows=audit_response("ఏమిటి అనుకుంటున్నారు")
    assert all(not x["clickable"] for x in rows)

def test_established_mapping_is_strict():
    v=strict_violations("ఇది ప్రభావం గురించి.")
    assert any(x.get("standard")=="ప్రభావం" for x in v)

def test_function_words_not_forbidden():
    assert not strict_violations("నువ్వు ఎలా ఉన్నావు")
