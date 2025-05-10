"""
Item 5: Prefer Multiple Assignment Unpacking Over Indexing

本模块演示如何使用多重赋值解包代替索引访问，以提升代码可读性和简洁性。
包含以下示例：
1. 使用索引 vs 解包访问元组
2. 嵌套结构解包
3. 手动交换变量 vs 解包交换变量
4. range + 索引遍历 vs enumerate + 解包遍历
5. 函数参数解包 (*args)
6. 多返回值函数与解包
7. match 语句中的结构化解包（Python 3.10+）
8. 单元素元组错误示例（Item 6 相关）
"""

# ————————————————————————
# 示例 1: 访问元组元素 - 索引 vs 解包
# ————————————————————————

def example_1_index_access():
    """使用索引访问元组元素"""
    item = ("Peanut butter", "Jelly")
    first_item = item[0]
    first_half = item[:1]
    print("Example 1 (Index):", first_item, first_half)


def example_1_unpacking():
    """使用解包访问元组元素"""
    item = ("Peanut butter", "Jelly")
    first, second = item
    print("Example 1 (Unpacking):", first, "and", second)


# ————————————————————————
# 示例 2: 嵌套结构解包
# ————————————————————————

def example_2_nested_unpacking():
    """解包嵌套结构"""
    favorite_snacks = {
        "salty": ("pretzels", 100),
        "sweet": ("cookies", 180),
        "veggie": ("carrots", 20),
    }

    ((type1, (name1, cals1)),
     (type2, (name2, cals2)),
     (type3, (name3, cals3))) = favorite_snacks.items()

    print(f"Favorite {type1} is {name1} with {cals1} calories")
    print(f"Favorite {type2} is {name2} with {cals2} calories")
    print(f"Favorite {type3} is {name3} with {cals3} calories")


# ————————————————————————
# 示例 3: 变量交换 - 手动临时变量 vs 解包
# ————————————————————————

def example_3_swap_with_temp():
    """使用临时变量交换两个值"""
    a = ["pretzels", "carrots"]
    temp = a[0]
    a[0] = a[1]
    a[1] = temp
    print("Example 3 (Temp var):", a)


def example_3_swap_with_unpacking():
    """使用解包交换两个值"""
    a = ["pretzels", "carrots"]
    a[0], a[1] = a[1], a[0]
    print("Example 3 (Unpacking):", a)


# ————————————————————————
# 示例 4: 遍历嵌套列表 - 索引 vs enumerate + 解包
# ————————————————————————

def example_4_loop_with_index():
    """使用 range + 索引遍历嵌套列表"""
    snacks = [("bacon", 350), ("donut", 240), ("muffin", 190)]
    for i in range(len(snacks)):
        name = snacks[i][0]
        calories = snacks[i][1]
        print(f"#{i+1}: {name} has {calories} calories")


def example_4_loop_with_enumerate_and_unpacking():
    """使用 enumerate + 解包遍历嵌套列表"""
    snacks = [("bacon", 350), ("donut", 240), ("muffin", 190)]
    for rank, (name, calories) in enumerate(snacks, 1):
        print(f"#{rank}: {name} has {calories} calories")


# ————————————————————————
# 示例 5: 函数参数解包 (*args)
# ————————————————————————

def example_5_function_args_unpacking():
    """函数参数解包"""
    def log_activity(activity, duration):
        print(f"Did {activity} for {duration} minutes.")

    data = ("coding", 45)
    log_activity(*data)  # 使用 * 解包作为位置参数传入


# ————————————————————————
# 示例 6: 多返回值函数与解包
# ————————————————————————

def example_6_multiple_return_values():
    """函数返回多个值并用解包接收"""
    def get_user_info():
        return "Alice", 28, "Engineer"

    name, age, job = get_user_info()
    print(f"{name} is {age} years old and works as a {job}.")


# ————————————————————————
# 示例 7: match 语句中的结构化解包（Python 3.10+）
# ————————————————————————

def example_7_match_unpacking():
    """match 中使用解包进行结构化匹配"""
    point = (3, 5)

    match point:
        case (0, 0):
            print("Origin")
        case (x, 0):
            print(f"Lies on x-axis at {x}")
        case (0, y):
            print(f"Lies on y-axis at {y}")
        case (x, y):
            print(f"Point located at ({x}, {y})")
        case _:
            print("Not a valid point")


# ————————————————————————
# 示例 8: 单元素元组错误示例（Item 6）
# ————————————————————————

def example_8_single_element_tuple_mistake():
    """错误地定义单元素元组"""
    snack1 = ("chips")   # ❌ 这不是一个元组
    snack2 = ("chips",)  # ✅ 正确的单元素元组

    print("snack1 type:", type(snack1))
    print("snack2 type:", type(snack2))


# ————————————————————————
# 主函数入口
# ————————————————————————

def main():
    print("=== 示例 1: 使用索引 vs 解包访问元组 ===")
    example_1_index_access()
    example_1_unpacking()

    print("\n=== 示例 2: 解包嵌套结构 ===")
    example_2_nested_unpacking()

    print("\n=== 示例 3: 交换变量值的方式对比 ===")
    example_3_swap_with_temp()
    example_3_swap_with_unpacking()

    print("\n=== 示例 4: 遍历嵌套列表方式对比 ===")
    print("使用 range 和索引:")
    example_4_loop_with_index()
    print("\n使用 enumerate + 解包:")
    example_4_loop_with_enumerate_and_unpacking()

    print("\n=== 示例 5: 函数参数解包 (*args) ===")
    example_5_function_args_unpacking()

    print("\n=== 示例 6: 多返回值函数与解包 ===")
    example_6_multiple_return_values()

    print("\n=== 示例 7: match 语句中的结构化解包 ===")
    try:
        example_7_match_unpacking()
    except SyntaxError:
        print("⚠️ 当前 Python 版本不支持 match 语法，请升级到 3.10 或更高版本。")

    print("\n=== 示例 8: 单元素元组错误示例 ===")
    example_8_single_element_tuple_mistake()


if __name__ == "__main__":
    main()
