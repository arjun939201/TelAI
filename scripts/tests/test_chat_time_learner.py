import os
import tempfile


def test_chat_time_learning_persists_explicit_mapping(monkeypatch):
    with tempfile.TemporaryDirectory() as td:
        db = os.path.join(td, "learn.sqlite3")
        monkeypatch.setattr("app.learner_store.SQLITE_FILE", db)
        monkeypatch.delenv("DATABASE_URL", raising=False)
        from app.chat_learner import learn_from_user_message, format_learned
        from app.learner_store import list_learning

        items = learn_from_user_message("సహాయం = బాసట")
        assert len(items) == 1
        assert items[0]["status"] == "approved"
        assert items[0]["standard"] == "సహాయం"
        assert items[0]["melimi"] == "బాసట"
        assert "సహాయం → బాసట" in format_learned("సహాయం")
        assert list_learning(status="approved")[0]["melimi"] == "బాసట"


def test_ordinary_sentence_is_not_auto_learned(monkeypatch, tmp_path):
    db = str(tmp_path / "learn.sqlite3")
    monkeypatch.setattr("app.learner_store.SQLITE_FILE", db)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    from app.chat_learner import learn_from_user_message
    from app.learner_store import list_learning

    assert learn_from_user_message("మేలిమి తెలుగులో ఏదైనా చెప్పు") == []
    assert list_learning() == []
