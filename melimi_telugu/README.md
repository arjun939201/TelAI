# మేలిమి తెలుగు — Language Subject

This directory is the authoritative Melimi Telugu language subject for TeluAI.
It is language knowledge, not a chatbot phrase bank.

## Identity

Melimi Telugu is treated as a distinct Telugu-based language/register system.
It must not be confused with Standard Telugu or Mixed Telugu, and a Melimi
formation must not be reinterpreted as an ordinary Telugu phrase merely because
its spelling resembles ordinary Telugu pieces.

## Knowledge layers

- `corpus/` — historical/source corpus and preserved user material.
- `vocabulary/` — lexical mappings, status, provenance and terminology.
- `grammar/` — grammatical and derivational rules.
- `word_formation/` — munujerpulu, padagramulu, derivation, reduplication,
  analogy and other documented formation patterns.
- `syntax/` — sentence structure and relationships.
- `examples/` — evaluation and usage examples.
- `prose/` — longer language evidence.
- `rules/` — authority, register, generation, provenance and validation policy.

## Authority

The supplied corpus and explicitly approved rules are authoritative. Generic
LLM knowledge is not authoritative. Unknown is not the same as loanword, and a
newly generated candidate is not automatically an established Melimi word.

## Generation

The engine should understand meaning and context, retrieve relevant language
evidence, generate an original response in the Melimi register, and then run a
local morphology-aware audit/correction pass. It must not rely on blind global
word replacement.

Ordinary Telugu grammar remains the grammatical framework unless the corpus
explicitly establishes otherwise. Established lexical and derivational Melimi
forms supply the distinctive language/register behavior.
