"""
本文件展示了如何使用 Python 的 `timeit` 模块进行微基准测试。
包含以下示例：
1. 基础使用：测量简单加法操作的性能。
2. 错误使用：迭代次数太少导致结果不可靠。
3. 正确使用：显式指定迭代次数并计算平均耗时。
4. 使用 setup 隔离初始化代码：测试 `list` 和 `set` 中成员检查的性能差异。
5. 测试循环函数性能：对列表求和的不同实现方式。
6. 使用命令行工具：通过 `python -m timeit` 进行快速性能测试。
"""

import timeit
import logging
import random

# 设置日志记录器
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def basic_timeit_example():
    """
    示例 1: 基础使用
    测量两个整数相加的操作耗时。
    默认运行 100 万次，返回总时间（秒）。
    """
    stmt = "1 + 2"
    delay = timeit.timeit(stmt=stmt, number=1_000_000)
    logger.info(f"基础加法耗时: {delay:.6f} 秒")
    return delay


def incorrect_low_iterations():
    """
    示例 2: 错误使用 - 迭代次数太少
    只运行 100 次，结果可能受系统噪声干扰。
    """
    stmt = "1 + 2"
    delay = timeit.timeit(stmt=stmt, number=100)
    logger.warning(f"错误使用 - 迭代次数太少: {delay:.9f} 秒")
    return delay


def correct_with_normalized_time():
    """
    示例 3: 正确使用 - 显式指定迭代次数并计算平均耗时
    运行 100 万次，并计算单次操作的纳秒级耗时。
    """
    count = 1_000_000
    delay = timeit.timeit(stmt="1 + 2", number=count)
    avg_time = (delay / count) * 1e9  # 转换为纳秒
    logger.info(f"正确使用 - 单次加法耗时: {avg_time:.2f} 纳秒")
    return avg_time


def setup_separate_initialization():
    """
    示例 4: 使用 setup 分隔初始化逻辑
    测试在 list 中查找值的性能。
    """
    count = 100_000
    delay = timeit.timeit(
        setup="""
numbers = list(range(10_000))
random.shuffle(numbers)
probe = 7_777
""",
        stmt="probe in numbers",
        globals=globals(),
        number=count,
    )
    avg_time = (delay / count) * 1e9
    logger.info(f"list 成员查找耗时: {avg_time:.2f} 纳秒")
    return avg_time


def compare_set_vs_list():
    """
    示例 5: 对比 set 和 list 成员查找性能
    使用 setup 替换 list 为 set。
    """
    count = 100_000
    delay = timeit.timeit(
        setup="""
numbers = set(range(10_000))
probe = 7_777
""",
        stmt="probe in numbers",
        globals=globals(),
        number=count,
    )
    avg_time = (delay / count) * 1e9
    logger.info(f"set 成员查找耗时: {avg_time:.2f} 纳秒")
    return avg_time

def loop_sum(items):
    """
    对列表中的元素进行累加求和。
    """
    total = 0
    for i in items:
        total += i
    return total

def test_loop_sum_performance():
    """
    示例 6: 测试循环求和函数性能
    """

    count = 1000
    delay = timeit.timeit(
        setup="numbers = list(range(10_000))",
        stmt="loop_sum(numbers)",
        globals=globals(),
        number=count,
    )
    avg_time_per_call = (delay / count) * 1e9
    avg_time_per_item = (delay / count / 10_000) * 1e9
    logger.info(f"loop_sum 函数调用耗时: {avg_time_per_call:.2f} 纳秒/次")
    logger.info(f"每个元素耗时: {avg_time_per_item:.2f} 纳秒/元素")
    return avg_time_per_item


def main():
    """主函数，运行所有示例"""
    logger.info("开始运行 timeit 示例")

    logger.info("\n=== 示例 1: 基础使用 ===")
    basic_timeit_example()

    logger.info("\n=== 示例 2: 错误使用 - 迭代次数太少 ===")
    incorrect_low_iterations()

    logger.info("\n=== 示例 3: 正确使用 - 显式指定迭代次数并归一化耗时 ===")
    correct_with_normalized_time()

    logger.info("\n=== 示例 4: 使用 setup 分隔初始化逻辑 ===")
    setup_separate_initialization()

    logger.info("\n=== 示例 5: 对比 set 和 list 成员查找性能 ===")
    compare_set_vs_list()

    logger.info("\n=== 示例 6: 测试循环求和函数性能 ===")
    test_loop_sum_performance()

    logger.info("\n所有示例运行完毕")


if __name__ == "__main__":
    main()
