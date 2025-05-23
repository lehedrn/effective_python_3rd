"""
本模块演示了如何使用 Python 的 concurrent.futures 模块进行并行计算。
包括串行执行、线程池执行（受 GIL 限制）以及进程池执行（真正的并行）的示例。

主要包含以下内容：
1. 串行执行：没有并发，任务按顺序执行。
2. 线程池执行：使用 ThreadPoolExecutor，但受限于 GIL，无法实现 CPU 并行。
3. 进程池执行：使用 ProcessPoolExecutor，可以真正利用多核 CPU 并行处理任务。
4. 错误示例：错误地尝试在多进程中使用全局状态或共享数据。
"""

import logging
import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def gcd(pair):
    """
    计算两个数的最大公约数 (GCD)。
    这是一个计算密集型函数，适合用于演示并行化效果。

    参数:
        pair (tuple): 包含两个整数的元组

    返回:
        int: 最大公约数
    """
    a, b = pair
    low = min(a, b)
    for i in range(low, 0, -1):
        if a % i == 0 and b % i == 0:
            return i
    raise RuntimeError("Not reachable")


# -----------------------------
# 示例 1: 串行执行
# -----------------------------

def serial_gcd(numbers):
    """
    串行计算最大公约数。
    适用于理解没有并行化的基准性能。

    参数:
        numbers (list): 包含多个元组的列表，每个元组有两个整数

    返回:
        list: 每个元组对应的最大公约数
    """
    return list(map(gcd, numbers))


def run_serial(numbers):
    """
    执行串行版本的 GCD 计算，并记录耗时。

    参数:
        numbers (list): 包含多个元组的列表，每个元组有两个整数
    """
    logger.info("开始串行执行...")
    start_time = time.perf_counter()
    results = serial_gcd(numbers)
    end_time = time.perf_counter()
    delta = end_time - start_time
    logger.info(f"串行执行完成，结果数量: {len(results)}，耗时: {delta:.3f} 秒")
    return results


# -----------------------------
# 示例 2: 使用 ThreadPoolExecutor（受 GIL 限制）
# -----------------------------

def threaded_gcd(numbers):
    """
    使用线程池执行最大公约数计算。
    虽然看起来是并行，但由于 GIL 的存在，CPU 密集型任务不会加快。

    参数:
        numbers (list): 包含多个元组的列表，每个元组有两个整数

    返回:
        list: 每个元组对应的最大公约数
    """
    with ThreadPoolExecutor(max_workers=8) as executor:
        return list(executor.map(gcd, numbers))


def run_threaded(numbers):
    """
    执行线程池版本的 GCD 计算，并记录耗时。

    参数:
        numbers (list): 包含多个元组的列表，每个元组有两个整数
    """
    logger.info("开始线程池执行...")
    start_time = time.perf_counter()
    results = threaded_gcd(numbers)
    end_time = time.perf_counter()
    delta = end_time - start_time
    logger.info(f"线程池执行完成，结果数量: {len(results)}，耗时: {delta:.3f} 秒")
    return results


# -----------------------------
# 示例 3: 使用 ProcessPoolExecutor（真正的并行）
# -----------------------------

def parallel_gcd(numbers):
    """
    使用进程池执行最大公约数计算。
    可以真正利用多核 CPU 加速 CPU 密集型任务。

    参数:
        numbers (list): 包含多个元组的列表，每个元组有两个整数

    返回:
        list: 每个元组对应的最大公约数
    """
    with ProcessPoolExecutor(max_workers=8) as executor:
        return list(executor.map(gcd, numbers))


def run_parallel(numbers):
    """
    执行进程池版本的 GCD 计算，并记录耗时。

    参数:
        numbers (list): 包含多个元组的列表，每个元组有两个整数
    """
    logger.info("开始进程池执行...")
    start_time = time.perf_counter()
    results = parallel_gcd(numbers)
    end_time = time.perf_counter()
    delta = end_time - start_time
    logger.info(f"进程池执行完成，结果数量: {len(results)}，耗时: {delta:.3f} 秒")
    return results


# -----------------------------
# 错误示例：尝试在多进程中共享可变状态
# -----------------------------

SHARED_COUNTER = 0

def bad_parallel_task(x):
    """
    错误示例：尝试在多个进程中修改共享变量。
    实际上每个进程有自己的内存空间，不能直接共享状态。
    """
    global SHARED_COUNTER
    SHARED_COUNTER += x
    return SHARED_COUNTER


def bad_parallel_execution():
    """
    错误地尝试在多个进程中共享状态，演示为什么这种方式不可行。
    """
    logger.warning("开始错误示例：尝试在多进程中共享状态...")
    numbers = [1, 2, 3, 4, 5]
    try:
        with ProcessPoolExecutor() as executor:
            results = list(executor.map(bad_parallel_task, numbers))
        logger.warning(f"错误示例结果: {results}")
        logger.warning("注意：每个进程都有自己的 SHARED_COUNTER 副本，全局状态未被共享！")
    except Exception as e:
        logger.error(f"错误示例抛出异常: {e}")


# -----------------------------
# 主函数入口
# -----------------------------

def main():
    """
    主函数，运行所有示例。
    """
    # 测试数据集
    NUMBERS = [
        (19633090, 22659730),
        (20306770, 38141720),
        (15516450, 22296200),
        (20390450, 20208020),
        (18237120, 19249280),
        (22931290, 10204910),
        (12812380, 22737820),
        (38238120, 42372810),
        (38127410, 47291390),
        (12923910, 21238110),
    ]

    # 1. 串行执行
    run_serial(NUMBERS)

    # 2. 线程池执行（受 GIL 影响）
    run_threaded(NUMBERS)

    # 3. 进程池执行（真正的并行）
    run_parallel(NUMBERS)

    # 4. 错误示例：尝试共享状态
    bad_parallel_execution()


if __name__ == "__main__":
    main()
