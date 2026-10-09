"""Shared CLI helper: pick one prompt-engineering case to run, default to none."""

import argparse
from collections.abc import Callable


def run_selected_case(cases: dict[str, Callable[[], None]], description: str) -> None:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "case",
        nargs="?",
        choices=sorted(cases),
        help="要运行的案例名称；缺省时只列出可选项，不发起任何请求。",
    )
    args = parser.parse_args()

    if args.case is None:
        print("未指定 case，可选值：")
        for name in sorted(cases):
            print(f"  {name}")
        print("用法：uv run python <脚本路径> <case>")
        return

    cases[args.case]()
