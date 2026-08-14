
"""Controlled learning: candidates are evidence, never instant authority."""
import json
import os
from datetime import datetime, timezone
from typing import Dict, List

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILE = os.path.join(ROOT, "data", "learning_candidates.json")


def load_candidates() -> List[Dict]:
    if not os.path.exists(FILE):
        return []
    try:
        with open(FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception:
        return []


def add_candidate(text: str, source: str = "user") -> Dict:
    items = load_candidates()
    item = {
        "status": "candidate",
        "source": source,
        "text": text.strip(),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    items.append(item)
    os.makedirs(os.path.dirname(FILE), exist_ok=True)
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    return item
