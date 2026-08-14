from app.melimi.firewall import deterministic_repair
from app.linguistics.normalizer import normalize_roman_telugu
from app.conversation import TurnState, infer_intent
from melimi_morphology import repair_known_forms


def test_problem_inflection_is_melimi():
    assert deterministic_repair("సమస్య సమస్యలు సమస్యలను") == "చిక్కు చిక్కులు చిక్కులను"


def test_invariant_adjective():
    assert deterministic_repair("ఆసక్తికరమైన ఎడాటం") == "హాళికాను ఎడాటం"
    assert deterministic_repair("ఈ ఎడాటం ఆసక్తికరంగా ఉంది") == "ఈ ఎడాటం హాళికానుగా ఉంది"


def test_cinema_inflection():
    assert repair_known_forms("సినిమా సినిమాలు సినిమాలను") == "తెఱాటం తెఱాటాలు తెఱాటాలను"


def test_roman_telugu_context():
    assert normalize_roman_telugu("cinemas gurinchi cheppu") == "సినిమాలు గురించి చెప్పు"


def test_short_followup():
    assert infer_intent("inka", TurnState(last_assistant="సినిమాల గురించి చెప్పాను.")) == "continue_current_topic"
