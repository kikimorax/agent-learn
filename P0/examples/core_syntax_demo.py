"""Phase 0: Python 核心语法速通示例。

运行方式：
    uv run python examples/core_syntax_demo.py
"""

from pathlib import Path
import json
import math


# 变量：Python 是动态类型语言，变量可以直接赋值使用。
course_name = "Python 核心语法速通"
lesson_count = 5
completion_rate = 0.8
topics = ["变量", "函数", "类", "模块", "异常处理"]
lesson_meta = {"phase": 0, "level": "beginner"}


def build_summary(name: str, count: int, topic_list: list[str]) -> str:
    """函数：接收参数并返回结果。"""
    joined_topics = "、".join(topic_list)
    return f"课程《{name}》共有 {count} 个主题：{joined_topics}"


def divide_safely(dividend: float, divisor: float) -> float:
    """异常处理示例：捕获除零错误并抛出更清晰的信息。"""
    try:
        return dividend / divisor
    except ZeroDivisionError as exc:
        raise ValueError("除数不能为 0") from exc


class Learner:
    """类：用于把数据和行为组织在一起。"""

    def __init__(self, name: str, completed_topics: list[str] | None = None) -> None:
        self.name = name
        self.completed_topics = completed_topics or []

    def complete_topic(self, topic: str) -> None:
        """实例方法：修改对象内部状态。"""
        if topic not in self.completed_topics:
            self.completed_topics.append(topic)

    def progress_text(self, total_topics: int) -> str:
        """返回当前学习进度。"""
        finished = len(self.completed_topics)
        return f"{self.name} 已完成 {finished}/{total_topics} 个主题"


def show_module_examples() -> None:
    """模块示例：使用标准库完成常见任务。"""
    root_dir = Path(__file__).resolve().parent
    circle_area = math.pi * 3**2
    json_preview = json.dumps(lesson_meta, ensure_ascii=False)

    print("模块示例：")
    print(f"- 当前脚本目录：{root_dir}")
    print(f"- 半径 3 的圆面积：{circle_area:.2f}")
    print(f"- lesson_meta 转成 JSON：{json_preview}")


def main() -> None:
    """把上面的语法点串起来演示。"""
    print("=" * 40)
    print(build_summary(course_name, lesson_count, topics))
    print(f"当前完成率：{completion_rate:.0%}")
    print("=" * 40)

    student = Learner("Alice")
    student.complete_topic("变量")
    student.complete_topic("函数")
    print(student.progress_text(total_topics=len(topics)))

    show_module_examples()

    print("异常处理示例：")
    try:
        safe_result = divide_safely(10, 2)
        print(f"- 10 / 2 = {safe_result}")

        # 故意触发异常，展示 try/except 的作用。
        divide_safely(10, 0)
    except ValueError as error:
        print(f"- 捕获到错误：{error}")
    finally:
        print("- 示例执行结束")


if __name__ == "__main__":
    main()
