
from app.retrieval.knowledge import retrieve


def test_retrieval():
    result = retrieve("నమస్కారం")
    assert result
    assert result[0]["melimi"] == "టేంకణములు"
