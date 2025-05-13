"""
本文件演示了 Python 中 for 循环变量使用不当的问题以及如何正确处理。
包含以下内容：
- 循环结束后访问循环变量的风险
- 列表推导式中不会泄漏循环变量
- 处理循环未执行时的替代方案
"""

from typing import Optional


# 示例 1: 在循环结束后访问循环变量（不推荐）
def bad_use_of_loop_variable():
    """
    演示在循环结束后访问循环变量可能导致的问题。
    - 如果循环从未执行，变量 `i` 不会被定义，导致 NameError。
    - 如果循环正常执行，`i` 会保留最后一个值。
    """
    categories = ["Hydrogen", "Uranium", "Iron", "Other"]
    for i, name in enumerate(categories):
        if name == "Iron":
            break
    print(f"找到 Iron 的索引为 {i}")  # 正常情况下有效

    try:
        empty_list = []
        for i, name in enumerate(empty_list):
            if name == "Lithium":
                break
        print(f"未找到 Lithium，归类到 Other (index {i})")  # 报错：i 未定义
    except NameError as e:
        print(f"[错误] 循环未执行，循环变量 i 未定义: {e}")


# 示例 2: 使用列表推导式不会泄漏循环变量（推荐方式之一）
def no_leak_in_comprehensions():
    """
    列表推导式中的变量不会泄漏到外部作用域。
    - 尝试访问推导式内部变量会引发 NameError。
    """
    my_numbers = [37, 13, 128, 21]
    found = [i for i in my_numbers if i % 2 == 0]
    try:
        print(i)  # 错误：i 不在当前作用域中
    except NameError as e:
        print(f"[错误] 推导式中的变量 i 不会泄漏: {e}")


# 示例 3: 安全地处理循环未执行的情况（推荐方式）
def safe_handling_loop_variable():
    """
    安全地处理循环变量，确保即使循环未执行也能有默认值。
    - 使用一个初始值为 None 的变量，在循环中更新它。
    - 最后检查变量是否被赋值。
    """
    categories = ["Hydrogen", "Uranium", "Iron", "Other"]
    index: Optional[int] = None
    for i, name in enumerate(categories):
        if name == "Iron":
            index = i
            break
    if index is not None:
        print(f"找到 Iron 的索引为 {index}")
    else:
        print("未找到 Iron，归类到 Other")

    categories_empty = []
    index: Optional[int] = None
    for i, name in enumerate(categories_empty):
        if name == "Lithium":
            index = i
            break
    if index is not None:
        print(f"找到 Lithium 的索引为 {index}")
    else:
        print("未找到 Lithium，归类到 Other")


# 示例 4: 使用 else 子句避免循环变量问题（推荐方式）
def use_else_clause():
    """
    使用 for-else 结构来区分循环是否找到了目标项。
    - 如果循环中 break，则不会执行 else 块。
    - 如果循环正常结束，则执行 else 块。
    """
    categories = ["Hydrogen", "Uranium", "Iron", "Other"]
    for i, name in enumerate(categories):
        if name == "Iron":
            print(f"找到 Iron 的索引为 {i}")
            break
    else:
        print("未找到 Iron，归类到 Other")

    categories_empty = []
    for i, name in enumerate(categories_empty):
        if name == "Lithium":
            print(f"找到 Lithium 的索引为 {i}")
            break
    else:
        print("未找到 Lithium，归类到 Other")


# 主函数：运行所有示例
def main():
    print("\n=== 示例 1: 在循环结束后访问循环变量 ===")
    bad_use_of_loop_variable()

    print("\n=== 示例 2: 列表推导式不会泄漏循环变量 ===")
    no_leak_in_comprehensions()

    print("\n=== 示例 3: 安全地处理循环变量不存在的情况 ===")
    safe_handling_loop_variable()

    print("\n=== 示例 4: 使用 for-else 来避免循环变量问题 ===")
    use_else_clause()


if __name__ == "__main__":
    main()
