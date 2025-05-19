"""
本文件演示了如何使用生成器表达式处理大型列表推导式的问题。包括：
1. 列表推导式可能导致内存问题的示例。
2. 使用生成器表达式避免内存问题的正确示例。
3. 生成器表达式的组合使用。
4. 错误地重复使用生成器表达式的后果。
"""

import logging
import random

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def example_list_comprehension_memory_issue():
    """
    示例说明：列表推导式可能导致内存问题。

    该函数演示了当使用列表推导式处理大文件时，可能会导致内存占用过高的问题。
    """

    logging.info("开始示例: 列表推导式可能导致内存问题")

    # 创建一个测试文件
    with open("large_file.txt", "w") as f:
        for _ in range(10000):  # 模拟大量数据
            f.write("a" * random.randint(0, 100))
            f.write("\n")

    try:
        # 使用列表推导式读取文件内容
        value = [len(x) for x in open("large_file.txt")]
        logging.info(f"读取完成，共 {len(value)} 行，前5行长度为 {value[:5]}")
    except MemoryError:
        logging.error("内存不足，程序崩溃！")

    logging.info("结束示例: 列表推导式可能导致内存问题")


def example_generator_expression_correct_usage():
    """
    示例说明：使用生成器表达式避免内存问题。

    该函数演示了如何使用生成器表达式逐行读取文件内容，从而避免内存问题。
    """

    logging.info("开始示例: 使用生成器表达式避免内存问题")

    # 创建一个测试文件
    with open("large_file.txt", "w") as f:
        for _ in range(10000):  # 模拟大量数据
            f.write("a" * random.randint(0, 100))
            f.write("\n")

    # 使用生成器表达式逐行读取文件内容
    it = (len(x) for x in open("large_file.txt"))

    # 仅消费前10个元素以验证效果
    first_10_lengths = [next(it) for _ in range(10)]
    logging.info(f"读取完成，前10行长度为 {first_10_lengths}")

    logging.info("结束示例: 使用生成器表达式避免内存问题")


def example_generator_expression_composition():
    """
    示例说明：生成器表达式的组合使用。

    该函数演示了如何将多个生成器表达式组合在一起，形成一个处理链。
    """

    logging.info("开始示例: 生成器表达式的组合使用")

    # 创建一个测试文件
    with open("large_file.txt", "w") as f:
        for _ in range(10):  # 模拟少量数据以便观察输出
            f.write("a" * random.randint(0, 100))
            f.write("\n")

    # 第一层生成器表达式：计算每行的长度
    line_lengths = (len(x) for x in open("large_file.txt"))

    # 第二层生成器表达式：对第一层的结果进行平方根运算
    roots = ((x, x ** 0.5) for x in line_lengths)

    # 读取并打印前3个结果
    results = [next(roots) for _ in range(3)]
    logging.info(f"生成器组合处理结果（值，平方根）：{results}")

    logging.info("结束示例: 生成器表达式的组合使用")


def example_reusing_generator_incorrectly():
    """
    示例说明：错误地重复使用生成器表达式。

    该函数演示了错误地多次使用同一个生成器表达式的结果。
    """

    logging.info("开始示例: 错误地重复使用生成器表达式")

    # 创建一个测试文件
    with open("large_file.txt", "w") as f:
        for _ in range(1):
            f.write("a" * random.randint(0, 100))
            f.write("\n")

    # 定义生成器表达式
    it = (len(x) for x in open("large_file.txt"))

    # 第一次使用生成器表达式
    first_result = next(it)
    logging.info(f"第一次读取: {first_result}")

    # 尝试重新使用生成器表达式
    try:
        second_result = next(it)
        logging.info(f"第二次读取: {second_result}")
    except StopIteration:
        logging.warning("生成器已经耗尽，无法继续读取！")

    # 再次尝试使用同一个生成器
    try:
        third_result = next(it)
        logging.info(f"第三次读取: {third_result}")
    except StopIteration:
        logging.warning("生成器已经耗尽，无法继续读取！")

    logging.info("结束示例: 错误地重复使用生成器表达式")


def main():
    """
    主函数：运行所有示例。
    """

    logging.info("开始运行所有示例")

    logging.info("\n=== 示例 1: 列表推导式可能导致内存问题 ===")
    example_list_comprehension_memory_issue()

    logging.info("\n=== 示例 2: 使用生成器表达式避免内存问题 ===")
    example_generator_expression_correct_usage()

    logging.info("\n=== 示例 3: 生成器表达式的组合使用 ===")
    example_generator_expression_composition()

    logging.info("\n=== 示例 4: 错误地重复使用生成器表达式 ===")
    example_reusing_generator_incorrectly()

    logging.info("所有示例运行完毕")


if __name__ == "__main__":
    main()
