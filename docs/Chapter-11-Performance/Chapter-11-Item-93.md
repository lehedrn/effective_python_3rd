# Chapter 11: Performance  (性能)

## Item 93: Optimize Performance-Critical Code Using `timeit` Microbenchmarks (使用 `timeit` 微基准测试优化性能关键代码)

When attempting to maximize the performance of a Python program, it’s extremely important to use a profiler because the source of slowness might be non-obvious (see Item 92: “Profile Before Optimizing”). Once the real problem areas are identified, refactoring to a better architecture or using more appropriate data structures can often have a dramatic effect (see Item 103: “Know How to Use `heapq` for Priority Queues”). However, some hotspots in the code might seem inextinguishable even after many rounds of profiling and optimizing. Before attempting more complex solutions (see Item 94: “Know When and How to Replace Python with Another Programming Language”), it’s worth considering the `timeit` built-in module to run microbenchmarks.

在尝试最大化 Python 程序的性能时，使用分析器是非常重要的，因为性能瓶颈可能并不明显（参见条目92：“优化前请先进行性能分析”）。一旦确定了真正的问题区域，重构到更好的架构或使用更合适的数据结构通常会产生显著的效果（参见条目103：“知道如何使用 `heapq` 实现优先队列”）。然而，一些代码中的热点即使经过多轮性能分析和优化后也可能看似无法消除。在尝试更复杂的解决方案之前（参见条目94：“知道何时以及如何用其他编程语言替代 Python”），值得考虑使用 `timeit` 内置模块运行微基准测试。

The purpose of `timeit` is to precisely measure the performance of small snippets of code. It lets you quantify and compare multiple solutions to the same pinpointed problem. While profiling and whole-program benchmarks do help with discovering room for optimization in larger components, the number of potential improvements at such wide scope might be limitless and costly to explore. Microbenchmarks, in contrast, can be used to measure multiple implementations of the same narrowly-defined behavior, enabling you to take a scientific approach in searching for the solution that performs best.

`timeit` 的目的是精确测量小型代码片段的性能。它让你可以量化并比较多个解决方案以解决同一个具体问题。虽然性能分析和整体程序基准测试有助于发现更大组件中的优化空间，但在这种广泛范围内可能存在的潜在改进是无限的且成本高昂。相反，微基准测试可用于测量同一狭义行为的多种实现方式，使你能采取科学的方法来寻找性能最佳的解决方案。

Using the `timeit` module is simple. Here, I measure how long it takes to add two integers together:

使用 `timeit` 模块非常简单。下面我测量了将两个整数相加所需的时间：

```
import timeit
delay = timeit.timeit(stmt="1+2")
print(delay)

>>>
0.003767708025407046
```

The returned value is the number of seconds required to run 1 million iterations of the code snippet provided in the `stmt` argument. This default amount of repetition might be too much for slower microbenchmarks, so timeit lets you to specify a more appropriate count using the `number` argument.


返回值是以秒为单位运行一百万次所提供的代码片段所需的时间。这个默认的重复次数对于较慢的微基准测试来说可能太多，因此 `timeit` 允许你通过 `number` 参数指定一个更合适的次数。

```
delay = timeit.timeit(stmt="1+2", number=100)
print(delay)

>>>
7.500057108700275e-07
```

However, the 100 iterations specified above are so few that the measured microbenchmark time might start to disappear in the noise of the computer. There will always be some natural variation in performance due to other processes interfering with memory and cache status, the operating system running periodic background tasks, hardware interrupts being received, etc. For a microbenchmark to be accurate, it needs to use a large number of iterations to compensate. The `timeit` module also disables garbage collection while it executes snippets to try to reduce variance.

然而，上述指定的 100 次迭代如此之少，以至于测得的微基准时间可能会开始消失在计算机噪声中。由于其他进程干扰内存和缓存状态、操作系统运行定期后台任务、硬件中断等原因，性能总是存在一定的自然波动。为了使微基准测试准确，需要使用大量的迭代次数来补偿。`timeit` 模块在执行代码片段时还会禁用垃圾回收，以尝试减少方差。

I suggest providing the iteration count argument explicitly. I usually assign it to a variable that I use again later to calculate the average per-iteration time. This normalized value then can serve as a robust metric that can be compared to other implementations if desired, or tracked over time (e.g., to detect regressions).

我建议显式提供迭代次数参数。我通常将其赋值给一个变量，以便稍后用于计算每次迭代的平均时间。这个归一化值可以作为稳健的指标进行比较，如果需要的话，还可以随时间跟踪（例如，检测性能回归）。

```
count = 1_000_000
delay = timeit.timeit(stmt="1+2", number=count)
print(f"{delay/count*1e9:.2f} nanoseconds")

>>>
4.36 nanoseconds
```

Running a single snippet of code over and over again isn’t always sufficient to produce a useful microbenchmark. You often need to create some kind of scaffolding, harness, or data structure that can be used during iteration. `timeit`'s `setup` argument addresses this need by accepting a code snippet that runs a single time before all iterations and is excluded from the time measurement.

一遍又一遍地运行单个代码片段并不总是足以生成有用的微基准测试。你经常需要创建某种脚手架、测试框架或数据结构，以便在迭代期间使用。`timeit` 的 `setup` 参数通过接受一段代码解决了这个问题，这段代码在所有迭代之前运行一次，并且不计入时间测量。

For example, imagine that I’m trying to determine if a number is present in a large, randomized list of values. I don’t want the microbenchmark to include the time spent creating a large list and randomize it. Here, I put these upfront tasks in the `setup` snippet; I also provide the `globals` argument so `stmt` and `setup` can refer to names defined elsewhere in the code, such as the imported `random` module (see Item 91: “Avoid `exec` and `eval` Unless You’re Building a Developer Tool” for background):

例如，假设我想确定某个数字是否存在于一个大型随机列表中。我不希望微基准测试包含创建大型列表并随机排序所花费的时间。在这里，我把这些前期任务放在 `setup` 代码段中；我还提供了 `globals` 参数，这样 `stmt` 和 `setup` 可以引用代码其他地方定义的名称，比如导入的 `random` 模块（有关背景，请参见条目91：“除非在构建开发者工具，否则避免使用 `exec` 和 `eval`”）：

```
import random
count = 100_000
delay = timeit.timeit(
    setup="""
numbers = list(range(10_000))
random.shuffle(numbers)
probe = 7_777
""",
    stmt="""
probe in numbers
""",
    globals=globals(),
    number=count,
)
print(f"{delay/count*1e9:.2f} nanoseconds")

>>>
13078.05 nanoseconds
```

With this baseline (13 milliseconds) established, I can try to produce the same behavior using a different approach to see how it affects the microbenchmark. Here, I swap out the `list` created in the `setup` code snippet for a `set` data structure:


有了这个基线（13毫秒）之后，我可以尝试用不同的方法生成相同的行为，看看它如何影响微基准测试。在这里，我在 `setup` 代码段中将创建的 `list` 替换为 `set` 数据结构：

```
delay = timeit.timeit(
    setup="""
numbers = set(range(10_000))
probe = 7_777
""",
    stmt="""
probe in numbers
""",
    globals=globals(),
    number=count,
)

print(f"{delay/count*1e9:.2f} nanoseconds")

>>>
14.87 nanoseconds
```

This shows that checking for membership in a `set` is about 1,000 times faster than checking in a `list` . The reason is that the `set` data structure provides constant time access to its elements, similar to a `dict` , whereas a `list` requires time proportional to the number of elements it contains. Using `timeit` like this is a great way to find an ideal data structure or algorithm for your needs.

这表明检查 `set` 中的成员资格比检查 `list` 快约1000倍。原因是 `set` 数据结构为其元素提供恒定时间的访问，类似于 `dict`，而 `list` 需要与它所包含的元素数量成比例的时间。像这样使用 `timeit` 是找到适合你需求的数据结构或算法的好方法。

One problem that can arise in microbenchmarking like this is the need to measure the performance of tight loops, such as in mathematical kernel functions. For example, here I test the speed of summing a list of numbers:

在这种微基准测试中可能出现的一个问题是需要测量紧密循环的性能，例如数学内核函数中。例如，这里我测试了对列表中的数字求和的速度：

```
def loop_sum(items):
    total = 0
    for i in items:
        total += i
    return total

count = 1000

delay = timeit.timeit(
    setup="numbers = list(range(10_000))",
    stmt="loop_sum(numbers)",
    globals=globals(),
    number=count,
)

print(f"{delay/count*1e9:.2f} nanoseconds")

>>>
142365.46 nanoseconds
```

This measurement is how long it takes for each call to `loop_sum` , which is meaningless on its own. What you need to make this microbenchmark robust is to normalize it by the number of iterations in the inner loop, which was hard-coded to `10_000` in the example above:

这个测量结果是每次调用 `loop_sum` 所需的时间，单独来看没有意义。要使此微基准测试可靠，你需要根据内部循环中的迭代次数进行标准化，该次数在上面的例子中硬编码为 `10_000`：

```
print(f"{delay/count/10_000*1e9:.2f} nanoseconds")

>>>
14.43 nanoseconds
```

Now I can see that this function will scale in proportion to the number of items in the list by 14.43 nanoseconds per additional item.

现在我可以看到，这个函数随着列表中项目数量的增加而成比例地增加了 14.43 纳秒每增加一个项目。

The `timeit` module can also be executed as a command-line tool, which can help you rapidly investigate any curiosities you have about Python performance. For example, imagine that I want to determine the fastest way to look up a key that’s already present in a dictionary (see Item 26: “Prefer `get` Over `in` and `KeyError` to Handle Missing Dictionary Keys”). Here, I use the timeit command-line interface to test using the `in` operator for this purpose:

`timeit` 模块也可以作为命令行工具执行，这可以帮助你快速调查任何关于 Python 性能的好奇之处。例如，想象一下我想确定查找字典中已存在的键的最快方法（参见条目26：“处理缺失字典键时，首选 `get` 而不是 `in` 和 `KeyError`”）。在这里，我使用 `timeit` 命令行接口测试使用 `in` 运算符的目的：

```
$ python3 -m timeit \
--setup='my_dict = {"key": 123}' \
'if "key" in my_dict: my_dict["key"]'

20000000 loops, best of 5: 19.3 nsec per loop
```

The tool automatically determines how many iterations to run based on how much time a single iteration takes. It also runs five separate tests to compensate for system noise and presents the minimum as the best-case, lower-bound performance.

该工具会根据单次迭代所需时间自动决定运行多少次迭代。它还会运行五次独立测试以补偿系统噪音，并将最小值作为最佳情况、下限性能呈现。

I can run the tool again using a different snippet that will show how the dict.get method compares to the in operator:

我可以再次运行该工具，使用不同代码段来显示 `dict.get` 方法与 `in` 运算符相比的表现：

```
$ python3 -m timeit \
--setup='my_dict = {"key": 123}' \
'if (value := my_dict.get("key")) is not None: va
20000000 loops, best of 5: 17.1 nsec per loop
```

Now I know that `get` is faster than `in` . What about the approach of catching a known exception type, which is a common style in Python programs (see Item 32: “Prefer Raising Exceptions to Returning `None` ”)?

现在我知道 `get` 比 `in` 更快。那捕获已知异常类型的方法呢？这在 Python 程序中是一种常见风格（参见条目32：“首选引发异常而不是返回 `None`”）？

```
$ python3 -m timeit \
--setup='my_dict = {"key": 123}' \
'try: my_dict["key"]
except KeyError: pass'
20000000 loops, best of 5: 10.6 nsec per loop
```

It turns out that the `KeyError` approach is actually fastest for keys that are expected to already exist in the dictionary. This might seem surprising given all of the extra machinery required to raise and catch exceptions in the missing key case. This non-obvious performance behavior illustrates why it’s so important to test your assumptions and use profiling and microbenchmarks to measure before optimizing Python code.

事实证明，在期望键已经存在于字典中的情况下，`KeyError` 方法实际上是最快的。考虑到在缺少键的情况下需要额外的机制来引发和捕获异常，这可能看起来令人惊讶。这种非显而易见的性能表现说明了为什么在优化 Python 代码之前测试你的假设并使用性能分析和微基准测试进行测量如此重要。

**Things to Remember**

- The `timeit` built-in module can be used to run microbenchmarks that help you scientifically determine the best data structures and algorithms for performance-critical parts of programs.
- To make microbenchmarks robust, use the `setup` code snippet to exclude initialization time and be sure to normalize the returned measurements into comparable metrics.
- The `python -m timeit` command-line interface lets you quickly understand the performance of Python code snippets with little effort.

**注意事项**

- `timeit` 内建模块可用于运行微基准测试，帮助你科学地确定最适合性能关键部分的程序数据结构和算法。
- 为了使微基准测试稳健，应使用 `setup` 代码段排除初始化时间，并确保将返回的测量值归一化为可比较的指标。
- `python -m timeit` 命令行接口让你能够轻松地理解 Python 代码片段的性能。