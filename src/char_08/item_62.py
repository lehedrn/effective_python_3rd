"""
本模块演示了如何使用 `__init_subclass__` 验证子类，替代传统的元类（metaclass）验证方式。
涵盖了以下内容：
- 使用元类进行子类验证的示例；
- 使用 `__init_subclass__` 替代元类进行验证；
- 多重继承中组合多个验证逻辑；
- 错误示例与正确示例对比；
- 使用 logging 代替 print 进行日志输出；
- 每个示例封装为独立函数，并在 main 中统一调用；
"""

import logging

# 设置日志格式
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def example_1_metaclass_validation():
    """
    示例 1：使用元类 ValidatePolygon 对 Polygon 子类进行验证。
    错误示例：定义边数小于 3 的 Line 类。
    正确示例：Triangle 和 Rectangle 符合要求。
    """

    class ValidatePolygon(type):
        def __new__(meta, name, bases, class_dict):
            if bases:  # 只验证子类
                if class_dict["sides"] < 3:
                    raise ValueError("Polygons need 3+ sides")
            return type.__new__(meta, name, bases, class_dict)

    class Polygon(metaclass=ValidatePolygon):
        sides = None

        @classmethod
        def interior_angles(cls):
            return (cls.sides - 2) * 180

    try:
        logger.info("尝试创建一个错误的类：Line（边数小于3）")

        class Line(Polygon):
            sides = 2  # 错误：边数不足

    except ValueError as e:
        logger.error(f"捕获到异常（预期）：{e}")

    logger.info("创建合法的类：Triangle 和 Rectangle")

    class Triangle(Polygon):
        sides = 3

    class Rectangle(Polygon):
        sides = 4

    assert Triangle.interior_angles() == 180
    assert Rectangle.interior_angles() == 360
    logger.info("验证通过：Triangle 和 Rectangle 合法")


def example_2_init_subclass_validation():
    """
    示例 2：使用 __init_subclass__ 替代元类验证。
    错误示例：Point 类边数为1。
    正确示例：Hexagon 边数为6。
    """

    class BetterPolygon:
        sides = None

        def __init_subclass__(cls, **kwargs):
            super().__init_subclass__(**kwargs)
            if cls.sides < 3:
                raise ValueError("Polygons need 3+ sides")

        @classmethod
        def interior_angles(cls):
            return (cls.sides - 2) * 180

    try:
        logger.info("尝试创建一个错误的类：Point（边数为1）")

        class Point(BetterPolygon):
            sides = 1  # 错误：边数不足

    except ValueError as e:
        logger.error(f"捕获到异常（预期）：{e}")

    logger.info("创建合法的类：Hexagon（边数为6）")

    class Hexagon(BetterPolygon):
        sides = 6

    assert Hexagon.interior_angles() == 720
    logger.info("验证通过：Hexagon 合法")


def example_3_multiple_inheritance_with_init_subclass():
    """
    示例 3：多重继承中使用 __init_subclass__ 实现多层验证。
    错误示例：BlueLine 边数为2；BeigeSquare 颜色不合法。
    正确示例：RedTriangle 同时满足颜色和边数要求。
    """

    class Filled:
        color = None

        def __init_subclass__(cls, **kwargs):
            super().__init_subclass__(**kwargs)
            if cls.color not in ("red", "green", "blue"):
                raise ValueError("Fills need a valid color")

    class BetterPolygon:
        sides = None

        def __init_subclass__(cls, **kwargs):
            super().__init_subclass__(**kwargs)
            if cls.sides < 3:
                raise ValueError("Polygons need 3+ sides")

        @classmethod
        def interior_angles(cls):
            return (cls.sides - 2) * 180

    try:
        logger.info("尝试创建错误的类：BlueLine（边数为2）")

        class BlueLine(Filled, BetterPolygon):
            color = "blue"
            sides = 2  # 错误：边数不足

    except ValueError as e:
        logger.error(f"捕获到异常（预期）：{e}")

    try:
        logger.info("尝试创建错误的类：BeigeSquare（颜色不合法）")

        class BeigeSquare(Filled, BetterPolygon):
            color = "beige"
            sides = 4  # 错误：颜色非法

    except ValueError as e:
        logger.error(f"捕获到异常（预期）：{e}")

    logger.info("创建合法的类：RedTriangle（颜色和边数均合法）")

    class RedTriangle(Filled, BetterPolygon):
        color = "red"
        sides = 3

    assert RedTriangle.interior_angles() == 180
    logger.info("验证通过：RedTriangle 合法")


def example_4_diamond_inheritance_with_init_subclass():
    """
    示例 4：菱形继承中使用 __init_subclass__。
    展示了多层 __init_subclass__ 调用顺序。
    """

    class Top:
        def __init_subclass__(cls, **kwargs):
            super().__init_subclass__(**kwargs)
            logger.info(f"Top 初始化 {cls}")

    class Left(Top):
        def __init_subclass__(cls, **kwargs):
            super().__init_subclass__(**kwargs)
            logger.info(f"Left 初始化 {cls}")

    class Right(Top):
        def __init_subclass__(cls, **kwargs):
            super().__init_subclass__(**kwargs)
            logger.info(f"Right 初始化 {cls}")

    class Bottom(Left, Right):
        def __init_subclass__(cls, **kwargs):
            super().__init_subclass__(**kwargs)
            logger.info(f"Bottom 初始化 {cls}")

    logger.info("显式触发 Bottom 类加载")
    _ = Bottom


def main():
    logger.info("开始执行示例 1：元类验证")
    example_1_metaclass_validation()

    logger.info("\n开始执行示例 2：使用 __init_subclass__ 验证")
    example_2_init_subclass_validation()

    logger.info("\n开始执行示例 3：多重继承中的 __init_subclass__")
    example_3_multiple_inheritance_with_init_subclass()

    logger.info("\n开始执行示例 4：菱形继承中的 __init_subclass__")
    example_4_diamond_inheritance_with_init_subclass()


if __name__ == "__main__":
    main()
