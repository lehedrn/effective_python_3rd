# Chapter 13: Testing and Debugging (测试与调试)

## Item 115: Use `tracemalloc` to Understand Memory Usage and Leaks (使用 `tracemalloc` 来理解内存使用和泄漏)

Memory management in the default implementation of Python, CPython, uses reference counting. This ensures that as soon as all references to an object have expired, the referenced object is also cleared from memory, freeing up that space for other data. CPython also has a built-in cycle detector to ensure that self-referencing objects are eventually garbage collected.

在默认实现的 Python（即 CPython）中，内存管理使用了引用计数机制。这意味着一旦某个对象的所有引用都失效了，该对象就会立即被从内存中清除，从而释放空间供其他数据使用。CPython 还内置了一个循环检测器，以确保自我引用的对象最终会被垃圾回收。

In theory, this means that most Python developers don’t have to worry about allocating or deallocating memory in their programs. It’s taken care of automatically by the language and the CPython runtime. However, in practice, programs eventually do run out of memory due to no longer useful references still being held. Figuring out where a Python program is using or leaking memory proves to be a challenge.

理论上，这表示大多数 Python 开发者不需要担心程序中的内存分配或释放问题。这些工作由语言本身和 CPython 运行时自动处理。然而实际上，程序仍然会因为持有不再有用的引用而耗尽内存。找出 Python 程序中内存使用或泄漏的位置是一项挑战。

One way to debug memory usage is to ask the `gc` built-in module to list every object currently known by the garbage collector. Although it’s quite a blunt tool, this approach lets you quickly get a sense of where your program’s memory is being used. Here, I define a module that fills up memory by keeping references:

一种调试内存使用的方法是使用 `gc` 内置模块列出垃圾收集器当前知道的每一个对象。虽然这是一个比较粗糙的工具，但这种方法可以快速了解程序的内存使用情况。以下我定义了一个模块来通过保持引用来填满内存：

```
# waste_memory.py
import os

class MyObject:
    def __init__(self):
        self.data = os.urandom(100)

def get_data():
    values = []
    for _ in range(100):
        obj = MyObject()
        values.append(obj)
    return values

def run():
    deep_values = []
    for _ in range(100):
        deep_values.append(get_data())
    return deep_values
```

Then, I run a program that uses the `gc` built-in module to print out how many objects were created during execution, along with a small sample of allocated objects:

然后，我运行一个程序，使用 `gc` 内置模块打印出执行期间创建的对象数量以及一部分已分配对象的示例：

```
# using_gc.py
import gc

found_objects = gc.get_objects()
print("Before:", len(found_objects))

import waste_memory

hold_reference = waste_memory.run()

found_objects = gc.get_objects()
print("After: ", len(found_objects))
for obj in found_objects[:3]:
    print(repr(obj)[:100])

print("...")

>>>
Before: 6207
After: 16801
<waste_memory.MyObject object at 0x10390aeb8>
<waste_memory.MyObject object at 0x10390aef0>
<waste_memory.MyObject object at 0x10390af28>
...
```

The problem with `gc.get_objects` is that it doesn’t tell you anything about how the objects were allocated. In complicated programs, objects of a specific class could be allocated many different ways. Knowing the overall number of objects isn’t nearly as important as identifying the code responsible for allocating the objects that are leaking memory.

`gc.get_objects` 的问题是它不会告诉你任何关于对象是如何分配的信息。在复杂的程序中，特定类的对象可能通过多种方式分配。知道对象的总数远不如识别负责分配泄漏内存对象的代码重要。

Python 3.4 introduced a new `tracemalloc` built-in module for solving this problem. `tracemalloc` makes it possible to connect an object back to where it was allocated. You use it by taking before and after snapshots of memory usage and comparing them to see what’s changed. Here, I use this approach to print out the top three memory usage offenders in a program:

Python 3.4 引入了一个新的 `tracemalloc` 内置模块来解决这个问题。`tracemalloc` 可以将对象与其分配位置关联起来。你可以通过对内存使用情况进行前后快照并进行对比来使用它。以下我使用这种方法打印出程序中最占用内存的前三个部分：

```
# top_n.py
import tracemalloc

tracemalloc.start(10)                      # Set stack depth
time1 = tracemalloc.take_snapshot()        # Before snapshot

import waste_memory

x = waste_memory.run()                     # Usage to debug
time2 = tracemalloc.take_snapshot()        # After snapshot

stats = time2.compare_to(time1, "lineno")  # Compare snapshots
for stat in stats[:3]:
    print(stat)
    
>>>
waste_memory.py:5: size=1299 KiB (+1299 KiB), count=10000 (+10000), average=133 B
waste_memory.py:10: size=785 KiB (+785 KiB), count=10000 (+10000), average=80 B
waste_memory.py:11: size=84.4 KiB (+84.4 KiB), count=100 (+100), average=864 B
```

The size and count labels in the output make it immediately clear which objects are dominating my program’s memory usage and where in the source code they were allocated.

输出中的 size 和 count 标签使得能够立即明确哪些对象在我的程序内存使用中占主导地位，以及它们是在源代码中的哪个位置分配的。

The `tracemalloc` module can also print out the full stack trace of each allocation (up to the number of frames passed to the `tracemalloc.start` function). Here, I print out the stack trace of the biggest source of memory usage in the program:

`tracemalloc` 模块还可以打印每个分配的完整堆栈跟踪（最多为传递给 `tracemalloc.start` 函数的帧数）。在这里，我打印出了程序中最大的内存使用来源的堆栈跟踪：

```
# with_trace.py
import tracemalloc

tracemalloc.start(10)
time1 = tracemalloc.take_snapshot()

import waste_memory

x = waste_memory.run()
time2 = tracemalloc.take_snapshot()

stats = time2.compare_to(time1, "traceback")
top = stats[0]
print("Biggest offender is:")
print("\n".join(top.traceback.format()))

>>>
Biggest offender is:
 File "with_trace.py", line 11
 x = waste_memory.run()
 File "waste_memory.py", line 20
 deep_values.append(get_data())
 File "waste_memory.py", line 12
 obj = MyObject()
 File "waste_memory.py", line 6
 self.data = os.urandom(100)
```

A stack trace like this is most valuable for figuring out which particular usage of a common function or class is responsible for memory consumption in a program.

这样的堆栈跟踪对于弄清楚某个常用函数或类的特定使用方式对程序内存消耗的影响非常有价值。

For more advanced memory profiling needs there are also community packages (see Item 116: “Know Where to Find Community-Built Modules”) to consider, such as Memray (`https://github.com/bloomberg/memray`).

如果你有更高级的内存分析需求，也可以考虑一些社区构建的工具包（参考第116条：“了解社区构建的模块在哪里”），比如 [Memray](https://github.com/bloomberg/memray） 。


**Things to Remember**
- It can be difficult to understand how Python programs use and leak memory.
- The `gc` module can help you understand which objects exist, but it has no information about how they were allocated.
- The `tracemalloc` built-in module provides powerful tools for understanding the sources of memory usage.

**注意事项**
- 理解 Python 程序如何使用和泄漏内存可能是困难的。
- `gc` 模块可以帮助你了解存在哪些对象，但它没有关于这些对象是如何分配的信息。
- `tracemalloc` 内置模块提供了强大的工具来理解内存使用的来源。