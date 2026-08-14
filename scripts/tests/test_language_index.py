
from app.melimi.index import inventory, language_profile, relevant_language_context


def test_subject_has_language_layers():
    info = inventory()
    assert info["documents"] >= 6
    assert info["by_kind"]["vocabulary"] >= 1
    assert info["by_kind"]["grammar"] >= 1
    assert info["by_kind"]["word_formation"] >= 1
    assert info["by_kind"]["rules"] >= 1


def test_profile_contains_rules():
    profile = language_profile()
    assert "MELIMI" in profile.upper()


def test_relevant_context():
    text = relevant_language_context("హత్తరం")
    assert "హత్తరం" in text or "ప్రభావం" in text
