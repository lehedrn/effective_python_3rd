"""
本文件展示了 Python 中 __getattr__, __getattribute__, __setattr__ 的使用示例。
这些方法用于实现对对象属性的动态处理，包括延迟加载、属性访问控制以及赋值拦截等场景。
每个示例都包含错误和正确用法，并附有详细的解释。
"""

import logging

# 配置日志输出
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def example_getattr_basic():
    """
    示例1: 基础 __getattr__ 使用
    说明:
        当访问不存在的属性时，会调用 __getattr__ 方法。
        该方法可用于实现延迟加载机制。
    """

    class LazyRecord:
        def __init__(self):
            self.exists = 5

        def __getattr__(self, name):
            logger.info(f"__getattr__: 属性 {name} 不存在，正在生成...")
            value = f"Value for {name}"
            setattr(self, name, value)
            return value

    logger.info("初始化对象")
    data = LazyRecord()
    logger.info(f"访问已存在属性 exists: {data.exists}")
    logger.info(f"首次访问缺失属性 foo: {data.foo}")
    logger.info(f"再次访问属性 foo (此时应从 __dict__ 获取): {data.foo}")


def example_getattr_with_inheritance():
    """
    示例2: 继承中的 __getattr__
    说明:
        子类重写 __getattr__ 时，应该使用 super() 调用父类方法，避免无限递归。
    """

    class LazyRecord:
        def __getattr__(self, name):
            value = f"Base value for {name}"
            setattr(self, name, value)
            return value

    class LoggingLazyRecord(LazyRecord):
        def __getattr__(self, name):
            logger.info(f"LoggingLazyRecord.__getattr__({name!r}) called")
            result = super().__getattr__(name)  # 正确使用 super
            logger.info(f"返回结果: {result!r}")
            return result

    data = LoggingLazyRecord()
    logger.info(f"首次访问属性 bar: {data.bar}")
    logger.info(f"再次访问属性 bar: {data.bar}")


def example_getattribute_basic():
    """
    示例3: __getattribute__ 的基本使用
    说明:
        不论属性是否存在，都会调用 __getattribute__。
        可用于全局状态检查（如事务有效性）。
    """

    class ValidatingRecord:
        def __init__(self):
            self.exists = 5

        def __getattribute__(self, name):
            logger.info(f"__getattribute__({name!r}) called")
            try:
                return super().__getattribute__(name)
            except AttributeError:
                value = f"Value for {name}"
                logger.info(f"设置新属性 {name!r} 为 {value!r}")
                setattr(self, name, value)
                return value

    data = ValidatingRecord()
    logger.info(f"访问已存在属性 exists: {data.exists}")
    logger.info(f"首次访问缺失属性 baz: {data.baz}")
    logger.info(f"再次访问属性 baz: {data.baz}")


def example_getattribute_recursion_error():
    """
    错误示例: __getattribute__ 中导致递归崩溃
    说明:
        在 __getattribute__ 中直接访问 self._data 会导致无限递归。
    """

    class BrokenDictionaryRecord:
        def __init__(self, data):
            self._data = data

        def __getattribute__(self, name):
            logger.info(f"__getattribute__({name!r}) called")
            return self._data[name]  # 这将引发 RecursionError

    try:
        data = BrokenDictionaryRecord({"key": "value"})
        _ = data.key
    except RecursionError as e:
        logger.error(f"捕获到递归异常: {e}")


def example_getattribute_correct_usage():
    """
    示例4: 正确使用 __getattribute__ 访问实例字典
    说明:
        应使用 super().__getattribute__ 来访问内部变量以避免递归。
    """

    class DictionaryRecord:
        def __init__(self, data):
            self._data = data

        def __getattribute__(self, name):
            if name == "__class__":
                return DictionaryRecord
            logger.info(f"__getattribute__({name!r}) called")
            data_dict = super().__getattribute__("_data")  # 安全获取内部变量
            return data_dict[name]

    data = DictionaryRecord({"key": "value"})
    logger.info(f"访问属性 key: {data.key}")


def example_setattr_basic():
    """
    示例5: __setattr__ 的基础使用
    说明:
        拦截所有属性赋值操作，可用于数据验证或记录变更。
    """

    class SavingRecord:
        def __setattr__(self, name, value):
            logger.info(f"__setattr__({name!r}, {value!r}) called")
            super().__setattr__(name, value)

    data = SavingRecord()
    data.name = "Alice"
    data.name = "Bob"


def example_setattr_recursion_error():
    """
    错误示例: __setattr__ 中引发无限递归
    说明:
        直接使用 self.name = value 将再次触发 __setattr__，导致死循环。
    """

    class RecursiveSetter:
        def __setattr__(self, name, value):
            self.name = value  # 错误：递归调用 __setattr__

    try:
        obj = RecursiveSetter()
        obj.value = 42  # 将引发 RecursionError
    except RecursionError as e:
        logger.error(f"捕获到递归异常: {e}")


def example_missing_property():
    """
    示例6: 抛出 AttributeError 表示属性缺失
    说明:
        如果某些属性不应存在，可以抛出 AttributeError。
    """

    class MissingPropertyRecord:
        def __getattr__(self, name):
            if name == "bad_name":
                raise AttributeError(f"{name} 不存在")
            return f"Value for {name}"

    data = MissingPropertyRecord()
    try:
        _ = data.bad_name
    except AttributeError as e:
        logger.error(f"捕获到 AttributeError: {e}")

    logger.info(f"访问 good_name: {data.good_name}")


def main():
    logger.info("===== 示例 1: 基础 __getattr__ =====")
    example_getattr_basic()

    logger.info("===== 示例 2: 继承中的 __getattr__ =====")
    example_getattr_with_inheritance()

    logger.info("===== 示例 3: __getattribute__ 基础用法 =====")
    example_getattribute_basic()

    logger.info("===== 错误示例: __getattribute__ 导致递归 =====")
    example_getattribute_recursion_error()

    logger.info("===== 示例 4: 正确使用 __getattribute__ =====")
    example_getattribute_correct_usage()

    logger.info("===== 示例 5: __setattr__ 基础用法 =====")
    example_setattr_basic()

    logger.info("===== 错误示例: __setattr__ 导致递归 =====")
    example_setattr_recursion_error()

    logger.info("===== 示例 6: 抛出 AttributeError =====")
    example_missing_property()


if __name__ == "__main__":
    main()
