
from pathlib import Path
import py_compile
import sys

root = Path(__file__).resolve().parents[1]
errors = []

for path in root.rglob("*.py"):
    if ".venv" in path.parts:
        continue
    try:
        py_compile.compile(str(path), doraise=True)
    except Exception as exc:
        errors.append((path, exc))

if errors:
    for path, error in errors:
        print(path, error)
    sys.exit(1)

print("Python syntax check: PASS")
