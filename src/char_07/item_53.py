"""
本文件展示了 Python 中使用 super() 初始化父类的重要性，以及在多重继承和菱形继承中使用直接调用 __init__ 方法的潜在问题。
包含错误示例与正确示例，并通过 logging 输出结果以说明不同方式的行为差异。

条目内容涵盖：
- 直接调用父类 __init__ 的问题
- 多重继承中初始化顺序不一致的问题
- 菱形继承导致超类多次初始化的问题
- 使用 super().__init__() 的解决方案及 MRO 机制

所有示例均符合 PEP8 规范，并提供详细的中文注释解释其行为。
"""

import logging

# 配置日志输出
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


# =============================
# 错误示例 1：直接调用父类 __init__
# =============================
class MyBaseClass:
    """基类，用于被继承的基础功能"""
    def __init__(self, value):
        self.value = value
        logging.info(f"MyBaseClass initialized with value: {self.value}")


class MyChildClass(MyBaseClass):
    """错误示例：子类直接调用 MyBaseClass.__init__"""
    def __init__(self):
        MyBaseClass.__init__(self, 5)
        logging.info(f"MyChildClass initialized")


def example_direct_init_call():
    """演示直接调用父类 __init__ 的问题"""
    logging.info("=== 错误示例 1：直接调用父类 __init__ ===")
    obj = MyChildClass()
    logging.info(f"Final value: {obj.value}")


# =============================
# 错误示例 2：多重继承中初始化顺序混乱
# =============================
class TimesTwo:
    def __init__(self, value):
        self.value = value * 2
        logging.info(f"TimesTwo initialized with value: {self.value}")


class PlusFive:
    def __init__(self, value):
        self.value = value + 5
        logging.info(f"PlusFive initialized with value: {self.value}")


class OneWay(MyBaseClass, TimesTwo, PlusFive):
    def __init__(self, value):
        MyBaseClass.__init__(self, value)
        TimesTwo.__init__(self, self.value)
        PlusFive.__init__(self, self.value)


class AnotherWay(MyBaseClass, PlusFive, TimesTwo):
    def __init__(self, value):
        MyBaseClass.__init__(self, value)
        TimesTwo.__init__(self, self.value)
        PlusFive.__init__(self, self.value)


def example_multiple_inheritance_conflict():
    """演示多重继承中初始化顺序冲突的问题"""
    logging.info("=== 错误示例 2：多重继承中初始化顺序混乱 ===")
    logging.info("OneWay(5):")
    foo = OneWay(5)
    logging.info(f"Final value (OneWay): {foo.value}")

    logging.info("\nAnotherWay(5):")
    bar = AnotherWay(5)
    logging.info(f"Final value (AnotherWay): {bar.value}")


# =============================
# 错误示例 3：菱形继承导致重复初始化
# =============================
class TimesSeven(MyBaseClass):
    def __init__(self, value):
        MyBaseClass.__init__(self, value)
        self.value *= 7
        logging.info(f"TimesSeven initialized with value: {self.value}")


class PlusNine(MyBaseClass):
    def __init__(self, value):
        MyBaseClass.__init__(self, value)
        self.value += 9
        logging.info(f"PlusNine initialized with value: {self.value}")


class ThisWay(TimesSeven, PlusNine):
    def __init__(self, value):
        TimesSeven.__init__(self, value)
        PlusNine.__init__(self, self.value)


def example_diamond_inheritance_issue():
    """演示菱形继承导致重复初始化的问题"""
    logging.info("=== 错误示例 3：菱形继承导致重复初始化 ===")
    obj = ThisWay(5)
    logging.info(f"Final value (ThisWay): {obj.value}")


# =============================
# 正确示例：使用 super() 和 MRO 解决继承问题
# =============================
class MyBaseClassCorrect:
    def __init__(self, value):
        self.value = value
        logging.info(f"MyBaseClassCorrect initialized with value: {self.value}")


class TimesSevenCorrect(MyBaseClassCorrect):
    def __init__(self, value):
        super().__init__(value)
        self.value *= 7
        logging.info(f"TimesSevenCorrect initialized with value: {self.value}")


class PlusNineCorrect(MyBaseClassCorrect):
    def __init__(self, value):
        super().__init__(value)
        self.value += 9
        logging.info(f"PlusNineCorrect initialized with value: {self.value}")


class GoodWay(TimesSevenCorrect, PlusNineCorrect):
    def __init__(self, value):
        super().__init__(value)


def example_super_and_mro():
    """演示使用 super() 和 MRO 的正确继承方式"""
    logging.info("=== 正确示例：使用 super() 和 MRO 解决继承问题 ===")
    obj = GoodWay(5)
    logging.info(f"Final value (GoodWay): {obj.value}")
    logging.info("\nMRO for GoodWay:")
    for cls in GoodWay.__mro__:
        logging.info(f"{cls}")


# =============================
# 主函数运行所有示例
# =============================
def main():
    logging.info("===== 开始执行示例 =====\n")
    example_direct_init_call()
    logging.info("\n----------------------------------------\n")

    example_multiple_inheritance_conflict()
    logging.info("\n----------------------------------------\n")

    example_diamond_inheritance_issue()
    logging.info("\n----------------------------------------\n")

    example_super_and_mro()
    logging.info("\n===== 示例执行完毕 =====")


if __name__ == "__main__":
    main()
