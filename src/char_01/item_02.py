"""
PEP 8 完整示例文件（修订版）

本模块展示了如何完全符合 PEP 8 规范地编写 Python 代码。
涵盖：空白字符、命名、表达式、导入等所有主要规则。
"""

# ----------------------------
# 导入（Imports）
# ----------------------------

import os
import sys
from typing import Dict, List, Optional, Union

import requests


# ----------------------------
# 常量（ALL_CAPS）
# ----------------------------

MAX_RETRY_COUNT = 3
DEFAULT_TIMEOUT = 5  # seconds
SUPPORTED_FORMATS: List[str] = ["json", "xml", "yaml"]


# ----------------------------
# 类（CapitalizedWord）
# ----------------------------

class DataProcessor:
    """
    数据处理器类，用于处理各种数据格式。
    """

    def __init__(self, name: str):
        """初始化对象."""
        self.name = name                  # 公共属性
        self._internal_counter = 0        # 受保护属性
        self.__private_data = []          # 私有属性

    def process(self, data: List[Dict]) -> None:
        """
        处理传入的数据列表。

        :param data: 包含字典的数据列表
        """
        if not data:
            print("No data to process.")
            return

        for item in data:
            self.__process_item(item)

    def __process_item(self, item: Dict) -> None:
        """
        私有方法，处理单个数据项。

        :param item: 单个数据项
        """
        self._internal_counter += 1
        print(f"Processing item {self._internal_counter}: {item}")


# ----------------------------
# 函数（lowercase_underscore）
# ----------------------------

def format_output(
    data: Union[List, Dict],
    verbose: bool = False
) -> str:
    """
    格式化输出内容。

    :param data: 要格式化的数据
    :param verbose: 是否启用详细模式
    :return: 格式化后的字符串
    """
    if isinstance(data, dict):
        result = "\n".join([f"{k}: {v}" for k, v in data.items()])
    elif isinstance(data, list):
        result = ", ".join(str(x) for x in data)
    else:
        result = str(data)

    if verbose:
        print(f"Formatted output:\n{result}")

    return result


# ----------------------------
# 表达式与语句（Expressions and Statements）
# ----------------------------

def check_status(status_code: int) -> None:
    """
    检查 HTTP 状态码是否成功。

    :param status_code: HTTP 状态码
    """
    if status_code is not None:
        print("Status code received.")

    items = []
    if not items:
        print("Items list is empty.")

    non_empty_items = [1, 2, 3]
    if non_empty_items:
        print("There are items available.")

    try:
        response = requests.get(
            "https://example.com",
            timeout=3
        )
    except requests.RequestException as e:
        print(f"Request failed: {e}")
    else:
        print(f"Response status code: {response.status_code}")

    some_condition = True
    y = 5
    long_expression = (
        (x * y for x in range(10) if x % 2 == 0)
        if some_condition
        else (x + y for x in range(10) if x % 2 != 0)
    )


# ----------------------------
# 字典格式（Whitespace in Dictionary）
# ----------------------------

config = {
    "host":     "localhost",
    "port":     8080,
    "debug":    True,
}


# ----------------------------
# 类型注解（Type Annotations）
# ----------------------------

def get_user_info(user_id: int) -> Optional[Dict[str, Union[str, int]]]:
    """
    获取用户信息。

    :param user_id: 用户 ID
    :return: 用户信息字典或 None
    """
    return {
        "id":   user_id,
        "name": "Alice",
        "age":  30,
    }


# ----------------------------
# 主程序入口（Main entry point）
# ----------------------------

def main() -> None:
    """
    主程序入口。
    """
    processor = DataProcessor("Sample Processor")

    sample_data = [
        {"id": 1, "value": "A"},
        {"id": 2, "value": "B"},
    ]

    processor.process(sample_data)

    output = format_output(sample_data, verbose=True)
    print(output)


# ----------------------------
# 程序执行入口
# ----------------------------

if __name__ == "__main__":
    main()
