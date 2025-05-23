# Chapter 10: Robustness (健壮性)

## Item 86: Understand the Difference Between `Exception` and `BaseException` (理解 `Exception` 和 `BaseException` 的区别)

Python documentation will tell you that programmer-defined exception classes must inherit from the `Exception` class. But the root of the exception tree in Python is actually `BaseException` , which is the parent class of `Exception` . Branching off from `BaseException` are other exception classes that Python uses for its own internal purposes.

Python文档会告诉你，程序员定义的异常类必须继承自 `Exception` 类。但实际上，Python中异常体系的根类是 `BaseException`，而 `Exception` 是它的子类。从 `BaseException` 派生出的其他异常类是Python用于自身内部用途的。

For example, when a user presses the Control-C key combination while a Python program runs, they expect to interrupt the running program and cause it to terminate. The precise way Python accomplishes this is platform dependent, but ultimately the interpreter runtime converts the interrupt signal into a `KeyboardInterrupt` exception and raises it in the program’s main thread. KeyboardInterrupt does not inherit from `Exception` , which means that it should bypass exception handlers all the way up to the entry point of the program and cause it to exit with an error message. Here, I show this behavior in action by exiting an infinite loop even though it catches the `Exception` class:

例如，当用户在一个Python程序运行时按下Control-C组合键，他们期望中断正在运行的程序并导致其终止。Python实现这种中断的具体方式依赖于平台，但最终解释器运行时会将中断信号转换为一个 `KeyboardInterrupt` 异常，并在程序的主线程中抛出。`KeyboardInterrupt` 并不继承自 `Exception`，这意味着它应该绕过所有异常处理程序，一直上溯到程序的入口点并导致程序退出并显示错误消息。下面的例子展示了这种行为，即使循环捕获了 `Exception` 类也会被中断：

```
def do_processing():
    raise KeyboardInterrupt

def main(argv):
    while True:
        try:
            do_processing()  # Interrupted
        except Exception as e:
            print("Error:", type(e), e)

    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))

>>>
Traceback ...
KeyboardInterrupt
```

Knowing this is possible, I might choose to catch the `BaseException` class so I can always do clean-up before program termination, such as flushing open files to disk to ensure they’re not corrupted. In other situations, catching a broad class of exceptions like this can be useful for insulating components against potential errors and providing resilient APIs (see Item 85: “Beware of Catching the `Exception` Class” and Item 121: “Define a Root `Exception` to Insulate Callers from APIs”). I can return
`1` at the end of the exception handler to indicate that the program should exit with an error code:

了解了这一点后，我可能会选择捕获 `BaseException` 类以便在程序终止前进行清理操作，比如刷新打开的文件以确保它们不会损坏。在其他情况下，捕获广泛的异常类对于隔离潜在错误和提供弹性API（参见条目85：“警惕捕获 `Exception` 类” 和 条目121：“定义一个根 `Exception` 以隔离调用者与APIs”）也是有用的。可以在异常处理程序的末尾返回 `1` 以指示程序应以错误代码退出：

```
with open("my_data.csv", "w") as f:
    f.write("file exists")

def do_processing(handle):
    raise KeyboardInterrupt

def main(argv):
    data_path = argv[1]
    handle = open(data_path, "w+")

    while True:
        try:
            do_processing(handle)
        except Exception as e:
            print("Error:", type(e), e)
        except BaseException:
            print("Cleaning up interrupt")
            handle.flush()
            handle.close()
            return 1

    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
    
>>>
Cleaning up interrupt
Traceback ...
SystemExit: 1
```

The problem is that there are other exception types that also inherit from `BaseException` , including `SystemExit` (caused by the `sys.exit` built-in function) and `GeneratorExit` (see Item 89: “Always Pass Resources into Generators and Have Callers Clean Them Up Outside”). Python might add more in the future as well. Python treats these exceptions as mechanisms for executing desired behavior instead of reporting error conditions, which is why they’re in a separate part of the class hierarchy. The runtime relies on users generally not catching these exceptions in order to work properly; if you catch them you might inadvertently cause harmful side-effects in a program.

问题是还有其他一些异常类型也继承自 `BaseException`，包括 `SystemExit`（由 `sys.exit` 内建函数引起）和 `GeneratorExit`（参见条目89：“始终将资源传递给生成器并在外部由调用者清理”）。Python将来可能还会添加更多的类型。Python将这些异常视为执行所需行为的机制而不是报告错误条件，这就是为什么它们位于类层次结构的不同部分的原因。运行时依赖于用户通常不捕获这些异常以正常工作；如果你捕获它们，可能会无意中在程序中造成有害的副作用。

Thus, if you want to achieve this type of clean-up behavior, it’s better to use constructs like `try` / `finally` statements (see Item 80: “Take Advantage of Each Block in `try` / `except` / `else` / `finally` ”) and with statements (see Item 82: “Consider contextlib and with Statements for Reusable `try` / `finally` Behavior”). These will ensure that the cleanup methods run regardless of whether the exception raised inherits from `Exception` or `BaseException` :

因此，如果你想实现这种类型的清理行为，最好使用像 `try` / `finally` 语句（参见条目80：“充分利用 `try` / `except` / `else` / `finally` 中的每个块”）和 with 语句（参见条目82：“考虑使用 contextlib 和 with 语句以实现可重用的 `try` / `finally` 行为”）这样的构造。这些将确保无论引发的异常是从 `Exception` 还是 `BaseException` 继承的，清理方法都会运行：

```
 def do_processing(handle):
    raise KeyboardInterrupt

def main(argv):
    data_path = argv[1]
    handle = open(data_path, "w+")

    try:
        while True:
            try:
                do_processing(handle)
            except Exception as e:
                print("Error:", type(e), e)
    finally:
        print("Cleaning up finally")  # Always runs
        handle.flush()
        handle.close()

if __name__ == "__main__":
    sys.exit(main(sys.argv))

>>>
Cleaning up finally
Traceback ...
KeyboardInterrupt
```

If for some reason you really must catch and handle a direct child class of `BaseException` , it’s important to propagate the error correctly so other code higher up in the call stack will still receive it. For example, I might catch `KeyboardInterrupt` exceptions and ask the user to confirm their intention to terminate the program. Here, I use a bare `raise` at the end of the exception handler to ensure the exception continues normally without modifications to its traceback (see Item 87: “Use traceback for Enhanced Exception Reporting” for background):

如果出于某些原因你真的必须捕获和处理直接继承自 `BaseException` 的异常类，那么重要的是要正确传播错误，以便调用栈更高层的代码仍能接收到它。例如，我可以捕获 `KeyboardInterrupt` 异常并要求用户确认他们是否想终止程序。在这里，我在异常处理程序的末尾使用了一个裸 `raise` 以确保异常继续正常而不修改其回溯信息（参见条目87：“使用 traceback 获取增强的异常报告”）：

```
def do_processing():
    raise KeyboardInterrupt

def input(prompt):
    print(f"{prompt}y")
    return "y"

def main(argv):
    while True:
        try:
            do_processing()
        except Exception as e:
            print("Error:", type(e), e)
        except KeyboardInterrupt:
            found = input("Terminate? [y/n]: ")
            if found == "y":
                raise  # Propagate the error

if __name__ == "__main__":
    sys.exit(main(sys.argv))

>>>
Terminate? [y/n]: y
Traceback ...
KeyboardInterrupt
```

Another situation where you might decide to catch `BaseException` is for enhanced logging utilities (see Item 87: “Use `traceback` for Enhanced Exception Reporting” for a related use-case). For example, I can define a function decorator that logs all inputs and outputs, including raised `Exception` subclass values (see Item 38: “Define Function Decorators with `functools.wraps` ” for background):

另一个你可能决定捕获 `BaseException` 的情况是为了增强日志记录工具（参见条目87：“使用 `traceback` 获取增强的异常报告”）。例如，我可以定义一个函数装饰器，记录所有输入和输出，包括引发的 `Exception` 子类值（参见条目38：“使用 `functools.wraps` 定义函数装饰器”）：

```
import functools

def log(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            result = e
            raise
        finally:
            print(
                f"Called {func.__name__}"
                f"(*{args!r}, **{kwargs!r}) "
                f"got {result!r}"
            )

    return wrapper
```

Calling a function decorated with log will print everything as expected:

调用用log装饰的函数将会按预期打印一切内容：

```
@log
def my_func(x):
    x / 0

my_func(123)

>>>
Called my_func(*(123,), **{}) got ZeroDivisionError
Traceback ...
ZeroDivisionError: division by zero
```

However, if the exception that’s raised inherits from `BaseException` instead of `Exception` , the decorator will break and cause unexpected errors:

然而，如果引发的异常继承自 `BaseException` 而不是 `Exception`，装饰器将会失效并导致意外错误：

```
@log
def other_func(x):
    if x > 0:
        sys.exit(1)
other_func(456)

>>>
Traceback ...
SystemExit: 1
The above exception was the direct cause of the f
exception:
Traceback ...
UnboundLocalError: cannot access local variable 
is not associated with a value
```

It might seem counter-intuitive, but the `finally` clause will run even in cases where there are no `except` clauses present or none of the provided `except` clauses actually match the exception value that was raised (see Item 84: “Beware of Exception Variables Disappearing” for another example). In the case above, that’s exactly what happened: `SystemExit` is not a subclass of `Exception` , thus that handler never ran and `result` was not assigned before the call to `print` in the `finally` clause. Simply catching `BaseException` instead of `Exception` solves the problem:

这似乎违反直觉，但在没有 `except` 子句存在或提供的任何 `except` 子句实际上不匹配所引发的异常值的情况下，`finally` 子句仍将运行（参见条目84：“警惕异常变量消失”中的另一个示例）。在上面的情况中，正是发生了这种情况：`SystemExit` 不是 `Exception` 的子类，因此该处理程序从未运行，且在调用 `print` 前 `result` 未被赋值。只需捕获 `BaseException` 而不是 `Exception` 即可解决此问题：

```
def fixed_log(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except BaseException as e:  # Fixed
            result = e
            raise
        finally:
            print(
                f"Called {func.__name__}"
                f"(*{args!r}, **{kwargs!r}) "
                f"got {result!r}"
            )

    return wrapper
```

Now the decorator works as expected for `SystemExit` :

现在装饰器对 `SystemExit` 也能按预期工作：

```
@fixed_log
def other_func(x):
    if x > 0:
        sys.exit(1)

other_func(456)
>>>
Called other_func(*(456,), **{}) got SystemExit(1
Traceback ...
SystemExit: 1
```

Handling `BaseException` and related classes can be useful, but it’s also quite tricky, so it’s important to pay close attention to the details and be careful.

处理 `BaseException` 及相关类可能是有用的，但也相当棘手，因此注意细节并小心行事非常重要。

**Things to Remember**

- For internal behaviors, Python sometimes raises `BaseException` child classes, which will skip `except` clauses that only handle the `Exception` base class.
- `try` / `finally` statements, `with` statements, and similar constructs properly handle raised `BaseException` child classes without extra effort.
- There are legitimate reasons to catch `BaseException` and related classes, but doing so can be error prone.

**注意事项**

- 对于内部行为，Python有时会抛出 `BaseException` 子类，这将跳过仅处理 `Exception` 基类的 `except` 子句。
- `try` / `finally` 语句、`with` 语句及类似结构可以正确处理抛出的 `BaseException` 子类，无需额外努力。
- 有正当理由捕获 `BaseException` 及相关类，但这样做可能会容易出错。