"""
本文件演示了如何使用 Python 的 dataclasses 模块创建不可变对象，并展示了与标准类实现的对比。
涵盖内容：
- 不可变对象的优势
- 标准类中通过 __setattr__ 实现不可变性
- 使用 dataclasses.frozen 创建不可变对象
- 使用 replace 创建修改后的副本
- 不可变对象在字典和集合中的使用
- namedtuple 的适用场景和局限性
"""

import logging
import dataclasses
from dataclasses import dataclass
from collections import namedtuple

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ======================================================================
# 示例 1: 不可变对象的基本概念及问题（错误示例）
# 描述：普通类对象被意外修改导致的问题
# ======================================================================

class Point:
    def __init__(self, name, x, y):
        self.name = name
        self.x = x
        self.y = y

def bad_distance(left, right):
    left.x = -3  # 错误操作：修改了输入对象的状态
    return ((left.x - right.x) ** 2 + (left.y - right.y) ** 2) ** 0.5

def example_mutable_point():
    logger.info("示例1: 普通类对象被意外修改")
    origin = Point("source", 0, 0)
    point = Point("destination", 3, 4)
    logger.info(f"原始距离: {bad_distance(origin, point)}")
    logger.info(f"origin.x 被意外修改为: {origin.x}")
    logger.warning("警告：函数修改了输入对象，破坏了函数式编程原则")

# ======================================================================
# 示例 2: 手动实现不可变类（正确示例）
# 描述：通过重写 __setattr__ 和 __delattr__ 实现不可变性
# ======================================================================

class ImmutablePoint:
    def __init__(self, name, x, y):
        self.__dict__.update(name=name, x=x, y=y)

    def __setattr__(self, key, value):
        raise AttributeError("Immutable object: set not allowed")

    def __delattr__(self, key):
        raise AttributeError("Immutable object: del not allowed")

def example_immutable_class():
    logger.info("示例2: 手动实现不可变类")
    try:
        point = ImmutablePoint("A", 1, 2)
        point.x = 10  # 尝试修改属性
    except AttributeError as e:
        logger.error(f"捕获到异常: {e}")

# ======================================================================
# 示例 3: 使用 dataclasses 创建不可变类（推荐方式）
# 描述：dataclass 提供简洁、安全且功能完整的不可变类定义方式
# ======================================================================

@dataclass(frozen=True)
class DataclassImmutablePoint:
    name: str
    x: float
    y: float

def example_dataclass_frozen():
    logger.info("示例3: 使用 dataclasses 创建不可变类")
    try:
        point = DataclassImmutablePoint("B", 3, 4)
        point.x = 10  # 尝试修改属性
    except Exception as e:
        logger.error(f"捕获到异常: {e}")

# ======================================================================
# 示例 4: 使用 replace 创建修改后的新对象（函数式风格）
# 描述：不可变对象的更新逻辑应通过返回新对象来实现
# ======================================================================

def translate_replace(point, delta_x, delta_y):
    return dataclasses.replace(point, x=point.x + delta_x, y=point.y + delta_y)

def example_replace_with_dataclass():
    logger.info("示例4: 使用 replace 创建修改后的新对象")
    point = DataclassImmutablePoint("C", 5, 6)
    new_point = translate_replace(point, 1, 2)
    logger.info(f"原始点: ({point.x}, {point.y}), 新点: ({new_point.x}, {new_point.y})")

# ======================================================================
# 示例 5: 不可变对象用于字典键和集合值
# 描述：展示不可变对象在数据结构中的天然兼容性
# ======================================================================

def example_immutables_in_collections():
    logger.info("示例5: 不可变对象作为字典键和集合元素")
    p1 = DataclassImmutablePoint("D", 7, 8)
    p2 = DataclassImmutablePoint("D", 7, 8)  # 等价于 p1

    charge_map = {
        p1: 100.0
    }

    logger.info(f"charge_map[p2]: {charge_map[p2]}")  # 应该能成功获取
    my_set = {p1, p2}
    logger.info(f"集合去重结果: {my_set}")

# ======================================================================
# 示例 6: namedtuple 的使用及注意事项
# 描述：namedtuple 适合顺序数据，但不推荐用于非顺序结构
# ======================================================================

PointNT = namedtuple('PointNT', ['x', 'y'])

def example_namedtuple_usage():
    logger.info("示例6: namedtuple 的使用")
    p = PointNT(1, 2)
    logger.info(f"namedtuple 实例: {p}")
    logger.info(f"可通过索引访问: p[0] = {p[0]}, p[1] = {p[1]}")

    # 修改需用 replace
    p_new = p._replace(x=3)
    logger.info(f"修改后的新实例: {p_new}")

# ======================================================================
# 主函数：运行所有示例
# ======================================================================

def main():
    logger.info("开始运行完整示例...")
    example_mutable_point()
    example_immutable_class()
    example_dataclass_frozen()
    example_replace_with_dataclass()
    example_immutables_in_collections()
    example_namedtuple_usage()
    logger.info("所有示例运行完成。")

if __name__ == "__main__":
    main()
