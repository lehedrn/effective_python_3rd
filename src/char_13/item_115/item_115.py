"""
memory_debugging_examples.py

此文件展示了如何使用 Python 的 `gc` 和 `tracemalloc` 模块来调试内存使用和检测内存泄漏。
包含以下内容：
1. 使用 `gc` 模块检查对象数量的错误示例（无法提供分配来源）。
2. 使用 `tracemalloc` 模块分析内存使用和分配来源的正确示例。
3. 对比 `tracemalloc.start(10)` 和 `tracemalloc.start(1)` 的堆栈深度影响。
4. 展示内存泄漏的错误示例和修复后的正确示例。
5. 所有示例使用 logging 记录输出，符合 PEP8 规范。
6. 提供清晰的注释和示例，便于理解内存调试的实际应用。

运行此文件将依次执行所有示例，展示不同调试方法的输出结果。
"""

import os
import gc
import tracemalloc
import logging
from typing import List

# 配置 logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# --------------------------------------
# 错误示例：使用 gc 模块检查内存使用
# --------------------------------------
def example_gc_wrong() -> None:
    """
    错误示例：使用 gc 模块检查内存使用。
    说明：此示例展示使用 gc.get_objects() 来检查内存中对象的数量，
         但无法提供对象分配的来源，调试能力有限。
    """
    logger.info("开始错误示例：使用 gc 模块")
    # 获取初始对象数量
    initial_objects = len(gc.get_objects())
    logger.info(f"运行前对象数量: {initial_objects}")

    # 创建大量对象，模拟内存使用
    class DataObject:
        def __init__(self):
            self.data = os.urandom(100)  # 分配 100 字节的随机数据

    def create_objects() -> List[DataObject]:
        objects = []
        for _ in range(1000):
            objects.append(DataObject())
        return objects

    # 持有引用，模拟内存占用
    hold_references = create_objects()

    # 获取运行后的对象数量
    final_objects = len(gc.get_objects())
    logger.info(f"运行后对象数量: {final_objects}")
    logger.info(f"对象数量增加: {final_objects - initial_objects}")
    logger.info("前三个对象示例: %s", [repr(obj)[:50] for obj in gc.get_objects()[:3]])
    logger.info("缺点：无法知道这些对象从何处分配，调试困难")

# --------------------------------------
# 正确示例：使用 tracemalloc 分析内存使用
# --------------------------------------
def example_tracemalloc_correct() -> None:
    """
    正确示例：使用 tracemalloc 模块分析内存使用和分配来源。
    说明：通过 tracemalloc 捕获内存快照并比较，识别内存使用的来源和分配位置。
    """
    logger.info("开始正确示例：使用 tracemalloc 模块")
    # 启动 tracemalloc，设置堆栈深度为 10
    tracemalloc.start(10)

    # 捕获初始快照
    snapshot1 = tracemalloc.take_snapshot()

    # 创建大量对象，模拟内存使用
    class DataObject:
        def __init__(self):
            self.data = os.urandom(100)  # 分配 100 字节的随机数据

    def create_objects() -> List[DataObject]:
        objects = []
        for _ in range(1000):
            objects.append(DataObject())
        return objects

    # 持有引用，模拟内存占用
    hold_references = create_objects()

    # 捕获运行后快照
    snapshot2 = tracemalloc.take_snapshot()

    # 比较快照，获取内存使用统计
    stats = snapshot2.compare_to(snapshot1, "lineno")
    logger.info("内存使用最多的前三个位置:")
    for stat in stats[:3]:
        logger.info(f"{stat}")

    # 获取最大内存使用者的堆栈跟踪
    top_stat = stats[0]
    logger.info("最大内存使用者的堆栈跟踪:")
    for line in top_stat.traceback.format():
        logger.info(line)

    # 清理 tracemalloc
    tracemalloc.stop()

# --------------------------------------
# 新增示例：对比 tracemalloc.start(10) 和 tracemalloc.start(1)
# --------------------------------------
def example_tracemalloc_stack_depth_comparison() -> None:
    """
    新增示例：对比 tracemalloc.start(10) 和 tracemalloc.start(1) 的影响。
    说明：展示堆栈深度对内存分析的差异，深度 10 提供详细的调用栈，深度 1 仅提供直接调用位置。
    """
    logger.info("开始示例：对比 tracemalloc 堆栈深度")

    # 定义通用的对象创建逻辑
    class DataObject:
        def __init__(self):
            self.data = os.urandom(100)  # 分配 100 字节的随机数据

    def create_objects() -> List[DataObject]:
        objects = []
        for _ in range(500):
            objects.append(DataObject())
        return objects

    # 测试堆栈深度为 10
    logger.info("测试 tracemalloc.start(10)")
    tracemalloc.start(10)
    snapshot1 = tracemalloc.take_snapshot()

    hold_references = create_objects()

    snapshot2 = tracemalloc.take_snapshot()
    stats = snapshot2.compare_to(snapshot1, "traceback")
    logger.info("堆栈深度 10 的最大内存使用者堆栈跟踪:")
    for line in stats[0].traceback.format():
        logger.info(line)

    tracemalloc.stop()

    # 测试堆栈深度为 1
    logger.info("测试 tracemalloc.start(1)")
    tracemalloc.start(1)
    snapshot1 = tracemalloc.take_snapshot()

    hold_references = create_objects()  # 重复运行以保持一致

    snapshot2 = tracemalloc.take_snapshot()
    stats = snapshot2.compare_to(snapshot1, "traceback")
    logger.info("堆栈深度 1 的最大内存使用者堆栈跟踪:")
    for line in stats[0].traceback.format():
        logger.info(line)

    tracemalloc.stop()
    logger.info("对比说明：堆栈深度 10 提供更详细的调用栈，适合复杂程序调试；深度 1 仅显示直接分配位置，适合简单分析")

# --------------------------------------
# 错误示例：内存泄漏
# --------------------------------------
def example_memory_leak_wrong() -> None:
    """
    错误示例：展示内存泄漏问题。
    说明：通过全局列表持有不再需要的对象引用，导致内存泄漏。
    """
    logger.info("开始错误示例：内存泄漏")
    global_leak_list = []  # 全局列表，模拟泄漏

    class LeakObject:
        def __init__(self, id: int):
            self.id = id
            self.data = os.urandom(1000)  # 分配 1000 字节

    def create_leak() -> None:
        for i in range(500):
            obj = LeakObject(i)
            global_leak_list.append(obj)  # 全局列表持有引用

    # 启动 tracemalloc
    tracemalloc.start(10)
    snapshot1 = tracemalloc.take_snapshot()

    # 运行泄漏代码
    create_leak()

    # 捕获快照并比较
    snapshot2 = tracemalloc.take_snapshot()
    stats = snapshot2.compare_to(snapshot1, "lineno")
    logger.info("内存泄漏分析:")
    for stat in stats[:3]:
        logger.info(f"{stat}")

    logger.info("缺点：global_leak_list 持有引用，导致对象无法被垃圾回收")
    tracemalloc.stop()

# --------------------------------------
# 正确示例：修复内存泄漏
# --------------------------------------
def example_memory_leak_fixed() -> None:
    """
    正确示例：修复内存泄漏问题。
    说明：通过避免全局引用和手动清理，确保对象可以被垃圾回收。
    """
    logger.info("开始正确示例：修复内存泄漏")

    class LeakObject:
        def __init__(self, id: int):
            self.id = id
            self.data = os.urandom(1000)  # 分配 1000 字节

    def create_objects_no_leak() -> List[LeakObject]:
        local_list = []
        for i in range(500):
            obj = LeakObject(i)
            local_list.append(obj)
        return local_list

    # 启动 tracemalloc
    tracemalloc.start(10)
    snapshot1 = tracemalloc.take_snapshot()

    # 运行代码，局部列表不会导致泄漏
    objects = create_objects_no_leak()

    # 手动清理引用
    objects.clear()

    # 捕获快照并比较
    snapshot2 = tracemalloc.take_snapshot()
    stats = snapshot2.compare_to(snapshot1, "lineno")
    logger.info("修复后内存使用分析:")
    for stat in stats[:3]:
        logger.info(f"{stat}")

    logger.info("优点：局部列表和手动清理确保对象可以被垃圾回收")
    tracemalloc.stop()

# --------------------------------------
# 主函数：运行所有示例
# --------------------------------------
def main() -> None:
    """
    主函数：依次运行所有内存调试示例。
    """
    logger.info("开始运行内存调试示例")
    logger.info("=" * 50)

    example_gc_wrong()
    logger.info("=" * 50)

    example_tracemalloc_correct()
    logger.info("=" * 50)

    example_tracemalloc_stack_depth_comparison()
    logger.info("=" * 50)

    example_memory_leak_wrong()
    logger.info("=" * 50)

    example_memory_leak_fixed()
    logger.info("=" * 50)
    logger.info("所有示例运行完成")

if __name__ == "__main__":
    main()