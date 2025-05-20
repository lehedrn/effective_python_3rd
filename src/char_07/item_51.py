"""
dataclasses 示例演示

该模块展示了 dataclasses 在简化类定义、提高可读性和减少错误方面的优势。
涵盖以下功能：
- 自动 __init__ 和类型提示
- 强制关键字参数初始化
- 默认属性值（包括可变默认值处理）
- 自动生成 __repr__
- 支持 asdict / astuple
- 自动等价性判断和排序支持
"""

import logging
from dataclasses import dataclass, field, asdict, astuple
from typing import Any, List

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


# 1. 避免 __init__ 冗余代码
class RGB:
    """手动实现的 RGB 类，存在重复代码和易错问题"""
    def __init__(self, red, green, blue):
        self.red = red
        self.green = green
        self.blue = blue


def bad_init_example():
    """错误示例：构造函数参数顺序混乱导致 bug"""
    try:
        class BadRGB:
            def __init__(self, green, red, blue):  # 参数顺序错误
                self.red = red
                self.green = green
                self.bloe = blue  # 拼写错误导致属性缺失

        obj = BadRGB(1, 2, 3)
        logger.info("BadRGB 初始化成功但存在拼写错误")
    except Exception as e:
        logger.error(f"BadRGB 出现错误: {e}")


@dataclass
class DataclassRGB:
    """dataclass 实现的 RGB 类，自动处理 __init__"""
    red: int
    green: int
    blue: int


def good_init_example():
    """正确示例：使用 dataclass 避免冗余代码"""
    color = DataclassRGB(1, 2, 3)
    logger.info(f"dataclass 初始化成功: {color}")
    assert color.red == 1 and color.green == 2 and color.blue == 3


# 2. 强制关键字参数初始化
class KWOnlyRGB:
    """强制关键字参数的标准类实现"""
    def __init__(self, *, red, green, blue):
        self.red = red
        self.green = green
        self.blue = blue


def bad_kw_only_example():
    """错误示例：位置参数调用失败"""
    try:
        color = KWOnlyRGB(1, 2, 3)  # 会抛出 TypeError
    except TypeError as e:
        logger.error(f"KWOnlyRGB 使用位置参数失败: {e}")


@dataclass(kw_only=True)
class DataclassKWOnlyRGB:
    """dataclass 实现强制关键字参数"""
    red: int
    green: int
    blue: int


def good_kw_only_example():
    """正确示例：使用 dataclass kw_only=True"""
    color = DataclassKWOnlyRGB(red=1, green=2, blue=3)
    logger.info(f"dataclass 关键字初始化成功: {color}")
    try:
        DataclassKWOnlyRGB(1, 2, 3)  # 会抛出 TypeError
    except TypeError as e:
        logger.warning(f"dataclass 不允许位置参数: {e}")


# 3. 默认值设置（不可变 vs 可变）
class RGBA:
    """带默认值的标准类"""
    def __init__(self, *, red, green, blue, alpha=1.0):
        self.red = red
        self.green = green
        self.blue = blue
        self.alpha = alpha


def bad_mutable_default_example():
    """错误示例：使用可变默认值导致共享引用"""
    try:
        class BadContainer:
            def __init__(self, value=[]):
                self.value = value

        obj1 = BadContainer()
        obj2 = BadContainer()
        obj1.value.append(1)
        assert obj2.value == [1]  # 共享列表对象导致错误
        logger.error("BadContainer 共享可变默认值")
    except Exception as e:
        logger.warning(f"BadContainer 错误: {e}")


@dataclass
class DataclassMutableDefault:
    """dataclass 使用 field(default_factory=...) 处理可变默认值"""
    value: List[int] = field(default_factory=list)


def good_mutable_default_example():
    """正确示例：使用 default_factory 避免共享引用"""
    obj1 = DataclassMutableDefault()
    obj2 = DataclassMutableDefault()
    obj1.value.append(1)
    assert obj1.value == [1]
    assert obj2.value == []
    logger.info("DataclassMutableDefault 正确分配独立列表")


# 4. __repr__ 自动生成
class Planet:
    """标准类需要手动实现 __repr__"""
    def __init__(self, distance, size):
        self.distance = distance
        self.size = size

    def __repr__(self):
        return f"{type(self).__name__}(distance={self.distance}, size={self.size})"


def manual_repr_example():
    """手动实现 __repr__ 示例"""
    planet = Planet(10, 5)
    logger.info(f"手动 __repr__: {planet}")


@dataclass
class DataclassPlanet:
    """dataclass 自动生成 __repr__"""
    distance: float
    size: float


def auto_repr_example():
    """dataclass 自动生成 __repr__ 示例"""
    planet = DataclassPlanet(10, 5)
    logger.info(f"dataclass 自动生成 __repr__: {planet}")


# 5. 转换为元组和字典
class ManualConvert:
    """手动实现 _asdict 和 _astuple 方法"""
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def _astuple(self):
        return (self.x, self.y)

    def _asdict(self):
        return {'x': self.x, 'y': self.y}


def manual_convert_example():
    """手动转换方法示例"""
    obj = ManualConvert(1, 2)
    logger.info(f"手动 _astuple: {obj._astuple()}")
    logger.info(f"手动 _asdict: {obj._asdict()}")


@dataclass
class DataclassConvert:
    """dataclass 使用内置转换函数"""
    x: int
    y: int


def dataclass_convert_example():
    """dataclass 转换函数示例"""
    obj = DataclassConvert(3, 4)
    logger.info(f"dataclass astuple: {astuple(obj)}")
    logger.info(f"dataclass asdict: {asdict(obj)}")


# 6. 等价性比较
class ManualEq:
    """手动实现 __eq__"""
    def __init__(self, a):
        self.a = a

    def __eq__(self, other):
        return type(self) == type(other) and self.a == other.a


def manual_eq_example():
    """手动实现 __eq__ 示例"""
    o1 = ManualEq(1)
    o2 = ManualEq(1)
    assert o1 == o2
    logger.info(f"手动 __eq__ 成功: {o1} == {o2}")


@dataclass
class DataclassEq:
    """dataclass 自动生成 __eq__"""
    a: int


def dataclass_eq_example():
    """dataclass 自动生成 __eq__ 示例"""
    o1 = DataclassEq(1)
    o2 = DataclassEq(1)
    assert o1 == o2
    logger.info(f"dataclass 自动生成 __eq__: {o1} == {o2}")


@dataclass(order=True)
class DataclassOrderedPlanet:
    """dataclass 自动生成排序方法，新增属性且部分字段不参与比较"""
    distance: float
    size: float
    name: str = field(compare=False)  # 设置字段不参与比较 compare=False



def dataclass_ordering_example():
    """dataclass 自动生成排序方法示例"""
    far = DataclassOrderedPlanet(10, 2, "far")
    near = DataclassOrderedPlanet(1, 5, "near")
    assert far > near
    assert near < far
    planets = [far, near]
    planets.sort()
    logger.info(f"dataclass 排序结果: {planets}")


# 主函数运行所有示例
def main():
    logger.info("开始运行 dataclasses 示例")

    logger.info("--- 1. 避免 __init__ 冗余 ---")
    bad_init_example()
    good_init_example()

    logger.info("--- 2. 强制关键字参数初始化 ---")
    bad_kw_only_example()
    good_kw_only_example()

    logger.info("--- 3. 默认值设置（不可变 vs 可变） ---")
    bad_mutable_default_example()
    good_mutable_default_example()

    logger.info("--- 4. __repr__ 自动生成 ---")
    manual_repr_example()
    auto_repr_example()

    logger.info("--- 5. 转换为元组和字典 ---")
    manual_convert_example()
    dataclass_convert_example()

    logger.info("--- 6. 等价性比较 ---")
    manual_eq_example()
    dataclass_eq_example()

    logger.info("--- 7. 排序支持 ---")
    dataclass_ordering_example()

    logger.info("所有示例运行完毕")


if __name__ == "__main__":
    main()
