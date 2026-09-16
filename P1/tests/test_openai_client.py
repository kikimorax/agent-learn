import importlib
import runpy
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from agent_common.llm_config import LLMSettings


def test_import_does_not_read_settings(monkeypatch):
    def unexpected_read(*args, **kwargs):
        raise AssertionError("Configuration must not be read during import")

    monkeypatch.setattr(LLMSettings, "from_environment", unexpected_read)
    module = importlib.import_module("openai_client")
    importlib.reload(module)
    for script in (Path(__file__).resolve().parents[1] / "examples").glob(
        "gpt_prompt_eng_*.py"
    ):
        runpy.run_path(str(script))


def test_client_uses_shared_settings():
    from openai_client import create_client

    with create_client(LLMSettings("http://proxy.example/v1", "test")) as client:
        assert str(client.base_url) == "http://proxy.example/v1/"
        assert client.api_key == "local-proxy"
    with create_client(LLMSettings("http://proxy.example/v1", "test", "key")) as client:
        assert client.api_key == "key"


def test_client_reads_settings_on_call(monkeypatch):
    from openai_client import create_client

    expected = LLMSettings("http://proxy.example/v1", "test")
    monkeypatch.setattr(LLMSettings, "from_environment", lambda: expected)
    with create_client() as client:
        assert str(client.base_url) == "http://proxy.example/v1/"


@pytest.mark.parametrize(
    "base_url, trust_env",
    [
        ("http://127.0.0.1:3030/v1", False),
        ("http://localhost:3030/v1", False),
        ("http://[::1]:3030/v1", False),
        ("http://proxy.example/v1", True),
    ],
)
def test_client_proxy_policy(base_url, trust_env):
    from openai_client import create_client

    with create_client(LLMSettings(base_url, "test")) as client:
        assert client._client.trust_env is trust_env


@pytest.mark.parametrize(
    "script",
    sorted(
        (Path(__file__).resolve().parents[1] / "examples").glob("gpt_prompt_eng_*.py")
    ),
    ids=lambda path: path.stem,
)
def test_completion_uses_configured_model_and_closes_client(script, monkeypatch):
    import openai_client

    expected = LLMSettings("http://proxy.example/v1", "configured-model")
    monkeypatch.setattr(LLMSettings, "from_environment", lambda: expected)
    context = MagicMock()
    client = context.__enter__.return_value
    client.chat.completions.create.return_value.choices[0].message.content = "answer"
    factory = MagicMock(return_value=context)
    monkeypatch.setattr(openai_client, "create_client", factory)
    namespace = runpy.run_path(str(script))
    assert namespace["get_completion"]("hello") == "answer"
    factory.assert_called_once_with(expected)
    assert (
        client.chat.completions.create.call_args.kwargs["model"] == "configured-model"
    )
    context.__exit__.assert_called_once()
    namespace["get_completion"]("hello", model="override")
    assert client.chat.completions.create.call_args.kwargs["model"] == "override"
