from app.core.config import get_settings


def test_settings_loaded():
    settings = get_settings()
    assert settings.OPENAI_API_KEY == "test-key"
    assert settings.OPENAI_MODEL == "gpt-4.1-nano"
    assert "sqlite" in settings.DATABASE_URL


def test_langfuse_enabled_property():
    settings = get_settings()
    # langfuse_enabled should be True only when both keys are non-empty
    expected = bool(settings.LANGFUSE_PUBLIC_KEY and settings.LANGFUSE_SECRET_KEY)
    assert settings.langfuse_enabled is expected


def test_cors_origins_parsing():
    settings = get_settings()
    origins = settings.cors_origin_list
    assert isinstance(origins, list)
    assert len(origins) >= 1
