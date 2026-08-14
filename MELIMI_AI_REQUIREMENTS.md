# TeluAI — Melimi Telugu AI Requirements

## Language identity
- Treat Melimi Telugu as a distinct Telugu-based language/register system.
- Keep Standard Telugu, Mixed Telugu and Melimi as separate modes.
- Corpus/rules outrank generic LLM knowledge.

## Vocabulary
- Prefer established native-Telugu Melimi forms.
- Do not blindly purify every word; preserve intelligibility and naturalness.
- Distinguish established, derived, proposed, experimental and rejected terms.
- Preserve user-established spellings and meanings.

## Morphology
- Noun/nominal derivation: కాను/కాన్, వాను/వాన్, మారి, పాదు, పఱ, ద/ఇద, అ, అంగి, మాలు, కము/ఇకము, గము, ఓరు, ఆది, ఓలి, ఓజ and other documented families.
- Verb derivation: అలవి/అల్వి and అరిది/అర్ది.
- Never interpret a derived Melimi form by ordinary Standard Telugu substring semantics: ముప్పుకాను ≠ ముప్పు కాదు.
- Resolve lexical root first, then apply grammatical inflection.
- Non-ం-ending adjective-capable Melimi forms may serve directly as noun and adjective: హాళికాను. Predicate -గా remains grammatical: హాళికానుగా. This is lexical/contextual, not a blanket rule for every word.

## Inflection
- Preserve plural, case, tense, person, agreement and other ordinary Telugu grammar.
- Do not create invalid forms by attaching Standard Telugu plural/case suffixes to an altered surface root.
- Example: సమస్య→చిక్కు; సమస్యలు→చిక్కులు; సమస్యలను→చిక్కులను.

## Conversation
- Understand Roman Telugu.
- Resolve short follow-ups such as ఇంకా using conversation context.
- Answer the exact task.
- For an underspecified essay request, ask for the topic instead of giving a generic tutorial.

## Generation
- Retrieval → planning → generation → local morphology/lexical validation → local repair → final answer.
- Groq is the generation engine, not the language authority.
- Never copy corpus prose as a canned answer.
- Never invent unsupported morphology merely to avoid Standard Telugu.

## Learning
- Chat-time learning is separate from the master corpus.
- Only explicit user-authored mappings/rules may enter learning candidates.
- Approved, pending and rejected states must remain distinguishable.
- Conflicts must not silently overwrite established knowledge.
- Automatic GitHub commits are disabled by default.

## Reliability
- Budget history, user input and retrieved evidence before Groq requests.
- Handle 413/429/provider errors with user-friendly messages.
- Never expose raw rate-limit reset headers to the user.
- Maintain regression tests for vocabulary, morphology, Roman Telugu, conversation, retrieval and learning.
