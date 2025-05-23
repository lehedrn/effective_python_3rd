# Chapter 10: Robustness (健壮性)

## Item 81: `assert` Internal Assumptions and `raise` Missed Expectations (使用 `assert` 验证内部假设，使用 `raise` 报告未满足的期望)

Python includes the `assert` statement, which will raise an `AssertionError` exception at runtime if the given expression is a falsey value (see Item 7: “Avoid Conditional Expressions in Favor of if Statements” for background). For example, here I try to verify that two lists are not empty, and the second assertion fails because the expression is not a truthy value:

Python 包含了 `assert` 语句，如果给定的表达式是一个假值（falsy value），在运行时会引发一个 `AssertionError` 异常（背景信息请参见条目7：“避免在条件表达式中使用if语句”）。例如，这里尝试验证两个列表不为空，第二个断言失败是因为表达式不是一个真值（truthy value）：

```
list_a = [1, 2, 3]
assert list_a, "a empty"
list_b = []
assert list_b, "b empty" # Raises
>>>
Traceback ...
AssertionError: b empty
```

Python also provides the `raise` statement for reporting exceptional conditions to callers (see Item 32: “Prefer Raising Exceptions to Returning `None` ” for when to use it). Here, I use `raise` along with an `if` statement to report the same type of empty list problem:

Python 还提供了 `raise` 语句，用于向调用者报告异常情况（何时使用请参见条目32：“优先抛出异常而不是返回 None”）。在这里，我将 `raise` 与 `if` 语句一起使用来报告同样的空列表问题：

```
class EmptyError(Exception):
    pass
list_c = []
if not list_c:
    raise EmptyError("c empty")
>>>
Traceback ...
EmptyError: c empty
```

The exceptions from `raise` statements can be caught with `try` / `except` statements (see Item 80: “Take Advantage of Each Block in `try` / `except` / `else` / `finally` ”)——this alternative type of control flow is the primary purpose of `raise` :

由 `raise` 语句引发的异常可以使用 `try` / `except` 语句捕获（请参见条目80：“充分利用 `try` / `except` / `else` / `finally` 中的每一个块”）——这种替代类型的控制流是 `raise` 的主要用途：

```
try:
    raise EmptyError("From raise statement")
except EmptyError as e:
    print(f"Caught: {e}")
>>>
Caught: From raise statement
```

But it’s also possible to catch the exceptions from `assert` statements at runtime:

但也可以在运行时捕获由 `assert` 语句引发的异常：

```
try:
    assert False, "From assert statement"
except AssertionError as e:
    print(f"Caught: {e}")
>>>
Caught: From assert statement
```


Why does Python provide two different ways ( `raise` and `assert` ) to report exceptional situations? The reason is that they serve separate roles. 

为什么 Python 提供了两种不同的方式 (`raise` 和 `assert`) 来报告异常情况？原因是它们服务于不同的角色。

Exceptions caused by `raise` statements are considered part of a function’s interface, just like arguments and return values. These exceptions are meant to be caught by calling code and processed accordingly. The potential exceptions a function raises should be in the documentation (see Item 118: “Write Docstrings for Every Function, Class, and Module”) so callers know that they might need to handle them. The behavior of these `raise` statements should also be verified in automated tests (see Item 109: “Prefer Integration Tests Over Unit Tests”). 

由 `raise` 语句引发的异常被视为函数接口的一部分，就像参数和返回值一样。这些异常旨在被调用代码捕获并相应地进行处理。函数可能引发的潜在异常应该包含在文档中（请参见条目118：“为每个函数、类和模块编写文档字符串”），以便调用者知道可能需要处理它们。这些 `raise` 语句的行为还应在自动化测试中得到验证（请参见条目109：“优先集成测试而非单元测试”）。

Exceptions caused by `assert` statements are not meant to be caught by callers of a function. They’re used to verify assumptions in an implementation that might not be obvious to new readers of the code. Assertions are self-documenting because they evaluate the second expression (after the comma) to create a debugging error message when the condition fails. These messages can be used by error reporting and logging facilities higher in the call stack to help developers find and fix bugs (see Item 87: “Use `traceback` for Enhanced Exception Reporting” for an example).

由 `assert` 语句引发的异常并不打算被函数的调用者捕获。它们用于验证实现中的假设，这些假设对代码的新读者可能并不明显。断言具有自我记录功能，因为它们评估第二个表达式（逗号后的表达式），当条件失败时生成调试错误消息。这些消息可以被更高层的错误报告和日志设施使用，以帮助开发人员查找和修复错误（例如，请参见条目87：“使用 `traceback` 增强异常报告”）。

Code that implements identical functionality might use `assert` statements, `raise` statements, or both, depending on the context in which it’s being used. For example, here I define a simple class that can be used to aggregate movie ratings. It provides a robust API that validates input and reports any problems to the caller using `raise` :

根据上下文的不同，实现相同功能的代码可能会使用 `assert` 语句、`raise` 语句或两者兼有。例如，这里定义了一个简单的类，可用于聚合电影评分。它提供了一个稳健的API，使用 `raise` 对输入进行验证并报告任何问题给调用者：

```
class RatingError(Exception):
    pass

class Rating:
    def __init__(self, max_rating):
        if not (max_rating > 0):
            raise RatingError("Invalid max_rating")
        self.max_rating = max_rating
        self.ratings = []

    def rate(self, rating):
        if not (0 < rating <= self.max_rating):
            raise RatingError("Invalid rating")
        self.ratings.append(rating)
```

The exceptions that this class raises are meant to be caught and, presumably, reported back to the end-user or API caller who sent the invalid input:

此类引发的异常旨在被捕获，并且很可能会被报告回发送无效输入的最终用户或API调用者：

```
movie = Rating(5)
movie.rate(5)
movie.rate(7) # Raises
>>>
Traceback ...
RatingError: Invalid rating
```

Here’s another implementation of the same functionality, but this version is not meant to report errors to the caller. Instead, this class assumes that other parts of the program have already done the necessary validation:

这里是相同功能的另一个实现版本，但此版本不打算向调用者报告错误。相反，此类假设程序的其他部分已经完成了必要的验证：

```
class RatingInternal:
    def __init__(self, max_rating):
        assert max_rating > 0, f"Invalid {max_rating=}"
        self.max_rating = max_rating
        self.ratings = []

    def rate(self, rating):
        assert 0 < rating <= self.max_rating, f"Invalid {rating=}"
        self.ratings.append(rating)
```

When an `assert` statement in this class raises an exception, it’s meant to report a bug in the code. The message should include information that can be used by the programmer later to find the cause and fix it:

当此类中的 `assert` 语句引发异常时，其目的是报告代码中的错误。消息应包含程序员日后查找原因和修复所需的信息：

```
movie = RatingInternal(5)
movie.rate(5)
movie.rate(7) # Raises
>>>
Traceback ...
AssertionError: Invalid rating=7
```

For assertions like this to be useful, it’s critical that calling code does not catch and silence `AssertionError` or `Exception` exceptions (see Item 85: “Beware of Catching the `Exception` Class”).

为了使这样的断言有用，关键在于调用代码不要捕获并抑制 `AssertionError` 或 `Exception` 异常（请参见条目85：“警惕捕获 `Exception` 类”）。

Ultimately, it’s on you to decide whether `raise` or `assert` will be the most appropriate choice. As the complexity of a Python program grows, the layers of interconnected functions, classes, and modules begin to take shape. Some of these systems are more externally-facing APIs: library functions and interfaces meant to be leveraged by other components. There, `raise` will be most useful (see Item 121: “Define a Root `Exception` to Insulate Callers from APIs”). Other pieces of code are internally-facing and only help one part of the program implement larger requirements. In these cases, `assert` is the way to go—just make sure you don’t disable assertions (see Item 90: “Never Set `__debug__` to False ”).

最终，决定使用 `raise` 还是 `assert` 是最合适的，这取决于你。随着Python程序复杂性的增长，互连的函数、类和模块的层次结构开始形成。其中一些系统更多是面向外部的API：旨在被其他组件利用的库函数和接口。在那里，`raise` 最为有用（请参见条目121：“定义一个根 `Exception` 来保护调用者免受API的影响”）。其他代码片段则是面向内部的，仅帮助程序的一个部分实现更大的需求。在这种情况下，使用 `assert` 是正确的选择——只需确保不要禁用断言（请参见条目90：“永远不要将 `__debug__` 设置为 False”）。

**Things to Remember**

- The `raise` statement can be used to report expected error conditions back to the callers of a function.
- The exceptions that a function directly raises are part of its explicit interface, and should be documented accordingly.
- The `assert` statement should be used to verify the programmer’s assumptions in the code and convey them to other readers of the implementation.
- Failed assertions are not part of the explicit interface of a function, and should not be caught by callers.

**注意事项**

- `raise` 语句可用于将预期的错误情况报告给函数的调用者。
- 函数直接引发的异常是其显式接口的一部分，应相应地进行文档化。
- 应使用 `assert` 语句来验证程序员在代码中的假设，并将其传达给代码实现的其他阅读者。
- 失败的断言不属于函数的显式接口，不应被调用者捕获。