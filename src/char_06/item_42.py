"""
本文件演示了如何在 Python 推导式中使用赋值表达式（海象运算符 `:=`）来减少重复计算，并展示了错误示例与正确示例。

包含以下内容：
1. 使用推导式的常见问题：重复计算。
2. 使用赋值表达式解决重复问题。
3. 错误地在推导式中引用未定义的变量。
4. 正确地在条件中使用赋值表达式并在其他部分引用该变量。
5. 推导式中变量泄漏到外层作用域的行为。
6. 生成器表达式中的赋值表达式使用。
"""

import logging

# 配置日志输出，替代 print
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def example_duplicate_comprehension():
    """
    示例 1：推导式中的重复计算导致的问题。

    在字典推导式中，多次调用相同的函数 `get_batches()` 来判断和赋值，容易造成冗余计算和潜在的不一致。
    """

    stock = {
        "nails": 125,
        "screws": 35,
        "wingnuts": 8,
        "washers": 24,
    }
    order = ["screws", "wingnuts", "clips"]

    def get_batches(count, size):
        return count // size

    # 错误示例：重复调用 get_batches()
    found = {name: get_batches(stock.get(name, 0), 8)
             for name in order
             if get_batches(stock.get(name, 0), 8)}

    logging.info("重复调用示例结果：%s", found)


def example_walrus_operator_correct_usage():
    """
    示例 2：使用赋值表达式（海象运算符）避免重复计算。

    使用 `batches := get_batches(...)` 将计算结果存储在一个变量中，然后在推导式的多个地方引用它。
    """

    stock = {
        "nails": 125,
        "screws": 35,
        "wingnuts": 8,
        "washers": 24,
    }
    order = ["screws", "wingnuts", "clips"]

    def get_batches(count, size):
        return count // size

    # 正确示例：使用 walrus operator 避免重复调用
    found = {name: batches for name in order
             if (batches := get_batches(stock.get(name, 0), 8))}

    logging.info("使用 walrus operator 示例结果：%s", found)


def example_wrong_variable_reference_in_comprehension():
    """
    示例 3：错误地在推导式中引用赋值表达式定义的变量。

    在推导式的值表达式中提前使用赋值表达式定义的变量会导致运行时异常。
    """

    stock = {
        "nails": 125,
        "screws": 35,
        "wingnuts": 8,
        "washers": 24,
    }

    try:
        # 错误示例：在条件之外引用赋值表达式定义的变量
        result = {name: (tenth := count // 10)
                  for name, count in stock.items() if tenth > 0}
    except NameError as e:
        logging.error("错误引用赋值表达式变量异常：%s", str(e))


def example_correct_variable_reference_in_comprehension():
    """
    示例 4：正确在推导式中引用赋值表达式定义的变量。

    将赋值表达式放在条件中，并在值表达式中引用它。
    """

    stock = {
        "nails": 125,
        "screws": 35,
        "wingnuts": 8,
        "washers": 24,
    }

    # 正确示例：将赋值表达式放在条件中，并在值表达式中引用
    result = {name: tenth for name, count in stock.items()
              if (tenth := count // 10) > 0}

    logging.info("正确引用赋值表达式变量示例结果：%s", result)


def example_walrus_leakage_in_comprehension():
    """
    示例 5：推导式中赋值表达式变量泄露到外层作用域。

    赋值表达式定义的变量会泄露到外层作用域，这一点与普通循环类似。
    """

    stock = {
        "nails": 125,
        "screws": 35,
        "wingnuts": 8,
        "washers": 24,
    }

    # 示例：推导式中使用赋值表达式，变量 last 和 squared 泄露
    half = [(squared := last ** 2)
            for count in stock.values()
            if (last := count // 2) > 10]

    logging.info("推导式中赋值表达式变量泄露示例结果：half=%s, last=%s, squared=%s", half, last, squared)


def example_generator_expression_with_walrus():
    """
    示例 6：在生成器表达式中使用赋值表达式。

    类似于推导式，在生成器表达式中也可以使用 walrus 运算符。
    """

    stock = {
        "nails": 125,
        "screws": 35,
        "wingnuts": 8,
        "washers": 24,
    }
    order = ["screws", "wingnuts", "clips"]

    def get_batches(count, size):
        return count // size

    # 示例：在生成器表达式中使用 walrus operator
    found = ((name, batches) for name in order
             if (batches := get_batches(stock.get(name, 0), 8)))

    logging.info("生成器表达式中使用 walrus 示例结果：%s", next(found))
    logging.info("生成器表达式中使用 walrus 示例结果：%s", next(found))


def main():
    """主函数，依次运行所有示例。"""
    logging.info("开始运行示例...")

    example_duplicate_comprehension()
    example_walrus_operator_correct_usage()
    example_wrong_variable_reference_in_comprehension()
    example_correct_variable_reference_in_comprehension()
    example_walrus_leakage_in_comprehension()
    example_generator_expression_with_walrus()

    logging.info("所有示例执行完成。")


if __name__ == "__main__":
    main()
