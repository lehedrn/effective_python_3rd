# Chapter 9: Concurrency and Parallelism (并发与并行)

## Item 72: Avoid Creating New `Thread` Instances for On-demand Fan-out (避免为按需扩展创建新的 `Thread` 实例)

Threads are the natural first tool to reach for in order to do parallel I/O in Python (see Item 68: “Use Threads for Blocking I/O, Avoid for Parallelism”). However, they have significant downsides when you try to use them for fanning out to many concurrent lines of execution.

线程通常是执行并行I/O操作的首选工具（参见条目68：“对阻塞式I/O使用线程，避免用于并行处理”）。然而，当你试图用它们来扩展到许多并发执行线路时，它们有显著的缺点。

To demonstrate this, I’ll continue with the Game of Life example from before (see Item 71: “Know How to Recognize When Concurrency Is Necessary” for background and the implementations of various functions and classes below). I’ll use threads to solve the latency problem caused by doing I/O in the `game_logic` function. To begin, threads will require coordination using locks to ensure that assumptions within data structures are maintained properly (see Item 69: “Use `Lock` to Prevent Data Races in Threads” for details). I can create a subclass of the `Grid` class that adds locking behavior so an instance can be used by multiple threads simultaneously:

为了说明这一点，我将继续使用前面的“生命游戏”示例（参见条目71：“知道如何识别何时需要并发”，以了解背景和下面各种函数和类的实现）。我将使用线程来解决在 `game_logic` 函数中进行I/O引起的延迟问题。首先，线程需要使用锁来进行协调，以确保数据结构内的假设得到正确维护（参见条目69：“使用 `Lock` 防止线程中的数据竞争”了解更多详情）。我可以创建一个添加了锁定行为的 `Grid` 类的子类，以便实例可以同时被多个线程使用：

```
from threading import Lock

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

Then, I can reimplement the `simulate` function to fan-out by creating a thread for each call to `step_cell` . The threads will run in parallel and won’t have to wait on each other’s I/O. I can then fan-in by waiting for all of the threads to complete before moving on to the next generation:

然后，我可以重新实现 `simulate` 函数，通过为每个调用 `step_cell` 创建一个线程来进行扩展。这些线程将并行运行，而不会互相等待I/O。然后，我可以通过等待所有线程完成后再进入下一代来实现聚合：

```
from threading import Thread

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
    # This version of the function is just to illustrate the point
    # that I/O is possible, but for example code we'll simply run
    # the normal game logic (below) so it's easier to understand.
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

def simulate_threaded(grid):
    next_grid = LockingGrid(grid.height, grid.width)
    threads = []
    for y in range(grid.height):
        for x in range(grid.width):
            args = (y, x, grid.get, next_grid.set)
            thread = Thread(target=step_cell, args=args)
            thread.start()  # Fan-out
            threads.append(thread)
    for thread in threads:
        thread.join()  # Fan-in
    return next_grid
```

I can run this code using the same implementation of `step_cell` , and the same driving code as before with only two lines changed to use the `LockingGrid` and `simulate_threaded` implementations:

我可以使用相同实现的 `step_cell` 和相同的驱动代码运行此代码，只需更改两行代码以使用 `LockingGrid` 和 `simulate_threaded` 的实现：

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


grid = LockingGrid(5, 9)  # Changed
grid.set(0, 3, ALIVE)
grid.set(1, 4, ALIVE)
grid.set(2, 2, ALIVE)
grid.set(2, 3, ALIVE)
grid.set(2, 4, ALIVE)

columns = ColumnPrinter()
for i in range(5):
    columns.append(str(grid))
    grid = simulate_threaded(grid)  # Changed

print(columns)
>>>
    0     |     1     |     2     |     3     |     4
---*----- | --------- | --------- | --------- | ---------
----*---- | --*-*---- | ----*---- | ---*----- | ----*----
--***---- | ---**---- | --*-*---- | ----**--- | -----*---
--------- | ---*----- | ---**---- | ---**---- | ---***---
--------- | --------- | --------- | --------- | ---------
```

This works as expected and the I/O is now parallelized between the threads. However, this code has three big problems:

这正如预期那样工作，并且现在I/O在各个线程之间并行化了。但是，这段代码有三个大问题：

- The `Thread` instances require special tools (i.e., `Lock` objects) to coordinate with each other safely. This makes the code that uses threads harder to reason about in comparison to the procedural, single-threaded code from before. This complexity makes threaded code more difficult to extend and maintain over time.
- Threads require a lot of memory, about 8 MB per executing thread. On many computers, that amount of memory doesn’t matter for the 45 threads I’d need in this example. But if the game grid had to grow to 10,000 cells, I would need to create that many threads, which is so much memory (80GB) that the program won’t fit on my machine. Although some operating systems play tricks to delay a thread’s full memory allocation until its execution stack is sufficiently deep, there’s still a risk that running one thread per concurrent activity won’t work reliably.
- Starting a thread is costly, and threads have a negative performance impact when they run due to the overhead of context switching between them. In the code above, all of the threads are started and stopped each generation of the game, which has so much overhead it will increase latency beyond the expected I/O time of 100 milliseconds.


- `Thread` 实例需要特殊的工具（例如 `Lock` 对象）来安全地相互协调。这使得使用线程的代码比之前的程序性单线程代码更难理解。这种复杂性使得随着时间推移，线程代码更难以扩展和维护。
- 线程需要大量的内存，大约每个执行线程需要8MB。在许多计算机上，这个数量的内存对于本例中所需的45个线程来说并不重要。但如果游戏网格必须增长到10,000个单元格，则需要创建那么多线程，这是如此多的内存（80GB），以至于程序无法在我的机器上运行。尽管某些操作系统会采用技巧来延迟线程的完整内存分配，直到其执行栈足够深，但由于运行一个线程对应一个并发活动的风险仍然存在。
- 启动一个线程是昂贵的，并且由于上下文切换的开销，线程运行时会有负面性能影响。在上面的代码中，所有线程都在游戏的每一代中启动和停止，这会导致很大的开销，从而增加延迟超过预期的I/O时间100毫秒。

This code would also be very difficult to debug if something went wrong. For example, imagine that the `game_logic` function raises an exception, which is highly likely due to the generally flaky nature of I/O:

如果出现问题，这段代码也很难调试。例如，想象一下 `game_logic` 函数抛出异常的情况，由于I/O通常不稳定，这种情况非常可能发生：

```
def game_logic(state, neighbors):
    raise OSError("Problem with I/O")
```

I can test what this would do by running a `Thread` instance pointed at this function and redirecting the `sys.stderr` output from the program to an in-memory `StringIO` buffer:

我可以通过运行指向此函数的 `Thread` 实例并将程序的 `sys.stderr` 输出重定向到内存中的 `StringIO` 缓冲区来测试会发生什么：

```
import contextlib
import io

fake_stderr = io.StringIO()
with contextlib.redirect_stderr(fake_stderr):
    thread = Thread(target=game_logic, args=(ALIVE, 3))
    thread.start()
    thread.join()

print(fake_stderr.getvalue())

>>>
Exception in thread Thread-226 (game_logic):
Traceback (most recent call last):
  File "threading.py", line 1073, in _bootstrap_inner
    self.run()
  File "threading.py", line 1010, in run
    self._target(*self._args, **self._kwargs)
  File "<stdin>", line 2, in game_logic
OSError: Problem with I/O
```

An `OSError` exception is expected, but somehow the code that created the `Thread` and called `join` on it is unaffected. How can this be? The reason is that the `Thread` class will independently catch any exceptions that are raised by the `target` function and then write their traceback to `sys.stderr` . Such exceptions are never re-raised to the caller that started the thread in the first place.

一个 `OSError` 异常是可以预料的，但奇怪的是，创建 `Thread` 并调用其 `join` 的代码不受影响。怎么会这样呢？原因在于 `Thread` 类会独立捕获由 `target` 函数引发的任何异常，然后将其跟踪信息写入 `sys.stderr` 。这样的异常永远不会在启动线程的代码或等待它完成的单独线程中重新引发。

Given all of these issues, it’s clear that threads are not the solution if you need to constantly create and finish new concurrent functions. Python provides other solutions that are a better fit (see Item 73: “Understand How Using Queue for Concurrency Requires Refactoring”, Item 74: “Consider ThreadPoolExecutor When Threads Are Necessary for Concurrency”, Item 75: “Achieve Highly Concurrent I/O with Coroutines”).

鉴于所有这些问题，很明显，如果你需要不断创建和完成新的并发函数，线程并不是解决方案。Python提供了其他更适合的解决方案（参见条目73：“了解使用Queue进行并发需要重构”，条目74：“在线程对于并发是必要的情况下考虑使用ThreadPoolExecutor”，条目75：“使用协程实现高度并发的I/O”）。

**Things to Remember**

- Threads have many downsides: They’re costly to start and run if you need a lot of them, they each require a significant amount of memory, and they require special tools like `Lock` instances for coordination.
- A `Thread` doesn’t have a built-in way to raise exceptions back in the code that started it or in a separate thread that is waiting for it to finish, which greatly hampers debugging.

**注意事项**

- 线程有许多缺点：如果你需要大量线程，它们的启动和运行成本都很高，每个线程都需要相当大的内存，并且它们需要像 `Lock` 实例这样的特殊工具来进行协调。
- `Thread` 没有内置的方法将目标函数中引发的异常重新在启动它的代码中或者在一个等待它完成的单独线程中抛出，这大大妨碍了调试。