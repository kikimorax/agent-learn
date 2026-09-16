"""Phase 0: a minimal multi-turn CLI using the Responses API."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import httpx
from agent_common.llm_config import LLMSettings

SYSTEM_PROMPT = "你是一个可靠、简洁的人工智能助手。"


def extract_output_text(body: Mapping[str, Any]) -> str:
    """Extract text without assuming the first output item is a message."""
    direct_text = body.get("output_text")
    if isinstance(direct_text, str) and direct_text:
        return direct_text

    text_parts: list[str] = []
    output = body.get("output", [])
    if not isinstance(output, list):
        raise TypeError("响应中的 output 不是列表")

    for item in output:
        if not isinstance(item, Mapping) or item.get("type") != "message":
            continue
        content = item.get("content", [])
        if not isinstance(content, list):
            continue
        for part in content:
            if (
                isinstance(part, Mapping)
                and part.get("type") == "output_text"
                and isinstance(part.get("text"), str)
            ):
                text_parts.append(part["text"])

    if not text_parts:
        raise ValueError("响应中没有可显示的 output_text")
    return "".join(text_parts)


def chat_with_openai(
    messages: list[dict[str, str]],
    settings: LLMSettings,
    *,
    transport: httpx.BaseTransport | None = None,
) -> str:
    payload = {
        "model": settings.model,
        "instructions": SYSTEM_PROMPT,
        "input": messages,
    }
    with httpx.Client(
        base_url=settings.base_url,
        headers=settings.headers,
        timeout=30.0,
        transport=transport,
        trust_env=not settings.local_gateway,
    ) as client:
        response = client.post("/responses", json=payload)
        response.raise_for_status()
        return extract_output_text(response.json())


def chat_cli() -> None:
    try:
        settings = LLMSettings.from_environment()
    except ValueError as exc:
        print(f"配置错误：{exc}")
        return

    print("欢迎使用本地模型 CLI！输入 exit 退出。")
    messages: list[dict[str, str]] = []

    while True:
        user_input = input("你: ").strip()
        if user_input.lower() == "exit":
            print("再见！")
            return
        if not user_input:
            print("助手: 请输入非空内容。\n")
            continue

        messages.append({"role": "user", "content": user_input})
        try:
            answer = chat_with_openai(messages, settings)
        except httpx.TimeoutException:
            print("助手: 请求超时，请检查本地代理或稍后重试。\n")
            messages.pop()
            continue
        except httpx.HTTPStatusError as exc:
            print(f"助手: 代理返回 HTTP {exc.response.status_code}。\n")
            messages.pop()
            continue
        except (httpx.RequestError, TypeError, ValueError) as exc:
            print(f"助手: 调用失败：{exc}\n")
            messages.pop()
            continue

        messages.append({"role": "assistant", "content": answer})
        print(f"助手: {answer}\n")


if __name__ == "__main__":
    chat_cli()
