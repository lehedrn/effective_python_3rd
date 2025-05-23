"""
本模块用于演示 Python 中异常变量的作用域问题以及如何正确处理它们。

包括以下内容：
1. 异常变量在 `except` 块之外不可访问。
2. 异常变量在 `finally` 块中也不可用。
3. 如何通过中间变量保存异常结果以供后续使用。
4. 不提前定义变量可能导致的错误。
5. 使用 logging 替代 print 进行调试输出。
"""

import logging

# 配置日志输出
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# 示例 1: 异常变量在 except 块外不可用
def example_1():
    """
    演示异常变量 e 在 except 块之外无法访问。
    """
    try:
        raise ValueError("这是一个 ValueError")
    except ValueError as e:
        logging.info(f"Inside except block: {e}")
    # 下面这行会引发 NameError，因为 e 只在 except 块内有效
    try:
        logging.info(f"Outside except block: {e}")
    except NameError as ne:
        logging.error(f"捕获到 NameError：{ne}")


# 示例 2: 异常变量在 finally 块中也无法访问
def example_2():
    """
    演示异常变量 e 在 finally 块中也无法访问。
    """
    try:
        raise TypeError("这是一个 TypeError")
    except TypeError as e:
        logging.info(f"Inside except block: {e}")
    finally:
        try:
            logging.info(f"Inside finally block: {e}")
        except NameError as ne:
            logging.error(f"捕获到 NameError：{ne}")


# 示例 3: 正确保存异常信息以供后续使用（推荐做法）
def example_3():
    """
    演示如何将异常信息保存到外部变量 result 中，以便在 finally 块中使用。
    """
    result = "Unexpected exception"
    try:
        raise KeyError("这是一个 KeyError")
    except KeyError as e:
        result = e
    except Exception as e:
        result = e
    else:
        result = "Success"
    finally:
        logging.info(f"Log result={result}")


# 示例 4: 不提前定义 result 变量导致的问题
def example_4():
    """
    演示未处理的异常情况下，未提前定义 result 变量导致的 NameError。
    """
    try:
        raise IndexError("这是一个 IndexError")  # 未被任何 except 捕获
    except ValueError as e:
        result = e
    else:
        result = "Success"
    finally:
        try:
            logging.info(f"Result is: {result}")
        except NameError as ne:
            logging.error(f"捕获到 NameError：{ne}")


# 主函数，运行所有示例
def main():
    logging.info("=== 示例 1: 异常变量在 except 块外不可用 ===")
    example_1()

    logging.info("\n=== 示例 2: 异常变量在 finally 块中也无法访问 ===")
    example_2()

    logging.info("\n=== 示例 3: 正确保存异常信息以供后续使用 ===")
    example_3()

    logging.info("\n=== 示例 4: 不提前定义 result 变量导致的问题 ===")
    example_4()


if __name__ == "__main__":
    main()
