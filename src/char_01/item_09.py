"""
Python `match` 语句完整示例文件（Chapter 1, Item 9）

本文件展示了以下内容：
1. 使用 match 时常见的错误：变量名被当作“捕获模式”。
2. 正确使用方式：通过 enum 避免捕获陷阱。
3. match 的结构解构能力：用于处理元组表示的二叉树。
4. 使用自定义类 Node 并结合 match 解构属性。
5. 利用 match 处理半结构化 JSON 数据的反序列化。

每个示例都包含 main 函数运行完整流程，并附有详细注释。
"""

import enum
from dataclasses import dataclass
import json


# ========================
# 示例 1: 错误使用 match - 捕获模式陷阱
# ========================

# def take_action_with_match(light):
#     """
#     ❌ 错误示例：case RED 实际上是赋值而非比较！
#     """
#     match light:
#         case RED:
#             print("Stop")
#         case YELLOW:
#             print("Slow down")
#         case GREEN:
#             print("Go!")
#         case _:
#             raise RuntimeError


# ========================
# 示例 2: 正确使用 match - 枚举 + 点号访问
# ========================

class LightColor(enum.Enum):
    RED = "red"
    YELLOW = "yellow"
    GREEN = "green"


def take_enum_action(light):
    """
    ✅ 正确示例：使用枚举避免捕获陷阱。
    """
    match light:
        case LightColor.RED:
            print("Stop")
        case LightColor.YELLOW:
            print("Slow down")
        case LightColor.GREEN:
            print("Go!")
        case _:
            raise RuntimeError


# ========================
# 示例 3: 使用 if 查找三元组表示的二叉树
# ========================

my_tree = (10, (7, None, 9), (13, 11, None))


def contains(tree, value):
    """
    ✅ 使用 if 判断结构并查找节点值。
    """
    if not isinstance(tree, tuple):
        return tree == value
    pivot, left, right = tree
    if value < pivot:
        return contains(left, value)
    elif value > pivot:
        return contains(right, value)
    else:
        return value == pivot


# ========================
# 示例 4: 使用 match 查找三元组表示的二叉树
# ========================

def contains_match(tree, value):
    """
    ✅ 使用 match 结合结构匹配查找节点值。
    更简洁且逻辑更清晰。
    """
    match tree:
        case pivot, left, _ if value < pivot:
            return contains_match(left, value)
        case pivot, _, right if value > pivot:
            return contains_match(right, value)
        case (pivot, _, _) | pivot:
            return pivot == value


# ========================
# 示例 5: 自定义类 Node + match 解构属性
# ========================

class Node:
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right


obj_tree = Node(
    value=10,
    left=Node(value=7, right=9),
    right=Node(value=13, left=11),
)


def contains_match_class(tree, value):
    """
    ✅ 使用 match 解构自定义对象属性。
    支持 isinstace 判断 + 属性提取 + 守卫条件。
    """
    match tree:
        case Node(value=pivot, left=left) if value < pivot:
            return contains_match_class(left, value)
        case Node(value=pivot, right=right) if value > pivot:
            return contains_match_class(right, value)
        case Node(value=pivot) | pivot:
            return pivot == value


# ========================
# 示例 6: 使用 match 反序列化 JSON 半结构化数据
# ========================

@dataclass
class PersonCustomer:
    first_name: str
    last_name: str


@dataclass
class BusinessCustomer:
    company_name: str


def deserialize(data):
    """
    ✅ 根据 JSON 结构创建不同的客户对象。
    使用 match 解构字典嵌套结构。
    """
    record = json.loads(data)
    match record:
        case {"customer": {"last": last_name, "first": first_name}}:
            return PersonCustomer(first_name, last_name)
        case {"customer": {"entity": company_name}}:
            return BusinessCustomer(company_name)
        case _:
            raise ValueError("Unknown record type")


# ========================
# 主函数入口 - 运行所有示例
# ========================

if __name__ == "__main__":
    # print("=== 示例 1: 错误用法 ===")
    # try:
    #     RED = "red"
    #     YELLOW = "yellow"
    #     GREEN = "green"
    #     take_action_with_match("green")
    # except Exception as e:
    #     print(f"❌ 报错原因：{e}")

    print("\n=== 示例 2: 枚举匹配 ===")
    take_enum_action(LightColor.RED)
    take_enum_action(LightColor.YELLOW)
    take_enum_action(LightColor.GREEN)

    print("\n=== 示例 3: if 版本查找树 ===")
    print("Contains 9?", contains(my_tree, 9))
    print("Contains 14?", contains(my_tree, 14))

    print("\n=== 示例 4: match 版本查找树 ===")
    print("Match Contains 9?", contains_match(my_tree, 9))
    print("Match Contains 14?", contains_match(my_tree, 14))

    print("\n=== 示例 5: 类版本 match 查找树 ===")
    print("Class Match Contains 9?", contains_match_class(obj_tree, 9))
    print("Class Match Contains 14?", contains_match_class(obj_tree, 14))

    print("\n=== 示例 6: JSON 反序列化 ===")
    record1 = '{"customer": {"last": "Ross", "first": "Bob"}}'
    record2 = '{"customer": {"entity": "Steve\'s Painting Co."}}'

    customer1 = deserialize(record1)
    customer2 = deserialize(record2)

    print("Person Customer:", customer1)
    print("Business Customer:", customer2)
