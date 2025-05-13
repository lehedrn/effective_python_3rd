"""
本模块演示了如何使用 Python 的 `zip` 函数并行处理迭代器，包括基本用法、长度不一致时的行为、以及如何使用 `strict` 参数和 `itertools.zip_longest` 来避免意外截断。

文档中涵盖了以下几点：
1. 使用 `zip` 来替代基于索引的循环，提高代码可读性。
2. 当输入迭代器长度不一致时，`zip` 会自动截断到最短长度。
3. 在 Python 3.10+ 中可以使用 `zip(..., strict=True)` 来防止静默截断。
4. 使用 `itertools.zip_longest` 填充缺失值来处理长度不一致的情况。

本文件包含错误示例和正确示例，并在 main() 函数中运行所有示例。
"""

from itertools import zip_longest


# 示例1：使用 zip 替代基于索引的循环（推荐做法）
def example_use_zip_instead_of_index():
    """
    使用 zip 替代手动通过索引访问多个列表中的元素，使代码更简洁易读。
    """
    names = ["Cecilia", "Lise", "Marie"]
    counts = [len(n) for n in names]

    longest_name = None
    max_count = 0

    # 使用 zip 并行遍历两个列表，无需手动索引
    for name, count in zip(names, counts):
        if count > max_count:
            longest_name = name
            max_count = count

    print("Example 1 - Longest name:", longest_name)


# 示例2：zip 截断行为（错误示例）
def example_zip_truncates_implicitly():
    """
    当传入不同长度的迭代器时，zip 会静默截断输出，只保留最短的长度。
    这可能导致遗漏数据，应特别注意。
    """
    names = ["Cecilia", "Lise", "Marie", "Rosalind"]
    counts = [7, 4, 5]  # 比 names 短一个元素

    print("Example 2 - Truncated output:")
    for name, count in zip(names, counts):
        print(name)


# 示例3：使用 zip(..., strict=True) 防止隐式截断（Python 3.10+）
def example_zip_with_strict_flag():
    """
    在 Python 3.10 及以上版本中，可以通过 `strict=True` 参数让 zip 在输入长度不一致时抛出异常。
    """
    names = ["Cecilia", "Lise", "Marie", "Rosalind"]
    counts = [7, 4, 5]  # 比 names 短一个元素

    try:
        print("Example 3 - Using zip with strict=True:")
        for name, count in zip(names, counts, strict=True):
            print(name)
    except ValueError as e:
        print("Caught error:", e)


# 示例4：使用 itertools.zip_longest 填充缺失项
def example_zip_longest_from_itertools():
    """
    如果你希望处理长度不一致的迭代器而不丢失任何数据，可以使用 itertools.zip_longest，
    它会填充缺失的值（默认为 None）。
    """
    names = ["Cecilia", "Lise", "Marie", "Rosalind"]
    counts = [7, 4, 5]

    print("Example 4 - Using zip_longest to fill missing values:")
    for name, count in zip_longest(names, counts):
        print(f"Name: {name}, Count: {count}")


# 主函数运行所有示例
def main():
    print("=== Example 1 ===")
    example_use_zip_instead_of_index()

    print("\n=== Example 2 ===")
    example_zip_truncates_implicitly()

    print("\n=== Example 3 ===")
    example_zip_with_strict_flag()

    print("\n=== Example 4 ===")
    example_zip_longest_from_itertools()


if __name__ == "__main__":
    main()
