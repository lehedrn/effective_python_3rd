# Chapter 6: Comprehensions and Generators (推导式与生成器)

## Item 47: Manage Iterative State Transitions with a Class Instead of the Generator `throw` Method (使用类而不是生成器的 `throw` 方法管理迭代状态转换)

In addition to `yield from` expressions (see Item 45: “Compose Multiple Generators with `yield from` ”) and the `send` method (see Item 46: “Pass Iterators into Generators as Arguments Instead of Calling the `send` Method”), another advanced generator feature is the `throw` method for re-raising `Exception` instances within generator functions. The way `throw` works is simple: When the method is called, the next occurrence of a `yield` expression inside the generator re-raises the provided `Exception` instance after its output is received instead of continuing normally. Here, I show a simple example of this behavior in action:

除了 `yield from` 表达式（见条目45：“使用 `yield from` 组合多个生成器”）和 `send` 方法（见条目46：“将迭代器作为参数传入生成器，而不是调用 `send` 方法”）之外，另一个高级生成器特性是使用 `throw` 方法在生成器函数中重新引发 `Exception` 实例。`throw` 的工作方式很简单：当调用该方法时，生成器内部下一次出现的 `yield` 表达式会重新引发所提供的 `Exception` 实例，而不是继续正常执行。下面我展示了一个简单示例来说明这种行为：

```
class MyError(Exception):
        pass
    
def my_generator():
    yield 1
    yield 2
    yield 3

it = my_generator()
print(next(it))                         # Yields 1
print(next(it))                         # Yields 2
print(it.throw(MyError("test error")))  # Raises

>>>
1
2
Traceback ...
MyError: test error
```

When you call `throw` , the generator function may catch the injected exception with a standard `try / except` compound statement that surrounds the last `yield` expression that was executed (see Item 80: “Take Advantage of Each Block in `try / except / else / finally` ” for more about exception handling):

当你调用 `throw` 时，生成器函数可能会通过围绕上一个执行过的 `yield` 表达式的标准 `try / except` 复合语句捕获注入的异常（另请参阅条目80：“充分利用 `try / except / else / finally` 中的每个块”了解有关异常处理的更多信息）：

```
def my_generator():
    yield 1

    try:
        yield 2
    except MyError:
        print("Got MyError!")
    else:
        yield 3

    yield 4

it = my_generator()
print(next(it))                         # Yields 1
print(next(it))                         # Yields 2
print(it.throw(MyError("test error")))  # Yields 4

>>>
1
2
Got MyError!
4
```

This functionality provides a two-way communication channel between a generator and its caller that can be useful in certain situations. For example, imagine that I need a timer program that supports sporadic resets. Here, I implement this behavior by defining a generator that relies on `Reset` exceptions to be raised when the `yield` expression is evaluated:

此功能提供了生成器与其调用者之间的双向通信通道，在某些情况下可能很有用。例如，假设我需要一个支持偶尔重置的计时器程序。在这里，我通过定义一个依赖于 `Reset` 异常的生成器来实现此行为，当 `yield` 表达式被求值时会引发这些异常：

```
class Reset(Exception):
    pass

def timer(period):
    current = period
    while current:
        try:
            yield current
        except Reset:
            print("Resetting")
            current = period
        else:
            current -= 1
```

Whenever the `throw` method is called on the generator with a `Reset` exception, the counter is restarted in the `except` block. Here, I define a driver function that iterates the `timer` generator, announces progress at each step, and injects reset events that might be caused by an externally￾polled input (such as a button):

每当在生成器上调用带有 `Reset` 异常的 `throw` 方法时，`except` 块中的计数器就会重启。这里，我定义了一个驱动函数来迭代 `timer` 生成器，在每一步都宣布进度，并注入可能由外部轮询输入（如按钮）引起的重置事件：

```
ORIGINAL_RESETS = [
    False,
    False,
    False,
    True,
    False,
    True,
    False,
    False,
    False,
    False,
    False,
    False,
    False,
    False,
]
RESETS = ORIGINAL_RESETS[:]

def check_for_reset():
    # Poll for external event
    return RESETS.pop(0)

def announce(remaining):
    print(f"{remaining} ticks remaining")

def run():
    it = timer(4)
    while True:
        try:
            if check_for_reset():
                current = it.throw(Reset())
            else:
                current = next(it)
        except StopIteration:
            break
        else:
            announce(current)

run()
>>>
4 ticks remaining
3 ticks remaining
2 ticks remaining
Resetting
4 ticks remaining
3 ticks remaining
Resetting
4 ticks remaining
3 ticks remaining
2 ticks remaining
1 ticks remaining
```

This code works as expected, but it’s much harder to read than necessary. The various levels of nesting required to catch `StopIteration` exceptions or decide to `throw` , call `next` , or `announce` make the code noisy.

这段代码按预期工作，但阅读起来比必要复杂得多。为了捕获 `StopIteration` 异常或决定是否调用 `throw`、`next` 或 `announce`，所需的多层嵌套使代码变得杂乱。

A simpler approach to implementing this functionality is to create a basic class to manage the timer’s state and enable state transitions. Here, I define a class with a `tick` method to step the timer, a `reset` method to restart the clock, and the `__bool__` special method to check whether the timer has elapsed (see Item 57: “Inherit from collections.abc for Custom Container Types” for background):

实现此功能的一个更简单的方法是创建一个基本类来管理定时器的状态并启用状态转换。在此处，我定义了一个具有 `tick` 方法逐步递减定时器、`reset` 方法重启定时器以及 `__bool__` 特殊方法检查定时器是否已过期的类（详见条目57：“为自定义容器类型从 collections.abc 继承”）：

```
class Timer:
    def __init__(self, period):
        self.current = period
        self.period = period

    def reset(self):
        print("Resetting")
        self.current = self.period

    def tick(self):
        before = self.current
        self.current -= 1
        return before

    def __bool__(self):
        return self.current > 0
```

Now, the `run` method can use the `Timer` object as the test expression in the `while` statement; the code in the loop body is much easier to follow because of the reduction in the levels of nesting:

现在，`run` 函数可以使用 `Timer` 对象作为 `while` 语句中的测试表达式；由于嵌套层级减少，循环体中的代码更容易理解：

```
RESETS = ORIGINAL_RESETS[:]

def run():
    timer = Timer(4)
    while timer:
        if check_for_reset():
            timer.reset()

        announce(timer.tick())

run()

>>>
4 ticks remaining
3 ticks remaining
2 ticks remaining
Resetting
4 ticks remaining
3 ticks remaining
Resetting
4 ticks remaining
3 ticks remaining
2 ticks remaining
1 ticks remaining
```

The output matches the earlier version using `throw` , but this implementation is much easier to understand, especially for new readers of the code. I suggest that you avoid using `throw` entirely and instead use a stateful class if you need this type of exceptional behavior (see Item 89: “Always Pass Resources into Generators and Have Callers Clean Them Up Outside” for another reason why). Otherwise, if you really need more advanced cooperation between generator-like functions, it’s worth considering Python’s asynchronous features (see Item 75: “Achieve Highly Concurrent I/O with Coroutines”).

输出与前面使用 `throw` 的版本相同，但此实现更易于理解，特别是对于新读者来说。我建议你完全避免使用 `throw`，而是使用有状态的类来代替，如果你需要此类异常行为的话（另一个原因，请参见条目89：“始终将资源传递给生成器，并让调用者在外部清理它们”）。否则，如果你真的需要生成器类似函数之间更复杂的协作，值得考虑 Python 的异步特性（详见条目75：“使用协程实现高度并发的 I/O”）。

**Things to Remember**
- The `throw` method can be used to re-raise exceptions within generators at the position of the most recently executed `yield` expression.
- Using `throw` harms readability because it requires additional nesting and boilerplate in order to raise and catch exceptions.
- A better approach is to simply define a stateful class that provides methods for iteration and state transitions.

**注意事项*
- `throw` 方法可以在生成器内最近执行的 `yield` 表达式位置重新引发异常。
- 使用 `throw` 会损害可读性，因为它需要额外的嵌套和样板代码来引发和捕获异常。
- 更好的方法是直接定义一个提供用于迭代和状态转换方法的状态类。