"""Interface texts in several languages. No text is written inside app.py: it asks t() for it."""

import json
from functools import cache
from pathlib import Path

TRANSLATIONS_DIR = Path(__file__).resolve().parent.parent / "translations"
LANGUAGES = {"es": "Español", "en": "English"}  # code -> name shown in the switch


@cache  # read each JSON file once, not on every call
def load(lang: str) -> dict[str, str]:
    return json.loads((TRANSLATIONS_DIR / f"{lang}.json").read_text(encoding="utf-8"))


def t(key: str, lang: str, **values) -> str:
    """Text for `key` in `lang`, with {placeholders} filled from `values`.

    t("delta", "en", change=-20.9, base="2017-01") -> "-20.9% vs. 2017-01"
    A missing key raises KeyError on purpose: a visible error beats a blank label.
    """
    return load(lang)[key].format(**values)
