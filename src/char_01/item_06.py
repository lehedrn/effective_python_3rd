"""
本文件演示了 Python 中元组字面量的各种写法，特别是单元素元组的注意事项。
包含四种元组定义方式、三种特殊情形（空元组、单元素元组有无括号）、错误使用逗号导致的问题，
以及推荐的最佳实践：始终用括号包裹单元素元组。
"""

# 四种常见的元组定义方式
def example_four_tuple_forms():
    first = (1, 2, 3)
    second = (1, 2, 3,)
    third = 1, 2, 3
    fourth = 1, 2, 3,

    assert first == second == third == fourth
    print("四种元组形式一致:", first)


# 空元组
def example_empty_tuple():
    empty = ()
    print("空元组:", empty)


# 单元素元组 - 必须有逗号
def example_single_element_tuple_with_comma():
    single_with = (1,)
    single_without = (1)
    assert single_with != single_without
    assert single_with[0] == single_without
    print("单元素元组有逗号:", single_with)
    print("被括号包裹的表达式:", single_without)


# 单元素元组 - 无括号但有逗号
def example_single_element_no_parens():
    single_parens = (1,)
    single_no_parens = 1,
    assert single_parens == single_no_parens
    print("单元素元组无括号有逗号:", single_no_parens)


# 错误示例：函数调用中多余的逗号导致返回值为元组
def calculate_refund(*args):
    # 模拟退款计算，返回整数
    return sum(args)

def example_trailing_comma_bug():
    user = None
    order = type('Order', (), {'id': 1, 'dest': 'US'})()

    def get_order_value(u, oid): return 100
    def get_tax(u, dest): return 10
    def adjust_discount(u): return 5

    # 错误写法：末尾多了一个逗号，导致参数变成了一个元组
    to_refund = calculate_refund(
        get_order_value(user, order.id),
        get_tax(user, order.dest),
        adjust_discount(user) + 0.1),
    print("错误写法: 返回类型是 tuple?", type(to_refund))  # 实际上是一个嵌套元组 ((...),)

    # 正确写法
    to_refund2 = calculate_refund(
        get_order_value(user, order.id),
        get_tax(user, order.dest),
        adjust_discount(user) + 0.1
    )
    print("正确写法: 返回类型是 int?", type(to_refund2))


# 单元素元组在赋值中的不同写法
def example_unpacking_single_tuple():
    def get_coupon_codes(user):
        return [['DEAL20']]

    user = None

    (a1,), = get_coupon_codes(user)
    (a2,) = get_coupon_codes(user)
    (a3), = get_coupon_codes(user)
    (a4) = get_coupon_codes(user)
    a5, = get_coupon_codes(user)
    a6 = get_coupon_codes(user)

    print("解包单元素元组的不同写法结果:")
    print(f"a1={a1}, a2={a2}, a3={a3}, a4={a4}, a5={a5}, a6={a6}")
    assert a1 not in (a2, a3, a4, a5, a6)
    assert a2 == a3 == a5
    assert a4 == a6


# 主函数运行所有示例
def main():
    print("=== 四种元组定义方式 ===")
    example_four_tuple_forms()

    print("\n=== 空元组 ===")
    example_empty_tuple()

    print("\n=== 单元素元组有逗号 ===")
    example_single_element_tuple_with_comma()

    print("\n=== 单元素元组无括号 ===")
    example_single_element_no_parens()

    print("\n=== 函数调用中多余逗号导致的 bug ===")
    example_trailing_comma_bug()

    print("\n=== 单元素元组在解包中的不同写法 ===")
    example_unpacking_single_tuple()


if __name__ == '__main__':
    main()
