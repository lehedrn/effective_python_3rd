"""
本文件展示了 Python 中 `Exception` 和 `BaseException` 的区别，以及如何正确处理这些异常。
包含错误示例和改进后的正确示例，覆盖了文档中提到的多个关键点：

1. `BaseException` 是所有异常的基类，包括像 `KeyboardInterrupt`、`SystemExit` 等特殊异常。
2. 捕获 `Exception` 不会捕获 `BaseException` 及其子类。
3. 使用 `try/finally` 或 `with` 语句可以确保资源释放。
4. 错误地捕获 `BaseException` 可能会导致程序行为异常。
5. 正确传播异常（如使用裸 raise）。
6. 在装饰器等工具中处理所有类型的异常时需要捕获 `BaseException`。

该文件遵循 PEP8 规范，并使用 logging 替代 print 输出日志信息。
"""

import logging
import sys
import functools

# 配置 logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 示例 1: 捕获 Exception 并无法处理 BaseException 子类（错误示例）
def example_1_do_processing():
    raise KeyboardInterrupt


def example_1_main():
    try:
        example_1_do_processing()
    except Exception as e:
        logging.info(f"捕获到异常：{type(e)} - {e}")

    return 0


# 示例 2: 使用 BaseException 捕获并进行清理（不推荐方式）
def example_2_do_processing():
    raise KeyboardInterrupt


def example_2_main():
    handle = open("example_file.txt", "w+")
    try:
        example_2_do_processing()
    except Exception as e:
        logging.info(f"捕获到普通异常：{type(e)} - {e}")
    except BaseException as be:
        logging.warning("检测到 BaseException，正在清理...")
        handle.flush()
        handle.close()
        raise
    finally:
        if not handle.closed:
            handle.close()
    return 0


# 示例 3: 推荐做法 - 使用 try/finally 保证清理（正确示例）
def example_3_do_processing():
    raise KeyboardInterrupt


def example_3_main():
    handle = open("example_file.txt", "w+")

    try:
        example_3_do_processing()
    except Exception as e:
        logging.info(f"捕获到普通异常：{type(e)} - {e}")
    finally:
        logging.info("无论何种异常都会执行清理操作")
        handle.flush()
        handle.close()

    return 0


# 示例 4: 正确传播异常并询问用户是否终止（正确示例）
def example_4_do_processing():
    raise KeyboardInterrupt


def example_4_input(prompt):
    logging.info(f"{prompt}y")
    return "y"


def example_4_main():
    try:
        example_4_do_processing()
    except Exception as e:
        logging.info(f"捕获到普通异常：{type(e)} - {e}")
    except KeyboardInterrupt:
        user_choice = example_4_input("确定要终止程序吗？[y/n]: ")
        if user_choice == 'y':
            logging.warning("用户确认终止，继续抛出异常")
            raise

    return 0


# 示例 5: 错误的日志记录装饰器未处理 BaseException（错误示例）
def log_error_only(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = None
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            result = e
            raise
        finally:
            logging.info(f"Called {func.__name__}(*{args!r}, **{kwargs!r}) got {result!r}")
        return result
    return wrapper


@log_error_only
def example_5_func(x):
    if x > 0:
        sys.exit(1)


# 示例 6: 改进版日志记录装饰器 - 正确处理 BaseException（正确示例）
def log_all_exceptions(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = None
        try:
            result = func(*args, **kwargs)
        except BaseException as be:
            result = be
            raise
        finally:
            logging.info(f"Called {func.__name__}(*{args!r}, **{kwargs!r}) got {result!r}")
        return result
    return wrapper


@log_all_exceptions
def example_6_func(x):
    if x > 0:
        sys.exit(1)


# 主函数运行所有示例
def main():
    logging.info("开始运行示例 1：捕获 Exception 并无法处理 BaseException 子类（错误示例）")
    try:
        example_1_main()
    except BaseException as e:
        logging.error(f"示例1出现未处理的异常：{e}")

    logging.info("\n开始运行示例 2：使用 BaseException 捕获并进行清理（不推荐方式）")
    try:
        example_2_main()
    except KeyboardInterrupt:
        logging.error("示例2成功捕获并重新抛出了 KeyboardInterrupt")

    logging.info("\n开始运行示例 3：推荐做法 - 使用 try/finally 保证清理（正确示例）")
    try:
        example_3_main()
    except KeyboardInterrupt:
        logging.warning("示例3触发了 KeyboardInterrupt 并已清理资源")

    logging.info("\n开始运行示例 4：正确传播异常并询问用户是否终止（正确示例）")
    try:
        example_4_main()
    except KeyboardInterrupt:
        logging.warning("示例4用户确认后抛出了 KeyboardInterrupt")

    logging.info("\n开始运行示例 5：错误的日志记录装饰器未处理 BaseException（错误示例）")
    try:
        example_5_func(100)
    except SystemExit:
        logging.warning("示例5触发了 SystemExit 异常，但未被正确记录")

    logging.info("\n开始运行示例 6：改进版日志记录装饰器 - 正确处理 BaseException（正确示例）")
    try:
        example_6_func(100)
    except SystemExit:
        logging.warning("示例6触发了 SystemExit 并被完整记录")


if __name__ == "__main__":
    sys.exit(main())
