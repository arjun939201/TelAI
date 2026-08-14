# TeluAI Chat-Time Learner

TeluAI now has a persistent, controlled learning layer separate from the authoritative Melimi corpus.

## Storage

- Local development: `data/chat_learning.sqlite3`.
- Render/production: set `DATABASE_URL` to a PostgreSQL connection string. The application automatically creates the `melimi_learning` table on startup.
- PostgreSQL uses `psycopg[binary]`; SQLite remains the zero-configuration fallback.

## What is learned automatically

Only **explicit user-authored equivalence statements** are promoted automatically, such as:

- `సహాయం = బాసట`
- `సమస్య → చిక్కు`

Ordinary conversation and AI-generated text are not automatically promoted. This prevents hallucinations from becoming language rules.

## Statuses

Each item has one of:

- `pending` — candidate knowledge
- `approved` — available to future Melimi retrieval
- `rejected` — retained as rejected evidence and not used for generation

The master Melimi corpus is never rewritten by the learner.

## API

- `GET /learner/knowledge?status=approved`
- `POST /learner/{id}/status` with `{ "status": "approved" | "pending" | "rejected" }`

Approved chat-time knowledge is retrieved only when relevant to the current Melimi request, keeping Groq token usage small.
