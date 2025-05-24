# Chapter 11: Performance (性能)

## Item 92: Profile Before Optimizing (优化之前先进行性能分析)

The dynamic nature of Python causes surprising behaviors in its runtime performance. Operations you might assume would be slow are actually very fast (e.g., string manipulation, generators). Language features you might assume would be fast are actually very slow (e.g., attribute accesses, function calls). The true source of slowdowns in a Python program can be obscure.

Python的动态特性导致其运行性能出现令人惊讶的行为。你可能认为会很慢的操作实际上非常快（例如，字符串操作、生成器）。而你可能认为很快的语言特性实际上却很慢（例如，属性访问、函数调用）。Python程序中的真正性能瓶颈可能是模糊不清的。

The best approach is to ignore your intuition and directly measure the performance of a program before you try to optimize it. Python provides a built-in profiler for determining which parts of a program are responsible for its execution time. Profiling enables you to focus your optimization efforts on the biggest sources of trouble and ignore parts of the program that don’t impact speed (i.e., follow Amdahl’s law from academic literature). For example, say that I want to determine why an algorithm in a program is slow. Here, I define a function that sorts a `list` of data using an insertion sort:

最佳做法是忽略你的直觉，在尝试优化程序之前直接测量其性能。Python提供了一个内置的性能分析工具，用于确定程序的哪些部分负责其执行时间。性能分析使您可以将优化工作集中在最大的问题源上，并忽略那些不影响速度的部分（即，遵循学术文献中的Amdahl定律）。例如，假设我想确定为什么程序中的某个算法很慢。在这里，我定义了一个使用插入排序对`list`数据进行排序的函数：

```
def insertion_sort(data):
    result = []
    for value in data:
        insert_value(result, value)
    return result
```

The core mechanism of the insertion sort is the function that finds the insertion point for each piece of data. Here, I define an extremely inefficient version of the `insert_value` function that does a linear scan over the input array:

插入排序的核心机制是一个为每个数据找到插入点的函数。这里，我定义了一个极其低效的`insert_value`函数版本，它对输入数组进行线性扫描：

```
def insert_value(array, value):
    for i, existing in enumerate(array):
        if existing > value:
            array.insert(i, value)
            return
    array.append(value)
```

To profile `insertion_sort` and `insert_value` , I create a data set of random numbers and define a `test` function to pass to the profiler (see Item 39: “Prefer `functools.partial` Over `lambda` Expressions For Glue Functions” for background on `lambda` ):

为了分析`insertion_sort`和`insert_value`，我创建了一个随机数数据集并定义了一个传递给性能分析器的`test`函数（参见条目39：“优先使用`functools.partial`而不是`lambda`表达式作为胶水函数”以获取背景信息）：

```
from random import randint

max_size = 12**4
data = [randint(0, max_size) for _ in range(max_size)]
test = lambda: insertion_sort(data)
```

Python provides two built-in profilers, one that is pure Python ( `profile` ) and another that is a C-extension module ( `cProfile` ). The `cProfile` built-in module is better because of its minimal impact on the performance of your program while it’s being profiled. The pure-Python alternative imposes a high overhead that skews the results.

Python提供了两个内置的性能分析器，一个是纯Python实现（`profile`），另一个是C扩展模块（`cProfile`）。由于`cProfile`对程序性能的影响最小，因此它是更好的选择。纯Python替代方案会产生很高的开销，这会扭曲结果。

---

> Note
When profiling a Python program, be sure that what you’re measuring is the code itself and not any external systems. Beware of functions that access the network or resources on disk. These may appear to have a large impact on your program’s execution time because of the slowness of the underlying systems. If your program uses a cache to mask the latency of slow resources like these, you should also ensure that it’s properly warmed up before you start profiling.

> 注意
在对Python程序进行性能分析时，请确保您测量的是代码本身而不是任何外部系统。注意访问网络或磁盘资源的函数。由于底层系统的缓慢，这些可能会对程序的执行时间产生很大影响。如果您的程序使用缓存来掩盖这些慢速资源的延迟，则还应确保在开始性能分析之前正确预热缓存。

---

Here, I instantiate a `Profile` object from the `cProfile` module and run the test function through it using the `runcall` method:

在这里，我从`cProfile`模块实例化了一个`Profile`对象，并使用`runcall`方法通过它运行测试函数：

```
from cProfile import Profile
profiler = Profile()
profiler.runcall(test)

>>>
[1474]
```

When the test function has finished running, I can extract statistics about its performance by using the `pstats` built-in module and its `Stats` class. Various methods on a `Stats` object adjust how to select and sort the profiling information to show only the things I care about:

当测试函数完成运行后，我可以使用`pstats`内置模块及其`Stats`类提取有关其性能的统计信息。`Stats`对象上的各种方法调整如何选择和排序性能分析信息，以显示仅我关心的内容：

```
from pstats import Stats
stats = Stats(profiler)
stats.strip_dirs()
stats.sort_stats("cumulative")
stats.print_stats()
```

The output is a table of information organized by function. The data sample is taken only from the time the profiler was active, during the `runcall` method above:

输出是一个按函数组织的信息表。数据样本仅取自性能分析器处于活动状态的时间，即上面的`runcall`方法期间：

```
>>>
<pstats.Stats object at 0x000001C7B77F1A90>
<pstats.Stats object at 0x000001C7B77F1A90>
stats.print_stats()
        5 function calls in 0.000 seconds

  Ordered by: cumulative time

  ncalls  tottime  percall  cumtime  percall filename:lineno(function)
       1    0.000    0.000    0.000    0.000 {method 'disable' of '_lsprof.Profiler' objects}
       1    0.000    0.000    0.000    0.000 <python-input-6>:1(<lambda>)
       1    0.000    0.000    0.000    0.000 <python-input-0>:1(insertion_sort)
       1    0.000    0.000    0.000    0.000 <python-input-2>:1(insert_value)
       1    0.000    0.000    0.000    0.000 {method 'append' of 'list' objects}
```

Here’s a quick guide to what the profiler statistics columns mean.

- `ncalls` : The number of calls to the function during the profiling period.
- `tottime` : The number of seconds spent executing the function, excluding time spent executing other functions it calls.
- `tottime percall` : The average number of seconds spent in the function each time it was called, excluding time spent executing other functions it calls. This is `tottime` divided by `ncalls` .
- `cumtime` : The cumulative number of seconds spent executing the function, including time spent in all other functions it calls.
- `cumtime percall` : The average number of seconds spent in the function each time it was called, including time spent in all other functions it calls. This is `cumtime` divided by `ncalls` .

以下是性能分析器统计信息列含义的快速指南。

- `ncalls` : 在性能分析期间调用该函数的次数。
- `tottime` : 执行该函数所花费的秒数，不包括执行其他被调用函数所花费的时间。
- `tottime percall` : 每次调用该函数时平均花费的秒数，不包括执行其他被调用函数所花费的时间。这是`tottime`除以`ncalls`。
- `cumtime` : 执行该函数所花费的累计秒数，包括所有被调用函数所花费的时间。
- `cumtime percall` : 每次调用该函数时平均花费的秒数，包括所有被调用函数所花费的时间。这是`cumtime`除以`ncalls`。

Looking at the profiler statistics table above, I can see that the biggest use of CPU in my test is the cumulative time spent in the `insert_value` function. Here, I redefine that function to use the more efficient `bisect` built-in module (see Item 102: “Consider Searching Sorted Sequences with `bisect` ”):

查看上面的性能分析器统计表，我可以看到在我的测试中CPU的最大使用量是在`insert_value`函数中花费的累计时间。在这里，我重新定义了该函数，使用更高效的`bisect`内置模块（参见条目102：“考虑使用`bisect`搜索已排序序列”）：

```
from bisect import bisect_left

def insert_value(array, value):
    i = bisect_left(array, value)
    array.insert(i, value)
```

I can run the profiler again and generate a new table of profiler statistics. The new function is much faster, with a cumulative time spent that is nearly 40 times smaller than with the previous `insert_value` function:

我可以再次运行性能分析器并生成新的性能分析统计表。新函数要快得多，其累计时间比之前的`insert_value`函数小近40倍：

```
profiler = Profile()
profiler.runcall(test)
stats = Stats(profiler)
stats.strip_dirs()
stats.sort_stats("cumulative")
stats.print_stats()

>>>
[1474]
<pstats.Stats object at 0x000001C7B9594690>
<pstats.Stats object at 0x000001C7B9594690>
stats.print_stats()
         6 function calls in 0.000 seconds

   Ordered by: cumulative time

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.000    0.000    0.000    0.000 {method 'disable' of '_lsprof.Profiler' objects}
        1    0.000    0.000    0.000    0.000 <python-input-6>:1(<lambda>)
        1    0.000    0.000    0.000    0.000 <python-input-0>:1(insertion_sort)
        1    0.000    0.000    0.000    0.000 <python-input-17>:1(insert_value)
        1    0.000    0.000    0.000    0.000 {built-in method _bisect.bisect_left}
        1    0.000    0.000    0.000    0.000 {method 'insert' of 'list' objects}


<pstats.Stats object at 0x000001C7B9594690>
```

Sometimes, when you’re profiling an entire program, you might find that a common utility function is responsible for the majority of execution time. The default output from the profiler makes such a situation difficult to understand because it doesn’t show that the utility function is called by many different parts of your program.

有时，当你分析整个程序时，你可能会发现一个常用实用函数负责大部分执行时间。默认的性能分析器输出使得这种情况难以理解，因为它没有显示该实用函数是由程序的许多不同部分调用的。

For example, here the `my_utility` function is called repeatedly by two different functions in the program:

例如，这里的`my_utility`函数被程序中的两个不同函数反复调用：

```
def my_utility(a, b):
    c = 1
    for i in range(100):
        c += a * b

def first_func():
    for _ in range(1000):
        my_utility(4, 5)

def second_func():
    for _ in range(10):
        my_utility(1, 3)

def my_program():
    for _ in range(20):
        first_func()
        second_func()
```

Profiling this code and using the default `print_stats` output produces statistics that are confusing:

分析这段代码并使用默认的`print_stats`输出产生的统计信息令人困惑：

```
profiler = Profile()
profiler.runcall(my_program)
stats = Stats(profiler)
stats.strip_dirs()
stats.sort_stats("cumulative")
stats.print_stats()
>>>
<pstats.Stats object at 0x000001C7B7776990>
<pstats.Stats object at 0x000001C7B7776990>
stats.print_stats()
         20242 function calls in 0.061 seconds

   Ordered by: cumulative time

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.000    0.000    0.061    0.061 <python-input-38>:1(my_program)
       20    0.003    0.000    0.060    0.003 <python-input-31>:1(first_func)
    20200    0.058    0.000    0.058    0.000 <python-input-30>:1(my_utility)
       20    0.000    0.000    0.000    0.000 <python-input-37>:1(second_func)
        1    0.000    0.000    0.000    0.000 {method 'disable' of '_lsprof.Profiler' objects}


<pstats.Stats object at 0x000001C7B7776990>
```

The `my_utility` function is clearly the source of most execution time, but it’s not immediately obvious why that function is called so much. If you search through the program’s code, you’ll find multiple call sites for `my_utility` and still be confused.

显然，`my_utility`函数是执行时间的主要来源，但并不明显为什么这个函数会被调用这么多次。如果你在程序的代码中搜索`my_utility`的调用站点，你会发现有多个调用点仍然会让你感到困惑。

To deal with this, the Python profiler provides the `print_callers` method to show which callers contributed to the profiling information of each function:

为了解决这个问题，Python性能分析器提供了`print_callers`方法，以显示哪些调用者贡献了每个函数的性能分析信息：

```
stats.print_callers()
```

This profiler statistics table shows functions called on the left and which function was responsible for making the call on the right. Here, it’s clear that `my_utility` is most used by `first_func` :

这个性能分析器统计表显示左侧的函数以及哪个函数负责进行调用。这里，很明显`my_utility`主要由`first_func`使用：

```
>>>
   Ordered by: cumulative time

Function                                          was called by...
                                                      ncalls  tottime  cumtime
<python-input-38>:1(my_program)                   <-
<python-input-31>:1(first_func)                   <-      20    0.003    0.060  <python-input-38>:1(my_program)
<python-input-30>:1(my_utility)                   <-   20000    0.057    0.057  <python-input-31>:1(first_func)
                                                         200    0.000    0.000  <python-input-37>:1(second_func)
<python-input-37>:1(second_func)                  <-      20    0.000    0.000  <python-input-38>:1(my_program)
{method 'disable' of '_lsprof.Profiler' objects}  <-


<pstats.Stats object at 0x000001C7B7776990>
```


Alternatively, you can call the `print_callees` method, which shows a top-down segmentation of how each function (on the left) spends time executing other dependent functions (on the right) deeper in the call stack:

或者，你可以调用`print_callees`方法，它展示了每个函数（左侧）如何将其时间分配到调用栈深处的其他依赖函数（右侧）：

```
stats.print_callees()

>>>
 stats.print_callees()
   Ordered by: cumulative time

Function                                          called...
                                                      ncalls  tottime  cumtime
<python-input-38>:1(my_program)                   ->      20    0.003    0.060  <python-input-31>:1(first_func)
                                                          20    0.000    0.000  <python-input-37>:1(second_func)
<python-input-31>:1(first_func)                   ->   20000    0.057    0.057  <python-input-30>:1(my_utility)
<python-input-30>:1(my_utility)                   ->
<python-input-37>:1(second_func)                  ->     200    0.000    0.000  <python-input-30>:1(my_utility)
{method 'disable' of '_lsprof.Profiler' objects}  ->


<pstats.Stats object at 0x000001C7B7776990>
```

If you’re not able to figure out why your program is slow using `cProfile` , fear not. Python includes other tools for assessing performance (see Item 93: “Optimize Performance-Critical Code Using `timeit` Microbenchmarks”, Item 98: “Lazy-load Modules with Dynamic Imports to Reduce Startup Time”, and (see Item 115: “Use `tracemalloc` to Understand Memory Usage and Leaks”). There are also community-built tools (see Item 116: “Know Where to Find Community-Built Modules”) that have additional capabilities for assessing performance, such as line profilers, sampling profilers, integration with Linux’s `perf` tool, memory usage profilers, and more.

如果您无法使用`cProfile`弄清楚为什么您的程序很慢，请不要担心。Python包含其他评估性能的工具（参见条目93：“使用`timeit`微基准测试优化性能关键代码”，条目98：“使用动态导入延迟加载模块以减少启动时间”，和条目115：“使用`tracemalloc`了解内存使用和泄漏情况”）。还有社区构建的工具（参见条目116：“知道在哪里找到社区构建的模块”），它们具有更多评估性能的功能，例如行性能分析器、采样性能分析器、与Linux的`perf`工具的集成、内存使用性能分析器等。


**Things to Remember**

- It’s important to profile Python programs before optimizing because the sources of slowdowns are often obscure.
- Use the `cProfile` module instead of the `profile` module because it provides more accurate profiling information.
- The `Profile` object’s `runcall` method provides everything you need to profile a tree of function calls in isolation.
- The `Stats` object lets you select and print the subset of profiling information you need to see to understand your program’s performance.

**注意事项**
- 在优化之前对Python程序进行性能分析很重要，因为性能下降的原因通常是模糊不清的。
- 使用`cProfile`模块而不是`profile`模块，因为它提供了更准确的性能分析信息。
- `Profile`对象的`runcall`方法提供了孤立地分析函数调用树所需的一切。
- `Stats`对象允许您选择和打印需要查看的性能分析信息子集，以了解程序的性能。