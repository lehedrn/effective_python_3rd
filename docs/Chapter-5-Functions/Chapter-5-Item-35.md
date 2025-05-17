# Chapter 5: Functions (函数)

## Item 35: Provide Optional Behavior with Keyword Arguments (使用关键字参数提供可选行为)

As in most other programming languages, in Python you may pass arguments by position when calling a function:

和大多数其他编程语言一样，在 Python 中调用函数时可以通过位置传递参数：

```
def remainder(number, divisor):
    return number % divisor
assert remainder(20, 7) == 6
```

All normal arguments to Python functions can also be passed by keyword, where the name of the argument is used in an assignment within the parentheses of a function call. Keyword arguments can be passed in any order as long as all of the required positional arguments are specified. You can mix and match keyword and positional arguments. These calls are equivalent:

所有常规的 Python 函数参数也可以通过关键字进行传递，即在函数调用的括号内使用参数名进行赋值。只要指定了所有必需的位置参数，关键字参数可以以任何顺序传递。你也可以混合使用关键字和位置参数。以下这些调用是等价的：

```
remainder(20, 7)
remainder(20, divisor=7)
remainder(number=20, divisor=7)
remainder(divisor=7, number=20)
```

Positional arguments must be specified before keyword arguments:

位置参数必须在关键字参数之前指定：

```
remainder(number=20, 7)
>>>
Traceback ...
SyntaxError: positional argument follows keyword argument
```

Each argument can be specified only once:

每个参数只能被指定一次：

```
remainder(20, number=7)
>>>
Traceback ...
TypeError: remainder() got multiple values for argument 'number'
```

If you already have a dictionary object, and you want to use its contents to call a function like `remainder` , you can do this by using the `**` operator. This instructs Python to pass the key-value pairs from the dictionary as the corresponding keyword arguments of the function:

如果你已经有一个字典对象，并且想用它的内容来调用像 `remainder` 这样的函数，你可以使用 `**` 操作符来实现这一点。这会指示 Python 将字典中的键-值对作为相应的关键字参数传递给函数：

```
my_kwargs = {
 "number": 20,
 "divisor": 7,
}
assert remainder(**my_kwargs) == 6
```

You can mix the `**` operator with positional arguments or keyword arguments in the function call, as long as no argument is repeated:

你可以在函数调用中将 ** 操作符与位置参数或关键字参数混合使用，只要不重复任何参数即可：

```
my_kwargs = {
    "divisor": 7,
}
assert remainder(number=20, **my_kwargs) == 6
```

You can also use the `**` operator multiple times if you know that the dictionaries don’t contain overlapping keys:

如果你知道多个字典没有重叠的键，你也可以多次使用 ** 操作符：

```
my_kwargs = {
    "number": 20,
}
other_kwargs = {
    "divisor": 7,
}
assert remainder(**my_kwargs, **other_kwargs) == 6
```

And if you’d like for a function to receive any named keyword argument, you can use the `**kwargs` catch-all parameter to collect those arguments into a `dict` that you can then process (see Item 38: “Define Function Decorators with functools.wraps ” for when this is especially useful):

如果你想让一个函数接收任何命名的关键字参数，你可以使用 `**kwargs` 捕获所有参数，将其收集到一个 `dict` 中以便后续处理（参见第 38 条：“使用 functools.wraps 定义函数装饰器”了解特别有用的情况）：

```
def print_parameters(**kwargs):
    for key, value in kwargs.items():
        print(f"{key} = {value}")

print_parameters(alpha=1.5, beta=9, gamma=4)
>>>
alpha = 1.5
beta = 9
gamma = 4
```

The flexibility of keyword arguments provides three significant benefits.

关键字参数的灵活性提供了三个显著的优势。

The first benefit is that keyword arguments make the function call clearer to new readers of the code. With the call `remainder(20, 7)` , it’s not evident which argument is `number` and which is divisor unless you look at the implementation of the remainder method. In the call with keyword arguments, `number=20` and `divisor=7` make it immediately obvious which parameter is being used for each purpose.

第一个优势是关键字参数使得代码的新读者更容易理解函数调用的目的。使用 `remainder(20, 7)` 调用时，除非查看 `remainder` 方法的实现，否则无法立即看出哪个参数是 `number`，哪个是 `divisor`。而在带有关键字的调用中，`number=20` 和 `divisor=7` 立即表明了每个参数的用途。

The second benefit of keyword arguments is that they can have default values specified in the function definition. This allows a function to provide additional capabilities when you need them, but you can accept the default behavior most of the time. This eliminates repetitive code and reduces noise.

关键字参数的第二个好处是它们可以在函数定义中指定默认值。这允许函数在需要时提供额外的功能，但在大多数情况下你可以接受默认行为。这消除了冗余代码并减少了噪音。

For example, say that I want to compute the rate of fluid flowing into a vat. If the vat is also on a scale to measure its weight, then I could use the difference between two weight measurements at two different times to determine the flow rate:

例如，假设我想计算流体流入容器的速率。如果这个容器还放在秤上测量其重量，那么我可以通过两个不同时间点的重量测量差异来确定流速：

```
def flow_rate(weight_diff, time_diff):
    return weight_diff / time_diff

weight_a = 2.5
weight_b = 3
time_a = 1
time_b = 4
weight_diff = weight_b - weight_a
time_diff = time_b - time_a
flow = flow_rate(weight_diff, time_diff)
print(f"{flow:.3} kg per second")

>>>
0.167 kg per second
```

In the typical case, it’s useful to know the flow rate in kilograms per second. Other times, it’d be helpful to use the last sensor measurements to approximate larger time scales, like hours or days. I can provide this behavior in the same function by adding an argument for the time period scaling factor:

在通常情况下，知道每秒的流速是有用的。其他时候，使用最近的传感器测量数据来近似更大的时间尺度（如小时或天）也是有帮助的。我可以通过为时间周期缩放因子添加一个参数来在同一函数中提供这种行为：

```
def flow_rate(weight_diff, time_diff, period):
    return (weight_diff / time_diff) * period
```

The problem is that now I need to specify the `period` argument every time I call the function, even in the common case of flow rate per second (where the period is `1` ):

问题是现在每次调用该函数时都需要指定 period 参数，即使在每秒流速的常见情况下（其中周期是 1）也是如此：

```
flow_per_second = flow_rate(weight_diff, time_diff, 1)
```

To make this less noisy, I can give the `period` argument a default value:

为了减少噪音，我可以为 period 参数提供一个默认值：

```
def flow_rate(weight_diff, time_diff, period=1):  # Changed
    return (weight_diff / time_diff) * period
```

The `period` argument is now optional:

现在 period 参数是可选的：

```
flow_per_second = flow_rate(weight_diff, time_diff)
flow_per_hour = flow_rate(weight_diff, time_diff, period=3600)
```

This works well for simple default values that are immutable; it gets tricky for complex default values like `list` instances and user-defined objects (see Item 36: “Use None and Docstrings to Specify Dynamic Default Arguments” for details).

对于简单不可变的默认值来说，这种方法很有效；但对于复杂默认值（如 `list` 实例和用户定义的对象）则变得棘手（详情请参见第 36 条：“使用 None 和文档字符串指定动态默认参数”）。

The third reason to use keyword arguments is that they provide a powerful way to extend a function’s parameters while remaining backward compatible with existing callers. This means you can provide additional functionality without having to migrate a lot of existing code, which reduces the chance of introducing bugs.

第三个使用关键字参数的原因是它们提供了一种强大的方式来扩展函数的参数，同时保持向后兼容性。这意味着你可以在不迁移大量现有代码的情况下提供新功能，从而降低引入错误的可能性。

For example, say that I want to extend the `flow_rate` function above to calculate flow rates in weight units besides kilograms. I can do this by adding a new optional parameter that provides a conversion rate to alternative measurement units:

例如，假设我想扩展上面的 `flow_rate` 函数，以计算除千克以外的重量单位的流速。我可以通过添加一个新的可选参数来实现这一点，该参数提供了一个转换率到替代度量单位：

```
def flow_rate(weight_diff, time_diff, period=1, units_per_kg=1):
    return ((weight_diff * units_per_kg) / time_diff) * period
```

The default argument value for `units_per_kg` is `1` , which makes the returned weight units remain kilograms. This means that all existing callers will see no change in behavior. New callers to `flow_rate` can specify the new keyword argument to see the new behavior:

units_per_kg 的默认参数值为 1，这使得返回的重量单位仍然是千克。这意味着所有现有的调用者都不会看到行为上的变化。新的 `flow_rate` 调用者可以指定新的关键字参数以看到新行为：

```
pounds_per_hour = flow_rate(
    weight_diff,
    time_diff,
    period=3600,
    units_per_kg=2.2,
)
print(pounds_per_hour)
```

Providing backward compatibility using optional keyword arguments like this is also crucial for functions that accept `*args` (see Item 34: “Reduce Visual Noise with Variable Positional Arguments”).

像这样使用可选关键字参数提供向后兼容性对于接受 `*args` 的函数也至关重要（参见第 34 条：“使用可变位置参数减少视觉噪声”）。

The only problem with this approach is that optional keyword arguments like `period` and `units_per_kg` may still be specified as positional arguments:

这种方法的唯一问题是可以仍然通过位置参数指定可选关键字参数：

```
pounds_per_hour = flow_rate(weight_diff, time_diff, 3600, 2.2)
print(pounds_per_hour)
```

Supplying optional arguments positionally can be confusing because it isn’t clear what the values `3600` and `2.2` correspond to. The best practice is to always specify optional arguments using the keyword names and never pass them as positional arguments. As a function author, you can also require that all callers use this more explicit keyword style to minimize potential errors (see Item 37: “Enforce Clarity with Keyword-Only and Positional-Only Arguments”).

通过位置传递可选参数可能会令人困惑，因为不清楚值 `3600` 和 `2.2` 对应的是什么。最佳实践是始终使用关键字名称指定可选参数，而不要作为位置参数传递。作为函数作者，你还可以要求所有调用者都使用这种更明确的关键字风格，以最小化潜在错误（参见第 37 条：“使用仅限关键字和仅限位置的参数强制清晰性”）。

**Things to Remember**
- Function arguments can be specified by position or by keyword.
- Keywords make it clear what the purpose of each argument is when it would be confusing with only positional arguments.
- Keyword arguments with default values make it easy to add new behaviors to a function without needing to migrate all existing callers.
- Optional keyword arguments should always be passed by keyword instead of by position.

**注意事项**
- 函数参数可以通过位置或关键字指定。
- 当仅使用位置参数会造成混淆时，关键字使每个参数的目的更加清晰。
- 带有默认值的关键字参数使得向函数添加新行为变得容易，无需迁移所有现有调用者。
- 可选关键字参数应该总是通过关键字而不是位置传递。