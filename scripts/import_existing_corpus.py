
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
legacy = ROOT / "data" / "vocabulary.json"
target = ROOT / "melimi_telugu" / "vocabulary" / "vocabulary.json"

if legacy.exists() and not target.exists():
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(legacy, target)
    print("Copied existing vocabulary into the Melimi language subject.")
else:
    print("Nothing copied. Existing subject vocabulary was preserved.")
