# TeluAI — Advanced Natural Standard & Melimi Telugu AI

## What changed

This version is a conceptual rewrite around **language understanding and
natural conversation**, not phrase substitution.

### Standard Telugu mode
- Natural Standard Telugu generation.
- Melimi knowledge is not injected into normal chat.
- No deliberate Melimi vocabulary leakage.

### Melimi Telugu mode
- Strict Melimi expression policy.
- Meaning is understood before language expression.
- Approved Melimi vocabulary is treated as linguistic knowledge.
- Word-formation knowledge can guide generation.
- The model is instructed to internally audit and revise its answer.
- It must not copy dictionary/corpus sentences.
- It must not blindly replace words.
- It should use a Melimi form whenever an appropriate established form exists.
- It should not invent a word just to avoid a loanword.

### Conversation intelligence
The system separates:
1. language normalization
2. conversation state
3. contextual intent
4. response planning
5. language generation
6. Melimi language policy
7. local language audit

Short messages are context-sensitive.

Example:

Assistant: `నీవు ఏమైనా ఆలోచిస్తున్నావా?`
User: `enti`

The system marks this as a clarification request rather than interpreting
`enti` as an isolated new question.

### Avoiding "file-copy AI"
Vocabulary and corpus entries are **evidence**, not response templates.
The prompt explicitly tells the model to:
- understand;
- reason;
- compose;
- self-check;
- revise;
- answer.

It must not stitch retrieved words or copy corpus phrases.

## Architecture

```text
User
 ↓
Input normalization
 ↓
Conversation state
 ↓
Contextual understanding
 ↓
Intent
 ↓
Relevant linguistic retrieval
 ↓
Natural response generation
 ↓
Melimi self-audit (inside the same model call)
 ↓
Response
```

The design deliberately avoids an extra Groq call for every message.

## Corpus

The original repository's large `data/vocabulary.json` is preserved by
`scripts/ensure_corpus.py`.

If the JSON is already present, it is never overwritten.

If the package is deployed without the large JSON, the script restores it from:

`https://raw.githubusercontent.com/arjun939201/TeluAI/main/data/vocabulary.json`

For a permanent standalone copy, run the script once while online and keep
the resulting `data/vocabulary.json` before uploading.

## Run

```bash
pip install -r requirements.txt
python scripts/ensure_corpus.py
pytest -q
uvicorn app.main:app --reload
```

Set:

```text
GROQ_TOKEN=your_key
GROQ_MODEL=llama-3.3-70b-versatile
```

## Important

This is a major architectural direction. The quality of Melimi generation
still depends on the quality and coverage of the authoritative Melimi corpus.
The system is designed so that adding better corpus/grammar knowledge improves
the language engine rather than turning the chatbot into a phrase lookup bot.
