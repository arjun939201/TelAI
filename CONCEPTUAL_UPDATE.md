# TeluAI Conceptual Conversation Update

This package is designed around a broader architectural change, not a fix for one
word such as `enti`.

## Core idea

TeluAI should separate:

1. Understanding the user's language
2. Understanding the current conversation
3. Planning the conversational move
4. Generating the answer
5. Expressing that answer in Melimi
6. Validating the final language

## Important behavior

A short message must be interpreted against the previous turn.

Example:

Assistant: `నీవు ఏమైనా ఆలోచిస్తున్నావా?`
User: `enti`

The system should understand this as a clarification request about the
assistant's previous question, not as a new isolated question.

## Natural conversation principles

- Answer the user's current conversational move first.
- Continue the existing topic when possible.
- Do not restart the conversation after every short reply.
- Do not automatically ask a generic follow-up question.
- Treat short words as context-sensitive.
- Keep uncertainty when the meaning is genuinely ambiguous.
- Use the LLM for broad language reasoning, but give it compact local context.
- Avoid additional LLM calls for local state/intent hints.

## Melimi principles

Melimi mode should be a language-expression policy, not a blind replacement pass.

- Prefer approved Melimi vocabulary whenever it fits.
- Preserve grammatical role and meaning.
- Use Melimi word-formation rules where supported.
- Do not invent an unsupported form just to remove a loanword.
- Check the completed answer for unnecessary standard/loan vocabulary.
- Keep the result conversational and natural.

## Integration

The modules are intentionally independent so they can be integrated into the
existing `main.py`, `groq_client.py`, `melimi_engine.py`, and prompt system
without replacing the current vocabulary or corpus.

The intended single-request flow is:

user
→ local normalization/retrieval
→ conversation state
→ contextual understanding
→ response plan
→ Melimi policy/context
→ one normal Groq request
→ local final validation
→ response

This is a conceptual foundation for the next major TeluAI architecture stage.


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
