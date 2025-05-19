"""
本模块演示了 Python 中使用函数作为接口的优势，以及如何通过 `__call__` 方法让类的实例表现得像函数一样。
同时展示了错误和正确的实现方式，并解释了它们在不同场景下的用途。

涵盖知识点：
- 使用函数作为回调钩子（hook）进行行为定制
- 有状态闭包与无状态函数的区别
- 使用类封装状态并通过 `__call__` 提供函数式接口

"""

import logging
from collections import defaultdict

# 配置 logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# 示例1：使用无状态函数作为钩子（正确示例）
def example_hook_with_function():
    """
    正确示例：使用无状态函数作为 defaultdict 的钩子。
    当访问缺失键时打印日志并返回默认值 0。
    """

    def log_missing():
        logging.info("Key added")
        return 0

    current = {"green": 12, "blue": 3}
    increments = [
        ("red", 5),
        ("blue", 17),
        ("orange", 9),
    ]

    result = defaultdict(log_missing, current)
    logging.info("Before: %s", dict(result))
    for key, amount in increments:
        result[key] += amount
    logging.info("After: %s", dict(result))


# 示例2：使用有状态闭包（正确示例）
def example_hook_with_closure():
    """
    正确示例：使用有状态闭包来跟踪缺失键的数量。
    """

    def increment_with_report(current, increments):
        added_count = 0

        def missing():
            nonlocal added_count
            added_count += 1
            return 0

        result = defaultdict(missing, current)
        for key, amount in increments:
            result[key] += amount
        return result, added_count

    current = {"green": 12, "blue": 3}
    increments = [
        ("red", 5),
        ("blue", 17),
        ("orange", 9),
    ]

    result, count = increment_with_report(current, increments)
    logging.info("After closure-based hook: %s", dict(result))
    logging.info("Number of keys added: %d", count)


# 示例3：使用类封装状态（正确示例）
def example_hook_with_class_method():
    """
    正确示例：使用类方法作为钩子，通过类封装状态。
    """

    class CountMissing:
        def __init__(self):
            self.added = 0

        def missing(self):
            self.added += 1
            return 0

    current = {"green": 12, "blue": 3}
    increments = [
        ("red", 5),
        ("blue", 17),
        ("orange", 9),
    ]

    counter = CountMissing()
    result = defaultdict(counter.missing, current)
    for key, amount in increments:
        result[key] += amount
    logging.info("After method-based hook: %s", dict(result))
    logging.info("Number of keys added: %d", counter.added)


# 示例4：使用 __call__ 方法使类实例可调用（最佳实践）
def example_hook_with_callable_class():
    """
    最佳示例：通过定义 __call__ 方法，使类实例可以直接作为钩子传入 defaultdict。
    这种方式更清晰地表达了类的主要用途。
    """

    class BetterCountMissing:
        def __init__(self):
            self.added = 0

        def __call__(self):
            self.added += 1
            return 0

    current = {"green": 12, "blue": 3}
    increments = [
        ("red", 5),
        ("blue", 17),
        ("orange", 9),
    ]

    counter = BetterCountMissing()
    result = defaultdict(counter, current)  # 利用 __call__
    for key, amount in increments:
        result[key] += amount
    logging.info("After callable class-based hook: %s", dict(result))
    logging.info("Number of keys added: %d", counter.added)


# 错误示例：不恰当使用类导致钩子逻辑复杂化
def example_incorrect_usage():
    """
    错误示例：错误地将类用于简单钩子逻辑，导致代码难以维护。
    在这里，我们试图手动模拟 defaultdict 的行为，而没有利用其内置机制。
    """

    class BadCounter:
        def __init__(self):
            self.added = 0

        def manual_missing(self, key):
            self.added += 1
            return 0

    current = {"green": 12, "blue": 3}
    increments = [
        ("red", 5),
        ("blue", 17),
        ("orange", 9),
    ]

    counter = BadCounter()
    result = dict(current)

    for key, amount in increments:
        try:
            result[key] += amount
        except KeyError:
            result[key] = amount + counter.manual_missing(key)

    logging.info("After incorrect usage (manual logic): %s", result)
    logging.warning("This approach does not scale and is error-prone.")


# 主函数，运行所有示例
def main():
    logging.info("示例1：使用无状态函数作为钩子")
    example_hook_with_function()

    logging.info("\n示例2：使用有状态闭包作为钩子")
    example_hook_with_closure()

    logging.info("\n示例3：使用类方法作为钩子")
    example_hook_with_class_method()

    logging.info("\n示例4：使用 __call__ 方法使类实例可调用")
    example_hook_with_callable_class()

    logging.info("\n错误示例：错误地使用类导致钩子逻辑复杂化")
    example_incorrect_usage()


if __name__ == "__main__":
    main()
