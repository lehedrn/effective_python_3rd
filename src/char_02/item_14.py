"""
本文件演示了 Python 中列表切片操作的各种用法和注意事项。
覆盖了从基本的切片语法、边界处理、负数索引、赋值行为到错误示例等完整内容。
"""

# 基础切片示例
def basic_slicing_example():
    """
    展示基础的切片语法，包括 start:end 形式，
    以及省略 start 或 end 的情况。
    """
    a = ["a", "b", "c", "d", "e", "f", "g", "h"]
    print("Middle two: ", a[3:5])  # ['d', 'e']
    print("All but ends:", a[1:7])  # ['b', 'c', 'd', 'e', 'f', 'g']

    # 省略 start
    assert a[:5] == a[0:5]

    # 省略 end
    assert a[5:] == a[5:len(a)]

# 负数索引切片示例
def negative_index_slicing_example():
    """
    展示使用负数进行切片的情况，
    包括相对末尾的偏移和组合使用正负索引。
    """
    a = ["a", "b", "c", "d", "e", "f", "g", "h"]

    print("a[:]     ", a[:])      # 全部元素
    print("a[:5]    ", a[:5])     # 前5个元素
    print("a[:-1]   ", a[:-1])    # 除最后一个外的所有元素
    print("a[4:]    ", a[4:])     # 从第5个开始到最后一个
    print("a[-3:]   ", a[-3:])    # 最后三个元素
    print("a[2:5]   ", a[2:5])    # 第3到第5个元素（不包含第6个）
    print("a[2:-1]  ", a[2:-1])   # 第3到倒数第二个元素
    print("a[-3:-1] ", a[-3:-1])  # 倒数第三个到倒数第二个元素

# 边界超出范围的切片
def out_of_bounds_slicing_example():
    """
    展示如何处理超出列表边界的切片索引，
    切片不会抛出异常而是返回空或部分结果。
    """
    a = ["a", "b", "c", "d", "e", "f", "g", "h"]

    print("First 20 items:", a[:20])   # 不会报错，只返回全部
    print("Last 20 items: ", a[-20:])  # 不会报错，只返回全部

    try:
        print(a[20])
    except IndexError as e:
        print("Accessing index 20 directly raises an error:", str(e))

# 修改切片后的原列表不变
def slicing_does_not_modify_original_list_example():
    """
    展示对切片的修改不会影响原始列表，
    因为切片返回的是一个新的列表。
    """
    a = ["a", "b", "c", "d", "e", "f", "g", "h"]
    b = a[3:]
    print("Before: ", b)
    b[1] = 99
    print("After: ", b)
    print("No change:", a)

# 切片赋值替换原列表中的部分
def slice_assignment_example():
    """
    展示通过切片赋值来替换原列表中的一部分，
    可以改变列表长度（变长或变短）。
    """
    a = ["a", "b", "c", "d", "e", "f", "g", "h"]
    print("Before ", a)
    a[2:7] = [99, 22, 14]
    print("After (shrunk)", a)

    a = ["a", "b", "c", "d", "e", "f", "g", "h"]
    print("Before ", a)
    a[2:3] = [47, 11]
    print("After (grown) ", a)

# 完全复制列表
def copy_list_example():
    """
    展示如何通过切片 `[:]` 来复制整个列表，
    并验证新旧列表是两个不同的对象。
    """
    a = ["a", "b", "c", "d", "e", "f", "g", "h"]
    b = a[:]
    print("Original list:", a)
    print("Copied list:  ", b)
    assert b == a and b is not a

# 切片赋值替换整个列表内容
def slice_assignment_replace_entire_list_example():
    """
    展示如何通过切片赋值 `[:]` 来替换整个列表的内容，
    而不是创建新的列表对象。
    """
    a = ["a", "b", "c", "d", "e", "f", "g", "h"]
    b = a
    print("Before a", a)
    print("Before b", b)
    a[:] = [101, 102, 103]
    assert a is b  # 仍然是同一个对象
    print("After a ", a)
    print("After b ", b)

# 错误示例：负数索引导致意外行为
def negative_index_slice_mistake_example():
    """
    展示一个常见的错误：使用变量 n 进行负数切片时，
    当 n 为 0 时会导致 `somelist[-0:]` 等价于 `somelist[:]`。
    """
    a = ["a", "b", "c", "d", "e", "f", "g", "h"]
    n = 0
    print("When n=0, somelist[-n:] becomes somelist[:]", a[-n:])
    print("Which is equivalent to the full copy of the list.")

# 主函数运行所有示例
def main():
    print("=== Basic Slicing ===")
    basic_slicing_example()

    print("\n=== Negative Index Slicing ===")
    negative_index_slicing_example()

    print("\n=== Out-of-Bounds Slicing ===")
    out_of_bounds_slicing_example()

    print("\n=== Slicing Does Not Modify Original List ===")
    slicing_does_not_modify_original_list_example()

    print("\n=== Slice Assignment (Replace Part of List) ===")
    slice_assignment_example()

    print("\n=== Copy List with Slicing ===")
    copy_list_example()

    print("\n=== Replace Entire List Content via Slice Assignment ===")
    slice_assignment_replace_entire_list_example()

    print("\n=== Negative Index Slice Mistake Example ===")
    negative_index_slice_mistake_example()


if __name__ == "__main__":
    main()
