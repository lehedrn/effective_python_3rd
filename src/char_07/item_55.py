"""
本模块演示了 Python 类中优先使用公共属性而非私有属性的设计原则，
包括错误示例与正确示例，涵盖命名冲突、继承问题和受保护字段的合理使用。

目标：
1. 展示 Python 中私有属性（__name）与受保护属性（_name）的区别
2. 演示私有属性在继承中的问题及子类访问失败的情况
3. 提供正确的做法：使用受保护字段并配合文档说明
4. 通过 logging 替代 print 输出日志信息，符合生产环境规范
"""

import logging

# 配置 logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# -----------------------------
# 示例1: 私有属性的基本行为
# -----------------------------
class MyObject:
    def __init__(self):
        self.public_field = 5
        self.__private_field = 10

    def get_private_field(self):
        return self.__private_field


def private_attribute_basic():
    """
    演示私有属性的基本行为：
    - 私有属性不能从外部直接访问
    - 类方法可以访问私有属性
    """
    obj = MyObject()

    # 公共属性可直接访问
    logging.info(f"Public field: {obj.public_field}")

    # 尝试直接访问私有属性会抛出异常
    try:
        logging.info(f"Trying to access private field directly: {obj.__private_field}")
    except AttributeError as e:
        logging.warning(f"Caught error: {e}")

    # 类方法可以访问私有属性
    logging.info(f"Access private field via method: {obj.get_private_field()}")


# -----------------------------
# 示例2: 子类无法访问父类私有属性
# -----------------------------
class MyParentObject:
    def __init__(self):
        self.__private_field = 71


class MyChildObject(MyParentObject):
    def get_private_field(self):
        return self.__private_field  # 实际上访问不到


def subclass_cannot_access_private():
    """
    演示子类无法访问父类私有属性的问题。
    Python 会对私有属性进行名称转换（name mangling），导致访问失败。
    """
    child = MyChildObject()

    try:
        logging.info("Trying to access parent's private field in child class...")
        child.get_private_field()
    except AttributeError as e:
        logging.error(f"Failed to access private field: {e}")


# -----------------------------
# 示例3: 手动绕过私有属性限制
# -----------------------------
def bypass_private_restriction():
    """
    演示如何手动绕过私有属性限制（不推荐）
    Python 的私有属性只是一种约定，不是严格的访问控制。
    """
    child = MyChildObject()

    # 通过了解 name mangling 机制间接访问私有属性
    logging.info("Manually bypassing private attribute restriction:")
    logging.info(f"Access via name mangling: {child._MyParentObject__private_field}")


# -----------------------------
# 示例4: 使用私有属性防止命名冲突
# -----------------------------
class ApiClass:
    def __init__(self):
        self.__value = 5   # 私有属性避免冲突

    def get_value(self):
        return self.__value


class Child(ApiClass):
    def __init__(self):
        super().__init__()
        self._value = "hello"  # 安全定义自己的 _value


def prevent_naming_conflict():
    """
    演示使用私有属性避免命名冲突的合理场景。
    父类使用私有属性以避免子类无意中覆盖。
    """
    instance = Child()
    logging.info(f"ApiClass value: {instance.get_value()}")
    logging.info(f"Child own value: {instance._value}")


# -----------------------------
# 示例5: 不推荐的做法 - 使用私有属性限制子类扩展
# -----------------------------
class MyStringClass:
    def __init__(self, value):
        self.__value = value

    def get_value(self):
        return str(self.__value)


class MyIntegerSubclass(MyStringClass):
    def get_value(self):
        return int(self._MyStringClass__value)  # 强行绕过访问限制


def bad_practice_restrict_subclass_extension():
    """
    错误示例：使用私有属性限制子类扩展能力。
    这种方式会带来脆弱性和维护难题。
    """
    obj = MyIntegerSubclass("5")
    logging.info(f"Bad practice subclass value: {obj.get_value()}")


# -----------------------------
# 示例6: 推荐做法 - 使用受保护属性 + 文档说明
# -----------------------------
class MyStringClassGood:
    def __init__(self, value):
        # 受保护属性建议子类谨慎使用
        self._value = value

    def get_value(self):
        return str(self._value)


class MyIntegerSubclassGood(MyStringClassGood):
    def get_value(self):
        return self._value  # 直接使用受保护属性


def good_practice_use_protected_fields():
    """
    正确示例：使用受保护属性并配合适当文档说明。
    更加灵活，便于子类安全扩展。
    """
    obj = MyIntegerSubclassGood(5)
    logging.info(f"Good practice subclass value: {obj.get_value()}")


# -----------------------------
# 主函数运行所有示例
# -----------------------------
def main():
    logging.info("=== 开始执行示例1：私有属性基本行为 ===")
    private_attribute_basic()

    logging.info("\n=== 开始执行示例2：子类无法访问父类私有属性 ===")
    subclass_cannot_access_private()

    logging.info("\n=== 开始执行示例3：手动绕过私有属性限制 ===")
    bypass_private_restriction()

    logging.info("\n=== 开始执行示例4：使用私有属性防止命名冲突 ===")
    prevent_naming_conflict()

    logging.info("\n=== 开始执行示例5：错误做法 - 使用私有属性限制子类扩展 ===")
    bad_practice_restrict_subclass_extension()

    logging.info("\n=== 开始执行示例6：推荐做法 - 使用受保护属性 + 文档说明 ===")
    good_practice_use_protected_fields()


if __name__ == '__main__':
    main()
