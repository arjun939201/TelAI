
"""Restore the full public TeluAI vocabulary before production deployment.

The script never replaces an existing large corpus.
"""
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
target = ROOT / "data" / "vocabulary.json"
url = "https://raw.githubusercontent.com/arjun939201/TeluAI/main/data/vocabulary.json"

if target.exists() and target.stat().st_size > 100_000:
    print("Large vocabulary.json already present; leaving it unchanged.")
else:
    print("Downloading the current public TeluAI vocabulary...")
    urllib.request.urlretrieve(url, target)
    print("Saved:", target, target.stat().st_size, "bytes")
