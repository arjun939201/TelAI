from pathlib import Path

from app.melimi.firewall import deterministic_repair
from app.melimi.grammar import NOUN_SUFFIXES, VERB_SUFFIXES
from app.melimi.index import build_index

ROOT = Path(__file__).resolve().parents[1]


def test_complete_language_requirements_file_exists():
    p = ROOT / "melimi_telugu" / "rules" / "complete_language_requirements.md"
    text = p.read_text(encoding="utf-8")
    assert "distinct Telugu-based language/register system" in text
    assert "Unknown is not the same as loanword" in text
    assert "సమస్యలు → చిక్కులు" in text


def test_documented_word_formation_files_are_indexed():
    paths = {d.path for d in build_index()}
    assert "melimi_telugu/word_formation/munujerpulu.json" in paths
    assert "melimi_telugu/word_formation/padagramulu.json" in paths
    assert "melimi_telugu/word_formation/derivational_suffixes.json" in paths


def test_noun_and_verb_suffix_classes_remain_separate():
    assert "కాను" in NOUN_SUFFIXES
    assert "మారి" in NOUN_SUFFIXES
    assert "వాను" in NOUN_SUFFIXES
    assert "పాదు" in NOUN_SUFFIXES
    assert "అలవి" in VERB_SUFFIXES
    assert "అరిది" in VERB_SUFFIXES
    assert "కాను" not in VERB_SUFFIXES
    assert "అలవి" not in NOUN_SUFFIXES


def test_inflection_preserves_plural_and_case():
    assert deterministic_repair("సమస్య") == "చిక్కు"
    assert deterministic_repair("సమస్యలు") == "చిక్కులు"
    assert deterministic_repair("సమస్యలను") == "చిక్కులను"


def test_invariant_adjective_behavior():
    assert deterministic_repair("ఆసక్తికరమైన ఎడాటం") == "హాళికాను ఎడాటం"
    assert deterministic_repair("ఆసక్తికరంగా ఉంది") == "హాళికానుగా ఉంది"
    assert deterministic_repair("హాళికాను") == "హాళికాను"


def test_derived_melimi_is_not_split_as_negation():
    text = "ముప్పుకాను"
    assert deterministic_repair(text) == text
    assert "ముప్పు కాదు" not in text


def test_subject_and_technical_files_are_indexed():
    paths = {d.path for d in build_index()}
    assert "melimi_telugu/vocabulary/subject_terms.json" in paths
    assert "melimi_telugu/vocabulary/technical_terms.json" in paths
