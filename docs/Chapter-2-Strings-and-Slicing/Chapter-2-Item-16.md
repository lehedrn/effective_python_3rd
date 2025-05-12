# Chapter 2: Strings and Slicing (字符串和切片操作)

## Item 16: Prefer Catch-All Unpacking Over Slicing (倾向于使用捕获所有项的解包而不是切片操作)

One limitation of basic unpacking (see Item 5: “Prefer Multiple Assignment Unpacking Over Indexing”) is that you must know the length of the sequences you’re unpacking in advance. For example, here I have a list of the ages of cars that are being traded in at a car dealership. When I try to take the first two items of the list with basic unpacking, an exception is raised at runtime:

基本解包的一个限制（参见条目5）是你必须提前知道你要解包的序列的长度。例如，这里有一个汽车经销商处交易的汽车年龄列表。当我尝试使用基本解包获取列表的前两个项目时，在运行时会引发异常：

```
car_ages = [0, 9, 4, 8, 7, 20, 19, 1, 6, 15]
car_ages_descending = sorted(car_ages, reverse=True)
oldest, second_oldest = car_ages_descending

>>>
Traceback ...
ValueError: too many values to unpack (expected 2)
```

Newcomers to Python often rely on indexing and slicing (see Item 14: “Know How to Slice Sequences”) for this situation. For example, here I extract the oldest, second oldest, and other car ages from a list of at least two items:

Python的初学者通常依赖索引和切片（参见条目14）来应对这种情况。例如，这里我从至少包含两个项目的列表中提取最老、第二老和其他车辆的年龄：

```
oldest = car_ages_descending[0]
second_oldest = car_ages_descending[1]
others = car_ages_descending[2:]
print(oldest, second_oldest, others)
>>>
20 19 [15, 9, 8, 7, 6, 4, 1, 0]
```

This works, but all of the indexing and slicing is visually noisy. In practice, it’s also error prone to divide the members of a sequence into various subsets this way because you’re much more likely to make off-by-one errors; for example, you might change boundaries on one line and forget to update the others.

这确实有效，但所有的索引和切片在视觉上很杂乱。实际上，通过这种方式将序列的成员分成各种子集也容易出错，因为你更可能犯边界错误；例如，你可能在一个行上更改了边界而忘记更新其他行。

To better handle this situation, Python also supports catch-all unpacking through a starred expression. This syntax allows one part of the unpacking assignment to receive all values that didn’t match any other part of the unpacking pattern. Here, I use a starred expression to achieve the same result as above without any indexing or slicing:

为了更好地处理这种情况，Python还支持通过星号表达式进行捕获所有项的解包。此语法允许解包分配的一部分接收未匹配到解包模式任何其他部分的所有值。在这里，我使用星号表达式实现与上述相同的结果，而无需任何索引或切片：

```
oldest, second_oldest, *others = car_ages_descend
print(oldest, second_oldest, others)
>>>
20 19 [15, 9, 8, 7, 6, 4, 1, 0]
```

This code is shorter, easier to read, and no longer has the error-prone brittleness of boundary indexes that must be kept in sync between lines.

这段代码更简短，更易于阅读，并且不再有需要保持同步的易出错的边界索引的脆弱性。

A starred expression may appear in any position—start, middle, or end—so you can get the benefits of catch-all unpacking anytime you need to extract one optional slice (see match for another situation where this is useful):

星号表达式可以出现在任何位置——开始、中间或末尾——因此当你需要提取一个可选切片时，可以在任何时候使用捕获所有项的解包的好处（另见匹配以了解另一个有用的情况）：

```
oldest, *others, youngest = car_ages_descending
print(oldest, youngest, others)

*others, second_youngest, youngest = car_ages_descending
print(youngest, second_youngest, others)

>>>
20 0 [19, 15, 9, 8, 7, 6, 4, 1]
0 1 [20, 19, 15, 9, 8, 7, 6, 4]
```

However, to unpack assignments that contain a starred expression, you must have at least one required part, or else you’ll get a `SyntaxError` . You can’t use a catch-all expression on its own:

但是，要进行包含星号表达式的解包赋值，你必须至少有一个必需的部分，否则你会得到一个`SyntaxError`。你不能单独使用捕获所有项的表达式：

```
*others = car_ages_descending
>>>
Traceback ...
SyntaxError: starred assignment target must be in
```

You also can’t use multiple catch-all expressions in a single unpacking pattern:

你也不能在单个解包模式中使用多个捕获所有项的表达式：

```
first, *middle, *second_middle, last = [1, 2, 3, 4]
>>>
Traceback ...
SyntaxError: multiple starred expressions in assi
```

But it is possible to use multiple starred expressions in an unpacking assignment statement, as long as they’re catch-alls for different levels of the nested structure being unpacked. I don’t recommend doing the following (see Item 30: “Never Unpack More Than Three Variables When Functions Return Multiple Values” for related guidance), but understanding it should help you develop an intuition for how starred expressions can be used in unpacking assignments:

但是，只要它们是为被解包的嵌套结构的不同层级捕获所有项，就可以在解包赋值语句中使用多个星号表达式。我不建议这样做（参见条目30），但理解它应该有助于你开发对星号表达式在解包赋值中的使用直觉：

```
car_inventory = {
    "Downtown": ("Silver Shadow", "Pinto", "DMC"),
    "Airport": ("Skyline", "Viper", "Gremlin", "Nova"),
}
((loc1, (best1, *rest1)),
 (loc2, (best2, *rest2))) = car_inventory.items()
print(f"Best at {loc1} is {best1}, {len(rest1)} others")
print(f"Best at {loc2} is {best2}, {len(rest2)} others")
```

Starred expressions become `list` instances in all cases. If there are no leftover items from the sequence being unpacked, the catch-all part will be an empty `list` . This is especially useful when you’re processing a sequence that you know in advance has at least N elements:

在所有情况下，星号表达式都会变成list实例。如果从正在解包的序列中没有剩余项目，则捕获所有项的部分将是一个空的list。当你处理预先知道长度至少为N的序列时，这特别有用：

```
short_list = [1, 2]
first, second, *rest = short_list
print(first, second, rest)
>>>
1 2 []
```

You can also unpack arbitrary iterators with the unpacking syntax. This isn’t worth much with a basic multiple-assignment statement. For example, here I unpack the values from iterating over a `range` of length 2. This doesn’t seem useful because it would be easier to just assign to a static `list` that matches the unpacking pattern (e.g., `[1, 2]` ):

你也可以使用解包语法解包任意迭代器。对于基本的多赋值语句来说，这并不太有价值。例如，这里我解包了一个从迭代器范围生成的值。这似乎不太有用，因为直接赋值给一个静态列表更简单（例如， `[1, 2]` ）：

```
it = iter(range(1, 3))
first, second = it
print(f"{first} and {second}")
>>>
1 and 2
```

But with the addition of starred expressions, the value of unpacking iterators becomes clear. For example, here I have a generator that yields the rows of a CSV (comma-separated values) file containing all car orders from the dealership this week:

但随着星号表达式的加入，解包迭代器的价值变得明显。例如，这里我有一个生成器，它按行生成本周该车行所有订单的CSV（逗号分隔值）文件：

```
def generate_csv():
    yield ("Date", "Make", "Model", "Year", "Price")
    for i in range(100):
        yield ("2019-03-25", "Honda", "Fit", "2010", "$3400")
        yield ("2019-03-26", "Ford", "F150", "2008", "$2400")
```

Processing the results of this generator using indexes and slices is fine, but it requires multiple lines and is visually noisy:

使用索引和切片处理这个生成器的结果是可以的，但它需要多行并且视觉上很杂乱：

```
all_csv_rows = list(generate_csv())
header = all_csv_rows[0]
rows = all_csv_rows[1:]
print("CSV Header:", header)
print("Row count: ", len(rows))

>>>
CSV Header: ('Date', 'Make', 'Model', 'Year', 'Prrice')
Row count: 200
```

Unpacking with a starred expression makes it easy to process the first row—the header—separately from the rest of the iterator’s contents. This is much clearer:

使用带有星号表达式的解包使得处理第一行——标题行——与其他迭代器内容分开变得很容易。这更加清晰：

```
it = generate_csv()
header, *rows = it
print("CSV Header:", header)
print("Row count: ", len(rows))
>>>
CSV Header: ('Date', 'Make', 'Model', 'Year', 'Pr
Row count: 200
```

Keep in mind, however, that because a starred expression is always turned into a `list` , unpacking an iterator also risks the potential of using up all of the memory on your computer and causing your program to crash (see memory for how to debug this). So you should only use catch-all unpacking on iterators when you have good reason to believe that the result data will all fit in memory (see Item 20: “Be Defensive When Iterating Over Arguments” for another approach).

不过，请记住，由于星号表达式始终转换为一个list，解包迭代器也会导致计算机内存耗尽并使程序崩溃的风险（参见内存了解如何调试）。因此，只有当你有充分理由相信结果数据能完全装入内存时才应使用捕获所有项的解包（另见条目20以了解另一种方法）。

**Things to Remember**
- Unpacking assignments may use a starred expression to store all values that weren’t assigned to the other parts of the unpacking pattern in a `list` .
- Starred expressions may appear in any position of the unpacking pattern. They will always become a `list` instance containing zero or more values.
- When dividing a `list` into non-overlapping pieces, catch-all unpacking is much less error prone than separate statements that do slicing and indexing.

**注意事项**

- 解包赋值可能会使用一个星号表达式来存储未分配给解包模式其他部分的所有值，并将其保存在一个list中。
- 星号表达式可以出现在解包模式的任何位置。它们总是会成为包含零个或多个值的list实例。
- 在将一个list分割成不重叠的部分时，捕获所有项的解包比单独使用切片和索引的语句更少出错。