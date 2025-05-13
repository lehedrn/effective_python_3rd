"""
本文件演示了为什么应该优先使用 enumerate 而不是 range 的原因，并展示了直接遍历列表、使用 range 获取索引以及使用 enumerate 的正确方法。
包括错误示例和正确示例，每个示例封装在一个函数中，并在 main 函数中运行。

1. generate_32bit_random_number
- 展示了 range 的合理使用场景：仅需要一组数字作为索引时。
- 使用按位或 |= 和左移 << 构建 32 位二进制数。
2. iterate_directly_over_list
- 当你不需要索引时，直接遍历是最简洁的方式。
3. iterate_with_range_and_index_bad_example
- 展示了不推荐的做法：通过 range(len(...)) 手动获取索引。
- 该方式代码冗长，容易出错（比如忘记处理边界情况）。
4. iterate_with_enumerate_good_example
- 推荐做法：使用 enumerate 同时获取索引和值。
- 更加 Pythonic，可读性强。
5. iterate_with_enumerate_starting_from_1
- 展示了 enumerate(iterable, start) 的高级用法。
- 避免了手动 i + 1，使代码更简洁清晰。
"""

from random import randint


def generate_32bit_random_number():
    """
    使用 `range` 生成一个 32 位的随机整数。
    这是一个清晰的 `range` 应用场景，因为我们只需要一组索引，而不需要遍历具体的数据结构。
    """
    random_bits = 0
    for i in range(32):
        if randint(0, 1):
            random_bits |= 1 << i
    print(f"Generated 32-bit random number: {random_bits}")
    print(f"Binary representation: {bin(random_bits)}")


def iterate_directly_over_list():
    """
    直接遍历列表元素，不需要索引的情况。
    """
    flavor_list = ["vanilla", "chocolate", "pecan", "strawberry"]
    print("Iterating directly over list:")
    for flavor in flavor_list:
        print(f"{flavor} is delicious")


def iterate_with_range_and_index_bad_example():
    """
    错误示例：使用 range(len(...)) 来获取索引，这种方式虽然有效，但代码不够简洁且容易出错。
    """
    flavor_list = ["vanilla", "chocolate", "pecan", "strawberry"]
    print("Bad example - iterating with range(len(...)):")
    for i in range(len(flavor_list)):
        flavor = flavor_list[i]
        print(f"{i + 1}: {flavor}")


def iterate_with_enumerate_good_example():
    """
    正确示例：使用 enumerate 遍历列表并同时获取索引和值，更清晰且不易出错。
    """
    flavor_list = ["vanilla", "chocolate", "pecan", "strawberry"]
    print("Good example - iterating with enumerate:")
    for i, flavor in enumerate(flavor_list):
        print(f"{i + 1}: {flavor}")


def iterate_with_enumerate_starting_from_1():
    """
    更进一步：使用 enumerate 并指定起始计数值为 1，避免手动加一操作。
    """
    flavor_list = ["vanilla", "chocolate", "pecan", "strawberry"]
    print("Using enumerate with start=1 to avoid manual i+1:")
    for i, flavor in enumerate(flavor_list, 1):
        print(f"{i}: {flavor}")


def main():
    """
    主函数，运行所有示例函数以展示不同遍历方式的效果。
    """
    print("=== 示例 1: 使用 range 生成 32 位随机数 ===")
    generate_32bit_random_number()

    print("\n=== 示例 2: 直接遍历列表元素（无需索引） ===")
    iterate_directly_over_list()

    print("\n=== 示例 3: 错误地使用 range(len(...)) 获取索引 ===")
    iterate_with_range_and_index_bad_example()

    print("\n=== 示例 4: 正确使用 enumerate 获取索引和值 ===")
    iterate_with_enumerate_good_example()

    print("\n=== 示例 5: 使用 enumerate 并指定起始计数值 ===")
    iterate_with_enumerate_starting_from_1()


if __name__ == "__main__":
    main()
