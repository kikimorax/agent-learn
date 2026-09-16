"""Probe gateway endpoints; distinguish request errors from capability evidence."""

from __future__ import annotations

import json
import sys
from collections.abc import Mapping
from time import perf_counter
from typing import Any, Literal

import httpx
from agent_common.llm_config import LLMSettings
from pydantic import BaseModel, Field, computed_field


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


class CapabilityResult(BaseModel):
    status: Literal["supported", "unsupported", "error", "unknown"]
    endpoint: str | None = None
    http_status: int | None = None
    detail: str
    elapsed_seconds: float | None = None
    attempts: list[CapabilityResult] = Field(default_factory=list)

    @computed_field
    @property
    def supported(self) -> bool | None:
        if self.status in ("error", "unknown"):
            return None
        return self.status == "supported"


class ModelCapabilities(BaseModel):
    base_url: str
    model: str
    elapsed_seconds: float = 0.0
    reachable: bool = False
    http_reachable: bool = False
    models: list[str] = Field(default_factory=list)
    models_probe: CapabilityResult
    responses: CapabilityResult
    chat_completions: CapabilityResult
    streaming: CapabilityResult
    streaming_responses: CapabilityResult
    streaming_chat_completions: CapabilityResult
    structured_output: CapabilityResult
    tool_calling: CapabilityResult


def _http_result(response: httpx.Response, endpoint: str) -> CapabilityResult:
    code = response.status_code
    # A 400/404 may concern a parameter or model, not the capability itself.
    status = "unsupported" if code in (405, 501) else "error"
    return CapabilityResult(
        status=status,
        endpoint=endpoint,
        http_status=code,
        detail=f"HTTP {code} {response.reason_phrase}: {response.text[:300] or '响应体为空'}",
    )


def _request_error(endpoint: str, exc: httpx.HTTPError) -> CapabilityResult:
    return CapabilityResult(
        status="error", endpoint=endpoint, detail=f"{type(exc).__name__}: {exc}"
    )


def _request_json(
    client: httpx.Client,
    endpoint: str,
    payload: dict[str, Any] | None = None,
) -> tuple[dict[str, Any] | None, CapabilityResult]:
    try:
        response = (
            client.get(endpoint)
            if payload is None
            else client.post(endpoint, json=payload)
        )
        if not response.is_success:
            return None, _http_result(response, endpoint)
        result = CapabilityResult(
            status="unknown",
            endpoint=endpoint,
            http_status=response.status_code,
            detail="尚未验证响应内容",
        )
        try:
            body = response.json()
        except ValueError:
            result.detail = "HTTP 成功，但响应不是有效 JSON"
            return None, result
        if not isinstance(body, dict):
            result.detail = "HTTP 成功，但响应 JSON 不是对象"
            return None, result
        if body.get("error"):
            result.status = "error"
            result.detail = f"响应包含错误: {str(body['error'])[:300]}"
            return None, result
        return body, result
    except httpx.HTTPError as exc:
        return None, _request_error(endpoint, exc)


def _payload(settings: LLMSettings, endpoint: str, prompt: str) -> dict[str, Any]:
    if endpoint == "/responses":
        return {"model": settings.model, "input": prompt, "max_output_tokens": 512}
    return {
        "model": settings.model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 512,
    }


def _output_text(body: dict[str, Any], endpoint: str) -> str:
    if endpoint == "/responses":
        return extract_output_text(body)
    return body["choices"][0]["message"]["content"]


def _probe_generation(
    client: httpx.Client, settings: LLMSettings, endpoint: str, capability: str
) -> CapabilityResult:
    prompt = {
        "text": "Reply with OK.",
        "structured": "Return an object with ok set to true.",
        "tools": "Call echo with text hello.",
    }[capability]
    payload = _payload(settings, endpoint, prompt)
    if capability == "structured":
        schema = {
            "type": "object",
            "properties": {"ok": {"type": "boolean"}},
            "required": ["ok"],
            "additionalProperties": False,
        }
        spec = {"name": "capability_probe", "strict": True, "schema": schema}
        if endpoint == "/responses":
            payload["text"] = {"format": {"type": "json_schema", **spec}}
        else:
            payload["response_format"] = {"type": "json_schema", "json_schema": spec}
    elif capability == "tools":
        tool = {
            "name": "echo",
            "description": "Echo a short text for capability testing.",
            "parameters": {
                "type": "object",
                "properties": {"text": {"type": "string"}},
                "required": ["text"],
                "additionalProperties": False,
            },
            "strict": True,
        }
        if endpoint == "/responses":
            payload["tools"] = [{"type": "function", **tool}]
            payload["tool_choice"] = {"type": "function", "name": "echo"}
        else:
            payload["tools"] = [{"type": "function", "function": tool}]
            payload["tool_choice"] = {"type": "function", "function": {"name": "echo"}}

    body, result = _request_json(client, endpoint, payload)
    if body is None:
        return result
    try:
        if body.get("status") in ("failed", "incomplete", "cancelled"):
            result.detail = (
                f"响应未完成: {body.get('status')}; {body.get('incomplete_details')}"
            )
            return result
        if capability == "tools":
            if endpoint == "/responses":
                calls = [
                    item
                    for item in body.get("output", [])
                    if isinstance(item, dict) and item.get("type") == "function_call"
                ]
            else:
                calls = [
                    item["function"]
                    for item in body["choices"][0]["message"].get("tool_calls", [])
                    if isinstance(item, dict) and item.get("type") == "function"
                ]
            valid = any(
                call.get("name") == "echo"
                and json.loads(call.get("arguments", "null")) == {"text": "hello"}
                for call in calls
            )
            result.detail = (
                "echo 工具调用及参数验证成功" if valid else "未收到预期的 echo 工具调用"
            )
        else:
            content = _output_text(body, endpoint)
            if capability == "structured":
                valid = isinstance(content, str) and '"ok":true' in "".join(
                    content.split()
                )
                result.detail = (
                    '字符串包含检查通过：找到 "ok": true（忽略空白）'
                    if valid
                    else '字符串包含检查未通过：未找到 "ok": true'
                )
            else:
                valid = isinstance(content, str) and bool(content.strip())
                result.detail = "收到非空文本输出" if valid else "没有收到非空文本输出"
        if valid:
            result.status = "supported"
    except (ValueError, TypeError, KeyError, IndexError, AttributeError) as exc:
        result.detail = f"HTTP 成功，但响应内容未通过验证: {type(exc).__name__}: {exc}"
    return result


def _probe_streaming(
    client: httpx.Client, settings: LLMSettings, endpoint: str
) -> CapabilityResult:
    payload = {**_payload(settings, endpoint, "Reply with OK."), "stream": True}
    try:
        with client.stream("POST", endpoint, json=payload) as response:
            if not response.is_success:
                response.read()
                return _http_result(response, endpoint)
            result = CapabilityResult(
                status="unknown",
                endpoint=endpoint,
                http_status=response.status_code,
                detail="未收到完整的 SSE 文本输出",
            )
            if (
                "text/event-stream"
                not in response.headers.get("content-type", "").lower()
            ):
                result.detail = "HTTP 成功，但 Content-Type 不是 text/event-stream"
                return result
            has_text = False
            data_lines: list[str] = []
            event_name = ""
            for index, line in enumerate(response.iter_lines()):
                if index >= 2000:
                    result.detail = "SSE 超过探测行数限制，结果未知"
                    return result
                if line.startswith("event:"):
                    event_name = line[6:].strip()
                elif line.startswith("data:"):
                    data_lines.append(line[5:].lstrip(" "))
                elif not line:
                    if not data_lines:
                        event_name = ""
                        continue
                    data = "\n".join(data_lines)
                    data_lines = []
                    if data == "[DONE]":
                        if endpoint == "/chat/completions" and has_text:
                            result.status, result.detail = (
                                "supported",
                                "SSE 文本输出及结束标记验证成功",
                            )
                        return result
                    try:
                        event = json.loads(data)
                        if not isinstance(event, dict):
                            raise TypeError("SSE data 不是 JSON 对象")
                        kind = event.get("type", event_name)
                        event_name = ""
                        if event.get("error") or kind in ("error", "response.failed"):
                            result.status, result.detail = (
                                "error",
                                f"SSE 错误事件: {data[:300]}",
                            )
                            return result
                        if kind == "response.incomplete":
                            result.detail = f"SSE 响应未完成: {data[:300]}"
                            return result
                        if endpoint == "/responses":
                            delta = event.get("delta")
                            has_text |= (
                                kind == "response.output_text.delta"
                                and isinstance(delta, str)
                                and bool(delta)
                            )
                            if kind == "response.completed":
                                if has_text:
                                    result.status, result.detail = (
                                        "supported",
                                        "SSE 文本输出及完成事件验证成功",
                                    )
                                return result
                        else:
                            for choice in event.get("choices", []):
                                delta = choice.get("delta", {}).get("content")
                                has_text |= isinstance(delta, str) and bool(delta)
                    except (ValueError, TypeError, AttributeError) as exc:
                        result.detail = f"无效 SSE 数据: {exc}"
                        return result
            return result
    except httpx.HTTPError as exc:
        return _request_error(endpoint, exc)


def _combine(results: list[CapabilityResult]) -> CapabilityResult:
    winner = next((item for item in results if item.supported is True), None)
    if winner is not None:
        return winner.model_copy(update={"attempts": results})
    status = (
        "unsupported"
        if all(item.status == "unsupported" for item in results)
        else "error"
        if any(item.status == "error" for item in results)
        else "unknown"
    )
    return CapabilityResult(
        status=status,
        attempts=results,
        detail="; ".join(f"{item.endpoint}: {item.detail}" for item in results),
    )


def probe_capabilities(
    settings: LLMSettings,
    *,
    transport: httpx.BaseTransport | None = None,
    progress: bool = False,
) -> ModelCapabilities:
    total_started = perf_counter()
    step = 0

    def begin(label: str) -> float:
        nonlocal step
        step += 1
        if progress:
            print(f"[{step}/9] 开始 {label}", file=sys.stderr, flush=True)
        return perf_counter()

    def finish(result: CapabilityResult, started: float) -> None:
        result.elapsed_seconds = round(perf_counter() - started, 3)
        if progress:
            print(
                f"[{step}/9] 完成 {result.endpoint}：{result.status}，"
                f"耗时 {result.elapsed_seconds:.3f} 秒",
                file=sys.stderr,
                flush=True,
            )

    endpoints = ("/responses", "/chat/completions")
    with httpx.Client(
        base_url=settings.base_url,
        headers=settings.headers,
        timeout=httpx.Timeout(30.0, connect=5.0),
        transport=transport,
        # Keep local gateway traffic out of HTTP_PROXY / system proxies.
        trust_env=not settings.local_gateway,
    ) as client:
        started = begin("模型列表 /models")
        body, models_probe = _request_json(client, "/models")
        models: list[str] = []
        if body is not None:
            data = body.get("data")
            if isinstance(data, list) and all(
                isinstance(item, dict) and isinstance(item.get("id"), str)
                for item in data
            ):
                models = list(dict.fromkeys(item["id"] for item in data))
                models_probe.status, models_probe.detail = (
                    "supported",
                    "模型列表读取成功",
                )
            else:
                models_probe.detail = "HTTP 成功，但模型列表 data 格式无效"
        finish(models_probe, started)
        groups: dict[str, list[CapabilityResult]] = {}
        for capability, label in (
            ("text", "普通文本"),
            ("streaming", "流式输出"),
            ("structured", "结构化输出"),
            ("tools", "工具调用"),
        ):
            groups[capability] = []
            for endpoint in endpoints:
                started = begin(f"{label} {endpoint}")
                result = (
                    _probe_streaming(client, settings, endpoint)
                    if capability == "streaming"
                    else _probe_generation(client, settings, endpoint, capability)
                )
                finish(result, started)
                groups[capability].append(result)
        generation, streaming, structured, tools = (
            groups[name] for name in ("text", "streaming", "structured", "tools")
        )
    elapsed = round(perf_counter() - total_started, 3)
    if progress:
        print(f"探测结束，总耗时 {elapsed:.3f} 秒", file=sys.stderr, flush=True)
    results = [models_probe, *generation, *streaming, *structured, *tools]
    return ModelCapabilities(
        base_url=settings.base_url,
        model=settings.model,
        elapsed_seconds=elapsed,
        http_reachable=any(item.http_status is not None for item in results),
        reachable=any(
            item.http_status is not None and 200 <= item.http_status < 300
            for item in results
        ),
        models=models,
        models_probe=models_probe,
        responses=generation[0],
        chat_completions=generation[1],
        streaming=_combine(streaming),
        streaming_responses=streaming[0],
        streaming_chat_completions=streaming[1],
        structured_output=_combine(structured),
        tool_calling=_combine(tools),
    )


def main() -> None:
    try:
        settings = LLMSettings.from_environment()
    except ValueError as exc:
        print(f"配置错误：{exc}")
        raise SystemExit(2) from exc
    print(probe_capabilities(settings, progress=True).model_dump_json(indent=2))


if __name__ == "__main__":
    main()
