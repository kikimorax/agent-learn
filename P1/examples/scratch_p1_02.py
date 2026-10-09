"""P1-02：比较第二轮不带历史与携带历史，并观察 token 用量。

在 P1 目录运行：uv run python examples/scratch_p1_02.py。
正常完成会发起三次真实模型请求；导入模块不会发起请求。
两组对照复用同一轮历史，模型和 temperature 保持相同。
"""

import json

from agent_common.llm_config import LLMSettings
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

from openai_client import create_client


def ask(
    client: OpenAI,
    model: str,
    label: str,
    messages: list[ChatCompletionMessageParam],
) -> str | None:
    print(f"\n=== {label} ===\n请求 messages：", flush=True)
    print(json.dumps(messages, ensure_ascii=False, indent=2), flush=True)

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0,
    )
    message = response.choices[0].message
    print("回复 message：")
    print(json.dumps(message.model_dump(exclude_none=True), ensure_ascii=False, indent=2))

    print("usage（token 用量）：")
    for field in ("prompt_tokens", "completion_tokens", "total_tokens"):
        value = getattr(response.usage, field, None)
        print(f"  {field}: {value if value is not None else '未知'}")
    return message.content


def main() -> None:
    settings = LLMSettings.from_environment()
    print(f"模型：{settings.model}；temperature=0", flush=True)
    first_messages: list[ChatCompletionMessageParam] = [
        {"role": "user", "content": "项目代号是青禾。"},
    ]
    question: ChatCompletionMessageParam = {
        "role": "user",
        "content": "项目代号是什么？",
    }

    with create_client(settings) as client:
        # 实验不自动重试，超时或接口错误直接报告，避免额外调用。
        client = client.with_options(timeout=60.0, max_retries=0)
        first_reply = ask(client, settings.model, "第一轮：告诉模型代号", first_messages)
        if first_reply is None:
            raise SystemExit("第一轮未返回文本，停止实验；请检查上面的完整 message。")

        # A：第二次请求只含当前问题，即使复用同一个 client 也没有历史。
        ask(client, settings.model, "第二轮 A：不带历史", [question])

        # B：补上第一轮问答。必须使用真实回复，不手写一条假回复。
        # 创建新列表，不把 A 的回答混进 B，保持对照条件一致。
        history: list[ChatCompletionMessageParam] = [
            *first_messages,
            {"role": "assistant", "content": first_reply},
            question,
        ]
        ask(client, settings.model, "第二轮 B：携带历史", history)

    print("\n观察：比较 A、B 的实际回答与 prompt_tokens；不带历史时答对也可能只是猜测。")
    print("上下文：本次请求实际发送的信息；上下文窗口有容量上限。")
    print("token：模型处理文本的单位，不等于汉字数；usage 缺失时不能用字数替代。")
    print("采样：temperature 影响输出分布；设为 0 也不保证正确或逐字复现。")


if __name__ == "__main__":
    main()
