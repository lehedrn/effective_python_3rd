"""
本文件演示了 Python 中 `str` 和 `repr` 的区别，以及如何在调试中使用它们。
- 展示了 `print`, `str`, `repr` 在不同数据类型上的行为。
- 提供了用户自定义类时如何实现 `__repr__` 和 `__str__` 的示例。
- 包含错误示例和正确示例，并通过函数组织代码以展示完整用法。

每个示例都封装在单独的函数中，main 函数运行所有示例。
"""

# 示例 1: 基础类型 str 和 repr 的对比
def example_basic_str_repr():
    """
    展示基础类型（如字符串、整数）的 str 和 repr 差异。
    - `str()` 返回人类可读的字符串。
    - `repr()` 返回可解析的字符串表示，适合调试。
    """
    s = "hello"
    i = 5

    print("example_basic_str_repr 输出：")
    print(f"str(s): {str(s)}")
    print(f"repr(s): {repr(s)}")
    print(f"str(i): {str(i)}")
    print(f"repr(i): {repr(i)}")


# 示例 2: 使用 f-string 和 % 格式化输出 str 和 repr
def example_formatting_str_repr():
    """
    展示 f-string 和 % 运算符如何控制 str 和 repr 输出。
    - `%s` 或 `{}` 表达式调用 `str()`
    - `%r` 或 `{!r}` 表达式调用 `repr()`
    """
    value = "test"

    print("example_formatting_str_repr 输出：")
    print("Using %%s: %s" % value)
    print("Using %%r: %r" % value)
    print(f"Using {{}}: {value}")
    print(f"Using {{!r}}: {value!r}")


# 示例 3: 默认情况下自定义类的 str 和 repr 输出
class DefaultClass:
    """
    没有定义 __str__ 或 __repr__ 的类将使用 object 的默认实现。
    输出不具信息性，无法用于重建对象。
    """

    def __init__(self, x, y):
        self.x = x
        self.y = y


def example_default_class_output():
    obj = DefaultClass(3, "abc")
    print("example_default_class_output 输出：")
    print("str(obj):", str(obj))
    print("repr(obj):", repr(obj))


# 示例 4: 自定义 __repr__ 实现以支持调试
class CustomReprClass:
    """
    定义 __repr__ 来返回可用于调试的字符串。
    如果未定义 __str__，则 __repr__ 也会被用作 str 的结果。
    """

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"CustomReprClass(x={self.x!r}, y={self.y!r})"


def example_custom_repr():
    obj = CustomReprClass(4, "xyz")
    print("example_custom_repr 输出：")
    print("repr(obj):", repr(obj))
    print("str(obj):", str(obj))


# 示例 5: 同时定义 __str__ 和 __repr__
class CustomStrAndReprClass:
    """
    定义 __str__ 用于 UI 显示，定义 __repr__ 用于调试。
    """

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"CustomStrAndReprClass(x={self.x!r}, y={self.y!r})"

    def __str__(self):
        return f"({self.x}, {self.y})"


def example_custom_str_and_repr():
    obj = CustomStrAndReprClass(5, "ui_string")
    print("example_custom_str_and_repr 输出：")
    print("str(obj):", str(obj))
    print("repr(obj):", repr(obj))


# 错误示例：没有 __repr__ 导致调试困难
class NoReprClass:
    def __init__(self, name):
        self.name = name


def bad_example_no_repr_for_debugging():
    obj = NoReprClass("Alice")
    print("bad_example_no_repr_for_debugging 输出：")
    print("Without __repr__, debugging is hard:")
    print("repr(obj):", repr(obj))  # 输出无意义信息，不利于调试


# 正确示例：为调试提供清晰的 __repr__
class GoodReprForDebugging:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"GoodReprForDebugging(name={self.name!r})"


def good_example_with_repr_for_debugging():
    obj = GoodReprForDebugging("Bob")
    print("good_example_with_repr_for_debugging 输出：")
    print("repr(obj):", repr(obj))  # 清晰地显示对象状态


# 主函数统一调用所有示例
def main():
    print("=== 示例 1: 基础类型 str 和 repr ===")
    example_basic_str_repr()

    print("\n=== 示例 2: 使用 f-string 和 % 格式化输出 ===")
    example_formatting_str_repr()

    print("\n=== 示例 3: 默认情况下自定义类的 str 和 repr ===")
    example_default_class_output()

    print("\n=== 示例 4: 自定义 __repr__ 实现以支持调试 ===")
    example_custom_repr()

    print("\n=== 示例 5: 同时定义 __str__ 和 __repr__ ===")
    example_custom_str_and_repr()

    print("\n=== 错误示例：没有 __repr__ 导致调试困难 ===")
    bad_example_no_repr_for_debugging()

    print("\n=== 正确示例：为调试提供清晰的 __repr__ ===")
    good_example_with_repr_for_debugging()


if __name__ == "__main__":
    main()
