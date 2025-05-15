"""
本文件演示了 Python 字典插入顺序行为的变化及其对程序的影响。

内容包括：
1. Python 3.5 及以前版本中字典迭代顺序是任意的。
2. Python 3.7+ 字典默认保留插入顺序。
3. 函数关键字参数（**kwargs）的行为变化。
4. 类实例字段顺序的变化。
5. 使用自定义词典类（如 SortedDict）可能导致问题。
6. 展示了如何避免依赖字典插入顺序的错误做法和正确做法。
"""

import logging
from collections.abc import MutableMapping
from typing import Dict, Iterator

# 配置日志输出
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# 示例 1: Python 3.5 及之前版本中字典不保留顺序
def example_dict_ordering_pre_3_7():
    """
    在 Python 3.5 及更早版本中，字典不会保留插入顺序。
    这意味着即使你按特定顺序插入键值对，遍历时顺序可能完全不同。
    """
    baby_names = {
        "cat": "kitten",
        "dog": "puppy"
    }
    logging.info(f"Python 3.5 及之前的字典顺序：{baby_names}")
    # 注意：此处输出顺序可能不是插入顺序


# 示例 2: Python 3.7+ 中字典保留插入顺序
def example_dict_ordering_post_3_7():
    """
    从 Python 3.7 开始，字典会保留插入顺序。
    这意味着你插入键值对的顺序将被保留并在遍历时反映出来。
    """
    baby_names = {
        "cat": "kitten",
        "dog": "puppy"
    }
    logging.info(f"Python 3.7+ 字典保留插入顺序：{baby_names}")


# 示例 3: 关键字参数顺序在 Python 3.7+ 的变化
def example_kwargs_ordering():
    """
    在 Python 3.7+ 中，函数的关键字参数 (**kwargs) 现在保留了调用时的顺序。
    这对于调试和序列化操作非常有用。
    """

    def my_func(**kwargs):
        for key, value in kwargs.items():
            logging.info(f"{key} = {value}")

    logging.info("Python 3.7+ 关键字参数保留调用顺序：")
    my_func(goose="gosling", kangaroo="joey")


# 示例 4: 实例属性 __dict__ 的顺序变化
def example_instance_dict_ordering():
    """
    在 Python 3.7+ 中，类实例的 __dict__ 属性现在保留了字段赋值顺序。
    这使得调试和序列化对象状态更加直观。
    """

    class MyClass:
        def __init__(self):
            self.alligator = "hatchling"
            self.elephant = "calf"

    a = MyClass()
    logging.info("Python 3.7+ 中 __dict__ 保留赋值顺序：")
    for key, value in a.__dict__.items():
        logging.info(f"{key} = {value}")


# 示例 5: 自定义 SortedDict 导致的问题
def example_sorted_dict_issue():
    """
    当使用自定义的 SortedDict 类（按字母顺序排序）时，
    如果代码依赖字典的插入顺序，可能会导致意外结果。
    """

    votes = {
        "otter": 1281,
        "polar bear": 587,
        "fox": 863,
    }

    ranks = {}
    populate_ranks(votes, ranks)
    winner = get_winner(ranks)
    logging.info(f"正常运行结果：{ranks}, 获胜者: {winner}")

    # 使用 SortedDict 替代 dict
    sorted_ranks = SortedDict()
    populate_ranks(votes, sorted_ranks)
    winner_wrong = get_winner(sorted_ranks)
    logging.warning(f"使用 SortedDict 后错误的结果：{sorted_ranks.data}, 错误获胜者: {winner_wrong}")


# 示例 5 辅助函数：填充排名
def populate_ranks(votes, ranks):
    names = list(votes.keys())
    names.sort(key=votes.get, reverse=True)
    for i, name in enumerate(names, 1):
        ranks[name] = i


# 示例 5 辅助函数：获取获胜者（依赖字典顺序）
def get_winner(ranks):
    return next(iter(ranks))


# 示例 6: 正确处理非 dict 子类的方法一：不依赖插入顺序
def example_get_winner_independent():
    """
    不依赖字典插入顺序获取获胜者。
    这种方法更安全，适用于任何类似字典的对象。
    """

    def get_winner(ranks):
        for name, rank in ranks.items():
            if rank == 1:
                return name
        return None

    votes = {
        "otter": 1281,
        "polar bear": 587,
        "fox": 863,
    }

    sorted_ranks = SortedDict()
    populate_ranks(votes, sorted_ranks)
    winner = get_winner(sorted_ranks)
    logging.info(f"不依赖顺序的 get_winner 正确返回获胜者: {winner}")


# 示例 7: 正确处理非 dict 子类的方法二：类型检查
def example_get_winner_with_type_check():
    """
    在获取获胜者的函数中加入类型检查，
    确保传入的是标准的 dict 类型。
    """

    def get_winner(ranks):
        if not isinstance(ranks, dict):
            raise TypeError("必须传入 dict 类型")
        return next(iter(ranks))

    votes = {
        "otter": 1281,
        "polar bear": 587,
        "fox": 863,
    }

    sorted_ranks = SortedDict()
    populate_ranks(votes, sorted_ranks)

    try:
        winner = get_winner(sorted_ranks)
    except TypeError as e:
        logging.error(f"类型检查拦截非法调用: {e}")


# 示例 8: 自定义 SortedDict 实现
class SortedDict(MutableMapping):
    """按字母顺序迭代的字典类"""

    def __init__(self):
        self.data = {}

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __delitem__(self, key):
        del self.data[key]

    def __iter__(self) -> Iterator[str]:
        keys = list(self.data.keys())
        keys.sort()
        for key in keys:
            yield key

    def __len__(self):
        return len(self.data)


# 主函数运行所有示例
def main():
    logging.info("=== 示例 1: Python 3.5 及之前字典顺序 ===")
    example_dict_ordering_pre_3_7()

    logging.info("\n=== 示例 2: Python 3.7+ 字典保留顺序 ===")
    example_dict_ordering_post_3_7()

    logging.info("\n=== 示例 3: 关键字参数顺序保留 ===")
    example_kwargs_ordering()

    logging.info("\n=== 示例 4: 实例字段 __dict__ 顺序 ===")
    example_instance_dict_ordering()

    logging.info("\n=== 示例 5: SortedDict 导致错误结果 ===")
    example_sorted_dict_issue()

    logging.info("\n=== 示例 6: 不依赖顺序的 get_winner ===")
    example_get_winner_independent()

    logging.info("\n=== 示例 7: 加入类型检查的 get_winner ===")
    example_get_winner_with_type_check()


if __name__ == "__main__":
    main()
