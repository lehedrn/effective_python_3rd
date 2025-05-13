# Chapter 3: Loops and Iterators (循环和迭代器)

## Item 24: Consider itertools for Working with Iterators and Generators (考虑使用 itertools 处理迭代器和生成器)

The `itertools` built-in module contains a large number of functions that are useful for organizing and interacting with iterators (see Item 43: “Consider Generators Instead of Returning Lists” and Item 21: “Be Defensive When Iterating Over Arguments” for background):

`itertools` 内置模块包含大量对处理迭代器非常有用的函数（参见条目43 和 条目21）：

```
import itertools
```

Whenever you find yourself dealing with tricky iteration code, it’s worth looking at the `itertools` documentation again to see if there’s anything in there for you to use (see https://docs.python.org/3/library/itertools.html). The following sections describe the most important functions that you should know in three primary categories.

每当你发现自己在处理棘手的迭代代码时，值得再次查看 `itertools` 的文档，看看是否有适合你使用的函数（请参阅 `https://docs.python.org/3/library/itertools.html`）。 以下章节描述了你应该了解的三个主要类别中的最重要的函数。

**Linking Iterators Together**

**将迭代器链接在一起**

The `itertools` built-in module includes a number of functions for linking iterators together.

`itertools` 内置模块包括一些用于将迭代器链接在一起的函数。

`chain`

Use chain to combine multiple iterators into a single sequential iterator.Essentially this flattens the provided input iterators into one iterator of items:

使用 `chain` 将多个迭代器组合成一个顺序迭代器。本质上，这会将提供的输入迭代器扁平化为一个项目迭代器：

```
it = itertools.chain([1, 2, 3], [4, 5, 6])
print(list(it))
>>>
[1, 2, 3, 4, 5, 6]
```

There’s also an alternative version of this function called `chain.from_iterable` that will consume an iterator of iterators and produce a single flattened output iterator that includes all of their contents:

还有一个名为 `chain.from_iterable` 的替代函数，它会消费一个迭代器的迭代器，并产生一个包含其所有内容的单一扁平输出迭代器：

```
it1 = [i * 3 for i in ("a", "b", "c")]
it2 = [j * 2 for j in ("x", "y", "z")]
nested_it = [it1, it2]
output_it = itertools.chain.from_iterable(nested_it)
print(list(output_it))
>>>
['aaa', 'bbb', 'ccc', 'xx', 'yy', 'zz']
```

`repeat`

Use `repeat` to output a single value forever, or use the second optional parameter to specify a maximum number of times:

使用 `repeat` 永远输出单个值，或者使用第二个可选参数指定最大次数：

```
it = itertools.repeat("hello", 3)
print(list(it))
>>>
['hello', 'hello', 'hello']
```

`cycle`

Use `cycle` to repeat an iterator’s items forever:

使用 `cycle` 永远重复一个迭代器的项目：

```
it = itertools.cycle([1, 2])
result = [next(it) for _ in range(10)]
print(result)
>>>
[1, 2, 1, 2, 1, 2, 1, 2, 1, 2]
```

`tee`

Use `tee` to split a single iterator into the number of parallel iterators specified by the second parameter. The memory usage of this function will grow if the iterators don’t progress at the same speed since buffering will be required to temporarily store the pending items:

使用 `tee` 将单个迭代器拆分为由第二个参数指定的多个并行迭代器。如果迭代器进展速度不同，则此函数的内存使用量将会增长，因为需要缓冲来临时存储待处理的项目：

```
it1, it2, it3 = itertools.tee(["first", "second"], 3)
print(list(it1))
print(list(it2))
print(list(it3))
>>>
['first', 'second']
['first', 'second']
['first', 'second']
```

`zip_longest`

This variant of the `zip` built-in function returns a placeholder value when an iterator is exhausted, which may happen if iterators have different lengths (see Item 18: “Use zip to Process Iterators in Parallel” for how the `strict` argument can provide similar behavior):

这个变体的内置 `zip` 函数在一个迭代器耗尽后返回一个占位符值，这可能发生在迭代器长度不同时（参见条目18）：

```
keys = ["one", "two", "three"]
values = [1, 2]

normal = list(zip(keys, values))
print("zip:        ", normal)

it = itertools.zip_longest(keys, values, fillvalue="nope")
longest = list(it)
print("zip_longest:", longest)
>>>
zip:         [('one', 1), ('two', 2)]
zip_longest: [('one', 1), ('two', 2), ('three', 'nope')]
```

**Filtering Items from an Iterator**

**从迭代器中过滤项目**

The `itertools` built-in module includes a number of functions for filtering items from an iterator.

`itertools` 内置模块包括一些用于从迭代器中过滤项目的函数。

`islice`

Use `islice` to slice an iterator by numerical indexes without copying. You can specify the end, start and end, or start, end, and step sizes. The behavior of islice is similar to that of standard sequence slicing and striding (see Item 14: “Know How to Slice Sequences” and Item 15: “Avoid Striding and Slicing in a Single Expression”):

使用 `islice` 按照数字索引切片一个迭代器而不复制。你可以指定结束、开始和结束，或者开始、结束和步长大小。`islice` 的行为类似于标准序列切片和步进（参见条目14和条目15）：

```
values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

first_five = itertools.islice(values, 5)
print("First five: ", list(first_five))

middle_odds = itertools.islice(values, 2, 8, 2)
print("Middle odds:", list(middle_odds))

>>>
First five: [1, 2, 3, 4, 5]
Middle odds: [3, 5, 7]
```

`takewhile`

`takewhile` returns items from an iterator until a predicate function returns False for an item, at which point all items from the iterator will be consumed but not returned (see Item 39: “Prefer functools.partial Over lambda Expressions For Glue Functions” for more about defining predicates):

`takewhile` 从一个迭代器中返回项目，直到谓词函数对某个项目返回 `False`，在这一点之后迭代器的所有项目都将被消费但不会返回（参见条目39）：

```
values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
less_than_seven = lambda x: x < 7
it = itertools.takewhile(less_than_seven, values)
print(list(it))
>>>
[1, 2, 3, 4, 5, 6]
```

`dropwhile`

`dropwhile` , which is the opposite of `takewhile` , skips items from an iterator until the predicate function returns False for the first time, at which point all items from the iterator will be returned:

`dropwhile` 是 `takewhile` 的相反操作，它会跳过迭代器中的项目，直到谓词函数第一次返回 `False`，在这一点之后迭代器的所有项目都将返回：

```
values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
less_than_seven = lambda x: x < 7
it = itertools.dropwhile(less_than_seven, values)
print(list(it))
>>>
[7, 8, 9, 10]
```

`filterfalse`

`filterfalse` , which is the opposite of the `filter` built-in function, returns all items from an iterator when a predicate function returns `False` :

`filterfalse` 是内置 `filter` 函数的相反操作，当谓词函数返回 `False` 时，它会返回迭代器中的所有项目：

```
values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
evens = lambda x: x % 2 == 0

filter_result = filter(evens, values)
print("Filter:      ", list(filter_result))

filter_false_result = itertools.filterfalse(evens, values)
print("Filter false:", list(filter_false_result))
>>>
Filter: [2, 4, 6, 8, 10]
Filter false: [1, 3, 5, 7, 9]
```

**Producing Combinations of Items from Iterators**

**从迭代器中生成项目组合**

The `itertools` built-in module includes a number of functions for producing combinations of items from iterators.

`itertools` 内置模块包括一些用于从迭代器中生成组合的函数。

`batched`

Use `batched` to create an iterator that outputs fixed sized, non￾overlapping groups of items from a single input iterator. The second argument is the batch size. This can be especially useful when processing data together for efficiency or satisfying other constraints like data size limits.

使用 `batched` 创建一个迭代器，该迭代器从单个输入迭代器中输出固定大小的非重叠组。第二个参数是批次大小。这在处理数据以提高效率或满足其他约束条件（如数据大小限制）时特别有用：

```
it = itertools.batched([1, 2, 3, 4, 5, 6, 7, 8, 9], 3)
print(list(it))
>>>
[(1, 2, 3), (4, 5, 6), (7, 8, 9)]
```

The last group produced by the iterator might be smaller than the specified batch size if the items can’t divide perfectly:

如果项目无法完美分割，最后一批生成的组可能小于指定的批次大小：

```
it = itertools.batched([1, 2, 3], 2)
print(list(it))
>>>
[(1, 2), (3,)]
```

`pairwise`

Use `pairwise` when you need to iterate through each pair of adjacent items in the input iterator. The pairs include overlaps, so each item—besides the ends—appears twice in the output iterator: once in the first position of a pair and another time in the second position. This can be helpful when writing graph traversal algorithms that need to step through sequential sets of vertexes or endpoints.

当需要遍历输入迭代器中每一对相邻项目时，请使用 `pairwise`。这些配对包括重叠，因此除了两端之外，每个项目都会在输出迭代器中出现两次：一次在配对的第一个位置，另一次在第二个位置。这在编写需要逐步通过连续顶点或端点的图遍历算法时很有帮助：

```
route = ["Los Angeles", "Bakersfield", "Modesto", "Sacramento"]
it = itertools.pairwise(route)
print(list(it))

>>>
[('Los Angeles', 'Bakersfield'), ('Bakersfield', 'Modesto'), ('Modesto', 'Sacramento')]
```

`accumulate`

`accumulate` folds an item from the iterator into a running value by applying a function that takes two parameters. It outputs the current accumulated result for each input value:

`accumulate` 通过应用一个接受两个参数的函数，将迭代器中的项目折叠到一个运行值中。它会为每个输入值输出当前累计结果：

```
values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
sum_reduce = itertools.accumulate(values)
print("Sum:   ", list(sum_reduce))

def sum_modulo_20(first, second):
    output = first + second
    return output % 20

modulo_reduce = itertools.accumulate(values, sum_modulo_20)
print("Modulo:", list(modulo_reduce))
>>>
Sum: [1, 3, 6, 10, 15, 21, 28, 36, 45, 55]
Modulo: [1, 3, 6, 10, 15, 1, 8, 16, 5, 15]
```

This is essentially the same as the `reduce` function from the `functools` built-in module, but with outputs yielded one step at a time. By default it sums the inputs if no binary function is specified.

这本质上与 `functools` 内置模块中的 `reduce` 函数相同，但是输出是一步步地产生。如果没有指定二元函数，默认会对输入进行求和。

`product`

`product` returns the Cartesian product of items from one or more iterators, which is a nice alternative to using deeply nested list comprehensions (see Item 41: “Avoid More Than Two Control Subexpressions in Comprehensions” for why to avoid those):

`product` 返回来自一个或多个迭代器的项目的笛卡尔积，这是嵌套列表推导式的不错替代方案（参见条目41）：

```
single = itertools.product([1, 2], repeat=2)
print("Single:  ", list(single))

multiple = itertools.product([1, 2], ["a", "b"])
print("Multiple:", list(multiple))
>>>
Single: [(1, 1), (1, 2), (2, 1), (2, 2)]
Multiple: [(1, 'a'), (1, 'b'), (2, 'a'), (2, 'b')
```

`permutations`

`permutations` returns the unique ordered permutations of length N—the second argument—with items from an iterator:

`permutations` 返回长度为 N（第二个参数）的唯一有序排列，其中包含来自迭代器的项目：

```
it = itertools.permutations([1, 2, 3, 4], 2)
print(list(it))
>>>
[(1, 2),
 (1, 3),
 (1, 4),
 (2, 1),
 (2, 3),
 (2, 4),
 (3, 1),
 (3, 2),
 (3, 4),
 (4, 1),
 (4, 2),
 (4, 3)]
```

`combinations`

`combinations` returns the unordered combinations of length N—the second argument—with unrepeated items from an iterator:

`combinations` 返回长度为 N（第二个参数）的无序组合，其中包含来自迭代器的不重复项目：

```
it = itertools.combinations([1, 2, 3, 4], 2)
print(list(it))
>>>
[(1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4)]
```

`combinations_with_replacement`

`combinations_with_replacement` is the same as `combinations` , but repeated values are allowed. The difference between this and the `permutations` function is this version allows the same input to be repeated multiple times in the output groups (i.e., see (1,1) in the output below):

`combinations_with_replacement` 与 `combinations` 相同，但允许重复值。此版本与 `permutations` 函数的区别在于，此版本允许相同的输入在输出组中多次重复（例如，参见下面输出中的 `(1,1)`）：

```
it = itertools.combinations_with_replacement([1, 2, 3, 4], 2)
print(list(it))
>>>
[(1, 1),
 (1, 2),
 (1, 3),
 (1, 4),
 (2, 2),
 (2, 3),
 (2, 4),
 (3, 3),
 (3, 4),
 (4, 4)]
```

**Things to Remember**
- The `itertools` functions fall into three main categories for working with iterators and generators: linking iterators together, filtering items they output, and producing combinations of items.
- There are more advanced functions, additional parameters, and useful recipes available in the official documentation.

**注意事项**
- `itertools` 函数分为三大类，用于处理迭代器和生成器：将迭代器链接在一起、过滤它们输出的项目以及生成项目的组合。
- 在官方文档中还有更多高级函数、额外参数和有用的示例可供参考。