"""
本文件展示了 Python 中 for/while 循环后使用 else 块的行为，以及推荐的替代写法。
包含错误示例和正确示例，并通过函数封装每个示例进行演示。

主要内容包括：
1. for 循环后使用 else 块的基本行为
2. break 语句影响 else 块的执行
3. 遍历空序列时 else 块立即执行
4. while 循环中 else 块的行为
5. 使用 else 块判断两个数是否互质（不推荐用法）
6. 推荐的替代方案：提前 return 和 使用状态变量
"""

# 示例 1: for 循环后使用 else 块的基本行为
def example_for_else_basic():
    """
    演示 for 循环后使用 else 块的基本行为。
    当循环正常结束时，else 块会执行。
    """
    print("示例 1: for 循环后使用 else 块的基本行为")
    for i in range(3):
        print("Loop", i)
    else:
        print("Else block!")
    print("-" * 50)

# 示例 2: break 语句影响 else 块的执行
def example_break_skips_else():
    """
    演示在循环中使用 break 会跳过 else 块。
    """
    print("示例 2: break 语句影响 else 块的执行")
    for i in range(3):
        print("Loop", i)
        if i == 1:
            break
    else:
        print("Else block!")
    print("-" * 50)

# 示例 3: 遍历空序列时 else 块立即执行
def example_empty_sequence():
    """
    演示遍历空序列时，else 块会立即执行。
    """
    print("示例 3: 遍历空序列时 else 块立即执行")
    for x in []:
        print("Never runs")
    else:
        print("For else block!")
    print("-" * 50)

# 示例 4: while 循环中 else 块的行为
def example_while_else():
    """
    演示 while 循环中 else 块的行为。
    当循环条件一开始就不满足时，else 块会执行。
    """
    print("示例 4: while 循环中 else 块的行为")
    while False:
        print("Never runs")
    else:
        print("While else block!")
    print("-" * 50)

# 示例 5: 使用 else 块判断两个数是否互质（不推荐用法）
def example_coprime_with_else():
    """
    演示使用 else 块判断两个数是否互质（不推荐用法）。
    如果循环中没有遇到 break，则执行 else 块表示互质。
    """
    print("示例 5: 使用 else 块判断两个数是否互质（不推荐）")
    a = 4
    b = 9

    for i in range(2, min(a, b) + 1):
        print("Testing", i)
        if a % i == 0 and b % i == 0:
            print("Not coprime")
            break
    else:
        print("Coprime")
    print("-" * 50)

# 示例 6: 推荐的替代方案 - 提前 return
def coprime(a, b):
    """
    判断两个数是否互质（推荐方式一：提前 return）。

    参数:
    a (int): 第一个整数
    b (int): 第二个整数

    返回:
    bool: 如果 a 和 b 互质返回 True，否则返回 False
    """
    for i in range(2, min(a, b) + 1):
        if a % i == 0 and b % i == 0:
            return False
    return True

def example_coprime_early_return():
    """
    演示推荐的互质判断方式：提前 return。
    """
    print("示例 6: 推荐的互质判断方式 - 提前 return")
    assert coprime(4, 9)
    assert not coprime(3, 6)
    print(f"4 和 9 是否互质: {coprime(4, 9)}")
    print(f"3 和 6 是否互质: {coprime(3, 6)}")
    print("-" * 50)

# 示例 7: 推荐的替代方案 - 使用状态变量
def coprime_alternate(a, b):
    """
    判断两个数是否互质（推荐方式二：使用状态变量）。

    参数:
    a (int): 第一个整数
    b (int): 第二个整数

    返回:
    bool: 如果 a 和 b 互质返回 True，否则返回 False
    """
    is_coprime = True
    for i in range(2, min(a, b) + 1):
        if a % i == 0 and b % i == 0:
            is_coprime = False
            break
    return is_coprime

def example_coprime_flag_variable():
    """
    演示推荐的互质判断方式：使用状态变量。
    """
    print("示例 7: 推荐的互质判断方式 - 使用状态变量")
    assert coprime_alternate(4, 9)
    assert not coprime_alternate(3, 6)
    print(f"4 和 9 是否互质: {coprime_alternate(4, 9)}")
    print(f"3 和 6 是否互质: {coprime_alternate(3, 6)}")
    print("-" * 50)

# 主函数，运行所有示例
def main():
    example_for_else_basic()
    example_break_skips_else()
    example_empty_sequence()
    example_while_else()
    example_coprime_with_else()
    example_coprime_early_return()
    example_coprime_flag_variable()

# 程序入口
if __name__ == "__main__":
    main()
