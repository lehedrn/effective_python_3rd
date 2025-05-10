"""
本文件演示 Python 3.8+ 中赋值表达式（海象运算符 :=）的多种使用方式。
涵盖内容：
- 避免在 if 条件中重复赋值
- 在条件判断中使用括号处理复合表达式
- 使用 walrus 替代 switch/case 嵌套逻辑
- while 循环中避免冗余调用
- 提高变量作用域定义的清晰度

适用于理解如何通过赋值表达式减少代码重复、提高可读性。
"""

# 水果篮子数据：用于模拟不同水果库存
fresh_fruit = {
    "apple": 10,
    "banana": 8,
    "lemon": 5,
}


# -----------------------------
# 辅助函数定义
# -----------------------------

def make_lemonade(count):
    """制作柠檬水"""
    print(f"Making {count} lemons into lemonade")


def make_cider(count):
    """制作苹果酒"""
    print(f"Making cider with {count} apples")


def slice_bananas(count):
    """切香蕉为片"""
    print(f"Slicing {count} bananas")
    return count * 4  # 假设每根香蕉切成 4 片


def make_smoothies(pieces):
    """制作奶昔"""
    if pieces < 2:
        raise OutOfBananas()  # 如果香蕉片不足则抛出异常
    print(f"Making a smoothie with {pieces} banana slices")
    return ["smoothie"]


class OutOfBananas(Exception):
    """自定义异常：香蕉不足"""
    pass


def out_of_stock():
    """库存不足提示"""
    print("Out of stock!")


def pick_fruit():
    """模拟获取新水果"""
    global fresh_fruit
    if fresh_fruit:
        result = fresh_fruit.copy()
        fresh_fruit.clear()
        return result
    return None


def make_juice(fruit, count):
    """制作果汁"""
    print(f"Making juice from {count} {fruit}")
    return [f"{fruit}_juice"] * count


# -----------------------------
# 错误与推荐示例函数
# -----------------------------

def bad_example_1():
    """
    ❌ 错误示例 1：普通赋值导致变量提前暴露
    count 被提前定义，即使只在 if 块中使用
    """
    count = fresh_fruit.get("lemon", 0)
    if count:
        make_lemonade(count)
    else:
        out_of_stock()


def good_example_1():
    """
    ✅ 推荐示例 1：使用 walrus 运算符简化逻辑
    变量 count 只在 if 判断中定义和使用
    """
    if count := fresh_fruit.get("lemon", 0):
        make_lemonade(count)
    else:
        out_of_stock()


def bad_example_2():
    """
    ❌ 错误示例 2：需要比较数值时仍使用普通赋值
    count 多次出现在代码中，影响可读性
    """
    count = fresh_fruit.get("apple", 0)
    if count >= 4:
        make_cider(count)
    else:
        out_of_stock()


def good_example_2():
    """
    ✅ 推荐示例 2：使用 walrus 并注意括号使用
    将赋值与判断合并一行，更简洁清晰
    """
    if (count := fresh_fruit.get("apple", 0)) >= 4:
        make_cider(count)
    else:
        out_of_stock()


def bad_example_3():
    """
    ❌ 错误示例 3：变量 pieces 分布在多个分支中定义
    可读性差，变量定义位置分散
    """
    count = fresh_fruit.get("banana", 0)
    if count >= 2:
        pieces = slice_bananas(count)
    else:
        pieces = 0
    try:
        make_smoothies(pieces)
    except OutOfBananas:
        out_of_stock()


def good_example_3():
    """
    ✅ 推荐示例 3：使用 walrus 提高结构清晰度
    变量定义集中，逻辑更易追踪
    """
    if (count := fresh_fruit.get("banana", 0)) >= 2:
        pieces = slice_bananas(count)
    else:
        pieces = 0
    try:
        make_smoothies(pieces)
    except OutOfBananas:
        out_of_stock()


def bad_example_4():
    """
    ❌ 错误示例 4：多层嵌套实现优先级判断（类似 switch）
    嵌套深，结构复杂，难以维护
    """
    count = fresh_fruit.get("banana", 0)
    if count >= 2:
        to_enjoy = make_smoothies(slice_bananas(count))
    else:
        count = fresh_fruit.get("apple", 0)
        if count >= 4:
            to_enjoy = make_cider(count)
        else:
            count = fresh_fruit.get("lemon", 0)
            if count:
                to_enjoy = make_lemonade(count)
            else:
                to_enjoy = "Nothing"
    return to_enjoy


def good_example_4():
    """
    ✅ 推荐示例 4：使用 walrus 简化嵌套结构
    用 walrus 合并赋值与判断，结构扁平，可读性强
    """
    if (count := fresh_fruit.get("banana", 0)) >= 2:
        to_enjoy = make_smoothies(slice_bananas(count))
    elif (count := fresh_fruit.get("apple", 0)) >= 4:
        to_enjoy = make_cider(count)
    elif count := fresh_fruit.get("lemon", 0):
        to_enjoy = make_lemonade(count)
    else:
        to_enjoy = "Nothing"
    return to_enjoy


def bad_example_5():
    """
    ❌ 错误示例 5：while 循环重复调用 pick_fruit
    初始化和更新状态两次调用相同函数，冗余明显
    """
    bottles = []
    fresh_fruit = pick_fruit()
    while fresh_fruit:
        for fruit, count in fresh_fruit.items():
            batch = make_juice(fruit, count)
            bottles.extend(batch)
        fresh_fruit = pick_fruit()
    return bottles


def good_example_5():
    """
    ✅ 推荐示例 5：使用 walrus 避免重复
    在 while 条件中完成赋值与判断，结构简洁清晰
    """
    bottles = []
    while fresh_fruit := pick_fruit():
        for fruit, count in fresh_fruit.items():
            batch = make_juice(fruit, count)
            bottles.extend(batch)
    return bottles


# -----------------------------
# 主函数：运行所有示例
# -----------------------------

def main():
    print("\n--- 错误示例 1 ---")
    bad_example_1()

    print("\n--- 正确示例 1 ---")
    good_example_1()

    print("\n--- 错误示例 2 ---")
    bad_example_2()

    print("\n--- 正确示例 2 ---")
    good_example_2()

    print("\n--- 错误示例 3 ---")
    bad_example_3()

    print("\n--- 正确示例 3 ---")
    good_example_3()

    print("\n--- 错误示例 4 ---")
    bad_example_4()

    print("\n--- 正确示例 4 ---")
    good_example_4()

    print("\n--- 错误示例 5 ---")
    bad_example_5()

    print("\n--- 正确示例 5 ---")
    good_example_5()


if __name__ == "__main__":
    main()
