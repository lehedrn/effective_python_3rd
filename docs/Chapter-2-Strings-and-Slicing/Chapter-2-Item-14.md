# Chapter 2: Strings and Slicing (字符串和切片操作)

## Item 14: Know How to Slice Sequences (了解如何对序列进行切片)

Python includes syntax for slicing sequences into pieces. Slicing allows you to access a subset of a sequence’s items with minimal effort. The simplest uses for slicing are the built-in types `list` , `tuple` , `str` , and `bytes` . Slicing can be extended to any Python class that implements the `__getitem__` and `__setitem__` special methods (see Item 56: "Inherit from collections.abc for Custom Container Types"). 

Python 包含用于将序列切分为部分的语法。切片允许您以最小的努力访问序列子集的项目。切片最简单的用途是内置类型 `list`、`tuple`、`str` 和 `bytes`。切片可以扩展到任何实现了 `getitem` 和 `setitem` 特殊方法的 Python 类（参见第56项）。

The basic form of the slicing syntax is `somelist[start:end]` , where start is inclusive and end is exclusive:

切片语法的基本形式是 somelist[start:end]，其中 start 是包含的而 end 是不包含的：

```
a = ["a", "b", "c", "d", "e", "f", "g", "h"]
print("Middle two: ", a[3:5])
print("All but ends:", a[1:7])
>>>
Middle two: ['d', 'e']
All but ends: ['b', 'c', 'd', 'e', 'f', 'g']
```

When slicing from the start of a sequence, you should leave out the zero index to reduce visual noise:

当从序列的开头进行切片时，应该省略零索引以减少视觉噪音：

```
assert a[:5] == a[0:5]
```

When slicing to the end of a sequence, you should leave out the final index because it’s redundant:

当切片到序列的末尾时，应该省略最后的索引，因为它是冗余的：

```
assert a[5:] == a[5:len(a)]
```

Using negative numbers for slicing is helpful for doing offsets relative to the end of a sequence. All of these forms of slicing would be clear to a new reader of your code:

使用负数进行切片有助于相对于序列末尾进行偏移。所有这些切片形式对于代码的新读者来说都是清晰的：

```
a[:]      # ["a", "b", "c", "d", "e", "f", "g", "h"]
a[:5]     # ["a", "b", "c", "d", "e"]
a[:-1]    # ["a", "b", "c", "d", "e", "f", "g"]
a[4:]     #                     ["e", "f", "g", "h"]
a[-3:]    #                          ["f", "g", "h"]
a[2:5]    #           ["c", "d", "e"]
a[2:-1]   #           ["c", "d", "e", "f", "g"]
a[-3:-1]  #                          ["f", "g"]
```

There are no surprises here, and I encourage you to use these variations.

这里没有意外情况，我鼓励您使用这些变化形式。

Slicing deals properly with start and end indexes that are beyond the boundaries of a `list` by silently omitting missing items. This behavior makes it easy for your code to establish a maximum length to consider for an input sequence:

切片正确处理了超出列表边界起始和结束索引的情况，通过静默省略缺失项来实现。这种行为使得您的代码很容易为输入序列建立一个最大长度考虑：

```
first_twenty_items = a[:20]
last_twenty_items = a[-20:]
```

In contrast, directly accessing the same missing index causes an exception:

相比之下，直接访问相同的缺失索引会导致异常：

```
a[20]
>>>
Traceback ...
IndexError: list index out of range
```

---

> Note
Beware that indexing a `list` by a negated variable is one of the few situations in which you can get surprising results from slicing. For example, the expression `somelist[-n:]` will work fine when n is greater than zero (e.g., `somelist[-3:]` when `n` is `3` ). However, when `n` is zero, the expression `somelist[-0:]` is equivalent to `somelist[:]` , which results in a copy of the original `list` .

> 注意 
请注意，用否定变量索引列表是少数几种可能从切片中得到令人惊讶结果的情况之一。例如，表达式 somelist[-n:] 在 n 大于零时会正常工作（例如，当 n 是 3 时的 somelist[-3:]）。然而，当 n 为零时，表达式 somelist[-0:] 等同于 somelist[:]，这将导致产生原始列表的一个副本。

---

The result of slicing a `list` is a whole new `list` . Each of the items in the new `list` will refer to the corresponding objects from the original `list` . Modifying the `list` created by slicing won’t affect the contents of the original `list` :

切片列表的结果是一个全新的列表。新列表中的每个项目都将引用原始列表中的对应对象。修改由切片创建的列表不会影响原始列表的内容：

```
b = a[3:]
print("Before: ", b)
b[1] = 99
print("After: ", b)
print("No change:", a)

>>>
Before: ['d', 'e', 'f', 'g', 'h']
After: ['d', 99, 'f', 'g', 'h']
No change: ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h]
```

When used in assignments, slices replace the specified range in the original `list` . Unlike unpacking assignments (like `a, b = c[:2]` ; see Item 5: "Prefer Multiple Assignment Unpacking Over Indexing" and catch all), the lengths of slice assignments don’t need to be the same. All of the values before and after the assigned slice will be preserved, with the new values stitched in between. Here, the `list` shrinks because the replacement `list` is shorter than the specified slice:

在赋值中使用时，切片替换原始列表中指定范围内的内容。与解包赋值（如 a, b = c[:2]；参见第5项）不同，切片赋值的长度不需要相同。指定切片之前和之后的所有值都将被保留，并在中间缝合新的值。在这里，列表变短了，因为替换的列表比指定的切片短：

```
print("Before ", a)
a[2:7] = [99, 22, 14]
print("After ", a)
>>>
Before ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
After ['a', 'b', 99, 22, 14, 'h']
```

And here the `list` grows because the assigned `list` is longer than the specific slice:

在这里，列表变长了，因为分配的列表比特定切片长：

```
print("Before ", a)
a[2:3] = [47, 11]
print("After ", a)

>>>
Before ['a', 'b', 99, 22, 14, 'h']
After ['a', 'b', 47, 11, 22, 14, 'h']
```

If you leave out both the start and the end indexes when slicing, you end up with a copy of the whole original `list` :

如果您在切片时同时省略起始和结束索引，最终将获得原始列表的完整副本：

```
b = a[:]
assert b == a and b is not a
```

If you assign to a slice with no start or end indexes, you replace the entire contents of the `list` with references to the items from the sequence on the right side (instead of allocating a new `list` ):

如果您给一个没有起始或结束索引的切片赋值，则会用右侧序列中的项目引用替换列表的全部内容（而不是分配一个新的列表）

```
b = a
print("Before a", a)
print("Before b", b)
a[:] = [101, 102, 103]
assert a is b             # Still the same list object
print("After a ", a)      # Now has different contents
print("After b ", b)      # Same list, so same contents as a
>>>
Before a ['a', 'b', 47, 11, 22, 14, 'h']
Before b ['a', 'b', 47, 11, 22, 14, 'h']
After a [101, 102, 103]
After b [101, 102, 103]
```

**Things to Remember**
- Avoid being verbose when slicing: Don’t supply 0 for the start index or the length of the sequence for the end index.
- Slicing is forgiving of start or end indexes that are out of bounds, which means it’s easy to express slices on the front or back boundaries of a sequence (like `a[:20]` or `a[-20:]` ).
- Assigning to a `list` slice replaces that range in the original sequence with what’s referenced even when the lengths are different.

**注意事项**
- 切片时避免冗长：不要提供 0 作为起始索引或序列长度作为结束索引。
- 切片对于超出列表边界的起始或结束索引非常宽容，这意味着很容易在序列的前边界或后边界上表达切片（比如 a[:20] 或 a[-20:]）。
- 给列表切片赋值会在原始序列中替换该范围内的内容，即使长度不同也是如此。