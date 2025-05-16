"""
本文件演示了 Python 中函数参数可变性（mutability）的相关概念。
包括错误示例与正确示例，展示了列表、字典、自定义类对象的引用传递行为，
以及如何通过复制来避免意外修改原始数据。

每个示例都封装在独立函数中，并在 main 函数中调用展示。
"""

import logging

# 配置日志输出
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def example_list_mutation():
    """
    错误示例：函数直接修改传入的列表，导致原始数据被更改。
    """

    def modify_list(items):
        items.append(4)

    original_list = [1, 2, 3]
    logger.info("原始列表: %s", original_list)
    modify_list(original_list)
    logger.info("调用modify_list后列表被修改: %s", original_list)


def example_list_safe_copy():
    """
    正确示例：使用切片创建副本，避免原始数据被修改。
    """

    def safe_modify_list(items):
        items.append(4)
        return items

    original_list = [1, 2, 3]
    logger.info("原始列表: %s", original_list)
    modified_list = safe_modify_list(original_list[:])  # 传入副本
    logger.info("原始列表未被修改: %s", original_list)
    logger.info("修改后的列表: %s", modified_list)


def example_dict_mutation():
    """
    错误示例：函数修改传入的字典内容。
    """

    def modify_dict(items):
        for key in items:
            items[key] += 10

    original_dict = {'a': 1, 'b': 2}
    logger.info("原始字典: %s", original_dict)
    modify_dict(original_dict)
    logger.info("调用modify_dict后字典被修改: %s", original_dict)


def example_dict_safe_copy():
    """
    正确示例：使用dict.copy()方法创建副本以保护原始数据。
    """

    def safe_modify_dict(items):
        for key in items:
            items[key] += 10
        return items

    original_dict = {'a': 1, 'b': 2}
    logger.info("原始字典: %s", original_dict)
    modified_dict = safe_modify_dict(original_dict.copy())  # 传入副本
    logger.info("原始字典未被修改: %s", original_dict)
    logger.info("修改后的字典: %s", modified_dict)


def example_class_mutation():
    """
    错误示例：函数修改了传入对象的属性。
    """

    class MyData:
        def __init__(self, value):
            self.value = value

    def modify_object(obj):
        obj.value += 100

    original_obj = MyData(50)
    logger.info("原始对象值: %d", original_obj.value)
    modify_object(original_obj)
    logger.info("调用modify_object后对象值被修改: %d", original_obj.value)


def example_class_safe_immutable():
    """
    正确示例：采用不可变设计模式，返回新对象而非修改原对象。
    """

    class MyData:
        def __init__(self, value):
            self.value = value

        def add(self, amount):
            return MyData(self.value + amount)  # 返回新实例

    original_obj = MyData(50)
    logger.info("原始对象值: %d", original_obj.value)
    modified_obj = original_obj.add(100)
    logger.info("原始对象值未被修改: %d", original_obj.value)
    logger.info("新的修改后的对象值: %d", modified_obj.value)


def example_aliasing_issue():
    """
    示例说明别名导致的副作用：两个变量指向同一对象。
    """

    def modify_list(items):
        items.append(99)

    a = [1, 2, 3]
    b = a  # 别名，指向同一列表
    logger.info("a 和 b 指向相同对象？%s", a is b)
    logger.info("原始 a: %s", a)
    modify_list(b)
    logger.info("修改 b 后 a 也被修改: %s", a)


def main():
    logger.info("开始演示：列表参数被修改")
    example_list_mutation()
    logger.info("\n" + "-" * 50 + "\n")

    logger.info("开始演示：使用副本避免列表被修改")
    example_list_safe_copy()
    logger.info("\n" + "-" * 50 + "\n")

    logger.info("开始演示：字典参数被修改")
    example_dict_mutation()
    logger.info("\n" + "-" * 50 + "\n")

    logger.info("开始演示：使用副本避免字典被修改")
    example_dict_safe_copy()
    logger.info("\n" + "-" * 50 + "\n")

    logger.info("开始演示：类对象被修改")
    example_class_mutation()
    logger.info("\n" + "-" * 50 + "\n")

    logger.info("开始演示：不可变类设计避免修改")
    example_class_safe_immutable()
    logger.info("\n" + "-" * 50 + "\n")

    logger.info("开始演示：别名导致的数据共享问题")
    example_aliasing_issue()


if __name__ == "__main__":
    main()
