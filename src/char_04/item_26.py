"""
本文件展示了如何处理字典中缺失键的不同方法。
包括使用 `in` 操作符、`KeyError` 异常、`get` 方法和 `setdefault` 方法。
还包含错误示例和正确示例，并通过函数调用展示不同方式的使用。
"""

import logging

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 示例1: 使用 `in` 操作符来处理简单计数器字典
def example_in_operator():
    """
    使用 `in` 操作符检查键是否存在，并更新计数器。
    这种方式需要访问键两次，代码重复且可读性较差。
    """
    counters = {
        "pumpernickel": 2,
        "sourdough": 1,
    }
    key = "wheat"

    if key in counters:
        count = counters[key]
    else:
        count = 0
    counters[key] = count + 1
    logging.info("使用 `in` 操作符的计数器结果: %s", counters)

# 示例2: 使用 `KeyError` 异常处理缺失键
def example_key_error():
    """
    使用 try/except 来捕获 KeyError 并设置默认值。
    虽然理论上更高效，但异常处理机制可能会带来额外开销。
    """
    counters = {
        "pumpernickel": 2,
        "sourdough": 1,
    }
    key = "wheat"

    try:
        count = counters[key]
    except KeyError:
        count = 0
    counters[key] = count + 1
    logging.info("使用 `KeyError` 的计数器结果: %s", counters)

# 示例3: 使用 `get` 方法处理简单计数器
def example_get_method():
    """
    使用 `dict.get(key, default)` 方法获取值或返回默认值。
    只需一次访问和一次赋值，是最清晰简洁的方式。
    """
    counters = {
        "pumpernickel": 2,
        "sourdough": 1,
    }
    key = "wheat"

    count = counters.get(key, 0)
    counters[key] = count + 1
    logging.info("使用 `get` 方法的计数器结果: %s", counters)

# 示例4: 使用 `setdefault` 方法处理列表值
def example_setdefault_with_list():
    """
    使用 `setdefault` 处理复杂类型如列表值。
    更简洁，但可读性不如 `get` 方法。
    """
    votes = {
        "baguette": ["Bob", "Alice"],
        "ciabatta": ["Coco", "Deb"],
    }
    key = "brioche"
    who = "Elmer"

    names = votes.setdefault(key, [])
    names.append(who)
    logging.info("使用 `setdefault` 的投票结果: %s", votes)

# 示例5: 使用 `get` 和赋值表达式 (Python 3.8+)
def example_get_with_walrus_operator():
    """
    使用 `get` 方法和海象运算符 `:=` 提高可读性和简洁性。
    注意：此功能仅适用于 Python 3.8 及以上版本。
    """
    votes = {
        "baguette": ["Bob", "Alice"],
        "ciabatta": ["Coco", "Deb"],
    }
    key = "brioche"
    who = "Elmer"

    if (names := votes.get(key)) is None:
        votes[key] = names = []
    names.append(who)
    logging.info("使用 `get` 和海象运算符的投票结果: %s", votes)

# 示例6: 错误示例 - 重用默认对象导致意外行为
def example_mistake_with_reused_default_value():
    """
    错误示例：在多个调用中复用同一个默认对象会导致意外行为。
    默认值直接插入到字典中而不是复制。
    """
    data = {}
    key = "foo"
    value = []  # 单个列表被多次复用

    data.setdefault(key, value)
    logging.info("初始数据: %s", data)

    value.append("hello")
    logging.warning("修改共享的默认值后: %s", data)  # 数据也被修改了！

# 示例7: 正确使用 `setdefault` - 每次创建新默认值
def example_correct_use_of_setdefault():
    """
    正确示例：每次调用时创建新的默认值以避免副作用。
    虽然性能略有影响，但确保了数据一致性。
    """
    data = {}
    key = "foo"

    # 每次都新建一个空列表
    data.setdefault(key, []).append("hello")
    logging.info("正确使用 `setdefault`: %s", data)

# 主函数 - 运行所有示例
def main():
    logging.info("开始运行示例...")

    logging.info("\n--- 示例1: 使用 `in` 操作符 ---")
    example_in_operator()

    logging.info("\n--- 示例2: 使用 `KeyError` 异常 ---")
    example_key_error()

    logging.info("\n--- 示例3: 使用 `get` 方法 ---")
    example_get_method()

    logging.info("\n--- 示例4: 使用 `setdefault` 方法处理列表 ---")
    example_setdefault_with_list()

    logging.info("\n--- 示例5: 使用 `get` 和海象运算符 ---")
    example_get_with_walrus_operator()

    logging.info("\n--- 示例6: 错误示例 - 复用默认值 ---")
    example_mistake_with_reused_default_value()

    logging.info("\n--- 示例7: 正确示例 - 每次创建新默认值 ---")
    example_correct_use_of_setdefault()

    logging.info("\n所有示例执行完毕。")

if __name__ == "__main__":
    main()
