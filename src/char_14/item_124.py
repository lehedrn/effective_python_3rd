"""
本文件演示了如何使用 Python 的 `typing` 模块进行类型注解，并通过静态分析工具（如 mypy）来提前发现潜在错误。
每个示例都包含错误和正确版本，以展示类型提示的优势。

本示例应该在命令行，使用 mypy --strict your_file.py 来试验
"""

import logging
from typing import List, Optional, TypeVar, Callable

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 1. 基本函数类型注解
def subtract_wrong(a, b):
    """
    错误示例：未使用类型注解，导致运行时错误。
    TypeError: unsupported operand type(s) for -: 'int' and 'str'
    """
    return a - b


def subtract_correct(a: int, b: int) -> int:
    """
    正确示例：使用类型注解后，mypy 可在编译阶段检测错误。
    """
    return a - b


# 2. 类型注解在类中的使用
class CounterWrong:
    def __init__(self):
        self.value = 0

    def add(self, offset):
        value += offset  # 错误：忘记使用 self.value

    def get(self) -> int:
        self.value  # 错误：缺少 return 语句


class CounterCorrect:
    def __init__(self):
        self.value: int = 0  # 正确：显式声明类型

    def add(self, offset: int) -> None:
        self.value += offset  # 正确：使用 self.value

    def get(self) -> int:
        return self.value  # 正确：返回值


# 3. 泛型与类型推断
T = TypeVar('T')


def combine_wrong(func, values):
    """
    错误示例：没有类型信息，无法被 mypy 检测出问题。
    最终 assert 失败：(6+4j)
    """
    result = values[0]
    for next_value in values[1:]:
        result = func(result, next_value)
    return result


def combine_correct(func: Callable[[T, T], T], values: List[T]) -> T:
    """
    正确示例：泛型 + 类型注解，mypy 可提前发现问题。
    """
    result = values[0]
    for next_value in values[1:]:
        result = func(result, next_value)
    return result


Real = TypeVar("Real", int, float)


def add_real(x: Real, y: Real) -> Real:
    return x + y


# 4. 可选类型 (None 安全)
def get_or_default_wrong(value, default):
    """
    错误示例：逻辑错误，返回 None 而不是 default。
    assert 失败：found == None
    """
    if value is not None:
        return value
    return value


def get_or_default_correct(value: Optional[int], default: int) -> int:
    """
    正确示例：返回 default，mypy 提前检测返回值类型是否匹配。
    """
    if value is not None:
        return value
    return default


# 5. 前向引用处理
class FirstClassWrong:
    def __init__(self, value: "SecondClass"):  # 运行时报错：NameError
        self.value = value


class SecondClass:
    def __init__(self, value: int):
        self.value = value


class FirstClassCorrect:
    def __init__(self, value: "SecondClass"):  # 使用字符串解决前向引用
        self.value = value


# 主函数：运行所有示例
def main():
    logging.info("=== 示例1：基本函数类型注解 ===")
    try:
        subtract_wrong(10, "5")  # 错误示例会抛出异常
    except Exception as e:
        logging.error(f"subtract_wrong 报错: {e}")

    try:
        result = subtract_correct(10, "5")  # mypy 会检测到错误
        logging.info(f"subtract_correct 返回: {result}")
    except Exception as e:
        logging.warning(f"subtract_correct 报错: {e}")

    logging.info("\n=== 示例2：类的类型注解 ===")
    try:
        counter_wrong = CounterWrong()
        counter_wrong.add(5)
    except Exception as e:
        logging.error(f"CounterWrong.add 报错: {e}")

    try:
        counter_correct = CounterCorrect()
        counter_correct.add(5)
        logging.info(f"CounterCorrect.get 返回: {counter_correct.get()}")
    except Exception as e:
        logging.warning(f"CounterCorrect 异常: {e}")

    logging.info("\n=== 示例3：泛型与类型推断 ===")
    inputs = [1, 2, 3, 4j]
    result = combine_wrong(add_real, inputs)  # mypy 不报错但运行失败
    logging.warning(f"combine_wrong 返回: {result}")

    try:
        result = combine_correct(add_real, inputs)  # mypy 报错
        logging.info(f"combine_correct 返回: {result}")
    except Exception as e:
        logging.warning(f"combine_correct 异常: {e}")

    logging.info("\n=== 示例4：可选类型 (None 安全) ===")
    found = get_or_default_wrong(None, 5)
    logging.warning(f"get_or_default_wrong 返回: {found}")  # assert 失败

    found = get_or_default_correct(None, 5)
    logging.info(f"get_or_default_correct 返回: {found}")

    logging.info("\n=== 示例5：前向引用处理 ===")
    try:
        second = SecondClass(5)
        first_wrong = FirstClassWrong(second)  # 运行时报错
    except Exception as e:
        logging.error(f"FirstClassWrong 初始化失败: {e}")

    first_correct = FirstClassCorrect(second)
    logging.info(f"FirstClassCorrect 初始化成功")


if __name__ == "__main__":
    main()

