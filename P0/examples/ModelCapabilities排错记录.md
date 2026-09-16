# ModelCapabilities 失败记录与处理方法

记录日期：2026-09-16。

本记录来自 P0 学习过程中的实际运行、截图和对照测试。历史结果只说明当次请求的情况，不代表服务当前状态；没有保存原始响应的请求，不用后续重试结果代替原文。

## 运行环境与入口

- 模型网关：`http://127.0.0.1:3030/v1`。
- 测试模型：`gpt-5.4`。
- 配置来源：`shared/.env` 和环境变量。
- 脚本现已移动到 `P0/examples/`。

在 `P0` 目录执行：

```powershell
uv run python examples/model_capabilities.py
```

探针分别检查模型列表，以及 Responses、Chat Completions 的普通文本、流式、结构化输出和工具调用，并非只测试流式。

## 1. 所有请求返回 502，却被报告为“不支持”

### 现象

旧报告中多个能力均为 `supported: false`，例如：

```json
{
  "supported": false,
  "endpoint": "/responses",
  "detail": "HTTP 502: "
}
```

同时出现 `reachable: true`、`models: []`。后来补全诊断后，确认有一次连 `GET /models` 都返回了 `502 Bad Gateway`，响应体为空。

### 原因与证据

这里有两个不同的问题：

1. **报告判定错误，已经确认。** 旧代码把 HTTP 异常统一转换成“不支持”；模型列表请求只要收到 HTTP 响应就设置 `reachable: true`，没有区分 200 和 502。
2. **502 的具体来源，未完全确认。** 可能是中间代理或本地网关的问题。没有对应时刻的服务日志，不能断言是模型不支持，也不能断言一定是环境代理。

后续绕过代理的检查成功：

```powershell
curl.exe --noproxy "*" -i http://127.0.0.1:3030/v1/models
```

用户截图显示 `HTTP/1.1 200 OK` 并返回模型列表。助手环境中默认 HTTPX 和 `trust_env=False` 的对照也都返回过 200，因此还需考虑终端环境差异或服务波动。

### 已实施的处理

- 增加 `status`、`http_status`、`models_probe` 和各接口的 `attempts`。
- `http_reachable` 表示收到过 HTTP 响应；`reachable` 表示至少一个请求返回了 2xx，不代表模型生成一定可用。
- 请求错误标为 `status: "error"`、`supported: null`，不再当成明确不支持。
- 普通请求返回 200 后还要检查是否有非空文本。
- 在公共配置中集中判断本机地址：

```python
@property
def local_gateway(self) -> bool:
    return urlsplit(self.base_url).hostname in ("127.0.0.1", "localhost", "::1")
```

探针和聊天示例创建客户端时统一使用：

```python
trust_env=not settings.local_gateway
```

这让本机请求直接连接，远程地址仍遵循环境设置；不会修改网关访问上游的代理配置。回归测试模拟了“代理返回 502、本机直连返回 200”的情况，修改后通过。它验证了绕过机制，但不能追溯证明历史 502 的来源。

如果修改后直连仍出现 502，需要按请求时间查看 3030 服务日志，而不是继续修改提示词。

## 2. 流式连接被强制关闭

### 现象

```text
ReadError: [WinError 10054] 远程主机强迫关闭了一个现有的连接。
```

该错误曾出现在 `/responses` 的流式测试中。

### 判断与处理

这是连接在读取过程中被对端重置，不能证明模型不支持流式。具体由哪个环节关闭连接，现有记录无法确定。

已将此类异常保留为 `error`，并分别测试两个接口的流式输出。流式校验读取实际 SSE 数据和完成事件，避免仅凭字符串中出现 `error` 就把普通回复判为失败。

后续一次实测中，两种接口的流式测试均成功；这说明它们当时可用，不代表连接重置的根因已查明。

## 3. 普通 Chat Completions 超时，但网页请求成功

### 现象

探针返回 `ReadTimeout: timed out`，但网页中的 `Hello!` 请求正常返回。

### 对照实验

使用相同模型、同一接口，临时把读取超时设为 90 秒，顺序执行：

| 请求 | HTTP 状态 | 当次耗时 |
|---|---|---|
| `Hello!`，不带 token 上限 | 200 | 6.19 秒 |
| `Hello!`，增加 `max_tokens: 512` | 200 | 10.08 秒 |
| `Reply with OK.`，`max_tokens: 512` | 200 | 33.58 秒 |

脚本原样请求能够成功，但这次等待时间超过了脚本的 30 秒读取超时。不能据此认定该提示词必然更慢，也不能用超时解释 HTTP 502。

### 处理状态

**90 秒仅用于当时的对照实验，当前探针仍是以下配置：**

```python
timeout=httpx.Timeout(30.0, connect=5.0)
```

如果需要容忍更慢的回复，可把读取超时提高到 90 秒；这是待选调整，不应记成已经完成。增大超时会增加失败时的等待时间，也不会解决网关返回的 502。

## 4. 结构化输出返回布尔值，导致整份报告崩溃

### 现象

旧代码执行：

```python
json.loads(content).get("ok")
```

实际出现：

```text
AttributeError: 'bool' object has no attribute 'get'
```

### 原因与处理

合法 JSON 不一定是对象，也可以是布尔值、数组或 `null`。这次解析结果是布尔值，所以没有 `.get()` 方法；当时没有保留原始文本，无法确认具体是 `true` 还是 `false`。

最初修复是先检查解析结果类型，并将异常响应记为 `unknown`，防止一项测试中断整个报告。随后按学习需求，结构化输出改为下面记录的字符串包含检查。

## 5. 回复中有正确内容，却出现 JSONDecodeError

### 现象

```text
HTTP 成功，但响应内容未通过验证:
JSONDecodeError: Expecting value: line 1 column 1 (char 0)
```

按相同结构化请求参数重试时，HTTP 返回 200，模型回复原文为：

````text
```json
{
  "ok": true
}
```
````

这是重试的原文，不能保证与之前未保存的响应完全相同。

### 原因

代码将整段模型文本传给 `json.loads()`。开头的 Markdown 反引号也是回复的一部分，不是合法 JSON，因此在解析阶段失败，尚未执行字段校验。

另外，本地网关的 OpenAPI 文档只声明了 Chat Completions 的 `text`、`json_object` 输出格式，没有声明 `json_schema`；Responses 请求结构也没有声明探针所用的 `text.format`。这提示兼容性需要验证，但文档缺项本身不能证明服务一定不支持。

### 当前处理方法

按用户要求，不再对结构化测试的模型文本做 JSON 解析，改为字符串包含检查：

```python
valid = (
    isinstance(content, str)
    and '"ok":true' in "".join(content.split())
)
```

忽略空格、换行和制表符后，只要包含 `"ok":true` 就通过。Markdown 代码块、说明文字和额外字段不会阻止通过。

**该结果只证明出现了预期文本，不证明回复是合法 JSON，也不证明严格遵循 JSON Schema。** 请求仍携带原有 Schema 参数；更改的是响应验证方式。HTTP 响应外层、SSE 事件和工具参数仍按各自逻辑解析，不是删除所有 JSON 处理。

## 6. 验证与复盘

在 `P0` 目录运行离线测试：

```powershell
uv run pytest tests ../shared/tests -q
```

最近一次目录迁移后的验证结果为 **48 passed**，覆盖配置、本机代理绕过、502、超时、连接失败、异常响应、字符串包含检查等。这是历史验证记录，不是执行本文档时自动生成的新结果。

保存下一次真实报告可以执行：

```powershell
uv run python examples/model_capabilities.py > examples/model_capabilities_report.json
```

本记录没有把历史对话中的零散输出拼成一份新的实测报告。生成报告后，应结合 `endpoint`、`http_status`、`detail` 和 `attempts` 判断：

- **请求层失败**：502、超时、连接重置，能力暂时无法判断。
- **响应格式未通过**：200 但内容不符合探针预期，需要查看模型原文。
- **探针自身错误**：错误分类不准确、假定 JSON 一定是对象，需要修改客户端代码。
- **验证成功**：仅说明本次样例通过当前规则，不等于所有模型能力都已得到证明。

相关文件：[能力探针](model_capabilities.py)、[聊天示例](openai_chat_demo.py)、[公共配置](../../shared/agent_common/llm_config.py)、[探针测试](../tests/test_model_capabilities.py)。
