# Chapter 9: Concurrency and Parallelism (并发与并行)

## Item 74: Consider `ThreadPoolExecutor` When Threads Are Necessary for Concurrency (当确实需要使用线程实现并发时，优先考虑使用`ThreadPoolExecutor`)

Python includes the `concurrent.futures` built-in module, which provides the `ThreadPoolExecutor` class. It combines the best of the `Thread` (see Item 72: “Avoid Creating New `Thread` Instances for On￾demand Fan-out”) and `Queue` (see Item 73: “Understand How Using `Queue` for Concurrency Requires Refactoring”) approaches to solving the parallel I/O problem from the Game of Life example (see Item 71: “Know How to Recognize When Concurrency Is Necessary” for background and the implementations of various functions and classes below):

Python 包含了 `concurrent.futures` 内建模块，它提供了 `ThreadPoolExecutor` 类。它结合了 `Thread`（参见条目72：“避免为按需发散创建新的 `Thread` 实例”）和 `Queue`（参见条目73：“了解在并发中使用 `Queue` 需要重构”）方法的优点，用于解决《生命游戏》示例中的并行 I/O 问题（参见条目71：“知道如何识别何时需要并发”以获取背景信息及下面各种函数和类的实现）：

```
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


from threading import Lock

class LockingGrid(Grid):
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
    # Do some blocking input/output in here:
    data = my_socket.recv(100)

def game_logic(state, neighbors):
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
    state = get_cell(y, x)
    neighbors = count_neighbors(y, x, get_cell)
    next_state = game_logic(state, neighbors)
    set_cell(y, x, next_state)
```

Instead of starting a new `Thread` instance for each `Grid` square, I can fan-out by submitting a function to an executor that will be run in a separate thread. Later, I can wait for the result of all tasks in order to fan-in:

与其为每个 `Grid` 方格启动一个新的 `Thread` 实例，不如通过提交一个将在另一个线程中运行的函数来扩展。之后，我可以等待所有任务的结果以便聚合：

```
from concurrent.futures import ThreadPoolExecutor

def simulate_pool(pool, grid):
    next_grid = LockingGrid(grid.height, grid.width)

    futures = []
    for y in range(grid.height):
        for x in range(grid.width):
            args = (y, x, grid.get, next_grid.set)
            future = pool.submit(step_cell, *args)  # Fan-out
            futures.append(future)

    for future in futures:
        future.result()                             # Fan-in

    return next_grid
```

The threads used for the executor can be allocated in advance, which means that I don’t have to pay the startup cost on each execution of `simulate_pool` . I can also specify the maximum number of threads to use for the pool——using the `max_workers` parameter——to prevent the memory blow-up issues associated with the naive `Thread` solution to the parallel I/O problem (i.e., one thread per cell):

分配给执行器使用的线程可以预先分配，这意味着我不必在每次执行 `simulate_pool` 时支付启动成本。我还可以指定池中用于线程的最大数量——使用 `max_workers` 参数——以防止与原生的 `Thread` 解决方案相关的内存暴涨问题（即，每个单元一个线程）：

```
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


grid = LockingGrid(5, 9)
grid.set(0, 3, ALIVE)
grid.set(1, 4, ALIVE)
grid.set(2, 2, ALIVE)
grid.set(2, 3, ALIVE)
grid.set(2, 4, ALIVE)

columns = ColumnPrinter()
with ThreadPoolExecutor(max_workers=10) as pool:
    for i in range(5):
        columns.append(str(grid))
        grid = simulate_pool(pool, grid)

print(columns)

>>>
 0 | 1 | 2 | 3 | 
---*----- | --------- | --------- | --------- | -
----*---- | --*-*---- | ----*---- | ---*----- | -
--***---- | ---**---- | --*-*---- | ----**--- | -
--------- | ---*----- | ---**---- | ---**---- | -
--------- | --------- | --------- | --------- | -
```

The best part about the `ThreadPoolExecutor` class is that it automatically propagates exceptions back to the caller when the result method is called on the `Future` instance returned by the `submit` method:

关于 `ThreadPoolExecutor` 类最好的一点是，当在由 `submit` 方法返回的 `Future` 实例上调用 `result` 方法时，它会自动将异常传播回调用者：

```
def game_logic(state, neighbors):
    raise OSError("Problem with I/O")

with ThreadPoolExecutor(max_workers=10) as pool:
    task = pool.submit(game_logic, ALIVE, 3)
    task.result()

>>>
Traceback ...
OSError: Problem with I/O
```

If I need to provide I/O parallelism for the `count_neighbors` function in addition to `game_logic` , no modifications to the program would be required since the `ThreadPoolExecutor` already runs these functions concurrently as part of `step_cell` . It’s even possible to achieve CPU parallelism by using the same interface if necessary (see Item 79: “Consider `concurrent.futures` for True Parallelism”).

如果我还需要为 `count_neighbors` 函数以及 `game_logic` 提供 I/O 并行性，则无需对程序进行任何修改，因为 `ThreadPoolExecutor` 已经作为 `step_cell` 的一部分并发运行这些函数。如果有必要，甚至可以通过使用相同的接口来实现 CPU 并行性（参见条目79：“考虑使用 `concurrent.futures` 实现真正的并行性”）。

However, the big problem that remains is the limited amount of I/O parallelism that `ThreadPoolExecutor` provides. Even if I use a `max_workers` parameter of 100, this solution still won’t scale if I need 10,000+ cells in the grid that require simultaneous I/O. `ThreadPoolExecutor` is a good choice for situations where there is no asynchronous solution (e.g., blocking file system operations), but there are better ways to maximize I/O parallelism in many cases (see Item 75: “Achieve Highly Concurrent I/O with Coroutines”).

然而，仍然存在的大问题是 `ThreadPoolExecutor` 提供的有限的 I/O 并行量。即使我将 `max_workers` 参数设置为100，此解决方案在网格中有10,000+个单元需要同时进行 I/O 操作的情况下仍然无法扩展。`ThreadPoolExecutor` 是一种在没有异步解决方案（例如，阻塞文件系统操作）情况下进行 I/O 并行的好选择，但在许多情况下还有更好的方法来最大化 I/O 并行性（参见条目75：“通过协程实现高度并发的 I/O”）。

**Things to Remember**
- `ThreadPoolExecutor` enables simple I/O parallelism with limited refactoring required.
- You can use `ThreadPoolExecutor` to avoid the cost of thread start-up each time fan-out concurrency is required.
- `ThreadPoolExecutor` makes threaded code easier to debug by automatically propagating exceptions across thread boundaries.
- Although `ThreadPoolExecutor` eliminates the potential memory blow-up issues of using threads directly, it also limits I/O parallelism by requiring `max_workers` to be specified up-front.

**注意事项**

- `ThreadPoolExecutor` 支持简单的 I/O 并行，且所需的重构较少。
- 使用 `ThreadPoolExecutor` 可以避免每次需要并发扩展时启动线程的成本。
- `ThreadPoolExecutor` 通过在线程边界之间自动传播异常使得调试多线程代码更加容易。
- 尽管 `ThreadPoolExecutor` 消除了直接使用线程时可能出现的潜在内存膨胀问题，但它要求提前指定 `max_workers`，这也限制了 I/O 并行性。