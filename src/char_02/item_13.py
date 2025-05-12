"""
本文件演示 Python 中显式与隐式字符串连接的不同场景，
包括列表、元组、函数参数中的使用方式，以及推荐的最佳实践。
涵盖文档中提到的所有要点，提供错误示例与正确写法的对比。


"""

# ----------------------
# 示例1：基本隐式字符串连接
# ----------------------

def example_implicit_concatenation():
    """
    隐式字符串连接的基本用法：
    相邻字符串字面量会自动合并，无需 '+' 运算符。
    """
    s1 = "hello" "world"
    s2 = "hello" + "world"
    assert s1 == s2
    print("示例1 - 隐式字符串连接结果:", s1)


# ----------------------
# 示例2：在多行中使用不同类型字符串进行隐式连接（可读性强）
# ----------------------

def example_multiline_implicit_concatenation():
    """
    多行中使用不同类型字符串进行隐式连接（如 raw string, f-string）。
    此种方式提高可读性且不易出错。
    """
    x = 1
    message = (
        r"first \ part is here with escapes\n, "
        f"string interpolation {x} in here, "
        'this has "double quotes" inside'
    )
    print("示例2 - 多行隐式字符串连接:\n", message)


# ----------------------
# 示例3：单行隐式连接容易出错（不推荐）
# ----------------------

def example_single_line_implicit_concatenation():
    """
    单行中使用多个字符串字面量进行隐式连接。
    虽然有效，但可读性差，容易误解。
    """
    y = 2
    result = r"fir\st" f"{y}" '"third"'
    print("示例3 - 单行隐式连接结果:", result)


# ----------------------
# 示例4：误加逗号导致生成元组（错误示例）
# ----------------------

def example_mistaken_comma_in_strings():
    """
    在相邻字符串之间不小心插入逗号，会导致生成一个元组而非字符串。
    这是常见的语法错误。
    """
    y = 2
    value = r"fir\st", f"{y}" '"third"'  # 实际上是元组
    print("示例4 - 错误添加逗号导致元组:", value)


# ----------------------
# 示例5：列表中隐式连接导致意外合并（错误示例）
# ----------------------

def example_list_implicit_concatenation_error():
    """
    列表中删除逗号后，相邻字符串会被隐式连接，造成静默错误。
    推荐使用 '+' 显式连接以避免歧义。
    """
    my_test5 = [
        "first line\n",
        "second line\n"  # 删除了逗号
        "third line\n",
    ]
    print("示例5 - 列表中隐式连接导致合并:\n", repr(my_test5))


# ----------------------
# 示例6：列表中使用显式连接（推荐做法）
# ----------------------

def example_list_explicit_concatenation():
    """
    使用 '+' 显式连接字符串，即使格式化工具换行，也能明确表达作者意图。
    """
    my_test6 = [
        "first line\n",
        "second line\n" +  # 显式连接
        "third line\n",
    ]
    print("示例6 - 列表中显式连接结果:\n", repr(my_test6))


# ----------------------
# 示例7：函数调用中多个位置参数时隐式连接易混淆（错误示例）
# ----------------------

class MyData:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

def example_function_call_implicit_concatenation():
    """
    函数调用中多个位置参数时使用隐式字符串连接容易引起歧义。
    """
    x = 10
    y = 20
    value = MyData(123,
                   "first argument",
                   f"my format string {x}"
                   f"another value {y}",
                   "and more text",
                   stream="stdout")
    print("示例7 - 函数调用中隐式连接结果:\n", value.args)


# ----------------------
# 示例8：函数调用中显式连接提升可读性（推荐做法）
# ----------------------

def example_function_call_explicit_concatenation():
    """
    函数调用中多个位置参数时，使用 '+' 显式连接字符串可以增强可读性。
    """
    x = 10
    y = 20
    value = MyData(123,
                   "first argument",
                   f"my format string {x}" +
                   f"another value {y}",
                   "and more text",
                   stream="stdout")
    print("示例8 - 函数调用中显式连接结果:\n", value.args)


# ----------------------
# 主函数入口
# ----------------------

def main():
    print("=== 开始执行字符串连接示例 ===\n")

    example_implicit_concatenation()
    print()

    example_multiline_implicit_concatenation()
    print()

    example_single_line_implicit_concatenation()
    print()

    example_mistaken_comma_in_strings()
    print()

    example_list_implicit_concatenation_error()
    print()

    example_list_explicit_concatenation()
    print()

    example_function_call_implicit_concatenation()
    print()

    example_function_call_explicit_concatenation()
    print()

    print("=== 所有示例执行完毕 ===")


if __name__ == "__main__":
    main()
