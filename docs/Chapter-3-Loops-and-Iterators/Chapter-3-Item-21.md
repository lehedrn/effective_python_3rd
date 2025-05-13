# Chapter 3: Loops and Iterators (循环和迭代器)

## Item 21: Be Defensive when Iterating over Arguments (在遍历参数时要保持防御性)

When a function takes a `list` of objects as a parameter, it’s often important to iterate over that `list` multiple times. For example, say that I want to analyze tourism numbers for the U.S. state of Texas. Imagine that the data set is the number of visitors to each city (in millions per year). I’d like to figure out what percentage of overall tourism each city receives.

当一个函数接收一个对象的list作为参数时，通常需要多次遍历该list。例如，假设我想分析美国德克萨斯州的旅游人数。想象一下，数据集是每个城市的游客数量（以百万计每年）。我想要弄清楚每个城市对整体旅游的百分比贡献。

To do this, I need a normalization function that sums the inputs to determine the total number of tourists per year, and then divides each city’s individual visitor count by the total to find that city’s contribution to the whole:

为了做到这一点，我需要一个归一化函数来求和输入数据以确定每年的总游客数，然后将每个城市的游客数量除以总数量以找到该城市的贡献：

```
def normalize(numbers):
    total = sum(numbers)
    result = []
    for value in numbers:
        percent = 100 * value / total
        result.append(percent)
    return result
```

This function works as expected when given a `list` of visits:

当给定一个城市的访问量列表时，此函数按预期工作：

```
visits = [15, 35, 80]
percentages = normalize(visits)
print(percentages)
assert sum(percentages) == 100.0

>>>
[11.538461538461538, 26.923076923076923, 61.53846153846154]
```

To scale this up, I need to read the data from a file that contains every city in all of Texas. I define a generator to do this because then I can reuse the same function later, when I want to compute tourism numbers for the whole world—a much larger data set with higher memory requirements (see Item 43: “Consider Generators Instead of Returning Lists” for background):

为了扩展这个功能，我需要从一个包含所有德克萨斯州城市的数据文件中读取数据。我定义了一个生成器来做这件事，因为这样稍后我可以重用相同的函数来计算全世界的旅游人数——这是一个更大的数据集，内存需求更高（请参阅条目43）：

```
path = "my_numbers.txt"
with open(path, "w") as f:
    for i in (15, 35, 80):
        f.write(f"{i}\n")

def read_visits(data_path):
    with open(data_path) as f:
        for line in f:
            yield int(line)
```

Surprisingly, calling `normalize` on the `read_visits` generator’s return value produces no results:

令人惊讶的是，在read_visits生成器的返回值上调用normalize没有产生任何结果：

```
it = read_visits("my_numbers.txt")
percentages = normalize(it)
print(percentages)
>>>
[]
```

This behavior occurs because an iterator produces its results only a single time. If you iterate over an iterator or a generator that has already raised a `StopIteration` exception, you won’t get any results the second time around:

这种行为发生的原因是一个迭代器只能产生一次结果。如果你在一个已经引发过`StopIteration`异常的迭代器或生成器上再次迭代，你不会得到任何结果：

```
it = read_visits("my_numbers.txt")
print(list(it))
print(list(it)) # Already exhausted
>>>
[15, 35, 80]
[]
```

Confusingly, an exception won’t be raised when you iterate over an already exhausted iterator. `for` loops, the `list` constructor, and many other functions throughout the Python standard library expect the `StopIteration` exception to be raised during normal operation. These functions can’t tell the difference between an iterator that has no output and an iterator that had output and is now exhausted.

令人困惑的是，当你尝试迭代一个已经耗尽的迭代器时，并不会抛出异常。for循环、list构造函数和其他许多Python标准库中的函数都期望在正常操作期间引发StopIteration异常。这些函数无法区分一个没有输出的迭代器和一个已经有输出并且现在已耗尽的迭代器。

To solve this problem, you can explicitly exhaust an input iterator and keep a copy of its entire contents in a `list` . You can then iterate over the `list` version of the data as many times as you need to. Here’s the same function as before, but it defensively copies the input iterator:

为了解决这个问题，你可以显式地耗尽一个输入迭代器并保留其全部内容的副本到一个`list`中。然后你可以根据需要多次迭代这份数据的副本。下面是与之前相同的功能，但这次它防御性地复制了输入迭代器：

```
def normalize_copy(numbers):
    numbers_copy = list(numbers)  # Copy the iterator
    total = sum(numbers_copy)
    result = []
    for value in numbers_copy:
        percent = 100 * value / total
        result.append(percent)
    return result
```

Now the function works correctly on the `read_visits` generator’s return value:

现在该函数可以正确处理read_visits生成器的返回值：

```
it = read_visits("my_numbers.txt")
percentages = normalize_copy(it)
print(percentages)
assert sum(percentages) == 100.0
>>>
[11.538461538461538, 26.923076923076923, 61.53846153846154]
```

The problem with this approach is that the copy of the input iterator’s contents could be extremely large. Copying the iterator could cause the program to run out of memory and crash (see Item 115: “Use tracemalloc to Understand Memory Usage and Leaks” on how to debug this). This potential for scalability issues undermines the reason that I wrote `read_visits` as a generator in the first place. One way around this is to accept a function that returns a new iterator each time it’s called:

这种方法的问题在于，输入迭代器的内容副本可能会非常大。复制迭代器可能导致程序内存不足而崩溃（参见条目115）。这种潜在的可扩展性问题削弱了我最初将read_visits编写为生成器的理由。一种解决方法是接受一个每次调用都会返回新迭代器的函数：

```
def normalize_func(get_iter):
    total = sum(get_iter())   # New iterator
    result = []
    for value in get_iter():  # New iterator
        percent = 100 * value / total
        result.append(percent)
    return result
```

To use `normalize_func` , I can pass in a `lambda` expression that produces a new generator iterator each time it’s called:

要使用`normalize_func`，我可以传入一个`lambda`表达式，该表达式会在每次调用时生成一个新的生成器迭代器：

```
path = "my_numbers.txt"
percentages = normalize_func(lambda: read_visits(path))
print(percentages)
assert sum(percentages) == 100.0
>>>
[11.538461538461538, 26.923076923076923, 61.53846153846154]
```

Although this works, having to pass a lambda function like this is clumsy. A better way to achieve the same result is to define a new container class that implements the iterator protocol.

虽然这有效，但必须像这样传递lambda函数是很笨拙的。实现同样效果的一种更好的方法是定义一个新的容器类，该类实现迭代器协议。

The iterator protocol is how Python `for` loops and related expressions traverse the contents of a container type. When Python sees a statement like `for x in foo` , it actually calls `iter(foo)` to discover the iterator to loop through. The `iter` built-in function calls the `foo.__iter__` special method in turn. The `__iter__` method must return an iterator object (which itself implements the `__next__` special method). Then, the `for` loop repeatedly calls the `next` built-in function on the iterator
object until it’s exhausted (indicated by raising a `StopIteration` exception).

迭代器协议是Python `for` 循环及相关表达式遍历容器类型内容的方式。当Python看到像 `for x in foo` 这样的语句时，实际上会调用 `iter(foo)` 来发现要遍历的迭代器。内置的 `iter` 函数又会调用 `foo.__iter__` 特殊方法。`iter` 方法必须返回一个迭代器对象（该对象本身实现了 `next` 特殊方法）。然后，`for` 循环会在迭代器对象上调用内置的 `next` 函数，直到它耗尽为止（通过引发 `StopIteration` 异常表示）。

It sounds complicated, but practically speaking, you can enable all of this behavior for your own classes by implementing the `__iter__` method as a generator. Here, I define an iterable container class that reads the file containing tourism data and uses `yield` to produce one line of data at a time:

听起来很复杂，但实际上，您可以通过实现 `__iter__` 方法作为一个生成器来为自己的类启用所有这些行为。在这里，我定义了一个可迭代的容器类，它读取包含旅游数据的文件并使用 `yield` 每次生成一行数据：

```
class ReadVisits:
    def __init__(self, data_path):
        self.data_path = data_path

    def __iter__(self):
        with open(self.data_path) as f:
            for line in f:
                yield int(line)
```

This new container type can be passed to the original function without any modifications:

这种新的容器类型可以在不进行任何修改的情况下传递给原始函数：

```
visits = ReadVisits(path)
percentages = normalize(visits) # Changed
print(percentages)
assert sum(percentages) == 100.0
>>>
[11.538461538461538, 26.923076923076923, 61.53846153846154]
```

This works because the `sum` method in `normalize` calls `ReadVisits.__iter__` to allocate a new iterator object. The `for` loop to normalize the numbers also calls `__iter__` to allocate a second iterator object. Each of those iterators will be advanced and exhausted independently, ensuring that each unique iteration sees all of the input data values. The only downside of this approach is that it reads the input data multiple times.

这是因为 `normalize` 中的 `sum` 方法调用了 `ReadVisits.__iter__` 来分配一个新的迭代器对象。`normalize` 函数的 `for` 循环也会调用 `__iter__` 来分配第二个迭代器对象。每个这些迭代器将独立推进和耗尽，确保每次唯一的迭代都能看到所有的输入数据值。这种方法的唯一缺点是它会多次读取输入数据。

Now that you know how containers like `ReadVisits` work, you can write your functions and methods to ensure that parameters aren’t just iterators. The protocol states that when an iterator is passed to the `iter` built-in function, `iter` returns the iterator itself. In contrast, when a container type is passed to `iter` , a new iterator object is returned each time. Thus, you can test an input value for this behavior and raise a `TypeError` to reject arguments that can’t be repeatedly iterated over:

既然你知道了像 `ReadVisits` 这样的容器是如何工作的，你就可以编写你的函数和方法来确保参数不仅仅是迭代器。协议规定，当迭代器被传递给内置的 `iter` 函数时，`iter` 返回迭代器本身。相反，当容器类型被传递给 `iter` 时，每次都会返回一个新的迭代器对象。因此，你可以测试输入值的这种行为并引发 `TypeError` 来拒绝那些不能被重复迭代的参数：

```
def normalize_defensive(numbers):
    if iter(numbers) is numbers:  # An iterator -- bad!
        raise TypeError("Must supply a container")
    total = sum(numbers)
    result = []
    for value in numbers:
        percent = 100 * value / total
        result.append(percent)
    return result
```

Alternatively, the `collections.abc` built-in module defines an `Iterator` class that can be used in an `isinstance` test to recognize the potential problem (see Item 57: “Inherit from collections.abc for Custom Container Types”):

或者，`collections.abc` 内置模块定义了一个 `Iterator` 类，可以用在 `isinstance` 测试中来识别潜在的问题（参见条目57）：

```
from collections.abc import Iterator

def normalize_defensive(numbers):
    if isinstance(numbers, Iterator):  # Another way to check
        raise TypeError("Must supply a container")
    total = sum(numbers)
    result = []
    for value in numbers:
        percent = 100 * value / total
        result.append(percent)
    return result
```

The approach of expecting a container is ideal if you don’t want to copy the full input iterator—like in the `normalize_copy` function above—but you also need to iterate over the input data multiple times. Here, I show how the `normalize_defensive` function can accept a `list` , a `ReadVisits` object, or theoretically any container that follows the iterator protocol:

如果你不想复制完整的输入迭代器（如上面的 `normalize_copy` 函数），但你也需要多次遍历输入数据，那么期待一个容器的方法是理想的。这里展示了 `normalize_defensive` 函数如何接受一个 `list`、一个 `ReadVisits` 对象，或者理论上任何遵循迭代器协议的容器：

```
visits_list = [15, 35, 80]
list_percentages = normalize_defensive(visits_list)

visits_obj = ReadVisits(path)
obj_percentages = normalize_defensive(visits_obj)

assert list_percentages == obj_percentages
assert sum(percentages) == 100.0
```

The `normalize_defensive` function raises an exception if the input is an iterator rather than a container:

如果输入是一个迭代器而不是一个容器，normalize_defensive 函数会引发一个异常：

```
visits = [15, 35, 80]
it = iter(visits)
normalize_defensive(it)
>>>
Traceback ...
TypeError: Must supply a container
```

The same approach of checking for compliance with the iterator protocol can also be used with asynchronous iterators (see Item 76: “Know How to Port Threaded I/O to asyncio ” for an example).

同样的检查符合迭代器协议的方法也可以用于异步迭代器（参见条目76）。

**Things to Remember**

- Beware of functions and methods that iterate over input arguments multiple times. If these arguments are iterators, you might see strange behavior and missing values.
- Python’s iterator protocol defines how containers and iterators interact with the `iter` and `next` built-in functions, `for` loops, and related expressions.
- You can easily define your own iterable container type by implementing the `__iter__` method as a generator.
- You can detect that a value is an iterator (instead of a container) if calling `iter` on it produces the same value as what you passed in. Alternatively, you can use the `isinstance` built-in function along with the `collections.abc.Iterator` class.

**注意事项**
- 警惕那些多次遍历输入参数的函数和方法。如果这些参数是迭代器，你可能会看到奇怪的行为和缺失的值。
- Python 的迭代器协议定义了容器和迭代器如何与内置的 `iter` 和 `next` 函数、`for` 循环以及相关表达式交互。
- 你可以通过将 `__iter__` 方法实现为生成器，轻松定义自己的可迭代容器类型。
- 如果调用 `iter` 在某个值上会产生与你传入的相同的值，则可以检测到该值是一个迭代器（而不是容器）。或者，您可以使用 `isinstance` 内置函数和 `collections.abc.Iterator` 类。