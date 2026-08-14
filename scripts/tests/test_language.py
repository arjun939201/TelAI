
from app.language import normalize_roman_telugu


def test_roman_telugu():
    assert normalize_roman_telugu("enti") == "ఏంటి"
    assert normalize_roman_telugu("haa") == "హా"


def test_existing_telugu_is_preserved():
    assert normalize_roman_telugu("నమస్కారం") == "నమస్కారం"
