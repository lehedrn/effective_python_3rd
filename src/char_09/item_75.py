"""
本文件演示了如何使用协程实现高度并发的I/O操作。
它包括了错误示例和正确示例，每个示例都定义在一个独立的函数中，
并通过main函数运行完整的示例。

注意事项:
- 使用async关键字定义的函数称为协程
- 协程提供了一种有效的方法来运行数万个看似同时执行的函数
- 协程可以使用扇出(fan-out)和扇入(fan-in)来并行化I/O操作
"""

import asyncio
import logging

# 配置日志系统
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

ALIVE = "*"
EMPTY = "-"


class Grid:
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


def count_neighbors(y, x, get_cell):
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


class ColumnPrinter:
    def __init__(self):
        self.columns = []

    def append(self, data):
        self.columns.append(data)

    def __str__(self):
        row_count = 1
        for data in self.columns:
            row_count = max(row_count, len(data.splitlines()) + 1)

        rows = [""] * row_count
        for j in range(row_count):
            for i, data in enumerate(self.columns):
                line = data.splitlines()[max(0, j - 1)]
                if j == 0:
                    padding = " " * (len(line) // 2)
                    rows[j] += padding + str(i) + padding
                else:
                    rows[j] += line

                if (i + 1) < len(self.columns):
                    rows[j] += " | "

        return "\n".join(rows)


async def game_logic_without_io(state, neighbors):
    """一个没有IO操作的game_logic协程示例"""
    if state == ALIVE:
        if neighbors < 2:
            return EMPTY
        elif neighbors > 3:
            return EMPTY
    else:
        if neighbors == 3:
            return ALIVE
    return state


async def step_cell_without_io(y, x, get_cell, set_cell):
    """一个没有IO操作的step_cell协程示例"""
    state = get_cell(y, x)
    neighbors = count_neighbors(y, x, get_cell)
    next_state = await game_logic_without_io(state, neighbors)
    set_cell(y, x, next_state)


async def simulate_without_io(grid: Grid) -> Grid:
    """一个没有IO操作的simulate协程示例"""
    next_grid = Grid(grid.height, grid.width)

    tasks = []
    for y in range(grid.height):
        for x in range(grid.width):
            task = step_cell_without_io(y, x, grid.get, next_grid.set)
            tasks.append(task)

    await asyncio.gather(*tasks)
    return next_grid


def error_example_coroutine():
    """
    错误示例：试图同步调用协程

    这个"示例"展示了一个常见的错误：
    开发者可能误以为直接调用协程函数会立即执行其代码体，
    但实际上这只会创建一个协程对象而不执行它。
    """
    logger.info("错误示例：试图同步调用协程")

    grid = Grid(5, 9)
    grid.set(0, 3, ALIVE)
    grid.set(1, 4, ALIVE)
    grid.set(2, 2, ALIVE)
    grid.set(2, 3, ALIVE)
    grid.set(2, 4, ALIVE)

    try:
        # 错误：直接调用协程函数而不await或调度它
        result = simulate_without_io(grid)
        logger.info(f"错误地调用协程但未等待，结果是一个协程对象: {result}")
    except Exception as e:
        logger.error(f"这个示例不会抛出异常，但代码未能正确执行协程: {e}")


def correct_example_without_io():
    """
    正确示例：使用asyncio.run正确执行协程

    这个示例展示了如何使用asyncio.run正确执行协程，
    并在主线程中驱动事件循环。
    """
    logger.info("正确示例：使用asyncio.run正确执行协程")

    grid = Grid(5, 9)
    grid.set(0, 3, ALIVE)
    grid.set(1, 4, ALIVE)
    grid.set(2, 2, ALIVE)
    grid.set(2, 3, ALIVE)
    grid.set(2, 4, ALIVE)

    columns = ColumnPrinter()
    for i in range(5):
        columns.append(str(grid))
        # 正确：使用asyncio.run执行主协程
        grid = asyncio.run(simulate_without_io(grid))

    logger.info("模拟完成，最终状态:\n%s", columns)


async def game_logic_with_io(state, neighbors):
    """一个带有IO操作的game_logic协程示例"""
    if state == ALIVE:
        if neighbors < 2:
            return EMPTY
        elif neighbors > 3:
            return EMPTY
    else:
        if neighbors == 3:
            return ALIVE
    return state


async def step_cell_with_io(y, x, get_cell, set_cell):
    """一个带有IO操作的step_cell协程示例"""
    state = get_cell(y, x)
    neighbors = count_neighbors(y, x, get_cell)
    next_state = await game_logic_with_io(state, neighbors)
    set_cell(y, x, next_state)


async def simulate_with_io(grid: Grid) -> Grid:
    """一个带有IO操作的simulate协程示例"""
    next_grid = Grid(grid.height, grid.width)

    tasks = []
    for y in range(grid.height):
        for x in range(grid.width):
            task = step_cell_with_io(y, x, grid.get, next_grid.set)
            tasks.append(task)

    await asyncio.gather(*tasks)
    return next_grid


def correct_example_with_io():
    """
    正确示例：协程中的IO操作

    这个示例展示了如何在协程中处理IO操作，
    虽然在这个例子中我们只是简单地模拟IO操作而不是真正的网络IO。
    """
    logger.info("正确示例：协程中的IO操作")

    grid = Grid(5, 9)
    grid.set(0, 3, ALIVE)
    grid.set(1, 4, ALIVE)
    grid.set(2, 2, ALIVE)
    grid.set(2, 3, ALIVE)
    grid.set(2, 4, ALIVE)

    columns = ColumnPrinter()
    for i in range(5):
        columns.append(str(grid))
        grid = asyncio.run(simulate_with_io(grid))

    logger.info("模拟完成，最终状态:\n%s", columns)


async def count_neighbors_with_io(y, x, get_cell):
    """一个带有IO操作的count_neighbors协程示例"""
    # 模拟IO操作，比如从网络获取邻居状态
    await asyncio.sleep(0)  # 模拟IO操作

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


async def step_cell_with_io_in_neighbors(y, x, get_cell, set_cell):
    """一个在count_neighbors中使用IO的step_cell协程示例"""
    state = get_cell(y, x)
    neighbors = await count_neighbors_with_io(y, x, get_cell)
    next_state = await game_logic_without_io(state, neighbors)
    set_cell(y, x, next_state)


async def simulate_with_io_in_neighbors(grid: Grid) -> Grid:
    """一个在count_neighbors中使用IO的simulate协程示例"""
    next_grid = Grid(grid.height, grid.width)

    tasks = []
    for y in range(grid.height):
        for x in range(grid.width):
            task = step_cell_with_io_in_neighbors(y, x, grid.get, next_grid.set)
            tasks.append(task)

    await asyncio.gather(*tasks)
    return next_grid


def example_with_io_in_neighbors():
    """
    示例：在count_neighbors中使用IO

    这个示例展示了如何在count_neighbors函数中使用IO操作，
    展示了协程在重构以支持IO方面的灵活性。
    """
    logger.info("示例：在count_neighbors中使用IO")

    grid = Grid(5, 9)
    grid.set(0, 3, ALIVE)
    grid.set(1, 4, ALIVE)
    grid.set(2, 2, ALIVE)
    grid.set(2, 3, ALIVE)
    grid.set(2, 4, ALIVE)

    columns = ColumnPrinter()
    for i in range(5):
        columns.append(str(grid))
        grid = asyncio.run(simulate_with_io_in_neighbors(grid))

    logger.info("模拟完成，最终状态:\n%s", columns)


def main():
    """主函数：运行所有示例"""
    logger.info("开始运行所有示例")

    logger.info("\n" + "-"*50)
    logger.info("错误示例：试图同步调用协程")
    error_example_coroutine()

    logger.info("\n" + "-"*50)
    logger.info("正确示例：使用asyncio.run正确执行协程")
    correct_example_without_io()

    logger.info("\n" + "-"*50)
    logger.info("正确示例：协程中的IO操作")
    correct_example_with_io()

    logger.info("\n" + "-"*50)
    logger.info("示例：在count_neighbors中使用IO")
    example_with_io_in_neighbors()

    logger.info("\n所有示例运行完毕")


if __name__ == "__main__":
    main()
