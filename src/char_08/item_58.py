"""
本模块演示了如何在 Python 中使用 `@property` 和普通属性来替代传统的 getter/setter 方法。
它涵盖了以下内容：
- 使用简单公共属性代替 getter 和 setter 的好处
- 如何使用 `@property` 实现属性访问控制
- 验证属性值、创建只读属性等场景
- 错误用法示例及正确做法

遵循 PEP8 规范，并使用 logging 代替 print 输出信息，便于调试和日志记录。
"""

import logging

# 设置日志配置
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# 示例 1: 传统 getter/setter 的使用（不推荐）
def example_old_resistor():
    """
    演示传统方式实现的电阻类，使用显式的 getter 和 setter 方法。
    缺点：代码冗长，难以进行就地操作（如加减）。
    """

    class OldResistor:
        def __init__(self, ohms):
            self._ohms = ohms

        def get_ohms(self):
            return self._ohms

        def set_ohms(self, ohms):
            self._ohms = ohms

    r0 = OldResistor(50e3)
    logging.info(f"Before: {r0.get_ohms()}")
    r0.set_ohms(10e3)
    logging.info(f"After: {r0.get_ohms()}")

    # 就地操作非常笨拙
    r0.set_ohms(r0.get_ohms() - 4e3)
    assert r0.get_ohms() == 6e3


# 示例 2: 使用公共属性（推荐）
def example_public_attributes():
    """
    使用简单的公共属性替代 getter/setter，使代码更简洁直观。
    支持自然的赋值和就地操作。
    """

    class Resistor:
        def __init__(self, ohms):
            self.ohms = ohms
            self.voltage = 0
            self.current = 0

    r1 = Resistor(50e3)
    r1.ohms = 10e3
    r1.ohms += 5e3  # 自然支持就地操作
    logging.info(f"Current ohms: {r1.ohms}")


# 示例 3: 使用 @property 实现电压与电流联动更新
def example_voltage_property():
    """
    使用 @property 控制 voltage 属性的赋值行为，自动更新 current。
    展示了属性之间的依赖关系。
    """

    class VoltageResistance:
        def __init__(self, ohms):
            self._voltage = 0
            self.ohms = ohms
            self.current = 0

        @property
        def voltage(self):
            return self._voltage

        @voltage.setter
        def voltage(self, value):
            self._voltage = value
            self.current = self._voltage / self.ohms

    r2 = VoltageResistance(1e2)
    logging.info(f"Before: {r2.current:.2f} amps")
    r2.voltage = 10
    logging.info(f"After: {r2.current:.2f} amps")


# 示例 4: 使用 @property 进行值验证
def example_value_validation():
    """
    使用 @property 对 ohms 属性进行值验证，确保大于零。
    构造函数中也触发验证逻辑。
    """

    class BoundedResistance:
        def __init__(self, ohms):
            self.ohms = ohms

        @property
        def ohms(self):
            return self._ohms

        @ohms.setter
        def ohms(self, value):
            if value <= 0:
                raise ValueError(f"ohms must be > 0; got {value}")
            self._ohms = value

    try:
        r3 = BoundedResistance(1e3)
        r3.ohms = 0  # 应该抛出异常
    except ValueError as e:
        logging.warning(f"Caught error: {e}")

    try:
        BoundedResistance(-5)  # 构造时也会抛出异常
    except ValueError as e:
        logging.warning(f"Caught error during construction: {e}")


# 示例 5: 使用 @property 创建只读属性
def example_readonly_property():
    """
    使用 @property 和 setter 实现只读属性。
    在对象构造完成后不允许修改 ohms。
    """

    class FixedResistance:
        def __init__(self, ohms):
            self._ohms = ohms

        @property
        def ohms(self):
            return self._ohms

        @ohms.setter
        def ohms(self, value):
            if hasattr(self, '_ohms'):
                raise AttributeError("Ohms is immutable")
            self._ohms = value

    r4 = FixedResistance(1e3)
    logging.info(f"Initial ohms: {r4.ohms}")
    try:
        r4.ohms = 2e3  # 构造后禁止修改
    except AttributeError as e:
        logging.warning(f"Caught readonly error: {e}")


# 示例 6: 不推荐的做法 - 在 getter 中引入副作用
def example_side_effect_in_getter():
    """
    错误示范：在 @property getter 中引入副作用（修改其他属性），导致不可预测的行为。
    """

    class MysteriousResistor:
        def __init__(self, ohms):
            self._ohms = ohms
            self.current = 0
            self.voltage = 0

        @property
        def ohms(self):
            self.voltage = self._ohms * self.current  # 不应该在这里修改其他属性
            return self._ohms

        @ohms.setter
        def ohms(self, value):
            self._ohms = value

    r7 = MysteriousResistor(10)
    r7.current = 0.1
    logging.info(f"Before: {r7.voltage:.2f}")
    _ = r7.ohms  # 调用 getter 导致 voltage 被修改
    logging.info(f"After: {r7.voltage:.2f}")


# 主函数运行所有示例
def main():
    logging.info("=== Example 1: 传统 getter/setter ===")
    example_old_resistor()

    logging.info("=== Example 2: 公共属性 ===")
    example_public_attributes()

    logging.info("=== Example 3: voltage 属性联动 ===")
    example_voltage_property()

    logging.info("=== Example 4: 值验证 ===")
    example_value_validation()

    logging.info("=== Example 5: 只读属性 ===")
    example_readonly_property()

    logging.info("=== Example 6: 错误做法 - getter 引入副作用 ===")
    example_side_effect_in_getter()


if __name__ == '__main__':
    main()
