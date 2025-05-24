# Chapter 12: Data Structures and Algorithms (数据结构和算法)

## Item 102: Consider Searching Sorted Sequences with `bisect` (考虑使用 `bisect` 在排序序列中进行搜索)

It’s common to find yourself with a large amount of data in memory as a sorted `list` that you then want to search. For example, you may have loaded an English language dictionary to use for spell checking, or perhaps a `list` of dated financial transactions to audit for correctness.

在内存中以已排序的 `list` 形式存储大量数据，然后需要搜索这些数据的情况很常见。例如，你可能已经加载了一本英文词典用于拼写检查，或者你可能有一个按日期排列的金融交易列表来验证正确性。

Regardless of the data your specific program needs to process, searching for a specific value in a `list` takes linear time proportional to the list’s length when you call the `index` method:

不管你的程序具体需要处理什么数据，当你调用 `index` 方法时，在 `list` 中查找特定值所需要的时间与列表长度成正比：

```
data = list(range(10**5))
index = data.index(91234)
assert index == 91234
```

If you’re not sure whether the exact value you’re searching for is in the `list` , then you might want to search for the closest index that is equal to or exceeds your goal value. The simplest way to do this is to linearly scan the `list` and compare each item to your goal value:

如果你不确定要搜索的确切值是否存在于 `list` 中，那么你可能想要找到等于或超过目标值的最接近索引。最简单的方法是线性扫描列表并比较每个项目与你的目标值：

```
def find_closest(sequence, goal):
    for index, value in enumerate(sequence):
        if goal < value:
            return index
    raise ValueError(f"{goal} is out of bounds")

index = find_closest(data, 91234.56)
assert index == 91235
```

Python’s built-in `bisect` module provides better ways to accomplish these types of searches through ordered lists. You can use the `bisect_left` function to do an efficient binary search through any sequence of sorted items. The index it returns will either be where the item is already present in the `list` , or where you’d want to insert the item in the `list` to keep it in sorted order:

Python 的内置模块 `bisect` 提供了更好的方法来完成这种类型的有序列表搜索。你可以使用 `bisect_left` 函数通过任何排序项序列进行高效的二分查找。它返回的索引要么是你已经在列表中存在的项目的索引，要么是你想将该项目插入到列表中的位置以保持排序顺序：

```
from bisect import bisect_left

index = bisect_left(data, 91234)     # Exact match
assert index == 91234

index = bisect_left(data, 91234.56)  # Closest match
assert index == 91235
```

The complexity of the binary search algorithm used by the `bisect` module is logarithmic. This means searching in a `list` of length 1 million takes roughly the same amount of time with `bisect` as linearly searching a `list` of length 20 using the `list.index` method ( `math.log2(10**6) == 19.93...` ). It’s way faster!

由 `bisect` 模块使用的二分查找算法的复杂度是对数级的。这意味着在一个一百万长度的列表中使用 `bisect` 进行搜索所花的时间大致相当于在线性搜索一个二十长度的列表中使用 `list.index` 方法（`math.log2(10**6) == 19.93...`）。速度要快得多！

I can verify this speed improvement for the example from above by using the `timeit` built-in module to run a microbenchmark (see Item 93: “Optimize Performance-Critical Code Using `timeit` Microbenchmarks” for details):

我可以通过使用 `timeit` 内置模块运行微基准测试来验证上面例子中的速度提升（详情请参见条目93：“使用 `timeit` 微基准优化性能关键代码”）：

```
import random
import timeit

size = 10**5
iterations = 1000

data = list(range(size))
to_lookup = [random.randint(0, size) for _ in range(iterations)]

def run_linear(data, to_lookup):
    for index in to_lookup:
        data.index(index)

def run_bisect(data, to_lookup):
    for index in to_lookup:
        bisect_left(data, index)

baseline = (
    timeit.timeit(
        stmt="run_linear(data, to_lookup)",
        globals=globals(),
        number=10,
    )
    / 10
)
print(f"Linear search takes {baseline:.6f}s")

comparison = (
    timeit.timeit(
        stmt="run_bisect(data, to_lookup)",
        globals=globals(),
        number=10,
    )
    / 10
)
print(f"Bisect search takes {comparison:.6f}s")

slowdown = 1 + ((baseline - comparison) / comparison)
print(f"{slowdown:.1f}x slower")

>>>
Linear search takes 0.317685s
Bisect search takes 0.000197s
1610.1x time
```


The best part about `bisect` is that it’s not limited to the `list` type; you can use it with any Python object that acts like a sequence (see Item 57: “Inherit from `collections.abc` Classes for Custom Container Types” for how to do that) containing values that have a natural ordering (see Item 104: “Know How to Use `heapq` for Priority Queues” for background). The module also provides additional features for more advanced situations (see `https://docs.python.org/3/library/bisect.html`).

关于 `bisect` 的最佳部分是它不仅限于 `list` 类型；你可以将其与任何表现得像序列的 Python 对象一起使用（如何做到这一点，请参见条目57：“为自定义容器类型继承自 `collections.abc` 类”），只要它们包含具有自然排序的值（背景信息，请参见条目104：“了解如何使用 `heapq` 实现优先队列”）。该模块还提供了更多功能以应对更高级的情况（更多信息请访问 `https://docs.python.org/3/library/bisect.html`）。

**Things to Remember**
- Searching sorted data contained in a `list` takes linear time using the `index` method or a for loop with simple comparisons.
- The `bisect` built-in module’s `bisect_left` function takes logarithmic time to search for values in sorted lists, which can be orders of magnitude faster than other approaches.

**注意事项**
- 使用 `index` 方法或带有简单比较的 for 循环在 `list` 中搜索排序数据需要线性时间。
- `bisect` 内置模块的 `bisect_left` 函数可以在对数时间内搜索排序列表中的值，这通常比其他方法快几个数量级。