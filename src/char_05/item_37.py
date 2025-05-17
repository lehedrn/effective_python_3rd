"""
本模块演示了 Python 中关键字限定参数（Keyword-Only Arguments）和位置限定参数（Positional-Only Arguments）的使用。
通过这些特性，可以增强函数调用的清晰性和接口稳定性。

包含以下示例：
1. 传统位置参数可能导致的错误使用。
2. 使用默认关键字参数提升可读性。
3. 强制使用关键字参数以避免歧义。
4. 使用位置限定参数防止接口耦合。
5. 混合使用位置限定、普通参数、关键字限定参数。
"""

import logging

# 配置日志输出
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# 示例 1: 传统位置参数可能导致的错误使用
def safe_division(number, divisor, ignore_overflow, ignore_zero_division):
    """
    传统位置参数函数：容易混淆布尔标志的位置。
    """
    try:
        return number / divisor
    except OverflowError:
        if ignore_overflow:
            return 0
        else:
            raise
    except ZeroDivisionError:
        if ignore_zero_division:
            return float("inf")
        else:
            raise


def example_1():
    logger.info("示例 1: 错误地使用位置参数导致逻辑错误")
    # 错误调用（布尔参数顺序颠倒）
    try:
        result = safe_division(1.0, 0, True, False)  # 期望忽略除零错误，但实际未忽略
        logger.warning(f"意外成功：{result}")
    except ZeroDivisionError:
        logger.error("正确行为：捕获到 ZeroDivisionError")


# 示例 2: 使用默认关键字参数提升可读性
def safe_division_b(number, divisor, ignore_overflow=False, ignore_zero_division=False):
    """
    使用默认关键字参数，提高调用时的可读性。
    """
    try:
        return number / divisor
    except OverflowError:
        if ignore_overflow:
            return 0
        else:
            raise
    except ZeroDivisionError:
        if ignore_zero_division:
            return float("inf")
        else:
            raise


def example_2():
    logger.info("示例 2: 使用关键字参数提高可读性")
    # 正确使用关键字参数
    result = safe_division_b(1.0, 10**500, ignore_overflow=True)
    logger.info(f"忽略溢出返回零: {result}")

    result = safe_division_b(1.0, 0, ignore_zero_division=True)
    logger.info(f"忽略除零返回无穷大: {result}")


# 示例 3: 强制使用关键字参数以避免歧义
def safe_division_c(number, divisor, *, ignore_overflow=False, ignore_zero_division=False):
    """
    使用 * 分隔符强制关键字参数。
    """
    try:
        return number / divisor
    except OverflowError:
        if ignore_overflow:
            return 0
        else:
            raise
    except ZeroDivisionError:
        if ignore_zero_division:
            return float("inf")
        else:
            raise


def example_3():
    logger.info("示例 3: 强制使用关键字参数")

    # 正确调用方式
    result = safe_division_c(1.0, 0, ignore_zero_division=True)
    logger.info(f"关键字参数调用成功: {result}")

    # 错误调用（尝试传入位置参数给关键字参数）
    try:
        safe_division_c(1.0, 10**500, True, False)
    except TypeError as e:
        logger.error(f"位置参数传递失败: {e}")


# 示例 4: 使用位置限定参数防止接口耦合
def safe_division_e(numerator, denominator, /, *, ignore_overflow=False, ignore_zero_division=False):
    """
    前两个参数为位置限定参数，之后的参数为关键字限定参数。
    """
    try:
        return numerator / denominator
    except OverflowError:
        if ignore_overflow:
            return 0
        else:
            raise
    except ZeroDivisionError:
        if ignore_zero_division:
            return float("inf")
        else:
            raise


def example_4():
    logger.info("示例 4: 使用位置限定参数防止接口耦合")

    # 正确调用
    result = safe_division_e(2, 5)
    logger.info(f"位置参数调用成功: {result}")

    # 错误调用（使用关键字传递位置限定参数）
    try:
        safe_division_e(numerator=2, denominator=5)
    except TypeError as e:
        logger.error(f"关键字传递位置限定参数失败: {e}")


# 示例 5: 混合使用位置限定、普通参数、关键字限定参数
def safe_division_f(numerator, denominator, /, ndigits=10, *, ignore_overflow=False, ignore_zero_division=False):
    """
    前两个参数为位置限定参数，
    ndigits 可以通过位置或关键字传递，
    后续参数为关键字限定参数。
    """
    try:
        fraction = numerator / denominator
        return round(fraction, ndigits)
    except OverflowError:
        if ignore_overflow:
            return 0
        else:
            raise
    except ZeroDivisionError:
        if ignore_zero_division:
            return float("inf")
        else:
            raise


def example_5():
    logger.info("示例 5: 混合使用位置限定、普通参数、关键字限定参数")

    # 多种合法调用方式
    result = safe_division_f(22, 7)
    logger.info(f"默认保留小数位数: {result}")

    result = safe_division_f(22, 7, 5)
    logger.info(f"指定保留5位小数: {result}")

    result = safe_division_f(22, 7, ndigits=2)
    logger.info(f"使用关键字指定保留2位小数: {result}")


# 主函数运行所有示例
def main():
    example_1()
    example_2()
    example_3()
    example_4()
    example_5()


if __name__ == "__main__":
    main()
