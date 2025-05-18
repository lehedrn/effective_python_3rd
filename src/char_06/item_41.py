"""
本文件演示了如何在Python中正确使用列表推导式，并避免在推导式中使用超过两个控制子表达式。
包含简单、清晰的示例，涵盖多层循环、多条件过滤以及复杂推导式的替代方案。

注意事项：
- 使用 `logging` 模块代替 `print` 用于日志输出。
- 所有代码符合 PEP8 规范。
"""

import logging

# 配置日志输出
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def simple_nested_loop_comprehension():
    """
    示例：简单的二维矩阵展开
    使用两个 for 子表达式完成二维列表的展开。
    这是一个合理且易于理解的推导式用法。
    """
    matrix = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9],
    ]
    flat = [x for row in matrix for x in row]
    logging.info("简单二维矩阵展开结果: %s", flat)


def nested_comprehension_with_operation():
    """
    示例：对二维矩阵中的每个元素进行平方操作
    推导式中嵌套一个循环并执行数学运算，虽然格式略显紧凑，但仍然可读。
    """
    matrix = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9],
    ]
    squared = [[x ** 2 for x in row] for row in matrix]
    logging.info("矩阵元素平方后的结果: %s", squared)


def three_level_nested_comprehension():
    """
    错误示例：三层嵌套推导式（不推荐）
    虽然语法正确，但三层结构难以阅读和维护。
    """
    my_lists = [
        [[1, 2, 3], [4, 5, 6]],
        [[7, 8, 9], [10, 11, 12]],
    ]
    flat = [x for sublist1 in my_lists for sublist2 in sublist1 for x in sublist2]
    logging.info("三层嵌套推导式的结果（不推荐）: %s", flat)


def equivalent_normal_loop():
    """
    正确示例：使用普通 for 循环实现三层嵌套逻辑
    更加清晰易懂，适合复杂嵌套场景。
    """
    my_lists = [
        [[1, 2, 3], [4, 5, 6]],
        [[7, 8, 9], [10, 11, 12]],
    ]
    flat = []
    for sublist1 in my_lists:
        for sublist2 in sublist1:
            flat.extend(sublist2)
    logging.info("等效普通循环实现三层嵌套的结果: %s", flat)


def multiple_conditions_in_comprehension():
    """
    示例：推导式中多个 if 条件
    多个 if 条件具有隐含的 and 逻辑，适用于简单的过滤。
    """
    a = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    b = [x for x in a if x > 4 if x % 2 == 0]
    c = [x for x in a if x > 4 and x % 2 == 0]
    logging.info("多条件推导式结果 (b): %s", b)
    logging.info("多条件推导式结果 (c): %s", c)


def complex_filtered_matrix_comprehension():
    """
    错误示例：复杂的推导式过滤矩阵行与列（难于理解）
    包含两个控制子表达式，但结构复杂，不适合初学者。
    """
    matrix = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9],
    ]
    filtered = [[x for x in row if x % 4 == 0] for row in matrix if sum(row) >= 10]
    logging.info("复杂推导式过滤矩阵的结果（不推荐）: %s", filtered)


def helper_function_for_complex_logic():
    """
    正确示例：将复杂逻辑拆分为辅助函数 + 简单推导式
    提高代码可读性和可维护性。
    """

    def is_row_valid(row):
        return sum(row) >= 10

    def filter_divisible_by_four(row):
        return [x for x in row if x % 4 == 0]

    matrix = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9],
    ]
    filtered = [filter_divisible_by_four(row) for row in matrix if is_row_valid(row)]
    logging.info("使用辅助函数的复杂过滤结果: %s", filtered)


def main():
    """
    主函数：运行所有示例
    """
    logging.info("开始执行示例...")

    simple_nested_loop_comprehension()
    nested_comprehension_with_operation()
    three_level_nested_comprehension()
    equivalent_normal_loop()
    multiple_conditions_in_comprehension()
    complex_filtered_matrix_comprehension()
    helper_function_for_complex_logic()

    logging.info("所有示例执行完毕。")


if __name__ == '__main__':
    main()
