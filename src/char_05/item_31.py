"""
本模块演示了 Python 函数返回多个值的最佳实践，包括：
1. 使用元组解包返回多个值。
2. 使用星号表达式捕获未明确解包的值。
3. 解包超过三个变量时潜在的问题。
4. 使用轻量级类替代多返回值以提高代码可读性和可维护性。
5. 包含错误示例和正确示例，并通过 logging 输出结果。

遵循 PEP8 规范，使用 logging 替代 print 输出信息。
"""

import logging
from dataclasses import dataclass

# 配置 logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# 示例 1: 使用元组解包返回多个值
def get_stats(numbers):
    """
    返回最小值和最大值，展示函数返回两个值的用法。
    """
    minimum = min(numbers)
    maximum = max(numbers)
    return minimum, maximum


# 示例 2: 使用星号表达式捕获中间值
def get_avg_ratio(numbers):
    """
    返回一个比例列表，并使用星号表达式捕获中间部分。
    """
    average = sum(numbers) / len(numbers)
    scaled = [x / average for x in numbers]
    scaled.sort(reverse=True)
    return scaled


# 示例 3: 错误地解包过多返回值导致的问题
def get_stats_more(numbers):
    """
    返回多个统计值，但解包时容易出错。
    """
    count = len(numbers)
    sorted_numbers = sorted(numbers)
    middle = count // 2
    if count % 2 == 0:
        lower = sorted_numbers[middle - 1]
        upper = sorted_numbers[middle]
        median = (lower + upper) / 2
    else:
        median = sorted_numbers[middle]
    minimum = min(numbers)
    maximum = max(numbers)
    average = sum(numbers) / count
    return minimum, maximum, average, median, count


# 示例 4: 使用数据类返回专用对象
@dataclass
class Stats:
    """
    轻量级类用于封装多种统计信息。
    """
    minimum: float
    maximum: float
    average: float
    median: float
    count: int


def get_stats_obj(numbers):
    """
    返回一个 `Stats` 对象，而不是元组。
    """
    count = len(numbers)
    minimum = min(numbers)
    maximum = max(numbers)
    average = sum(numbers) / count
    sorted_numbers = sorted(numbers)
    middle = count // 2
    if count % 2 == 0:
        lower = sorted_numbers[middle - 1]
        upper = sorted_numbers[middle]
        median = (lower + upper) / 2
    else:
        median = sorted_numbers[middle]
    return Stats(minimum=minimum, maximum=maximum, average=average, median=median, count=count)


# 主函数运行所有示例
def main():
    lengths = [63, 73, 72, 60, 67, 66, 71, 61, 72, 70]

    # 示例 1: 元组解包
    logging.info("示例 1: 元组解包返回最小值和最大值")
    minimum, maximum = get_stats(lengths)
    logging.info(f"Min: {minimum}, Max: {maximum}")

    # 示例 2: 星号表达式捕获中间值
    logging.info("示例 2: 使用星号表达式捕获中间值")
    longest, *middle, shortest = get_avg_ratio(lengths)
    logging.info(f"Longest: {longest:>4.0%}")
    logging.info(f"Shortest: {shortest:>4.0%}")

    # 示例 3: 错误解包导致的问题
    logging.info("示例 3: 错误解包多个返回值导致的问题")
    try:
        minimum, maximum, median, average, count = get_stats_more(lengths)
        logging.warning("注意：这里交换了 median 和 average 的顺序，可能导致逻辑错误！")
    except Exception as e:
        logging.error(f"解包错误: {e}")

    # 正确调用方式
    logging.info("示例 3: 正确解包多个返回值")
    minimum, maximum, average, median, count = get_stats_more(lengths)
    logging.info(f"Min: {minimum}, Max: {maximum}, Average: {average}, Median: {median}, Count: {count}")

    # 示例 4: 使用数据类返回专用对象
    logging.info("示例 4: 使用数据类返回专用对象")
    result = get_stats_obj(lengths)
    logging.info(f"Stats: {result}")


if __name__ == "__main__":
    main()
