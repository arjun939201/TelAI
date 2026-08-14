# Render import fix

The previous deployment failed because the repository contained both:

- `app/conversation.py`
- `app/conversation/__init__.py`

Python imported the package directory instead of `conversation.py`, so
`build_state` could not be imported.

This ZIP removes the conflicting `app/conversation/` directory and keeps
`app/conversation.py` as the canonical conversation module.

Render start command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Before deployment, make sure the full `data/vocabulary.json` corpus is present.
If needed:

```bash
python scripts/ensure_corpus.py
```
