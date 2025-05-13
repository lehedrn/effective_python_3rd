"""
本文件演示了如何在Python中处理迭代器和容器对象的防御性编程技巧。
包括错误使用迭代器的问题、正确使用容器对象的方法，以及如何检测并避免传入迭代器。

包含以下示例：
1. 错误地使用生成器（迭代器）导致无结果。
2. 正确使用列表复制迭代器内容。
3. 使用函数返回新迭代器的方式。
4. 使用自定义可迭代容器类。
5. 检测输入是否为迭代器并抛出异常。
"""

from collections.abc import Iterator


# 示例 1: 错误地使用迭代器导致问题
def example_use_iterator_wrongly():
    """
    演示错误地使用迭代器导致无法正常工作的例子。
    `normalize` 函数在处理一个已经耗尽的迭代器时不会产生任何结果。
    """

    def normalize(numbers):
        total = sum(numbers)
        result = []
        for value in numbers:
            percent = 100 * value / total
            result.append(percent)
        return result

    def read_visits(data_path):
        with open(data_path) as f:
            for line in f:
                yield int(line)

    path = "my_numbers.txt"
    with open(path, "w") as f:
        for i in (15, 35, 80):
            f.write(f"{i}\n")

    it = read_visits(path)
    percentages = normalize(it)
    print("错误示例 - 使用迭代器导致空结果:", percentages)  # 输出空列表 []


# 示例 2: 正确使用列表复制迭代器内容
def example_normalize_with_copy():
    """
    演示通过将迭代器内容复制到列表中来确保多次遍历。
    这样可以保证 `sum` 和 `for` 循环都能看到完整数据。
    """

    def normalize_copy(numbers):
        numbers_copy = list(numbers)
        total = sum(numbers_copy)
        result = []
        for value in numbers_copy:
            percent = 100 * value / total
            result.append(percent)
        return result

    def read_visits(data_path):
        with open(data_path) as f:
            for line in f:
                yield int(line)

    path = "my_numbers.txt"
    it = read_visits(path)
    percentages = normalize_copy(it)
    print("正确示例 - 复制迭代器内容:", percentages)
    assert sum(percentages) == 100.0


# 示例 3: 使用函数返回新迭代器的方式
def example_normalize_with_func():
    """
    演示通过传递一个每次返回新迭代器的函数来实现多次遍历。
    避免一次性加载全部数据到内存中。
    """

    def normalize_func(get_iter):
        total = sum(get_iter())
        result = []
        for value in get_iter():
            percent = 100 * value / total
            result.append(percent)
        return result

    def read_visits(data_path):
        with open(data_path) as f:
            for line in f:
                yield int(line)

    path = "my_numbers.txt"
    percentages = normalize_func(lambda: read_visits(path))
    print("正确示例 - 使用函数返回新迭代器:", percentages)
    assert sum(percentages) == 100.0


# 示例 4: 使用自定义可迭代容器类
def example_normalize_with_container():
    """
    演示通过定义一个实现了 `__iter__` 方法的容器类来支持多次遍历。
    每次调用 `iter()` 都会返回一个新的迭代器对象。
    """

    class ReadVisits:
        def __init__(self, data_path):
            self.data_path = data_path

        def __iter__(self):
            with open(self.data_path) as f:
                for line in f:
                    yield int(line)

    def normalize(numbers):
        total = sum(numbers)
        result = []
        for value in numbers:
            percent = 100 * value / total
            result.append(percent)
        return result

    path = "my_numbers.txt"
    visits = ReadVisits(path)
    percentages = normalize(visits)
    print("正确示例 - 使用自定义可迭代容器类:", percentages)
    assert sum(percentages) == 100.0


# 示例 5: 检测输入是否为迭代器并抛出异常
def example_defensive_checking():
    """
    演示如何在函数中检测输入是否为迭代器，并主动拒绝此类输入。
    如果传入的是迭代器而非容器，函数会抛出 `TypeError`。
    """

    from collections.abc import Iterator

    def normalize_defensive(numbers):
        if isinstance(numbers, Iterator):  # 检查是否是迭代器
            raise TypeError("必须提供一个容器，而不是迭代器")
        total = sum(numbers)
        result = []
        for value in numbers:
            percent = 100 * value / total
            result.append(percent)
        return result

    def read_visits(data_path):
        with open(data_path) as f:
            for line in f:
                yield int(line)

    path = "my_numbers.txt"
    visits_list = [15, 35, 80]
    visits_gen = read_visits(path)

    print("正确示例 - 列表输入:", normalize_defensive(visits_list))

    try:
        normalize_defensive(visits_gen)
    except TypeError as e:
        print("预期错误 - 拒绝迭代器输入:", e)


# 主函数运行所有示例
def main():
    print("=== 示例 1: 错误使用迭代器 ===")
    example_use_iterator_wrongly()

    print("\n=== 示例 2: 正确复制迭代器内容 ===")
    example_normalize_with_copy()

    print("\n=== 示例 3: 使用函数返回新迭代器 ===")
    example_normalize_with_func()

    print("\n=== 示例 4: 使用自定义可迭代容器类 ===")
    example_normalize_with_container()

    print("\n=== 示例 5: 检测并拒绝迭代器输入 ===")
    example_defensive_checking()


if __name__ == "__main__":
    main()
