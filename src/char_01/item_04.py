"""
Chapter 1: Pythonic Thinking
Item 4: Write Helper Functions Instead of Complex Expressions

本文件演示了将复杂表达式封装到辅助函数中的好处。
包含一个不好的示例（复杂难懂）和一个好示例（使用辅助函数提高可读性和复用性）。

目标是从解析后的查询字符串中提取整数值，并在值缺失或为空时提供默认值 0。
"""

from urllib.parse import parse_qs


# ❌ 不推荐：复杂的单行表达式难以阅读和维护
def bad_example():
    """
    展示使用复杂逻辑的一行代码来提取并转换查询参数为整数。
    这种写法虽然简短，但不易理解和调试。
    """
    data = "red=5&blue=0&green="
    my_values = parse_qs(data, keep_blank_values=True)

    # 复杂且难以理解的表达式
    red = int(my_values.get("red", [""])[0] or 0)
    green = int(my_values.get("green", [""])[0] or 0)
    opacity = int(my_values.get("opacity", [""])[0] or 0)

    print(f"[Bad Example] red={red}, green={green}, opacity={opacity}")


# ✅ 推荐：定义一个清晰的辅助函数处理逻辑
def get_first_int(values, key, default=0):
    """
    从字典中安全获取第一个整数值，若不存在或为空则返回默认值。

    参数:
        values (dict): 包含列表值的字典。
        key (str): 要查找的键。
        default (int): 如果值为空或不存在时返回的默认值。

    返回:
        int: 解析后的整数或默认值。
    """
    found = values.get(key, [""])
    if found[0]:  # 若值存在且非空
        try:
            return int(found[0])
        except ValueError:  # 若字符串无法转为整数
            return default
    return default


# ✅ 好示例：使用辅助函数使主逻辑更清晰
def good_example():
    """
    使用辅助函数 get_first_int 提取并转换查询参数为整数。
    代码简洁、易读、可重用性强。
    """
    data = "red=5&blue=0&green="
    my_values = parse_qs(data, keep_blank_values=True)

    # 清晰易读的调用方式
    red = get_first_int(my_values, "red")
    green = get_first_int(my_values, "green")
    opacity = get_first_int(my_values, "opacity")

    print(f"[Good Example] red={red}, green={green}, opacity={opacity}")


# 🧪 主函数运行所有示例
def main():
    """
    主函数用于执行所有示例函数。
    """
    print("开始运行 Item 4 示例：\n")
    bad_example()
    good_example()
    print("\n示例运行结束。")


if __name__ == "__main__":
    main()
