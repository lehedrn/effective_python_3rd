"""
本模块演示了 Python 中 `with` 语句与 `contextlib.contextmanager` 的使用，
包括资源管理、上下文切换、异常处理以及日志级别临时修改等场景。
每个函数对应一个完整示例，main 函数运行所有示例。

目标：
1. 展示 `with` 语句替代 `try/finally` 的优势。
2. 使用 `contextmanager` 创建自定义上下文管理器。
3. 演示如何通过 `as` 获取上下文对象。
4. 包含错误示例和正确示例进行对比。
"""

import logging
import os.path
from contextlib import contextmanager

# 配置基础日志设置
logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")

# 正确示例：使用 with 管理文件资源
def correct_with_file_usage():
    """使用 with 打开文件并写入数据，确保文件自动关闭。"""
    logging.info("正确示例：使用 with 打开文件")
    try:
        with open("example.txt", "w") as f:
            f.write("This is some data!")
        logging.info("文件已关闭")
    except Exception as e:
        logging.error(f"发生异常：{e}")


# 错误示例：手动使用 try/finally 管理文件资源
def incorrect_manual_file_usage():
    """手动打开文件并尝试关闭，存在逻辑错误风险。"""
    logging.info("错误示例：手动管理文件关闭")
    f = open("example.txt", "w")
    try:
        f.write("This is some data!")
    finally:
        f.close()
    logging.info("文件已关闭（但代码冗长且易出错）")


# 正确示例：使用 contextmanager 修改日志级别
@contextmanager
def debug_logging(level):
    logger = logging.getLogger()
    old_level = logger.getEffectiveLevel()
    logger.setLevel(level)
    try:
        yield
    finally:
        logger.setLevel(old_level)


def correct_contextmanager_usage():
    """使用 contextmanager 临时提升日志级别为 DEBUG"""
    logging.info("正确示例：使用 contextmanager 临时提升日志级别")
    with debug_logging(logging.DEBUG):
        logging.debug("This debug message should appear")
    logging.debug("This debug message should NOT appear (level restored)")


# 错误示例：未使用 contextmanager 导致日志级别无法恢复
def incorrect_logger_level_change():
    """直接修改日志级别但未恢复，可能导致后续日志行为异常"""
    logging.info("错误示例：未恢复日志级别")
    logger = logging.getLogger()
    old_level = logger.getEffectiveLevel()
    logger.setLevel(logging.DEBUG)  # 修改级别但未恢复
    logging.debug("This debug message appears")
    logger.setLevel(old_level)  # 假设忘记这一步，将导致日志混乱


# 正确示例：contextmanager 返回值用于 as 目标
@contextmanager
def log_level(level, name):
    logger = logging.getLogger(name)
    old_level = logger.getEffectiveLevel()
    logger.setLevel(level)
    try:
        yield logger
    finally:
        logger.setLevel(old_level)


def correct_contextmanager_with_as_usage():
    """使用 contextmanager 并通过 as 获取 Logger 对象"""
    logging.info("正确示例：contextmanager 通过 as 提供 Logger 实例")
    with log_level(logging.DEBUG, "my-log") as my_logger:
        my_logger.debug("This debug message should appear for 'my-log'")
    my_logger = logging.getLogger("my-log")
    my_logger.debug("This debug message should NOT appear (level restored)")
    my_logger.error("This error message will always appear")


# 错误示例：未使用 as 目标导致无法访问上下文对象
def incorrect_missing_as_target():
    """未使用 as 目标，无法获取上下文中的对象"""
    logging.info("错误示例：未使用 as 获取上下文对象")
    logger = logging.getLogger("other-log")
    logger.setLevel(logging.DEBUG)
    logger.debug("This debug message appears")
    logger.setLevel(logging.WARNING)  # 无自动恢复机制，需手动控制


# 主函数：运行所有示例
def main():
    logging.info("开始执行示例程序\n")

    logging.info("=== 示例 1：正确使用 with 管理文件 ===")
    correct_with_file_usage()

    logging.info("\n=== 示例 2：错误使用手动管理文件 ===")
    incorrect_manual_file_usage()

    logging.info("\n=== 示例 3：正确使用 contextmanager 改变日志级别 ===")
    correct_contextmanager_usage()

    logging.info("\n=== 示例 4：错误修改日志级别未恢复 ===")
    incorrect_logger_level_change()

    logging.info("\n=== 示例 5：正确使用 contextmanager + as 获取 Logger ===")
    correct_contextmanager_with_as_usage()

    logging.info("\n=== 示例 6：错误忽略 as 目标 ===")
    incorrect_missing_as_target()

    if os.path.exists("example.txt"):
        os.remove("example.txt")

    logging.info("\n示例程序执行完毕")


if __name__ == "__main__":
    main()
