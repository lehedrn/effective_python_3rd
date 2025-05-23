"""
本模块演示了 Python 中异常链的处理方式，包括隐式和显式链接异常的技术。
涵盖了以下内容：
- 异常的基本捕获与抛出
- 隐式异常链（__context__）
- 显式异常链（__cause__）
- 抑制异常链上下文
- 自定义异常类及其使用场景

每个示例都封装在一个函数中，并在 main 函数中调用以展示不同场景下的异常行为。
"""

import logging
from traceback import extract_tb

# 设置日志记录器
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class MissingError(Exception):
    """自定义异常：用于表示缺失的键错误"""
    pass


class ServerMissingKeyError(Exception):
    """自定义异常：用于表示服务器端缺失的键错误"""
    pass


def implicit_exception_chaining():
    """
    演示隐式异常链：
    在 except 块中引发新异常时，原始异常会自动保存到 __context__ 属性中。
    """
    my_dict = {}
    try:
        my_dict["does_not_exist"]
    except KeyError:
        raise MissingError("Oops!")


def explicit_exception_chaining():
    """
    演示显式异常链：
    使用 raise ... from ... 语法将原始异常设置为新异常的 cause。
    """
    my_dict = {}

    try:
        my_dict["does_not_exist"]
    except KeyError as e:
        raise MissingError("Explicit chain") from e


def suppress_context_exception():
    """
    演示如何抑制异常链上下文：
    使用 raise ... from None 来完全移除原始异常信息。
    """
    try:
        raise KeyError("Suppressed context")
    except KeyError:
        raise ServerMissingKeyError("No context") from None


def nested_exception_handling():
    """
    演示嵌套异常处理中的异常链：
    处理多个层级的异常捕获和抛出。
    """
    def contact_server(key):
        raise ServerMissingKeyError(f"Server has no key: {key}")

    def lookup(my_key):
        my_dict = {}
        try:
            return my_dict[my_key]
        except KeyError:
            try:
                result = contact_server(my_key)
            except ServerMissingKeyError:
                raise MissingError(f"Failed to fetch key '{my_key}'")  # 隐式链
            else:
                my_dict[my_key] = result
                return result

    lookup("nested_key")


def custom_exception_with_context():
    """
    演示手动访问异常的 __context__ 和 __cause__ 属性，
    以及如何通过 traceback 提取完整的异常链。
    """
    def get_cause(exc):
        if exc.__cause__ is not None:
            return exc.__cause__
        elif not exc.__suppress_context__:
            return exc.__context__
        else:
            return None

    try:
        nested_exception_handling()
    except Exception as e:
        while e is not None:
            stack = extract_tb(e.__traceback__)
            for i, frame in enumerate(stack, 1):
                logger.info(f"{i} {frame.line}")
            e = get_cause(e)
            if e:
                logger.info("Caused by")


def main():
    """
    主函数：运行所有示例并捕获异常进行日志记录。
    """
    examples = [
        implicit_exception_chaining,
        explicit_exception_chaining,
        suppress_context_exception,
        nested_exception_handling,
        custom_exception_with_context
    ]

    for example in examples:
        logger.info(f"\n{'-' * 40}\nRunning example: {example.__name__}\n{'-' * 40}")
        try:
            example()
        except Exception as e:
            logger.error("Exception occurred:", exc_info=True)


if __name__ == "__main__":
    main()
