"""
本文件演示了如何在 Python 中使用线程和 `Lock` 来防止数据竞争问题。
包含了未使用锁导致计数错误的示例，以及使用 `threading.Lock` 修复该问题的正确示例。

条目说明：
- 即使 Python 有全局解释器锁 (GIL)，仍然需要使用互斥锁（如 threading.Lock）来保护共享数据。
- 如果允许多个线程在没有同步机制的情况下修改同一对象，程序可能会破坏其数据结构。
- 使用 `threading.Lock` 可以确保多个线程之间对共享资源的访问是安全的。

包含两个主要函数：
1. `incorrect_counter_example()`：展示不使用锁时的错误行为。
2. `correct_counter_example()`：展示使用锁后正确的行为。
"""

import logging
import threading

# 设置日志配置
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 全局计数器变量
counter = 0
# 线程屏障，用于模拟并发场景
BARRIER = None
# 每个线程执行次数
HOW_MANY = 100000
# 线程数量
SENSOR_COUNT = 4


def unsafe_worker(sensor_index, how_many):
    """
    不安全的计数器增加函数，没有使用锁保护。
    多个线程同时操作 `counter += get_offset(data)` 会导致数据竞争。
    """
    global counter
    BARRIER.wait()
    for _ in range(how_many):
        data = read_sensor(sensor_index)
        delta = get_offset(data)
        # 下面这行代码不是原子操作，存在数据竞争风险
        counter += delta


def safe_worker(sensor_index, how_many):
    """
    安全的计数器增加函数，使用 threading.Lock 保护共享资源。
    """
    global counter
    BARRIER.wait()
    for _ in range(how_many):
        data = read_sensor(sensor_index)
        delta = get_offset(data)
        with lock:  # 获取锁并确保释放
            counter += delta


def read_sensor(sensor_index):
    """
    模拟传感器读取操作（阻塞 I/O），返回固定值。
    实际应用中可能涉及真实 I/O 操作。
    """
    return sensor_index  # 模拟返回的数据


def get_offset(data):
    """
    返回偏移量，始终为 1 或更大。
    """
    return 1  # 简化处理，总是返回 1


def incorrect_counter_example():
    """
    展示不使用锁时，多线程环境下的数据竞争问题。
    """
    logger.info("开始不安全的计数器示例...")
    global counter, BARRIER
    counter = 0
    BARRIER = threading.Barrier(SENSOR_COUNT)

    threads = []
    for i in range(SENSOR_COUNT):
        thread = threading.Thread(target=unsafe_worker, args=(i, HOW_MANY))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    expected = HOW_MANY * SENSOR_COUNT
    logger.info(f"预期结果: {expected}, 实际结果: {counter}")


def correct_counter_example():
    """
    展示使用 threading.Lock 后的正确计数行为。
    """
    logger.info("开始安全的计数器示例...")
    global counter, BARRIER
    counter = 0
    BARRIER = threading.Barrier(SENSOR_COUNT)

    threads = []
    for i in range(SENSOR_COUNT):
        thread = threading.Thread(target=safe_worker, args=(i, HOW_MANY))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    expected = HOW_MANY * SENSOR_COUNT
    logger.info(f"预期结果: {expected}, 实际结果: {counter}")


if __name__ == '__main__':
    # 初始化锁
    lock = threading.Lock()

    # 执行不安全的示例
    incorrect_counter_example()

    # 执行安全的示例
    correct_counter_example()
