"""
使用 `key` 参数按复杂准则排序示例

本文件演示了如何在 Python 中使用 `list.sort()` 方法和 `key` 参数进行灵活的排序。
包括基本排序、对象排序、多条件排序以及错误用法的示例，并解释了如何处理不同类型的数据排序问题。

功能涵盖：
- 基础类型排序（整数、字符串）
- 对象属性排序（name, weight）
- 多条件排序（元组、多次调用 sort）
- 错误示例与修复方法
"""

import logging

# 设置日志格式
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def example_sort_basic_types():
    """
    示例 1：基础类型排序（整数升序）

    演示对整数列表进行默认升序排序。
    """

    numbers = [93, 86, 11, 68, 70]
    logger.info("原始数据: %s", numbers)
    numbers.sort()
    logger.info("排序后数据: %s", numbers)


def example_sort_objects_without_key():
    """
    示例 2：未使用 key 的对象排序（会抛出异常）

    演示未定义比较方法的对象无法直接排序，将导致 TypeError。
    """

    class Tool:
        def __init__(self, name, weight):
            self.name = name
            self.weight = weight

        def __repr__(self):
            return f"Tool({self.name!r}, {self.weight})"

    tools = [
        Tool("level", 3.5),
        Tool("hammer", 1.25),
        Tool("screwdriver", 0.5),
        Tool("chisel", 0.25),
    ]

    try:
        tools.sort()  # 会失败，因为没有实现比较逻辑
    except TypeError as e:
        logger.error("对象排序失败: %s", str(e))


def example_sort_objects_by_name():
    """
    示例 3：使用 key 按名称排序工具对象

    使用 lambda 函数提取 `name`属性作为排序依据。
    """

    class Tool:
        def __init__(self, name, weight):
            self.name = name
            self.weight = weight

        def __repr__(self):
            return f"Tool({self.name!r}, {self.weight})"

    tools = [
        Tool("level", 3.5),
        Tool("hammer", 1.25),
        Tool("screwdriver", 0.5),
        Tool("chisel", 0.25),
    ]

    logger.info("未排序工具列表: %s", tools)
    tools.sort(key=lambda x: x.name)
    logger.info("按名称排序后: %s", tools)


def example_sort_objects_by_weight():
    """
    示例 4：使用 key 按重量排序工具对象

    使用 lambda 函数提取 `weight` 属性作为排序依据。
    """

    class Tool:
        def __init__(self, name, weight):
            self.name = name
            self.weight = weight

        def __repr__(self):
            return f"Tool({self.name!r}, {self.weight})"

    tools = [
        Tool("level", 3.5),
        Tool("hammer", 1.25),
        Tool("screwdriver", 0.5),
        Tool("chisel", 0.25),
    ]

    logger.info("未排序工具列表: %s", tools)
    tools.sort(key=lambda x: x.weight)
    logger.info("按重量排序后: %s", tools)


def example_sort_case_insensitive():
    """
    示例 5：忽略大小写排序字符串列表

    使用 `str.lower` 方法转换为小写后再排序。
    """

    places = ["home", "work", "New York", "Paris"]
    logger.info("原始字符串列表: %s", places)
    places.sort(key=lambda x: x.lower())
    logger.info("忽略大小写排序后: %s", places)


def example_sort_multiple_criteria_tuple():
    """
    示例 6：使用 tuple 实现多条件排序（weight 然后 name）

    返回一个 (weight, name) 元组用于排序。
    """

    class Tool:
        def __init__(self, name, weight):
            self.name = name
            self.weight = weight

        def __repr__(self):
            return f"Tool({self.name!r}, {self.weight})"

    power_tools = [
        Tool("drill", 4),
        Tool("circular saw", 5),
        Tool("jackhammer", 40),
        Tool("sander", 4),
    ]

    logger.info("原始动力工具列表: %s", power_tools)
    power_tools.sort(key=lambda x: (x.weight, x.name))
    logger.info("按 weight 升序 + name 升序排序后: %s", power_tools)


def example_sort_with_reverse_and_negation():
    """
    示例 7：使用一元减号混合排序方向（weight 降序 + name 升序）

    在元组中使用负值反转数值排序方向。
    """

    class Tool:
        def __init__(self, name, weight):
            self.name = name
            self.weight = weight

        def __repr__(self):
            return f"Tool({self.name!r}, {self.weight})"

    power_tools = [
        Tool("drill", 4),
        Tool("sander", 4),
        Tool("circular saw", 5),
        Tool("jackhammer", 40),
    ]

    logger.info("原始动力工具列表: %s", power_tools)
    power_tools.sort(key=lambda x: (-x.weight, x.name))
    logger.info("按 weight 降序 + name 升序排序后: %s", power_tools)


def example_sort_with_multiple_calls():
    """
    示例 8：通过多次调用 sort 实现多条件排序（weight 降序 + name 升序）

    先按次要条件排序，再按主条件排序。
    """

    class Tool:
        def __init__(self, name, weight):
            self.name = name
            self.weight = weight

        def __repr__(self):
            return f"Tool({self.name!r}, {self.weight})"

    power_tools = [
        Tool("drill", 4),
        Tool("sander", 4),
        Tool("circular saw", 5),
        Tool("jackhammer", 40),
    ]

    logger.info("原始动力工具列表: %s", power_tools)

    # 先按 name 升序
    power_tools.sort(key=lambda x: x.name)
    logger.info("先按 name 排序: %s", power_tools)

    # 再按 weight 降序
    power_tools.sort(key=lambda x: x.weight, reverse=True)
    logger.info("最终按 weight 降序排序: %s", power_tools)


def example_unsupported_negation():
    """
    示例 9：尝试对不支持取反的类型进行排序（会抛出异常）

    字符串不能使用负号取反，将导致 TypeError。
    """

    class Tool:
        def __init__(self, name, weight):
            self.name = name
            self.weight = weight

        def __repr__(self):
            return f"Tool({self.name!r}, {self.weight})"

    power_tools = [
        Tool("drill", 4),
        Tool("sander", 4),
        Tool("circular saw", 5),
        Tool("jackhammer", 40),
    ]

    try:
        power_tools.sort(key=lambda x: (x.weight, -x.name), reverse=True)
    except TypeError as e:
        logger.error("字符串不能取反排序: %s", str(e))


def main():
    logger.info("开始执行示例...")

    example_sort_basic_types()
    example_sort_objects_without_key()
    example_sort_objects_by_name()
    example_sort_objects_by_weight()
    example_sort_case_insensitive()
    example_sort_multiple_criteria_tuple()
    example_sort_with_reverse_and_negation()
    example_sort_with_multiple_calls()
    example_unsupported_negation()

    logger.info("所有示例执行完毕。")


if __name__ == "__main__":
    main()
