"""
本模块演示了如何使用 Python 的 `functools.singledispatch` 实现函数式风格的动态分派，
对比面向对象多态性在大型程序中的优劣。示例包括：
- 单一分派函数的基本用法；
- 类继承与单一分派的兼容性；
- 错误处理与扩展性问题；
- 混合使用 OOP 与单一分派。

目标是通过清晰、完整的代码示例帮助理解文档中提到的关键点。
"""

import functools
import logging

# 配置日志输出
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def example_basic_singledispatch():
    """
    示例1：基本的 singledispatch 使用方式。
    展示如何根据参数类型选择不同的函数实现。
    """

    @functools.singledispatch
    def my_print(value):
        logger.error("未支持的类型")

    @my_print.register(int)
    def _(value):
        logger.info(f"整数: {value}")

    @my_print.register(str)
    def _(value):
        logger.info(f"字符串: {value}")

    # 调用不同类型的示例
    logger.info("【示例1】基本 singledispatch 使用")
    my_print(42)
    my_print("hello")
    my_print([1, 2, 3])  # 不支持的类型，会调用默认逻辑


def example_inheritance_with_singledispatch():
    """
    示例2：子类自动继承父类的 singledispatch 处理逻辑。
    展示单一分派对继承的支持。
    """

    class Animal:
        pass

    class Dog(Animal):
        pass

    @functools.singledispatch
    def describe(animal):
        logger.warning("未知动物")

    @describe.register(Animal)
    def _(animal):
        logger.info("这是动物")

    logger.info("【示例2】继承与 singledispatch 兼容性")
    dog = Dog()
    describe(dog)  # Dog 是 Animal 的子类，因此匹配 Animal 的注册实现


def example_missing_type_registration():
    """
    示例3：未注册类型的错误处理。
    展示当尝试调用未注册的类型时会抛出 NotImplementedError。
    """

    @functools.singledispatch
    def process_data(data):
        raise NotImplementedError("不支持的数据类型")

    class CustomData:
        pass

    data = CustomData()

    logger.info("【示例3】未注册类型的错误处理")
    try:
        process_data(data)
    except NotImplementedError as e:
        logger.error(f"捕获到未实现异常: {e}")


def example_evaluate_and_pretty_with_singledispatch():
    """
    示例4：使用 singledispatch 实现 evaluate 和 pretty 功能。
    对比传统 OOP 多态和函数式单一分派的实现方式。
    """

    class Integer:
        def __init__(self, value):
            self.value = value

    class Add:
        def __init__(self, left, right):
            self.left = left
            self.right = right

    class Multiply:
        def __init__(self, left, right):
            self.left = left
            self.right = right

    @functools.singledispatch
    def evaluate(node):
        raise NotImplementedError

    @evaluate.register(Integer)
    def _(node):
        return node.value

    @evaluate.register(Add)
    def _(node):
        return evaluate(node.left) + evaluate(node.right)

    @evaluate.register(Multiply)
    def _(node):
        return evaluate(node.left) * evaluate(node.right)

    @functools.singledispatch
    def pretty(node):
        raise NotImplementedError

    @pretty.register(Integer)
    def _(node):
        return repr(node.value)

    @pretty.register(Add)
    def _(node):
        return f"({pretty(node.left)} + {pretty(node.right)})"

    @pretty.register(Multiply)
    def _(node):
        return f"({pretty(node.left)} * {pretty(node.right)})"

    logger.info("【示例4】使用 singledispatch 实现 evaluate 和 pretty")
    tree = Multiply(
        Add(Integer(3), Integer(5)),
        Add(Integer(4), Integer(7)),
    )

    result = evaluate(tree)
    formatted = pretty(tree)

    logger.info(f"计算结果: {result}")
    logger.info(f"格式化表达式: {formatted}")


def example_mixed_oo_and_singledispatch():
    """
    示例5：混合使用 OOP 与 singledispatch。
    在简单数据结构上定义通用方法，并结合单一分派扩展功能。
    """

    class Node:
        def __init__(self, value):
            self.value = value

    class Operation:
        def __init__(self, left, right):
            self.left = left
            self.right = right

    class Add(Operation):
        pass

    class Multiply(Operation):
        pass

    @functools.singledispatch
    def serialize(obj):
        raise NotImplementedError

    @serialize.register(Node)
    def _(obj):
        return str(obj.value)

    @serialize.register(Add)
    def _(obj):
        return f"({serialize(obj.left)} + {serialize(obj.right)})"

    @serialize.register(Multiply)
    def _(obj):
        return f"({serialize(obj.left)} * {serialize(obj.right)})"

    logger.info("【示例5】混合 OOP 与 singledispatch")
    expr = Multiply(Add(Node(2), Node(3)), Node(5))
    logger.info(f"序列化表达式: {serialize(expr)}")


def main():
    """
    主函数：运行所有示例
    """
    example_basic_singledispatch()
    example_inheritance_with_singledispatch()
    example_missing_type_registration()
    example_evaluate_and_pretty_with_singledispatch()
    example_mixed_oo_and_singledispatch()


if __name__ == '__main__':
    main()
