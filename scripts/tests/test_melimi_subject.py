
from app.melimi.subject import subject_inventory, search_subject


def test_subject_exists():
    info = subject_inventory()
    assert info["documents"] >= 3
    assert info["by_kind"]["vocabulary"] >= 1
    assert info["by_kind"]["grammar"] >= 1


def test_subject_retrieval():
    results = search_subject("హత్తరం ప్రభావం")
    assert results
