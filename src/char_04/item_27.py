"""
本模块演示了在处理字典中缺失项时，使用 defaultdict 和 setdefault 的不同方式。
重点说明为何在管理内部状态时应优先使用 defaultdict。

包含以下示例：
1. 使用 `setdefault` 来处理外部字典的缺失键问题。
2. 使用 `defaultdict` 来简化内部状态字典的实现。
3. 展示错误地使用 `setdefault` 导致性能问题的情况。
4. 展示正确使用 `defaultdict` 来避免性能问题的情况。
"""

import logging
import time
from collections import defaultdict

# 设置日志输出格式
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# 示例 1：使用 setdefault 处理外部字典的缺失键
def example_setdefault_external():
    """
    演示如何使用 setdefault 方法来向外部字典中添加城市信息。
    """
    visits = {
        "Mexico": {"Tulum", "Puerto Vallarta"},
        "Japan": {"Hakone"},
    }

    # 使用 setdefault 添加新国家和城市
    visits.setdefault("France", set()).add("Arles")
    # 如果国家已存在，则添加新的城市到已有集合中
    visits.setdefault("Japan", set()).add("Kyoto")

    logging.info("Example setdefault (external dict): %s", visits)


# 示例 2：使用 defaultdict 管理内部状态
class VisitsWithDefaultDict:
    """
    使用 defaultdict 来管理内部状态，自动为不存在的键提供默认值。
    """

    def __init__(self):
        self.data = defaultdict(set)

    def add(self, country, city):
        """
        添加城市访问记录。
        :param country: 国家名
        :param city: 城市名
        """
        self.data[country].add(city)


def example_defaultdict_internal():
    """
    演示使用 defaultdict 实现的类，其 add 方法更简洁高效。
    """
    visits = VisitsWithDefaultDict()
    visits.add("England", "Bath")
    visits.add("England", "London")
    visits.add("Russia", "Yekaterinburg")
    visits.add("Tanzania", "Zanzibar")

    logging.info("Example defaultdict (internal state): %s", dict(visits.data))


# 错误示例：低效使用 setdefault（每次都创建新对象）
class VisitsWithSetdefaultInefficient:
    """
    错误示例：每次调用 add 都会创建一个新的 set 对象，即使该键已经存在。
    这会导致不必要的内存分配。
    """

    def __init__(self):
        self.data = {}

    def add(self, country, city):
        city_set = self.data.setdefault(country, set())  # 每次都新建 set
        city_set.add(city)


# 正确示例：改进后的 setdefault 使用方式（不推荐但展示对比）
class VisitsWithSetdefaultEfficient:
    """
    改进的 setdefault 使用方式，仅在需要时才创建 set。
    但代码冗长且不如 defaultdict 清晰。
    """

    def __init__(self):
        self.data = {}

    def add(self, country, city):
        if country not in self.data:
            self.data[country] = set()
        self.data[country].add(city)


def compare_setdefault_vs_defaultdict():
    """
    对比低效 setdefault 和高效 defaultdict 的性能差异。
    """

    # 测试 VisitsWithSetdefaultInefficient
    inefficient = VisitsWithSetdefaultInefficient()
    start_time = time.time()
    for _ in range(100000000):
        inefficient.add("TestCountry", "TestCity")
    logging.info("Inefficient setdefault used with unnecessary set allocations. times:  %s seconds", time.time() - start_time)

    # 测试 VisitsWithSetdefaultEfficient
    efficient_setdefault = VisitsWithSetdefaultEfficient()
    start_time = time.time()
    for _ in range(100000000):
        efficient_setdefault.add("TestCountry", "TestCity")
    logging.info("Efficient setdefault without unnecessary allocations. times:  %s seconds", time.time() - start_time)

    # 测试 VisitsWithDefaultDict
    default_dict = VisitsWithDefaultDict()
    start_time = time.time()
    for _ in range(100000000):
        default_dict.add("TestCountry", "TestCity")
    logging.info("Defaultdict handled missing keys efficiently. times:  %s seconds", time.time() - start_time)


# 主函数运行所有示例
def main():
    logging.info("开始运行示例...")

    logging.info("\n--- 示例 1: 使用 setdefault 处理外部字典 ---")
    example_setdefault_external()

    logging.info("\n--- 示例 2: 使用 defaultdict 管理内部状态 ---")
    example_defaultdict_internal()

    logging.info("\n--- 性能对比: setdefault vs defaultdict ---")
    compare_setdefault_vs_defaultdict()

    logging.info("\n所有示例运行完成。")


if __name__ == "__main__":
    main()
