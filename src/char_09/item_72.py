"""
本模块演示了在 Python 中使用线程（Thread）进行并发处理时的问题，包括：
- 线程协调需要 `Lock` 的使用
- 每个线程占用大量内存（约 8MB）
- 启动和销毁线程的性能开销高
- 异常无法直接传递回主线程

包含错误示例与正确示例，并通过 logging 输出日志。
"""

import threading
import time
import logging
from contextlib import contextmanager
from io import StringIO
import contextlib

# 配置日志输出
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# 示例1：线程协调需要 Lock
def example_lock_usage():
    """
    使用 Lock 来保护共享资源的访问，防止数据竞争。
    """

    class SharedCounter:
        def __init__(self):
            self._value = 0
            self._lock = threading.Lock()

        def increment(self):
            with self._lock:
                self._value += 1

        def get_value(self):
            with self._lock:
                return self._value

    def worker(counter, iterations):
        for _ in range(iterations):
            counter.increment()

    logger.info("示例1: 线程协调需要 Lock")
    counter = SharedCounter()
    threads = []
    num_threads = 5
    iterations_per_thread = 1000

    for _ in range(num_threads):
        t = threading.Thread(target=worker, args=(counter, iterations_per_thread))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    expected = num_threads * iterations_per_thread
    actual = counter.get_value()
    logger.info(f"预期计数器值: {expected}, 实际计数器值: {actual}")
    assert expected == actual, "多线程下计数器不一致"


# 示例2：线程占用大量内存（约 8MB/线程）
def example_thread_memory_usage():
    """
    创建大量线程会占用巨大内存，不适合大规模并发任务。
    """

    def dummy_task():
        time.sleep(0.01)

    logger.info("示例2: 线程占用大量内存")
    thread_count = 100
    logger.info(f"即将创建 {thread_count} 个线程，每个线程预计消耗 ~8MB 内存")

    threads = [threading.Thread(target=dummy_task) for _ in range(thread_count)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    logger.info("线程已全部完成")


# 示例3：频繁启动/停止线程带来性能损耗
def example_thread_creation_overhead():
    """
    频繁创建和销毁线程会导致上下文切换开销大，影响性能。
    """

    def task():
        pass  # 仅测试线程创建开销

    logger.info("示例3: 频繁创建线程带来的性能开销")

    num_tasks = 1000
    start_time = time.time()

    threads = []
    for _ in range(num_tasks):
        t = threading.Thread(target=task)
        threads.append(t)
        t.start()
    for t in threads:
        t.join()

    duration = time.time() - start_time
    logger.info(f"执行 {num_tasks} 个线程耗时: {duration:.4f}s")


# 示例4：线程内异常不会传播到主线程
def example_thread_exception_handling():
    """
    线程内的异常不会自动传播到主线程，需要手动捕获和处理。
    """

    logger.info("示例4: 线程内异常不会自动传播到主线程")

    def faulty_task():
        raise RuntimeError("故意抛出的异常")

    fake_stderr = StringIO()
    with contextlib.redirect_stderr(fake_stderr):
        t = threading.Thread(target=faulty_task)
        t.start()
        t.join()

    error_output = fake_stderr.getvalue()
    logger.info("异常信息被捕获并写入 stderr:")
    logger.info(error_output)


# 示例5：推荐使用 ThreadPoolExecutor 替代手动管理线程
def example_thread_pool_executor():
    """
    使用 ThreadPoolExecutor 更高效地管理线程，避免频繁创建销毁。
    """

    from concurrent.futures import ThreadPoolExecutor

    logger.info("示例5: 推荐使用 ThreadPoolExecutor 替代手动管理线程")

    def task(x):
        return x * x

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(task, i) for i in range(10)]
        results = [future.result() for future in futures]

    logger.info(f"计算结果: {results}")


# 主函数运行所有示例
def main():
    logger.info("开始运行示例程序...")

    example_lock_usage()
    example_thread_memory_usage()
    example_thread_creation_overhead()
    example_thread_exception_handling()
    example_thread_pool_executor()

    logger.info("所有示例运行完毕。")


if __name__ == "__main__":
    main()
