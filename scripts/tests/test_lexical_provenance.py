
from app.melimi.registry import audit_response, lexical_inventory

def test_unknown_is_not_automatically_red():
    rows=audit_response("ఏమిటి అనుకుంటున్నారు నువ్వు")
    assert all(not x["clickable"] for x in rows)

def test_registered_melimi_is_not_red():
    rows=audit_response("హత్తరం")
    assert all(not x["clickable"] for x in rows)

def test_unknown_is_not_claimed_as_melimi():
    rows=audit_response("అనుకుంటున్నారు")
    assert rows[0]["registered"] is False
