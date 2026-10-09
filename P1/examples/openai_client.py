"""P1 OpenAI client creation; settings are shared through agent_common."""

from agent_common.llm_config import LLMSettings
from openai import DefaultHttpxClient, OpenAI
from openai.types.chat import ChatCompletionMessageParam
from openai.types.chat.chat_completion import Choice


def create_client(settings: LLMSettings | None = None) -> OpenAI:
    if settings is None:
        settings = LLMSettings.from_environment()
    # The SDK requires a non-empty key even if the local gateway needs no auth.
    return OpenAI(
        api_key=settings.api_key or "local-proxy",
        base_url=settings.base_url,
        http_client=DefaultHttpxClient(trust_env=not settings.local_gateway),
    )


def get_completion(
    prompt: str | list[ChatCompletionMessageParam], model: str | None = None, temperature: float = 0
) -> list[Choice]:
    """Return all choices, including each message and its finish reason."""
    messages: list[ChatCompletionMessageParam] = (
        prompt if isinstance(prompt, list) else [{"role": "user", "content": prompt}]
    )
    settings = LLMSettings.from_environment()
    with create_client(settings) as client:
        response = client.chat.completions.create(
            model=model or settings.model,
            messages=messages,
            temperature=temperature,
        )
    return response.choices


def get_completion_text(
    prompt: str | list[ChatCompletionMessageParam], model: str | None = None, temperature: float = 0
) -> str | None:
    """Return the first choice's text, or None when it has no text content."""
    choices = get_completion(prompt, model=model, temperature=temperature)
    return choices[0].message.content
