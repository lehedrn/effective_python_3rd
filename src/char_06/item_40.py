"""
本模块演示了如何使用 Python 的列表推导式（List Comprehensions）代替 `map` 和 `filter` 内建函数。
它涵盖了以下内容：
1. 列表推导式的基本用法，包括过滤和变换。
2. 字典和集合推导式的使用。
3. 与 `map` 和 `filter` 相比的可读性和简洁性。
4. 错误示例与正确示例的对比。
5. 使用 logging 替代 print 输出结果。

通过这些示例，您将理解为什么列表推导式是更推荐的方式，并学会如何在实际开发中使用它们。
"""

import logging

# 设置日志配置
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def example_basic_list_comprehension():
    """
    正确示例：使用列表推导式计算每个数字的平方。
    """
    a = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    squares = [x**2 for x in a]  # 列表推导式实现
    logging.info("基本列表推导式 - 平方: %s", squares)


def example_basic_list_comprehension_with_loop():
    """
    错误示例：使用传统的 for 循环来实现相同功能。
    虽然功能一致，但代码行数更多，不够简洁。
    """
    a = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    squares = []
    for x in a:
        squares.append(x**2)
    logging.info("传统 for 循环 - 平方: %s", squares)


def example_map_lambda_for_squares():
    """
    错误示例：使用 map 和 lambda 实现平方计算。
    需要 lambda 函数，语法较冗余。
    """
    a = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    squares = list(map(lambda x: x**2, a))
    logging.info("map + lambda - 平方: %s", squares)


def example_list_comprehension_with_filter():
    """
    正确示例：使用列表推导式计算偶数的平方。
    """
    a = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    even_squares = [x**2 for x in a if x % 2 == 0]
    logging.info("列表推导式 + 过滤 - 偶数平方: %s", even_squares)


def example_map_filter_for_even_squares():
    """
    错误示例：使用 map 和 filter 实现偶数平方计算。
    由于嵌套 lambda 和 filter，可读性较差。
    """
    a = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    even_squares = list(map(lambda x: x**2, filter(lambda x: x % 2 == 0, a)))
    logging.info("map + filter + lambda - 偶数平方: %s", even_squares)


def example_dict_comprehension():
    """
    正确示例：使用字典推导式生成偶数的平方字典。
    """
    a = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    even_squares_dict = {x: x**2 for x in a if x % 2 == 0}
    logging.info("字典推导式 - 偶数平方字典: %s", even_squares_dict)


def example_set_comprehension():
    """
    正确示例：使用集合推导式生成能被 3 整除的立方集合。
    """
    a = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    threes_cubed_set = {x**3 for x in a if x % 3 == 0}
    logging.info("集合推导式 - 能被3整除的立方集合: %s", threes_cubed_set)


def example_dict_comprehension_with_map_filter():
    """
    错误示例：使用 map 和 filter 构造字典。
    代码冗长且难以维护。
    """
    a = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    alt_dict = dict(
        map(
            lambda x: (x, x**2),
            filter(lambda x: x % 2 == 0, a),
        )
    )
    logging.info("map + filter + dict 构造器 - 偶数平方字典: %s", alt_dict)


def example_set_comprehension_with_map_filter():
    """
    错误示例：使用 map 和 filter 构造集合。
    代码冗长且结构复杂。
    """
    a = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    alt_set = set(
        map(
            lambda x: x**3,
            filter(lambda x: x % 3 == 0, a),
        )
    )
    logging.info("map + filter + set 构造器 - 能被3整除的立方集合: %s", alt_set)


def main():
    """
    主函数，调用所有示例函数运行完整流程。
    """
    logging.info("开始执行示例...")

    example_basic_list_comprehension()
    example_basic_list_comprehension_with_loop()
    example_map_lambda_for_squares()
    example_list_comprehension_with_filter()
    example_map_filter_for_even_squares()
    example_dict_comprehension()
    example_set_comprehension()
    example_dict_comprehension_with_map_filter()
    example_set_comprehension_with_map_filter()

    logging.info("所有示例执行完成。")


if __name__ == "__main__":
    main()
