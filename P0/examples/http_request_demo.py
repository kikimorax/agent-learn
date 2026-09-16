# 练习题1： 用 `httpx` 顺序请求 3 个不同的 URL，打印响应状态码、返回长度和耗时；再用 `asyncio` 做一个并发版本并对比耗时。

# 这里使用httpx库：
# httpx 由 Encode 团队开发，于 2019 年首次发布，目标是提供一个现代化的 HTTP 客户端，支持同步和异步操作，并兼容 HTTP/1.1 和 HTTP/2。
# 背景：
# requests 库虽然功能强大，但缺乏对异步和 HTTP/2 的原生支持。
# httpx 应运而生，弥补了 requests 的不足，同时保持了类似的 API 设计。
# 核心优势：
# 同步和异步双模式。
# 支持 HTTP/2。
# 类型提示完善，兼容 Python 3.6+。

import asyncio
import sys
import time

from contextlib import contextmanager

import httpx

@contextmanager
def timer():
    start = time.perf_counter()
    yield
    end = time.perf_counter()
    print(f"代码块耗时: {end - start:.6f} 秒")


def safe_json(response: httpx.Response, name: str):
    """Safely parse JSON response and print diagnostics when unavailable."""
    content_type = response.headers.get("content-type", "")
    if response.status_code >= 400:
        print(f"{name} 请求失败: status={response.status_code}")
        print(f"{name} 响应片段: {response.text[:120]!r}")
        return None
    if "json" not in content_type.lower():
        print(f"{name} 非 JSON 响应: content-type={content_type!r}")
        print(f"{name} 响应片段: {response.text[:120]!r}")
        return None
    try:
        return response.json()
    except ValueError as exc:
        print(f"{name} JSON 解析失败: {exc}")
        print(f"{name} 响应片段: {response.text[:120]!r}")
        return None


def safe_request(method: str, url: str, name: str, **kwargs):
    """Run a sync request and handle network errors gracefully."""
    try:
        return httpx.request(method, url, timeout=10.0, **kwargs)
    except httpx.RequestError as exc:
        print(f"{name} 请求异常: {exc}")
        return None


async def safe_request_async(client: httpx.AsyncClient, method: str, url: str, name: str, **kwargs):
    """Run an async request and handle network errors gracefully."""
    try:
        return await client.request(method, url, timeout=10.0, **kwargs)
    except httpx.RequestError as exc:
        print(f"{name} 请求异常: {exc}")
        return None


def fetch_synchronous():
    with timer():
        r = safe_request("GET", "https://httpbin.org/get", "GET /get")
        if r is not None:
            print(r.status_code)  # 200
            print(len(r.content))

        headers = {"User-Agent": "my-app/1.0"}
        r = safe_request("GET", "https://httpbin.org/headers", "GET /headers", headers=headers)
        if r is not None:
            payload = safe_json(r, "GET /headers")
            if payload:
                print(payload.get("headers", {}).get("User-Agent"))

        json_data = {"name": "httpx", "type": "client"}
        r = safe_request("POST", "https://httpbin.org/post", "POST /post", json=json_data)
        if r is not None:
            payload = safe_json(r, "POST /post")
            if payload:
                print(payload.get("json"))


async def fetch_async_sequential():
    async with httpx.AsyncClient() as client:
        with timer():
            r1 = await safe_request_async(client, "GET", "https://httpbin.org/get", "GET /get")
            if r1 is not None:
                print(r1.status_code)
                print(len(r1.content))

            headers = {"User-Agent": "my-app/1.0"}
            r2 = await safe_request_async(client, "GET", "https://httpbin.org/headers", "GET /headers", headers=headers)
            if r2 is not None:
                payload = safe_json(r2, "GET /headers")
                if payload:
                    print(payload.get("headers", {}).get("User-Agent"))

            json_data = {"name": "httpx", "type": "client"}
            r3 = await safe_request_async(client, "POST", "https://httpbin.org/post", "POST /post", json=json_data)
            if r3 is not None:
                payload = safe_json(r3, "POST /post")
                if payload:
                    print(payload.get("json"))


async def fetch_async_concurrent():
    async with httpx.AsyncClient() as client:
        with timer():
            headers = {"User-Agent": "my-app/1.0"}
            json_data = {"name": "httpx", "type": "client"}

            task1 = safe_request_async(client, "GET", "https://httpbin.org/get", "GET /get")
            task2 = safe_request_async(client, "GET", "https://httpbin.org/headers", "GET /headers", headers=headers)
            task3 = safe_request_async(client, "POST", "https://httpbin.org/post", "POST /post", json=json_data) # data=json_data 的话，httpx不会转json

            r1, r2, r3 = await asyncio.gather(task1, task2, task3)

            if r1 is not None:
                print(r1.status_code)
                print(len(r1.content))
            if r2 is not None:
                payload2 = safe_json(r2, "GET /headers")
                if payload2:
                    print(payload2.get("headers", {}).get("User-Agent"))
            if r3 is not None:
                payload3 = safe_json(r3, "POST /post")
                if payload3:
                    print(payload3.get("json"))


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] == "sync":
        print("正在执行同步版本...")
        fetch_synchronous()
    elif sys.argv[1] == "async":
        print("正在执行异步顺序版本...")
        asyncio.run(fetch_async_sequential())
    elif sys.argv[1] == "con":
        print("正在执行异步并发版本...")
        asyncio.run(fetch_async_concurrent())
