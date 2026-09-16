# 示例与练习

**学习优先级：** [必做 → 巩固 → 进阶](../../docs/课程大纲.md#学习优先级)。先完成课次“必做”及阶段验收；巩固按薄弱点补练，进阶不阻塞进度。每阶段维护一份实验记录，后续项目与报告复用已有成果。

本目录包含以下示例：

- `core_syntax_demo.py`：Python 核心语法。
- `pydantic_demo.py`：字段约束、错误信息、类型转换、严格模式和模型回复校验；无需启动模型网关。
- `http_request_demo.py`：同步、异步顺序和异步并发 HTTP 请求。
- [../project/openai_chat_demo.py](../project/openai_chat_demo.py)：已在 project/ 的多轮聊天客户端。
- `model_capabilities.py`：模型网关接口及能力探测。

在 `P0` 目录运行：

```powershell
uv run python examples/core_syntax_demo.py
uv run python examples/pydantic_demo.py
uv run python examples/http_request_demo.py sync
uv run python examples/http_request_demo.py async
uv run python examples/http_request_demo.py con
uv run python project/openai_chat_demo.py
uv run python examples/model_capabilities.py
uv run pytest
```

模型连接配置仍使用公共的 `shared/.env`，详见 [P0 说明](../README.md)。

## 练习任务与记录

按 [P0-01 至 P0-07](../../docs/P0.md) 复习。HTTP/CLI 的新增错误测试为待实现练习，现有文件不代表这些任务已全部覆盖。提交时按[统一格式](../../docs/课程大纲.md#实验记录)保存运行命令、结果和失败说明。

Pydantic 示例练习：修改 `pydantic_demo.py` 中的姓名、年龄、语言和搜索次数，观察校验结果；对比默认模式与严格模式下字符串年龄的处理方式。

### 已整理的记录

- [ModelCapabilities 失败记录与处理方法](ModelCapabilities排错记录.md)：502、代理绕过、连接重置、读取超时、异常 JSON 和字符串包含验证的排查过程。
