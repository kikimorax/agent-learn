import pytest

from agent_common.llm_config import LLMSettings


def test_settings_require_base_url_and_model(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("LLM_BASE_URL", raising=False)
    monkeypatch.delenv("LLM_MODEL", raising=False)

    with pytest.raises(ValueError, match="LLM_BASE_URL, LLM_MODEL"):
        LLMSettings.from_environment(env_file=None)


def test_settings_read_optional_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_BASE_URL", "http://proxy.example/v1/")
    monkeypatch.setenv("LLM_MODEL", "test-model")
    monkeypatch.setenv("LLM_API_KEY", "secret")

    settings = LLMSettings.from_environment()

    assert settings.base_url == "http://proxy.example/v1"
    assert settings.model == "test-model"
    assert settings.headers["Authorization"] == "Bearer secret"
