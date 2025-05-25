"""
本文件演示了如何使用 heapq 模块高效实现优先队列。
它展示了以下内容：
1. 使用 list 实现的低效优先队列及其性能问题。
2. heapq 的基本用法及类对象排序支持。
3. 正确处理书籍归还的情况。
4. 不同实现方式的性能对比。
"""

import heapq
import functools
import logging
import random
import timeit

# 配置日志系统
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# 1. 基于 list 的低效优先队列（按截止日期排序）
def example_inefficient_priority_queue():
    """
    使用 list 实现的基于排序的优先队列。
    缺点：每次添加元素都需要重新排序，时间复杂度为 O(n log n)。
    """

    class Book:
        def __init__(self, title, due_date):
            self.title = title
            self.due_date = due_date

        def __repr__(self):
            return f"{self.title} (Due: {self.due_date})"

    def add_book(queue, book):
        queue.append(book)
        # 每次插入后都要手动排序
        queue.sort(key=lambda b: b.due_date)

    def next_overdue_book(queue, now):
        if queue and queue[-1].due_date < now:
            return queue.pop()
        raise Exception("No overdue books")

    logger.info("示例 1: 使用 list 排序实现的低效优先队列")
    queue = []
    add_book(queue, Book("Don Quixote", "2019-06-07"))
    add_book(queue, Book("Frankenstein", "2019-06-05"))
    add_book(queue, Book("Les Misérables", "2019-06-08"))
    add_book(queue, Book("War and Peace", "2019-06-03"))

    try:
        overdue = next_overdue_book(queue, "2019-06-10")
        while overdue:
            logger.info(f"Overdue: {overdue}")
            overdue = next_overdue_book(queue, "2019-06-10")
    except Exception as e:
        logger.info(f"Exception: {e}")


# 2. 使用 heapq 实现的高效优先队列
def example_heapq_basic_usage():
    """
    使用 heapq 实现的优先队列。
    优势：heapq 内部维护堆结构，保证插入和弹出操作的时间复杂度为 O(log n)。
    """

    @functools.total_ordering
    class Book:
        def __init__(self, title, due_date):
            self.title = title
            self.due_date = due_date

        def __lt__(self, other):
            return self.due_date < other.due_date

        def __repr__(self):
            return f"{self.title} (Due: {self.due_date})"

    def add_book(queue, book):
        heapq.heappush(queue, book)

    def next_overdue_book(queue, now):
        while queue:
            book = queue[0]
            if book.due_date < now:
                return heapq.heappop(queue)
            else:
                break
        raise Exception("No overdue books")

    logger.info("示例 2: 使用 heapq 实现的高效优先队列")
    queue = []
    add_book(queue, Book("Pride and Prejudice", "2019-06-01"))
    add_book(queue, Book("The Time Machine", "2019-05-30"))
    add_book(queue, Book("Crime and Punishment", "2019-06-06"))
    add_book(queue, Book("Wuthering Heights", "2019-06-12"))

    try:
        overdue = next_overdue_book(queue, "2019-06-02")
        while overdue:
            logger.info(f"Overdue: {overdue}")
            overdue = next_overdue_book(queue, "2019-06-02")
    except Exception as e:
        logger.info(f"Exception: {e}")


# 3. 尝试不定义 __lt__ 方法会引发错误
def example_heapq_missing_lt_method():
    """
    错误示例：未定义 __lt__ 方法会导致 heapq 报错。
    heapq 要求队列中的对象必须是可比较大小的。
    """

    class Book:
        def __init__(self, title, due_date):
            self.title = title
            self.due_date = due_date

    logger.info("示例 3: 忘记定义 __lt__ 方法导致 heapq 出错")

    queue = []
    try:
        heapq.heappush(queue, Book("Little Women", "2019-06-05"))
    except TypeError as e:
        logger.error(f"TypeError: {e}")


# 4. 处理提前归还书籍的情况
def example_handle_book_returns():
    """
    示例展示如何在使用 heapq 时处理图书提前归还的问题。
    解决方案：标记为已归还，并忽略这些条目。
    """

    @functools.total_ordering
    class Book:
        def __init__(self, title, due_date):
            self.title = title
            self.due_date = due_date
            self.returned = False

        def __lt__(self, other):
            return self.due_date < other.due_date

        def __repr__(self):
            return f"{self.title} (Due: {self.due_date}, Returned: {self.returned})"

    def add_book(queue, book):
        heapq.heappush(queue, book)

    def next_overdue_book(queue, now):
        while queue:
            book = queue[0]
            if book.returned:
                heapq.heappop(queue)
                continue
            if book.due_date < now:
                return heapq.heappop(queue)
            else:
                break
        raise Exception("No overdue books")

    def return_book(book):
        book.returned = True

    logger.info("示例 4: 处理图书提前归还")
    queue = []
    book1 = Book("Treasure Island", "2019-06-04")
    book2 = Book("Moby Dick", "2019-06-10")

    add_book(queue, book1)
    add_book(queue, book2)

    logger.info(f"Before return: {queue}")
    return_book(book1)
    logger.info(f"After return: {queue}")

    try:
        overdue = next_overdue_book(queue, "2019-06-05")
        logger.info(f"Overdue: {overdue}")
    except Exception as e:
        logger.info(f"Exception: {e}")


# 5. 性能测试：list vs heapq
def example_performance_comparison():
    """
    对比 list 手动排序与 heapq 的性能差异。
    结论：随着数据量增大，heapq 明显优于 list。
    """

    def list_based_benchmark(count):
        def prepare():
            return [], list(range(count))

        def run(queue, items):
            for i in items:
                queue.append(i)
                queue.sort(reverse=True)
            while queue:
                queue.pop()

        return timeit.timeit(
            stmt="run(*prepare())",
            globals=locals(),
            number=1,
        )

    def heapq_based_benchmark(count):
        def prepare():
            return [], list(range(count))

        def run(queue, items):
            for i in items:
                heapq.heappush(queue, i)
            while queue:
                heapq.heappop(queue)

        return timeit.timeit(
            stmt="run(*prepare())",
            globals=locals(),
            number=1,
        )

    logger.info("示例 5: 性能对比 - list 排序 vs heapq")
    for count in [1000, 2000, 5000, 10000]:
        list_time = list_based_benchmark(count)
        heap_time = heapq_based_benchmark(count)
        logger.info(f"Count {count}: List Sort={list_time:.5f}s, Heapq={heap_time:.5f}s")


# 主函数运行所有示例
def main():
    example_inefficient_priority_queue()
    example_heapq_basic_usage()
    example_heapq_missing_lt_method()
    example_handle_book_returns()
    example_performance_comparison()


if __name__ == "__main__":
    main()
