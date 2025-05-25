"""
本模块演示了在 Python 中使用 `decimal` 模块进行高精度计算的重要性。
它涵盖了 IEEE 754 浮点数的精度问题、使用 `Decimal` 进行精确计算、
构造 `Decimal` 实例的最佳实践，以及如何控制舍入行为。同时对比了错误示例与正确示例。

主要内容：
- 精度丢失的浮点数计算（错误示例）
- 使用 Decimal 的精确计算（正确示例）
- 构造 Decimal 实例时 float 和 str 的区别
- 控制舍入行为：round vs quantize with ROUND_UP
"""

import logging
from decimal import Decimal, ROUND_UP

# 配置日志输出
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def floating_point_precision_issue():
    """
    错误示例：IEEE 754 浮点数精度问题导致的结果不准确。
    计算费用时由于浮点误差，结果为 5.364999999999999 而不是期望的 5.365。
    """
    rate = 1.45
    seconds = 3 * 60 + 42
    cost = rate * seconds / 60
    logger.info(f"Floating point cost: {cost}")
    logger.info(f"Rounded using round: {round(cost, 2)}")


def decimal_precision_example():
    """
    正确示例：使用 Decimal 类确保计算精度。
    使用字符串构造 Decimal 值以避免浮点精度损失。
    """
    rate = Decimal("1.45")
    seconds = Decimal(3 * 60 + 42)
    cost = rate * seconds / Decimal(60)
    logger.info(f"Decimal precision cost: {cost}")
    logger.info(f"Rounded using round (Decimal): {round(cost, 2)}")


def decimal_constructor_with_float():
    """
    错误示例：使用 float 构造 Decimal 导致精度损失。
    """
    value = Decimal(1.45)
    logger.info(f"Decimal from float: {value}")


def decimal_constructor_with_string():
    """
    正确示例：使用字符串构造 Decimal，避免精度损失。
    """
    value = Decimal("1.45")
    logger.info(f"Decimal from string: {value}")


def rounding_with_round_function():
    """
    错误示例：使用 round 函数对极小值进行四舍五入，结果被归零。
    """
    rate = Decimal("0.05")
    seconds = Decimal("5")
    small_cost = rate * seconds / Decimal(60)
    logger.info(f"Small cost with float-like rounding: {small_cost}")
    logger.info(f"Rounded to cents using round: {round(small_cost, 2)}")


def rounding_with_quantize_and_round_up():
    """
    正确示例：使用 Decimal.quantize() 并指定 ROUND_UP 舍入方式，
    可确保即使是非常小的金额也不会被忽略。
    """
    rate = Decimal("0.05")
    seconds = Decimal("5")
    small_cost = rate * seconds / Decimal(60)

    rounded = small_cost.quantize(Decimal("0.01"), rounding=ROUND_UP)
    logger.info(f"Small cost with quantize and ROUND_UP: {small_cost}")
    logger.info(f"Rounded to cents using quantize + ROUND_UP: {rounded}")


def main():
    """
    主函数：运行所有示例函数以展示不同场景下的精度和舍入处理。
    """
    logger.info("=== 错误示例：浮点精度问题 ===")
    floating_point_precision_issue()

    logger.info("\n=== 正确示例：使用 Decimal 进行精确计算 ===")
    decimal_precision_example()

    logger.info("\n=== 错误示例：使用 float 构造 Decimal ===")
    decimal_constructor_with_float()

    logger.info("\n=== 正确示例：使用字符串构造 Decimal ===")
    decimal_constructor_with_string()

    logger.info("\n=== 错误示例：使用 round 对极小值舍入 ===")
    rounding_with_round_function()

    logger.info("\n=== 正确示例：使用 quantize + ROUND_UP 处理极小值 ===")
    rounding_with_quantize_and_round_up()


if __name__ == "__main__":
    main()
