# P1 — LLM 应用基础

**学习优先级：** [必做 → 巩固 → 进阶](../docs/课程大纲.md#学习优先级)。先完成课次“必做”及阶段验收；巩固按薄弱点补练，进阶不阻塞进度。每阶段维护一份实验记录，后续项目与报告复用已有成果。

将自然语言变成结构化 ResearchRequest，并对拒答、输入缺失和解析失败给出明确结果。

## 今天先做什么

详见 [P1-01 与本阶段学习指南](../docs/P1.md#p1-01)。

**材料现状：** 已有三个 Prompt Engineering 脚本、客户端创建模块和客户端测试；结构化解析器、流式练习和评估集尚需实现。

## 学习顺序

1. [P1-01 一次模型请求与 Message / Instruction](../docs/P1.md#p1-01)
2. [P1-02 上下文、token 与采样](../docs/P1.md#p1-02)
3. [P1-03 明确约束与 Few-shot 对照](../docs/P1.md#p1-03)
4. [P1-04 JSON、Schema 与业务校验](../docs/P1.md#p1-04)
5. [P1-05 拒答、格式失败与有限修复](../docs/P1.md#p1-05)
6. [P1-06 普通输出与流式事件](../docs/P1.md#p1-06)
7. [P1-07 固定评估集](../docs/P1.md#p1-07)
8. [P1-08 研究任务解析器](../docs/P1.md#p1-08)

每课先完成必做概念与实验并保存证据，再按需选做巩固和进阶。第 1 周完成 01–03；第 2 周完成 04–06；第 3 周完成 07–08、项目与验收。

## 配置与运行

配置由 agent_common.llm_config 读取 shared/.env 或环境变量；[openai_client.py](examples/openai_client.py) 的 create_client 负责创建客户端，本机网关绕过环境代理。

第一课使用 [课程中的两次总结调用](../docs/P1.md)，命令在 P1 目录执行。guidelines 脚本当前 main 默认运行幻觉示例，不等于第一课。

离线测试在仓库根目录运行：

```powershell
uv run --project P1 pytest P1/tests shared/tests
```

现有 gpt_prompt_eng_l*.py 是 DeepLearning.AI Prompt Engineering 课程的脚本化材料，按课次选函数阅读；不要求一次运行所有案例，也不要求模型输出隐藏推理。

## 目录与验收

- [examples/](examples/README.md)：已有材料、待实现练习与实验记录。
- [project/](project/README.md)：承接前阶段的项目增量和交付要求。
- [tests/](tests/README.md)：离线测试范围与模型评估边界。

验收以 [P1 课程](../docs/P1.md) 为准；阶段完成状态在[课程总览](../docs/课程大纲.md)标记。
