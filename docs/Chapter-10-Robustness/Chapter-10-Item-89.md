# Chapter 10: Robustness (健壮性)

## Item 89: Always Pass Resources into Generators and Have Callers Clean Them Up Outside (始终将资源传递给生成器，并在外部由调用者清理它们)

Python provides a variety of tools, such as exception handlers (see Item 80: “Take Advantage of Each Block in `try` / `except` / `else` / `finally` ”) and with statements (see Item 82: “Consider `contextlib` and `with` Statements for Reusable `try` / `finally` Behavior”), to help you ensure that resources like files, mutexes, and sockets are properly cleaned up at the right time. For example, in a normal function, a simple `finally` clause will be executed before the return value is actually received by the caller, making it an ideal location to reliably close file handles:

Python 提供了多种工具，例如异常处理程序（参见条目80：“充分利用 `try` / `except` / `else` / `finally` 中的每个块”）和 with 语句（参见条目82：“考虑使用 `contextlib` 和 `with` 语句以实现可重用的 `try` / `finally` 行为”），以帮助您确保文件、互斥锁和套接字等资源能够在适当的时间被正确清理。例如，在一个普通函数中，简单的 `finally` 子句将在返回值实际被调用者接收之前执行，使其成为可靠关闭文件句柄的理想位置：

```
def my_func():
    try:
        return 123
    finally:
        print("Finally my_func")

print("Before")
print(my_func())
print("After")

>>>
Before
Finally my_func
123
After
```

In contrast, when using a generator function (see Item 43: “Consider Generators Instead of Returning Lists”), the `finally` clause won’t execute until the `StopIteration` exception is raised to indicate the sequence of values has been exhausted (see Item 21: “Be Defensive When Iterating Over Arguments”). That means the `finally` clause is executed after the last item is received by the caller, unlike a normal function:

相比之下，当使用生成器函数时（参见条目43：“考虑使用生成器代替返回列表”），`finally` 子句不会执行，直到引发 `StopIteration` 异常以指示值序列已耗尽（参见条目21：“迭代参数时要谨慎”）。这意味着 `finally` 子句是在最后一个项目被调用者接收之后执行的，这与普通函数不同：

```
def my_generator():
    try:
        yield 10
        yield 20
        yield 30
    finally:
        print("Finally my_generator")

print("Before")

for i in my_generator():
    print(i)

print("After")

>>>
Before
10
20
30
Finally my_generator
After
```

However, it’s also possible for Python generators to not finish being iterated. In theory, this could prevent the `StopIteration` exception from ever being raised and thereby avoid executing the `finally` clause. Here, I simulate this behavior by manually stepping forward the generator function’s iterator—note how `"Finally my_generator"` doesn't print:

然而，Python 生成器也可能不完成迭代。理论上，这可能防止 `StopIteration` 异常被引发，从而避免执行 `finally` 子句。在这里，我通过手动前进生成器函数的迭代器来模拟这种行为——请注意 `"Finally my_generator"` 并没有打印出来：

```
it = my_generator()
print("Before")
print(next(it))
print(next(it))
print("After")

>>>
Before
10
20
After
```

The `finally` clause hasn’t executed yet. When will it? The answer is that it depends—it might never run. If the last reference to the iterator is dropped, garbage collection is enabled, and a collection cycle runs, that should cause the generator’s `finally` clause to execute:

`finally` 子句尚未执行。它什么时候会执行呢？答案是取决于情况——它可能永远不会运行。如果迭代器的最后一个引用被删除，启用了垃圾回收，并且运行了一个回收周期，那应该会导致生成器的 `finally` 子句执行：

```
import gc
del it
gc.collect()

>>>
Finally my_generator
```

The mechanism that powers this is the `GeneratorExit` exception that inherits from `BaseException` (see Item 86: “Understand the Difference Between `Exception` and `BaseException` ”). Upon garbage collection, Python will `send` this special type of exception into the generator if it’s not exhausted (see Item 46: “Pass Iterators into Generators as Arguments Instead of Calling the `send` Method” for background). Normally this causes the generator to return and clear its stack, but technically you can catch this type of exception and handle it:

驱动这一机制的是从 `BaseException` 继承的 `GeneratorExit` 异常（参见条目86：“了解 `Exception` 和 `BaseException` 之间的区别”）。在垃圾回收时，如果生成器未耗尽，Python 将向生成器发送这种特殊类型的异常（参见条目46：“将迭代器作为参数传入生成器，而不是调用 `send` 方法”以获得背景信息）。通常这会导致生成器返回并清除其堆栈，但从技术上讲，您可以捕获此类型的异常并进行处理：

```
def catching_generator():
    try:
        yield 40
        yield 50
        yield 60
    except BaseException as e:  # Catches GeneratorExit
        print("Catching handler", type(e), e)
        raise
```

At the end of the exception handler I use a bare `raise` keyword with no arguments to ensure that the `GeneratorExit` exception propagates and none of Python’s runtime machinery breaks. Here, I step forward this new generator and then cause another garbage collecting cycle:

在异常处理程序的末尾，我使用了一个没有参数的 `raise` 关键字，以确保 `GeneratorExit` 异常传播，并且 Python 的任何运行时机制都不会中断。这里，我前进了这个新生成器，然后引发了另一个垃圾收集周期：

```
it = catching_generator()
print("Before")
print(next(it))
print(next(it))
print("After")
del it
gc.collect()

>>>
Before
40
50
After
Catching handler <class 'GeneratorExit'>
```

The exception handler is run separately by the `gc` module, not in the original call stack that created the generator and stepped it forward. What happens if a different exception is raised while handling the `GeneratorExit` exception? Here, I define another generator to demonstrate this possibility:

异常处理程序是由 `gc` 模块单独运行的，而不是在创建生成器和前进它的原始调用栈中运行。如果在处理 `GeneratorExit` 异常时引发其他异常会发生什么？在这里，我定义了另一个生成器来演示这种可能性：

```
import gc
import sys

def broken_generator():
    try:
        yield 70
        yield 80
    except BaseException as e:
        print("Broken handler", type(e), e)
        raise RuntimeError("Broken")

it = broken_generator()
print("Before")
print(next(it))
print("After")
sys.stdout.flush()
del it
gc.collect()
print("Still going")

>>>
Before
70
After
Broken handler <class 'GeneratorExit'>
Exception ignored in: <generator object broken_generator at 0x0000023520695C40>
Traceback (most recent call last):
  File "<python-input-36>", line 7, in broken_generator
RuntimeError: Broken
0
Still going
```

This outcome is surprising: The `gc` module catches the `RuntimeError` raised by `broken_generator` and prints it out to `sys.stderr` . The exception is not raised back into the main thread where `gc.collect` was called. Instead, it’s completely swallowed and hidden from the rest of the program, which continues running. This means that you can’t rely on exception handlers or `finally` clauses in generators to always execute and report errors back to callers.

这个结果令人惊讶：`gc` 模块捕获了由 `broken_generator` 引发的 `RuntimeError` 并将其打印到 `sys.stderr`。该异常没有重新引发回调用 `gc.collect` 的主线程，而是完全被吞噬并隐藏了起来，整个程序继续运行。这意味着你不能依赖生成器中的异常处理程序或 `finally` 子句总是执行并报告错误回给调用者。

To work around this potential risk, you can allocate resources that need to be cleaned up outside of a generator and pass them in as arguments. For example, imagine I’m trying to build a simple utility that finds the maximum length of the first 5 lines of a file. Here, I define a simple generator that yields line lengths given a file path:

为了避免这种潜在风险，你可以在生成器之外分配需要清理的资源，并将它们作为参数传入。例如，假设我试图构建一个简单的实用程序来查找文件前五行的最大长度。在这里，我定义了一个简单的生成器，它给定一个文件路径后按行长度生成：

```
with open("my_file.txt", "w") as f:
    for _ in range(20):
        f.write("a" * random.randint(0, 100))
        f.write("\n")

def lengths_path(path):
    try:
        with open(path) as handle:
            for i, line in enumerate(handle):
                print(f"Line {i}")
                yield len(line.strip())
    finally:
        print("Finally lengths_path")
```

I can use the generator in a loop to calculate the maximum, and then terminate the loop early, leaving the `lengths_path` generator in a partially executed state.

我可以使用循环中的生成器计算最大值，然后提前终止循环，使 `lengths_path` 生成器处于部分执行状态。

```
max_head = 0
it = lengths_path("my_file.txt")

for i, length in enumerate(it):
    if i == 5:
        break
    else:
        max_head = max(max_head, length)

print(max_head)

>>>
Line 0
Line 1
Line 2
Line 3
Line 4
Line 5
99
```

After the generator iterator goes out of scope sometime later it will be garbage collected and the `finally` clause will run as expected.

在生成器迭代器稍后超出作用域时，它将被垃圾回收，`finally` 子句将如预期般运行。

```
del it
gc.collect()

>>>
Finally lengths_path
```


This delayed behavior is what I’m trying to avoid. I need `finally` to run within the call stack of the original loop so if any errors are encountered they’re properly raised back to the caller. This is especially important for resources like mutex locks that must avoid deadlocking. To accomplish the correct behavior, I can pass an open file handle into the generator function:

这种延迟的行为是我想要避免的。我需要 `finally` 在原始循环的调用栈中运行，以便在遇到任何错误时能够正确地将它们引发回给调用者。这对于必须避免死锁的互斥锁等资源尤其重要。为了实现正确的行为，我可以将一个打开的文件句柄传递给生成器函数：

```
def lengths_handle(handle):
    try:
        for i, line in enumerate(handle):
            print(f"Line {i}")
            yield len(line.strip())
    finally:
        print("Finally lengths_handle")
```

I can use a `with` statement around the loop to make sure the file is opened and closed reliably and immediately so the generator doesn’t have to:

我可以使用 `with` 语句围绕循环以确保文件可靠且立即打开和关闭，这样生成器就不必这样做：

```
max_head = 0

with open("my_file.txt") as handle:
    it = lengths_handle(handle)
    for i, length in enumerate(it):
        if i == 5:
            break
        else:
            max_head = max(max_head, length)

print(max_head)
print("Handle closed:", handle.closed)

>>>
Line 0
Line 1
Line 2
Line 3
Line 4
Line 5
99
Handle closed: True
```

Again, because the loop iteration ended before exhaustion, the generator function hasn’t exited and the `finally` clause hasn’t executed. But that’s okay with this different approach because I’m not relying on the generator to do any important clean-up.

同样，由于循环迭代在耗尽之前结束，生成器函数尚未退出，`finally` 子句也未执行。但在这个不同的方法中没问题，因为我并不依赖于生成器来做任何重要的清理工作。

The `GeneratorExit` exception represents a compromise between correctness and system health. If generators weren’t forced to exit eventually, all prematurely stopped generators would leak memory and potentially cause the program to crash. Swallowing errors is the trade off that Python makes because it’s a reasonable thing to do most of the time. But it’s up to you to make sure your generators expect this behavior and plan accordingly.

`GeneratorExit` 异常代表了正确性和系统健康之间的妥协。如果生成器不被强制最终退出，所有提前停止的生成器都会泄漏内存并可能导致程序崩溃。吞下错误是 Python 做出的权衡，因为大多数时候这是合理的事情。但您有责任确保您的生成器预料到这种行为并相应地计划。

**Things to Remember**
- In normal functions, `finally` clauses are executed before values are returned, but in generator functions `finally` clauses are only run after exhaustion when the `StopIteration` exception is raised.
- In order to prevent memory leaks, the garbage collector will inject `GeneratorExit` exceptions into unreferenced, partially-iterated generators to cause them to exit and release resources.
- Due to this behavior, it’s often better to pass resources (like files and mutexes) into generator functions instead of relying on them to allocate and clean up the resources properly.

**注意事项**

- 在普通函数中，`finally` 子句在值返回之前执行，但在生成器函数中，`finally` 子句仅在耗尽时引发 `StopIteration` 异常后运行。
- 为了防止内存泄漏，垃圾收集器将向未引用的、部分迭代的生成器注入 `GeneratorExit` 异常，以导致它们退出并释放资源。
- 由于这种行为，最好将资源（如文件和互斥锁）传递给生成器函数，而不是依赖它们正确分配和清理资源。