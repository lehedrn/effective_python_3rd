"""
本模块演示了以下技术点：
- 使用冗余参数手动绑定字段名称的问题。
- 使用元类（metaclass）自动绑定字段名。
- 使用 __set_name__ 替代元类实现更简洁的字段绑定。
- 未继承元类基类导致的运行时错误。
- 推荐做法：在描述符中定义 __set_name__ 自动获取属性名。

每个示例封装为独立函数，main 函数统一调度。
日志系统替代 print，代码符合 PEP8 规范。
"""

import logging

# 初始化日志配置
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# =============================
# 示例1：手动传递字段名（冗余写法）
# =============================
class FieldWithManualName:
    """
    手动传入字段名，用于将属性名映射到内部存储名（例如 first_name -> _first_name）。
    这种写法会导致重复声明字段名，不够优雅。
    """

    def __init__(self, column_name):
        self.column_name = column_name
        self.internal_name = "_" + self.column_name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return getattr(instance, self.internal_name, "")

    def __set__(self, instance, value):
        setattr(instance, self.internal_name, value)


class ManualCustomer:
    """手动传入字段名的客户类示例"""
    first_name = FieldWithManualName("first_name")
    last_name = FieldWithManualName("last_name")


def manual_example():
    logger.info("=== 示例1: 手动绑定字段名 ===")
    cust = ManualCustomer()
    logger.info(f"Before setting: {cust.first_name!r}, {cust.__dict__}")
    cust.first_name = "Euclid"
    logger.info(f"After setting: {cust.first_name!r}, {cust.__dict__}")


# =============================
# 示例2：使用元类自动绑定字段名
# =============================
class FieldWithAutoName:
    """
    字段类，构造时不需传参，由元类在类创建时注入字段名。
    """

    def __init__(self):
        self.column_name = None
        self.internal_name = None

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return getattr(instance, self.internal_name, "")

    def __set__(self, instance, value):
        setattr(instance, self.internal_name, value)

class Meta(type):
    """
    元类，在类定义完成后遍历所有属性，
    如果是 FieldWithAutoName 类型，则自动设置其 column_name 和 internal_name。
    """

    def __new__(cls, name, bases, class_dict):
        for key, value in class_dict.items():
            if isinstance(value, FieldWithAutoName):
                value.column_name = key
                value.internal_name = "_" + key
        return type.__new__(cls, name, bases, class_dict)


class DatabaseRow(metaclass=Meta):
    """所有需要字段绑定的类应继承此类"""
    pass

class BetterCustomer(DatabaseRow):
    first_name = FieldWithAutoName()
    last_name = FieldWithAutoName()


def metaclass_example():
    logger.info("=== 示例2: 使用元类自动绑定字段名 ===")
    cust = BetterCustomer()
    logger.info(f"Before setting: {cust.first_name!r}, {cust.__dict__}")
    cust.first_name = "Euler"
    logger.info(f"After setting: {cust.first_name!r}, {cust.__dict__}")


# =============================
# 示例3：错误用法 - 未继承 DatabaseRow
# =============================
class BrokenCustomer:
    """错误示例：未继承 DatabaseRow 导致无法自动设置字段信息"""
    first_name = FieldWithAutoName()
    last_name = FieldWithAutoName()


def broken_example():
    logger.info("=== 示例3: 错误用法 - 未继承元类基类 ===")
    try:
        cust = BrokenCustomer()
        cust.first_name = "Mersenne"  # 将引发 TypeError
    except TypeError as e:
        logger.error(f"捕获异常：{e}")


# =============================
# 示例4：使用 __set_name__ 替代元类（推荐做法）
# =============================
class FieldWithSetName:
    """
    描述符类，利用 __set_name__ 方法自动获取被赋值的属性名，
    不再需要继承特定基类或使用元类。
    """

    def __init__(self):
        self.column_name = None
        self.internal_name = None

    def __set_name__(self, owner, name):
        self.column_name = name
        self.internal_name = "_" + name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return getattr(instance, self.internal_name, "")

    def __set__(self, instance, value):
        setattr(instance, self.internal_name, value)


class FixedCustomer:
    """无需继承任何基类即可使用描述符"""
    first_name = FieldWithSetName()
    last_name = FieldWithSetName()


def set_name_example():
    logger.info("=== 示例4: 使用 __set_name__ 替代元类 ===")
    cust = FixedCustomer()
    logger.info(f"Before setting: {cust.first_name!r}, {cust.__dict__}")
    cust.first_name = "Mersenne"
    logger.info(f"After setting: {cust.first_name!r}, {cust.__dict__}")


# =============================
# 主函数入口
# =============================
def main():
    manual_example()
    metaclass_example()
    broken_example()
    set_name_example()


if __name__ == "__main__":
    main()
