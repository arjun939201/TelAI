# TeluAI — Advantage Update Package

This is an **overlay package** for the current `arjun939201/TeluAI` repository.

## Improvements

1. **Roman Telugu understanding**
   - Common inputs such as `haa`, `emle`, `sare`, `cheppu`, `nuvvu`, etc. get a local Telugu-script hint.
   - Existing Telugu-script input is left unchanged.

2. **Intent hints**
   - Greeting, acknowledgement, agreement, gratitude, asking-how, and continuation intents are detected locally.
   - These are hints only; Groq still performs the actual language understanding.

3. **No extra LLM call**
   - The update does not add another API request.
   - It only enriches the existing system prompt.

4. **Safer output**
   - Removes accidental `Assistant:` / `TeluAI:` prefixes.
   - Collapses excessive blank lines.
   - Does **not** perform automatic Standard→Melimi replacement.

5. **Regression tests**
   - Basic tests cover Roman-Telugu normalization and intent detection.

## Apply

Unzip this package into the **root of your existing TeluAI repository**, then run:

```bash
python apply_updates.py
```

Then:

```bash
pip install -r requirements.txt
pytest -q
```

Finally run your normal FastAPI/Render command.

### Important

This package is intentionally an **overlay**, not a replacement of your whole repository. Your existing `vocabulary.json`, learned corpus, frontend, and other files remain untouched.

If an update anchor does not match because you have changed the source code separately, the script stops instead of silently corrupting the file.
