"""Pydantic v2 校验示例，无需启动模型网关。

在 P0 目录运行：uv run python examples/pydantic_demo.py
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError


class User(BaseModel):
    """没有默认值的字段必填；Field 可以补充长度和数值范围约束。"""

    name: str = Field(min_length=1, description="姓名，至少一个字符")
    age: int = Field(ge=0, le=120, description="年龄，范围为 0 到 120")
    city: str = "上海"


class StrictUser(BaseModel):
    """严格检查类型，并拒绝模型中未声明的字段。"""

    model_config = ConfigDict(strict=True, extra="forbid")

    name: str
    age: int


class ResearchRequest(BaseModel):
    """将研究任务的字段要求写成可执行的校验规则。"""

    model_config = ConfigDict(extra="forbid")

    topic: str = Field(min_length=1)
    language: Literal["zh", "en"] = "zh"
    max_searches: int = Field(default=3, ge=1, le=10)


def print_errors(exc: ValidationError) -> None:
    """展示字段位置和错误类型；JSON 解析失败时可能没有字段位置。"""
    for error in exc.errors():
        location = ".".join(str(part) for part in error["loc"]) or "整个输入"
        print(f"  字段：{location}；类型：{error['type']}；原因：{error['msg']}")


def demo_basic_validation() -> None:
    print("\n1. 创建对象、使用默认值、导出数据")
    user = User(name="小明", age=18)
    print("姓名：", user.name)
    print("默认城市：", user.city)
    print("字典：", user.model_dump())
    print("JSON 字符串：", user.model_dump_json())

    print("\n2. 非法输入：姓名为空、年龄小于 0")
    try:
        User(name="", age=-1)
    except ValidationError as exc:
        print_errors(exc)


def demo_type_conversion() -> None:
    print("\n3. 默认模式会尝试转换兼容类型")
    # 从字典读取数据，字符串 "18" 会转换成整数 18。
    user = User.model_validate({"name": "小明", "age": "18"})
    print(f"转换后的年龄：{user.age}；类型：{type(user.age).__name__}")

    print("\n4. 严格模式拒绝字符串年龄，extra='forbid' 拒绝额外字段")
    try:
        StrictUser.model_validate({"name": "小明", "age": "18", "nickname": "明明"})
    except ValidationError as exc:
        print_errors(exc)

    user = StrictUser(name="小明", age=18)
    print("使用正确的字段和类型后通过：", user.model_dump())


def demo_model_output() -> None:
    print("\n5. 校验模拟的模型回复（不调用真实模型）")
    model_reply = '{"topic": "学习 Pydantic", "language": "zh", "max_searches": 3}'
    # model_validate_json 同时完成 JSON 解析和字段校验。
    task = ResearchRequest.model_validate_json(model_reply)
    print("校验通过：", task.model_dump())

    invalid_replies = [
        ("缺少必填 topic", '{"language": "zh"}'),
        ("language 不在允许值中", '{"topic": "学习 Pydantic", "language": "fr"}'),
        ("搜索次数超出上限", '{"topic": "学习 Pydantic", "max_searches": 100}'),
        ("存在多余字段", '{"topic": "学习 Pydantic", "other": 1}'),
        ("带 Markdown 标记，不是纯 JSON", '```json\n{"topic": "学习 Pydantic"}\n```'),
    ]
    for label, reply in invalid_replies:
        print(f"\n{label}：")
        try:
            ResearchRequest.model_validate_json(reply)
        except ValidationError as exc:
            print_errors(exc)

    print("\n注意：字段校验通过，只代表格式和约束符合要求，不代表内容事实正确。")


def main() -> None:
    demo_basic_validation()
    demo_type_conversion()
    demo_model_output()


if __name__ == "__main__":
    main()
