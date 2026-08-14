# TeluAI — Melimi Telugu Complete Language Requirements

This is the implementation checklist derived from the user's supplied Melimi Telugu corpus, transfer material, and explicit later corrections. The corpus remains authoritative. This document describes what the AI must do; it is not permission to invent unsupported morphology.

## 1. Language identity

Treat Melimi Telugu as a distinct Telugu-based language/register system. Distinguish it from Standard/ordinary Telugu and Mixed Telugu. The engine must be able to understand, generate, distinguish, validate, and convert between these modes without confusing Melimi-derived words with ordinary Telugu phrases.

## 2. Vocabulary authority and provenance

Each lexical item should preserve, where available: word, meaning, word class, root, derivation, register, domain, source, confidence, status, examples, and preferred alternative. Statuses include established, corpus-supported, derived-by-rule, candidate, uncertain, proposed, experimental, approved, and rejected. Unknown is not the same as loanword.

## 3. Native-word policy

Prefer established native Telugu/Melimi forms. Do not replace every unregistered Telugu word merely because it is absent from the dictionary. Do not invent a word just to satisfy a purity rule. Explicit Standard→Melimi mappings are authoritative.

## 4. Semantic lexical interpretation

A documented Melimi formation is a whole lexical formation. Never reinterpret it as a Standard Telugu word plus an ordinary suffix. Example: `ముప్పుకాను` is a single Melimi formation meaning dangerous/characterized by danger; it is not `ముప్పు కాదు`.

## 5. Munujerpulu / prefixes

The documented prefixes must be represented as linguistic rules, not ordinary vocabulary: `అడి, అలన్, అసి, ఆ, ఇని/ఇను, ఎగన్, ఎడ/ఎడన్, ఎదురు, ఎస/ఎసన్/ఎసల్, ఒడ/ఒడన్/ఒన/ఒనన్, క్రీన్/క్రిన్, దిగన్, తోన్, పడ/పెడన్, పై/పైన్, మీదు, మీన్, మరు/మారు, మున్/మును, మై/మైన్, లోన్, వెన్/వెను/వెనుక, సాన్, మిడి, వైన్/వై, ఐన్/ఐ, తమూ, అక, ఔన్/మన్, సి/సీ, కై, ఓ, తరు, మఱి/మఱీ, బై, అమా, ఎల/ఎలన్/ఎల్, వి, లా/లాన్, సై, ఆయి, సరి, పొలో, అపా, తిరి, మెల, ఉడున్` with their corpus-defined meanings.

## 6. Padagramulu

Represent the documented padagramulu as productive/grammatical material: `దరి, లలి, కడ, చేన్/చేయన్, కాన్, రాన్, పోన్, పేరు, బోరు, ప్రెన్/ప్రెను/పెన్, ఇల, తన్/తమ్, తాన్/తా, కౌన్, కలన్/కలయన్, వెలి, మై/మే/మేన్, మేల్, రో, ఎల/ఎల్ల, పరి, వా, కో/కోన్, కడు, మిన్న్, విన్న్, మ్రాన్/మ్రా, ఱ, పారి, వల, మన్, రా, రే, వే, రట్టు/రటు, గుట్టు/గుటు, తరము/తర, నేన, కరి, బైలు/బైల్, తెలి, లెస్స/లెస, మైమై, కల` with documented meanings.

## 7. Word formation

Support documented initial-letter deletion/retention patterns, reduplication/ఆమ్రేడితం, analogy formations, padanchalamulu, and the documented examples. These are linguistic evidence, not spelling errors or arbitrary generators.

## 8. Noun-based derivation

Noun/nominal suffixes such as `కాను/కాన్, వాను/వాన్, మారి, పాదు, పఱ, ద/ఇద, అ, అంగి, మాలు, కము/ఇకము, గము, ఓరు, ఆది, ఓలి, ఓజ, ఇ` must be category-aware. Meaning comes from the base + suffix combination. The suffix is not a free-standing replacement.

## 9. Verb-based derivation

Verb suffixes such as `అలవి/అల్వి` and `అరిది/అర్ది` attach to verbs. Example: `చేయు + అలవి → చేయల్వి`. Do not attach verb-only derivation to arbitrary nouns.

## 10. Adjective behavior

Relevant Melimi forms that do **not** end in `ం` may function directly as both noun/predicative form and adjective when lexical evidence supports it. Example: `హాళికాను` can express both `ఆసక్తికరం` and `ఆసక్తికరమైన`. Do not mechanically create `హాళికానము`, `హాళికానమైన`, `హాళికానపు`, etc. unless the corpus explicitly supports such forms.

## 11. Predicative -గా behavior

When the invariant adjective-capable Melimi form is used in a `-గా` construction, attach the ordinary grammatical ending to the Melimi surface form: `హాళికాను → హాళికానుగా`; e.g. `ఈ ఎడాటం హాళికానుగా ఉంది.` This is grammatical inflection/use, not a new lexical derivation.

## 12. Inflection

The existing Telugu inflection system remains authoritative for plural, case, person, tense, agreement, and related grammatical endings. Lexical replacement must operate on the lexical root and preserve the actual grammatical suffix. Example: `సమస్య → చిక్కు`, `సమస్యలు → చిక్కులు`, `సమస్యలను → చిక్కులను`.

## 13. Grammar preservation

Preserve natural Telugu syntax, word order, tense, aspect, person, number, case, agreement, particles, postpositions, auxiliaries, and conversational structure unless the Melimi corpus explicitly establishes a different construction.

## 14. Register control

Support at least Melimi, Standard Telugu, Mixed Telugu, conversational, formal/literary, academic, technical, and Telugu-first modern register as distinct controls where the application exposes them. Melimi mode must not silently fall back to Standard Telugu.

## 15. Mixed→Melimi conversion

Convert only established mappings and supported derivations while preserving meaning and grammar. Do not perform blind global replacement.

## 16. Don't over-purify

The goal is not to replace every possible word. Naturalness, intelligibility, continuity, grammar, and expressive capability matter. An unknown word is not automatically a forbidden loan.

## 17. Technical terminology

Index and retrieve established technical terms, including network vocabulary and developer/engineering/technician vocabulary already present in the corpus.

## 18. New terminology

For a genuinely missing term: semantic decomposition → native roots → documented derivational/compound patterns → candidate generation → validation → ranking → human approval → authoritative registration. Candidate terms must never silently become established.

## 19. Semantic relationships

The knowledge layer should represent root, derived form, synonym, related term, opposite, compound, technical term, example, and derivational relationship when the source supports them.

## 20. Conversation memory

Remember user corrections and newly supplied terms in conversation, but distinguish temporary conversational knowledge from authoritative permanent language knowledge. Do not silently rewrite the permanent corpus from a single conversational correction.

## 21. Retrieval architecture

Use retrieval → context/prompt construction → generation → local validation → deterministic correction. Do not dump the entire corpus into every prompt.

## 22. Validation

Validate language/register identity, lexical authority, derivational category, grammar-preserving inflection, unsupported morphology, Standard/Mixed leakage, loanword leakage, semantic correctness, and naturalness. Unknown native-looking words must not be flagged solely because they are unknown.

## 23. Correction

Correction must be morphology-aware and file-derived. It may repair an explicit Standard→Melimi mapping with preserved inflection and supported invariant adjective behavior. It must not become a generic `replace()` engine.

## 24. Groq role

The Melimi corpus, grammar, vocabulary, terminology, and derivational rules are the authority. Groq is only the generation engine. Changing Groq models must not remove Melimi knowledge.

## 25. Evaluation

Maintain tests for lexical mappings, inflection, derivation, adjective invariance, register identity, mixed-language leakage, technical terminology, naturalness, unknown-word handling, and unsupported-morphology rejection. Evaluation should include at least everyday, educational, scientific, technical, historical, and story-generation prompts.

## 26. Core quality target

Success is not "more replacements." Success is a coherent Telugu response that understands the user's meaning, uses authoritative Melimi vocabulary and morphology, preserves grammar and context, avoids unnecessary Mixed Telugu, and does not teach unsupported inventions as established Melimi.
