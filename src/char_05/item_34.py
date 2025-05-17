"""
本文件展示了如何正确和错误地使用 `*args` 和生成器。
包括了函数接受可变数量的位置参数、使用 `*` 操作符、处理生成器可能导致内存问题的情况，
以及在添加新位置参数时的潜在问题。

示例包括：
1. 使用 `*args` 来减少视觉噪声。
2. 使用 `*` 操作符将序列作为位置参数传递给函数。
3. 与生成器一起使用 `*` 导致内存问题的示例。
4. 添加新的位置参数到已有 `*args` 函数中导致调用错误的示例。
"""

from typing import Generator


def log(message: str, *values: int) -> None:
    """
    记录日志信息，支持可变数量的位置参数。

    :param message: 日志消息。
    :param values: 可选的整数值列表。
    """
    if not values:
        print(message)
    else:
        values_str = ", ".join(str(x) for x in values)
        print(f"{message}: {values_str}")


def use_star_with_list() -> None:
    """
    正确使用 `*` 操作符将列表中的元素作为位置参数传递给函数。
    """
    favorites = [7, 33, 99]
    log("Favorite colors", *favorites)


def generator_example() -> None:
    """
    错误使用 `*` 操作符与生成器可能导致内存问题。
    """
    def my_generator() -> Generator[int, None, None]:
        for i in range(1000000):  # 假设这是一个非常大的生成器
            yield i

    def process(*args: int) -> None:
        print(f"Processed {len(args)} items.")

    gen = my_generator()
    try:
        # 注意：这会将整个生成器转换为元组，可能会占用大量内存！
        process(*gen)
    except MemoryError:
        print("内存不足，程序崩溃。")


def add_new_positional_arg() -> None:
    """
    错误示例：向已有 `*args` 的函数添加新的位置参数导致调用错误。
    """
    def log_seq(sequence: int, message: str, *values: int) -> None:
        if not values:
            print(f"{sequence} - {message}")
        else:
            values_str = ", ".join(str(x) for x in values)
            print(f"{sequence} - {message}: {values_str}")

    # 错误调用，没有提供 sequence 参数
    try:
        log_seq("Favorite numbers", 7, 33)  # 这里会导致类型错误
    except TypeError as e:
        print(f"TypeError: {e}")


def main() -> None:
    """
    主函数，运行所有示例。
    """
    print("=== 示例 1: 使用 *args ===")
    log("My numbers are", 1, 2)
    log("Hi there")

    print("\n=== 示例 2: 使用 * 操作符 ===")
    use_star_with_list()

    print("\n=== 示例 3: 与生成器一起使用 * 可能导致内存问题 ===")
    generator_example()

    print("\n=== 示例 4: 向已有 *args 函数添加新位置参数 ===")
    add_new_positional_arg()


if __name__ == "__main__":
    main()
