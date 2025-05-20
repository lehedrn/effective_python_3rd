"""
本文件演示了如何正确和错误地创建自定义容器类型，并展示了为何应该从 collections.abc 中的抽象基类继承。

内容涵盖：
1. 自定义列表子类（FrequencyList）
2. 错误实现序列类型的示例（IndexableNode，缺少 __len__）
3. 正确实现序列类型的示例（SequenceNode，包含 __len__）
4. 未实现抽象基类方法导致的实例化错误（BadType）
5. 正确实现 Sequence 接口的 BetterNode 示例

每个示例都封装在单独的函数中，并通过 main 函数运行。
"""

import logging
from collections.abc import Sequence

# 初始化日志配置
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class FrequencyList(list):
    """
    简单的 list 子类，用于统计元素频率。
    """

    def frequency(self):
        """
        统计列表中每个元素出现的次数。

        Returns:
            dict: 元素频率字典，key 是元素，value 是出现次数
        """
        counts = {}
        for item in self:
            counts[item] = counts.get(item, 0) + 1
        return counts


def example_frequency_list():
    """
    演示 FrequencyList 的使用。
    """
    logger.info("=== 示例：FrequencyList（正确的 list 子类） ===")
    foo = FrequencyList(["a", "b", "a", "c", "b", "a", "d"])
    logger.info(f"初始长度: {len(foo)}")
    foo.pop()
    logger.info(f"弹出最后一个元素后: {repr(foo)}")
    logger.info(f"元素频率: {foo.frequency()}")


class BinaryNode:
    """
    二叉树节点基础类。
    """

    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right


class IndexableNode(BinaryNode):
    """
    实现了 __getitem__ 的自定义序列类（但不完整），仅支持索引访问。
    """

    def _traverse(self):
        if self.left is not None:
            yield from self.left._traverse()
        yield self
        if self.right is not None:
            yield from self.right._traverse()

    def __getitem__(self, index):
        for i, item in enumerate(self._traverse()):
            if i == index:
                return item.value
        raise IndexError(f"Index {index} is out of range")


def example_indexable_node():
    """
    演示 IndexableNode 的部分序列行为。
    """
    logger.info("=== 示例：IndexableNode（不完整的序列类型） ===")
    tree = IndexableNode(
        10,
        left=IndexableNode(
            5,
            left=IndexableNode(2),
            right=IndexableNode(6, right=IndexableNode(7)),
        ),
        right=IndexableNode(15, left=IndexableNode(11)),
    )

    logger.info(f"访问 LRR 节点值: {tree.left.right.right.value}")
    logger.info(f"索引 0 值为: {tree[0]}")
    logger.info(f"索引 1 值为: {tree[1]}")
    logger.info(f"是否包含 11: {11 in tree}")
    logger.info(f"转换为列表: {list(tree)}")

    try:
        logger.info(f"尝试获取长度: {len(tree)}")
    except TypeError as e:
        logger.error(f"错误：无法调用 len() - {e}")


class SequenceNode(IndexableNode):
    """
    完整实现了 __len__ 方法，符合序列语义。
    """

    def __len__(self):
        count = 0
        for _ in self._traverse():
            count += 1
        return count


def example_sequence_node():
    """
    演示 SequenceNode 的完整序列行为。
    """
    logger.info("=== 示例：SequenceNode（完整的序列类型） ===")
    tree = SequenceNode(
        10,
        left=SequenceNode(
            5,
            left=SequenceNode(2),
            right=SequenceNode(6, right=SequenceNode(7)),
        ),
        right=SequenceNode(15, left=SequenceNode(11)),
    )

    logger.info(f"树长度: {len(tree)}")
    logger.info(f"索引 3 值为: {tree[3]}")


class BadType(Sequence):
    """
    未实现 Sequence 必需方法的错误示例。
    """
    pass


def example_bad_type():
    """
    尝试实例化未完全实现 Sequence 接口的类。
    """
    logger.info("=== 示例：BadType（未实现接口方法的错误示例） ===")
    try:
        bad_instance = BadType()
    except TypeError as e:
        logger.error(f"TypeError: {e}")


class BetterNode(SequenceNode, Sequence):
    """
    正确继承 Sequence 接口，自动获得 index、count 等方法。
    """
    pass


def example_better_node():
    """
    演示 BetterNode 使用 Sequence 提供的额外功能。
    """
    logger.info("=== 示例：BetterNode（完整实现 Sequence 接口） ===")
    tree = BetterNode(
        10,
        left=BetterNode(
            5,
            left=BetterNode(2),
            right=BetterNode(6, right=BetterNode(7)),
        ),
        right=BetterNode(15, left=BetterNode(11)),
    )
    logger.info(f"数字 7 的索引位置: {tree.index(7)}")
    logger.info(f"数字 10 出现的次数: {tree.count(10)}")


def main():
    """
    主函数，依次运行所有示例。
    """
    example_frequency_list()
    example_indexable_node()
    example_sequence_node()
    example_bad_type()
    example_better_node()


if __name__ == "__main__":
    main()
