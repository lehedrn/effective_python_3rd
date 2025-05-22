# Chapter 9: Concurrency and Parallelism (并发与并行)

## Item 75: Achieve Highly Concurrent I/O with Coroutines (通过协程实现高并发的I/O)

The previous items have tried to solve the parallel I/O problem for the Game of Life example with varying degrees of success (see Item 71: “Know How to Recognize When Concurrency Is Necessary” for background and the implementations of various functions and classes below). All of the other approaches fall short in their ability to handle
thousands of simultaneously concurrent functions (see Item 72: “Avoid Creating New `Thread` Instances for On-demand Fan-out”, Item 73: “Understand How Using `Queue` for Concurrency Requires Refactoring”, and Item 74: “Consider `ThreadPoolExecutor` When Threads Are Necessary for Concurrency”).

前面的条目尝试使用不同的成功程度解决生命游戏示例中的并行I/O问题（参见条目71：“知道何时需要识别并发是必要的”以了解背景和以下各种函数和类的实现）。所有其他方法在处理同时并发运行的数千个函数时都显得不足（参见条目72：“避免为按需扇出创建新的`Thread`实例”，条目73：“理解使用`Queue`进行并发需要重构”，以及条目74：“在线程对于并发是必要时考虑`ThreadPoolExecutor`”）。

Python addresses the need for highly concurrent I/O with coroutines. Coroutines let you have a very large number of seemingly simultaneously executing functions in your Python programs. They’re implemented using the `async` and `await` keywords along with the same infrastructure that powers generators (see Item 43: “Consider Generators Instead of Returning Lists”, Item 46: “Pass Iterators into Generators as Arguments Instead of Calling the `send` Method”, and Item 47: “Manage Iterative State Transitions with a Class Instead of the Generator `throw` Method”).

Python通过协程解决了高并发I/O的需求。协程让你在Python程序中拥有大量看似同时执行的函数。它们是使用`async`和`await`关键字以及支持生成器的相同基础设施来实现的（参见条目43：“考虑用生成器代替返回列表”，条目46：“将迭代器作为参数传递给生成器而不是调用`send`方法”，以及条目47：“使用类管理迭代状态转换而不是生成器的`throw`方法”）。

The cost of starting a coroutine is a function call. Once a coroutine is active, it uses less than 1 KB of memory until it’s exhausted. Like threads, coroutines are independent functions that can consume inputs from their environment and produce resulting outputs. The difference is that coroutines pause at each `await` expression and resume executing an `async` function after the pending awaitable is resolved (similar to how `yield` behaves in generators).

启动一个协程的成本是一个函数调用。一旦协程激活，它使用的内存不到1 KB，直到它耗尽为止。像线程一样，协程是独立的函数，可以从环境中消费输入并产生输出。区别在于协程在每个`await`表达式处暂停，并在待处理的等待对象解析后恢复执行`async`函数（类似于`yield`在生成器中的行为）。

When many separate `async` functions are advanced in lockstep, they all seem to be running simultaneously, mimicking the concurrent behavior of Python threads. However, coroutines do this without the memory overhead, start-up and context switching costs, or complex locking and synchronization code that’s required for threads. The magical mechanism powering coroutines is the event loop, which can do highly concurrent I/O efficiently, while rapidly interleaving execution between appropriately-written functions.

当许多单独的`async`函数同步推进时，它们似乎都在同时运行，模仿了Python线程的并发行为。然而，协程这样做不需要线程所需的内存开销、启动和上下文切换成本或复杂的锁定和同步代码。驱动协程的神奇机制是事件循环，它可以高效地进行高并发I/O，同时在适当编写的函数之间快速交错执行。

I can use coroutines to implement the Game of Life. My goal is to allow for I/O to occur within the `game_logic` function, while overcoming the problems from the `Thread` , `Queue` , and `ThreadPoolExecutor` approaches in the previous items. To do this, first I indicate that the `game_logic` function is a coroutine by defining it using async def instead of `def` . This will allow me to use the `await` syntax for I/O, such as an asynchronous `read` from a socket:

我可以使用协程来实现生命游戏。我的目标是在`game_logic`函数内允许发生I/O，同时克服之前条目中提到的`Thread`、`Queue`和`ThreadPoolExecutor`方法的问题。为此，首先我通过使用`async def`而不是`def`定义`game_logic`函数来表明它是一个协程。这将允许我在I/O中使用`await`语法，例如从套接字异步读取：

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

async def game_logic(state, neighbors):
    # Do some input/output in here:
    data = await my_socket.read(50)


async def game_logic(state, neighbors):
    if state == ALIVE:
        if neighbors < 2:
            return EMPTY
        elif neighbors > 3:
            return EMPTY
    else:
        if neighbors == 3:
            return ALIVE
    return state
```

Similarly, I can turn `step_cell` into a coroutine by adding `async` to its definition and using `await` for the call to the `game_logic` function:

同样，我可以通过在其定义中添加`async`并在对`game_logic`函数的调用中使用`await`将`step_cell`转换为协程：

```
async def step_cell(y, x, get_cell, set_cell):
    state = get_cell(y, x)
    neighbors = count_neighbors(y, x, get_cell)
    next_state = await game_logic(state, neighbors)
    set_cell(y, x, next_state)
```

The `simulate` function also needs to become a coroutine:

`simulate` 函数也需要成为协程：

```
import asyncio

async def simulate(grid):
    next_grid = Grid(grid.height, grid.width)

    tasks = []
    for y in range(grid.height):
        for x in range(grid.width):
            task = step_cell(y, x, grid.get, next_grid.set)  # Fan-out
            tasks.append(task)

    await asyncio.gather(*tasks)                             # Fan-in

    return next_grid

```

The coroutine version of the `simulate` function requires some explanation:

`simulate` 函数的协程版本需要一些解释：

- Calling `step_cell` doesn’t immediately run that function. Instead, it returns a `coroutine` instance that can be used with an `await` expression at a later time. This is similar to how generator functions that use `yield` return a generator instance when they’re called instead of executing immediately. Deferring execution like this is the mechanism that causes fan-out.
- The `gather` function from the `asyncio` built-in library is what causes fan-in. The await expression on gather instructs the event loop to run the `step_cell` coroutines concurrently and resume execution of the `simulate` coroutine when all of them have been completed (see Item 77: “Mix Threads and Coroutines to Ease the Transition to `asyncio` ” for another approach using `asyncio.TaskGroup` ).
- No locks are required for the `Grid` instance since all execution occurs within a single thread. The I/O becomes parallelized as part of the event loop that’s provided by `asyncio` .

- 调用 `step_cell` 不会立即运行该函数。相反，它返回一个 `coroutine` 实例，可以在稍后的 `await` 表达式中使用。这类似于使用 `yield` 的生成器函数在被调用时返回一个生成器实例而不是立即执行。这种延迟执行机制是导致扇出的原因。
- `asyncio` 内置库中的 `gather` 函数会导致扇入。`gather` 上的 `await` 表达式指示事件循环并发运行 `step_cell` 协程，并在它们全部完成后恢复执行 `simulate` 协程（另请参见条目77：“混合线程和协程以简化向 `asyncio` 的过渡”中使用 `asyncio.TaskGroup` 的另一种方法）。
- 不需要 `Grid` 实例的锁，因为所有执行都在单个线程中进行。I/O 成为了由 `asyncio` 提供的事件循环的一部分，并行化。

Finally, I can drive this code with a one-line change to the original example. This relies on the `asyncio.run` function to execute the `simulate` coroutine in an event loop and carry out its dependent I/O:

最后，我可以通过对原始示例的一行更改来驱动这段代码。这依赖于 `asyncio.run` 函数在事件循环中执行 `simulate` 协程并执行其相关的 I/O：

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


logging.getLogger().setLevel(logging.ERROR)

grid = Grid(5, 9)
grid.set(0, 3, ALIVE)
grid.set(1, 4, ALIVE)
grid.set(2, 2, ALIVE)
grid.set(2, 3, ALIVE)
grid.set(2, 4, ALIVE)

columns = ColumnPrinter()
for i in range(5):
    columns.append(str(grid))
    grid = asyncio.run(simulate(grid))  # Run the event loop

print(columns)

>>>
 0 | 1 | 2 | 3 | 
---*----- | --------- | --------- | --------- | -
----*---- | --*-*---- | ----*---- | ---*----- | -
--***---- | ---**---- | --*-*---- | ----**--- | -
--------- | ---*----- | ---**---- | ---**---- | -
--------- | --------- | --------- | --------- | -
```

The result is the same as before. All of the overhead associated with threads has been eliminated. Whereas the `Queue` and `ThreadPoolExecutor` approaches are limited in their exception handling—merely re-raising exceptions across thread boundaries—with coroutines I can even use the interactive debugger to step through the exception handling code line by line (see Item 115: “Consider Interactive Debugging with pdb ”).

结果是一样的。与线程相关的所有开销都被消除了。而 `Queue` 和 `ThreadPoolExecutor` 方法在异常处理方面受到限制——仅仅是在跨线程边界重新抛出异常，使用协程甚至可以使用交互式调试器逐行调试异常处理代码（参见条目115：“考虑使用 pdb 进行交互式调试”）。

Later, if my requirements change and I also need to do I/O from within `count_neighbors` , I can easily accomplish this by adding `async` and `await` keywords to the existing functions and call sites instead of having to restructure everything as I would have had to do if I were using `Thread` or `Queue` instances (see Item 76: “Know How to Port Threaded I/O to `asyncio` ” for another example):

以后，如果我的需求发生变化，并且我也需要在 `count_neighbors` 中进行 I/O，我可以通过在现有函数和调用点上添加 `async` 和 `await` 关键字轻松完成这一点，而不必像使用 `Thread` 或 `Queue` 实例时那样必须重构一切（参见条目76：“知道如何将线程 I/O 移植到 `asyncio`”以获取另一个示例）：

```
async def count_neighbors(y, x, get_cell):
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

async def step_cell(y, x, get_cell, set_cell):
    state = get_cell(y, x)
    neighbors = await count_neighbors(y, x, get_cell)
    next_state = await game_logic(state, neighbors)
    set_cell(y, x, next_state)

async def game_logic(state, neighbors):
    if state == ALIVE:
        if neighbors < 2:
            return EMPTY
        elif neighbors > 3:
            return EMPTY
    else:
        if neighbors == 3:
            return ALIVE
    return state

logging.getLogger().setLevel(logging.ERROR)

grid = Grid(5, 9)
grid.set(0, 3, ALIVE)
grid.set(1, 4, ALIVE)
grid.set(2, 2, ALIVE)
grid.set(2, 3, ALIVE)
grid.set(2, 4, ALIVE)

columns = ColumnPrinter()
for i in range(5):
    columns.append(str(grid))
    grid = asyncio.run(simulate(grid))

print(columns)

>>>
 0 | 1 | 2 | 3 | 
---*----- | --------- | --------- | --------- | -
----*---- | --*-*---- | ----*---- | ---*----- | -
--***---- | ---**---- | --*-*---- | ----**--- | -
--------- | ---*----- | ---**---- | ---**---- | -
--------- | --------- | --------- | --------- | -
```


The beauty of coroutines is that they decouple your code’s instructions for the external environment (i.e., I/O) from the implementation that carries out your wishes (i.e., the event loop). They let you focus on the logic of what you’re actually trying to do, instead of wasting time trying to figure out how you’re going to accomplish your goals concurrently.

协程的美妙之处在于，它们将你的代码对外部环境（即I/O）的指令与其执行这些愿望的实现解耦（即事件循环）。它们让你专注于实际要做的事情的逻辑，而不是浪费时间试图弄清楚如何并发地完成目标。

**Things to Remember**

- Functions that are defined using the `async` keyword are called coroutines. A caller can receive the result of a dependent coroutine by using the `await` keyword.
- Coroutines provide an efficient way to run tens of thousands of functions seemingly at the same time.
- Coroutines can use fan-out and fan-in in order to parallelize I/O, while also overcoming all of the problems associated with doing I/O in threads.

**注意事项**

- 使用`async`关键字定义的函数称为协程。调用者可以使用`await`关键字接收依赖协程的结果。
- 协程提供了一种有效的方法来同时运行数万个函数。
- 协程可以使用扇出和扇入来并行化I/O，同时克服在线程中进行I/O的所有相关问题。