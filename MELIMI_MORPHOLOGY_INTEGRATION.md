# Melimi Morphology v11

The repository now includes `melimi_morphology.py`.

The final-response pipeline should call:

```python
from melimi_morphology import repair_known_forms
text = repair_known_forms(text)
```

**after generation and before final response validation/output.**

This deliberately applies established lexical paradigms before ordinary
inflection is carried over. In particular:

- సినిమా → తెఱాటం
- సినిమాలు → తెఱాటాలు
- సినిమాలను → తెఱాటాలను
- సమస్య → చిక్కు
- సమస్యలు → చిక్కులు
- సమస్యలను → చిక్కులను

Do not implement Melimi morphology by blindly appending Standard Telugu
suffixes to a replaced root.
