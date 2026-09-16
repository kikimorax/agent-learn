"""P1 OpenAI client creation; settings are shared through agent_common."""

from agent_common.llm_config import LLMSettings
from openai import DefaultHttpxClient, OpenAI


def create_client(settings: LLMSettings | None = None) -> OpenAI:
    if settings is None:
        settings = LLMSettings.from_environment()
    # The SDK requires a non-empty key even if the local gateway needs no auth.
    return OpenAI(
        api_key=settings.api_key or "local-proxy",
        base_url=settings.base_url,
        http_client=DefaultHttpxClient(trust_env=not settings.local_gateway),
    )
