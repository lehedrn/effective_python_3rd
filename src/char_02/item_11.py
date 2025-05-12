"""
Python 字符串格式化演示文件

本文件展示了以下内容：
1. C-style 格式化的缺陷和问题
2. str.format 的使用及其局限性
3. f-strings 的优势及正确使用方式
4. 每种方法的错误示例和正确示例
"""

# ----------------------------
# C-style 格式化问题示例
# ----------------------------

def c_style_type_mismatch():
    """
    C-style 第一个问题：类型不匹配导致的运行时错误

    错误示例：交换了变量顺序导致类型错误
    正确示例：保持正确的变量顺序
    """
    key = "my_var"
    value = 1.234

    # 错误示例
    try:
        reordered_tuple = "%(key)-10s = %(value).2f" % {
            "value": value,  # 错误顺序
            "key": key,
        }
        print("错误示例结果:", reordered_tuple)
    except TypeError as e:
        print("错误示例异常:", e)

    # 正确示例
    correct_order = "%(key)-10s = %(value).2f" % {
        "key": key,
        "value": value,
    }
    print("正确示例结果:", correct_order)

def c_style_redundancy():
    """
    C-style 第四个问题：冗余问题

    错误示例：重复定义字典键
    正确示例：使用更简洁的语法（虽然仍然有冗余）
    """
    soup = "lentil"

    # 错误示例
    error_prone = "Today's soup is %(soup)s." % {"soup": soup}
    print("错误示例结果:", error_prone)

    # 更清晰的写法（但仍存在冗余）
    clearer = "Today's soup is %(soup)s." % {
        "soup": soup,
    }
    print("正确示例结果:", clearer)

# ----------------------------
# str.format 问题示例
# ----------------------------

def format_positional_index():
    """
    str.format 示例：使用位置索引

    展示如何通过位置索引重新排序输出
    """
    key = "my_var"
    value = 1.234

    # 改变输出顺序
    formatted = "{1} = {0}".format(key, value)
    print("str.format 输出顺序调整:", formatted)

def format_expression_limitation():
    """
    str.format 第二个问题：表达式限制

    错误示例：无法直接在格式字符串中执行复杂表达式
    正确示例：在外部执行表达式后再传入
    """
    pantry = [
        ("avocados", 1.25),
        ("bananas", 2.5),
        ("cherries", 15),
    ]

    # 错误示例：尝试在格式字符串中直接调用 round()
    try:
        for i, (item, count) in enumerate(pantry):
            formatted = "#{}: {:<10s} = {round(count)}".format(
                i + 1,
                item.title(),
                count=count,
            )
            print("错误示例结果:", formatted)
    except KeyError as e:
        print("错误示例异常:", e)

    # 正确示例：先计算 round 再传入
    for i, (item, count) in enumerate(pantry):
        formatted = "#{i}: {item:<10s} = {count}".format(
            i=i + 1,
            item=item.title(),
            count=round(count),
        )
        print("正确示例结果:", formatted)


# ----------------------------
# f-strings 优势示例
# ----------------------------

def f_string_basic_usage():
    """
    f-strings 基础用法

    展示基本的变量插入和格式化选项
    """
    key = "my_var"
    value = 1.234

    # 基本用法
    formatted = f"{key} = {value}"
    print("基础用法:", formatted)

    # 高级格式化
    formatted = f"{key!r:<10} = {value:.2f}"
    print("高级格式化:", formatted)

def f_string_expression_support():
    """
    f-strings 表达式支持

    展示如何在占位符中嵌入任意Python表达式
    """
    pantry = [
        ("avocados", 1.25),
        ("bananas", 2.5),
        ("cherries", 15),
    ]

    # 单行表达
    for i, (item, count) in enumerate(pantry):
        print(f"#{i+1}: {item.title():<10s} = {round(count)}")

    # 多行表达（相邻字符串自动拼接）
    for i, (item, count) in enumerate(pantry):
        print(f"#{i+1}: "
              f"{item.title():<10s} = "
              f"{round(count)}")

def f_string_dynamic_formatting():
    """
    f-strings 动态格式化

    展示如何动态指定格式化参数
    """
    places = 3
    number = 1.23456
    print(f"My number is {number:.{places}f}")

# ----------------------------
# 主函数
# ----------------------------

def main():
    """主函数：运行所有示例"""
    print("\n=== C-style 格式化问题 ===")
    print("---- 类型不匹配问题 ----")
    c_style_type_mismatch()

    print("\n---- 冗余问题 ----")
    c_style_redundancy()

    print("\n=== str.format 问题 ===")
    print("---- 位置索引使用 ----")
    format_positional_index()

    print("\n---- 表达式限制 ----")
    format_expression_limitation()

    print("\n=== f-strings 优势 ===")
    print("---- 基础用法 ----")
    f_string_basic_usage()

    print("\n---- 表达式支持 ----")
    f_string_expression_support()

    print("\n---- 动态格式化 ----")
    f_string_dynamic_formatting()

if __name__ == "__main__":
    main()
