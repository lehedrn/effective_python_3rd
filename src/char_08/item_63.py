"""
本模块演示了如何使用 `__init_subclass__` 和元类来实现类的自动注册机制。
包括错误示例和正确示例，展示了序列化与反序列化的过程，
以及如何避免忘记调用 `register_class` 的问题。

特性：
- 使用 logging 替代 print 输出日志信息
- 所有代码符合 PEP8 规范
- 每个功能封装为独立函数
- 包含清晰的中文注释说明
"""

import json
import logging

# 配置 logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# 示例 1：基础序列化类（未包含类名）
class Serializable:
    def __init__(self, *args):
        self.args = args

    def serialize(self):
        return json.dumps({"args": self.args})

    def __repr__(self):
        name = self.__class__.__name__
        args_str = ", ".join(str(x) for x in self.args)
        return f"{name}({args_str})"


def example_basic_serialization():
    """展示基础的序列化功能，但无法通过类名反序列化。"""

    class Point2D(Serializable):
        def __init__(self, x, y):
            super().__init__(x, y)
            self.x = x
            self.y = y

    point = Point2D(5, 3)
    logger.info("Object: %s", point)
    logger.info("Serialized: %s", point.serialize())


# 示例 2：可反序列化的类（需要提前知道类型）
class Deserializable(Serializable):
    @classmethod
    def deserialize(cls, json_data):
        params = json.loads(json_data)
        return cls(*params["args"])


def example_deserializable():
    """展示基于已知类型的反序列化功能。"""

    class BetterPoint2D(Deserializable):
        def __init__(self, x, y):
            super().__init__(x, y)
            self.x = x
            self.y = y

    before = BetterPoint2D(5, 3)
    logger.info("Before: %s", before)
    data = before.serialize()
    logger.info("Serialized: %s", data)
    after = BetterPoint2D.deserialize(data)
    logger.info("After: %s", after)


# 示例 3：错误示例 - 忘记注册类导致反序列化失败
REGISTRY = {}


def register_class(target_class):
    REGISTRY[target_class.__name__] = target_class


def deserialize(data):
    params = json.loads(data)
    name = params["class"]
    target_class = REGISTRY[name]
    return target_class(*params["args"])


def example_forget_to_register():
    """错误示例：定义了类但忘记注册，导致反序列化失败。"""

    class Point3D(BetterSerializable):
        def __init__(self, x, y, z):
            super().__init__(x, y, z)
            self.x = x
            self.y = y
            self.z = z

    try:
        point = Point3D(5, 9, -4)
        data = point.serialize()
        deserialize(data)  # KeyError: 'Point3D'
    except KeyError as e:
        logger.error("KeyError: %s - 忘记注册类导致反序列化失败", e)


# 示例 4：使用带有类名的序列化基类
class BetterSerializable:
    def __init__(self, *args):
        self.args = args

    def serialize(self):
        return json.dumps(
            {
                "class": self.__class__.__name__,
                "args": self.args,
            }
        )

    def __repr__(self):
        name = self.__class__.__name__
        args_str = ", ".join(str(x) for x in self.args)
        return f"{name}({args_str})"


def example_with_class_name():
    """展示带类名的序列化功能。"""

    class EvenBetterPoint2D(BetterSerializable):
        def __init__(self, x, y):
            super().__init__(x, y)
            self.x = x
            self.y = y

    register_class(EvenBetterPoint2D)

    before = EvenBetterPoint2D(5, 3)
    logger.info("Before: %s", before)
    data = before.serialize()
    logger.info("Serialized: %s", data)
    after = deserialize(data)
    logger.info("After: %s", after)


# 示例 5：使用元类自动注册子类
class Meta(type):
    def __new__(meta, name, bases, class_dict):
        cls = type.__new__(meta, name, bases, class_dict)
        register_class(cls)
        return cls


class RegisteredSerializable(BetterSerializable, metaclass=Meta):
    pass


def example_with_metaclass():
    """展示使用元类自动注册子类的功能。"""

    class Vector3D(RegisteredSerializable):
        def __init__(self, x, y, z):
            super().__init__(x, y, z)
            self.x, self.y, self.z = x, y, z

    before = Vector3D(10, -7, 3)
    logger.info("Before: %s", before)
    data = before.serialize()
    logger.info("Serialized: %s", data)
    after = deserialize(data)
    logger.info("After: %s", after)


# 示例 6：使用 `__init_subclass__` 自动注册子类
class BetterRegisteredSerializable(BetterSerializable):
    def __init_subclass__(cls):
        super().__init_subclass__()
        register_class(cls)


def example_with_init_subclass():
    """展示使用 `__init_subclass__` 自动注册子类的功能。"""

    class Vector1D(BetterRegisteredSerializable):
        def __init__(self, magnitude):
            super().__init__(magnitude)
            self.magnitude = magnitude

    before = Vector1D(6)
    logger.info("Before: %s", before)
    data = before.serialize()
    logger.info("Serialized: %s", data)
    after = deserialize(data)
    logger.info("After: %s", after)


def main():
    logger.info("=== 示例 1：基础序列化 ===")
    example_basic_serialization()

    logger.info("\n=== 示例 2：基于已知类型的反序列化 ===")
    example_deserializable()

    logger.info("\n=== 示例 3：错误示例 - 忘记注册类 ===")
    example_forget_to_register()

    logger.info("\n=== 示例 4：带类名的序列化 ===")
    example_with_class_name()

    logger.info("\n=== 示例 5：使用元类自动注册子类 ===")
    example_with_metaclass()

    logger.info("\n=== 示例 6：使用 `__init_subclass__` 自动注册子类 ===")
    example_with_init_subclass()


if __name__ == "__main__":
    main()
