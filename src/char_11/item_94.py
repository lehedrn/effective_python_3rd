"""
本模块演示了如何在 Python 中进行性能优化以及何时使用其他语言替代。
包括错误示例与正确示例，涵盖文档中提到的各个关键点。
"""

import logging
import timeit
import tracemalloc
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import numba
import ctypes
import os

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ================================
# 错误示例：Python 实现低效的 dot_product
# ================================
def bad_dot_product(a, b):
    """
    使用纯 Python 的 zip 和循环实现点积，效率低下。
    """
    result = 0
    for i, j in zip(a, b):
        result += i * j
    return result


# ================================
# 正确示例：使用 NumPy 进行高效计算
# ================================
def good_dot_product_with_numpy(a, b):
    """
    使用 NumPy 进行向量化运算，极大提升性能。
    """
    a_np = np.array(a)
    b_np = np.array(b)
    return np.dot(a_np, b_np)


# ================================
# 正确示例：使用 Numba JIT 编译加速
# ================================
@numba.jit(nopython=True)
def good_dot_product_with_numba(a, b):
    """
    使用 Numba JIT 编译加速，适用于原生 Python 函数。
    """
    result = 0
    for i in range(len(a)):
        result += a[i] * b[i]
    return result


# ================================
# 正确示例：使用 ctypes 调用 C 库
# ================================
def good_dot_product_with_ctypes(a, b):
    """
    调用本地 C 编写并编译好的 DLL/so 文件进行高性能计算。
    注意：需要提前准备好对应的 C 动态库文件。
    """
    # 假设我们有一个名为 libdot.so 的共享库（Windows 下为 .dll）
    lib_path = os.path.join(os.path.dirname(__file__), 'libdot.so')
    if not os.path.exists(lib_path):
        logging.warning("C 库未找到，请先构建 libdot.so/.dll")
        return None

    lib = ctypes.CDLL(lib_path)
    lib.dot_product.argtypes = [ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double), ctypes.c_int]
    lib.dot_product.restype = ctypes.c_double

    arr_type = ctypes.c_double * len(a)
    c_a = arr_type(*a)
    c_b = arr_type(*b)

    return lib.dot_product(c_a, c_b, len(a))


# ================================
# 错误示例：不合理的线程使用
# ================================
def cpu_bound_task(n):
    return sum(i ** 2 for i in range(n))

def bad_parallel_usage():
    """
    在 CPU 密集型任务中使用 threading 模块无法提高性能（受 GIL 影响）。
    """
    from threading import Thread
    results = []

    def task_wrapper(n):
        result = cpu_bound_task(n)
        results.append(result)

    threads = [Thread(target=task_wrapper, args=(1000000,)) for _ in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    return sum(results)


# ================================
# 正确示例：使用 multiprocessing 并行化
# ================================
def good_parallel_usage():
    """
    使用 multiprocessing 实现真正的多核并行，绕过 GIL 限制。
    """

    with ProcessPoolExecutor() as executor:
        results = list(executor.map(cpu_bound_task, [1000000] * 4))
    return sum(results)


# ================================
# 示例：使用 tracemalloc 分析内存泄漏
# ================================
def check_memory_usage():
    """
    使用 tracemalloc 分析程序内存消耗情况。
    """
    tracemalloc.start()

    snapshot1 = tracemalloc.take_snapshot()
    # 模拟内存分配
    temp_list = [i ** 2 for i in range(1000000)]
    snapshot2 = tracemalloc.take_snapshot()

    top_stats = snapshot2.compare_to(snapshot1, 'lineno')
    logging.info("[内存分析] 最显著的内存分配:")
    for stat in top_stats[:5]:
        logging.info(stat)


# ================================
# 示例：使用 timeit 微基准测试
# ================================
def benchmark_dot_products():
    """
    使用 timeit 对不同实现进行微基准测试。
    """
    size = 1000
    a = list(range(size))
    b = list(range(size))

    def run_test(func):
        return timeit.timeit(lambda: func(a, b), number=1000)

    bad_time = run_test(bad_dot_product)
    good_numpy_time = run_test(good_dot_product_with_numpy)
    good_numba_time = run_test(good_dot_product_with_numba)

    logging.info(f"[性能对比] 纯 Python: {bad_time:.4f}s")
    logging.info(f"[性能对比] NumPy: {good_numpy_time:.4f}s")
    logging.info(f"[性能对比] Numba: {good_numba_time:.4f}s")


# ================================
# 主函数运行所有示例
# ================================
def main():
    """
    主函数，用于执行所有示例。
    """
    logging.info("开始执行所有性能相关示例...")

    # 测试点积性能
    benchmark_dot_products()

    # 内存分析
    check_memory_usage()

    # 多进程并行
    start_time = timeit.default_timer()
    total_good = good_parallel_usage()
    end_time = timeit.default_timer()
    logging.info(f"[good_parallel_usage] 总和: {total_good}, 耗时: {end_time - start_time:.6f}s")

    # 错误线程使用（仅演示）
    logging.warning("以下是一个错误线程使用的示例（不推荐）")
    start_time = timeit.default_timer()
    total_bad = bad_parallel_usage()
    end_time = timeit.default_timer()
    logging.info(f"[bad_parallel_usage] 总和: {total_bad}, 耗时: {end_time - start_time:.6f}s")


if __name__ == '__main__':
    main()
