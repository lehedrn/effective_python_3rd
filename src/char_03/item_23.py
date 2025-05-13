"""
本模块演示了如何高效地使用 Python 的内置函数 `any` 和 `all` 来处理逻辑判断。
这些函数在与迭代器结合使用时，能够实现短路逻辑，从而提升性能。

主要涵盖以下内容：
- 使用 `all` 检查所有条件是否为真（Truthy）
- 使用 `any` 检查是否存在任意一个真值
- 对比列表推导式和生成器表达式的性能差异
- 展示错误的写法（如使用列表推导式）与正确的写法（如使用生成器表达式）
- 通过日志记录输出结果，避免使用 `print`
"""

import random
import logging

# 配置日志系统
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 定义硬币翻转函数
def flip_coin():
    """返回随机的硬币翻转结果：'Heads' 或 'Tails'"""
    return "Heads" if random.randint(0, 1) == 0 else "Tails"

def flip_is_heads():
    """检查硬币是否为正面"""
    return flip_coin() == "Heads"

def flip_is_tails():
    """检查硬币是否为反面"""
    return flip_coin() == "Tails"


# 示例 1: 错误使用 all + 列表推导式
def example_1_wrong_all_with_list_comprehension():
    """
    错误示例：使用 all 与列表推导式。
    问题：列表推导式会预先计算所有项，导致不必要的开销。
    """
    result = all([flip_is_heads() for _ in range(20)])
    logging.info("Example 1 - All Heads (Wrong with list): %s", result)


# 示例 2: 正确使用 all + 生成器表达式
def example_2_correct_all_with_generator_expression():
    """
    正确示例：使用 all 与生成器表达式。
    优势：一旦遇到 False，立即终止，节省资源。
    """
    result = all(flip_is_heads() for _ in range(20))
    logging.info("Example 2 - All Heads (Correct with generator): %s", result)


# 示例 3: 错误使用 any + 列表推导式
def example_3_wrong_any_with_list_comprehension():
    """
    错误示例：使用 any 与列表推导式。
    问题：列表推导式会预先计算所有项，浪费资源。
    """
    result = not any([flip_is_tails() for _ in range(20)])
    logging.info("Example 3 - All Heads (Wrong with list): %s", result)


# 示例 4: 正确使用 any + 生成器表达式
def example_4_correct_any_with_generator_expression():
    """
    正确示例：使用 any 与生成器表达式。
    优势：一旦遇到 True（即出现 Tails），立即终止。
    """
    result = not any(flip_is_tails() for _ in range(20))
    logging.info("Example 4 - All Heads (Correct with generator): %s", result)


# 示例 5: 使用显式循环来实现 all 的功能
def example_5_explicit_loop_for_all():
    """
    显式循环实现 all 功能。
    虽然效率高，但代码冗长且不够简洁。
    """
    all_heads = True
    for _ in range(20):
        if not flip_is_heads():
            all_heads = False
            break
    logging.info("Example 5 - All Heads (Explicit loop): %s", all_heads)


# 示例 6: 使用生成器函数替代生成器表达式
def repeated_is_heads(count):
    """
    生成器函数，用于产生 flip_is_heads 的结果。
    """
    for _ in range(count):
        yield flip_is_heads()

def example_6_generator_function_with_all():
    """
    使用生成器函数配合 all 实现高效逻辑。
    """
    result = all(repeated_is_heads(20))
    logging.info("Example 6 - All Heads (Generator function): %s", result)


# 示例 7: 使用生成器函数替代 any 的生成器表达式
def repeated_is_tails(count):
    """
    生成器函数，用于产生 flip_is_tails 的结果。
    """
    for _ in range(count):
        yield flip_is_tails()

def example_7_generator_function_with_any():
    """
    使用生成器函数配合 any 实现高效逻辑。
    """
    result = not any(repeated_is_tails(20))
    logging.info("Example 7 - All Heads (Generator function with any): %s", result)


# 主函数运行所有示例
def main():
    logging.info("Starting examples...")

    # 运行错误示例
    example_1_wrong_all_with_list_comprehension()
    example_3_wrong_any_with_list_comprehension()

    # 运行正确示例
    example_2_correct_all_with_generator_expression()
    example_4_correct_any_with_generator_expression()
    example_5_explicit_loop_for_all()
    example_6_generator_function_with_all()
    example_7_generator_function_with_any()

    logging.info("All examples completed.")


if __name__ == "__main__":
    main()
