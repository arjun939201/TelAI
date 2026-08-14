
"""Restore the authoritative vocabulary from the current public repository
when this full package is deployed without the large JSON corpus.

This keeps the repository package small while preserving the existing corpus.
If vocabulary.json already exists, it is never overwritten.
"""
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
target = ROOT / "data" / "vocabulary.json"

URL = (
    "https://raw.githubusercontent.com/"
    "arjun939201/TeluAI/main/data/vocabulary.json"
)

if target.exists() and target.stat().st_size > 100000:
    print("vocabulary.json already present; leaving it unchanged.")
else:
    print("Restoring authoritative TeluAI vocabulary...")
    target.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(URL, target)
    print("Restored:", target, target.stat().st_size, "bytes")
