# Chapter 12: Data Structures and Algorithms (数据结构与算法)

## Item 101: Know the Difference Between `sort` and `sorted` (了解 `sort` 和 `sorted` 的区别)

The most familiar way to sort data in Python is using the `list` type’s built-in `sort` method (see Item 100: “Sort by Complex Criteria Using the `key` Parameter”). This method causes the data to be sorted in-place, meaning the original list is modified and the unsorted arrangement is no longer available. For example, here I alphabetize a list of butterfly names:

在 Python 中对数据进行排序最熟悉的方式是使用 `list` 类型的内置 `sort` 方法（参见条目 100：“使用 `key` 参数按复杂条件排序”）。此方法会导致数据就地排序，意味着原始列表会被修改，未排序的排列不再可用。例如，这里我将蝴蝶名称按字母顺序排序：

```
butterflies = ["Swallowtail", "Monarch", "Red Admiral"]
print(f"Before {butterflies}")
butterflies.sort()
print(f"After {butterflies}")
>>>
Before ['Swallowtail', 'Monarch', 'Red Admiral']
After ['Monarch', 'Red Admiral', 'Swallowtail']
```

Another way to sort data in Python is using the `sorted` built-in function. This function will sort the contents of the given object, and return the results as a list while leaving the original intact:

在 Python 中另一种排序的方法是使用内置的 `sorted` 函数。该函数会对给定对象的内容进行排序，并以列表形式返回结果，同时保留原始内容不变：

```
original = ["Swallowtail", "Monarch", "Red Admiral"]
alphabetical = sorted(original)
print(f"Original {original}")
print(f"Sorted   {alphabetical}")

>>>
Original ['Swallowtail', 'Monarch', 'Red Admiral']
Sorted   ['Monarch', 'Red Admiral', 'Swallowtail']
```

The `sorted` built-in function can be used with any iterable object (see Item 21: “Be Defensive When Iterating Over Arguments”), including tuples, dictionaries, and sets:

`sorted` 内置函数可以用于任何可迭代对象（包括元组、字典和集合）（参见条目 21：“遍历参数时要具有防御性”）：

```
patterns = {"solid", "spotted", "cells"}
print(sorted(patterns))
>>>
['cells', 'solid', 'spotted']
```

It also supports the `reverse` and `key` parameters just like the `sort` built-in function (see Item 100: “Sort by Complex Criteria Using the `key` Parameter”):

它还支持与 `sort` 内置函数一样的 `reverse` 和 `key` 参数（参见条目 100：“使用 `key` 参数按复杂条件排序”）：

```
legs = {"insects": 6, "spiders": 8, "lizards": 4}
sorted_legs = sorted(
    legs,
    key=lambda x: legs[x],
    reverse=True,
)
print(sorted_legs)

>>>
['spiders', 'insects', 'lizards']
```

There are two benefits of `sort` over `sorted` . First is that `sort` is done in-place. This means that the memory consumed by your program will stay the same during and after the sort. `sorted` needs to make a copy of the iterable’s contents in order to produce a sorted list, which might double your program’s memory requirements. Second, `sort` can be a lot faster because it’s doing less work overall: the result list is already known and doesn’t need to be allocated or resized, iteration only needs to occur over a list instead of arbitrary iterable objects, and if the data is already partially ordered index reassignments can be avoided altogether.

`sort` 相对于 `sorted` 有两个优势。首先是 `sort` 是就地完成的。这意味着在排序期间和之后程序所占用的内存保持不变。而 `sorted` 需要复制可迭代对象的内容，以便生成一个已排序的列表，这可能会使程序的内存需求翻倍。其次，`sort` 可能更快，因为它整体上做的工作更少：结果列表已经是确定的，不需要分配或调整大小，在列表而非任意可迭代对象上进行迭代，如果数据已经部分有序，则完全可以避免索引重新分配。

Yet there are still two primary benefits of `sorted` in comparison to `sort` . First, the original object is left alone, ensuring that you don’t inadvertently modify arguments supplied to your functions and cause perplexing bugs (see Item 30: “Know That Function Arguments Can Be Mutated” and Item 56: “Prefer `dataclasses` for Creating Immutable Objects” for background). Second, `sorted` works for any type of iterator, not just lists, meaning your functions can rely on duck typing and be more flexible in the types they accept (see Item 25: “Be Cautious When Relying on Dictionary Insertion Ordering” for an example).

然而，与 `sort` 相比，`sorted` 仍有两个主要优点。首先，原始对象保持不变，确保您不会无意中修改提供给函数的参数并导致令人困惑的 bug（有关背景信息，请参见条目 30：“知道函数参数可能会被修改” 和条目 56：“为创建不可变对象优先选择 `dataclasses`”）。其次，`sorted` 适用于任何类型的迭代器，而不仅仅是列表，这意味着您的函数可以依赖鸭子类型，从而接受的类型更加灵活（例如参见条目 25：“依赖字典插入顺序时需谨慎”）。

Arguably, `sorted` is more Pythonic because it enables additional flexibility and is more explicit in how it produces results. The choice will depend on the circumstances and what you’re trying to accomplish.

可以说，`sorted` 更加 Pythonic，因为它提供了额外的灵活性，并且在产生结果方面更为明确。具体选择取决于具体情况和您想要实现的目标。

Things to Remember
- `sort` achieves maximum performance with minimal memory overhead, but requires the target list to be modified in-place.
- `sorted` can process all types of iterators and collections as input, and won’t inadvertently mutate data.

**注意事项**
- `sort` 实现了最高性能和最小内存开销，但需要就地修改目标列表。
- `sorted` 可以处理所有类型的迭代器和集合作为输入，并且不会无意间修改数据。