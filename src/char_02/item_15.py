"""
本文件演示了如何正确使用Python中的切片和步长操作，以避免在单个表达式中同时使用起始、结束和步长导致的易混淆行为。
涵盖了基本用法、错误示例、推荐写法以及itertools.islice替代方案。
"""

from itertools import islice


# 示例1：基础步长切片（正步长）
def example_positive_stride():
    """
    使用正步长进行切片，选择偶数索引和奇数索引元素。
    """
    x = ["red", "orange", "yellow", "green", "blue", "purple"]
    odds = x[::2]    # 取第0, 2, 4项
    evens = x[1::2]  # 取第1, 3, 5项
    print("Example 1 - Positive stride:")
    print("Odds:", odds)
    print("Evens:", evens)


# 示例2：负步长反转序列（适用于bytes和str）
def example_negative_stride_reverse():
    """
    使用负步长反转byte字符串和Unicode字符串。
    """
    byte_str = b"mongoose"
    reversed_byte = byte_str[::-1]
    unicode_str = "你好世界"
    reversed_unicode = unicode_str[::-1]
    print("Example 2 - Negative stride for reversing:")
    print("Reversed bytes:", reversed_byte)
    print("Reversed Unicode:", reversed_unicode)


# 示例3：错误示例 - 对编码后的字节串使用负步长反转
def example_error_invalid_utf8_decode():
    """
    错误示例：对UTF-8编码后的字符串进行负步长反转再解码会导致错误。
    """
    try:
        w = "你好世界"
        x = w.encode("utf-8")  # 编码为UTF-8字节串
        y = x[::-1]            # 反转字节顺序
        z = y.decode("utf-8")  # 这里会抛出异常
    except UnicodeDecodeError as e:
        print("Example 3 - Error on UTF-8 decode after reverse:")
        print("Caught error:", e)


# 示例4：不同组合的切片与步长
def example_various_combinations():
    """
    展示多种组合形式的切片+步长操作。
    """
    x = ["a", "b", "c", "d", "e", "f", "g", "h"]
    print("Example 4 - Various combinations of slicing and striding:")
    print("x[::2] ->", x[::2])       # 每隔一个取一个
    print("x[::-2] ->", x[::-2])     # 倒序每隔一个取一个
    print("x[2::2] ->", x[2::2])     # 从索引2开始每隔一个取一个
    print("x[-2::-2] ->", x[-2::-2]) # 从倒数第二个开始向前每隔一个取一个
    print("x[-2:2:-2] ->", x[-2:2:-2]) # 从倒数第二个到索引2之间每隔一个取一个
    print("x[2:2:-2] ->", x[2:2:-2]) # 无效区间，返回空列表


# 示例5：推荐做法 - 分两步操作（先步长后切片）
def example_preferred_two_steps():
    """
    推荐写法：将步长和切片分开两步执行，提升可读性。
    """
    x = ["a", "b", "c", "d", "e", "f", "g", "h"]
    step_one = x[::2]         # 第一步：获取每隔一个元素
    step_two = step_one[1:-1] # 第二步：去掉首尾
    print("Example 5 - Preferred two-steps approach:")
    print("Step one (strided):", step_one)
    print("Step two (sliced):", step_two)


# 示例6：使用itertools.islice避免多重索引问题
def example_use_itertools_islice():
    """
    推荐写法：使用itertools.islice处理复杂的迭代器切片逻辑。
    """
    from itertools import islice

    x = ["a", "b", "c", "d", "e", "f", "g", "h"]
    result = list(islice(x, 1, None, 2))  # start=1, stop=None, step=2
    print("Example 6 - Using itertools.islice:")
    print("islice result:", result)


# 主函数运行所有示例
def main():
    print("Running Example 1:")
    example_positive_stride()
    print("\nRunning Example 2:")
    example_negative_stride_reverse()
    print("\nRunning Example 3:")
    example_error_invalid_utf8_decode()
    print("\nRunning Example 4:")
    example_various_combinations()
    print("\nRunning Example 5:")
    example_preferred_two_steps()
    print("\nRunning Example 6:")
    example_use_itertools_islice()


if __name__ == "__main__":
    main()
