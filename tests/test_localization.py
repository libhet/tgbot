from app.localization.translator import TRANSLATIONS, translate


def test_translate_returns_string_for_supported_locale():
    assert translate("auth.success", locale="en") == TRANSLATIONS["en"]["auth.success"]
    assert translate("auth.success", locale="ru") == TRANSLATIONS["ru"]["auth.success"]


def test_translate_falls_back_to_default_locale(monkeypatch):
    monkeypatch.setitem(TRANSLATIONS, "es", {"auth.success": "Autenticación exitosa."})
    from app.localization import translator

    monkeypatch.setattr(translator.SETTINGS, "default_locale", "es")
    monkeypatch.setattr(translator.SETTINGS, "supported_locales", ["es", "en", "ru"])
    assert translate("auth.success", locale="de") == "Autenticación exitosa."
