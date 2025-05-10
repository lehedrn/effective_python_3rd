"""
本文件展示了 Python 中条件表达式（Conditional Expressions）的使用方法、注意事项以及与传统 if 语句的对比。
涵盖了以下内容：
- 条件表达式的基本语法
- 条件表达式与三元运算符的区别
- 列表推导式中的类似行为
- 布尔逻辑替代方案的局限性
- 多行条件表达式的可读性问题
- 条件表达式与赋值表达式（:=）的结合使用
- 推荐使用标准 if 语句的情况
"""

# 1. 基本条件表达式示例
def example_basic_conditional():
    i = 3
    x = "even" if i % 2 == 0 else "odd"
    print(f"[example_basic_conditional] i={i}, x={x}")

# 2. 条件为 False 时不会执行右边的表达式（与 C 的三元运算符不同）
def example_lazy_evaluation():
    def fail():
        raise Exception("Oops")

    x = fail() if False else 20
    print(f"[example_lazy_evaluation] x={x}")

# 3. 在列表推导式中的类似结构
def example_list_comprehension_with_condition():
    result = [x / 4 for x in range(10) if x % 2 == 0]
    print(f"[example_list_comprehension_with_condition] result={result}")

# 4. 使用布尔逻辑模拟条件表达式（不推荐）
def example_boolean_logic_trick():
    i = 3
    x = (i % 2 == 0 and "even") or "odd"
    print(f"[example_boolean_logic_trick] i={i}, x={x}")

# 5. 错误示例：布尔逻辑无法返回假值
def example_boolean_logic_bug():
    i = 2
    # 想要返回空列表当 i 是偶数时，但实际总是返回 [1]
    x = (i % 2 == 0 and []) or [1]
    print(f"[example_boolean_logic_bug] i={i}, x={x}")

# 6. 使用标准 if/else 更清晰
def example_standard_if_else():
    i = 3
    if i % 2 == 0:
        x = "even"
    else:
        x = "odd"
    print(f"[example_standard_if_else] i={i}, x={x}")

# 7. 可扩展的标准 if/else（支持添加调试输出等）
def example_extended_if_else():
    i = 4
    if i % 2 == 0:
        x = "even"
        print("It was even!")
    else:
        x = "odd"
    print(f"[example_extended_if_else] i={i}, x={x}")

# 8. 支持 elif 分支
def example_elif_in_if_statement():
    i = 9
    if i % 2 == 0:
        x = "even"
    elif i % 3 == 0:
        x = "divisible by three"
    else:
        x = "odd"
    print(f"[example_elif_in_if_statement] i={i}, x={x}")

# 9. 将逻辑封装到辅助函数中以便复用
def number_group(i):
    if i % 2 == 0:
        return "even"
    else:
        return "odd"

def example_helper_function():
    i = 5
    x = number_group(i)
    print(f"[example_helper_function] i={i}, x={x}")

# 10. 避免多行条件表达式（可读性差）
def example_multi_line_conditional_bad():
    def my_long_function_call(a, b, c):
        return "A"
    def my_other_long_function_call(d, e, f):
        return "B"

    i = 3
    x = (my_long_function_call(1, 2, 3)
         if i % 2 == 0
         else my_other_long_function_call(4, 5, 6)
         )
    print(f"[example_multi_line_conditional_bad] i={i}, x={x}")

# 11. 使用赋值表达式（:=）与条件表达式结合
def example_conditional_with_walrus_operator():
    x = 2
    y = 1
    z = (a := x > y)  # 赋值表达式可以嵌套在表达式中
    print(f"[example_conditional_with_walrus_operator] a={a}, z={z}")

# 12. 错误示例：条件表达式嵌套导致歧义
def example_ambiguous_nested_conditional():
    x = 5
    y = 3
    z = True
    w = False

    # 下面两行形式都合法，但含义不同，容易引起误解
    if x > y if z else w:
        print("[example_ambiguous_nested_conditional] Condition 1 is true")

    if x > (y if z else w):
        print("[example_ambiguous_nested_conditional] Condition 2 is true")

# 主函数运行所有示例
def main():
    example_basic_conditional()
    example_lazy_evaluation()
    example_list_comprehension_with_condition()
    example_boolean_logic_trick()
    example_boolean_logic_bug()
    example_standard_if_else()
    example_extended_if_else()
    example_elif_in_if_statement()
    example_helper_function()
    example_multi_line_conditional_bad()
    example_conditional_with_walrus_operator()
    example_ambiguous_nested_conditional()

if __name__ == "__main__":
    main()
