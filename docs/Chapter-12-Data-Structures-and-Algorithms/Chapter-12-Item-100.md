# Chapter 12: Data Structures and Algorithms (数据结构与算法)

## Item 100: Sort by Complex Criteria Using the `key` Parameter (使用 `key` 参数按复杂准则排序)

The `list` built-in type provides a `sort` method for ordering the items in a `list` instance based on a variety of criteria (not to be confused with `sorted` ; see Item 101: “Know the Difference Between `sort` and `sorted` ”). By default, `sort` will order a `list`’s contents by the natural ascending order of the items. For example, here I sort a `list` of integers from smallest to largest:

`list` 内建类型提供了一个 `sort` 方法，用于根据各种准则对 `list` 实例中的项目进行排序（不要与 `sorted` 混淆；参见条目101：“了解 `sort` 和 `sorted` 的区别”）。默认情况下，`sort` 将按照列表项的自然升序对列表内容进行排序。例如，这里我将一个整数列表从最小到最大排序：

```
numbers = [93, 86, 11, 68, 70]
numbers.sort()
print(numbers)

>>>
[11, 68, 70, 86, 93]
```

The `sort` method works for nearly all built-in types (strings, floats, etc) that have a natural ordering to them. What does `sort` do with objects? For example, here I define a class—including a `__repr__` method so instances are printable; see Item 12: “Understand the Difference Between `repr` and `str` When Printing Objects”—to represent various tools you might need to use on a construction site:

对于几乎所有具有自然顺序的内建类型（字符串、浮点数等），`sort` 都有效。那么 `sort` 如何处理对象呢？例如，这里我定义了一个类——包括一个 `__repr__` 方法，以便实例可打印；参见条目12：“理解打印对象时 `repr` 和 `str` 的区别”——来表示在建筑工地上可能需要使用的各种工具：

```
class Tool:
    def __init__(self, name, weight):
        self.name = name
        self.weight = weight
    def __repr__(self):
        return f"Tool({self.name!r}, {self.weight})"

tools = [
    Tool("level", 3.5),
    Tool("hammer", 1.25),
    Tool("screwdriver", 0.5),
    Tool("chisel", 0.25),
]
```

Sorting objects of this type doesn’t work because the `sort` method tries to call comparison special methods that aren’t defined by the class:

这种类型的对象排序不起作用，因为 `sort` 方法会尝试调用该类未定义的比较特殊方法：

```
tools.sort()
>>>
Traceback ...
TypeError: '<' not supported between instances of 'Tool' and 'Tool'
```

If your class should have a natural ordering like integers do, then you can define the necessary special methods (see Item 104: “Know How to Use `heapq` for Priority Queues” for an example and Item 57: “Inherit from `collections.abc` Classes for Custom Container Types” for background) to make `sort` to work without any extra parameters. But the more common case is that your objects might need to support multiple orderings, in which case defining a single natural ordering really doesn’t make sense.

如果你的类应该像整数一样具有自然顺序，那么你可以定义必要的特殊方法（参见条目104：“知道如何使用 `heapq` 进行优先队列”中的示例和条目57：“为自定义容器类型继承 `collections.abc` 类”以获取背景知识）来使 `sort` 在不使用任何额外参数的情况下工作。但更常见的情况是，你的对象可能需要支持多种排序方式，在这种情况下，定义单一的自然顺序确实没有意义。

Often there’s an attribute on the object that you’d like to use for sorting. To support this use case, the `sort` method accepts a `key` parameter that’s expected to be a function (see Item 48: “Accept Functions Instead of Classes for Simple Interfaces” for background). The `key` function is passed a single argument, which is an item from the `list` that is being sorted. The return value of the `key` function should be a comparable value (i.e., with a natural ordering) to use in place of an item for sorting purposes.

通常，对象上有一个属性你希望用于排序。为了支持这种情况，`sort` 方法接受一个 `key` 参数，它期望是一个函数（参见条目48：“为简单接口接受函数而不是类”以获取背景信息）。`key` 函数传递一个参数，即正在排序的列表中的一个项目。`key` 函数的返回值应是一个可比较的值（即具有自然顺序），用于代替项目进行排序。

Here, I use the `lambda` keyword (see Item 39: “Prefer `functools.partial` Over `lambda` Expressions For Glue Functions” for background) to define a function for the `key` parameter that enables me to sort the `list` of `Tool` objects alphabetically by their `name` :

在这里，我使用 `lambda` 关键字（参见条目39：“优先使用 `functools.partial` 而不是 `lambda` 表达式作为粘合函数”以获取背景信息）定义一个函数，用于 `key` 参数，使我能够按 `name` 对 `Tool` 对象的列表进行字母排序：

```
print("Unsorted:", repr(tools))
tools.sort(key=lambda x: x.name)
print("\nSorted: ", tools)

>>>
Unsorted: [Tool('level', 3.5), Tool('hammer', 1.25), Tool('screwdriver', 0.5), Tool('chisel', 0.25)]
Sorted:  [Tool('chisel', 0.25), Tool('hammer', 1.25), Tool('level', 3.5), Tool('screwdriver', 0.5)]
```

I can just as easily define another lambda function to sort by `weight` and pass it as the `key` parameter to the `sort` method:

我可以同样容易地定义另一个 lambda 函数来按 `weight` 排序，并将其作为 `key` 参数传递给 `sort` 方法：

```
tools.sort(key=lambda x: x.weight)
print("By weight:", tools)
>>>
By weight: [Tool('chisel', 0.25), Tool('screwdriver', 0.5), Tool('hammer', 1.25), Tool('level', 3.5)]
```

Within the lambda function that’s passed as the `key` parameter, you can access attributes of items as I’ve done here, index into items (for sequences, tuples, and dictionaries), or use any other valid expression.

在作为 `key` 参数传递的 lambda 函数中，您可以访问项目的属性，如我在此处所做的那样，或者索引到项目中（适用于序列、元组和字典），或使用任何其他有效的表达式。

For basic types like strings, you might even want to use the `key` function to do transformations on the values before sorting. For example, here I apply the `lower` method to each item in a `list` of place names to ensure that they’re in alphabetical order, ignoring any capitalization (since in the natural lexical ordering of strings, capital letters come before lowercase letters):

对于像字符串这样的基本类型，您甚至可能希望在排序之前对值进行转换。例如，这里我对一个包含地点名称的列表应用 `lower` 方法，以确保它们按字母顺序排列，忽略任何大写（因为在字符串的自然词法排序中，大写字母出现在小写字母之前）：

```
places = ["home", "work", "New York", "Paris"]
places.sort()
print("Case sensitive: ", places)
places.sort(key=lambda x: x.lower())
print("Case insensitive:", places)
>>>
Case sensitive:  ['New York', 'Paris', 'home', 'work']
Case insensitive: ['home', 'New York', 'Paris', 'work']
```

Sometimes you might need to use multiple criteria for sorting. For example, say that I have a `list` of power tools and I want to sort them first by `weight` and then by `name` . How can I accomplish this?

有时您可能需要使用多个标准进行排序。例如，假设我有一个动力工具列表，我想先按 `weight` 然后按 `name` 对它们进行排序。如何实现这一点？

```
power_tools = [
    Tool("drill", 4),
    Tool("circular saw", 5),
    Tool("jackhammer", 40),
    Tool("sander", 4),
]
```

The simplest solution in Python is to use the `tuple` type (see Item 56: “Prefer `dataclasses` for Creating Immutable Objects” for another approach). Tuples are immutable sequences of arbitrary Python values. Tuples are comparable by default and have a natural ordering, meaning that they implement all of the special methods, such as `__lt__` , that are required by the `sort` method. Tuples implement these special method comparators by iterating over each position in the `tuple` and comparing the corresponding values one index at a time. Here, I show how this works when one tool is heavier than another:

Python 中最简单的解决方案是使用 `tuple` 类型（参见条目56：“为创建不可变对象首选 `dataclasses`”以获取另一种方法）。元组是任意 Python 值的不可变序列。元组默认是可比较的，并且有自然顺序，这意味着它们实现了所有特殊的比较方法，如`__lt__`，这些方法是 `sort` 方法所需要的。元组通过遍历每个位置的元组并逐一比较相应的值来实现这些特殊的比较方法。在这里，我展示了当一个工具比另一个重时是如何工作的：

```
saw = (5, "circular saw")
jackhammer = (40, "jackhammer")
assert not (jackhammer < saw)  # Matches expectations
```

If the first position in the tuples being compared are equal——`weight` in this case——then the `tuple` comparison will move on to the second position, and so on:

如果被比较的元组的第一个位置相等——在这种情况下是 `weight`——那么元组比较将继续到第二个位置，依此类推：

```
drill = (4, "drill")
sander = (4, "sander")
assert drill[0] == sander[0]  # Same weight
assert drill[1] < sander[1]   # Alphabetically less
assert drill < sander         # Thus, drill comes first
```

You can take advantage of this `tuple` comparison behavior in order to sort the `list` of power tools first by `weight` and then by `name` . Here, I define a `key` function that returns a `tuple` containing the two attributes that I want to sort on in order of priority:

您可以利用这种元组比较行为来对动力工具列表首先按 `weight` 然后按 `name` 进行排序。在这里，我定义了一个 `key` 函数，该函数返回一个包含两个要排序的属性的元组，按优先级顺序排列：

```
power_tools.sort(key=lambda x: (x.weight, x.name))
print(power_tools)
>>>
[Tool('drill', 4), Tool('sander', 4), Tool('circular saw', 5), Tool('jackhammer', 40)]
```

One limitation of having the `key` function return a `tuple` is that the direction of sorting for all criteria must be the same (either all in ascending order, or all in descending order). If I provide the `reverse` parameter to the sort method, it will affect both criteria in the `tuple` the same way (note how `"sander"` now comes before `"drill"` instead of after):

让 `key` 函数返回一个元组的一个限制是，所有准则的排序方向必须相同（要么都在升序，要么都在降序）。如果向排序方法提供 `reverse` 参数，它会对元组中的所有准则产生同样的影响（注意 `"sander"` 现在在 `"drill"` 之前而不是之后）：

```
power_tools.sort(
    key=lambda x: (x.weight, x.name),
    reverse=True,  # Makes all criteria descending
)
print(power_tools)
>>>
[Tool('jackhammer', 40), Tool('circular saw', 5), Tool('sander', 4), Tool('drill', 4)]
```

For numerical values it’s possible to mix sorting directions by using the unary minus operator in the `key` function. This negates one of the values in the returned `tuple` , effectively reversing its sort order while leaving the others intact. Here, I use this approach to sort by `weight` descending, and then by name ascending (note how `"sander"` now comes after `"drill"` instead of before):

对于数值类型，可以通过在 `key` 函数中使用一元减号运算符来混合排序方向。这会否定返回的元组中的一个值，有效地反转其排序顺序，同时保持其他值不变。在这里，我使用这种方法按 `weight` 降序然后按名称升序排序（注意 `"sander"` 现在在 `"drill"` 之后而不是之前）：

```
power_tools.sort(key=lambda x: (-x.weight, x.name))
print(power_tools)
>>>
[Tool('jackhammer', 40), Tool('circular saw', 5), Tool('drill', 4), Tool('sander', 4)]
```

Unfortunately, unary negation isn’t possible for all types. Here, I try to achieve the same outcome by using the `reverse` argument to sort by `weight` descending and then negating `name` to put it in ascending order:

不幸的是，一元减号运算符并不适用于所有类型。在这里，我尝试通过使用 `reverse` 参数来达到相同的效果，按 `weight` 降序排序，然后对 `name` 取反以使其升序排序：

```
power_tools.sort(key=lambda x: (x.weight, -x.name), reverse=True)
>>>
Traceback ...
TypeError: bad operand type for unary -: 'str'
```

For situations like this, Python provides a stable sorting algorithm. The `sort` method of the `list` type will preserve the order of the input `list` when the `key` function returns values that are equal to each other. This means that I can call `sort` multiple times on the same `list` to combine different criteria together. Here, I produce the same sort ordering of `weight` descending and `name` ascending as I did above, but by using two separate calls to `sort` :

对于这种情况，Python 提供了一个稳定的排序算法。`list` 类型的 `sort` 方法将在 `key` 函数返回的值彼此相等时保留输入列表的顺序。这意味着我可以在同一个列表上调用多次 `sort` 来组合不同的准则。在这里，我通过两次单独调用 `sort` 来生成与上面相同的 `weight` 降序和 `name` 升序的排序：

```
power_tools.sort(
    key=lambda x: x.name,    # Name ascending
)
power_tools.sort(
    key=lambda x: x.weight,  # Weight descending
    reverse=True,
)
print(power_tools)
>>>
[Tool('jackhammer', 40), Tool('circular saw', 5), Tool('drill', 4), Tool('sander', 4)]
```

To understand why this works, note how the first call to `sort` puts the names in alphabetical order:

要理解为什么这样可以工作，请注意第一次调用 `sort` 是按名称升序排列的：

```
power_tools.sort(key=lambda x: x.name)
print(power_tools)
>>>
[Tool('circular saw', 5), Tool('drill', 4), Tool('jackhammer', 40), Tool('sander', 4)]
```

When the second `sort` call by `weight` descending is made, it sees that both `"sander"` and `"drill"` have a weight of `4` . This causes the sort method to put both items into the final result `list` in the same order that they appeared in the original `list` , thus preserving their relative ordering by `name` ascending:

当第二次调用按 `weight` 降序排序时，它发现 `"sander"` 和 `"drill"` 的重量都是 `4`。这导致排序方法将这两个项目放入最终结果列表中，保持它们在原始列表中的相对顺序，从而保留了按名称升序的相对顺序：

```
power_tools.sort(
 key=lambda x: x.weight,
 reverse=True,
)
print(power_tools)
>>>
[Tool('jackhammer', 40), Tool('circular saw', 5) Tool('drill', 4), Tool('sander', 4)]
```

This same approach can be used to combine as many different types of sorting criteria as you’d like in any direction, respectively. You just need to make sure that you execute the sorts in the opposite sequence of what you want the final `list` to contain. In this example, I wanted the sort order to be by `weight` descending and then by name ascending, so I had to do the `name` sort first, followed by the `weight` sort.

同样的方法可以用来组合任意数量的不同类型的排序准则，分别按所需顺序执行。您只需确保以与最终列表所需的相反顺序执行排序即可。在这个例子中，我希望排序顺序是按 `weight` 降序然后按名称升序，所以我必须先做名称排序，然后做重量排序。

That said, the approach of having the `key` function return a `tuple` , and using unary negation to mix sort orders, is simpler to read and requires less code. I recommend only using multiple calls to `sort` if it’s absolutely necessary.

尽管如此，拥有返回元组的 `key` 函数的方法，并使用一元减号操作符混合排序顺序，阅读起来更简单，代码也更少。建议仅在绝对必要时才使用多次调用 `sort` 的方法。

**Things to Remember**
- The `sort` method of the `list` type can be used to rearrange a list’s contents by the natural ordering of built-in types like strings, integers, tuples, and so on.
- The `sort` method doesn’t work for objects unless they define a natural ordering using special methods, which is uncommon.
- The `key` parameter of the `sort` method can be used to supply a helper function that returns the value to use in place of each item from the `list` while sorting.
- Returning a `tuple` from the `key` function allows you to combine multiple sorting criteria together. The unary minus operator can be used to reverse individual sort orders for types that allow it.
- For types that can’t be negated, you can combine many sorting criteria together by calling the `sort` method multiple times using different key functions and `reverse` values, in the order of lowest rank `sort` call to highest rank `sort` call.

**注意事项**
- `list` 类型的 `sort` 方法可用于按照字符串、整数、元组等内置类型的自然顺序重新排列列表的内容。
- `sort` 方法不适用于对象，除非它们使用特殊方法定义了自然顺序，这是不常见的。
- `sort` 方法的 `key` 参数可用于提供一个辅助函数，该函数返回替代列表中每个项目的值来进行排序。
- 从 `key` 函数返回一个元组允许您将多个排序条件组合在一起。对于允许的类型，可以使用一元减号操作符来反转个别排序顺序。
- 对于不能取反的类型，您可以通过使用不同的键函数和 `reverse` 值多次调用 `sort` 方法来组合多个排序条件，从最低级别的排序调用到最高级别的排序调用。