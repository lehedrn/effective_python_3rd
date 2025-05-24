"""
本文件展示了如何使用 Python 的性能分析工具 cProfile 和 pstats 来识别代码中的性能瓶颈。
其中包括了文档中提到的插入排序低效实现与优化后的版本，以及一个公用函数被多次调用导致性能问题的示例。

主要内容包括：
- 错误示例：低效的插入排序实现。
- 正确示例：使用 bisect 模块优化插入排序。
- 分析工具使用：cProfile 进行性能剖析，pstats 打印统计信息、调用者和被调用者关系。
"""

import logging
from sys import stdout as STDOUT
from cProfile import Profile
from pstats import Stats
from bisect import bisect_left
import random


# 配置日志输出
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# -------------------------------
# 示例 1: 低效的插入排序（错误示例）
# -------------------------------

def insert_value_slow(array, value):
    """
    低效的插入排序辅助函数。对数组进行线性扫描查找插入位置。
    """
    for i, existing in enumerate(array):
        if existing > value:
            array.insert(i, value)
            return
    array.append(value)


def insertion_sort_slow(data):
    """
    使用低效插入方式的插入排序。
    """
    result = []
    for value in data:
        insert_value_slow(result, value)
    return result


# -------------------------------
# 示例 2: 高效的插入排序（正确示例）
# -------------------------------

def insert_value_fast(array, value):
    """
    使用 bisect 模块进行二分查找的插入排序辅助函数。
    大幅提升了插入排序的核心性能。
    """
    i = bisect_left(array, value)
    array.insert(i, value)


def insertion_sort_fast(data):
    """
    使用高效插入方式的插入排序。
    """
    result = []
    for value in data:
        insert_value_fast(result, value)
    return result


# -------------------------------
# 示例 3: 公共函数被频繁调用的情况
# -------------------------------

def my_utility(a, b):
    """
    模拟耗时操作的公共函数。
    """
    c = 1
    for i in range(100):
        c += a * b


def first_func():
    """
    第一个调用 my_utility 的函数。
    """
    for _ in range(1000):
        my_utility(4, 5)


def second_func():
    """
    第二个调用 my_utility 的函数。
    """
    for _ in range(10):
        my_utility(1, 3)


def my_program():
    """
    主程序，调用了多个函数，进而调用了同一个公共函数。
    """
    for _ in range(20):
        first_func()
        second_func()


# -------------------------------
# 主运行函数
# -------------------------------

def run_performance_analysis():
    """
    对各个示例运行性能分析，并打印结果。
    """

    # 生成测试数据
    max_size = 12 ** 4
    data = [random.randint(0, max_size) for _ in range(max_size)]

    # 测试低效插入排序
    logging.info("开始分析低效插入排序...")
    test_slow = lambda: insertion_sort_slow(data)
    profiler = Profile()
    profiler.runcall(test_slow)

    stats = Stats(profiler, stream=STDOUT)
    stats.strip_dirs()
    stats.sort_stats("cumulative")
    logging.info("低效插入排序性能分析结果:")
    stats.print_stats()

    # 测试高效插入排序
    logging.info("开始分析高效插入排序...")
    test_fast = lambda: insertion_sort_fast(data)
    profiler = Profile()
    profiler.runcall(test_fast)

    stats = Stats(profiler, stream=STDOUT)
    stats.strip_dirs()
    stats.sort_stats("cumulative")
    logging.info("高效插入排序性能分析结果:")
    stats.print_stats()

    # 测试函数调用链
    logging.info("开始分析函数调用链...")
    profiler = Profile()
    profiler.runcall(my_program)

    stats = Stats(profiler, stream=STDOUT)
    stats.strip_dirs()
    stats.sort_stats("cumulative")

    logging.info("函数调用链性能分析结果 (调用次数/时间消耗):")
    stats.print_stats()

    logging.info("展示哪个函数调用了 my_utility:")
    stats.print_callers()

    logging.info("展示 my_utility 被哪些函数调用:")
    stats.print_callees()


# -------------------------------
# 程序入口点
# -------------------------------

if __name__ == "__main__":
    logging.info("开始运行性能分析示例...")
    run_performance_analysis()
    logging.info("性能分析示例运行结束。")
