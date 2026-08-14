
from app.linguistics.normalizer import normalize_roman_telugu, analyze_input


def test_roman_telugu():
    assert normalize_roman_telugu("enti") == "ఏంటి"
    assert normalize_roman_telugu("haa") == "హా"


def test_telugu_preserved():
    text = "నమస్కారం"
    assert normalize_roman_telugu(text) == text


def test_mixed_input_signal():
    result = analyze_input("nenu Telugu మాట్లాడుతున్నాను")
    assert result["mixed_script"] is True
