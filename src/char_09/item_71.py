"""
本模块演示如何识别何时需要并发处理（Item 71）。
包含以下内容：
- 康威生命游戏的基本实现
- 错误示例：在串行中执行 I/O 操作导致性能问题
- 正确示例：准备用于并发处理的结构
"""

import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

ALIVE = "*"
EMPTY = "-"


class Grid:
    """
    表示康威生命游戏中的网格，每个细胞可以存活或空着。
    网格支持坐标循环访问（即超出边界的坐标会“环绕”）。
    """

    def __init__(self, height: int, width: int):
        self.height = height
        self.width = width
        self.rows = [[EMPTY] * width for _ in range(height)]

    def get(self, y: int, x: int) -> str:
        return self.rows[y % self.height][x % self.width]

    def set(self, y: int, x: int, state: str):
        self.rows[y % self.height][x % self.width] = state

    def __str__(self):
        return "\n".join("".join(row) for row in self.rows)


def count_neighbors(y: int, x: int, get_cell) -> int:
    """
    统计指定位置周围活着的邻居数量。
    使用传入的 get_cell 函数来获取邻居状态，避免直接依赖 Grid 类。
    """
    neighbor_states = [
        get_cell(y - 1, x),     # North
        get_cell(y - 1, x + 1), # Northeast
        get_cell(y, x + 1),     # East
        get_cell(y + 1, x + 1), # Southeast
        get_cell(y + 1, x),     # South
        get_cell(y + 1, x - 1), # Southwest
        get_cell(y, x - 1),     # West
        get_cell(y - 1, x - 1), # Northwest
    ]
    return sum(1 for state in neighbor_states if state == ALIVE)


def game_logic(state: str, neighbors: int) -> str:
    """
    根据当前细胞状态和邻居数量决定下一代的状态。
    这是游戏的核心逻辑。
    """
    if state == ALIVE:
        if neighbors < 2 or neighbors > 3:
            return EMPTY  # 死亡
    else:
        if neighbors == 3:
            return ALIVE  # 复活
    return state


def step_cell(y: int, x: int, get_cell, set_cell):
    """
    对单个细胞进行一次更新操作。
    该函数是解耦设计的一部分，不直接依赖 Grid 实例。
    """
    current_state = get_cell(y, x)
    neighbors = count_neighbors(y, x, get_cell)
    next_state = game_logic(current_state, neighbors)
    set_cell(y, x, next_state)


def simulate(grid: Grid) -> Grid:
    """
    对整个网格进行一次更新，生成下一代。
    使用函数接口 get 和 set 来保证同步更新。
    """
    next_grid = Grid(grid.height, grid.width)
    for y in range(grid.height):
        for x in range(grid.width):
            step_cell(y, x, grid.get, next_grid.set)
    return next_grid


def error_example():
    """
    错误示例：在 game_logic 中添加阻塞 I/O 会导致性能瓶颈。
    在此示例中，模拟了一个耗时操作（sleep），展示了串行执行的问题。
    """
    logger.info("开始运行错误示例：串行执行并模拟阻塞 I/O")

    from time import sleep

    global game_logic
    original_game_logic = game_logic

    def slow_game_logic(state: str, neighbors: int) -> str:
        # 模拟一个耗时的 I/O 操作（例如网络请求）
        sleep(0.1)
        return original_game_logic(state, neighbors)

    # Monkey patch game_logic to simulate blocking I/O
    game_logic = slow_game_logic

    grid = Grid(5, 9)
    grid.set(0, 3, ALIVE)
    grid.set(1, 4, ALIVE)
    grid.set(2, 2, ALIVE)
    grid.set(2, 3, ALIVE)
    grid.set(2, 4, ALIVE)

    try:
        for i in range(5):
            logger.info(f"Generation {i}:\n{grid}")
            grid = simulate(grid)
    finally:
        # Restore original logic
        game_logic = original_game_logic


def correct_preparation_for_concurrency():
    """
    正确示例：准备用于并发处理的结构。
    展示了如何将 game_logic 改造成异步友好的形式，
    并保持 simulate 函数不变，便于后续扩展为多线程或多进程。
    """
    logger.info("开始运行正确示例：准备用于并发处理的结构")

    from threading import Thread

    def threaded_step(y: int, x: int, get_cell, set_cell):
        """
        将 step_cell 包装成线程安全的版本。
        注意：这只是一个示例，实际应使用更高级的并发机制如 ThreadPoolExecutor。
        """
        thread = Thread(target=step_cell, args=(y, x, get_cell, set_cell))
        thread.start()
        return thread

    grid = Grid(5, 9)
    grid.set(0, 3, ALIVE)
    grid.set(1, 4, ALIVE)
    grid.set(2, 2, ALIVE)
    grid.set(2, 3, ALIVE)
    grid.set(2, 4, ALIVE)

    for i in range(5):
        logger.info(f"Generation {i}:\n{grid}")
        threads = []
        next_grid = Grid(grid.height, grid.width)
        for y in range(grid.height):
            for x in range(grid.width):
                threads.append(threaded_step(y, x, grid.get, next_grid.set))

        # Wait for all threads to complete
        for t in threads:
            t.join()

        grid = next_grid


def main():
    """
    主函数，依次运行错误示例和正确示例。
    """
    logger.info("开始运行 Item 71 示例程序")
    error_example()
    correct_preparation_for_concurrency()
    logger.info("所有示例运行完成")


if __name__ == "__main__":
    main()
