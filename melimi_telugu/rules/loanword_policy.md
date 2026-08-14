# Loanword marking policy

The chat UI must NOT mark every unregistered Telugu word red.

Normal Telugu grammatical/native words such as pronouns, particles and ordinary
native vocabulary remain visually normal even when they have not been registered
as Melimi lexical entries.

A word becomes a red clickable candidate when the language subject explicitly
classifies it as:
- loan
- loanword
- borrowed
- foreign

A Standard->Melimi mapping can also create a clickable Melimi gap when the source
word is explicitly mapped but its Melimi form is not registered.

Do not infer that an unknown Telugu-looking word is a loanword merely because it
is absent from the Melimi vocabulary. Absence is not evidence of borrowing.

To classify a word, add it to a vocabulary entry with `status: "loanword"` or
`source_type: "loanword"` and provide its Melimi equivalent when known.

## Native Melimi expression

Melimi generation should prefer native Telugu lexical material. This is a
lexical-generation requirement, not permission to fabricate replacements for
words whose Melimi equivalent has not been established by the corpus.
