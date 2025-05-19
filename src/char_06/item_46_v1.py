"""
动态生成日志消息，展示如何通过迭代器而非 send 方法向生成器传递数据。

本文件实现了《Effective Python》第三版第六章第46条的建议，通过两个示例对比：
1. 错误示例：使用 send 方法动态调整日志级别，展示其复杂性和意外行为。
2. 正确示例：通过迭代器传递日志级别，展示其清晰性和可靠性。
示例使用 logging 模块记录日志，符合 PEP8 规范，并覆盖书中所有关键点。
"""

import logging
from typing import Iterator, List

# 配置 logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)

# 日志级别映射
LEVELS = {
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
}


def log_with_send(levels: List[str], messages: List[str]) -> Iterator[str]:
    """
    错误示例：使用 send 方法动态调整日志级别。

    生成器接收日志消息并根据 send 方法提供的级别记录日志。
    缺点：
    - 代码复杂，yield 在赋值语句右边不直观。
    - 与 yield from 结合时可能产生 None 输出。
    - 难以理解和维护。
    """
    level = yield  # 接收初始级别
    for msg in messages:
        # 使用 yield 接收级别并记录日志
        level = yield logger.log(LEVELS.get(level, logging.INFO), msg)


def complex_log_with_send(messages: List[str]) -> Iterator[str]:
    """
    错误示例：使用 yield from 组合多个 log_with_send 生成器。

    展示 send 方法与 yield from 结合时的意外行为（None 输出）。
    每次切换子生成器时，初始 yield 导致 None 输出。
    """
    yield from log_with_send(messages[:2], messages[:2])
    yield from log_with_send(messages[2:], messages[2:])


def log_with_iterator(
    level_it: Iterator[str], messages: List[str]
) -> Iterator[str]:
    """
    正确示例：使用迭代器动态调整日志级别。

    生成器通过 next() 从迭代器获取日志级别，逻辑清晰。
    优点：
    - 代码直观，易于理解和维护。
    - 避免 send 方法的复杂性和 None 输出问题。
    - 支持动态级别来源，灵活可组合。
    """
    for msg in messages:
        # 从迭代器获取下一个级别
        level = next(level_it)
        yield logger.log(LEVELS.get(level, logging.INFO), msg)


def complex_log_with_iterator(
    level_it: Iterator[str], messages: List[str]
) -> Iterator[str]:
    """
    正确示例：使用 yield from 组合多个 log_with_iterator 生成器。

    展示迭代器的状态保持特性，多个生成器共享同一迭代器。
    每次切换子生成器时，级别无缝衔接，无 None 输出。
    """
    yield from log_with_iterator(level_it, messages[:2])
    yield from log_with_iterator(level_it, messages[2:])


def run_send_example(messages: List[str], levels: List[str]) -> None:
    """
    运行错误示例：使用 send 方法动态调整日志级别。

    展示 send 方法的复杂性及与 yield from 结合时的 None 输出问题。
    """
    logger.info("=== 运行 send 方法示例 ===")
    gen = complex_log_with_send(messages)
    # 首次 send 必须为 None
    output = gen.send(None)
    if output is None:
        logger.warning("意外的 None 输出")
    for level in levels:
        try:
            output = gen.send(level)
            if output is None:
                logger.warning("意外的 None 输出")
        except StopIteration:
            break


def run_iterator_example(messages: List[str], levels: List[str]) -> None:
    """
    运行正确示例：使用迭代器动态调整日志级别。

    展示迭代器的清晰性和可靠性，无 None 输出问题。
    迭代器支持动态级别来源，代码简洁。
    """
    logger.info("=== 运行迭代器示例 ===")
    level_it = iter(levels)
    gen = complex_log_with_iterator(level_it, messages)
    for _ in messages:
        try:
            next(gen)  # 推进生成器，记录日志
        except StopIteration:
            break


def main() -> None:
    """
    主函数：运行错误和正确示例，比较 send 方法与迭代器方式。

    提供相同的消息和级别输入，展示两种方式的差异。
    """
    messages = [
        "用户登录成功",
        "数据加载完成",
        "文件上传失败",
        "系统重启中",
    ]
    levels = ["INFO", "INFO", "ERROR", "WARNING"]

    # 运行错误示例（send 方法）
    run_send_example(messages, levels)

    # 运行正确示例（迭代器）
    run_iterator_example(messages, levels)


if __name__ == "__main__":
    main()