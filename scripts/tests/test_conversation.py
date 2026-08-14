
from app.conversation.state import ConversationState
from app.conversation.understanding import infer_intent


def test_enti_after_question_is_clarification():
    state = ConversationState(
        open_question="నీవు ఏమైనా ఆలోచిస్తున్నావా?"
    )
    result = infer_intent("enti", state)
    assert result["intent"] == "clarification_request"


def test_sare():
    assert infer_intent("sare", ConversationState())["intent"] == "agreement"


def test_cheppu():
    assert infer_intent("cheppu", ConversationState())["intent"] == "continue_current_topic"
