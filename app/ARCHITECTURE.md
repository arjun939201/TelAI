# TeluAI runtime architecture

## One Groq generation per chat turn

1. Local conversation/linguistic analysis.
2. Relevant Melimi subject retrieval.
3. One Groq generation request.
4. Local Melimi validation.
5. Local deterministic repair from explicit file mappings.
6. Return response.

There is no LLM retry loop for lexical validation.

Unknown words are not treated as loanwords merely because they are absent from
the corpus. Only explicit file mappings create deterministic lexical rules.
