"""
本模块演示了使用 Python 的 threading 和 queue 模块实现并发处理的多个示例。
涵盖以下内容：
1. 使用 `Thread` 实现并行 I/O 处理（存在问题）
2. 使用 `Queue` 优化线程管理，提高可扩展性（基本用法）
3. 多阶段流水线处理（扇入/扇出）（进阶用法）
4. 异常传播与调试（错误处理机制）

目标是通过对比不同实现方式，展示 `Queue` 在多线程编程中的优势与限制。
"""

import logging
import threading
from queue import Queue, Empty, ShutDown

# 配置日志系统
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 定义全局状态
ALIVE = "*"
EMPTY = "-"


class SimulationError(Exception):
    """用于封装模拟过程中的异常"""
    pass


class Grid:
    """表示生命游戏的二维网格，不使用锁"""

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
    """支持线程安全操作的 Grid 类"""

    def __init__(self, height, width):
        super().__init__(height, width)
        self.lock = threading.Lock()

    def __str__(self):
        with self.lock:
            return super().__str__()

    def get(self, y, x):
        with self.lock:
            return super().get(y, x)

    def set(self, y, x, state):
        with self.lock:
            return super().set(y, x, state)


class StoppableWorker(threading.Thread):
    """可停止的线程类，用于消费队列任务"""

    def __init__(self, func, in_queue, out_queue, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.func = func
        self.in_queue = in_queue
        self.out_queue = out_queue

    def run(self):
        while True:
            try:
                item = self.in_queue.get(timeout=1)  # 设置超时防止死锁
                result = self.func(item)
                self.out_queue.put(result)
                self.in_queue.task_done()
            except Empty:
                logger.debug("Input queue is empty, stopping worker.")
                break
            except ShutDown:
                logger.info("Shutting down worker thread.")
                return
            except Exception as e:
                logger.error(f"Error processing item: {e}", exc_info=True)


def count_neighbors(y, x, get_cell):
    """计算某个位置周围的活细胞数量"""
    n_ = get_cell(y - 1, x + 0)  # North
    ne = get_cell(y - 1, x + 1)  # Northeast
    e_ = get_cell(y + 0, x + 1)  # East
    se = get_cell(y + 1, x + 1)  # Southeast
    s_ = get_cell(y + 1, x + 0)  # South
    sw = get_cell(y + 1, x - 1)  # Southwest
    w_ = get_cell(y + 0, x - 1)  # West
    nw = get_cell(y - 1, x - 1)  # Northwest
    neighbor_states = [n_, ne, e_, se, s_, sw, w_, nw]
    count = 0
    for state in neighbor_states:
        if state == ALIVE:
            count += 1
    return count


def game_logic(state, neighbors):
    """核心逻辑：根据当前状态和邻居数量决定下一步状态"""
    if state == ALIVE:
        if neighbors < 2:
            return EMPTY
        elif neighbors > 3:
            return EMPTY
    else:
        if neighbors == 3:
            return ALIVE
    return state


def game_logic_with_io(state, neighbors):
    """模拟 I/O 操作的 game_logic"""
    raise OSError("Problem with I/O in game_logic")


def simulate_threaded(grid):
    """
    错误示例：直接使用 Thread 实现并行模拟。
    存在资源浪费、难以调试、无法自动扩展等问题。
    """

    threads = []
    results = []

    def worker(y, x, state, neighbors):
        try:
            next_state = game_logic(state, neighbors)
        except Exception as e:
            next_state = e
        results.append((y, x, next_state))

    for y in range(grid.height):
        for x in range(grid.width):
            state = grid.get(y, x)
            neighbors = count_neighbors(y, x, grid.get)
            thread = threading.Thread(target=worker, args=(y, x, state, neighbors))
            threads.append(thread)
            thread.start()

    for thread in threads:
        thread.join()

    next_grid = Grid(grid.height, grid.width)
    for y, x, next_state in results:
        if isinstance(next_state, Exception):
            raise SimulationError(y, x) from next_state
        next_grid.set(y, x, next_state)

    return next_grid


def simulate_pipeline(grid, in_queue, out_queue):
    """
    正确示例：使用 Queue 实现线程池调度。
    支持扇入/扇出，资源可控，易于调试。
    """

    for y in range(grid.height):
        for x in range(grid.width):
            state = grid.get(y, x)
            neighbors = count_neighbors(y, x, grid.get)
            in_queue.put((y, x, state, neighbors))  # 扇出

    in_queue.join()
    item_count = out_queue.qsize()

    next_grid = Grid(grid.height, grid.width)
    for _ in range(item_count):
        y, x, next_state = out_queue.get()  # 扇入
        if isinstance(next_state, Exception):
            raise SimulationError(y, x) from next_state
        next_grid.set(y, x, next_state)

    return next_grid


def simulate_phased_pipeline(grid, in_queue, logic_queue, out_queue):
    """
    进阶示例：多阶段流水线，包含两个阶段的扇入/扇出。
    更复杂的场景，展示了如何将多个任务串联执行。
    """

    for y in range(grid.height):
        for x in range(grid.width):
            state = grid.get(y, x)
            item = (y, x, state, grid.get)
            in_queue.put(item)  # 第一阶段扇出

    in_queue.join()
    logic_queue.join()
    item_count = out_queue.qsize()

    next_grid = LockingGrid(grid.height, grid.width)
    for _ in range(item_count):
        y, x, next_state = out_queue.get()  # 最终结果收集
        if isinstance(next_state, Exception):
            raise SimulationError(y, x) from next_state
        next_grid.set(y, x, next_state)

    return next_grid


def count_neighbors_thread(item):
    """用于线程的邻居计数函数"""
    y, x, state, get_cell = item
    try:
        neighbors = count_neighbors(y, x, get_cell)
    except Exception as e:
        neighbors = e
    return (y, x, state, neighbors)


def game_logic_thread(item):
    """用于线程的核心逻辑处理函数"""
    y, x, state, neighbors = item
    if isinstance(neighbors, Exception):
        next_state = neighbors
    else:
        try:
            next_state = game_logic(state, neighbors)
        except Exception as e:
            next_state = e
    return (y, x, next_state)


def main():
    """主函数，运行所有示例"""

    logger.info("开始运行错误示例：simulate_threaded")
    try:
        grid = Grid(5, 9)
        grid.set(0, 3, ALIVE)
        grid.set(1, 4, ALIVE)
        grid.set(2, 2, ALIVE)
        grid.set(2, 3, ALIVE)
        grid.set(2, 4, ALIVE)

        next_grid = simulate_threaded(grid)
        logger.info("simulate_threaded 结果:\n%s", next_grid)
    except Exception as e:
        logger.error("simulate_threaded 出错: %s", e)

    logger.info("开始运行正确示例：simulate_pipeline")
    try:
        in_queue = Queue()
        out_queue = Queue()

        threads = []
        for _ in range(5):
            thread = StoppableWorker(game_logic_thread, in_queue, out_queue)
            thread.start()
            threads.append(thread)

        next_grid = simulate_pipeline(grid, in_queue, out_queue)
        logger.info("simulate_pipeline 结果:\n%s", next_grid)

        in_queue.shutdown()
        for thread in threads:
            thread.join()
    except Exception as e:
        logger.error("simulate_pipeline 出错: %s", e)

    logger.info("开始运行进阶示例：simulate_phased_pipeline")
    try:
        in_queue = Queue()
        logic_queue = Queue()
        out_queue = Queue()

        threads = []
        for _ in range(5):
            thread = StoppableWorker(count_neighbors_thread, in_queue, logic_queue)
            thread.start()
            threads.append(thread)

        for _ in range(5):
            thread = StoppableWorker(game_logic_thread, logic_queue, out_queue)
            thread.start()
            threads.append(thread)

        next_grid = simulate_phased_pipeline(grid, in_queue, logic_queue, out_queue)
        logger.info("simulate_phased_pipeline 结果:\n%s", next_grid)

        in_queue.shutdown()
        logic_queue.shutdown()
        for thread in threads:
            thread.join()
    except Exception as e:
        logger.error("simulate_phased_pipeline 出错: %s", e)


if __name__ == "__main__":
    main()
