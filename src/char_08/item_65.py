"""
本模块演示了如何通过类体定义顺序来建立属性之间的关系。
涵盖了以下内容：
- 使用 `__init_subclass__` 自动发现子类中定义的字段或方法
- 利用类体定义顺序控制程序行为（如CSV映射、工作流执行等）
- 使用描述符实现字段类型转换
- 错误示例与正确示例对比
"""

import logging
from typing import Any, Callable, Dict, List, Tuple, Type

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# 示例 1：基础 RowMapper 类，使用 fields 元组显式声明字段
class RowMapper:
    """
    基础类，用于将 CSV 行数据映射为对象属性。
    """

    fields = ()  # 子类必须重写此元组，表示字段顺序

    def __init__(self, **kwargs: Dict[str, Any]):
        for key, value in kwargs.items():
            if key not in type(self).fields:
                raise TypeError(f"Invalid field: {key}")
            setattr(self, key, value)

    @classmethod
    def from_row(cls, row: List[Any]) -> 'RowMapper':
        if len(row) != len(cls.fields):
            raise ValueError("Wrong number of fields")
        kwargs = dict(pair for pair in zip(cls.fields, row))
        return cls(**kwargs)


class DeliveryMapper(RowMapper):
    """
    使用字符串元组定义字段顺序的子类
    """
    fields = ("destination", "method", "weight")


def example_1() -> None:
    """
    示例 1：展示 RowMapper 的基本用法
    """
    logger.info("开始示例 1：RowMapper 基本用法")

    row = ["Sydney", "truck", "25"]
    obj = DeliveryMapper.from_row(row)
    logger.info(f"目标地: {obj.destination}, 方法: {obj.method}, 重量: {obj.weight}")

    try:
        DeliveryMapper.from_row(["Sydney"])
    except ValueError as e:
        logger.warning(f"错误处理成功: {e}")


# 示例 2：BetterRowMapper 使用省略号和 __init_subclass__ 自动发现字段
class BetterRowMapper(RowMapper):
    """
    更加 Pythonic 的 RowMapper 实现，自动从类体中提取字段名
    """

    def __init_subclass__(cls):
        fields = []
        for key, value in cls.__dict__.items():
            if value is Ellipsis:
                fields.append(key)
        cls.fields = tuple(fields)


class BetterDeliveryMapper(BetterRowMapper):
    """
    使用类体定义字段顺序的子类
    """
    destination = ...
    method = ...
    weight = ...


def example_2() -> None:
    """
    示例 2：展示 BetterRowMapper 使用类体定义字段顺序
    """
    logger.info("开始示例 2：BetterRowMapper 使用类体定义字段顺序")

    row = ["Sydney", "truck", "25"]
    obj = BetterDeliveryMapper.from_row(row)
    logger.info(f"目标地: {obj.destination}, 方法: {obj.method}, 重量: {obj.weight}")

    class InvalidOrderMapper(BetterRowMapper):
        method = ...
        weight = ...  # 缺少一个字段

    try:
        InvalidOrderMapper.from_row(["road train", "90"])
    except ValueError as e:
        logger.warning(f"字段数量不匹配错误处理成功: {e}")


# 示例 3：DescriptorRowMapper 使用描述符实现字段验证和类型转换
class Field:
    """
    描述符基类，支持字段验证和类型转换
    """

    def __init__(self):
        self.internal_name = None

    def __set_name__(self, owner: Type, column_name: str):
        self.internal_name = "_" + column_name

    def __get__(self, instance: Any, instance_type: Type) -> Any:
        if instance is None:
            return self
        return getattr(instance, self.internal_name, "")

    def __set__(self, instance: Any, value: Any) -> None:
        adjusted_value = self.convert(value)
        setattr(instance, self.internal_name, adjusted_value)

    def convert(self, value: Any) -> Any:
        raise NotImplementedError


class StringField(Field):
    def convert(self, value: Any) -> str:
        if not isinstance(value, str):
            raise ValueError("Value must be a string")
        return value


class FloatField(Field):
    def convert(self, value: Any) -> float:
        return float(value)


class DescriptorRowMapper(RowMapper):
    def __init_subclass__(cls):
        fields = []
        for key, value in cls.__dict__.items():
            if isinstance(value, Field):
                fields.append(key)
        cls.fields = tuple(fields)


class ConvertingDeliveryMapper(DescriptorRowMapper):
    destination = StringField()
    method = StringField()
    weight = FloatField()


def example_3() -> None:
    """
    示例 3：使用描述符实现字段验证和类型转换
    """
    logger.info("开始示例 3：使用描述符实现字段验证和类型转换")

    row = ["Sydney", "truck", "25"]
    obj = ConvertingDeliveryMapper.from_row(row)
    logger.info(f"目标地: {obj.destination}, 方法: {obj.method}, 重量: {obj.weight} (类型: {type(obj.weight)})")

    try:
        ConvertingDeliveryMapper.from_row(["Sydney", "truck", "twenty-five"])
    except ValueError as e:
        logger.warning(f"类型转换失败错误处理成功: {e}")


# 示例 4：Workflow 类使用装饰器标记步骤并按定义顺序运行
def step(func: Callable) -> Callable:
    func._is_step = True
    return func


class Workflow:
    def __init_subclass__(cls):
        steps = []
        for key, value in cls.__dict__.items():
            if callable(value) and hasattr(value, "_is_step"):
                steps.append(key)
        cls.steps = tuple(steps)

    def run(self) -> None:
        for step_name in type(self).steps:
            func = getattr(self, step_name)
            func()


class MyWorkflow(Workflow):
    @step
    def start_engine(self) -> None:
        logger.info("Engine is on!")

    def my_helper_function(self) -> None:
        raise RuntimeError("Should not be called")

    @step
    def release_brake(self) -> None:
        logger.info("Brake is off!")


def example_4() -> None:
    """
    示例 4：使用装饰器标记步骤并按定义顺序运行
    """
    logger.info("开始示例 4：使用装饰器标记步骤并按定义顺序运行")

    workflow = MyWorkflow()
    workflow.run()


# 示例 5：错误示例演示
class BadRowMapper(RowMapper):
    """
    错误示例：没有定义 fields 的子类
    """
    pass


def example_5() -> None:
    """
    示例 5：错误示例演示
    """
    logger.info("开始示例 5：错误示例演示")

    try:
        BadRowMapper.from_row(["Sydney"])
    except ValueError as e:
        logger.warning(f"未定义 fields 字段错误处理成功: {e}")

    class InvalidFieldMapper(BetterRowMapper):
        destination = ...
        invalid_field = "not ellipsis"  # 不是 Ellipsis

    try:
        obj = InvalidFieldMapper.from_row(["Sydney", "truck"])
    except AssertionError as e:
        logger.warning(f"字段类型错误处理成功: {e}")


# 主函数：运行所有示例
def main() -> None:
    """
    主函数：依次运行所有示例
    """
    example_1()
    example_2()
    example_3()
    example_4()
    example_5()


if __name__ == "__main__":
    main()
