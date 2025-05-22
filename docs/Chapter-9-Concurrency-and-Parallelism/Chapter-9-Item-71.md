# Chapter 9: Concurrency and Parallelism (并发与并行)

## Item 71:Know How to Recognize When Concurrency Is Necessary (学会识别何时需要并发处理)

Inevitably, as the scope of a program grows, it also becomes more complicated. Dealing with expanding requirements in a way that maintains clarity, testability, and efficiency is one of the most difficult parts of programming. Perhaps the hardest type of change to handle is moving from a single-threaded program to one that needs multiple concurrent lines of execution.

随着程序规模的增长，它也会变得更加复杂。以一种保持清晰、可测试性和效率的方式处理不断扩展的需求是编程中最困难的部分之一。从单线程程序过渡到需要多条并发执行线程的程序可能是最难处理的一种变化类型。

Let me demonstrate how you might encounter this problem with an example. Say that I want to implement Conway’s Game of Life, a classic illustration of finite state automata. The rules of the game are simple:  there’s a two-dimensional grid of an arbitrary size and each cell in the grid can either be alive or empty:

让我通过一个例子来演示你可能会遇到的这个问题。假设我想实现康威的生命游戏（Conway's Game of Life），这是一个有限状态自动机的经典示例。这个游戏的规则很简单：有一个任意大小的二维网格，每个格子中的细胞可以存活或空着：

```
ALIVE = "*"
EMPTY = "-"
```

The game progresses one tick of the clock at a time. Every tick, each cell counts how many of its neighboring eight cells are still alive. Based on its neighbor count, a cell decides if it will keep living, die, or regenerate—I’ll explain the specific rules further below. Here’s an example of a 5 × 5 Game of Life grid after four generations with time going to the right:

游戏每次时钟滴答推进一次。在每一次滴答中，每个细胞都会统计其周围八个相邻格子中有多少个仍然存活。根据其邻居的数量，一个细胞会决定是否继续生存、死亡或者再生 - 我将在下面进一步解释具体规则。以下是一个5 × 5生命游戏网格在四代之后的例子，时间向右推进：

```
 0    |   1   |   2   |   3   |   4
----- | ----- | ----- | ----- | -----
-*--- | --*-- | --**- | --*-- | -----
--**- | --**- | -*--- | -*--- | -**--
---*- | --**- | --**- | --*-- | -----
----- | ----- | ----- | ----- | -----
```

I can represent the state of each cell with a simple container class. The class must have methods that allow me to get and set the value of any coordinate. Coordinates that are out of bounds should wrap around, making the grid act like an infinite looping space:

我可以使用一个简单的容器类来表示每个细胞的状态。该类必须有允许我获取和设置任何坐标的值的方法。超出边界的坐标应该循环利用，使得网格表现得像一个无限循环的空间：

```
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
```

To see this class in action, I can create a `Grid` instance and set its initial state to a classic shape called a glider:

为了展示这个类的实际应用，我可以创建一个`Grid`实例，并将其初始状态设为称为滑翔机的经典形状：

```
grid = Grid(5, 9)
grid.set(0, 3, ALIVE)
grid.set(1, 4, ALIVE)
grid.set(2, 2, ALIVE)
grid.set(2, 3, ALIVE)
grid.set(2, 4, ALIVE)
print(grid)
>>>
---*-----
----*----
--***----
---------
---------
```

Now, I need a way to retrieve the status of neighboring cells. I can do this with a helper function that queries the grid for information about its surrounding environment and returns the count of living neighbors. I use a simple function for the `get_cell` parameter instead of passing in a whole `Grid` instance in order to reduce coupling (see Item 48: “Accept Functions Instead of Classes for Simple Interfaces” for more about this approach):

现在，我需要一种方法来检索邻近细胞的状态。我可以使用一个辅助函数来查询网格关于其周围环境的信息并返回活着的邻居数量。我在`get_cell`参数中使用了一个简单的函数而不是传入整个`Grid`实例，以便减少耦合（更多相关信息，请参见第48条：“对于简单接口接受函数而不是类”）：

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

Now, I define the simple logic for Conway’s Game of Life, based on the game’s three rules: Die if a cell has fewer than two neighbors, die if a cell has more than three neighbors, or become alive if an empty cell has exactly three neighbors:

现在，我定义了基于游戏三条规则的简单逻辑用于康威的生命游戏：如果一个细胞少于两个邻居则死亡，如果一个细胞多于三个邻居也死亡，或者如果一个空单元格正好有三个邻居则复活：

```
def game_logic(state, neighbors):
    if state == ALIVE:
        if neighbors < 2:
            return EMPTY     # Die: Too few
        elif neighbors > 3:
            return EMPTY     # Die: Too many
    else:
        if neighbors == 3:
            return ALIVE     # Regenerate
    return state
```

I can connect `count_neighbors` and `game_logic` together in another function that transitions the state of a cell. This function will be called each generation to figure out a cell’s current state, inspect the neighboring cells around it, determine what its next state should be, and update the resulting grid accordingly. Again, I use a function interface for `set_cell` instead of passing in the `Grid` instance to make this code more decoupled:

我可以将 `count_neighbors` 和 `game_logic` 在另一个函数中连接起来，该函数会在每一代中转换细胞的状态。此函数将在每一代中被调用，以确定细胞的当前状态，检查周围的细胞，确定其下一个状态应是什么，并相应地更新结果网格。同样，我再次使用 `set_cell` 的函数接口而不是传递 `Grid` 实例，以使代码更加解耦：

```
def step_cell(y, x, get_cell, set_cell):
    state = get_cell(y, x)
    neighbors = count_neighbors(y, x, get_cell)
    next_state = game_logic(state, neighbors)
    set_cell(y, x, next_state)
```

Finally, I can define a function that progresses the whole grid of cells forward by a single step and then returns a new grid containing the state for the next generation. The important detail here is that I need all dependent functions to call the `get_cell` method on the previous generation’s `Grid` instance, and to call the `set` method on the next generation’s `Grid` instance. This is how I ensure that all of the cells move in lockstep, which is an essential part of how the game works. This is easy to achieve because I used function interfaces for `get_cell` and `set_cell` instead of passing `Grid` instances:

最后，我可以定义一个函数，该函数将整个细胞网格向前推进一步，然后返回包含下一代状态的新网格。这里的重要细节是，我需要所有依赖的函数调用上一代 `Grid` 实例的 `get_cell` 方法，并调用下一代 `Grid` 实例的 `set` 方法。这就是我如何确保所有细胞同步前进，这是游戏运作的关键部分。这很容易实现，因为我在 `get_cell` 和 `set_cell` 上使用了函数接口而不是传递 `Grid` 实例：

```
def simulate(grid):
    next_grid = Grid(grid.height, grid.width)
    for y in range(grid.height):
        for x in range(grid.width):
            step_cell(y, x, grid.get, next_grid.set)
    return next_grid
```

Now, I can progress the grid forward one generation at a time. You can see how the glider moves down and to the right on the grid based on the simple rules from the `game_logic` function.

现在，我可以逐代逐步推进网格。你可以看到基于 `game_logic` 函数的简单规则，滑翔机是如何向下并向右移动的。

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


columns = ColumnPrinter()
for i in range(5):
    columns.append(str(grid))
    grid = simulate(grid)

print(columns)
>>>
    0     |     1     |     2     |     3     | 
---*----- | --------- | --------- | --------- | -
----*---- | --*-*---- | ----*---- | ---*----- | -
--***---- | ---**---- | --*-*---- | ----**--- | -
--------- | ---*----- | ---**---- | ---**---- | -
--------- | --------- | --------- | --------- | -
```


This works great for a program that can run in one thread on a single machine. But imagine that the program’s requirements have changed—as I alluded to above—and now I need to do some I/O (e.g., with a network socket) from within the `game_logic` function. For example, this might be required if I’m trying to build a massively multiplayer online game where the state transitions are determined by a combination of the grid state and communication with other players over the Internet.

这对于一个可以在单个机器上的单线程运行的程序来说效果很好。但想象一下，正如上面提到的，程序的要求已经改变，现在我需要在 `game_logic` 函数中进行一些I/O操作（例如，通过网络套接字）。例如，如果我要构建一个大规模多人在线游戏，其中状态转换由网格状态和通过互联网与其他玩家通信共同决定，则可能需要这样做。

How can I extend this implementation to support such functionality? The simplest thing to do is to add blocking I/O directly into the `game_logic` function:

我该如何扩展这个实现以支持这种功能？最简单的方法是在 `game_logic` 函数中直接添加阻塞I/O：

```
def game_logic(state, neighbors):
    # Do some blocking input/output in here:
    data = my_socket.recv(100)
```

The problem with this approach is that it’s going to slow down the whole program. If the latency of the I/O required is 100 milliseconds (i.e., a reasonably good cross-continent, round-trip latency on the Internet), and there are 45 cells in the grid, then each generation will take a minimum of 4.5 seconds to evaluate because each cell is processed serially in the `simulate` function. That’s far too slow and will make the game unplayable. It also scales poorly: If I later wanted to expand the grid to 10,000 cells, I would need over 15 minutes to evaluate each generation.

这种方法的问题在于它会减慢整个程序的速度。如果所需的I/O延迟是100毫秒（即，在互联网上跨大陆往返延迟的一个合理的好值），并且网格中有45个细胞，那么由于每个细胞在 `simulate` 函数中按顺序处理，每一代至少需要4.5秒来评估。这太慢了，会使游戏无法进行。而且它的扩展性很差：如果我以后想将网格扩展到10,000个细胞，评估每一代就需要超过15分钟。

The solution is to do the I/O in parallel so each generation takes roughly 100 milliseconds, regardless of how big the grid is. The process of spawning a concurrent line of execution for each unit of work——a cell in this case——is called fan-out. Waiting for all of those concurrent units of work to finish before moving on to the next phase in a coordinated process——a generation in this case——is called fan-in.

解决方案是以并行方式执行I/O，因此无论网格有多大，每一代大约需要100毫秒。为每个工作单元——在这种情况下是一个细胞——生成并发线程的过程被称为扇出（fan-out）。在协调过程中等待所有这些并发单元完成后再进入下一阶段——在这种情况下是一代——被称为扇入（fan-in）。

Python provides many built-in tools for achieving fan-out and fan-in with various trade-offs. You should understand the pros and cons of each approach, and choose the best tool for the job depending on the situation. See the following items for details: Item 72: “Avoid Creating New `Thread` Instances for On-demand Fan-out”, Item 73: “Understand How Using `Queue` for Concurrency Requires Refactoring”, Item 74: “Consider `ThreadPoolExecutor` When Threads Are Necessary for Concurrency”, Item 75: “Achieve Highly Concurrent I/O with Coroutines”).

Python提供了许多内置工具来实现各种权衡取舍的扇出和扇入。您应该了解每种方法的优缺点，并根据情况选择最适合的工作。详情请参见以下条目：第72条：“避免为按需扇出创建新的`Thread`实例”，第73条：“理解使用`Queue`进行并发需要重构”，第74条：“在线程对并发是必要的情况下考虑使用`ThreadPoolExecutor`”，第75条：“使用协程实现高度并发的I/O”。

**Things to Remember**
- As a program’s scope and complexity increases, it often starts requiring support for multiple concurrent lines of execution.
- The most common types of concurrency coordination are fan-out (generating new units of concurrency) and fan-in (waiting for existing units of concurrency to complete).
- Python has many different ways of achieving fan-out and fan-in.

**注意事项**
- 随着程序范围和复杂性的增加，它通常开始需要支持多个并发执行线程。
- 最常见的并发协调类型是扇出（生成新并发单元）和扇入（等待现有并发单元完成）。
- Python有许多不同的方式来实现扇出和扇入。