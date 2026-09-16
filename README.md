# Agent 开发学习课程

**学习优先级：** [必做 → 巩固 → 进阶](docs/课程大纲.md#学习优先级)。先完成课次“必做”及阶段验收；巩固按薄弱点补练，进阶不阻塞进度。每阶段维护一份实验记录，后续项目与报告复用已有成果。

这个仓库面向掌握 Python 基础、希望继续学习 Agent 工程的学习者。课程为期 26 周，从模型 CLI 入手，逐步搭建可测试、可评估、可恢复、可部署的知识研究助手。

完整课程内容、各阶段练习和验收标准见 [课程大纲](docs/课程大纲.md)。

## 今天怎么学

采用“理解概念 → 阅读示例 → 修改并观察 → 用结果验收”的顺序。库只学当前课需要的部分，不必先通读框架文档。

P0 已完成，可直接进入 [P1-01：一次模型请求](docs/P1.md#p1-01)。每课都有固定输入、操作步骤、失败场景和完成证据；实验记录放在对应 examples/，格式见[统一实验记录](docs/课程大纲.md#实验记录)。

## 学习顺序

| 目录 | 主题 | 建议周期 |
|---|---|---:|
| `P0` | 工程与模型接入 | 2 周 |
| `P1` | LLM 应用基础 | 3 周 |
| `P2` | 工具调用与单 Agent | 3 周 |
| `P3` | LangChain 与 LangGraph | 4 周 |
| `P4` | RAG 与事实依据 | 4 周 |
| `P5` | 评估、安全与可靠性 | 3 周 |
| `P6` | API 与生产运行 | 4 周 |
| `P7` | 综合项目交付 | 3 周 |

每周投入 8–9 小时，完成当前阶段的测试、行为评估和失败演练后，再进入下一阶段。

## Windows / PowerShell 快速开始

安装 `uv`：

```powershell
.\init.ps1
```

配置本地 OpenAI 兼容代理：

```powershell
$env:LLM_BASE_URL = "http://127.0.0.1:3030/v1"
$env:LLM_MODEL = "你的代理所支持的模型名"
# 代理需要鉴权时再设置：
$env:LLM_API_KEY = "你的密钥"
```

也可以将`shared/.env.example` 复制为 `shared/.env`，填写实际地址、模型名和可选密钥。P0、P1 调用公共配置时会自动读取 `shared/.env`，如果终端中已设置同名环境变量，则优先使用环境变量的值。`.env` 已被 Git 忽略，不要提交真实密钥。

公共配置使用 `python-dotenv` 解析文件，每次调用时都会重新读取，但不会修改进程环境变量。单独导入模块时，不会读取或校验配置。

进入 P0 并安装依赖：

```powershell
Set-Location P0
uv sync
uv run python examples/model_capabilities.py
uv run pytest
```

如果本地代理尚未启动，能力探针会输出不可用原因，离线单元测试仍应通过。

### 依赖配置说明

- `[project.dependencies]` 保存程序运行时必需的依赖。
- `[dependency-groups].dev` 保存 pytest 等仅用于开发和测试的依赖。
- uv 默认会在 `uv sync` 和 `uv run` 时包含 `dev` 组；不需要再传 `--extra dev`。
- `[project.optional-dependencies]` 用于声明发布后供使用者选择的额外功能所需依赖，本课程的测试工具不放在这里。

## 阶段目录约定

每个 `P0`–`P7` 目录都使用相同结构：

```text
README.md       阶段入口、运行方式和交付要求
examples/       可运行示例、练习代码、实验结果和排错记录
project/        贯穿项目在该阶段的增量
tests/          确定性测试、Fixture 和评估入口
```

P0/P1 已有部分脚本与测试，P2–P7 当前是引导练习和交付说明，没有现成的完整示例。课程会明确指出哪些可以运行、哪些需要自己实现；阶段 README 提供入口，详细步骤以 docs/ 下的阶段文档为准。

## 完成标准

- 未验证的清单项保持 `[ ]`。
- 每个阶段至少保留一个确定性测试、一个模型行为评估和一个失败场景。
- 模型不可用时，使用 Mock 或录制的 Fixture 的测试仍能运行。
- 最终项目的核心回归集成功率不低于 90%，权限与危险操作测试必须全部通过。

Multi-Agent、MCP 和 Code Agent 位于 `electives/`，属于完成核心主线后的选修内容。

## 跨阶段复用模型配置

配置实现统一放在 `shared/agent_common/llm_config.py`。P0、P1 各自通过 `pyproject.toml` 声明本地可编辑依赖，执行 `uv sync` 后，两个阶段会引用同一份源代码。

```python
from agent_common.llm_config import LLMSettings

settings = LLMSettings.from_environment()
```

默认读取 `shared/.env`，路径根据公共模块位置确定，与运行命令所在目录无关。也可以传入 `env_file="其他配置文件路径"`；测试中使用 `env_file=None` 禁用文件读取。

P1 的 `examples/openai_client.py` 只保留 OpenAI SDK 客户端创建函数，配置读取和校验均由公共包负责。P0 使用 httpx，无需依赖 OpenAI SDK。

后续阶段需要使用公共配置时，在对应 `Pn` 目录执行 `uv add --editable ../shared`，然后使用上面的导入方式。各阶段仍保留独立虚拟环境。

验证公共配置与各阶段测试（在仓库根目录执行）：

```powershell
uv run --project P0 pytest P0/tests shared/tests
uv run --project P1 pytest P1/tests shared/tests
```
