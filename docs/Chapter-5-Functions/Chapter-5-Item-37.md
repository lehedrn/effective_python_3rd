# Chapter 5: Functions (函数)

## Item 37: Enforce Clarity with Keyword-Only and Positional-Only Arguments (通过关键字限定和位置限定参数来强制清晰性)

Passing arguments by keyword is a powerful feature of Python functions (see Item 35: “Provide Optional Behavior with Keyword Arguments”). The flexibility of keyword arguments enables you to write functions that will be clear to new readers of your code for many use cases. 

按关键字传递参数是 Python 函数的强大特性（参见条目 35：“使用关键字参数提供可选行为”）。关键字参数的灵活性使您能够编写对许多用例都清晰明了的函数。

For example, say that I want to divide one number by another while being very careful about special cases. Sometimes, I want to ignore `ZeroDivisionError` exceptions and return infinity instead. Other times, I want to ignore OverflowError exceptions and return zero instead. Here, I define a function with these options:

例如，假设我想要将一个数字除以另一个数字，同时非常小心地处理特殊情况。有时，我想忽略 `ZeroDivisionError` 异常并返回无穷大。其他时候，我想忽略 `OverflowError` 异常并返回零。在这里，我定义了一个具有这些选项的函数：

```
def safe_division(
    number,
    divisor,
    ignore_overflow,
    ignore_zero_division,
):
    try:
        return number / divisor
    except OverflowError:
        if ignore_overflow:
            return 0
        else:
            raise
    except ZeroDivisionError:
        if ignore_zero_division:
            return float("inf")
        else:
            raise
```

Using this function is straightforward. This call ignores the `float` overflow from division and returns zero:

使用这个函数是很直接的。以下调用忽略了除法中的浮点溢出，并返回零：

```
result = safe_division(1.0, 10**500, True, False)
print(result)
>>>
0
```

This call ignores the error from dividing by zero and returns infinity:

这次调用忽略了除以零的错误，并返回无穷大：

```
result = safe_division(1.0, 0, False, True)
print(result)
>>>
inf
```

The problem is that it’s easy to confuse the position of the two Boolean arguments that control the exception handling behavior. This can easily cause bugs that are hard to track down. One way to improve the readability of this code is to use keyword arguments. Using default keyword arguments (see Item 36: “Use None and Docstrings to Specify Dynamic Default Arguments”), the function can be overly cautious and can always re-raise exceptions:

问题是，很容易混淆控制异常处理行为的两个布尔参数的位置。这可能导致难以追踪的 bug。改进这段代码可读性的一种方法是使用关键字参数。使用默认关键字参数（参见条目 36：“使用 None 和文档字符串指定动态默认参数”），函数可以过于谨慎，并且总是重新引发异常：

```
def safe_division_b(
    number,
    divisor,
    ignore_overflow=False,       # Changed
    ignore_zero_division=False,  # Changed
):
    try:
        return number / divisor
    except OverflowError:
        if ignore_overflow:
            return 0
        else:
            raise
    except ZeroDivisionError:
        if ignore_zero_division:
            return float("inf")
        else:
            raise
```

Then, callers can use keyword arguments to specify which of the ignore flags they want to set for specific operations, overriding the default behavior:

然后，调用者可以使用关键字参数来指定他们希望为特定操作设置哪些忽略标志，覆盖默认行为：

```
result = safe_division_b(1.0, 10**500, ignore_overflow=True)
print(result)

result = safe_division_b(1.0, 0, ignore_zero_division=True)
print(result)

>>>
0
inf
```

The problem is, since these keyword arguments are optional behavior, there’s nothing forcing callers of your functions to use keyword arguments for clarity. Even with the new definition of safe_division_b , I can still call it the old way with positional arguments:

问题是，由于这些关键字参数是可选行为，没有什么强制调用者在您的函数中使用关键字参数以提高清晰度。即使有了 `safe_division_b` 的新定义，我仍然可以用位置参数旧方式调用它：

```
assert safe_division_b(1.0, 10**500, True, False) == 0
```

With complex functions like this, it’s better to require that callers are clear about their intentions by defining your functions with keyword-only arguments. These arguments can only be supplied by keyword, never by position.

对于像这样的复杂函数，最好要求调用者明确他们的意图，通过定义只接受关键字参数的函数。这些参数只能通过关键字提供，而不能通过位置提供。

Here, I redefine the `safe_division` function to accept keyword-only arguments. The `*` symbol in the argument list indicates the end of positional arguments and the beginning of keyword-only arguments ( *args has the same effect; see Item 34: “Reduce Visual Noise with Variable Positional Arguments”):

这里，我重新定义了 `safe_division` 函数以接受仅关键字参数。参数列表中的 `*` 符号表示位置参数的结束和仅关键字参数的开始（`*args` 有相同的效果；参见条目 34：“使用变量位置参数减少视觉噪音”）：

```
def safe_division_c(
    number,
    divisor,
    *,  # Added
    ignore_overflow=False,
    ignore_zero_division=False,
):
    try:
        return number / divisor
    except OverflowError:
        if ignore_overflow:
            return 0
        else:
            raise
    except ZeroDivisionError:
        if ignore_zero_division:
            return float("inf")
        else:
            raise
```

Now, calling the function with positional arguments that correspond to the keyword arguments won’t work:

现在，用对应关键字参数的位置参数调用该函数将不起作用：

```
safe_division_c(1.0, 10**500, True, False)
>>>
Traceback ...
TypeError: safe_division_c() takes 2 positional arguments but 4 were given
```

But keyword arguments and their default values will work as expected (ignoring an exception in one case and raising it in another):

但关键字参数及其默认值将如预期般工作（在一个情况下忽略异常，在另一个情况下引发异常）：

```
tresult = safe_division_c(1.0, 0, ignore_zero_division=True)
assert result == float("inf")

try:
    result = safe_division_c(1.0, 0)
except ZeroDivisionError:
    pass  # Expected
```

However, a problem still remains with the `safe_division_c` version of this function: Callers may specify the first two required arguments ( `number` and `divisor` ) with a mix of positions and keywords:

然而，`safe_division_c` 版本的函数仍存在一个问题：调用者可能使用混合位置和关键字来指定前两个必需参数（number 和 divisor）：

```
assert safe_division_c(number=2, divisor=5) == 0.4
assert safe_division_c(divisor=5, number=2) == 0.4
assert safe_division_c(2, divisor=5) == 0.4
```

Later, I may decide to change the names of these first two arguments because of expanding needs or even just because my style preferences change:

之后，我可能会因为扩展需求甚至只是风格偏好的改变而决定更改这两个参数的名称：

```
def safe_division_d(
    numerator,    # Changed
    denominator,  # Changed
    *,
    ignore_overflow=False,
    ignore_zero_division=False
):
    try:
        return numerator / denominator
    except OverflowError:
        if ignore_overflow:
            return 0
        else:
            raise
    except ZeroDivisionError:
        if ignore_zero_division:
            return float("inf")
        else:
            raise

```

Unfortunately, this seemingly superficial change breaks all of the existing callers that specified the `number` or `divisor` arguments using keywords:

不幸的是，这种看似表面的变化破坏了所有显式使用关键字指定 `number` 或 `divisor` 参数的现有调用者：

```
safe_division_d(number=2, divisor=5)
>>>
Traceback ...
TypeError: safe_division_d() got an unexpected ke
'number'
```

This is especially problematic because I never intended for the keywords `number` and `divisor` to be part of an explicit interface for this function. These were just convenient parameter names that I chose for the implementation, and I didn’t expect anyone to rely on them explicitly.

这尤其成问题，因为我从未打算让 `number` 和 `divisor` 关键字成为此函数显式接口的一部分。这些只是我在实现中选择的方便的参数名，我没有预料到有人会依赖它们显式地使用。

Python 3.8 introduces a solution to this problem, called positional-only arguments. These arguments can be supplied only by position and never by keyword (the opposite of the keyword-only arguments demonstrated above).

Python 3.8 引入了解决这个问题的方法，称为位置限定参数。这些参数只能通过位置提供，而不能通过关键字（与上面演示的关键字限定参数相反）。

Here, I redefine the `safe_division` function to use positional-only arguments for the first two required parameters. The `/` symbol in the argument list indicates where positional-only arguments end:

在此，我重新定义了 `safe_division` 函数以在前两个必需参数中使用位置限定参数。参数列表中的 `/` 符号指示位置限定参数的结束位置：

```
def safe_division_e(
    numerator,
    denominator,
    /,  # Added
    *,
    ignore_overflow=False,
    ignore_zero_division=False,
):
    try:
        return numerator / denominator
    except OverflowError:
        if ignore_overflow:
            return 0
        else:
            raise
    except ZeroDivisionError:
        if ignore_zero_division:
            return float("inf")
        else:
            raise
```

I can verify that this function works when the required arguments are provided positionally:

我可以验证当必需参数通过位置提供时此函数的工作情况：

```
assert safe_division_e(2, 5) == 0.4
```

But an exception is raised if keywords are used for the positional-only parameters:

但如果通过关键字使用位置限定参数，则会引发异常：

```
safe_division_e(numerator=2, denominator=5)
>>>
Traceback ...
TypeError: safe_division_e() got some positional-only arguments passed as keyword arguments: 'numerator, denominator'
```

Now, I can be sure that the first two required positional arguments in the definition of the `safe_division_e` function are decoupled from callers. I won’t break anyone if I change the parameters’ names again.

现在，我可以确定在 `safe_division_e` 函数定义中的前两个必需的位置参数与调用者解耦。如果我再次更改参数名称，也不会影响任何人。

One notable consequence of keyword- and positional-only arguments is that any parameter name between the `/` and `*` symbols in the argument list may be passed either by position or by keyword (which is the default for all function arguments in Python). Depending on your API’s style and needs, allowing both argument passing styles can increase readability and reduce noise. For example, here I’ve added another optional parameter to `safe_division` that allows callers to specify how many digits to use in rounding the result:

关键字限定和位置限定参数的一个显著后果是，参数列表中 `/` 和 `*` 符号之间的任何参数名称都可以通过位置或关键字传递（这是 Python 中所有函数参数的默认行为）。根据您的 API 风格和需求，允许两种参数传递方式可以提高可读性并减少噪音。例如，这里我向 `safe_division` 添加了另一个可选参数，允许调用者指定结果舍入时使用的位数：

```
def safe_division_f(
    numerator,
    denominator,
    /,
    ndigits=10,  # Changed
    *,
    ignore_overflow=False,
    ignore_zero_division=False,
):
    try:
        fraction = numerator / denominator  # Changed
        return round(fraction, ndigits)     # Changed
    except OverflowError:
        if ignore_overflow:
            return 0
        else:
            raise
    except ZeroDivisionError:
        if ignore_zero_division:
            return float("inf")
        else:
            raise
```

Now, I can call this new version of the function in all of these different ways, since `ndigits` is an optional parameter that may be passed either by position or by keyword:

现在，我可以以所有这些不同的方式调用这个新版本的函数，因为 `ndigits` 是一个可以通过位置或关键字传递的可选参数：

```
result = safe_division_f(22, 7)
print(result)
result = safe_division_f(22, 7, 5)
print(result)
result = safe_division_f(22, 7, ndigits=2)
print(result)
>>>
3.1428571429
3.14286
3.14
```

**Things to Remember**
- Keyword-only arguments force callers to supply certain arguments by keyword (instead of by position), which makes the intention of a function call clearer. Keyword-only arguments are defined after a `*` in the argument list (whether on its own or part of variable arguments like `*args` ).
- Positional-only arguments ensure that callers can’t supply certain parameters using keywords, which helps reduce coupling. Positional-only arguments are defined before a single `/` in the argument list.
- Parameters between the `/` and `*` characters in the argument list may be supplied by position or keyword, which is the default for Python parameters.

**注意事项**
- 关键字限定参数迫使调用者必须通过关键字（而不是位置）提供某些参数，这使得函数调用的意图更加清晰。关键字限定参数在参数列表中 `*` 之后定义（无论它是单独的还是像 `*args `这样的变量参数的一部分）。
- 位置限定参数确保调用者无法使用关键字提供某些参数，这有助于减少耦合。位置限定参数在参数列表中的单个 `/` 之前定义。
- 参数列表中 `/` 和 `*` 字符之间的任何参数都可以通过位置或关键字提供，这是 Python 参数的默认行为。