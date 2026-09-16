# P1 示例与练习

**学习优先级：** [必做 → 巩固 → 进阶](../../docs/课程大纲.md#学习优先级)。先完成课次“必做”及阶段验收；巩固按薄弱点补练，进阶不阻塞进度。每阶段维护一份实验记录，后续项目与报告复用已有成果。

已有三个 Prompt Engineering 脚本、客户端创建模块和客户端测试；结构化解析器、流式练习和评估集尚需实现。

完整步骤见 [P1 课次](../../docs/P1.md)，按编号完成。记录遵循[统一实验格式](../../docs/课程大纲.md#实验记录)，保存在本目录；独立练习可以新建自己的脚本，不覆盖原始结果。

## 已有阅读入口

| 文件与函数 | 对应课程 |
|---|---|
| [openai_client.py](openai_client.py) / create_client | P1-01：客户端与配置 |
| [guidelines](gpt_prompt_eng_l2-guidelines.py) / get_completion、p1_t4_few_shot_prompting | P1-01、P1-03 |
| [iterative](gpt_prompt_eng_l3-iterative.py) / issue1_limit_length | P1-03：单变量改写 |
| [transforming](gpt_prompt_eng_l4-transforming.py) / translation_basic、tone_transformation | 独立练习的替换材料 |

第一课按[课程入口](../../docs/P1.md)只调用 get_completion，执行目录是 P1。现有脚本中的格式示例不等于原生 Structured Output 已通过验证。

## 待实现练习

多轮上下文、ResearchRequest 校验、有限修复、事件记录和固定评估集，按 P1-02 至 P1-08 编写；这里没有完整答案脚本。
