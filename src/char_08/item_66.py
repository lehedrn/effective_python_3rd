"""
本模块演示了如何在 Python 中使用类装饰器和元类来扩展类的功能。
重点包括：
1. 使用函数装饰器对单个方法进行装饰；
2. 使用元类自动装饰所有方法；
3. 元类冲突问题及解决方式；
4. 使用类装饰器替代元类，实现更灵活的组合；
5. 展示错误示例与正确示例。

每个示例都封装为独立函数，并通过 main 函数调用执行。
"""

import logging
from functools import wraps
import types

# 配置日志输出
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ========================
# 工具函数：装饰器定义
# ========================

def trace_func(func):
    """用于打印函数调用细节的装饰器"""
    if hasattr(func, "tracing"):
        return func

    @wraps(func)
    def wrapper(*args, **kwargs):
        args_repr = repr(args)
        kwargs_repr = repr(kwargs)
        result = None
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            result = e
            raise
        finally:
            logger.info(f"{func.__name__}({args_repr}, {kwargs_repr}) -> {result!r}")

    wrapper.tracing = True
    return wrapper


# ========================
# 示例 1：手动装饰方法（冗余）
# ========================

class TraceDictManual(dict):
    @trace_func
    def __init__(self, *args, **kwargs):
        return super().__init__(*args, **kwargs)

    @trace_func
    def __setitem__(self, *args, **kwargs):
        return super().__setitem__(*args, **kwargs)

    @trace_func
    def __getitem__(self, *args, **kwargs):
        return super().__getitem__(*args, **kwargs)

def example_manual_decorator():
    """
    手动装饰每个方法，存在冗余代码且无法覆盖新增方法。
    """
    logger.info("=== 示例 1：手动装饰方法 ===")
    trace_dict = TraceDictManual([("hi", 1)])
    trace_dict["there"] = 2
    trace_dict["hi"]
    try:
        trace_dict["does not exist"]
    except KeyError:
        pass  # Expected


# ========================
# 示例 2：使用元类自动装饰
# ========================

TRACE_TYPES = (
    types.MethodType,
    types.FunctionType,
    types.BuiltinFunctionType,
    types.BuiltinMethodType,
    types.MethodDescriptorType,
    types.ClassMethodDescriptorType,
    types.WrapperDescriptorType,
)

IGNORE_METHODS = (
    "__repr__",
    "__str__",
)

class TraceMeta(type):
    def __new__(meta, name, bases, class_dict):
        klass = super().__new__(meta, name, bases, class_dict)

        for key in dir(klass):
            if key in IGNORE_METHODS:
                continue

            value = getattr(klass, key)
            if not isinstance(value, TRACE_TYPES):
                continue

            wrapped = trace_func(value)
            setattr(klass, key, wrapped)

        return klass

class TraceDictWithMeta(dict, metaclass=TraceMeta):
    pass

def example_metaclass_decorator():
    """
    使用元类自动装饰类中所有方法。
    """
    logger.info("=== 示例 2：使用元类自动装饰 ===")
    trace_dict = TraceDictWithMeta([("hi", 1)])
    trace_dict["there"] = 2
    trace_dict["hi"]
    try:
        trace_dict["does not exist"]
    except KeyError:
        pass  # Expected


# ========================
# 示例 3：元类冲突示例
# ========================

class OtherMeta(type):
    pass

# 错误示例：两个元类冲突
class SimpleDictWithOtherMeta(dict, metaclass=OtherMeta):
    pass

def example_metaclass_conflict():
    """
    错误示例：当子类同时继承具有不同元类的父类时，会抛出 TypeError。
    """

    logger.info("=== 示例 3：元类冲突示例（错误） ===")
    try:
        class ChildTraceDict(SimpleDictWithOtherMeta, metaclass=TraceMeta):
            pass
    except TypeError as e:
        logger.error(f"捕获到元类冲突异常: {e}")


# ========================
# 示例 4：使用类装饰器
# ========================

def trace(klass):
    """
    类装饰器：自动装饰类中的所有可调用属性。
    """
    for key in dir(klass):
        if key in IGNORE_METHODS:
            continue

        value = getattr(klass, key)
        if not isinstance(value, TRACE_TYPES):
            continue

        wrapped = trace_func(value)
        setattr(klass, key, wrapped)

    return klass

@trace
class DecoratedTraceDict(dict):
    pass

def example_class_decorator():
    """
    使用类装饰器替代元类，实现更灵活的类扩展。
    """
    logger.info("=== 示例 4：使用类装饰器 ===")
    trace_dict = DecoratedTraceDict([("hi", 1)])
    trace_dict["there"] = 2
    trace_dict["hi"]
    try:
        trace_dict["does not exist"]
    except KeyError:
        pass  # Expected


# ========================
# 示例 5：类装饰器与元类共存
# ========================

class OtherMeta(type):
    pass

@trace
class HasMetaTraceDict(dict, metaclass=OtherMeta):
    pass

def example_class_decorator_with_metaclass():
    """
    类装饰器可以与元类共存，避免了元类冲突的问题。
    """
    logger.info("=== 示例 5：类装饰器与元类共存 ===")
    trace_dict = HasMetaTraceDict([("hi", 1)])
    trace_dict["there"] = 2
    trace_dict["hi"]
    try:
        trace_dict["does not exist"]
    except KeyError:
        pass  # Expected


# ========================
# 主函数入口
# ========================

def main():
    example_manual_decorator()
    example_metaclass_decorator()
    example_metaclass_conflict()
    example_class_decorator()
    example_class_decorator_with_metaclass()


if __name__ == "__main__":
    main()

