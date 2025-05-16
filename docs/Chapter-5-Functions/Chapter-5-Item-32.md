# Chapter 5: Functions (函数)

## Item 32: Prefer Raising Exceptions to Returning `None` (优先使用异常而非返回 None)

When writing utility functions, there’s a draw for Python programmers to give special meaning to the return value of `None` . It seems to make sense in some cases (see Item 26: “Prefer get Over in and KeyError to Handle Missing Dictionary Keys”). For example, say I want a helper function that divides one number by another. In the case of dividing by zero, returning `None` seems natural because the result is undefined:

在编写实用函数时，Python 程序员倾向于给返回值 `None` 赋予特殊含义。这在某些情况下似乎合情合理（参见条目26：“处理缺失字典键时优先使用 get 方法而非 in 和 KeyError”）。例如，假设我需要一个辅助函数来将一个数字除以另一个数字。在除以零的情况下，返回 `None` 似乎很自然，因为结果未定义：

```
def careful_divide(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        return None
```

Code using this function can interpret the return value accordingly:

使用此函数的代码可以相应地解释返回值：

```
x, y = 1, 0
result = careful_divide(x, y)
if result is None:
    print("Invalid inputs")
```

What happens with the `careful_divide` function when the numerator is zero? If the denominator is not zero, then the function returns zero. The problem is that a zero return value can cause issues when you evaluate the result in a condition like an if statement. You might accidentally look for any falsey value to indicate errors instead of only looking for None (see Item 4: “Write Helper Functions Instead of Complex Expressions” and Item 7: “Avoid Conditional Expressions in Favor of if Statements”):

当分子为零时，`careful_divide` 函数会发生什么？如果分母不是零，则该函数返回零。问题是，当您在条件语句（如 `if` 语句）中评估返回值时，零返回值可能会导致问题。您可能不小心查找任何假值来指示错误，而不仅仅是查找 `None`（请参见条目4：“用辅助函数代替复杂表达式”和条目7：“避免在 if 语句中使用条件表达式”）：

```
x, y = 0, 5
result = careful_divide(x, y)
if not result:               # Changed
    print("Invalid inputs")  # This runs! But shouldn't
else:
    assert False
>>>
Invalid inputs
```

This misinterpretation of a `False`-equivalent return value is a common mistake in Python code when `None` has special meaning. This is why returning `None` from a function like `careful_divide` is error prone. There are two ways to reduce the chance of such errors.

对 `False` 等效返回值的这种误解是 Python 代码中的常见错误，尤其是在 `None` 具有特殊含义时。这就是为什么从像 `careful_divide` 这样的函数返回 None 容易出错的原因。有两种方法可以减少此类错误的可能性。

The first way is to split the return value into a two-tuple (see Item 31: “Return Dedicated Result Objects Instead of Requiring Function Callers to Unpack More Than Three Variables” for background). The first part of the `tuple` indicates that the operation was a success or failure. The second part is the actual result that was computed:

第一种方法是将返回值拆分为一个二元组（参见条目31：“返回专用的结果对象而不是要求函数调用者解包超过三个变量”）。元组的第一部分表示操作是否成功或失败。第二部分是计算出的实际结果：

```
def careful_divide(a, b):
    try:
        return True, a / b
    except ZeroDivisionError:
        return False, None
```

Callers of this function have to unpack the `tuple` . That forces them to consider the status part of the tuple instead of just looking at the result of division:

该函数的调用者必须解包这个元组。这迫使他们考虑元组的状态部分，而不仅仅是查看除法的结果：

```
success, result = careful_divide(x, y)
if not success:
    print("Invalid inputs")
```

The problem is that callers can easily ignore the first part of the `tuple` (using the underscore variable name, a Python convention for unused variables). The resulting code doesn’t look wrong at first glance, but this can be just as error prone as returning `None` :

问题是，调用者可以轻松忽略元组的第一部分（使用下划线变量名，这是 Python 中未使用变量的约定）。生成的代码乍一看并不错误，但这可能与返回 None 一样容易出错：

```
_, result = careful_divide(x, y)
if not result:
    print("Invalid inputs")
```

The second, better way to reduce these errors is to never return `None` for special cases. Instead, raise an `Exception` up to the caller and have the caller deal with it. Here, I turn a `ZeroDivisionError` into a `ValueError` to indicate to the caller that the input values are bad (see Item 88: “Consider Explicitly Chaining Exceptions to Clarify Tracebacks” and Item 121: “Define a Root `Exception` to Insulate Callers from APIs” for details):

第二种更好的减少这些错误的方法是永远不要为特殊情况返回 `None`。相反，向调用者抛出一个 `Exception`，并让调用者处理它。在这里，我将 `ZeroDivisionError` 转换为 `ValueError`，以指示调用者输入值有问题（有关详细信息，请参见条目88：“考虑显式链接异常以澄清跟踪”和条目121：“定义一个根 Exception 以隔离调用者与 API 的影响”）：

```
def careful_divide(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        raise ValueError("Invalid inputs") # Changed
```

The caller no longer requires a condition on the return value of the function. Instead, it can assume that the return value is always valid and use the results immediately in the `else` block after `try` (see Item 80: “Take Advantage of Each Block in `try / except / else / finally` ” for background):

调用者不再需要对函数的返回值进行条件判断。相反，它可以假设返回值始终有效，并立即在 `try` 之后的 `else` 块中使用结果（有关背景信息，请参见条目80：“充分利用 `try / except / else / finally` 中的每个块”）：

```
x, y = 5, 2
try:
    result = careful_divide(x, y)
except ValueError:
    print("Invalid inputs")
else:
    print(f"Result is {result:.1f}")
>>>
Result is 2.5
```

This approach can be extended to code using type annotations (see Item 124: “Consider Static Analysis via typing to Obviate Bugs” for background). You can specify that a function’s return value will always be a `float` and thus will never be `None` . However, Python’s gradual typing purposefully doesn’t provide a way to indicate when exceptions are part of a function’s interface (also known as checked exceptions). Instead, you have to document the exception-raising behavior and expect callers to rely on that in order to know which `Exceptions` they should plan to catch (see Item 118: “Write Docstrings for Every Function, Class, and Module”). 

这种方法可以扩展到使用类型注解的代码（有关背景，请参见条目124：“考虑通过 typing 进行静态分析以消除 bug”）。您可以指定函数的返回值始终是一个 `float`，因此永远不会是 `None`。但是，Python 的渐进式类型系统有意不提供一种方式来表明异常是函数接口的一部分（也称为检查型异常）。相反，您必须记录引发异常的行为，并期望调用者依赖这一点才能知道哪些 `Exceptions` 他们应该计划捕获（请参见条目118：“为每个函数、类和模块编写文档字符串”）。

Pulling it all together, here’s what this function should look like when using type annotations and docstrings:

综合所有内容，以下是使用类型注解和文档字符串后该函数的样子：

```
def careful_divide(a: float, b: float) -> float:
    """Divides a by b.

    Raises:
        ValueError: When the inputs cannot be divided.
    """
    try:
        return a / b
    except ZeroDivisionError:
        raise ValueError("Invalid inputs")

try:
    result = careful_divide(1, 0)
except ValueError:
    print("Invalid inputs")  # Expected
else:
    print(f"Result is {result:.1f}")
    
>>>
$ python3 -m mypy --strict example.py
Success: no issues found in 1 source file
```

Now the inputs, outputs, and exceptional behavior is clear, and the chance of a caller doing the wrong thing is extremely low.

现在输入、输出和异常行为都很清晰，调用者做错事情的可能性极低。

**Things to Remember**
- Functions that return `None` to indicate special meaning are error prone because `None` and other values (e.g., zero, the empty string) all evaluate to `False` in Boolean expressions.
- Raise exceptions to indicate special situations instead of returning `None` . Expect the calling code to handle exceptions properly when they’re documented.
- Type annotations can be used to make it clear that a function will never return the value `None` , even in special situations.

**注意事项**
- 返回 `None` 以表示特殊含义的函数容易出错，因为在布尔表达式中，`None` 和其他值（例如零、空字符串）都会被求值为 `False`。
- 应使用异常来表示特殊情况，而不是返回 `None`。应在文档中说明应如何正确处理这些异常。
- 类型注解可用于明确表示即使在特殊情况下，函数也不会返回 `None` 值。