"""
本模块演示了如何在 Python 中使用 `lambda` 和 `functools.partial` 来调整函数接口以适应不同的需求。
主要涵盖以下内容：
1. 使用 `lambda` 重排参数顺序以适配特定接口（如 `functools.reduce`）。
2. 使用 `functools.partial` 固定部分参数，实现柯里化或部分应用。
3. 对比 `lambda` 和 `partial` 的优缺点，并展示何时更适合使用哪种方式。
4. 展示错误用法与正确用法的对比，帮助理解最佳实践。

本文件中的代码符合 PEP8 规范，并尽量使用 `logging` 模块替代 `print` 进行日志输出。
"""

import math
import functools
import logging

# 配置 logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def log_sum(log_total, value):
    """
    计算自然对数之和的基础函数，用于 reduce 接口。

    参数:
        log_total (float): 累计值。
        value (float): 当前输入值。

    返回:
        float: 更新后的累计值。
    """
    log_value = math.log(value)
    return log_total + log_value


def log_sum_alt(value, log_total):
    """
    参数顺序调换后的版本，用于演示 lambda 调整接口。

    参数:
        value (float): 当前输入值。
        log_total (float): 累计值。

    返回:
        float: 更新后的累计值。
    """
    log_value = math.log(value)
    return log_total + log_value


def log_sum_for_reduce(total, value):
    """
    使用 lambda 替代方案后，定义一个辅助函数用于多次调用。

    参数:
        total (float): 累计值。
        value (float): 当前输入值。

    返回:
        float: 更新后的累计值。
    """
    return log_sum_alt(value, total)


def logn_sum(base, logn_total, value):
    """
    支持自定义底数的对数求和函数。

    参数:
        base (float): 对数的底数。
        logn_total (float): 累计值。
        value (float): 当前输入值。

    返回:
        float: 更新后的累计值。
    """
    logn_value = math.log(value, base)
    return logn_total + logn_value


def logn_sum_last(logn_total, value, *, base=10):
    """
    使用关键字参数指定对数底数的版本。

    参数:
        logn_total (float): 累计值。
        value (float): 当前输入值。
        base (float): 对数的底数，默认为 10。

    返回:
        float: 更新后的累计值。
    """
    logn_value = math.log(value, base)
    return logn_total + logn_value


def incorrect_lambda_usage():
    """
    错误示例：使用 lambda 表达式时未正确处理参数顺序。

    这会导致 reduce 函数无法正常工作。
    """

    try:
        result = functools.reduce(
            lambda total, value: log_sum_alt(total, value),
            [10, 20, 40],
            0,
        )
        logger.info(f"错误示例结果: {math.exp(result)}")
    except Exception as e:
        logger.error(f"错误示例出错: {e}")


def correct_lambda_usage():
    """
    正确示例：使用 lambda 表达式重新排列参数顺序以适配 reduce。
    """

    result = functools.reduce(
        lambda total, value: log_sum_alt(value, total),
        [10, 20, 40],
        0,
    )
    logger.info(f"正确示例结果: {math.exp(result)}")


def correct_helper_function_usage():
    """
    正确示例：定义辅助函数以多次复用适配逻辑。
    """

    result = functools.reduce(
        log_sum_for_reduce,
        [10, 20, 40],
        0,
    )
    logger.info(f"使用辅助函数的结果: {math.exp(result)}")


def correct_partial_usage_with_positional():
    """
    正确示例：使用 functools.partial 固定位置参数。
    """

    result = functools.reduce(
        functools.partial(logn_sum, 10),
        [10, 20, 40],
        0,
    )
    logger.info(f"使用 partial 固定位置参数的结果: {math.pow(10, result)}")


def correct_partial_usage_with_keyword():
    """
    正确示例：使用 functools.partial 固定关键字参数。
    """

    log_sum_e = functools.partial(logn_sum_last, base=math.e)
    result = log_sum_e(3, math.e ** 10)
    logger.info(f"使用 partial 固定关键字参数的结果: {result}")


def verbose_lambda_usage():
    """
    错误示例：使用冗长且易出错的 lambda 表达式来固定关键字参数。
    """

    log_sum_e_alt = lambda *a, base=math.e, **kw: logn_sum_last(*a, base=base, **kw)
    result = log_sum_e_alt(3, math.e ** 10)
    logger.info(f"冗长 lambda 表达式的使用结果: {result}")


def main():
    """
    主函数，运行所有示例。
    """

    logger.info("=== 错误示例 ===")
    incorrect_lambda_usage()

    logger.info("=== 正确使用 lambda 示例 ===")
    correct_lambda_usage()

    logger.info("=== 使用辅助函数 ===")
    correct_helper_function_usage()

    logger.info("=== 使用 functools.partial 固定位置参数 ===")
    correct_partial_usage_with_positional()

    logger.info("=== 使用 functools.partial 固定关键字参数 ===")
    correct_partial_usage_with_keyword()

    logger.info("=== 冗长 lambda 表达式 ===")
    verbose_lambda_usage()


if __name__ == '__main__':
    main()
