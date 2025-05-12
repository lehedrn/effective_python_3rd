"""
本文件演示了 Python 中使用捕获所有项的解包（星号表达式）的各种示例，
包括基本用法、错误用法、正确用法以及在不同场景中的应用。

内容涵盖：
- 使用 `*` 进行捕获所有项的解包
- 错误用法，如单独使用星号表达式或多星号表达式
- 在列表、迭代器、生成器中的实际应用场景
"""

# 示例 1: 基本解包失败的情况（长度不匹配）
def example_basic_unpacking_failure():
    car_ages = [0, 9, 4, 8, 7, 20, 19, 1, 6, 15]
    car_ages_descending = sorted(car_ages, reverse=True)

    try:
        oldest, second_oldest = car_ages_descending
    except ValueError as e:
        print("【错误示例】基本解包失败：", e)


# 示例 2: 使用索引和切片提取数据（有效但易出错）
def example_indexing_and_slicing():
    car_ages = [0, 9, 4, 8, 7, 20, 19, 1, 6, 15]
    car_ages_descending = sorted(car_ages, reverse=True)

    oldest = car_ages_descending[0]
    second_oldest = car_ages_descending[1]
    others = car_ages_descending[2:]
    print("【正确示例】索引与切片提取：", oldest, second_oldest, others)


# 示例 3: 使用星号表达式进行捕获所有项的解包（推荐方式）
def example_starred_unpacking():
    car_ages = [0, 9, 4, 8, 7, 20, 19, 1, 6, 15]
    car_ages_descending = sorted(car_ages, reverse=True)

    oldest, second_oldest, *others = car_ages_descending
    print("【正确示例】星号解包提取：", oldest, second_oldest, others)


# 示例 4: 星号表达式出现在中间位置（灵活解包）
def example_star_in_middle():
    car_ages = [0, 9, 4, 8, 7, 20, 19, 1, 6, 15]
    car_ages_descending = sorted(car_ages, reverse=True)

    oldest, *others, youngest = car_ages_descending
    print("【正确示例】星号在中间解包：", oldest, youngest, others)


# 示例 5: 星号表达式出现在开头（灵活解包）
def example_star_at_start():
    car_ages = [0, 9, 4, 8, 7, 20, 19, 1, 6, 15]
    car_ages_descending = sorted(car_ages, reverse=True)

    *others, second_youngest, youngest = car_ages_descending
    print("【正确示例】星号在开头解包：", youngest, second_youngest, others)


# 示例 6: 单独使用星号表达式（错误）
# def example_single_star_usage():
#     car_ages_descending = [20, 19, 15, 9, 8, 7, 6, 4, 1, 0]
#
#     try:
#         # 这里IDE直接不让报错，不让运行
#         *others = car_ages_descending
#     except SyntaxError as e:
#         print("【错误示例】单独使用星号表达式：", e)


# 示例 7: 多个星号表达式（错误）
# IDE直接不让运行
# def example_multiple_stars_usage():
#     car_ages_descending = [20, 19, 15, 9, 8, 7, 6, 4, 1, 0]
#
#     try:
#         first, *middle, *second_middle, last = car_ages_descending
#     except SyntaxError as e:
#         print("【错误示例】多个星号表达式：", e)


# 示例 8: 使用星号解包处理短列表（自动填充空列表）
def example_short_list_unpacking():
    short_list = [1, 2]
    first, second, *rest = short_list
    print("【正确示例】解包短列表：", first, second, rest)


# 示例 9: 使用星号解包处理生成器（清晰简洁）
def example_unpack_generator():
    def generate_csv():
        yield ("Date", "Make", "Model", "Year", "Price")
        for i in range(100):
            yield ("2019-03-25", "Honda", "Fit", "2010", "$3400")
            yield ("2019-03-26", "Ford", "F150", "2008", "$2400")

    it = generate_csv()
    header, *rows = it
    print(f"CSV Header: {header}")
    print(f"Row count: {len(rows)}")


# 主函数运行所有示例
def main():
    print("=== 示例 1: 基本解包失败 ===")
    example_basic_unpacking_failure()

    print("\n=== 示例 2: 使用索引和切片 ===")
    example_indexing_and_slicing()

    print("\n=== 示例 3: 使用星号表达式解包 ===")
    example_starred_unpacking()

    print("\n=== 示例 4: 星号表达式在中间 ===")
    example_star_in_middle()

    print("\n=== 示例 5: 星号表达式在开头 ===")
    example_star_at_start()

    # print("\n=== 示例 6: 单独使用星号表达式 ===")
    # example_single_star_usage()

    # print("\n=== 示例 7: 多个星号表达式 ===")
    # example_multiple_stars_usage()

    print("\n=== 示例 8: 解包短列表 ===")
    example_short_list_unpacking()

    print("\n=== 示例 9: 解包生成器 ===")
    example_unpack_generator()


if __name__ == "__main__":
    main()
