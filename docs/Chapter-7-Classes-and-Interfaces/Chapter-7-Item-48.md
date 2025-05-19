# Chapter 7: Classes and Interfaces (类与接口)

## Item 48: Accept Functions Instead of Classes for Simple Interfaces (对于简单接口，接受函数而不是类)

Many of Python’s built-in APIs allow you to customize behavior by passing in a function. These hooks are used by APIs to call back your code while they execute. For example, the `list` type’s `sort` method takes an optional `key` argument that’s used to determine each index’s value for sorting (see Item 100: “Sort by Complex Criteria Using the key Parameter” for details). Here, I sort a `list` of names based on their lengths by providing the `len` built-in function as the `key` hook:

Python 的许多内置 API 允许您通过传入一个函数来定制行为。这些钩子（hook）被 API 用于在执行过程中回调您的代码。例如，`list` 类型的 `sort` 方法接受一个可选的 `key` 参数，用于确定每个索引值以进行排序（详见条目100：“使用 key 参数按复杂准则排序”）。在这里，我通过提供 `len` 内置函数作为 `key` 钩子，根据名称长度对列表进行排序：

```
names = ["Socrates", "Archimedes", "Plato", "Aristotle"]
names.sort(key=len)
print(names)

>>>
['Plato', 'Socrates', 'Aristotle', 'Archimedes']
```

In other languages, you might expect hooks to be defined by an abstract class. In Python, many hooks are just stateless functions with well-documented arguments and return values. Functions are ideal for hooks because they are easier to describe and simpler to implement than classes. Functions work as hooks because Python has first-class functions: Functions and methods can be passed around and referenced like any other value in the language.

在其他语言中，你可能会期望钩子由抽象类定义。在 Python 中，许多钩子只是具有良好文档记录参数和返回值的无状态函数。函数非常适合用作钩子，因为它们比类更容易描述和实现。函数可以作为钩子使用，因为 Python 拥有一等函数：函数和方法可以像语言中的任何其他值一样传递和引用。

For example, say that I want to customize the behavior of the `defaultdict` class (see Item 27: “Prefer `defaultdict` Over `setdefault` to Handle Missing Items in Internal State” for background). This data structure allows you to supply a function that will be called with no arguments each time a missing key is accessed. The function must return the default value that the missing key should have in the dictionary. Here, I define a hook that logs each time a key is missing and returns `0` for the default value:

例如，假设我想自定义 `defaultdict` 类的行为（有关背景信息，请参见条目27：“优先使用 `defaultdict` 而不是 `setdefault` 来处理内部状态中的缺失项”）。此数据结构允许您提供一个函数，该函数将在每次访问缺失键时被调用而无需参数。该函数必须返回缺失键在字典中应具有的默认值。在这里，我定义了一个钩子，在每次缺少键时会打印一条日志，并为默认值返回 `0`：

```
def log_missing():
    print("Key added")
    return 0
```

Given an initial dictionary and a set of desired increments, I can cause the `log_missing` function to run and print twice (for `'red'` and `'orange'` ):

给定一个初始字典和一组所需的增量值，我可以使 `log_missing` 函数运行并打印两次（针对 `'red'` 和 `'orange'`）：

```
from collections import defaultdict

current = {"green": 12, "blue": 3}
increments = [
    ("red", 5),
    ("blue", 17),
    ("orange", 9),
]
result = defaultdict(log_missing, current)
print("Before:", dict(result))
for key, amount in increments:
    result[key] += amount
print("After: ", dict(result))

>>>
Before: {'green': 12, 'blue': 3}
Key added
Key added
After: {'green': 12, 'blue': 20, 'red': 5, 'orange': 9}
```

Enabling functions like `log_missing` to be supplied helps APIs separate side effects from deterministic behavior. For example, say I now want the default value hook passed to `defaultdict` to count the total number of keys that were missing. One way to achieve this is by using a stateful closure (see Item 33: “Know How Closures Interact with Variable Scope and `nonlocal` ” for details). Here, I define a helper function that uses such a closure as the default value hook:

启用像 `log_missing` 这样的函数被提供有助于 API 将副作用与确定性行为分开。例如，假设我现在希望传递给 `defaultdict` 的默认值钩子能够统计缺失键的总数。一种实现方法是使用有状态的闭包（有关详细信息，请参见条目33：“了解闭包如何与变量作用域及 `nonlocal` 关键字交互”）。在这里，我定义了一个使用此类闭包的帮助函数作为默认值钩子：

```
def increment_with_report(current, increments):
    added_count = 0

    def missing():
        nonlocal added_count  # Stateful closure
        added_count += 1
        return 0

    result = defaultdict(missing, current)
    for key, amount in increments:
        result[key] += amount

    return result, added_count
```

Running this function produces the expected result ( `2` ), even though the `defaultdict` has no idea that the `missing` hook maintains state in the `added_count` closure variable:

运行这个函数会产生预期的结果（`2`），即使 `defaultdict` 不知道 `missing` 钩子在 `added_count` 闭包变量中维护了状态：

```
result, count = increment_with_report(current, increments)
assert count == 2
```

The problem with defining a closure for stateful hooks is that it’s harder to read than the stateless function example. Another approach is to define a small class that encapsulates the state you want to track:

为有状态钩子定义闭包的问题在于它比无状态函数示例更难阅读。另一种方法是定义一个小类来封装您想要跟踪的状态：

```
class CountMissing:
    def __init__(self):
        self.added = 0

    def missing(self):
        self.added += 1
        return 0
```

In other languages, you might expect that now `defaultdict` would have to be modified to accommodate the interface of `CountMissing` . But in Python, thanks to first-class functions, you can reference the `CountMissing.missing` method directly on an object and pass it to `defaultdict` as the default value hook. It’s trivial to have an object
instance’s method satisfy a function interface:

在其他语言中，您可能期望 `defaultdict` 必须修改以适应 `CountMissing` 的接口。但在 Python 中，得益于一等函数，您可以直接引用对象上的 `CountMissing.missing` 方法，并将其作为默认值钩子传递给 `defaultdict`。让一个实例的方法满足函数接口非常简单：

```
counter = CountMissing()
result = defaultdict(counter.missing, current)  # Method ref
for key, amount in increments:
    result[key] += amount
assert counter.added == 2
```

Using a helper class like this to provide the behavior of a stateful closure is clearer than using the `increment_with_report` function, as above. However, in isolation, it’s still not immediately obvious what the purpose of the `CountMissing` class is. Who constructs a `CountMissing` object? Who calls the `missing` method? Will the class need other public methods to be added in the future? Until you see its usage with `defaultdict` , the class is a bit of a mystery.

像这样使用辅助类来提供有状态闭包的行为比使用 `increment_with_report` 函数更清晰，如上所示。然而，单独来看，`CountMissing` 类的目的仍然不是立即显而易见的。谁构建了 `CountMissing` 对象？谁调用了 `missing` 方法？这个类将来是否需要添加其他公共方法？在您看到其与 `defaultdict` 的用法之前，这个类有点神秘。

To clarify this situation, Python classes can define the `__call__` special method. `__call__` allows an `object` to be called just like a function. It also causes the `callable` built-in function to return `True` for such an instance, just like a normal function or method. All objects that can be executed in this manner are referred to as callables:

为了澄清这种情况，Python 类可以定义 `__call__` 特殊方法。`__call__` 允许像调用函数一样调用一个对象。它还会导致 `callable` 内置函数为此类实例返回 `True`，就像正常函数或方法一样。所有可以通过这种方式执行的对象都被称为可调用对象（callable）：

```
class BetterCountMissing:
    def __init__(self):
        self.added = 0

    def __call__(self):
        self.added += 1
        return 0

counter = BetterCountMissing()
assert counter() == 0
assert callable(counter)
```

Here, I use a `BetterCountMissing` instance as the default value hook for a `defaultdict` to track the number of missing keys that were added:

在这里，我将 `BetterCountMissing` 实例作为 `defaultdict` 的默认值钩子使用，以跟踪被添加的缺失键数量：

```
counter = BetterCountMissing()
result = defaultdict(counter, current)  # Relies on __call__
for key, amount in increments:
    result[key] += amount
assert counter.added == 2
```

This is much clearer than the `CountMissing.missing` example. The `__call__` method indicates that a class’s instances will be used somewhere a function argument would also be suitable (like API hooks). It directs new readers of the code to the entry point that’s responsible for the class’s primary behavior. It provides a strong hint that the goal of the class is to act as a stateful closure.

这比 `CountMissing.missing` 示例要清晰得多。`__call__` 方法表明类的实例将在某个地方作为函数参数使用（比如 API 钩子）。它引导代码的新读者前往负责类主要行为的入口点。它强烈暗示该类的目标是作为一个有状态的闭包。

Best of all, `defaultdict` still has no view into what’s going on when you use `__call__` . All that `defaultdict` requires is a callable for the default value hook. Python provides many different ways to satisfy a simple function interface, and you can choose the one that works best for what you need to accomplish.

最重要的是，当您使用 `__call__` 时，`defaultdict` 仍然无法了解幕后发生了什么。`defaultdict` 只要求一个可调用对象作为默认值钩子。Python 提供了许多不同的方式来满足简单的函数接口需求，您可以选择最适合您需求的方式。

**Things to Remember**
- Instead of defining and instantiating classes, you can often simply use functions for simple interfaces between components in Python.
- References to functions and methods in Python are first class, meaning they can be used in expressions (like any other type).
- The `__call__` special method enables instances of a class to be called like plain Python functions and pass `callable` checks.
- When you need a function to maintain state, consider defining a class that provides the `__call__` method instead of implementing a stateful closure function.

 *注意事项**
- 在 Python 中，组件之间的简单接口通常可以直接使用函数，而不必定义和实例化类。
- Python 中对函数和方法的引用是一等公民，这意味着它们可以在表达式中使用（如同任何其他类型）。
- `__call__` 特殊方法使得类的实例可以像普通 Python 函数一样被调用，并能通过 `callable` 检查。
- 当您需要一个函数来维持状态时，请考虑定义一个提供 `__call__` 方法的类，而不是实现一个有状态的闭包函数。