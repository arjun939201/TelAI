
"""Root-aware Melimi lexical substitution: singular, plural, case-marked forms.

Covers the reported gap where the deterministic Melimi firewall replaced an
exact Standard Telugu word (సమస్య -> చిక్కు) but failed once a Telugu
grammatical suffix (plural, case marker, etc.) was attached to it.
"""

from app.melimi.firewall import lexical_violations, deterministic_repair


def test_singular_exact_match_still_works():
    assert deterministic_repair("సమస్య") == "చిక్కు"


def test_plural_suffix_lu():
    assert deterministic_repair("సమస్యలు") == "చిక్కులు"


def test_accusative_plural_suffix_lanu():
    assert deterministic_repair("సమస్యలను") == "చిక్కులను"


def test_oblique_plural_suffix_la():
    assert deterministic_repair("సమస్యల") == "చిక్కుల"


def test_dative_plural_suffix_laku():
    assert deterministic_repair("సమస్యలకు") == "చిక్కులకు"


def test_instrumental_plural_suffix_lato():
    assert deterministic_repair("సమస్యలతో") == "చిక్కులతో"


def test_locative_plural_suffix_lalo():
    assert deterministic_repair("సమస్యలలో") == "చిక్కులలో"


def test_another_root_still_handles_inflection_generally():
    # This must not be a hardcoded rule for సమస్య; సహాయం -> బాసట should also
    # inflect correctly, e.g. dative "సహాయానికి"-style plain "కు" suffix on a
    # simpler case, and the exact/plural forms.
    assert deterministic_repair("సహాయం") == "బాసట"
    assert deterministic_repair("సహాయంతో") == "బాసటతో"


def test_acceptance_sentence_one():
    text = "ఈ బిసెర్మి రంగంలో అనేక సమస్యలు ఉన్నాయి."
    expected = "ఈ బిసెర్మి రంగంలో అనేక చిక్కులు ఉన్నాయి."
    assert deterministic_repair(text) == expected


def test_acceptance_sentence_two():
    text = "పెంపుకాను సమస్యలను తీర్చాలి."
    expected = "పెంపుకాను చిక్కులను తీర్చాలి."
    assert deterministic_repair(text) == expected


def test_meaning_and_grammar_untouched_outside_the_matched_word():
    # Everything except the matched root+suffix must be byte-for-byte
    # identical: no restructuring, no reordering, no extra edits.
    before = "ఈ బిసెర్మి రంగంలో అనేక సమస్యలు ఉన్నాయి."
    after = deterministic_repair(before)
    before_words = before.replace("సమస్యలు", "").split()
    after_words = after.replace("చిక్కులు", "").split()
    assert before_words == after_words


def test_violations_report_includes_inflected_forms():
    violations = lexical_violations("ఈ రంగంలో అనేక సమస్యలు ఉన్నాయి.")
    assert any(v["source"] == "సమస్యలు" and v["preferred"] == "చిక్కులు" for v in violations)


def test_unrelated_words_are_not_mangled():
    text = "ఇది చాలా బాగుంది."
    assert deterministic_repair(text) == text


def test_unregistered_word_with_suffix_is_left_alone():
    # A word that merely LOOKS like it ends in a case suffix, but whose root
    # is not a registered Standard Telugu mapping, must not be touched.
    text = "పిల్లలు బడికి వెళ్తారు."
    assert deterministic_repair(text) == text
