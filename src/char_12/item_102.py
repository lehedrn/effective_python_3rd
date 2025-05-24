"""
bisect模块示例演示

该模块展示了bisect模块的使用方法，包括：
- 使用bisect_left进行二分查找
- 与线性查找(index方法)进行性能对比
- 在非精确匹配场景下的应用
- 错误使用示例及正确用法对比
"""

import bisect
import logging
import timeit
import random

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def linear_search_example():
    """
    线性搜索示例 - 使用index方法

    演示了在有序列表中使用index方法进行搜索
    该方法的时间复杂度为O(n)，对于大列表来说效率较低
    """
    data = list(range(10**5))
    try:
        index = data.index(91234)
        logger.info(f"使用index方法找到值91234，索引为：{index}")
    except ValueError:
        logger.error("值不在列表中")

def bisect_left_exact_match():
    """
    bisect_left精确匹配示例

    演示了使用bisect_left在有序列表中进行精确匹配
    时间复杂度为O(log n)
    """
    data = list(range(10**5))
    index = bisect.bisect_left(data, 91234)
    logger.info(f"使用bisect_left找到精确匹配值91234，索引为：{index}")

def bisect_left_closest_match():
    """
    bisect_left最近匹配示例

    演示了当找不到精确匹配时，bisect_left返回应插入的位置
    这个特性可用于寻找最近匹配值
    """
    data = list(range(10**5))
    index = bisect.bisect_left(data, 91234.56)
    logger.info(f"使用bisect_left找到最近匹配值91234.56，应插入位置为：{index}")

def bisect_performance_comparison():
    """
    性能对比示例

    对比线性搜索和bisect_left在大型有序列表上的性能差异
    展示了对数时间复杂度 vs 线性时间复杂度的实际表现
    """
    size = 10**5
    iterations = 1000

    data = list(range(size))
    to_lookup = [random.randint(0, size) for _ in range(iterations)]

    def run_linear():
        for index in to_lookup:
            data.index(index)

    def run_bisect():
        for value in to_lookup:
            bisect.bisect_left(data, value)

    baseline = timeit.timeit(run_linear, number=10) / 10
    logger.info(f"线性搜索耗时: {baseline:.6f}s")

    comparison = timeit.timeit(run_bisect, number=10) / 10
    logger.info(f"Bisect搜索耗时: {comparison:.6f}s")

    slowdown = 1 + ((baseline - comparison) / comparison)
    logger.info(f"线性搜索速度慢{slowdown:.1f}倍")

def bisect_with_non_list_sequence():
    """
    在非列表序列上使用bisect示例

    演示了bisect可以在任何已排序的序列类型上使用
    这里使用tuple作为示例
    """
    data = tuple(range(10**5))  # 使用tuple而不是list
    index = bisect.bisect_left(data, 91234)
    logger.info(f"在tuple上使用bisect_left找到值91234，索引为：{index}")

def incorrect_usage_of_bisect():
    """
    错误使用bisect示例

    演示了当数据未排序时使用bisect可能导致错误的结果
    """
    unsorted_data = [5, 2, 8, 1, 3]  # 未排序的数据
    try:
        index = bisect.bisect_left(unsorted_data, 3)
        logger.warning(f"在未排序数据上使用bisect_left得到错误结果: 值3应该在位置{index}")
    except TypeError as e:
        logger.error(f"发生错误: {e}")

def correct_usage_of_bisect_with_unsorted_data():
    """
    正确处理未排序数据示例

    演示了如何正确处理未排序数据的方法
    首先对数据进行排序，然后再使用bisect
    """
    unsorted_data = [5, 2, 8, 1, 3]
    sorted_data = sorted(unsorted_data)  # 先对数据排序
    index = bisect.bisect_left(sorted_data, 3)
    logger.info(f"先对数据排序后使用bisect_left: 值3在排序后的数据中的位置{index}")

def find_closest_value_wrong_approach():
    """
    寻找最接近值的错误实现示例

    演示了一个常见的错误实现方式
    该实现在某些情况下会抛出异常或返回错误结果
    """
    def find_closest(sequence, goal):
        for index, value in enumerate(sequence):
            if goal < value:
                return index
        return len(sequence)  # 修改为不抛出异常

    data = list(range(10**5))
    index = find_closest(data, 91234.56)
    logger.info(f"使用简单实现找到最接近值91234.56，位置为：{index}")

def find_closest_value_correct_approach():
    """
    寻找最接近值的正确实现示例

    演示了如何正确实现寻找最接近值的功能
    使用bisect_left并检查相邻元素来找到最接近值
    """
    def find_closest(sequence, goal):
        index = bisect.bisect_left(sequence, goal)
        if index == 0:
            return 0
        if index == len(sequence):
            return len(sequence) - 1
        before = sequence[index - 1]
        after = sequence[index] if index < len(sequence) else float('inf')
        if after - goal < goal - before:
            return index
        else:
            return index - 1

    data = list(range(10**5))
    index = find_closest(data, 91234.56)
    logger.info(f"使用bisect找到最接近值91234.56，最接近的位置为：{index}")

def main():
    """主函数 - 运行所有示例"""
    logger.info("开始运行线性搜索示例")
    linear_search_example()

    logger.info("\n开始运行bisect_left精确匹配示例")
    bisect_left_exact_match()

    logger.info("\n开始运行bisect_left最近匹配示例")
    bisect_left_closest_match()

    logger.info("\n开始运行性能对比示例")
    bisect_performance_comparison()

    logger.info("\n开始运行非列表序列bisect示例")
    bisect_with_non_list_sequence()

    logger.info("\n开始运行错误使用bisect示例")
    incorrect_usage_of_bisect()

    logger.info("\n开始运行正确处理未排序数据示例")
    correct_usage_of_bisect_with_unsorted_data()

    logger.info("\n开始运行寻找最接近值错误实现示例")
    find_closest_value_wrong_approach()

    logger.info("\n开始运行寻找最接近值正确实现示例")
    find_closest_value_correct_approach()

if __name__ == "__main__":
    main()
