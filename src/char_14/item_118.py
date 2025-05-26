"""
这是一个示例模块，用于演示如何为每个函数、类和模块编写文档字符串。

该模块包含以下内容：
- 模块级文档字符串的使用
- 类级文档字符串的使用
- 函数级文档字符串的使用
- 错误示例与正确示例对比
- 使用类型注解时的文档字符串优化
"""

import logging
from typing import List, Optional

# 设置日志配置
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 示例1: 模块级文档字符串
# 本文件顶部已经展示了模块级文档字符串的使用


class ExampleClass:
    """
    示例类，用于演示类级文档字符串的使用。

    该类提供了一些方法来展示不同情况下的文档字符串写法。

    子类可以覆盖 `example_method` 来实现自定义行为。

    公共属性:
    - count: 记录调用次数 (整数)
    """

    def __init__(self):
        """初始化示例类，设置计数器为0"""
        self.count = 0  # type: int

    def example_method(self, input_str: str) -> str:
        """
        示例方法，返回输入字符串的大写形式

        Args:
            input_str: 需要转换为大写的字符串

        Returns:
            转换后的字符串

        Raises:
            ValueError: 如果输入不是字符串
        """
        if not isinstance(input_str, str):
            raise ValueError("Input must be a string")

        self.count += 1
        return input_str.upper()


def bad_docstring_example():
    """错误的文档字符串示例"""
    pass


def good_docstring_example(param1: int, param2: Optional[str] = None) -> List[int]:
    """
    正确的文档字符串示例

    该函数接受一个必填参数和一个可选参数，返回一个整数列表。

    Args:
        param1: 必填参数，表示基础值
        param2: 可选参数，默认为None。如果提供，将影响生成列表的方式

    Returns:
        根据输入参数生成的整数列表

    Raises:
        TypeError: 如果param1不是整数
    """
    if not isinstance(param1, int):
        raise TypeError("param1 must be an integer")

    result = [i * param1 for i in range(5)]

    if param2 == "reverse":
        result.reverse()

    return result


def generator_function(n: int) -> int:
    """
    生成器函数示例

    产生从0到n-1的数字

    Args:
        n: 生成数字的上限（不包含）

    Yields:
        从0到n-1的数字
    """
    for i in range(n):
        yield i


def main():
    """主函数，运行所有示例"""
    logging.info("开始运行示例")

    # 示例1: 类级文档字符串
    logging.info("示例1: 类级文档字符串")
    example = ExampleClass()
    logging.info(f"调用example_method('hello'): {example.example_method('hello')}")
    logging.info(f"调用次数: {example.count}")

    # 示例2: 错误的文档字符串 vs 正确的文档字符串
    logging.info("\n示例2: 错误的文档字符串 vs 正确的文档字符串")
    try:
        bad_docstring_example()
    except Exception as e:
        logging.warning(f"bad_docstring_example异常: {e}")

    logging.info(f"good_docstring_example结果: {good_docstring_example(3, 'reverse')}")

    # 示例3: 使用类型注解的函数
    logging.info("\n示例3: 使用类型注解的函数")
    logging.info(f"good_docstring_example结果: {good_docstring_example(2)}")

    # 示例4: 生成器函数
    logging.info("\n示例4: 生成器函数")
    logging.info("生成0-4的数字:")
    for num in generator_function(5):
        logging.info(num, exc_info=True)

    logging.info("所有示例运行完成")


if __name__ == "__main__":
    main()
