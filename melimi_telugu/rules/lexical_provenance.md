# Strict Melimi lexical provenance

TeluAI must distinguish these concepts:

1. **Registered Melimi word** — appears on the Melimi side of an approved
   vocabulary entry or user-verified registration.
2. **Native/grammar word** — Telugu structural/native material that should not be
   painted red merely because it is not in the Melimi dictionary.
3. **Loan/borrowed word** — explicitly classified in the language subject as
   `loan`, `loanword`, `borrowed`, `foreign`, `sanskrit_loan`,
   `sanskrit-derived`, or `non_native`.
4. **Unresolved loan** — a classified loan word for which no Melimi equivalent
   has yet been registered.
5. **Mapped Standard term** — an explicit Standard->Melimi mapping exists.
6. **Unknown word** — no evidence. Unknown is NOT equivalent to loan.

Only unresolved loans and explicit mapped gaps are red/clickable in chat.

The system must never infer that every absent word is non-Melimi.
