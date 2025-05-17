"""
本模块演示了 Python 中使用关键字参数的多种场景，包括：
- 位置参数与关键字参数的基本用法
- 使用 `**kwargs` 解包字典进行函数调用
- 关键字参数的默认值机制
- 扩展函数参数以保持向后兼容性
- 常见错误示例（如关键字后的位置参数、重复参数）
- 推荐的最佳实践：始终使用关键字传递可选参数

该文件包含多个示例函数，每个函数说明一个关键概念，并在 main 函数中运行完整示例。
"""

import logging

# 配置日志输出
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def example_positional_vs_keyword():
    """
    示例 1: 位置参数与关键字参数对比

    remainder(number, divisor)
    """
    def remainder(number, divisor):
        return number % divisor

    # 正确示例
    logger.info("正确示例：")
    logger.info("remainder(20, 7) = %d", remainder(20, 7))
    logger.info("remainder(20, divisor=7) = %d", remainder(20, divisor=7))
    logger.info("remainder(number=20, divisor=7) = %d", remainder(number=20, divisor=7))
    logger.info("remainder(divisor=7, number=20) = %d", remainder(divisor=7, number=20))

    # 错误示例 1：关键字后的位置参数
    # IDE编译不过
    # try:
    #     remainder(number=20, 7)
    # except SyntaxError as e:
    #     logger.error("错误示例 1（SyntaxError）: %s", e)

    # 错误示例 2：重复参数
    try:
        remainder(20, number=7)
    except TypeError as e:
        logger.error("错误示例 2（TypeError）: %s", e)


def example_kwargs_unpacking():
    """
    示例 2: 使用 **kwargs 解包字典进行函数调用
    """
    def remainder(number, divisor):
        return number % divisor

    my_kwargs = {"number": 20, "divisor": 7}
    result = remainder(**my_kwargs)
    logger.info("使用 **kwargs 解包调用 remainder: %d", result)

    my_kwargs_single = {"divisor": 7}
    result_mixed = remainder(number=20, **my_kwargs_single)
    logger.info("混合使用关键字和 **kwargs 调用 remainder: %d", result_mixed)

    my_kwargs1 = {"number": 20}
    my_kwargs2 = {"divisor": 7}
    result_multi_unpack = remainder(**my_kwargs1, **my_kwargs2)
    logger.info("多次解包调用 remainder: %d", result_multi_unpack)


def example_kwargs_catch_all():
    """
    示例 3: 使用 **kwargs 捕获所有关键字参数
    """
    def print_parameters(**kwargs):
        for key, value in kwargs.items():
            logger.info(f"{key} = {value}")

    logger.info("调用 print_parameters:")
    print_parameters(alpha=1.5, beta=9, gamma=4)


def example_default_arguments():
    """
    示例 4: 使用默认参数简化常见调用
    """
    def flow_rate(weight_diff, time_diff, period=1):
        return (weight_diff / time_diff) * period

    weight_diff = 0.5
    time_diff = 3

    # 默认调用（每秒流速）
    rate_per_second = flow_rate(weight_diff, time_diff)
    logger.info("默认调用（每秒流速）: %.3f kg/s", rate_per_second)

    # 自定义周期（每小时流速）
    rate_per_hour = flow_rate(weight_diff, time_diff, period=3600)
    logger.info("自定义周期调用（每小时流速）: %.3f kg/h", rate_per_hour)


def example_backward_compatibility():
    """
    示例 5: 新增参数并保持向后兼容性
    """
    def flow_rate(weight_diff, time_diff, period=1, units_per_kg=1):
        return ((weight_diff * units_per_kg) / time_diff) * period

    weight_diff = 0.5
    time_diff = 3

    # 向后兼容调用（千克/秒）
    kg_per_second = flow_rate(weight_diff, time_diff)
    logger.info("向后兼容调用（千克/秒）: %.3f kg/s", kg_per_second)

    # 使用新参数（磅/小时）
    pounds_per_hour = flow_rate(weight_diff, time_diff, period=3600, units_per_kg=2.2)
    logger.info("新增参数调用（磅/小时）: %.3f lb/h", pounds_per_hour)

    # 错误示例：位置参数混淆
    try:
        pounds_per_hour_wrong = flow_rate(weight_diff, time_diff, 3600, 2.2)
        logger.warning("虽然结果可能正确，但参数含义不清晰: %.3f lb/h", pounds_per_hour_wrong)
    except Exception as e:
        logger.error("位置参数调用异常: %s", e)


def main():
    logger.info("开始执行示例 1: 位置参数 vs 关键字参数")
    example_positional_vs_keyword()

    logger.info("\n开始执行示例 2: 使用 **kwargs 解包字典进行函数调用")
    example_kwargs_unpacking()

    logger.info("\n开始执行示例 3: 使用 **kwargs 捕获所有关键字参数")
    example_kwargs_catch_all()

    logger.info("\n开始执行示例 4: 使用默认参数简化常见调用")
    example_default_arguments()

    logger.info("\n开始执行示例 5: 新增参数并保持向后兼容性")
    example_backward_compatibility()


if __name__ == "__main__":
    main()
