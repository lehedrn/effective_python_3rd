# Chapter 14: Collaboration (协作)

## Item 121: Define a Root `Exception` to Insulate Callers from APIs (定义一个根 `Exception` 以将调用者与 API 隔离)

When you’re defining a module’s API, the exceptions you raise are just as much a part of your interface as the functions and classes you define (see Item 32: “Prefer Raising Exceptions to Returning `None` ” for an example of why).

在定义模块的 API 时，你所引发的异常和你定义的函数及类一样，都是接口的重要组成部分（参见条目 32：“优先使用异常而非返回 `None`”了解为何如此重要）。

Python has a built-in hierarchy of exceptions for the language and standard library (see Item 86: “Understand the Difference Between `Exception` and `BaseException` ” for background). There’s a draw to using the built-in exception types for reporting errors instead of defining your own new types. For example, I could raise a `ValueError` exception whenever an invalid parameter is passed to a function in one of my modules:

Python 为语言本身和标准库提供了一个内建的异常层级结构（参见条目 86：“理解 `Exception` 和 `BaseException` 的区别”）。有一种倾向是直接使用这些内置的异常类型来报告错误，而不是定义自己的新类型。例如，当我的模块中的某个函数收到无效参数时，可以引发一个 `ValueError` 异常：

```
# my_module.py
def determine_weight(volume, density):
    if density <= 0:
        raise ValueError("Density must be positive")

try:
    determine_weight(1, 0)
except ValueError:
    pass
else:
    assert False
```

In some cases, using `ValueError` makes sense, but for APIs, it’s much more powerful to define a new hierarchy of exceptions. I can do this by providing a root `Exception` in my module and having all other exceptions raised by that module inherit from the root exception:

在某些情况下，使用 `ValueError` 是合理的，但对于 API 而言，定义一个新的异常层级更为强大。可以通过在模块中提供一个根 `Exception` 并让该模块引发的所有其他异常继承自这个根异常来实现这一点：

```
# my_module.py
class Error(Exception):
    """Base-class for all exceptions raised by this module."""

class InvalidDensityError(Error):
    """There was a problem with a provided density value."""

class InvalidVolumeError(Error):
    """There was a problem with the provided weight value."""

def determine_weight(volume, density):
    if density < 0:
        raise InvalidDensityError("Density must be positive")
    if volume < 0:
        raise InvalidVolumeError("Volume must be positive")
    if volume == 0:
        density / volume
```

Having a root exception in a module makes it easy for consumers of an API to catch all of the exceptions that were raised deliberately. For example, here a consumer of my API makes a function call with a `try / except` statement that catches my root exception:

在模块中拥有一个根异常，使得 API 消费者能够轻松捕获所有故意引发的异常。例如，API 使用者通过一个带有 `try/except` 语句的函数调用来捕获我定义的根异常：

```
class my_module:
    Error = Error
    InvalidDensityError = InvalidDensityError

    @staticmethod
    def determine_weight(volume, density):
        if density < 0:
            raise InvalidDensityError("Density must be positive")
        if volume < 0:
            raise InvalidVolumeError("Volume must be positive")
        if volume == 0:
            density / volume

try:
    weight = my_module.determine_weight(1, -1)
except my_module.Error:
    logging.exception("Unexpected error")

>>>
Unexpected error
Traceback (most recent call last):
 File ".../example.py", line 3, in <module>
 weight = my_module.determine_weight(1, -1)
 File ".../my_module.py", line 10, in determine_
 raise InvalidDensityError("Density must be po    
 InvalidDensityError: Density must be positive
```

The `logging.exception` function prints the full stack trace of the caught exception so it’s easier to debug in this situation. The `try / except` also prevents my API’s exceptions from propagating too far upward and breaking the calling program. It insulates the calling code from my API. This insulation has three helpful effects.

`logging.exception` 函数会打印捕获异常的完整堆栈跟踪，因此在这种情况下更容易调试。同时，`try/except` 还能防止我的 API 异常向上抛出过多并破坏调用程序。它将调用代码与我的 API 隔离开来。这种隔离有三个有益的效果。

First, root exceptions let callers understand when there’s a problem with their usage of an API. If callers are using my API properly, they should catch the various exceptions that I deliberately raise. If they don’t handle such an exception, it will propagate all the way up to the insulating `except` block that catches my module’s root exception. That block can bring the exception to the attention of the API consumer, providing an opportunity for them to add proper handling of the missed exception type:

首先，根异常可以让调用者明白何时他们的 API 使用存在问题。如果调用者正确使用了我的 API，他们应该捕获我明确引发的各种异常。如果他们没有处理此类异常，它将一直传播到捕获我的模块根异常的隔离 `except` 块。该块可以将异常引起 API 消费者的注意，从而有机会添加对未处理异常类型的适当处理：

```
SENTINEL = object()
weight = SENTINEL
try:
    weight = my_module.determine_weight(-1, 1)
except my_module.InvalidDensityError:
    weight = 0
except my_module.Error:
    logging.exception("Bug in the calling code")

>>>
Bug in the calling code
Traceback (most recent call last):
 File ".../example.py", line 3, in <module>
 weight = my_module.determine_weight(-1, 1)
 File ".../my_module.py", line 12, in determine_
 raise InvalidVolumeError("Volume must be posi
InvalidVolumeError: Volume must be positive
```

The second advantage of using root exceptions is that they can help find bugs in an API module’s code. If my code only deliberately raises exceptions that I define within my module’s hierarchy, then all other types of exceptions raised by my module must be the ones that I didn’t intend to raise. These are bugs in my API’s code.

使用根异常的第二个优势是可以帮助发现 API 模块代码中的 bug。如果我的代码只明确引发我在模块层级中定义的异常，那么我的模块引发的其他类型的异常一定是我无意中引发的。这些是我 API 中的 bug。

Using the `try` / `except` statement above will not insulate API consumers from bugs in my API module’s code. To do that, the caller needs to add another except block that catches Python’s Exception base class (see Item 85: “Beware of Catching the `Exception` Class” for details).

上面的 `try/except` 语句不会将 API 消费者与我 API 中的 bug 隔离开。要做到这一点，调用者需要添加另一个捕获 Python `Exception` 基类的 except 块（详情参见条目 85：“警惕捕获 `Exception` 类”）。

This allows the API consumer to detect when there’s a bug in the API module’s implementation that needs to be fixed. The output for this example includes both the `logging.exception` message and the default interpreter output for the exception since it was re-raised:

这允许 API 消费者检测到 API 模块实现中的 bug 并进行修复。此示例的输出包括 `logging.exception` 消息和解释器默认输出的异常信息，因为它被重新引发：

```
weight = SENTINEL
try:
    weight = my_module.determine_weight(0, 1)
except my_module.InvalidDensityError:
    weight = 0
except my_module.Error:
    logging.exception("Bug in the calling code")
except Exception:
    logging.exception("Bug in the API code!")
    raise  # Re-raise exception to the caller
    
>>>
Bug in the API code!
Traceback (most recent call last):
 File ".../example.py", line 3, in <module>
 weight = my_module.determine_weight(0, 1)
 File ".../my_module.py", line 14, in determine_
 density / volume
 ~~~~~~~~^~~~~~~~
ZeroDivisionError: division by zero
Traceback ...
ZeroDivisionError: division by zero
```

The third impact of using root exceptions is future-proofing an API. Over time, I might want to expand my API to provide more specific exceptions in certain situations. For example, I could add an `Exception` subclass that indicates the error condition of supplying negative densities:

使用根异常的第三个影响是使 API 具备未来扩展性。随着时间推移，我可能希望扩展我的 API 以在特定情况下提供更多具体的异常。例如，我可以添加一个 `Exception` 子类，表示提供了负数密度值的错误情况：

```
# my_module.py
class NegativeDensityError(InvalidDensityError):
    """A provided density value was negative."""


def determine_weight(volume, density):
    if density < 0:
        raise NegativeDensityError("Density must be positive")
```

The calling code will continue to work exactly as before because it already catches `InvalidDensityError` exceptions (the parent class of `NegativeDensityError` ). In the future, the caller could decide to special-case the new type of exception and change the handling behavior accordingly:

调用代码将继续像以前一样工作，因为它已经捕获了 `InvalidDensityError` 异常（`NegativeDensityError` 的父类）。将来，调用者可以选择特殊处理新的异常类型，并相应地更改处理行为：

```
my_module.NegativeDensityError = NegativeDensityError
my_module.determine_weight = determine_weight
try:
    weight = my_module.determine_weight(1, -1)
except my_module.NegativeDensityError:
    raise ValueError("Must supply non-negative density")
except my_module.InvalidDensityError:
    weight = 0
except my_module.Error:
    logging.exception("Bug in the calling code")
except Exception:
    logging.exception("Bug in the API code!")
    raise

>>>
Traceback ...
NegativeDensityError: Density must be positive
The above exception was the direct cause of the f
Traceback ...
ValueError: Must supply non-negative density
```

I can take API future-proofing further by providing a broader set of exceptions directly below the root exception. For example, imagine that that I have one set of errors related to calculating weights, another related to calculating volume, and a third related to calculating density:

我可以进一步通过在根异常下提供更广泛的异常集来进行 API 的未来扩展。例如，假设我有一组与计算重量相关的错误，另一组与计算体积相关，第三组与计算密度相关：

```
# my_module.py
class Error(Exception):
    """Base-class for all exceptions raised by this module."""

class WeightError(Error):
    """Base-class for weight calculation errors."""

class VolumeError(Error):
    """Base-class for volume calculation errors."""

class DensityError(Error):
    """Base-class for density calculation errors."""
```

Specific exceptions would inherit from these general exceptions. Each intermediate exception acts as its own kind of root exception. This makes it easier to insulate layers of calling code from API code based on broad functionality. This is much better than having all callers catch a long list of very specific `Exception` subclasses.

具体异常将从这些一般异常中继承。每个中间异常都充当其自身的根异常。这使得调用代码层可以根据广泛的功能与 API 代码隔离开来。这比要求所有调用者捕获一长串非常具体的 `Exception` 子类要好得多。

**Things to Remember**
- When a module defines a root exception and only raises their child classes, API consumers have a simple way to isolate themselves from unexpected situations encountered by the module.
- Catching root exceptions can help you find bugs in code that consumes an API.
- Catching the Python `Exception` base class can help you find bugs in API implementations.
- Intermediate root exceptions let you raise more specific types of exceptions in the future without breaking API consumers.

**注意事项**
- 当一个模块定义了一个根异常并且仅引发其子类时，API 消费者有简单的方法将自己与模块遇到的意外情况隔离开。
- 捕获根异常可以帮助你找到消费 API 的代码中的 bug。
- 捕获 Python 的 `Exception` 基类可以帮助你找到 API 实现中的 bug。
- 中间根异常让你可以在未来引发更具体的异常类型，而不会破坏 API 消费者。