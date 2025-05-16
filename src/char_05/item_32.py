"""
本模块演示了为什么函数返回 None 容易出错，以及如何通过抛出异常来替代 None 返回值。
包含错误示例和正确示例，并使用 logging 记录日志以代替 print 输出。

条目 32：优先使用异常而非返回 `None`
- 错误示例：返回 None 可能导致条件判断错误
- 正确示例：抛出异常以明确处理错误情况
- 使用元组返回状态与结果（非推荐）
- 使用类型注解和文档字符串提高可读性与安全性
"""

import logging

# 配置 logging 模块
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


# 示例1: 错误示例 - 返回 None 的问题
def careful_divide_return_none(a: float, b: float) -> float | None:
    """
    当除法运算失败时返回 None。
    :param a: 被除数
    :param b: 除数
    :return: 商 或 None
    """
    try:
        return a / b
    except ZeroDivisionError:
        return None


def example_return_none():
    """错误示例：使用返回 None 的函数可能导致逻辑错误"""
    x, y = 0, 5
    result = careful_divide_return_none(x, y)

    # 错误的条件判断方式
    if not result:
        logging.warning("错误地将零作为无效输入处理")
    else:
        logging.info(f"计算结果为: {result}")


# 示例2: 推荐做法 - 抛出异常
def careful_divide_raise_exception(a: float, b: float) -> float:
    """
    当除法运算失败时抛出 ValueError 异常。
    :param a: 被除数
    :param b: 除数
    :return: 商
    :raises ValueError: 当除数为零时抛出异常
    """
    try:
        return a / b
    except ZeroDivisionError:
        raise ValueError("无效输入：除数不能为零") from None


def example_raise_exception_success():
    """正确示例：使用异常机制成功执行除法"""
    x, y = 5, 2
    try:
        result = careful_divide_raise_exception(x, y)
        logging.info(f"计算结果为: {result:.1f}")
    except ValueError as e:
        logging.error(e)


def example_raise_exception_failure():
    """正确示例：使用异常机制处理除零错误"""
    x, y = 1, 0
    try:
        result = careful_divide_raise_exception(x, y)
        logging.info(f"计算结果为: {result:.1f}")
    except ValueError as e:
        logging.error(e)


# 示例3: 不推荐做法 - 使用元组返回状态与结果
def careful_divide_tuple_return(a: float, b: float) -> tuple[bool, float | None]:
    """
    使用元组返回操作状态和结果。
    :param a: 被除数
    :param b: 除数
    :return: (操作是否成功, 商 或 None)
    """
    try:
        return True, a / b
    except ZeroDivisionError:
        return False, None


def example_tuple_return_bad_usage():
    """不推荐用法：调用者可能忽略元组的第一部分"""
    x, y = 0, 5
    _, result = careful_divide_tuple_return(x, y)

    # 错误地将有效结果视为错误
    if not result:
        logging.warning("错误地将零作为无效输入处理")
    else:
        logging.info(f"计算结果为: {result}")


def example_tuple_return_good_usage():
    """不推荐用法：但强制检查元组第一部分"""
    x, y = 0, 5
    success, result = careful_divide_tuple_return(x, y)

    if not success:
        logging.warning("检测到无效输入")
    else:
        logging.info(f"计算结果为: {result}")


# 主函数运行所有示例
def main():
    logging.info("=== 示例1：错误示例 - 返回 None ===")
    example_return_none()

    logging.info("=== 示例2：正确示例 - 抛出异常（成功）===")
    example_raise_exception_success()

    logging.info("=== 示例2：正确示例 - 抛出异常（失败）===")
    example_raise_exception_failure()

    logging.info("=== 示例3：不推荐用法 - 元组返回（错误使用）===")
    example_tuple_return_bad_usage()

    logging.info("=== 示例3：不推荐用法 - 元组返回（正确使用）===")
    example_tuple_return_good_usage()


if __name__ == "__main__":
    main()
