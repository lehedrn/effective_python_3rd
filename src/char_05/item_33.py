"""
本模块演示了 Python 中闭包与变量作用域之间的交互，包括：
1. 闭包的基本使用方式；
2. 使用 nonlocal 关键字修改外层作用域变量；
3. 展示不使用 nonlocal 导致的常见错误；
4. 使用类封装状态来替代 nonlocal 的复杂场景。

覆盖文档中提到的所有要点，并提供清晰、符合 PEP8 规范的完整示例。
"""

import logging

# 设置日志配置
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def sort_priority(values, group):
    """
    正确排序并优先显示指定组中的元素。

    Args:
        values (list): 待排序的数字列表。
        group (set): 优先显示的数字集合。

    Returns:
        None: 排序在原列表上进行。
    """

    def helper(x):
        if x in group:
            return (0, x)
        return (1, x)

    values.sort(key=helper)


def sort_priority2_wrong(numbers, group):
    """
    错误示例：尝试通过闭包修改外部变量 found，但由于作用域问题导致失败。

    Args:
        numbers (list): 待排序的数字列表。
        group (set): 优先显示的数字集合。

    Returns:
        bool: 返回错误的 found 状态（始终为 False）。
    """

    found = False

    def helper(x):
        if x in group:
            # 错误地定义了一个新的局部变量 found，而不是修改外部的 found
            found = True
            return (0, x)
        return (1, x)

    numbers.sort(key=helper)
    return found


def sort_priority3_correct(numbers, group):
    """
    正确示例：使用 nonlocal 修改外部作用域变量 found。

    Args:
        numbers (list): 待排序的数字列表。
        group (set): 优先显示的数字集合。

    Returns:
        bool: 是否找到了优先组中的元素。
    """

    found = False

    def helper(x):
        nonlocal found
        if x in group:
            found = True
            return (0, x)
        return (1, x)

    numbers.sort(key=helper)
    return found


class Sorter:
    """
    使用类封装状态，避免 nonlocal 的副作用。

    Attributes:
        group (set): 优先显示的数字集合。
        found (bool): 是否找到优先组中的元素。
    """

    def __init__(self, group):
        self.group = group
        self.found = False

    def __call__(self, x):
        if x in self.group:
            self.found = True
            return (0, x)
        return (1, x)


def main():
    """
    主函数，运行所有示例并输出结果。
    """

    numbers = [8, 3, 1, 2, 5, 4, 7, 6]
    group = {2, 3, 5, 7}

    # 示例1: 基础闭包排序
    logger.info("示例1: 基础闭包排序")
    sorted_numbers = numbers[:]
    sort_priority(sorted_numbers, group)
    logger.info("排序后: %s", sorted_numbers)

    # 示例2: 错误使用闭包修改外部变量
    logger.info("示例2: 错误示例 - 不使用 nonlocal 导致的错误")
    sorted_numbers = numbers[:]
    found = sort_priority2_wrong(sorted_numbers, group)
    logger.info("是否找到优先组元素: %s", found)  # 输出 False，但预期应为 True

    # 示例3: 正确使用 nonlocal
    logger.info("示例3: 正确使用 nonlocal")
    sorted_numbers = numbers[:]
    found = sort_priority3_correct(sorted_numbers, group)
    logger.info("是否找到优先组元素: %s", found)

    # 示例4: 使用类封装状态
    logger.info("示例4: 使用类封装状态替代 nonlocal")
    sorted_numbers = numbers[:]
    sorter = Sorter(group)
    sorted_numbers.sort(key=sorter)
    logger.info("是否找到优先组元素: %s", sorter.found)
    logger.info("排序后: %s", sorted_numbers)


if __name__ == "__main__":
    main()
