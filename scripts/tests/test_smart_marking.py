
from app.melimi.registry import audit_response

def test_unknown_telugu_is_not_automatically_loan():
    rows=audit_response("ఏమిటి అనుకుంటున్నారు")
    assert all(not x["clickable"] for x in rows)

def test_function_words_are_not_red():
    rows=audit_response("నువ్వు ఎలా ఉన్నావు")
    assert all(not x["clickable"] for x in rows)
