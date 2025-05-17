# Chapter 5: Functions

## Item 39: Prefer `functools.partial` over `lambda` Expressions for Glue Functions (优先使用 `functools.partial` 而不是 `lambda` 表达式来编写粘合函数)

Many APIs in Python accept simple functions as part of their interface (see Item 100: “Sort by Complex Criteria Using the `key` Parameter”, Item 27: “Prefer `defaultdict` Over `setdefault` to Handle Missing Items in Internal State”, and Item 24: “Consider `itertools` for Working with Iterators and Generators”). However, these interfaces can cause friction because they might fall short of your needs.

Python 中的许多 API 接受简单函数作为其接口的一部分（参见第100条：“使用 key 参数按复杂标准排序”，第27条：“优先使用 `defaultdict` 而不是 `setdefault` 来处理内部状态中的缺失项”，以及第24条：“考虑使用 `itertools` 处理迭代器和生成器”）。然而，这些接口可能会带来一些不便，因为它们可能无法完全满足你的需求。

For example, the `reduce` function from the `functools` built-in module allows you to calculate one result from a near-limitless iterator of values. Here, I use `reduce` to calculate the sum of many log-scaled numbers (which effectively multiplies them):

例如，`functools` 内置模块中的 `reduce` 函数允许你从一个几乎无限的值迭代器中计算出一个结果。在这里，我使用 `reduce` 来计算多个对数刻度数值的总和（这实际上等于将它们相乘）：

```
import math
import functools

def log_sum(log_total, value):
    log_value = math.log(value)
    return log_total + log_value

result = functools.reduce(log_sum, [10, 20, 40], 0)
print(math.exp(result))

>>>
8000.0
```

The problem is that you don’t always have a function like `log_sum` that exactly matches the function signature required by `reduce` . For example, imagine that you simply had the parameters reversed—since it’s an arbitrary choice anyway—with `value` first and `log_total` second. How could you easily fit this function to the required interface?

问题是，并非总是有一个像 `log_sum` 这样的函数能准确匹配 `reduce` 所需的函数签名。例如，想象一下你只是将参数顺序调换了——毕竟这只是个任意的选择——让 `value` 在前，`log_total` 在后。如何轻松地将这个函数适配到所需的接口？

```
def log_sum_alt(value, log_total):  # Changed
    log_value = math.log(value)
    return log_total + log_value
```

One solution is to define a `lambda` function in an expression to reorder the input arguments to match what’s required by `reduce` :

一个解决方案是定义一个 lambda 函数，在表达式中重新排列输入参数以匹配 reduce 的要求：

```
result = functools.reduce(
    lambda total, value: log_sum_alt(value, total),  # Reordered
    [10, 20, 40],
    0,
)
print(math.exp(result))
```

For one-offs, creating a `lambda` like this is fine. But if you find yourself doing this repeatedly and copying code, it’s worth defining another helper function with reordered arguments that you can call multiple times:

对于一次性操作，创建这样的 `lambda` 是可以的。但如果你发现自己反复这样做并复制代码，那就值得定义另一个具有重新排列参数的帮助函数以便多次调用：

```
def log_sum_for_reduce(total, value):
    return log_sum_alt(value, total)

result = functools.reduce(
    log_sum_for_reduce,
    [10, 20, 40],
    0,
)
print(math.exp(result))
```

Another situation where function interfaces are mismatched is when you need to pass along some additional information for use in processing. For example, say I want to choose the base for the logarithm instead of always using natural log:

函数接口不匹配的另一种情况是你需要传递一些额外的信息用于处理时。例如，假设我想选择对数的底而不是始终使用自然对数：

```
def logn_sum(base, logn_total, value):  # New first parameter
    logn_value = math.log(value, base)
    return logn_total + logn_value
```

In order to pass this function to `reduce` , I need to somehow provide the `base` argument for every call. But `reduce` doesn’t give me a way to do this easily. Again, `lambda` can help here by allowing me to specify one parameter and pass through the rest. Here, I always provide `10` as the first argument to `logn_sum` in order to calculate a base-10 logarithm:

为了将此函数传递给 `reduce`，我需要在每次调用时以某种方式提供 `base` 参数。但 `reduce` 并没有给我一种简便的方式来做到这一点。同样，`lambda` 可以在这里通过指定一个参数并将其余参数传递来帮助解决这个问题。在这里，我始终为 `logn_sum` 提供第一个参数 `10` 以计算以`10`为底的对数：

```
result = functools.reduce(
    lambda total, value: logn_sum(10, total, value),  # Changed
    [10, 20, 40],
    0,
)
print(math.pow(10, result))
>>>
8000.000000000004
```

This pattern of pinning some arguments to specific values while allowing the rest of them to be passed normally is quite common with functional-style code. This technique is often called Currying or partial application. The `functools` built-in module provides the `partial` function to make this easy and more readable. It takes the function to partially apply as the first argument followed by the pinned positional arguments:

这种固定某些参数的值同时允许其余参数正常传递的模式在函数式风格的代码中非常常见。这项技术通常被称为柯里化或部分应用。`functools` 内置模块提供了 `partial` 函数使这种方式更简单且更具可读性。它接受要部分应用的函数作为第一个参数，然后是固定的定位参数：

```
result = functools.reduce(
    functools.partial(logn_sum, 10),  # Changed
    [10, 20, 40],
    0,
)
print(math.pow(10, result))
```

`partial` also allows you to easily pin keyword arguments (see Item 35: “Provide Optional Behavior with Keyword Arguments” and Item 37: “Enforce Clarity with Keyword-Only and Positional-Only Arguments” for background). For example, imagine that the `logn_sum` function accepts `base` as a keyword-only argument, like this:

`partial` 还允许你轻松地固定关键字参数（背景信息请参见第35条：“使用关键字参数提供可选行为” 和第37条：“使用关键字限定和位置限定参数增强清晰度”）。例如，想象一下 `logn_sum` 函数接受 `base` 作为仅限关键字的参数，如下所示：

```
def logn_sum_last(logn_total, value, *, base=10):  # New last parameter
    logn_value = math.log(value, base)
    return logn_total + logn_value
```

Here, I use `partial` to pin the value of `base` to Euler’s number:

在这里，我使用 `partial` 将 `base` 的值固定为欧拉数：

```
import math

log_sum_e = functools.partial(logn_sum_last, base=math.e)  # Pinned `base`
print(log_sum_e(3, math.e**10))
>>>
13.0
```

Achieving the same behavior is possible with a `lambda` expression, but it’s verbose and error-prone:

实现相同的行为是可能的，但使用 lambda 表达式会显得冗长且容易出错：

```
log_sum_e_alt = lambda *a, base=math.e, **kw: logn_sum_last(*a, base=base, **kw)
print(log_sum_e_alt(3, math.e**10))
```

`partial` also allows you to inspect which arguments have already been supplied, and the function being wrapped, which can be helpful for debugging:

`partial` 还允许你检查哪些参数已经被提供，以及被包装的函数，这对于调试可能会有帮助：

```
print(log_sum_e.args, log_sum_e.keywords, log_sum_e.func)
>>>
() {'base': 2.718281828459045} <function logn_sum
0x1033534c0>
```

In general, you should prefer using `partial` when it satisfies your use￾case because of these extra niceties. However, `partial` can’t be used to reorder the parameters altogether, so that’s one situation where `lambda` is preferable.

总的来说，由于这些额外的优点，在你的用例能够满足的情况下，你应该优先使用 `partial`。但是，`partial` 不能用来完全重新排列参数，因此这是其中一个更适合使用 `lambda` 的情况。

In many cases, a `lambda` or `partial` instance is still not enough, especially if you need to access or modify state as part of a simple function interface. Luckily, Python provides additional facilities, including closures, to make this possible (see Item 33: “Know How Closures Interact with Variable Scope and nonlocal ” and Item 48: “Accept Functions Instead of Classes for Simple Interfaces”).

在许多情况下，即使是 `lambda` 或 `partial` 实例仍然不够，特别是如果你需要在简单函数接口中访问或修改状态时。幸运的是，Python 提供了其他功能，包括闭包，使得这种情况成为可能（参见第33条：“了解闭包如何与变量作用域和 nonlocal 交互” 和第48条：“对于简单的接口，接受函数而不是类”）。

**Things to Remember**
- `lambda` expressions can succinctly make two function interfaces compatible by reordering arguments or pinning certain parameter values.
- The `partial` function from the `functools` built-in is a general tool for creating functions with pinned positional and keyword arguments.
- Use `lambda` instead of `partial` if you need to reorder the arguments of a wrapped function.

**注意事项**
- `lambda` 表达式可以通过重新排列参数或固定某些参数值来简洁地使两个函数接口兼容。
- `functools` 内置模块中的 `partial` 函数是一个通用工具，用于创建带有固定位置和关键字参数的函数。
- 如果你需要重新排列被封装函数的参数，请使用 `lambda` 而不是 `partial`。