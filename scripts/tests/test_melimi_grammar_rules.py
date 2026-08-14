from app.melimi.grammar import (
    NOUN_SUFFIXES,
    VERB_SUFFIXES,
    INVARIANT_NOUN_ADJECTIVE_RULE,
    is_non_am_ending_melimi,
    grammar_policy,
)
from app.melimi.firewall import deterministic_repair


def test_noun_based_suffixes_are_distinct_from_verb_suffixes():
    assert "కాను" in NOUN_SUFFIXES
    assert "మారి" in NOUN_SUFFIXES
    assert "వాను" in NOUN_SUFFIXES
    assert "పాదు" in NOUN_SUFFIXES
    assert "అలవి" in VERB_SUFFIXES
    assert "అల్వి" in VERB_SUFFIXES
    assert "అరిది" in VERB_SUFFIXES
    assert "అర్ది" in VERB_SUFFIXES
    assert "కాను" not in VERB_SUFFIXES
    assert "అలవి" not in NOUN_SUFFIXES


def test_invariant_adjective_rule_is_explicit():
    assert "హాళికాను" in INVARIANT_NOUN_ADJECTIVE_RULE
    assert "ఆసక్తికరం" in INVARIANT_NOUN_ADJECTIVE_RULE
    assert "ఆసక్తికరమైన" in INVARIANT_NOUN_ADJECTIVE_RULE


def test_non_am_ending_helper():
    assert is_non_am_ending_melimi("హాళికాను")
    assert not is_non_am_ending_melimi("హత్తరం")


def test_attributive_standard_adjective_maps_to_invariant_melimi_form():
    assert deterministic_repair("ఆసక్తికరమైన ఎడాటం") == "హాళికాను ఎడాటం"


def test_predicative_melimi_form_is_left_unchanged():
    assert deterministic_repair("ఈ ఎడాటం హాళికాను") == "ఈ ఎడాటం హాళికాను"


def test_grammar_policy_mentions_category_constraints():
    policy = grammar_policy()
    assert "NOUN-BASED SUFFIXES" in policy
    assert "VERB-BASED SUFFIXES" in policy
    assert "హాళికాను" in policy
