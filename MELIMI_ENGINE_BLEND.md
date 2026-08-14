# TeluAI — Melimi Engine 1 Blend

This build uses the existing TeluAI repository as the base. The existing UI, Groq client, conversation system, Melimi subject architecture, GitHub teaching/registration, lexical firewall, and one-Groq-call design are preserved.

## Added from Melimi Telugu Engine 1

- A consolidated `melimi_telugu/corpus/Melimi_Telugu_Master.txt` corpus containing the transferred Melimi Telugu material.
- SQLite FTS5 passage retrieval for broad corpus/grammar/prose search.
- Incremental indexing so changed subject files are refreshed automatically.
- `scripts/ingest_melimi_fts.py` for manual index rebuilding.

## Important

The FTS layer is supplementary. It does **not** replace the existing structured Melimi subject index or the authoritative vocabulary/grammar rules. Groq remains the generation engine. Melimi validation and deterministic repair remain local; no second Groq call is introduced.

The frontend is intentionally unchanged.


## Melimi register identity

Melimi Telugu is treated by TeluAI as a distinct Telugu-based language
register, not as Standard Telugu with blind word substitution. Its
authoritative vocabulary and native-Telugu derivational system determine
lexical meaning and word formation. A complete formation such as `ముప్పుకాను`
must be interpreted as its documented Melimi meaning (dangerous), not as
`ముప్పు కాదు`.

Non-`ం`-ending Melimi lexical forms may be invariant noun/adjectives where
the corpus supports that function. For example, `హాళికాను` can represent
both `ఆసక్తికరం` and `ఆసక్తికరమైన`; in predicative/adverbial use,
`ఆసక్తికరంగా ఉంది` becomes `హాళికానుగా ఉంది`.
