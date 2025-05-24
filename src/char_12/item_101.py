"""
本模块演示了 Python 中 `list.sort()` 方法与 `sorted()` 函数之间的区别。
包括就地排序、原始数据保留、错误使用示例、性能考虑以及如何正确使用这两种方法。
"""

import logging

# 设置日志输出，替代 print 用于调试和信息展示
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def example_sort_in_place():
    """
    示例 1: 使用 list.sort() 进行就地排序。
    原始列表会被修改，适用于内存敏感场景。
    """
    butterflies = ["Swallowtail", "Monarch", "Red Admiral"]
    logging.info("Before sort: %s", butterflies)
    butterflies.sort()
    logging.info("After sort (in-place): %s", butterflies)


def example_sorted_preserve_original():
    """
    示例 2: 使用 sorted() 保留原始数据。
    排序后返回新列表，原始列表不变。
    """
    original = ["Swallowtail", "Monarch", "Red Admiral"]
    alphabetical = sorted(original)
    logging.info("Original list remains unchanged: %s", original)
    logging.info("Sorted list: %s", alphabetical)


def example_sorted_with_iterable():
    """
    示例 3: sorted() 支持任意可迭代对象（如集合、字典等）。
    """
    patterns = {"solid", "spotted", "cells"}
    sorted_patterns = sorted(patterns)
    logging.info("Sorted set: %s", sorted_patterns)

    legs = {"insects": 6, "spiders": 8, "lizards": 4}
    sorted_legs = sorted(legs, key=lambda x: legs[x], reverse=True)
    logging.info("Sorted dictionary keys by value (descending): %s", sorted_legs)


def example_mutable_arguments_side_effect():
    """
    错误示例：使用 sort() 修改函数参数导致副作用。
    """

    def sort_butterflies(butterflies):
        butterflies.sort()

    data = ["Swallowtail", "Monarch", "Red Admiral"]
    logging.info("Before function call: %s", data)
    sort_butterflies(data)
    logging.warning("Data was modified inside the function: %s", data)


def example_correct_use_with_immutable_data():
    """
    正确示例：使用 sorted() 避免修改原始数据。
    """

    def get_sorted_butterflies(butterflies):
        return sorted(butterflies)

    data = ["Swallowtail", "Monarch", "Red Admiral"]
    sorted_data = get_sorted_butterflies(data)
    logging.info("Original data is preserved: %s", data)
    logging.info("Sorted data from function: %s", sorted_data)


def example_performance_consideration():
    """
    性能对比：sort() 通常比 sorted() 更快，因为无需复制。
    """
    import timeit

    large_list = list(range(100000, 0, -1))

    def test_sort():
        lst = large_list[:]
        lst.sort()

    def test_sorted():
        _ = sorted(large_list)

    time_sort = timeit.timeit(test_sort, number=100)
    time_sorted = timeit.timeit(test_sorted, number=100)

    logging.info("Time for list.sort(): %.5f seconds", time_sort)
    logging.info("Time for sorted(list): %.5f seconds", time_sorted)


def main():
    logging.info("=== 示例 1: list.sort() 就地排序 ===")
    example_sort_in_place()

    logging.info("\n=== 示例 2: sorted() 保留原始数据 ===")
    example_sorted_preserve_original()

    logging.info("\n=== 示例 3: sorted() 支持任意可迭代对象 ===")
    example_sorted_with_iterable()

    logging.info("\n=== 错误示例: sort() 导致函数副作用 ===")
    example_mutable_arguments_side_effect()

    logging.info("\n=== 正确示例: 使用 sorted() 避免副作用 ===")
    example_correct_use_with_immutable_data()

    logging.info("\n=== 性能对比: sort() vs sorted() ===")
    example_performance_consideration()


if __name__ == "__main__":
    main()
