from melimi_morphology import repair_known_forms, standard_to_melimi


def test_cinema_paradigm():
    assert standard_to_melimi("సినిమా") == "తెఱాటం"
    assert standard_to_melimi("సినిమాలు") == "తెఱాటాలు"
    assert standard_to_melimi("సినిమాలను") == "తెఱాటాలను"


def test_problem_inflection():
    assert repair_known_forms("సమస్య") == "చిక్కు"
    assert repair_known_forms("సమస్యలు") == "చిక్కులు"
    assert repair_known_forms("సమస్యలను") == "చిక్కులను"


def test_no_bad_suffix_copy():
    text = repair_known_forms("సినిమాలు మరియు సినిమాలను")
    assert "తెఱాటంలు" not in text
    assert "తెఱాటంలను" not in text
    assert "తెఱాటాలు" in text
    assert "తెఱాటాలను" in text


def test_adjective_forms():
    assert repair_known_forms("ఆసక్తికరమైన") == "హాళికాను"
    assert repair_known_forms("ఆసక్తికరంగా") == "హాళికానుగా"
