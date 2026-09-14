from devintel.modules.language import LanguageIntelligence


def test_understanding_is_deterministic_and_bounded():
    engine = LanguageIntelligence()
    result = engine.understand("  What can you build?  ")
    assert result.normalized_text == "What can you build?"
    assert "question" in result.intents
    assert "creation" in result.intents
    assert len(result.text_digest) == 64
    assert engine.understand("What can you build?").text_digest == result.text_digest


def test_high_impact_language_requires_confirmation():
    result = LanguageIntelligence().understand("Please transfer the money")
    assert "high_impact_action" in result.intents
    assert result.requires_confirmation is True


def test_language_hint_and_response_constraints():
    engine = LanguageIntelligence()
    result = engine.understand("Bawo padi mi")
    assert result.language_hint == "yo"
    constraints = engine.response_constraints(result, max_chars=512)
    assert constraints.language == "yo"
    assert constraints.preserve_uncertainty is True


def test_bounds_fail_closed():
    engine = LanguageIntelligence()
    try:
        engine.understand("x" * 16_385)
        raise AssertionError("expected bound failure")
    except ValueError:
        pass
    result = engine.understand("hello")
    try:
        engine.response_constraints(result, max_chars=64)
        raise AssertionError("expected constraint failure")
    except ValueError:
        pass
