# 阶段项目

**学习优先级：** [必做 → 巩固 → 进阶](../../docs/课程大纲.md#学习优先级)。先完成课次“必做”及阶段验收；巩固按薄弱点补练，进阶不阻塞进度。每阶段维护一份实验记录，后续项目与报告复用已有成果。

已有 [openai_chat_demo.py](openai_chat_demo.py)。在仓库根目录运行 `uv run --project P0 python P0/project/openai_chat_demo.py`；连接需要公共配置和本地模型代理。

## 项目增量

| 项目 | 约定 |
|---|---|
| 承接 | 基础 Python 与命令行；不依赖前一阶段项目。 |
| 新增 | 统一配置、模型 HTTP 调用、错误分类、多轮 CLI 和能力报告。 |
| 典型输入 | CLI 第一轮输入“我叫小林”，第二轮问“我叫什么”；能力探针读取实际代理配置。 |
| 预期行为 | CLI 能利用历史回复；探针逐项给出证据、错误或未知状态，不将 HTTP 可达等同于模型可用。 |
| 失败处理 | 缺配置时说明缺少变量；连接失败或超时时给出错误；非文本项和非法响应不会被误当答案。 |
| 交付证据 | 可运行 CLI、能力报告、配置/错误测试及排错记录。 |

详细步骤及验收见 [P0 课程](../../docs/P0.md)。完成必做实验后再在本目录集成，不在每阶段重新实现上一阶段全部代码。


交付可配置、可测试的本地模型 CLI，以及一次真实的 `ModelCapabilities` 探测报告。

## 历史能力报告（保留原记录）

以下是此前一次运行的结果，不代表当前代理状态，也不代表严格 Schema 校验通过。实际能力需用当前配置重新探测。

```json
{
  "base_url": "http://127.0.0.1:3030/v1",
  "model": "gpt-5.4",
  "reachable": true,
  "http_reachable": true,
  "models": [
    "claude-sonnet-5",
    "gemini-3.5-flash",
    "gemini-3.6-flash",
    "gemini-3.7-flash",
    "gemini-3.8-flash",
    "gpt-5.3-codex",
    "gpt-5.4-mini",
    "gpt-5.4",
    "gpt-5.6-luna",
    "gpt-5.6-terra",
    "grok-4.5",
    "grok-4.6",
    "kimi-k2.7-code",
    "kimi-k3",
    "mai-code-1.1-flash",
    "gpt-5-mini",
    "gpt-4o-mini",
    "claude-haiku-4.5",
    "auto",
    "copilot-utility-small",
    "copilot-utility",
    "copilot-dictation-cleanup-luna",
    "copilot-claude-sonnet-5",
    "copilot-gemini-3.5-flash",
    "copilot-gemini-3.6-flash",
    "copilot-gemini-3.7-flash",
    "copilot-gemini-3.8-flash",
    "copilot-gpt-5.3-codex",
    "copilot-gpt-5.4-mini",
    "copilot-gpt-5.4",
    "copilot-gpt-5.6-luna",
    "copilot-gpt-5.6-terra",
    "copilot-grok-4.5",
    "copilot-grok-4.6",
    "copilot-kimi-k2.7-code",
    "copilot-kimi-k3",
    "copilot-oswe-vscode-modeld",
    "copilot-gpt-5-mini",
    "copilot-gpt-4o-mini",
    "copilot-claude-haiku-4.5",
    "copilot-mai-code-1.1-flash"
  ],
  "models_probe": {
    "status": "supported",
    "endpoint": "/models",
    "http_status": 200,
    "detail": "模型列表读取成功",
    "attempts": [],
    "supported": true
  },
  "responses": {
    "status": "supported",
    "endpoint": "/responses",
    "http_status": 200,
    "detail": "收到非空文本输出",
    "attempts": [],
    "supported": true
  },
  "chat_completions": {
    "status": "error",
    "endpoint": "/chat/completions",
    "http_status": 502,
    "detail": "HTTP 502 Bad Gateway: {\"error\":{\"message\":\"Failed to retrieve Copilot response: Please check your firewall rules and network connection then try again. Error Code: net::ERR_CONNECTION_CLOSED. \",\"type\":\"bad_gateway\",\"code\":\"command_failed\",\"param\":null}}",
    "attempts": [],
    "supported": null
  },
  "streaming": {
    "status": "supported",
    "endpoint": "/chat/completions",
    "http_status": 200,
    "detail": "SSE 文本输出及结束标记验证成功",
    "attempts": [
      {
        "status": "error",
        "endpoint": "/responses",
        "http_status": 200,
        "detail": "SSE 错误事件: {\"type\":\"error\",\"error\":{\"type\":\"api_error\",\"message\":\"Please check your firewall rules and network connection then try again. Error Code: net::ERR_CONNECTION_CLOSED.\"}}",
        "attempts": [],
        "supported": null
      },
      {
        "status": "supported",
        "endpoint": "/chat/completions",
        "http_status": 200,
        "detail": "SSE 文本输出及结束标记验证成功",
        "attempts": [],
        "supported": true
      }
    ],
    "supported": true
  },
  "streaming_responses": {
    "status": "error",
    "endpoint": "/responses",
    "http_status": 200,
    "detail": "SSE 错误事件: {\"type\":\"error\",\"error\":{\"type\":\"api_error\",\"message\":\"Please check your firewall rules and network connection then try again. Error Code: net::ERR_CONNECTION_CLOSED.\"}}",
    "attempts": [],
    "supported": null
  },
  "streaming_chat_completions": {
    "status": "supported",
    "endpoint": "/chat/completions",
    "http_status": 200,
    "detail": "SSE 文本输出及结束标记验证成功",
    "attempts": [],
    "supported": true
  },
  "structured_output": {
    "status": "supported",
    "endpoint": "/responses",
    "http_status": 200,
    "detail": "字符串包含检查通过：找到 \"ok\": true（忽略空白）",
    "attempts": [
      {
        "status": "supported",
        "endpoint": "/responses",
        "http_status": 200,
        "detail": "字符串包含检查通过：找到 \"ok\": true（忽略空白）",
        "attempts": [],
        "supported": true
      },
      {
        "status": "unknown",
        "endpoint": "/chat/completions",
        "http_status": 200,
        "detail": "字符串包含检查未通过：未找到 \"ok\": true",
        "attempts": [],
        "supported": null
      }
    ],
    "supported": true
  },
  "tool_calling": {
    "status": "supported",
    "endpoint": "/chat/completions",
    "http_status": 200,
    "detail": "echo 工具调用及参数验证成功",
    "attempts": [
      {
        "status": "unknown",
        "endpoint": "/responses",
        "http_status": 200,
        "detail": "未收到预期的 echo 工具调用",
        "attempts": [],
        "supported": null
      },
      {
        "status": "supported",
        "endpoint": "/chat/completions",
        "http_status": 200,
        "detail": "echo 工具调用及参数验证成功",
        "attempts": [],
        "supported": true
      }
    ],
    "supported": true
  }
}
```
