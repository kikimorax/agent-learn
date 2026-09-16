# P0 — 工程与模型接入

**学习优先级：** [必做 → 巩固 → 进阶](../docs/课程大纲.md#学习优先级)。先完成课次“必做”及阶段验收；巩固按薄弱点补练，进阶不阻塞进度。每阶段维护一份实验记录，后续项目与报告复用已有成果。

统一配置、模型 HTTP 调用、错误分类、多轮 CLI 和能力报告。

## 今天先做什么

详见 [P0-01 与本阶段学习指南](../docs/P0.md#p0-01)。P0 已完成，新增课次用于复习；当前学习入口是 [P1-01](../docs/P1.md#p1-01)。

**材料现状：** 已有语法、HTTP、Pydantic、能力探针及 CLI；现有测试以配置为主，指南中的新增错误测试是待完成练习。

## 学习顺序

1. [P0-01 环境与运行路径](../docs/P0.md#p0-01)
2. [P0-02 配置和密钥](../docs/P0.md#p0-02)
3. [P0-03 类型与 Pydantic](../docs/P0.md#p0-03)
4. [P0-04 HTTP、JSON 和异常](../docs/P0.md#p0-04)
5. [P0-05 pytest 与 Mock](../docs/P0.md#p0-05)
6. [P0-06 同步、异步和并发](../docs/P0.md#p0-06)
7. [P0-07 能力报告与 CLI 复盘](../docs/P0.md#p0-07)

每课先完成必做概念与实验并保存证据，再按需选做巩固和进阶。第 1 周复习 01–04；第 2 周复习 05–07 并整理已有证据。

## 已有脚本运行

以下命令在仓库根目录执行；前两个示例无需模型网关，能力探针和 CLI 需要配置本地代理。

```powershell
uv run --project P0 python P0/examples/core_syntax_demo.py
uv run --project P0 python P0/examples/pydantic_demo.py
uv run --project P0 python P0/examples/model_capabilities.py
uv run --project P0 python P0/project/openai_chat_demo.py
uv run --project P0 pytest P0/tests shared/tests
```

配置读取 [shared/.env.example](../shared/.env.example) 对应的 shared/.env 或环境变量。不要把密钥写入脚本与实验记录。

## 目录与验收

- [examples/](examples/README.md)：已有材料、待实现练习与实验记录。
- [project/](project/README.md)：承接前阶段的项目增量和交付要求。
- [tests/](tests/README.md)：离线测试范围与模型评估边界。

验收以 [P0 课程](../docs/P0.md) 为准；阶段完成状态在[课程总览](../docs/课程大纲.md)标记。
