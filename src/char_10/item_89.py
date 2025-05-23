"""
本模块演示了 Python 中生成器资源管理的正确与错误实践。
重点包括：
1. 错误地在生成器内部管理资源（如文件、锁等），可能导致资源无法及时释放或异常丢失。
2. 正确做法是将资源传递给生成器，由调用者负责资源的清理工作。
3. 展示 `GeneratorExit` 和垃圾回收对生成器中 `finally` 子句执行的影响。
4. 演示如何通过 `with` 语句确保资源可靠释放。

每个函数代表一个完整示例，并在 main 函数中依次运行。
"""

import logging
import gc
import sys
import random

# 配置日志输出
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def example_normal_function_finally():
    """
    示例1：普通函数中的 finally 子句会立即执行。
    在返回值之前，finally 总会被执行。
    """
    logger.info("进入 normal_function 示例")

    def my_func():
        try:
            return 123
        finally:
            logger.info("Finally my_func 执行")

    result = my_func()
    logger.info(f"函数返回值: {result}")
    logger.info("退出 normal_function 示例")


def example_generator_with_finally():
    """
    示例2：生成器中的 finally 子句只会在迭代完成时执行。
    如果提前中断迭代，finally 不会立刻执行。
    """
    logger.info("进入 generator_with_finally 示例")

    def my_generator():
        try:
            yield 10
            yield 20
            yield 30
        finally:
            logger.info("Finally my_generator 执行")

    # 完整迭代生成器
    logger.info("完整迭代生成器")
    for i in my_generator():
        logger.info(f"生成器产出值: {i}")

    # 部分迭代生成器
    logger.info("部分迭代生成器")
    it = my_generator()
    logger.info(next(it))
    logger.info(next(it))
    del it
    gc.collect()  # 强制触发垃圾回收
    logger.info("退出 generator_with_finally 示例")


def example_generator_exit_unexpectedly():
    """
    示例3：生成器未完全迭代导致 finally 未执行。
    只有在垃圾回收时才会执行 finally。
    """
    logger.info("进入 generator_exit_unexpectedly 示例")

    def my_generator():
        try:
            yield 10
            yield 20
            yield 30
        finally:
            logger.info("Finally my_generator 执行")

    it = my_generator()
    logger.info(next(it))
    logger.info(next(it))

    del it
    gc.collect()  # 触发垃圾回收
    logger.info("退出 generator_exit_unexpectedly 示例")


def example_generator_catch_generator_exit():
    """
    示例4：捕获 GeneratorExit 异常。
    即使捕获后重新抛出，也会被垃圾回收机制处理。
    """
    logger.info("进入 generator_catch_generator_exit 示例")

    def catching_generator():
        try:
            yield 40
            yield 50
            yield 60
        except BaseException as e:
            logger.info(f"Catching handler 捕获异常: {type(e)} - {e}")
            raise

    it = catching_generator()
    logger.info(next(it))
    logger.info(next(it))
    del it
    gc.collect()
    logger.info("退出 generator_catch_generator_exit 示例")


def example_generator_raise_error_on_exit():
    """
    示例5：生成器在处理 GeneratorExit 时抛出异常。
    此类异常不会传播回主线程，而是被系统吞掉。
    """
    logger.info("进入 generator_raise_error_on_exit 示例")

    def broken_generator():
        try:
            yield 70
            yield 80
        except BaseException as e:
            logger.info(f"Broken handler 捕获异常: {type(e)} - {e}")
            raise RuntimeError("Broken")

    it = broken_generator()
    logger.info(next(it))
    del it
    gc.collect()
    logger.info("退出 generator_raise_error_on_exit 示例")


def example_wrong_way_pass_path_to_generator():
    """
    示例6（错误）：将路径传入生成器并依赖其清理资源。
    如果生成器未耗尽，资源可能延迟释放。
    """
    logger.info("进入 wrong_way_pass_path_to_generator 示例")

    with open("my_file.txt", "w") as f:
        for _ in range(20):
            f.write("a" * random.randint(0, 100) + "\n")

    def lengths_path(path):
        try:
            with open(path) as handle:
                for i, line in enumerate(handle):
                    logger.info(f"Line {i}")
                    yield len(line.strip())
        finally:
            logger.info("Finally lengths_path 执行")

    max_head = 0
    it = lengths_path("my_file.txt")

    for i, length in enumerate(it):
        if i == 5:
            break
        else:
            max_head = max(max_head, length)

    logger.info(f"最大长度: {max_head}")
    del it
    gc.collect()
    logger.info("退出 wrong_way_pass_path_to_generator 示例")


def example_correct_way_pass_handle_to_generator():
    """
    示例7（正确）：将已打开的文件句柄传入生成器。
    调用者使用 with 管理资源生命周期，保证及时释放。
    """
    logger.info("进入 correct_way_pass_handle_to_generator 示例")

    with open("my_file.txt", "w") as f:
        for _ in range(20):
            f.write("a" * random.randint(0, 100) + "\n")

    def lengths_handle(handle):
        try:
            for i, line in enumerate(handle):
                logger.info(f"Line {i}")
                yield len(line.strip())
        finally:
            logger.info("Finally lengths_handle 执行")

    max_head = 0
    with open("my_file.txt") as handle:
        it = lengths_handle(handle)
        for i, length in enumerate(it):
            if i == 5:
                break
            else:
                max_head = max(max_head, length)

    logger.info(f"最大长度: {max_head}")
    logger.info(f"文件是否关闭: {handle.closed}")
    logger.info("退出 correct_way_pass_handle_to_generator 示例")


def main():
    """主函数，运行所有示例"""
    logger.info("开始运行所有示例")

    example_normal_function_finally()
    example_generator_with_finally()
    example_generator_exit_unexpectedly()
    example_generator_catch_generator_exit()
    example_generator_raise_error_on_exit()
    example_wrong_way_pass_path_to_generator()
    example_correct_way_pass_handle_to_generator()

    logger.info("所有示例运行完毕")


if __name__ == "__main__":
    main()
