from pathlib import Path

import pytest

from agent_common.llm_config import LLMSettings


@pytest.mark.parametrize(
    "base_url, expected",
    [
        ("http://127.0.0.1:3030/v1", True),
        ("http://localhost:3030/v1", True),
        ("http://LOCALHOST:3030/v1", True),
        ("http://[::1]:3030/v1", True),
        ("https://gateway.example/v1", False),
        ("http://localhost.example/v1", False),
    ],
)
def test_local_gateway_detection(base_url, expected):
    assert LLMSettings(base_url, "test-model").local_gateway is expected


@pytest.fixture(autouse=True)
def clear_llm_environment(monkeypatch):
    for name in ("LLM_BASE_URL", "LLM_MODEL", "LLM_API_KEY"):
        monkeypatch.delenv(name, raising=False)


def test_dotenv_and_environment_precedence(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text(
        'LLM_BASE_URL="http://proxy.example/v1/"\n'
        'LLM_MODEL=file-model\nLLM_API_KEY=file-key\n', encoding="utf-8"
    )
    monkeypatch.setenv("LLM_MODEL", "terminal-model")
    settings = LLMSettings.from_environment(env_file=env_file)
    assert settings.base_url == "http://proxy.example/v1"
    assert settings.model == "terminal-model"
    assert settings.headers["Authorization"] == "Bearer file-key"


def test_configuration_is_read_again_on_each_call(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("LLM_BASE_URL=http://proxy.example/v1\nLLM_MODEL=first\n")
    assert LLMSettings.from_environment(env_file=env_file).model == "first"
    env_file.write_text("LLM_BASE_URL=http://proxy.example/v1\nLLM_MODEL=second\n")
    assert LLMSettings.from_environment(env_file=env_file).model == "second"


def test_missing_file_reports_missing_configuration(tmp_path):
    with pytest.raises(ValueError, match="LLM_BASE_URL, LLM_MODEL"):
        LLMSettings.from_environment(env_file=tmp_path / "missing.env")


def test_default_file_is_independent_of_working_directory(tmp_path, monkeypatch):
    import agent_common.llm_config as config

    expected = Path(__file__).resolve().parents[1] / ".env"
    calls = []

    def fake_dotenv(path, **kwargs):
        calls.append(path)
        return {"LLM_BASE_URL": "http://proxy.example/v1", "LLM_MODEL": "test"}

    monkeypatch.setattr(config, "dotenv_values", fake_dotenv)
    monkeypatch.chdir(tmp_path)
    LLMSettings.from_environment()
    assert calls == [expected]


def test_empty_environment_value_overrides_dotenv(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text("LLM_BASE_URL=http://proxy.example/v1\nLLM_MODEL=test\n")
    monkeypatch.setenv("LLM_MODEL", " ")
    with pytest.raises(ValueError, match="LLM_MODEL"):
        LLMSettings.from_environment(env_file=env_file)


def test_optional_key_has_no_authorization_header(monkeypatch):
    monkeypatch.setenv("LLM_BASE_URL", "http://proxy.example/v1")
    monkeypatch.setenv("LLM_MODEL", "test")
    settings = LLMSettings.from_environment(env_file=None)
    assert settings.api_key is None
    assert "Authorization" not in settings.headers
