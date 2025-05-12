# Chapter 2: Strings and Slicing (字符串和切片操作)

## Item 15: Avoid Striding and Slicing in a Single Expression (避免在单个表达式中使用步长和切片)

In addition to basic slicing (see Item 14: "Know How to Slice Sequences"), Python has special syntax for the stride of a slice in the form `somelist[start:end:stride]` . This lets you take every nth item when slicing a sequence. For example, the stride makes it easy to group by even and odd ordinal positions in a `list` :

除了基本的切片之外（参见条目14："知道如何切片序列"），Python还有一种特殊的语法用于切片的步长，形式为`somelist[start:end:stride]`。这允许你在切片一个序列时取每一个第n个元素。例如，步长使得很容易根据偶数和奇数位置从一个list中分组选取元素：

```
x = ["red", "orange", "yellow", "green", "blue", "purple"]
odds = x[::2]    # First, third, fifth
evens = x[1::2]  # Second, fourth, sixth
print(odds)
print(evens)
```

The problem is that the stride syntax often causes unexpected behavior that can introduce bugs. For example, a common Python trick for reversing a byte string is to slice the string with a stride of `-1` :

问题在于，步长语法经常会导致意外的行为，从而引入错误。例如，一个常见的Python技巧是用步长为`-1`来反转一个字节字符串：

```
x = b"mongoose"
y = x[::-1]
print(y)
>>>
b'esoognom'
```

This also works correctly for Unicode strings (see Item 10: "Know the Differences Between bytes and str"):

这对于Unicode字符串同样有效（参见条目10："知道bytes和str之间的区别"）:

```
x = " "
y = x[::-1]
print(y)

>>>

```

But it will break when Unicode data is encoded as a UTF-8 byte string:

但是当Unicode数据被编码为UTF-8字节字符串时会出错：

```
w = " "
x = w.encode("utf-8")
y = x[::-1]
z = y.decode("utf-8")
>>>
Traceback ...
UnicodeDecodeError: 'utf-8' codec can't decode by position 0: invalid start byte
```

Are negative strides besides `-1` useful? Consider the following examples:

除了-1以外的负步长是否有用？考虑以下示例：

```
x = ["a", "b", "c", "d", "e", "f", "g", "h"]
x[::2]  # ["a", "c", "e", "g"]
x[::-2] # ["h", "f", "d", "b"]
```

Here, `::2` means “Select every second item starting at the beginning.” Trickier, `::-2` means “Select every second item starting at the end and moving backward.”

这里，`::2`的意思是“从开始每隔一个项目选一个”。更难一点，`::-2`的意思是“从末尾开始向后移动，每第二个项选一个”。

What do you think `2::2` means? What about `-2::-2` vs. `-2:2:-2` vs. `2:2:-2` ?

你觉得`2::2`是什么意思？`-2::-2`与`-2:2:-2`或`2:2:-2`相比呢？

```
x[2::2]     # ["c", "e", "g"]
x[-2::-2]   # ["g", "e", "c", "a"]
x[-2:2:-2]  # ["g", "e"]
x[2:2:-2]   # []
>>>
['c', 'e', 'g']
['g', 'e', 'c', 'a']
['g', 'e']
[]
```

The point is that the stride part of the slicing syntax can be extremely confusing. Having three numbers within the brackets is hard enough to read because of its density. Then, it’s not obvious when the start and end indexes come into effect relative to the stride value, especially when the stride is negative.

重点是，切片语法中的步长部分可能会极其令人困惑。由于其密集性，在括号内有三个数字已经很难阅读了。然后，相对于步长值而言，起始和结束索引何时生效并不明显，尤其是当步长为负时。

To prevent problems, I suggest you avoid using a stride along with start and end indexes. If you must use a stride, prefer making it a positive value and omit start and end indexes. If you must use a stride with start or end indexes, consider using one assignment for striding and another for slicing:

为了避免问题，我建议避免在同一个切片中使用步长以及起始和结束索引。如果必须使用步长，请尽量将其设为正值并省略起始和结束索引。如果您必须在起始或结束索引中使用步长，请考虑使用一次赋值进行步长操作，另一次进行切片操作：

```
y = x[::2]  # ["a", "c", "e", "g"]
z = y[1:-1] # ["c", "e"]
```

Striding and then slicing creates an extra shallow copy of the data. The first operation should try to reduce the size of the resulting slice by as much as possible. If your program can’t afford the time or memory required for two steps, consider using the `itertools` built-in module’s `islice` method (see Item 23: "Consider itertools for Working with Iterators and Generators"), which is clearer to read and doesn’t permit negative values for start, end, or stride.

步长操作然后再切片会创建一个数据的额外浅拷贝。第一次操作应尽可能减少结果切片的大小。如果你的程序无法承担两步所需的时间或内存，请考虑使用itertools内置模块的islice方法（参见条目23），它读起来更加清晰，并且不允许start、end或stride为负值。

**Things to Remember**

- Specifying start, end, and stride together in a single slice can be extremely confusing.
- If striding is necessary, try to use only positive stride values without start or end indexes; avoid negative stride values.
- If you need start, end, and stride in a single slice, consider doing two assignments (one to stride and another to slice) or using `islice` from the `itertools` built-in module.

**注意事项**

- 在单个切片中同时指定起始、结束和步长可能会非常混乱。
- 如果必须使用步长，请尝试仅使用正的步长值而不指定起始或结束索引；避免使用负的步长值。
- 如果您需要在一个切片中使用起始、结束和步长，请考虑执行两次赋值（一次用于步长，另一次用于切片）或使用来自`itertools`内置模块的`islice`函数。