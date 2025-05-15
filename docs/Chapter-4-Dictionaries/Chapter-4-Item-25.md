# Chapter 4: Dictionaries (字典)

## Item 25: Be Cautious when Relying on Dictionary Insertion Ordering (在依赖字典插入顺序时要谨慎)

In Python versions 3.5 and earlier, iterating over a dictionary instance would return its keys in arbitrary order. The order of iteration would not match the order in which the items were inserted into the dictionary originally. For example, here I create a dictionary mapping animal names to their corresponding baby names:

在 Python 3.5 及更早版本中，遍历一个字典实例会以任意顺序返回其键。这意味着遍历的顺序不会与最初插入字典中的项的顺序一致。例如，我创建了一个将动物名称映射到其对应幼崽名称的字典：

```
# Python 3.5
baby_names = {
 "cat": "kitten",
 "dog": "puppy",
}
print(baby_names)
>>>
{'dog': 'puppy', 'cat': 'kitten'}
```

When I created the dictionary the keys were in the order `cat` , `dog` , but when I printed it the keys were in the reverse order `dog` , `cat` . This behavior is surprising, makes it harder to reproduce test cases, increases the difficulty of debugging, and is especially confusing to newcomers to Python. This happened because the dictionary type previously implemented its hash table algorithm with a combination of the hash built-in function and a random seed that was assigned when the Python interpreter process started executing. Together, these behaviors caused dictionary orderings to not match insertion order and to randomly shuffle between program executions.

当我在创建字典时，键的顺序是 `cat`、`dog`，但当我打印它时，键的顺序变成了相反的顺序 `dog`、`cat`。这是因为字典类型以前实现其哈希表算法时使用了内置的 hash 函数和一个在 Python 解释器启动时分配的随机种子。这些行为一起导致字典的顺序与插入顺序不匹配，并且在程序执行之间随机打乱。

Starting with Python 3.6, and officially part of the Python specification since version 3.7, dictionaries will preserve insertion order. Now, this code will always print the dictionary in the same way it was originally created by the programmer:

从 Python 3.6 开始，并在 3.7 版本正式成为 Python 规范的一部分后，字典将保留插入顺序。现在，这段代码将始终以程序员最初创建的方式打印字典：

```
baby_names = {
 "cat": "kitten",
 "dog": "puppy",
}
print(baby_names)
>>>
{'cat': 'kitten', 'dog': 'puppy'}
```

With Python 3.5 and earlier, all methods provided by `dict` that relied on iteration order, including `keys` , `values` , `items` , and `popitem` , would similarly demonstrate this random-looking behavior:

对于 Python 3.5 及更早版本，所有由 `dict` 提供的依赖于迭代顺序的方法（包括 `keys`、`values`、`items` 和 `popitem`）同样会展示这种看似随机的行为：

```
# Python 3.5
print(list(baby_names.keys()))
print(list(baby_names.values()))
print(list(baby_names.items()))
print(baby_names.popitem()) # Randomly chooses a
>>>
['dog', 'cat']
['puppy', 'kitten']
[('dog', 'puppy'), ('cat', 'kitten')]
('dog', 'puppy')
```

These methods now provide consistent insertion ordering that you can rely on when you write your programs:

这些方法现在提供了你可以依赖的一致插入顺序：

```
print(list(baby_names.keys()))
print(list(baby_names.values()))
print(list(baby_names.items()))
print(baby_names.popitem()) # Last item inserted
>>>
['cat', 'dog']
['kitten', 'puppy']
[('cat', 'kitten'), ('dog', 'puppy')]
('dog', 'puppy')
```

There are many repercussions of this change on other Python features that are dependent on the dict type and its specific implementation.

这一变化对其他依赖于 dict 类型及其特定实现的 Python 特性有许多影响。

Keyword arguments to functions—including the `**kwargs` catch-all parameter (see Item 35: “Provide Optional Behavior with Keyword Arguments” and Item 37: “Enforce Clarity with Keyword-Only and Positional-Only Arguments”)—previously would come through in seemingly random order, which can make it harder to debug function calls:

函数的关键字参数——包括 **kwargs 通配符参数（参见第 35 条 和 第 37 条）——以前会以看似随机的顺序传入，这可能会使调试函数调用变得困难：

```
# Python 3.5
def my_func(**kwargs):
    for key, value in kwargs.items():
        print("%s = %s" % (key, value))
my_func(goose="gosling", kangaroo="joey")
>>>
kangaroo = joey
goose = gosling
```

Now in the latest version of Python, the order of keyword arguments is always preserved to match how the programmer originally called the function:

现在在最新版本的 Python 中，关键字参数的顺序总是保留为与程序员最初调用函数时的顺序一致：

```
def my_func(**kwargs):
    for key, value in kwargs.items():
        print(f"{key} = {value}")
my_func(goose="gosling", kangaroo="joey")
>>>
goose = gosling
kangaroo = joey
```

Classes also use the `dict` type for their instance dictionaries. In previous versions of Python, `object` fields would show the randomizing behavior:

类也使用 `dict` 类型作为其实例字典。在之前的 Python 版本中，`object` 字段会显示随机化行为：

```
# Python 3.5
class MyClass:
    def __init__(self):
        self.alligator = "hatchling"
        self.elephant = "calf"
a = MyClass()
for key, value in a.__dict__.items():
    print("%s = %s" % (key, value))
>>>
elephant = calf
alligator = hatchling
```

Again, you can now assume that the order of assignment for these instance fields will be reflected in `__dict__` :

同样，现在可以假设这些实例字段的赋值顺序会在 `__dict__` 中反映出来：

```
class MyClass:
    def __init__(self):
        self.alligator = "hatchling"
        self.elephant = "calf"
a = MyClass()
for key, value in a.__dict__.items():
    print(f"{key} = {value}")
>>>
alligator = hatchling
elephant = calf
```

The way that dictionaries preserve insertion ordering is now part of the Python language specification. For the language features above, you can rely on this behavior and even make it part of the APIs you design for your classes and functions (see Item 65: “Consider Class Body Definition Order to Establish Sequential Relationships Between Attributes” for an example).

字典保留插入顺序的方式现在已成为 Python 语言规范的一部分。对于上述语言特性，您可以依赖此行为，甚至可以将其作为您为类和函数设计的 API 的一部分（参见第 65 条）。

> Note
For a long time the `collections` built-in module has had an `OrderedDict` class that preserves insertion ordering. Although this class’s behavior is similar to that of the standard `dict` type (since Python 3.7), the performance characteristics of `OrderedDict` are quite different. If you need to handle a high rate of key insertions and `popitem` calls (e.g., to implement a least-recently-used cache), `OrderedDict` may be a better fit than the standard Python `dict` type (see Item 92: “Profile Before Optimizing” on how to make sure you need this).

> 注意 
长期以来，collections 内置模块都有一个 OrderedDict 类，用于保留插入顺序。尽管该类的行为类似于标准 dict 类型（自 Python 3.7 起），但 OrderedDict 的性能特征却大相径庭。如果您需要处理高频率的键插入和 popitem 调用（例如，实现最近最少使用缓存），OrderedDict 可能比标准 Python dict 类型更适合（参见第 92 条）。

---

However, you shouldn’t always assume that insertion ordering behavior will be present when you’re handling dictionaries. Python makes it easy for programmers to define their own custom container types that emulate the standard protocols matching `list` , `dict` , and other types (see Item 57: “Inherit from collections.abc for Custom Container Types”).

但是，在处理字典时，你不应该总是假定插入顺序会被保留。Python 让程序员很容易定义自己的容器类型，这些容器类型模拟了 `list`、`dict` 等标准协议的行为（参见第 57 条）。

Python is not statically typed, so most code relies on duck typing—where an object’s behavior is its de facto type—instead of rigid class hierarchies (see Item 3: “Never Expect Python to Detect Errors at Compile Time”). This can result in surprising gotchas.

Python 不是静态类型的，所以大多数代码依赖于鸭子类型——即对象的行为是其实际类型——而不是严格的类层次结构（参见第 3 条）。这可能导致令人意外的问题。

For example, say that I’m writing a program to show the results of a contest for the cutest baby animal. Here, I start with a dictionary containing the total vote count for each one:

例如，假设我正在编写一个程序来展示一场可爱宝宝动物比赛的结果。在这里，我从一个包含每个动物总投票数的字典开始：

```
votes = {
 "otter": 1281,
 "polar bear": 587,
 "fox": 863,
}
```

Now, I define a function to process this voting data and save the rank of each animal name into a provided empty dictionary. In this case, the dictionary could be the data model that powers a UI element:

现在，我定义一个函数来处理这些投票数据，并将每个动物名称的排名保存到提供的空字典中。在这种情况下，这个字典可能是支持 UI 元素的数据模型：

```
def populate_ranks(votes, ranks):
    names = list(votes.keys())
    names.sort(key=votes.get, reverse=True)
    for i, name in enumerate(names, 1):
        ranks[name] = i
```

I also need a function that will tell me which animal won the contest. This function works by assuming that `populate_ranks` will assign the contents of the `ranks` dictionary in ascending order, meaning that the first key must be the winner:

我也需要一个告诉我哪个动物赢得比赛的函数。这个函数的工作原理是假设 `populate_ranks` 会按升序分配 `ranks` 字典的内容，这意味着第一个键必须是获胜者：

```
def get_winner(ranks):
    return next(iter(ranks))
```

Here, I confirm that these functions work as designed and deliver the result that I expected:

这里，我确认这些函数按照设计工作并交付预期结果：

```
ranks = {}
populate_ranks(votes, ranks)
print(ranks)
winner = get_winner(ranks)
print(winner)
>>>
{'otter': 1, 'fox': 2, 'polar bear': 3}
otter
```

Now, imagine that the requirements of this program have changed. The UI element that shows the results should be in alphabetical order instead of rank order. To accomplish this, I can use the `collections.abc` built-in module to define a new dictionary-like class that iterates its contents in alphabetical order:

现在，想象这个程序的需求已经改变。显示结果的 UI 元素应该按字母顺序而不是排名顺序。为了实现这一点，我可以使用 `collections.abc` 内置模块来定义一个新的类似字典的类，该类以其内容按字母顺序迭代：

```
from collections.abc import MutableMapping
class SortedDict(MutableMapping):
    def __init__(self):
        self.data = {}
    def __getitem__(self, key):
        return self.data[key]
    def __setitem__(self, key, value):
        self.data[key] = value
    def __delitem__(self, key):
        del self.data[key]
    def __iter__(self):
        keys = list(self.data.keys())
        keys.sort()
        for key in keys:
            yield key
    def __len__(self):
        return len(self.data)
```

I can use a `SortedDict` instance in place of a standard `dict` with the functions from before and no errors will be raised since this class conforms to the protocol of a standard dictionary. However, the results are incorrect:

我可以在之前的功能中使用一个 `SortedDict` 实例代替标准 `dict`，并且不会引发任何错误，因为此类符合标准字典的协议。然而，结果是错误的：

```
sorted_ranks = SortedDict()
populate_ranks(votes, sorted_ranks)
print(sorted_ranks.data)
winner = get_winner(sorted_ranks)
print(winner)
>>>
{'otter': 1, 'fox': 2, 'polar bear': 3}
fox
```

The problem here is that the implementation of `get_winner` assumes that the dictionary’s iteration is in insertion order to match `populate_ranks` . This code is using `SortedDict` instead of `dict` , so that assumption is no longer true. Thus, the value returned for the winner is `'fox'` , which is alphabetically first.

这里的问题在于 `get_winner` 的实现假设字典的迭代顺序与其插入顺序匹配。这段代码使用的是 `SortedDict` 而不是 `dict`，因此这个假设不再成立。因此，返回的获胜者是按字母顺序的第一个 'fox'。

There are three ways to mitigate this problem. First, I can reimplement the `get_winner` function to no longer assume that the `ranks` dictionary has a specific iteration order. This is the most conservative and robust solution:

有三种方法可以缓解这个问题。首先，我可以重新实现 `get_winner` 函数，使其不再假设 `ranks` 字典具有特定的迭代顺序。这是最保守且最稳健的解决方案：

```
def get_winner(ranks):
    for name, rank in ranks.items():
        if rank == 1:
            return name
winner = get_winner(sorted_ranks)
print(winner)
>>>
otter
```

The second approach is to add an explicit check to the top of the function to ensure that the type of `ranks` matches my expectations, and to raise an exception if not. This solution likely has better runtime performance than the more conservative approach:

第二种方法是在函数顶部添加一个显式检查，以确保 `ranks` 的类型符合我的预期，并在不符合时引发异常。相比更为保守的方法，这种解决方案可能具有更好的运行时性能：

```
def get_winner(ranks):
    if not isinstance(ranks, dict):
        raise TypeError("must provide a dict instance")
    return next(iter(ranks))
get_winner(sorted_ranks)
>>>
Traceback ...
TypeError: must provide a dict instance
```

The third alternative is to use type annotations to enforce that the value passed to `get_winner` is a `dict` instance and not a `MutableMapping` with dictionary-like behavior (see Item 124: “Consider Static Analysis via typing to Obviate Bugs”). Here, I run the `mypy` tool in strict mode on a type-annotated version of the code above:

第三种替代方案是使用类型注解来强制传递给 `get_winner` 的值是一个 `dict` 实例，而不仅仅是一个具有字典行为的 `MutableMapping`（参见第 124 条）。在这里，我在严格模式下运行 `mypy` 工具对上面的类型注解代码进行检查：

```
from typing import Dict, MutableMapping

def populate_ranks(votes: Dict[str, int], ranks: Dict[str, int]) -> None:
    names = list(votes.keys())
    names.sort(key=votes.__getitem__, reverse=True)
    for i, name in enumerate(names, 1):
        ranks[name] = i

def get_winner(ranks: Dict[str, int]) -> str:
    return next(iter(ranks))

from typing import Iterator, MutableMapping

class SortedDict(MutableMapping[str, int]):
    def __init__(self) -> None:
        self.data: Dict[str, int] = {}

    def __getitem__(self, key: str) -> int:
        return self.data[key]

    def __setitem__(self, key: str, value: int) -> None:
        self.data[key] = value

    def __delitem__(self, key: str) -> None:
        del self.data[key]

    def __iter__(self) -> Iterator[str]:
        keys = list(self.data.keys())
        keys.sort()
        for key in keys:
            yield key

    def __len__(self) -> int:
        return len(self.data)


votes = {
    "otter": 1281,
    "polar bear": 587,
    "fox": 863,
}

sorted_ranks = SortedDict()
populate_ranks(votes, sorted_ranks)
print(sorted_ranks.data)
winner = get_winner(sorted_ranks)
print(winner)

$ python3 -m mypy --strict example.py

```

This correctly detects the mismatch between the `dict` and `SortedDict` types and flags the incorrect usage as an error. This solution provides the best mix of static type safety and runtime performance.

这正确地检测到了 `dict` 和 `SortedDict` 类型之间的不匹配，并将错误的使用标记为错误。这种解决方案提供了最佳的静态类型安全性和运行时性能组合。

**Things to Remember**
- Since Python 3.7, you can rely on the fact that iterating a dictionary instance’s contents will occur in the same order in which the keys were initially added.
- Python makes it easy to define objects that act like dictionaries but that aren’t `dict` instances. For these types, you can’t assume that insertion ordering will be preserved.
- There are three ways to be careful about dictionary-like classes: Write code that doesn’t rely on insertion ordering, explicitly check for the `dict` type at runtime, or require `dict` values using type annotations and static analysis.

**注意事项**
- 自 Python 3.7 起，您可以依靠字典实例内容的迭代顺序与其初始添加键的顺序相同。
- Python 使得定义行为像字典但不是 `dict` 实例的对象变得简单。对于这些类型，您不能假设插入顺序将被保留。
- 对于类似字典的类，有三种需要注意的方法：编写不依赖插入顺序的代码、在运行时显式检查 `dict` 类型，或使用类型注解和静态分析要求 `dict` 值。