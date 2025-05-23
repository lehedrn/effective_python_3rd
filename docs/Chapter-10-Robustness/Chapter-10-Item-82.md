# Chapter 10: Robustness (健壮性)

## Item 82: Consider `contextlib` and `with` Statements for Reusable `try`/ `finally` Behavior (考虑使用 `contextlib` 和 `with` 语句来重用 `try` / `finally` 行为)

The `with` statement in Python is used to indicate when code is running in a special context. For example, mutual-exclusion locks (see Item 69: “Use `Lock` to Prevent Data Races in Threads”) can be used in `with` statements to indicate that the indented code block runs only while the lock is held:

Python 中的 `with` 语句用于指示代码在特殊上下文中运行。例如，互斥锁（参见条目69：“使用 `Lock` 防止线程中的数据竞争”）可以在 `with` 语句中使用，以表明缩进的代码块仅在持有锁时运行：

```
from threading import Lock
lock = Lock()
with lock:
    # Do something while maintaining an invariant
    pass
```

The example above is equivalent to this `try` / `finally` construction (see Item 80: “Take Advantage of Each Block in `try` / `except` / `else` / `finally` ”) because the `Lock` class properly enables use in `with` statements:

上面的例子等价于以下 `try` / `finally` 构造（参见条目80：“充分利用 `try` / `except` / `else` / `finally` 的每个块”），因为 `Lock` 类正确启用了在 `with` 语句中的使用：

```
lock.acquire()
try:
    # Do something while maintaining an invariant
    pass
finally:
    lock.release()
```

The `with` statement version of this is better because it eliminates the need to write the repetitive code of the `try` / `finally` compound statement, ensuring that you don’t forget to have a corresponding `release` call for every `acquire` call.

`with` 语句版本更好，因为它消除了编写重复的 `try` / `finally` 复合语句的需要，确保你不会忘记为每个 `acquire` 调用都写一个对应的 `release` 调用。

It’s easy to make your objects and functions work in `with` statements by using the `contextlib` built-in module. This module contains the `contextmanager` decorator (see Item 38: “Define Function Decorators with `functools.wraps` ” for background), which lets a simple function be used in `with` statements. This is much easier than defining a new class with the special methods `__enter__` and `__exit__` (the standard object-oriented approach).

通过使用内置的 `contextlib` 模块，可以轻松地使你的对象和函数在 `with` 语句中工作。这个模块包含了一个名为 `contextmanager` 的装饰器（参见条目38：“使用 `functools.wraps` 定义函数装饰器”以获取背景信息），它允许一个简单的函数在 `with` 语句中使用。这比定义一个带有特殊方法 `__enter__`和 `__exit__` 的新类（标准的面向对象方法）要容易得多。

For example, say that I want a region of code to have more debug logging sometimes. Here, I define a function that does logging at two severity levels:

例如，假设我希望某段代码在某些时候进行更多的调试日志记录。在这里，我定义了一个在两个严重级别上进行日志记录的函数：

```
import logging
logging.getLogger().setLevel(logging.WARNING)
def my_function():
    logging.debug("Some debug data")
    logging.error("Error log here")
    logging.debug("More debug data")
```

The default log level for my program is `WARNING` , so only the `logging.error` message will print to screen when I run the function:

我的程序的默认日志级别是 `WARNING`，因此当我运行该函数时，只有 `logging.error` 消息会打印到屏幕上：

```
my_function()
>>>
Error log here
```

I can elevate the log level of this function temporarily by defining a context manager. This helper function boosts the logging severity level before running the code in the `with` block, and reduces the logging severity level afterward:

我可以通过定义一个上下文管理器临时提升此函数的日志级别。这个辅助函数在运行 `with` 块中的代码之前提升日志严重级别，并在之后降低日志严重级别：

```
from contextlib import contextmanager
@contextmanager
def debug_logging(level):
    logger = logging.getLogger()
    old_level = logger.getEffectiveLevel()
    logger.setLevel(level)
    try:
        yield
    finally:
        logger.setLevel(old_level)
```

The `yield` expression is the point at `which` the with block’s contents will execute (see Item 43: “Consider Generators Instead of Returning Lists” for background). Any exceptions that happen in the `with` block will be reraised by the `yield` expression for you to catch in the helper function (see Item 47: “Manage Iterative State Transitions with a Class Instead of the Generator `throw` Method” for how that works).

`yield` 表达式是 `with` 块内容将要执行的点（参见条目43：“考虑生成器而不是返回列表”以获取背景信息）。在 `with` 块中发生的任何异常都将由 `yield` 表达式重新引发，供你在辅助函数中捕获（参见条目47：“使用类管理迭代状态转换，而不是生成器的 `throw` 方法”以了解其工作原理）。

Now, I can call the same logging function again, but in the `debug_logging` context. This time, all of the debug messages are printed to the screen during the `with` block. The same function running outside the `with` block won’t print debug messages:

现在，我可以再次调用相同的日志函数，但在 `debug_logging` 上下文中。这一次，在 `with` 块期间，所有调试消息都会打印到屏幕上。在 `with` 块之外运行的相同函数不会打印调试消息：

```
with debug_logging(logging.DEBUG):
    print("* Inside:")
    my_function()

print("* After:")
my_function()

>>>
* Inside:
Some debug data
Error log here
More debug data
* After:
Error log here
```

### Enabling `as` Targets ( 启用 `as` 目标)

The context manager passed to a `with` statement may also return an object. This object is assigned to a local variable in the `as` part of the compound statement. This gives the code running in the `with` block the ability to directly interact with its context (see Item 76: “Know How to Port Threaded I/O to `asyncio` ” for another example).

传递给 `with` 语句的上下文管理器还可以返回一个对象。这个对象被分配给复合语句 `as` 部分中的本地变量。这使得在 `with` 块中运行的代码能够直接与其上下文交互（参见条目76：“知道如何将线程I/O移植到 `asyncio`”以获取另一个示例）。

For example, say that I want to write a file and ensure that it’s always closed correctly. I can do this by passing `open` to the `with` statement. `open` returns a file handle for the `as` target of `with` , and it closes the handle when the `with` block exits:

例如，假设我想写入一个文件并确保它始终正确关闭。我可以通过将 `open` 传递给 `with` 语句来实现这一点。`open` 返回一个文件句柄作为 `with` 的 `as` 目标，并且当 `with` 块退出时关闭该句柄：

```
with open("my_output.txt", "w") as handle:
    handle.write("This is some data!")
```

The `with` approach is more Pythonic than manually opening and closing the file handle with a `try` / `finally` compound statement:

与手动打开和关闭文件句柄相比，`with` 方法更加 Pythonic：

```
handle = open("my_output.txt", "w")
try:
    handle.write("This is some data!")
finally:
    handle.close()
```

Using the `as` target also gives you confidence that the file is eventually closed when execution leaves the `with` statement. By highlighting the critical section, it also encourages you to reduce the amount of code that executes while the file handle is open, which is good practice in general.

使用 `as` 目标还让你确信，当执行离开 `with` 语句时，文件最终会被关闭。通过突出显示关键部分，它还鼓励你减少文件句柄打开时执行的代码量，这通常是一个好习惯。

To enable your own functions to supply values for `as` targets, all you need to do is `yield` a value from your context manager. For example, here I define a context manager to fetch a `Logger` instance, set its level, and then `yield` it to become the `as` target:

为了使你自己的函数能够为 `as` 目标提供值，你只需要从你的上下文管理器中 `yield` 一个值。例如，这里我定义了一个上下文管理器来获取一个 `Logger` 实例，设置它的级别，然后将其 `yield` 成为 `as` 目标：

```
@contextmanager
def log_level(level, name):
    logger = logging.getLogger(name)
    old_level = logger.getEffectiveLevel()
    logger.setLevel(level)
    try:
        yield logger
    finally:
        logger.setLevel(old_level)
```

Calling logging methods like `debug` on `the` as target produces output because the logging severity level is set low enough in the `with` block on that specific `Logger` instance. Using the `logging` module directly won’t print anything because the default logging severity level for the default program logger is `WARNING` :

在 `with` 块中对 `as` 目标调用像 `debug` 这样的日志方法会产生输出，因为在特定的 `Logger` 实例上的 `with` 块中，日志严重级别设置得足够低。直接使用 `logging` 模块不会打印任何内容，因为默认程序日志记录器的默认日志严重级别是 `WARNING`：

```
with log_level(logging.DEBUG, "my-log") as my_logger:
    my_logger.debug(f"This is a message for {my_logger.name}!")
    logging.debug("This will not print")

>>>
This is a message for my-log!
```

After the `with` statement exits, calling debug logging methods on the `Logger` named `"my-log"` will not print anything because the default logging severity level has been restored automatically. Error log messages will always print:

在 `with` 语句退出后，调用名为 `"my-log"` 的 `Logger` 的调试日志方法不会打印任何内容，因为默认的日志严重级别已经自动恢复。错误日志消息将始终打印：

```
logger = logging.getLogger("my-log")
logger.debug("Debug will not print")
logger.error("Error will print")
>>>
Error will print
```

Later, I can change the name of the logger I want to use by simply updating the `with` statement. This will point the `Logger` that’s the `as` target in the `with` block to a different instance, but I won’t have to update any of my other code to match:

稍后，我可以通过简单地更新 `with` 语句来更改我要使用的日志记录器名称。这会将 `with` 块中的 `Logger` 所指向的实例更改为不同的实例，但我无需更新其他任何代码来匹配：

```
with log_level(logging.DEBUG, "other-log") as my_logger:  # Changed
    my_logger.debug(f"This is a message for {my_logger.name}!")
    logging.debug("This will not print")

>>>
This is a message for other-log!
```

This isolation of state and decoupling between creating a context and acting within that context is another benefit of the `with` statement.

这种状态隔离以及创建上下文和在该上下文中执行之间的解耦是 `with` 语句的另一个好处。

**Things to Remember**
- The `with` statement allows you to reuse logic from `try` / `finally` blocks and reduce visual noise.
- The `contextlib` built-in module provides a `contextmanager` decorator that makes it easy to use your own functions in `with` statements.
- The value yielded by context managers is supplied to the `as` part of the `with` statement. It’s useful for letting your code directly access the cause of the special context.

**注意事项**
- `with` 语句允许您重用 `try` / `finally` 块中的逻辑并减少视觉噪音。
- 内置的 `contextlib` 模块提供了一个 `contextmanager` 装饰器，使得在 `with` 语句中使用自己的函数变得容易。
- 上下文管理器产生的值提供给了 `with` 语句的 `as` 部分。这对于让您的代码直接访问特殊上下文的原因非常有用。