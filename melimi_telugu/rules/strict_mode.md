# Strict Melimi Telugu Mode

Melimi mode is a constrained language-generation mode, not a replacement filter.

Pipeline:
1. Detect conversational meaning and intent from the full turn history.
2. Retrieve relevant Melimi subject evidence.
3. Build a compact grammar/word-formation language profile.
4. Generate an original response in ordinary, natural conversational Telugu,
   then substitute only the specific words that have a registered Melimi
   equivalent, keeping grammar and suffixes intact.
5. Run a deterministic lexical gate against established Standard→Melimi mappings and known loanwords.
6. If a violation is found, perform up to the configured repair attempts.
7. Run the final audit and expose only the response to the user.

Unknown native-looking Telugu is never treated as a loanword merely because it is absent from the corpus.

Established language knowledge has priority over generic model knowledge. Unsupported Melimi words must not be invented merely for purity.

8. Native-word and derivational constraints are authoritative: do not invent a Melimi word merely to satisfy a purity constraint.
9. Noun-based suffixes and verb-based suffixes must be applied only to their documented base categories.
10. Relevant non-ం/nasal-ending Melimi lexical forms may serve as invariant noun/adjective forms; preserve their surface form when used adjectivally.
