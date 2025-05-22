# Chapter 9: Concurrency and Parallelism (第9章：并发与并行)

## Item 73: Understand How Using `Queue` for Concurrency Requires Refactoring (条目73：理解使用 `Queue` 进行并发需要重构代码)

In the previous item (see Item 72: “Avoid Creating New `Thread` Instances for On-demand Fan-out”) I covered the downsides of using `Thread` to solve the parallel I/O problem in the Game of Life example from earlier (see Item 71: “Know How to Recognize When Concurrency Is Necessary” for background and the implementations of various functions and classes below).

在上一条（见条目72：“避免为按需扇出创建新的 `Thread` 实例”）中，我讨论了使用 `Thread` 解决之前“生命游戏”示例中的并行 I/O 问题的缺点（参见条目71：“了解何时意识到并发是必要的”，以获取背景信息和下面各种函数和类的实现）。

The next approach to try is implementing a threaded pipeline using the `Queue` class from the `queue` built-in module (see Item 70: “Use `Queue` to Coordinate Work Between Threads” for background; I rely on the implementation of `StoppableWorker` from that item in the example code below).

下一个尝试的方法是使用 `queue` 内置模块中的 `Queue` 类来实现线程化流水线（参见条目70：“使用 `Queue` 协调线程间工作”了解背景；我在下面的示例代码中依赖该条目中 `StoppableWorker` 的实现）。

Here’s the general approach: Instead of creating one thread per cell per generation of the Game of Life, I can create a fixed number of worker threads upfront and have them do parallelized I/O as needed. This will keep my resource usage under control and eliminate the overhead of frequently starting new threads.

这里是一般的方法：不是为“生命游戏”的每个单元格每代创建一个线程，而是预先创建固定数量的工作线程，并让它们根据需要执行并行 I/O。这将控制我的资源使用，并消除频繁启动新线程的开销。

To do this, I need two `Queue` instances to use for communicating to and from the worker threads that execute the `game_logic` function:

为了做到这一点，我需要两个 `Queue` 实例，用于与执行 `game_logic` 函数的工作线程通信：

```
from queue import Queue
in_queue = Queue()
out_queue = Queue()
```

I can start multiple threads that will consume items from the `in_queue` , process them by calling `game_logic` , and put the results on `out_queue` . These threads will run concurrently, allowing for parallel I/O and reduced latency for each generation:

我可以启动多个线程，这些线程会从 `in_queue` 中消费项目，在调用 `game_logic` 后处理它们，并将结果放在 `out_queue` 上。这些线程将并发运行，允许并行 I/O 并减少每代的延迟：

```
from threading import Thread

from queue import ShutDown


class StoppableWorker(Thread):
    def __init__(self, func, in_queue, out_queue, *args, **kwargs):
        super().__init__(*args, **kwargs)
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

def game_logic_thread(item):
    y, x, state, neighbors = item
    try:
        next_state = game_logic(state, neighbors)
    except Exception as e:
        next_state = e
    return (y, x, next_state)

# Start the threads upfront
threads = []
for _ in range(5):
    thread = StoppableWorker(game_logic_thread, in_queue, out_queue)
    thread.start()
    threads.append(thread)
```

Now, I can redefine the `simulate` function to interact with these queues to request state transition decisions and receive corresponding responses. Adding items to the `in_queue` is what causes fan-out, and consuming items from the `out_queue` until it’s empty is what causes fan-in:

现在，我可以重新定义 `simulate` 函数，以与这些队列交互，请求状态转换决策并接收相应的响应。向 `in_queue` 添加项目会引起扇出，而从 `out_queue` 消费项目直到为空会引起扇入：

```
ALIVE = "*"
EMPTY = "-"

class SimulationError(Exception):
    pass

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

def simulate_pipeline(grid, in_queue, out_queue):
    for y in range(grid.height):
        for x in range(grid.width):
            state = grid.get(y, x)
            neighbors = count_neighbors(y, x, grid.get)
            in_queue.put((y, x, state, neighbors))  # Fan-out

    in_queue.join()
    item_count = out_queue.qsize()

    next_grid = Grid(grid.height, grid.width)
    for _ in range(item_count):
        item = out_queue.get()                      # Fan-in
        y, x, next_state = item
        if isinstance(next_state, Exception):
            raise SimulationError(y, x) from next_state
        next_grid.set(y, x, next_state)

    return next_grid
```

The calls to `Grid.get` and `Grid.set` both happen within this new `simulate_pipeline` function, which means that I can use the single-threaded implementation of `Grid` instead of the implementation that requires `Lock` instances for synchronization (see Item 69: “Use `Lock` to Prevent Data Races in Threads” for background).

对 `Grid.get` 和 `Grid.set` 的调用都发生在这个新的 `simulate_pipeline` 函数中，这意味着我可以使用单线程实现的 `Grid`，而不是需要使用 `Lock` 实例进行同步的实现（参见条目69：“使用 `Lock` 防止线程中的数据竞争”了解背景）。

This code is also easier to debug than the `Thread` approach used in the previous item. If an exception occurs while doing I/O in the `game_logic` function, it will be caught by the surrounding `game_logic_thread` function, propagated to the `out_queue` , and then re-raised in the main thread:

这段代码也比前一条中使用的 `Thread` 方法更容易调试。如果在 `game_logic` 函数中进行 I/O 时发生异常，它将被周围的 `game_logic_thread` 函数捕获，传播到 `out_queue`，然后在主线程中再次引发：

```
def game_logic(state, neighbors):
    raise OSError("Problem with I/O in game_logic")

simulate_pipeline(Grid(1, 1), in_queue, out_queue)

>>>
Traceback ...
OSError: Problem with I/O in game_logic
The above exception was the direct cause of the f
exception:
Traceback ...
SimulationError: (0, 0)
```

I can drive this multi-threaded pipeline for repeated generations by calling `simulate_pipeline` in a loop.

我可以通过在循环中调用 `simulate_pipeline` 来驱动这个多线程流水线以生成重复的世代。

```
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


grid = Grid(5, 9)
grid.set(0, 3, ALIVE)
grid.set(1, 4, ALIVE)
grid.set(2, 2, ALIVE)
grid.set(2, 3, ALIVE)
grid.set(2, 4, ALIVE)

columns = ColumnPrinter()
for i in range(5):
    columns.append(str(grid))
    grid = simulate_pipeline(grid, in_queue, out_queue)

print(columns)

in_queue.shutdown()
in_queue.join()

for thread in threads:
    thread.join()

>>>
 0 | 1 | 2 | 3 | 
---*----- | --------- | --------- | --------- | -
----*---- | --*-*---- | ----*---- | ---*----- | -
--***---- | ---**---- | --*-*---- | ----**--- | -
--------- | ---*----- | ---**---- | ---**---- | -
--------- | --------- | --------- | --------- | -
```


The results are the same as before. Although I’ve addressed the memory explosion problem, start-up costs, and debugging issues of using threads on their own, many issues remain:

结果与之前相同。尽管我已经解决了单独使用线程时的内存爆炸问题、启动成本和调试问题，但许多问题依然存在：

- The `simulate_pipeline` function is even harder to follow than the `simulate_threaded` approach from the previous item.
- Extra support functionality was required (e.g., `StoppableWorker` ) in order to make the code easier to read, at the expense of increased complexity.
- I have to specify the amount of potential parallelism—the number of threads running `game_logic_thread`——up-front based on my expectations of the workload, instead of having the system automatically scale up parallelism as needed.
- In order to enable debugging, I have to manually catch exceptions in worker threads, propagate them on a `Queue` , and then re-raise them in the main thread.

- `simulate_pipeline` 函数甚至比上一条中提到的 `simulate_threaded` 方法更难理解。
- 为了使代码更易于阅读，需要额外的支持功能（例如 `StoppableWorker`），但这增加了复杂性。
- 我必须根据对工作负载的预期提前指定潜在并行性的数量——即运行 `game_logic_thread` 的线程数，而不是让系统根据需要自动扩展并行性。
- 为了启用调试，我必须手动在线程中捕获异常，通过 `Queue` 传播它们，然后在主线程中重新抛出它们。

However, the biggest problem with this code is apparent if the requirements change again. Imagine that later I needed to do I/O within the `count_neighbors` function in addition to the I/O that was needed within `game_logic` :

然而，这段代码最大的问题在于需求再次变化时变得明显。假设之后我需要在 `count_neighbors` 函数中进行 I/O，除了 `game_logic` 中所需的 I/O 之外：

```
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
```

In order to make this parallelizable, I need to add another stage to the pipeline that runs `count_neighbors` in a thread. I need to make sure that exceptions propagate correctly between the worker threads and the main thread. And I need to use a `Lock` for the `Grid` class in order to ensure safe synchronization between the worker threads (see for background and Item 72: “Avoid Creating New Thread Instances for On￾demand Fan-out” for the implementation of `LockingGrid` ):

为了使其可以并行化，我需要在管道中添加另一个阶段，该阶段在线程中运行 `count_neighbors`。我需要确保异常在线程和主线程之间正确传播。并且我需要使用 `Lock` 对 `Grid` 类进行锁定，以确保线程之间的安全同步（参见相关背景知识以及条目72：“避免为按需扇出创建新的线程实例”中 `LockingGrid` 的实现）：

```
def count_neighbors_thread(item):
    y, x, state, get_cell = item
    try:
        neighbors = count_neighbors(y, x, get_cell)
    except Exception as e:
        neighbors = e
    return (y, x, state, neighbors)

def game_logic_thread(item):
    y, x, state, neighbors = item
    if isinstance(neighbors, Exception):
        next_state = neighbors
    else:
        try:
            next_state = game_logic(state, neighbors)
        except Exception as e:
            next_state = e
    return (y, x, next_state)

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
```

I have to create another set of `Queue` instances for the `count_neighbors_thread` workers, and the corresponding `Thread` instances:

我需要为 `count_neighbors_thread` 工作线程创建另一组 `Queue` 实例，以及相应的 `Thread` 实例：

```
in_queue = Queue()
logic_queue = Queue()
out_queue = Queue()

threads = []

for _ in range(5):
    thread = StoppableWorker(
        count_neighbors_thread, in_queue, logic_queue
    )
    thread.start()
    threads.append(thread)

for _ in range(5):
    thread = StoppableWorker(
        game_logic_thread, logic_queue, out_queue
    )
    thread.start()
    threads.append(thread)
```

Finally, I need to update `simulate_pipeline` to coordinate the multiple phases in the pipeline and ensure that work fans-out and back in correctly:

最后，我需要更新 `simulate_pipeline` 以协调管道中的多个阶段，并确保工作正确地扇出和扇回：

```
def simulate_phased_pipeline(grid, in_queue, logic_queue, out_queue):
    for y in range(grid.height):
        for x in range(grid.width):
            state = grid.get(y, x)
            item = (y, x, state, grid.get)
            in_queue.put(item)              # Fan-out

    in_queue.join()
    logic_queue.join()                      # Pipeline sequencing
    item_count = out_queue.qsize()

    next_grid = LockingGrid(grid.height, grid.width)
    for _ in range(item_count):
        y, x, next_state = out_queue.get()  # Fan-in
        if isinstance(next_state, Exception):
            raise SimulationError(y, x) from next_state
        next_grid.set(y, x, next_state)

    return next_grid
```

With these updated implementations, now I can run the multi-phase pipeline end-to-end:

有了这些更新的实现，现在我可以端到端地运行多阶段管道：

```
grid = LockingGrid(5, 9)
grid.set(0, 3, ALIVE)
grid.set(1, 4, ALIVE)
grid.set(2, 2, ALIVE)
grid.set(2, 3, ALIVE)
grid.set(2, 4, ALIVE)

columns = ColumnPrinter()
for i in range(5):
    columns.append(str(grid))
    grid = simulate_phased_pipeline(
        grid, in_queue, logic_queue, out_queue
    )

print(columns)

in_queue.shutdown()
in_queue.join()

logic_queue.shutdown()
logic_queue.join()

for thread in threads:
    thread.join()

>>>
 0 | 1 | 2 | 3 | 
---*----- | --------- | --------- | --------- | -
----*---- | --*-*---- | ----*---- | ---*----- | -
--***---- | ---**---- | --*-*---- | ----**--- | -
--------- | ---*----- | ---**---- | ---**---- | -
--------- | --------- | --------- | --------- | -
```


Again, this works as expected, but it required a lot of changes and boilerplate. The point here is that `Queue` does make it possible to solve fan-out and fan-in problems, but the complexity is very high. Although using `Queue` is a better approach than using `Thread` instances on their own, it’s still not nearly as good as some of the other tools provided by Python (see Item 74: “Consider `ThreadPoolExecutor` When Threads Are Necessary for Concurrency” and Item 75: “Achieve Highly Concurrent I/O with Coroutines”).

同样，这样也能如预期般工作，但它需要大量的修改和样板代码。此处的重点是，虽然 `Queue` 确实使得解决扇出和扇入问题成为可能，但其复杂性非常高。虽然使用 `Queue` 比单独使用 `Thread` 实例是一个更好的方法，但它仍然不如 Python 提供的一些其他工具（参见条目74：“当线程对于并发是必要时考虑 `ThreadPoolExecutor`”和条目75：“使用协程实现高度并发的 I/O”）。

**Things to Remember**
- Using `Queue` instances with a fixed number of worker threads improves the scalability of fan-out and fan-in using threads.
- It takes a significant amount of work to refactor existing code to use `Queue` , especially when multiple stages of a pipeline are required.
- Using `Queue` with a fixed number of worker threads fundamentally limits the total amount of I/O parallelism a program can leverage compared to alternative approaches provided by other built-in Python features and modules that are more dynamic.

**注意事项**
- 使用 `Queue` 实例配合固定数量的工作线程可以改善使用线程的扇出和扇入的可扩展性。
- 将现有代码重构为使用 `Queue` 需要大量工作，尤其是在需要管道的多个阶段时。
- 使用具有固定数量工作线程的 `Queue` 根本性地限制了程序可以利用的 I/O 并行总量，相较于其他由 Python 内建特性和模块提供的更具动态性的方法。