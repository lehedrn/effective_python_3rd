"""
本模块演示了 itertools 模块中各种函数的使用方法。
涵盖了以下功能：
- 将迭代器链接在一起 (chain, repeat, cycle, tee, zip_longest)
- 从迭代器中过滤项目 (islice, takewhile, dropwhile, filterfalse)
- 生成项目组合 (batched, pairwise, accumulate, product, permutations, combinations, combinations_with_replacement)

每个函数都有一个正确的示例和潜在的错误示例。
"""

import itertools
import logging

# 配置日志输出
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def demonstrate_chain():
    """
    演示 itertools.chain 函数：将多个迭代器合并为一个顺序迭代器。
    错误示例展示了如何不正确地处理嵌套列表。
    """
    logging.info("正确使用 chain 合并两个列表：")
    it = itertools.chain([1, 2], [3, 4])
    logging.info(list(it))

    logging.warning("错误使用 chain（未展平嵌套列表）：")
    try:
        it_wrong = itertools.chain([[1, 2], [3, 4]])
        logging.warning(f"错误输出: {list(it_wrong)}")
    except Exception as e:
        logging.error(f"发生错误: {e}")

def demonstrate_repeat():
    """
    演示 itertools.repeat 函数：重复某个值指定次数。
    错误示例展示无限循环的风险。
    """
    logging.info("使用 repeat 限制次数：")
    it = itertools.repeat("hello", 3)
    logging.info(list(it))

    logging.warning("未限制次数的 repeat（将产生无限迭代器）：")
    try:
        it_unlimited = itertools.repeat("loop_forever")
        logging.warning(f"第一个元素: {next(it_unlimited)}")
        logging.warning("这不会自动停止，除非手动中断。")
    except Exception as e:
        logging.error(f"发生错误: {e}")

def demonstrate_cycle():
    """
    演示 itertools.cycle 函数：无限循环迭代器中的元素。
    展示如何安全地获取有限数量的元素。
    """
    logging.info("使用 cycle 获取有限元素：")
    it = itertools.cycle([1, 2])
    result = [next(it) for _ in range(6)]
    logging.info(result)

def demonstrate_tee():
    """
    演示 itertools.tee 函数：将一个迭代器拆分为多个独立的迭代器。
    展示如果迭代器进度不同可能带来的性能问题。
    """
    logging.info("使用 tee 分割迭代器：")
    it1, it2 = itertools.tee([1, 2, 3], 2)
    logging.info(f"迭代器 1: {list(it1)}")
    logging.info(f"迭代器 2: {list(it2)}")

def demonstrate_zip_longest():
    """
    演示 itertools.zip_longest 函数：与普通 zip 不同，可以处理长度不一致的迭代器。
    展示 fillvalue 参数的作用。
    """
    keys = ["one", "two", "three"]
    values = [1, 2]

    logging.info("使用 zip（截断到最短）：")
    logging.info(list(zip(keys, values)))

    logging.info("使用 zip_longest（填充缺失值）：")
    it = itertools.zip_longest(keys, values, fillvalue="nope")
    logging.info(list(it))

def demonstrate_islice():
    """
    演示 itertools.islice 函数：按索引切片迭代器。
    展示 start/stop/step 参数的使用方式。
    """
    values = list(range(1, 11))
    logging.info("原始列表: %s", values)

    first_five = itertools.islice(values, 5)
    logging.info("前五个元素: %s", list(first_five))

    middle_odds = itertools.islice(values, 2, 8, 2)
    logging.info("中间奇数位: %s", list(middle_odds))

def demonstrate_takewhile():
    """
    演示 itertools.takewhile 函数：在条件成立时持续返回元素。
    展示一旦条件失败就立即停止的行为。
    """
    values = list(range(1, 11))
    pred = lambda x: x < 7

    logging.info("takewhile 条件小于 7：")
    it = itertools.takewhile(pred, values)
    logging.info(list(it))

def demonstrate_dropwhile():
    """
    演示 itertools.dropwhile 函数：跳过直到条件首次失败。
    展示跳过行为。
    """
    values = list(range(1, 11))
    pred = lambda x: x < 7

    logging.info("dropwhile 条件小于 7：")
    it = itertools.dropwhile(pred, values)
    logging.info(list(it))

def demonstrate_filterfalse():
    """
    演示 itertools.filterfalse 函数：返回使谓词函数返回 False 的元素。
    对比内置 filter 函数。
    """
    values = list(range(1, 11))
    pred = lambda x: x % 2 == 0

    logging.info("filter（偶数）：")
    logging.info(list(filter(pred, values)))

    logging.info("filterfalse（奇数）：")
    logging.info(list(itertools.filterfalse(pred, values)))

def demonstrate_batched():
    """
    演示 itertools.batched 函数：将迭代器分批输出。
    展示无法整除时的行为。
    """
    logging.info("batched 精确分割：")
    it = itertools.batched(range(1, 10), 3)
    logging.info(list(it))

    logging.info("batched 带余数：")
    it_remainder = itertools.batched(range(1, 4), 2)
    logging.info(list(it_remainder))

def demonstrate_pairwise():
    """
    演示 itertools.pairwise 函数：生成相邻配对。
    展示重叠行为。
    """
    route = ["Los Angeles", "Bakersfield", "Modesto", "Sacramento"]
    logging.info("pairwise 示例：")
    logging.info(list(itertools.pairwise(route)))

def demonstrate_accumulate():
    """
    演示 itertools.accumulate 函数：累计计算。
    展示默认求和行为和自定义模运算。
    """
    values = list(range(1, 11))

    logging.info("accumulate 默认求和：")
    logging.info(list(itertools.accumulate(values)))

    def sum_modulo_20(first, second):
        return (first + second) % 20

    logging.info("accumulate 自定义函数（模 20）：")
    logging.info(list(itertools.accumulate(values, sum_modulo_20)))

def demonstrate_product():
    """
    演示 itertools.product 函数：笛卡尔积。
    展示单个输入和多个输入的情况。
    """
    logging.info("product 使用 repeat=2：")
    logging.info(list(itertools.product([1, 2], repeat=2)))

    logging.info("product 使用两个输入：")
    logging.info(list(itertools.product([1, 2], ["a", "b"])))

def demonstrate_permutations():
    """
    演示 itertools.permutations 函数：生成有序排列。
    展示不同长度的排列。
    """
    logging.info("permutations 长度为 2：")
    logging.info(list(itertools.permutations([1, 2, 3], 2)))

def demonstrate_combinations():
    """
    演示 itertools.combinations 函数：生成无序组合。
    展示不重复的组合。
    """
    logging.info("combinations 长度为 2：")
    logging.info(list(itertools.combinations([1, 2, 3, 4], 2)))

def demonstrate_combinations_with_replacement():
    """
    演示 itertools.combinations_with_replacement 函数：允许重复的组合。
    对比 combinations。
    """
    logging.info("combinations_with_replacement 示例：")
    logging.info(list(itertools.combinations_with_replacement([1, 2, 3, 4], 2)))

def main():
    """
    主函数，运行所有演示函数。
    """
    logging.info("开始运行 itertools 功能演示")

    logging.info("\n=== 连接迭代器 ===")
    demonstrate_chain()
    demonstrate_repeat()
    demonstrate_cycle()
    demonstrate_tee()
    demonstrate_zip_longest()

    logging.info("\n=== 过滤项目 ===")
    demonstrate_islice()
    demonstrate_takewhile()
    demonstrate_dropwhile()
    demonstrate_filterfalse()

    logging.info("\n=== 生成组合 ===")
    demonstrate_batched()
    demonstrate_pairwise()
    demonstrate_accumulate()
    demonstrate_product()
    demonstrate_permutations()
    demonstrate_combinations()
    demonstrate_combinations_with_replacement()

    logging.info("完成 itertools 功能演示")

if __name__ == "__main__":
    main()
