"""
本模块演示了如何使用面向对象编程（OOP）替代基于`isinstance`检查的函数式编程，
以更好地支持代码的可维护性、扩展性和测试性。示例涵盖了以下内容：

1. 使用`isinstance`检查的传统AST评估方式及其局限性。
2. 使用OOP多态实现AST评估，避免冗长的类型判断逻辑。
3. 扩展功能：添加表达式格式化输出功能（pretty printing）。
4. 错误示例和正确示例对比，展示不同方法之间的优劣。

所有示例都包含完整的类定义和运行入口main函数，并使用logging代替print进行日志输出。
"""

import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# ========================================
# 示例 1: 使用 isinstance 检查的传统 AST 实现
# 存在可扩展性差、难以维护的问题
# ========================================

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


def evaluate(node):
    """
    使用 isinstance 判断节点类型进行递归计算。
    缺点：每新增一个操作类型都需要修改该函数。
    """
    if isinstance(node, Integer):
        return node.value
    elif isinstance(node, Add):
        return evaluate(node.left) + evaluate(node.right)
    elif isinstance(node, Multiply):
        return evaluate(node.left) * evaluate(node.right)
    else:
        raise NotImplementedError(f"Unsupported node type: {type(node)}")


def example_with_isinstance():
    logging.info("示例1：使用 isinstance 的传统实现")
    tree = Multiply(
        Add(Integer(3), Integer(5)),
        Add(Integer(4), Integer(7)),
    )
    result = evaluate(tree)
    logging.info(f"结果为：{result}")


# ========================================
# 示例 2: 面向对象多态实现 AST 评估
# 更易扩展、维护，无需修改中心逻辑
# ========================================

class Node:
    def evaluate(self):
        raise NotImplementedError("子类必须实现 evaluate 方法")


class IntegerNode(Node):
    def __init__(self, value):
        self.value = value

    def evaluate(self):
        return self.value


class AddNode(Node):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def evaluate(self):
        return self.left.evaluate() + self.right.evaluate()


class MultiplyNode(Node):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def evaluate(self):
        return self.left.evaluate() * self.right.evaluate()


def example_with_oop_polymorphism():
    logging.info("示例2：使用 OOP 多态实现评估")
    tree = MultiplyNode(
        AddNode(IntegerNode(3), IntegerNode(5)),
        AddNode(IntegerNode(4), IntegerNode(7)),
    )
    result = tree.evaluate()
    logging.info(f"结果为：{result}")


# ========================================
# 示例 3: 添加新功能 - 表达式美化输出（Pretty Printing）
# 展示 OOP 易于扩展的优势
# ========================================

class NodeAlt:
    def evaluate(self):
        raise NotImplementedError("子类必须实现 evaluate 方法")

    def pretty(self):
        raise NotImplementedError("子类必须实现 pretty 方法")


class IntegerNodeAlt(NodeAlt):
    def __init__(self, value):
        self.value = value

    def evaluate(self):
        return self.value

    def pretty(self):
        return str(self.value)


class AddNodeAlt(NodeAlt):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def evaluate(self):
        return self.left.evaluate() + self.right.evaluate()

    def pretty(self):
        return f"({self.left.pretty()} + {self.right.pretty()})"


class MultiplyNodeAlt(NodeAlt):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def evaluate(self):
        return self.left.evaluate() * self.right.evaluate()

    def pretty(self):
        return f"({self.left.pretty()} * {self.right.pretty()})"


def example_with_pretty_printing():
    logging.info("示例3：使用 OOP 实现表达式美化输出")
    tree = MultiplyNodeAlt(
        AddNodeAlt(IntegerNodeAlt(3), IntegerNodeAlt(5)),
        AddNodeAlt(IntegerNodeAlt(4), IntegerNodeAlt(7)),
    )
    result = tree.pretty()
    logging.info(f"美化后的表达式为：{result}")


# ========================================
# 示例 4: 错误示例 - 添加新操作时需修改 evaluate 函数
# 对比 OOP 的可扩展性优势
# ========================================

class Subtract:
    def __init__(self, left, right):
        self.left = left
        self.right = right


def bad_example_add_new_operation():
    """
    错误示例：尝试添加新的减法操作但未更新 evaluate 函数。
    结果抛出 NotImplementedError，表明代码结构不灵活。
    """
    logging.info("错误示例：未更新 evaluate 函数导致异常")
    tree = Subtract(Integer(10), Integer(4))
    try:
        evaluate(tree)
    except NotImplementedError as e:
        logging.error(f"发生错误：{e}")


# ========================================
# 示例 5: 正确示例 - 在 OOP 中添加新操作只需继承和实现
# 不需要修改已有逻辑
# ========================================

class SubtractNode(Node):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def evaluate(self):
        return self.left.evaluate() - self.right.evaluate()


def good_example_extend_with_oop():
    logging.info("正确示例：通过 OOP 扩展减法操作")
    tree = SubtractNode(
        IntegerNode(10),
        IntegerNode(4),
    )
    result = tree.evaluate()
    logging.info(f"减法运算结果为：{result}")


# ========================================
# 主函数入口
# 运行所有示例
# ========================================

def main():
    example_with_isinstance()
    example_with_oop_polymorphism()
    example_with_pretty_printing()
    bad_example_add_new_operation()
    good_example_extend_with_oop()


if __name__ == "__main__":
    main()
