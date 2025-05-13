# Chapter 3: Loops and Iterators (循环和迭代器)

## Item 17: Prefer enumerate over range (优先使用 enumerate 而不是 range)


The `range` built-in function is useful for loops that iterate over a set of integers. For example, here I generate a 32-bit random number by flipping a coin for each bit position:

内置的 `range` 函数在遍历一组整数的循环中非常有用。例如，下面我通过每一位都抛硬币来生成一个 32 位的随机数：

```
from random import randint

random_bits = 0
for i in range(32):
    if randint(0, 1):
        random_bits |= 1 << i

print(bin(random_bits))

>>>
0b11101000100100000111000010000001
```

When you have a data structure to iterate over, like a `list` of strings, you can loop directly over the sequence:

当你有一个数据结构需要遍历，比如一个字符串列表时，你可以直接循环遍历这个序列：

```
flavor_list = ["vanilla", "chocolate", "pecan", "strawberry"]
for flavor in flavor_list:
    print(f"{flavor} is delicious")
>>>
vanilla is delicious
chocolate is delicious
pecan is delicious
strawberry is delicious
```

Often, you’ll want to iterate over a `list` and also know the index of the current item in the `list` . For example, say that I want to print the ranking of my favorite ice cream flavors. One way to do this is by using range to generate offsets for each position in the `list` :

通常，你可能希望遍历一个列表并同时知道当前项在列表中的索引。例如，假设我想打印出我最喜欢的冰淇淋口味的排名。一种方法是使用 range 生成列表中每个位置的偏移量：

```
for i in range(len(flavor_list)):
    flavor = flavor_list[i]
    print(f"{i + 1}: {flavor}")
>>>
1: vanilla
2: chocolate
3: pecan
4: strawberry
```

This looks clumsy compared with the other examples of a `for` statement over `flavor_list` or `range` . I have to get the length of the `list` . I have to index into the array. The multiple steps make it harder to read.

与在 `flavor_list` 或 `range` 上的其他 `for` 语句相比，这看起来有些笨拙。我必须获取列表的长度，然后索引到数组中。多个步骤使代码更难阅读。

Python provides the `enumerate` built-in function to simplify this situation. `enumerate` wraps any iterator with a lazy generator (see Item 43: “Consider Generators Instead of Returning Lists”). `enumerate` yields pairs of the loop index and the next value from the given iterator. Here, I manually advance the returned iterator with the `next` built-in function to demonstrate what it does:

Python 提供了内置函数 `enumerate` 来简化这种情况。`enumerate` 使用一个惰性生成器包装任何迭代器（参见第 43 条）。`enumerate` 会生成由循环索引和来自给定迭代器的下一个值组成的对。这里我手动使用内置函数 `next` 推动返回的迭代器以演示其行为：

```
it = enumerate(flavor_list)
print(next(it))
print(next(it))
>>>
(0, 'vanilla')
(1, 'chocolate')
```

Each pair yielded by `enumerate` can be succinctly unpacked in a `for` statement (see Item 5: “Prefer Multiple Assignment Unpacking Over Indexing” for how that works). The resulting code is much clearer:

每次由 `enumerate` 生成的对都可以在 `for` 语句中简洁地解包（参见第 5 条）。由此产生的代码更加清晰：

```
for i, flavor in enumerate(flavor_list):
    print(f"{i + 1}: {flavor}")
>>>
1: vanilla
2: chocolate
3: pecan
4: strawberry
```

I can make this even shorter by specifying the number for `enumerate` to use to begin counting ( `1` in this case) as the second parameter:

通过指定 `enumerate` 的第二个参数作为起始计数值（在此情况下为 `1`），我可以进一步缩短这段代码：

```
for i, flavor in enumerate(flavor_list, 1):
    print(f"{i}: {flavor}")
```

**Things to Remember**
- `enumerate` provides concise syntax for looping over an iterator and getting the index of each item from the iterator as you go.
- Prefer `enumerate` instead of looping over a `range` and indexing into a sequence.
- You can supply a second, optional parameter to `enumerate` that specifies the beginning number for counting (zero is the default).

**注意事项**

- `enumerate` 提供了一个简洁的语法用于遍历一个迭代器，并在遍历时获得该项的索引。
- 优先选择 `enumerate` 而不是遍历 `range` 并索引到序列中。
- 你可以向 `enumerate` 提供第二个可选参数，该参数指定了开始计数的数字（默认是零）。