"""
本文件演示了 Python 中线程的使用场景及其限制。
主要包含以下内容：

1. 使用多线程进行计算密集型任务（受限于 GIL，无法提升性能）。
2. 使用多线程处理阻塞 I/O 任务（可以有效并行化）。
3. 展示错误使用线程的情况和正确使用方式。

遵循 PEP8 规范，并使用 logging 替代 print 输出信息。
"""

import threading
import time
import select
import socket
import logging

# 配置日志输出
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 计算密集型任务：因数分解
def factorize(number):
    """
    对一个数字进行因数分解，返回所有因数。

    Args:
        number (int): 要分解的数字。

    Returns:
        list: 所有能整除 number 的因数。
    """
    factors = []
    for i in range(1, number + 1):
        if number % i == 0:
            factors.append(i)
    return factors


# 错误示例：多线程用于计算密集型任务（无法提升性能）
def bad_example_threaded_computation():
    """
    错误示例：尝试使用多线程来加速计算密集型任务。
    由于 GIL 的存在，这种方式并不会提升性能。
    """
    numbers = [7775876, 6694411, 5038540, 5426782,
               9934740, 9168996, 5271226, 8288002,
               9403196, 6678888, 6776096, 9582542,
               7107467, 9633726, 5747908, 7613918]

    class FactorizeThread(threading.Thread):
        def __init__(self, number):
            super().__init__()
            self.number = number

        def run(self):
            self.factors = factorize(self.number)

    threads = []
    start_time = time.perf_counter()

    for number in numbers:
        thread = FactorizeThread(number)
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    end_time = time.perf_counter()
    logging.info("Bad Example (Threaded Computation) Took %.3f seconds", end_time - start_time)


# 正确示例：多线程用于阻塞 I/O 任务（可以有效并行）
def good_example_threaded_io():
    """
    正确示例：使用多线程执行阻塞 I/O 操作。
    在这种情况下，GIL 不会成为瓶颈，系统调用可以在多个线程中并行执行。
    """

    def slow_systemcall():
        select.select([socket.socket()], [], [], 0.1)

    threads = []

    start_time = time.perf_counter()

    for _ in range(5):
        thread = threading.Thread(target=slow_systemcall)
        thread.start()
        threads.append(thread)

    # 模拟主线程计算工作
    def compute_helicopter_location(index):
        pass

    for i in range(5):
        compute_helicopter_location(i)

    for thread in threads:
        thread.join()

    end_time = time.perf_counter()
    logging.info("Good Example (Threaded I/O) Took %.3f seconds", end_time - start_time)


# 串行执行计算密集型任务作为基准
def serial_computation():
    """
    串行执行计算密集型任务，用于对比多线程版本的性能。
    """
    numbers = [7775876, 6694411, 5038540, 5426782,
               9934740, 9168996, 5271226, 8288002,
               9403196, 6678888, 6776096, 9582542,
               7107467, 9633726, 5747908, 7613918]

    start_time = time.perf_counter()

    for number in numbers:
        factorize(number)

    end_time = time.perf_counter()
    logging.info("Serial Computation Took %.3f seconds", end_time - start_time)


# 主函数，运行所有示例
def main():
    logging.info("开始运行示例...")

    logging.info("\n--- 运行串行计算任务 ---")
    serial_computation()

    logging.info("\n--- 错误示例：多线程用于计算密集型任务 ---")
    bad_example_threaded_computation()

    logging.info("\n--- 正确示例：多线程用于阻塞 I/O 任务 ---")
    good_example_threaded_io()

    logging.info("\n--- 示例运行完成 ---")


if __name__ == "__main__":
    main()
