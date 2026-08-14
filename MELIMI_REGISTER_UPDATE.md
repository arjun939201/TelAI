# Melimi Telugu Register Update

This repository treats Melimi Telugu as a distinct Telugu-based language
register, not as Standard Telugu with blind word substitution.

Key rules implemented:
- Native Telugu lexical material is preferred/required for Melimi expression.
- Noun-based derivational suffixes such as కాను, మారి, వాను, పాదు are interpreted
  as part of the complete base+suffix formation.
- Verb-based suffixes such as అలవి/అల్వి and అరిది/అర్ది attach to verb bases.
- Existing plural/case inflection is preserved.
- Relevant non-ం-ending Melimi lexical forms may be invariant noun/adjectives.
  Example: హాళికాను = ఆసక్తికరం / ఆసక్తికరమైన.
- Predicate/adverbial -గా use is supported: ఆసక్తికరంగా ఉంది -> హాళికానుగా ఉంది.
- A complete Melimi derivation such as ముప్పుకాను must not be interpreted as
  "ముప్పు కాదు"; its documented Melimi meaning is authoritative.
