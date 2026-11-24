from src.i18n import LANGUAGES, load, t


def test_every_language_has_the_same_keys():
    # If a text is added to es.json but forgotten in en.json, the English page would crash.
    keys = {lang: set(load(lang)) for lang in LANGUAGES}
    assert keys["en"] == keys["es"]


def test_placeholders_are_filled():
    assert t("delta", "en", change=-20.94, base="2017-01") == "-20.9% vs. 2017-01"
