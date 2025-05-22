"""
本模块演示了如何使用 `Queue` 协调线程间的工作。
主要涵盖以下内容：
- 使用自定义队列实现流水线处理工作流，以及其存在的问题（如忙等待、内存溢出等）
- 使用 Python 标准库中的 `queue.Queue` 实现更健壮的并发管道
- 演示错误示例与正确示例
"""

import logging
import time
from threading import Thread, Lock
from collections import deque
from queue import Queue, ShutDown

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# 错误示例：自定义队列的问题
class MyQueue:
    def __init__(self):
        self.items = deque()
        self.lock = Lock()

    def put(self, item):
        with self.lock:
            self.items.append(item)

    def get(self):
        with self.lock:
            return self.items.popleft()


class Worker(Thread):
    def __init__(self, func, in_queue, out_queue):
        super().__init__()
        self.func = func
        self.in_queue = in_queue
        self.out_queue = out_queue
        self.polled_count = 0
        self.work_done = 0

    def run(self):
        while True:
            self.polled_count += 1
            try:
                item = self.in_queue.get()
            except IndexError:
                time.sleep(0.01)  # No work to do
            except AttributeError:
                return
            else:
                result = self.func(item)
                self.out_queue.put(result)
                self.work_done += 1

def download(item):
    time.sleep(0.001)  # 模拟下载耗时
    # logger.info("Downloaded an item")
    return item


def resize(item):
    time.sleep(0.001)  # 模拟调整大小耗时
    # logger.info("Resized an item")
    return item


def upload(item):
    time.sleep(0.001)  # 模拟上传耗时
    # logger.info("Uploaded an item")
    return item

def bad_pipeline_example():
    """
    错误示例：使用自定义队列实现流水线，存在忙等待和资源浪费等问题。
    """

    logger.info("开始运行错误示例：自定义队列流水线")

    download_queue = MyQueue()
    resize_queue = MyQueue()
    upload_queue = MyQueue()
    done_queue = MyQueue()

    threads = [
        Worker(download, download_queue, resize_queue),
        Worker(resize, resize_queue, upload_queue),
        Worker(upload, upload_queue, done_queue),
    ]

    for thread in threads:
        thread.start()

    for _ in range(1000):
        download_queue.put(object())

    while len(done_queue.items) < 1000:
        time.sleep(0.1)

    for thread in threads:
        thread.in_queue = None
        thread.join()

    processed = len(done_queue.items)
    polled = sum(t.polled_count for t in threads)
    logger.info(f"Processed {processed} items after polling {polled} times")


# 正确示例：使用 queue.Queue 实现流水线
class StoppableWorker(Thread):
    def __init__(self, func, in_queue, out_queue):
        super().__init__()
        self.func = func
        self.in_queue = in_queue
        self.out_queue = out_queue

    def run(self):
        while True:
            try:
                item = self.in_queue.get()
            except ShutDown:
                return
            else:
                result = self.func(item)
                self.out_queue.put(result)
                self.in_queue.task_done()


def start_threads(count, *args):
    threads = [StoppableWorker(*args) for _ in range(count)]
    for thread in threads:
        thread.start()
    return threads


def drain_queue(input_queue):
    input_queue.shutdown()

    counter = 0

    while True:
        try:
            item = input_queue.get()
        except ShutDown:
            break
        else:
            input_queue.task_done()
            counter += 1

    input_queue.join()

    return counter


def good_pipeline_example():
    """
    正确示例：使用 queue.Queue 实现流水线，解决了忙等待、内存溢出等问题。
    """

    logger.info("开始运行正确示例：queue.Queue 流水线")

    download_queue = Queue()
    resize_queue = Queue(100)
    upload_queue = Queue(100)
    done_queue = Queue()

    threads = (
        start_threads(3, download, download_queue, resize_queue)
        + start_threads(4, resize, resize_queue, upload_queue)
        + start_threads(5, upload, upload_queue, done_queue)
    )

    for _ in range(2000):
        download_queue.put(object())

    download_queue.shutdown()
    download_queue.join()

    resize_queue.shutdown()
    resize_queue.join()

    upload_queue.shutdown()
    upload_queue.join()

    counter = drain_queue(done_queue)

    for thread in threads:
        thread.join()

    logger.info(f"{counter} items finished")


# 示例函数：展示 queue.Queue 的阻塞行为
def blocking_behavior_example():
    """
    示例：展示 queue.Queue 的阻塞行为，避免忙等待。
    """

    logger.info("开始运行 queue.Queue 阻塞行为示例")

    my_queue = Queue()

    def consumer():
        logger.info("Consumer waiting")
        my_queue.get()  # Runs after put() below
        logger.info("Consumer done")

    thread = Thread(target=consumer)
    thread.start()

    logger.info("Producer putting")
    my_queue.put(object())  # Runs before get() above
    logger.info("Producer done")

    thread.join()


# 示例函数：展示 queue.Queue 的反压机制
def backpressure_example():
    """
    示例：展示 queue.Queue 的缓冲区大小限制，防止内存溢出。
    """

    logger.info("开始运行 queue.Queue 缓冲区大小限制示例")

    my_queue = Queue(1)  # Buffer size of 1

    def consumer():
        time.sleep(0.1)  # Wait
        my_queue.get()   # Runs second
        logger.info("Consumer got 1")
        my_queue.get()   # Runs fourth
        logger.info("Consumer got 2")
        logger.info("Consumer done")

    thread = Thread(target=consumer)
    thread.start()

    my_queue.put(object())  # Runs first
    logger.info("Producer put 1")
    my_queue.put(object())  # Runs third
    logger.info("Producer put 2")
    logger.info("Producer done")

    thread.join()


# 示例函数：展示 queue.Queue 的任务完成跟踪
def task_done_example():
    """
    示例：展示 queue.Queue 的 task_done 和 join 方法，避免轮询。
    """

    logger.info("开始运行 queue.Queue 任务完成跟踪示例")

    in_queue = Queue()

    def consumer():
        logger.info("Consumer waiting")
        work = in_queue.get()      # Runs second
        logger.info("Consumer working")
        logger.info("Consumer done")
        in_queue.task_done()       # Runs third

    thread = Thread(target=consumer)
    thread.start()

    logger.info("Producer putting")
    in_queue.put(object()) # Runs first
    logger.info("Producer waiting")
    in_queue.join() # Runs fourth
    logger.info("Producer done")

    thread.join()


# 示例函数：展示 queue.Queue 的 shutdown 功能
def shutdown_example():
    """
    示例：展示 queue.Queue 的 shutdown 方法，优雅终止线程。
    """

    logger.info("开始运行 queue.Queue shutdown 示例")

    my_queue2 = Queue()

    def consumer():
        while True:
            try:
                item = my_queue2.get()
            except ShutDown:
                logger.info("Terminating!")
                return
            else:
                logger.info("Got item %s", item)
                my_queue2.task_done()

    thread = Thread(target=consumer)

    my_queue2.put(1)
    my_queue2.put(2)
    my_queue2.put(3)
    my_queue2.shutdown()

    thread.start()

    my_queue2.join()
    thread.join()
    logger.info("Done")


def main():
    """
    主函数：依次运行所有示例
    """
    bad_pipeline_example()
    good_pipeline_example()
    blocking_behavior_example()
    backpressure_example()
    task_done_example()
    shutdown_example()


if __name__ == "__main__":
    main()
