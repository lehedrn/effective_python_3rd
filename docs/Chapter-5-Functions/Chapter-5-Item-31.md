# Chapter 5: Functions (函数)

## Item 31: Return Dedicated Result Objects Instead of Requiring Function Callers to Unpack More Than Three Variables (返回专用的结果对象，而不是要求调用者解包超过三个变量)

One effect of the unpacking syntax (see Item 5: “Prefer Multiple Assignment Unpacking Over Indexing”) is that it allows Python functions to seemingly return more than one value. For example, say that I’m trying to determine various statistics for a population of alligators. Given a `list` of lengths, I need to calculate the minimum and maximum lengths in the population. Here, I do this in a single function that appears to return two values:

解包语法的一个效果（见条目5：“优先使用多重赋值解包而不是索引”）是它允许Python函数看起来返回多于一个值。例如，假设我试图确定鳄鱼种群的各种统计数据。给定一个长度列表，我需要计算该种群中的最小和最大长度。在这里，我在一个函数中完成这些操作，这个函数似乎返回两个值：

```
def get_stats(numbers):
    minimum = min(numbers)
    maximum = max(numbers)
    return minimum, maximum

lengths = [63, 73, 72, 60, 67, 66, 71, 61, 72, 70]

minimum, maximum = get_stats(lengths)  # Two return values

print(f"Min: {minimum}, Max: {maximum}")

>>>
Min: 60, Max: 73
```

The way this works is that multiple values are returned together in a two-item `tuple` . The calling code then unpacks the returned `tuple` by assigning two variables. Here, I use an even simpler example to show how an unpacking statement and multiple-return function work the same way:

其工作原理是，多个值一起在一个包含两个项目的元组中返回。调用代码然后通过分配两个变量来解包返回的元组。这里，我使用一个更简单的例子来展示解包语句和多返回函数如何以相同的方式工作：

```
first, second = 1, 2
assert first == 1
assert second == 2

def my_function():
    return 1, 2

first, second = my_function()
assert first == 1
assert second == 2
```

Multiple return values can also be received by starred expressions for catch-all unpacking (see Item 16: “Prefer Catch-All Unpacking Over Slicing”). For example, say I need another function that calculates how big each alligator is relative to the population average. This function returns a `list` of ratios, but I can receive the longest and shortest items individually by using a starred expression for the middle portion of the `list` :

多返回值也可以通过星号表达式接收用于捕获所有未明确解包的值（见条目16：“优先使用捕获所有解包而不是切片”）。例如，假设我需要另一个函数来计算每只鳄鱼相对于种群平均大小的比例。此函数返回一个比例列表，但通过使用中间部分的星号表达式，我可以单独接收最长和最短的项目：

```
def get_avg_ratio(numbers):
    average = sum(numbers) / len(numbers)
    scaled = [x / average for x in numbers]
    scaled.sort(reverse=True)
    return scaled

longest, *middle, shortest = get_avg_ratio(lengths)

print(f"Longest:  {longest:>4.0%}")
print(f"Shortest: {shortest:>4.0%}")
>>>
Longest: 108%
Shortest: 89%
```

Now, imagine that the program’s requirements change, and I need to also determine the average length, median length, and total population size of the alligators. I can do this by expanding the `get_stats` function to also calculate these statistics and return them in the result `tuple` that is unpacked by the caller:

现在，设想程序的需求发生变化，我还需要确定鳄鱼的平均长度、中位数长度以及总种群数量。我可以通过扩展 get_stats 函数来计算这些统计信息，并在调用者解包的结果元组中返回它们：

```
def get_median(numbers):
    count = len(numbers)
    sorted_numbers = sorted(numbers)
    middle = count // 2
    if count % 2 == 0:
        lower = sorted_numbers[middle - 1]
        upper = sorted_numbers[middle]
        median = (lower + upper) / 2
    else:
        median = sorted_numbers[middle]
    return median

def get_stats_more(numbers):
    minimum = min(numbers)
    maximum = max(numbers)
    count = len(numbers)
    average = sum(numbers) / count
    median = get_median(numbers)
    return minimum, maximum, average, median, count

minimum, maximum, average, median, count = get_stats_more(lengths)

print(f"Min: {minimum}, Max: {maximum}")
print(f"Average: {average}, Median: {median}, Count {count}")

>>>
Min: 60, Max: 73
Average: 67.5, Median: 68.5, Count 10
```

There are two problems with this code. First, all of the return values are numeric, so it is all too easy to reorder them accidentally (e.g., swapping average and median), which can cause bugs that are hard to spot later. Using a large number of return values is extremely error prone:

这段代码有两个问题。首先，所有的返回值都是数字，因此非常容易意外地重新排序它们（例如，交换平均值和中位数），这可能导致以后难以发现的错误。使用大量的返回值是非常容易出错的：

```
# Correct:
minimum, maximum, average, median, count =
get_stats_more(lengths)
# Oops! Median and average swapped:
minimum, maximum, median, average, count =
get_stats_more(lengths)
```

Second, the line that calls the function and unpacks the values is long, and it likely will need to be wrapped in one of a variety of ways (due to PEP 8 style; see Item 2: “Follow the PEP 8 Style Guide”), which hurts readability:

其次，调用函数并解包值的那行代码很长，可能需要用各种方式之一进行换行（由于PEP 8风格；见条目2：“遵循PEP 8风格指南”），这会降低可读性：

```
minimum, maximum, average, median, count = get_stats_more(lengths)

minimum, maximum, average, median, count = \
    get_stats_more(lengths)

(minimum, maximum, average,
 median, count) = get_stats_more(lengths)

(minimum, maximum, average, median, count
    ) = get_stats_more(lengths)

```

To avoid these problems, you should never use more than three variables when unpacking the multiple return values from a function. These could be individual values from a three-tuple, two variables and one catch-all starred expression, or anything shorter.

为了避免这些问题，在解包从函数返回的多个返回值时，您永远不应该使用超过三个变量。这些可以是一个三元组中的各个值，两个变量和一个通配符星号表达式，或者任何更短的情况。

If you need to unpack more return values than that, you’re better off defining a lightweight class (see Item 29: “Compose Classes Instead of Deeply Nesting Dictionaries, Lists, and Tuples” and Item 51: “Prefer dataclasses For Defining Light-Weight Classes”) and having your function return an instance of that instead. Here, I write another version of the `get_stats` function that returns a result object instead of a tuple:

如果您需要解包比这更多的返回值，最好定义一个轻量级类（见条目29：“组合类而不是深度嵌套字典、列表和元组”和条目51：“对于定义轻量级类优先选择数据类”），并让您的函数返回该类的实例。在这里，我编写了另一个版本的 get_stats 函数，它返回一个结果对象而不是一个元组：

```
from dataclasses import dataclass

@dataclass
class Stats:
    minimum: float
    maximum: float
    average: float
    median: float
    count: int

def get_stats_obj(numbers):
    return Stats(
        minimum=min(numbers),
        maximum=max(numbers),
        count=len(numbers),
        average=sum(numbers) / count,
        median=get_median(numbers),
    )

result = get_stats_obj(lengths)
print(result)
>>>
Stats(minimum=60, maximum=73, average=67.5, median=68.5, count=10)
```

The code is clearer, less error-prone, and will be easier to refactor later.

这样的代码更加清晰，不易出错，并且将来更容易重构。

**Things to Remember**
- You can have functions return multiple values by putting them in a `tuple` and having the caller take advantage of Python’s unpacking syntax.
- Multiple return values from a function can also be unpacked by catch-all starred expressions.
- Unpacking into four or more variables is error prone and should be avoided; instead, return an instance of a light-weight class.

**注意事项**
- 您可以通过将多个值放在一个元组中，并让调用者利用Python的解包语法来实现函数返回多个值。
- 函数的多返回值也可以通过通配符星号表达式进行解包。
- 解包到四个或更多变量中容易出错，应避免；相反，返回一个轻量级类的实例。