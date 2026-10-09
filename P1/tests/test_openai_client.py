import importlib
import runpy
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from agent_common.llm_config import LLMSettings
from openai.types.chat import ChatCompletion


def test_import_does_not_read_settings(monkeypatch):
    def unexpected_read(*args, **kwargs):
        raise AssertionError("Configuration must not be read during import")

    monkeypatch.setattr(LLMSettings, "from_environment", unexpected_read)
    module = importlib.import_module("openai_client")
    importlib.reload(module)
    for script in (Path(__file__).resolve().parents[1] / "examples" / "prompts").glob(
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
        (Path(__file__).resolve().parents[1] / "examples" / "prompts").glob("gpt_prompt_eng_*.py")
    ) + [Path(__file__).resolve().parents[1] / "examples" / "scratch_p1_01.py"],
    ids=lambda path: path.stem,
)
@pytest.mark.parametrize("content", ["answer", None])
def test_completion_text_uses_configured_model_and_closes_client(script, content, monkeypatch):
    import openai_client

    expected = LLMSettings("http://proxy.example/v1", "configured-model")
    monkeypatch.setattr(LLMSettings, "from_environment", lambda: expected)
    context = MagicMock()
    client = context.__enter__.return_value
    client.chat.completions.create.return_value.choices[0].message.content = content
    factory = MagicMock(return_value=context)
    monkeypatch.setattr(openai_client, "create_client", factory)
    namespace = runpy.run_path(str(script))
    assert namespace["get_completion_text"]("hello") == content
    factory.assert_called_once_with(expected)
    assert (
        client.chat.completions.create.call_args.kwargs["model"] == "configured-model"
    )
    context.__exit__.assert_called_once()
    namespace["get_completion_text"]("hello", model="override", temperature=0.7)
    assert client.chat.completions.create.call_args.kwargs["model"] == "override"
    assert client.chat.completions.create.call_args.kwargs["temperature"] == 0.7


@pytest.mark.parametrize(
    "prompt",
    [
        "hello",
        [
            {"role": "user", "content": "The codename is Qinghe."},
            {"role": "assistant", "content": "Understood."},
            {"role": "user", "content": "What is the codename?"},
        ],
    ],
)
def test_completion_returns_all_choices_and_preserves_messages(prompt, monkeypatch):
    import openai_client

    settings = LLMSettings("http://proxy.example/v1", "configured-model")
    monkeypatch.setattr(LLMSettings, "from_environment", lambda: settings)
    context = MagicMock()
    client = context.__enter__.return_value
    client.chat.completions.create.return_value = ChatCompletion.model_validate({
        "id": "chatcmpl-test",
        "object": "chat.completion",
        "created": 0,
        "model": "override",
        "choices": [
            {
                "index": 0,
                "finish_reason": "stop",
                "message": {"role": "assistant", "content": "answer"},
            },
            {
                "index": 1,
                "finish_reason": "tool_calls",
                "message": {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [{
                        "id": "call-test",
                        "type": "function",
                        "function": {"name": "lookup_project", "arguments": "{}"},
                    }],
                },
            },
        ],
    })
    monkeypatch.setattr(openai_client, "create_client", lambda settings: context)

    choices = openai_client.get_completion(prompt, model="override", temperature=0.7)

    assert isinstance(choices, list)
    assert len(choices) == 2
    assert choices[0].index == 0
    assert choices[0].message.content == "answer"
    assert choices[0].finish_reason == "stop"
    assert choices[1].index == 1
    assert choices[1].message.content is None
    assert choices[1].finish_reason == "tool_calls"
    assert choices[1].message.tool_calls[0].function.name == "lookup_project"
    assert choices[1].message.tool_calls[0].function.arguments == "{}"
    client.chat.completions.create.assert_called_once_with(
        model="override",
        messages=[{"role": "user", "content": "hello"}] if isinstance(prompt, str) else prompt,
        temperature=0.7,
    )
    context.__exit__.assert_called_once()
