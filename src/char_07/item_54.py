"""
本模块演示了如何使用 Mix-in 类来组合功能，以替代多重继承。涵盖以下内容：
- ToDictMixin：将对象转换为字典以便序列化。
- BinaryTree 示例及其带 parent 的变体 BinaryTreeWithParent，处理循环引用问题。
- JsonMixin：提供 JSON 序列化与反序列化能力。
- 混入类的组合使用（如同时使用 ToDictMixin 和 JsonMixin）。
- 错误示例：错误地使用多重继承导致的问题。
"""

import logging
import json

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# ✅ 正确示例 1: ToDictMixin 基础实现
class ToDictMixin:
    def to_dict(self):
        return self._traverse_dict(self.__dict__)

    def _traverse_dict(self, instance_dict):
        output = {}
        for key, value in instance_dict.items():
            output[key] = self._traverse(key, value)
        return output

    def _traverse(self, key, value):
        if isinstance(value, ToDictMixin):
            return value.to_dict()
        elif isinstance(value, dict):
            return self._traverse_dict(value)
        elif isinstance(value, list):
            return [self._traverse(key, i) for i in value]
        elif hasattr(value, "__dict__"):
            return self._traverse_dict(value.__dict__)
        else:
            return value


# ✅ 正确示例 2: 使用 ToDictMixin 的 BinaryTree
class BinaryTree(ToDictMixin):
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right


def example_binary_tree():
    logger.info("运行示例：BinaryTree.to_dict()")
    tree = BinaryTree(
        10,
        left=BinaryTree(7, right=BinaryTree(9)),
        right=BinaryTree(13, left=BinaryTree(11)),
    )
    logger.info(f"BinaryTree 转换为字典结果: {tree.to_dict()}")


# ✅ 正确示例 3: 避免循环引用的 BinaryTreeWithParent
class BinaryTreeWithParent(BinaryTree):
    def __init__(self, value, left=None, right=None, parent=None):
        super().__init__(value, left=left, right=right)
        self.parent = parent

    def _traverse(self, key, value):
        if isinstance(value, BinaryTreeWithParent) and key == "parent":
            return value.value  # 防止循环
        else:
            return super()._traverse(key, value)


def example_binary_tree_with_parent():
    logger.info("运行示例：BinaryTreeWithParent.to_dict()")
    root = BinaryTreeWithParent(10)
    root.left = BinaryTreeWithParent(7, parent=root)
    root.left.right = BinaryTreeWithParent(9, parent=root.left)
    logger.info(f"BinaryTreeWithParent 转换为字典结果: {root.to_dict()}")


# ✅ 正确示例 4: 使用 ToDictMixin 的 NamedSubTree
class NamedSubTree(ToDictMixin):
    def __init__(self, name, tree_with_parent):
        self.name = name
        self.tree_with_parent = tree_with_parent


def example_named_subtree():
    logger.info("运行示例：NamedSubTree.to_dict()")
    root = BinaryTreeWithParent(10)
    root.left = BinaryTreeWithParent(7, parent=root)
    root.left.right = BinaryTreeWithParent(9, parent=root.left)
    my_tree = NamedSubTree("foobar", root.left.right)
    logger.info(f"NamedSubTree 转换为字典结果: {my_tree.to_dict()}")


# ✅ 正确示例 5: JsonMixin 提供 JSON 序列化支持
class JsonMixin:
    @classmethod
    def from_json(cls, data):
        kwargs = json.loads(data)
        return cls(**kwargs)

    def to_json(self):
        return json.dumps(self.to_dict())


# ✅ 正确示例 6: 同时使用 ToDictMixin 和 JsonMixin
class Machine(ToDictMixin, JsonMixin):
    def __init__(self, cores=None, ram=None, disk=None):
        self.cores = cores
        self.ram = ram
        self.disk = disk


def example_machine_with_json():
    logger.info("运行示例：Machine.to_json()")
    machine = Machine(cores=8, ram=32e9, disk=5e12)
    json_data = machine.to_json()
    logger.info(f"Machine 序列化为 JSON: {json_data}")
    reconstructed = Machine.from_json(json_data)
    logger.info(f"Machine 反序列化后属性: {reconstructed.__dict__}")


# ❌ 错误示例：不恰当使用多重继承导致的问题
class A:
    def __init__(self):
        self.value = 1


class B:
    def __init__(self):
        self.value = 2


# 多重继承中 __init__ 冲突，不会自动调用两个父类构造函数
class C(A, B):
    pass


def example_wrong_multiple_inheritance():
    logger.warning("运行错误示例：C() 初始化仅调用第一个父类 A.__init__")
    c = C()
    logger.warning(f"C().value 实际值是 {c.value}，但预期可能是多个值，这会导致逻辑混乱")


# 🧪 主函数统一运行所有示例
def main():
    logger.info("开始运行所有示例")

    example_binary_tree()
    example_binary_tree_with_parent()
    example_named_subtree()
    example_machine_with_json()
    example_wrong_multiple_inheritance()

    logger.info("所有示例运行完毕")


if __name__ == '__main__':
    main()
