
from app.github_sync import status

def test_github_status_shape():
    s=status()
    assert "repository" in s and "path" in s and "configured" in s
