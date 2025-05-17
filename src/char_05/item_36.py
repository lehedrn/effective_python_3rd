"""
本文件展示了在 Python 函数中使用动态默认参数时的常见错误及正确做法。

包含以下示例：
1. 错误示例：使用 `datetime.now()` 作为默认参数，导致时间戳不更新。
2. 正确示例：使用 `None` 作为默认参数，并在函数体内动态生成当前时间。
3. 错误示例：使用可变对象（如字典）作为默认参数，导致所有调用共享同一个对象。
4. 正确示例：使用 `None` 作为默认参数，并在函数体内动态创建新字典。
5. 可选类型注解示例：结合 `Optional[datetime]` 使用 `None` 动态参数。

每个示例都配有 main 函数运行演示，并附有详细说明。
"""

import logging
from datetime import datetime
from time import sleep
import json

# 配置 logging 模块
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')


# 示例 1: 错误使用 datetime.now() 作为默认参数
def log_bad(message, when=datetime.now()):
    """
    错误示例：when 的默认值只在定义时评估一次，不会随调用更新。

    Args:
        message (str): 要记录的消息。
        when (datetime): 时间戳，默认为函数定义时的时间。
    """
    logging.info(f"{when}: {message}")


# 示例 2: 正确使用 None 作为默认参数，并在函数内部赋值
def log_good(message, when=None):
    """
    正确示例：when 默认为 None，在函数内部动态获取当前时间。

    Args:
        message (str): 要记录的消息。
        when (datetime | None): 时间戳，默认为 None，表示当前时间。
    """
    if when is None:
        when = datetime.now()
    logging.info(f"{when}: {message}")


# 示例 3: 错误使用可变对象（dict）作为默认参数
def decode_bad(data, default={}):
    """
    错误示例：default 参数被多个调用共享，修改会影响所有后续调用。

    Args:
        data (str): JSON 格式的字符串。
        default (dict): 解码失败时返回的默认字典，默认为空字典。
    """
    try:
        return json.loads(data)
    except ValueError:
        return default


# 示例 4: 正确使用 None 并在函数内部创建新字典
def decode_good(data, default=None):
    """
    正确示例：default 默认为 None，在函数内部创建新字典以避免共享。

    Args:
        data (str): JSON 格式的字符串。
        default (dict | None): 解码失败时返回的默认字典，默认为空字典。
    """
    try:
        return json.loads(data)
    except ValueError:
        if default is None:
            default = {}
        return default


# 示例 5: 使用类型注解 Optional[datetime] 的正确方式
def log_typed(message: str, when: datetime | None = None) -> None:
    """
    类型注解示例：when 是 Optional[datetime]，推荐使用 None 作为默认值。

    Args:
        message (str): 要记录的消息。
        when (datetime | None): 时间戳，默认为 None，表示当前时间。
    """
    if when is None:
        when = datetime.now()
    logging.info(f"{when}: {message}")


# 主函数运行示例
def main():
    # 示例 1 和 2: 测试 log_bad vs log_good
    logging.info("=== 测试 log_bad vs log_good ===")
    log_bad("Bad Log Message")
    sleep(0.1)
    log_bad("Same Timestamp")  # 应该和前一个时间相同

    log_good("Good Log Message")
    sleep(0.1)
    log_good("Different Timestamp")  # 应该不同

    # 示例 3 和 4: 测试 decode_bad vs decode_good
    logging.info("=== 测试 decode_bad vs decode_good ===")
    foo = decode_bad('invalid')
    foo['bad'] = 1
    bar = decode_bad('also invalid')
    bar['bad_again'] = 2
    logging.info(f"decode_bad 共享对象: foo={foo}, bar={bar}")  # 会共享同一个 dict

    good_foo = decode_good('invalid')
    good_foo['good'] = 1
    good_bar = decode_good('also invalid')
    good_bar['good_again'] = 2
    logging.info(f"decode_good 独立对象: foo={good_foo}, bar={good_bar}")  # 不共享

    # 示例 5: 使用类型注解的 log_typed
    logging.info("=== 使用类型注解的 log_typed ===")
    log_typed("Typed Log Message")
    sleep(0.1)
    log_typed("Another Typed Message")


if __name__ == "__main__":
    main()
