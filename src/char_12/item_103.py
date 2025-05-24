"""
本模块演示了在 Python 中使用 `list` 和 `deque` 实现生产者-消费者队列的正确与错误方式。
重点对比了两者的性能差异，并展示了为何优先推荐使用 `collections.deque`。

包含以下示例：
1. 使用 list 作为 FIFO 队列（性能差）
2. 使用 deque 作为 FIFO 队列（高性能）
3. 性能基准测试：list vs deque
"""

import logging
from collections import deque
import timeit

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# =============================
# 示例 1: 使用 list 作为 FIFO 队列（不推荐）
# =============================

class Email:
    def __init__(self, sender, receiver, message):
        self.sender = sender
        self.receiver = receiver
        self.message = message


class NoEmailError(Exception):
    pass


def try_receive_email(reset=False):
    """
    模拟接收邮件，返回 Email 实例或抛出 NoEmailError 异常。
    reset 参数用于强制重置邮件列表。
    """
    if not hasattr(try_receive_email, 'emails') or reset:
        # 初始化模拟邮件数据
        try_receive_email.emails = [
            Email("a@example.com", "b@example.com", "Hello 1"),
            Email("c@example.com", "d@example.com", "Hello 2"),
            None,
            Email("e@example.com", "f@example.com", "Hello 3"),
            None,
            Email("g@example.com", "h@example.com", "Hello 4"),
        ]
    if not try_receive_email.emails:
        raise NoEmailError("No more emails to receive.")
    email = try_receive_email.emails.pop(0)
    logger.info(f"Produced email: {email.message if email else 'None'}")
    return email



def produce_emails_with_list(queue):
    """
    使用 list 作为队列的生产者函数。
    只将非 None 的 Email 实例加入队列。
    """
    while True:
        try:
            email = try_receive_email()
        except NoEmailError:
            break
        if email is not None:
            queue.append(email)



def consume_one_email_with_list(queue):
    if not queue:
        return
    email = queue.pop(0)
    if email is not None:
        logger.info(f"Consumed email: {email.message}")
    else:
        logger.warning("Consumed a None value from the queue.")



def run_list_fifo_queue():
    queue = []
    keep_running = lambda: len(queue) > 0

    logger.info("开始运行 list 作为队列的生产者-消费者模型")
    try_receive_email(reset=True)  # 重置邮件数据
    produce_emails_with_list(queue)
    while keep_running():
        consume_one_email_with_list(queue)
    logger.info("list 队列处理完成")


# =============================
# 示例 2: 使用 deque 作为 FIFO 队列（推荐）
# =============================

def consume_one_email_with_deque(queue):
    """
    使用 deque 作为队列的消费者函数（高性能）。
    增加对 None 的安全检查。
    """
    if not queue:
        return
    email = queue.popleft()
    if email is not None:
        logger.info(f"Consumed email: {email.message}")
    else:
        logger.warning("Consumed a None value from the deque queue.")



def run_deque_fifo_queue():
    queue = deque()
    keep_running = lambda: len(queue) > 0

    logger.info("开始运行 deque 作为队列的生产者-消费者模型")
    try_receive_email(reset=True)  # 重置邮件数据
    produce_emails_with_list(queue)
    while keep_running():
        consume_one_email_with_deque(queue)
    logger.info("deque 队列处理完成")



# =============================
# 示例 3: 性能基准测试
# =============================

def benchmark_list_append(count):
    def run(queue):
        for i in range(count):
            queue.append(i)

    return timeit.timeit(
        setup="queue = []",
        stmt="run(queue)",
        globals=locals(),
        number=1
    )


def benchmark_list_pop(count):
    def prepare():
        return list(range(count))

    def run(queue):
        while queue:
            queue.pop(0)

    return timeit.timeit(
        setup="queue = prepare()",
        stmt="run(queue)",
        globals=locals(),
        number=1
    )


def benchmark_deque_append(count):
    def run(queue):
        for i in range(count):
            queue.append(i)

    return timeit.timeit(
        setup="from collections import deque; queue = deque()",
        stmt="run(queue)",
        globals=locals(),
        number=1
    )


def benchmark_deque_popleft(count):
    def prepare():
        from collections import deque
        return deque(range(count))

    def run(queue):
        while queue:
            queue.popleft()

    return timeit.timeit(
        setup="queue = prepare()",
        stmt="run(queue)",
        globals=locals(),
        number=1
    )


def run_benchmarks():
    logger.info("开始性能基准测试...")

    logger.info("测试 list.append 性能:")
    for i in range(1, 6):
        count = i * 1_000_000
        delay = benchmark_list_append(count)
        logger.info(f"Count {count:,} takes: {delay * 1e3:.2f}ms")

    logger.info("\n测试 list.pop(0) 性能:")
    for i in range(1, 6):
        count = i * 10_000
        delay = benchmark_list_pop(count)
        logger.info(f"Count {count:,} takes: {delay * 1e3:.2f}ms")

    logger.info("\n测试 deque.append 性能:")
    for i in range(1, 6):
        count = i * 100_000
        delay = benchmark_deque_append(count)
        logger.info(f"Count {count:,} takes: {delay * 1e3:.2f}ms")

    logger.info("\n测试 deque.popleft 性能:")
    for i in range(1, 6):
        count = i * 100_000
        delay = benchmark_deque_popleft(count)
        logger.info(f"Count {count:,} takes: {delay * 1e3:.2f}ms")


# =============================
# 主函数
# =============================

def main():
    logger.info("开始运行生产者-消费者队列示例程序")

    logger.info("\n===== 示例 1: 使用 list 作为 FIFO 队列（不推荐）=====")
    run_list_fifo_queue()

    logger.info("\n===== 示例 2: 使用 deque 作为 FIFO 队列（推荐）=====")
    run_deque_fifo_queue()

    logger.info("\n===== 示例 3: 性能基准测试 ====")
    run_benchmarks()


if __name__ == "__main__":
    main()
