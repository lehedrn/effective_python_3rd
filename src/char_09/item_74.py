"""
本模块演示了如何使用 `ThreadPoolExecutor` 来实现 I/O 并行处理，涵盖以下要点：
1. 使用 `ThreadPoolExecutor` 简化线程管理并提升性能。
2. 如何通过 `submit` 和 `result` 实现任务的并发执行和异常传播。
3. 展示错误示例（如直接创建线程）与正确示例（使用线程池）。
4. 通过 `max_workers` 控制线程数量，避免内存暴涨问题。
5. 结合《生命游戏》示例说明并发编程中的实际应用。

该模块定义了多个函数来展示不同场景下的线程行为，并在 main 函数中统一运行所有示例。
"""

import logging
import time
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

ALIVE = "*"
EMPTY = "-"

class Grid:
    """表示一个二维网格，用于模拟《生命游戏》的基本结构。"""

    def __init__(self, height, width):
        self.height = height
        self.width = width
        self.rows = []
        for _ in range(self.height):
            self.rows.append([EMPTY] * self.width)

    def get(self, y, x):
        return self.rows[y % self.height][x % self.width]

    def set(self, y, x, state):
        self.rows[y % self.height][x % self.width] = state

    def __str__(self):
        output = ""
        for row in self.rows:
            for cell in row:
                output += cell
            output += "\n"
        return output


class LockingGrid(Grid):
    """带锁的 Grid 类，确保多线程访问时的安全性。"""

    def __init__(self, height, width):
        super().__init__(height, width)
        self.lock = Lock()

    def __str__(self):
        with self.lock:
            return super().__str__()

    def get(self, y, x):
        with self.lock:
            return super().get(y, x)

    def set(self, y, x, state):
        with self.lock:
            return super().set(y, x, state)


def count_neighbors(y, x, get_cell):
    """
    计算指定位置周围存活细胞的数量。

    参数:
        y: 当前单元格的 y 坐标。
        x: 当前单元格的 x 坐标。
        get_cell: 获取某个坐标的细胞状态的函数。

    返回:
        neighbors: 存活细胞的数量。
    """
    n_ = get_cell(y - 1, x + 0)  # 北方
    ne = get_cell(y - 1, x + 1)  # 东北方
    e_ = get_cell(y + 0, x + 1)  # 东方
    se = get_cell(y + 1, x + 1)  # 东南方
    s_ = get_cell(y + 1, x + 0)  # 南方
    sw = get_cell(y + 1, x - 1)  # 西南方
    w_ = get_cell(y + 0, x - 1)  # 西方
    nw = get_cell(y - 1, x - 1)  # 西北方
    neighbor_states = [n_, ne, e_, se, s_, sw, w_, nw]
    count = 0
    for state in neighbor_states:
        if state == ALIVE:
            count += 1
    return count


def game_logic(state, neighbors):
    """
    根据当前细胞的状态和邻居数量决定下一步的状态。

    参数:
        state: 当前细胞的状态（存活或死亡）。
        neighbors: 活细胞邻居的数量。

    返回:
        next_state: 下一步的状态。
    """
    if state == ALIVE:
        if neighbors < 2:
            return EMPTY
        elif neighbors > 3:
            return EMPTY
    else:
        if neighbors == 3:
            return ALIVE
    return state


def step_cell(y, x, get_cell, set_cell):
    """
    处理单个细胞的状态更新。

    参数:
        y: 细胞的 y 坐标。
        x: 细胞的 x 坐标。
        get_cell: 获取细胞状态的函数。
        set_cell: 设置细胞状态的函数。
    """
    state = get_cell(y, x)
    neighbors = count_neighbors(y, x, get_cell)
    next_state = game_logic(state, neighbors)
    set_cell(y, x, next_state)


def simulate_pool(pool, grid):
    """
    使用线程池并发更新整个网格的状态。

    参数:
        pool: 用于提交任务的线程池。
        grid: 当前的网格实例。

    返回:
        next_grid: 更新后的网格实例。
    """
    next_grid = LockingGrid(grid.height, grid.width)

    futures = []
    for y in range(grid.height):
        for x in range(grid.width):
            args = (y, x, grid.get, next_grid.set)
            future = pool.submit(step_cell, *args)  # Fan-out
            futures.append(future)

    for future in futures:
        future.result()  # Fan-in

    return next_grid


def naive_threading_example():
    """
    错误示例：直接为每个单元格创建新线程。
    这会导致资源浪费和潜在的内存问题。
    """
    logging.info("开始错误示例：直接创建线程")
    grid = LockingGrid(5, 9)
    grid.set(0, 3, ALIVE)
    grid.set(1, 4, ALIVE)
    grid.set(2, 2, ALIVE)
    grid.set(2, 3, ALIVE)
    grid.set(2, 4, ALIVE)

    next_grid = LockingGrid(grid.height, grid.width)

    threads = []
    for y in range(grid.height):
        for x in range(grid.width):
            from threading import Thread
            args = (y, x, grid.get, next_grid.set)
            thread = Thread(target=step_cell, args=args)
            thread.start()
            threads.append(thread)

    for thread in threads:
        thread.join()

    logging.info("错误示例完成:\n%s", str(next_grid))


def correct_executor_example():
    """
    正确示例：使用 ThreadPoolExecutor 提高效率并简化线程管理。
    """
    logging.info("开始正确示例：使用 ThreadPoolExecutor")
    grid = LockingGrid(5, 9)
    grid.set(0, 3, ALIVE)
    grid.set(1, 4, ALIVE)
    grid.set(2, 2, ALIVE)
    grid.set(2, 3, ALIVE)
    grid.set(2, 4, ALIVE)

    with ThreadPoolExecutor(max_workers=10) as executor:
        next_grid = simulate_pool(executor, grid)

    logging.info("正确示例完成:\n%s", str(next_grid))


def exception_propagation_example():
    """
    示例：展示 ThreadPoolExecutor 如何自动传播异常。
    """

    def faulty_game_logic(state, neighbors):
        raise OSError("Problem with I/O")

    try:
        logging.info("开始异常传播示例")
        with ThreadPoolExecutor(max_workers=10) as executor:
            task = executor.submit(faulty_game_logic, ALIVE, 3)
            task.result()
    except Exception as e:
        logging.error("捕获到预期的异常: %s", e)


def limited_parallelism_issue():
    """
    示例：展示 ThreadPoolExecutor 在大规模数据上的限制。
    """
    logging.info("开始展示线程池限制")
    large_grid = LockingGrid(100, 100)
    for i in range(100):
        large_grid.set(i // 10, i % 10, ALIVE)

    start_time = time.time()
    with ThreadPoolExecutor(max_workers=100) as executor:
        next_grid = simulate_pool(executor, large_grid)
    end_time = time.time()

    logging.info("模拟耗时 %.2f 秒，网格大小 %d x %d", end_time - start_time, large_grid.height, large_grid.width)


def main():
    """
    主函数，运行所有示例。
    """
    logging.info("开始运行所有示例")

    logging.info("\n--- 错误示例：直接创建线程 ---")
    naive_threading_example()

    logging.info("\n--- 正确示例：使用 ThreadPoolExecutor ---")
    correct_executor_example()

    logging.info("\n--- 异常传播示例 ---")
    exception_propagation_example()

    logging.info("\n--- 线程池限制示例 ---")
    limited_parallelism_issue()

    logging.info("所有示例运行完毕")


if __name__ == "__main__":
    main()
