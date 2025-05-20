# Chapter 7: Classes and Interfaces (类与接口)

## Item 57: Inherit from `collections.abc` Classes for Custom Container Types (为自定义容器类型继承 `collections.abc` 类)

Much of programming in Python involves defining classes that contain data and describing how such objects relate to each other. Every Python class is a container of some kind, encapsulating attributes and functionality together. Python also provides built-in container types for managing data: lists, tuples, sets, and dictionaries.

Python 中的许多编程工作都涉及定义包含数据的类，并描述此类对象如何相互关联。每个 Python 类都是某种类型的容器，将属性和功能封装在一起。Python 还提供了内置的容器类型来管理数据：列表（lists）、元组（tuples）、集合（sets）和字典（dictionaries）。

When you’re designing classes for simple use cases like sequences, it’s natural to want to subclass Python’s built-in `list` type directly. For example, say I want to create my own custom `list` type that has additional methods for counting the frequency of its members:

当您设计用于简单用例的类时，比如序列，自然会希望直接从 Python 的内置 `list` 类型派生。例如，假设我想创建一个自己的自定义 `list` 类型，具有额外的方法来计算其成员的频率：

```
class FrequencyList(list):
    def __init__(self, members):
        super().__init__(members)
    def frequency(self):
        counts = {}
        for item in self:
            counts[item] = counts.get(item, 0) + 1
        return counts
```

By subclassing `list` , I get all of `list` ’s standard functionality and preserve the semantics familiar to all Python programmers. I can define additional methods to provide any custom behaviors that I need:

通过继承 `list`，我获得了 `list` 的所有标准功能，并保留了所有 Python 程序员熟悉的语义。我可以定义额外的方法来提供任何需要的自定义行为：

```
foo = FrequencyList(["a", "b", "a", "c", "b", "a", "d"])
print("Length is", len(foo))
foo.pop()  # Removes "d"
print("After pop:", repr(foo))
print("Frequency:", foo.frequency())
>>>
Length is 7
After pop: ['a', 'b', 'a', 'c', 'b', 'a']
Frequency: {'a': 3, 'b': 2, 'c': 1}
```

Now, imagine that I need to define an object that feels like a `list` and allows indexing but isn’t a `list` subclass. For example, say that I want to provide sequence semantics (like `list` or `tuple` ; see Item 14: “Know How to Slice Sequences” for background) for a binary tree class:

现在，假设我需要定义一个感觉像 `list` 并允许索引但不是 `list` 子类的对象。例如，假设我希望为二叉树类提供序列语义（如 `list` 或 `tuple`；参见条目14：“了解如何切片序列”以获取背景信息）：

```
class BinaryNode:
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right
```

How do you make this class act like a sequence type? Python implements its container behaviors with instance methods that have special names. When you access a sequence item by index:

如何让这个类表现得像一个序列类型？Python 使用具有一些特殊名称的实例方法来实现其容器行为。当你通过索引访问一个序列项时：

```
bar = [1, 2, 3]
bar[0]
```

it will be interpreted as:

```
bar.__getitem__(0)
```

To make the `BinaryNode` class act like a sequence, you can provide a custom implementation of `__getitem__` (often pronounced “dunder getitem” as an abbreviation for “double underscore getitem”) that traverses the object tree depth-first:

为了使 `BinaryNode` 类表现得像一个序列，您可以提供一个自定义的 `__getitem__` 实现（通常简称为“dunder getitem”，即“双下划线 getitem”），该实现按深度优先遍历对象树：

```
class IndexableNode(BinaryNode):
    def _traverse(self):
        if self.left is not None:
            yield from self.left._traverse()
        yield self
        if self.right is not None:
            yield from self.right._traverse()
    def __getitem__(self, index):
        for i, item in enumerate(self._traverse()):
            if i == index:
                return item.value
        raise IndexError(f"Index {index} is out of range")
```

Here, I construct a binary tree with normal object initialization:

在这里，我使用正常的对象初始化构建了一个二叉树：

```
tree = IndexableNode(
    10,
    left=IndexableNode(
        5,
        left=IndexableNode(2),
        right=IndexableNode(6, right=IndexableNode(7)),
    ),
    right=IndexableNode(15, left=IndexableNode(11)),
)
```

But I can also access it like a `list` in addition to being able to traverse the tree with the `left` and `right` attributes:

但我也可以像访问 `list` 一样访问它，除了能够使用 `left` 和 `right` 属性遍历树之外：

```
print("LRR is", tree.left.right.right.value)
print("Index 0 is", tree[0])
print("Index 1 is", tree[1])
print("11 in the tree?", 11 in tree)
print("17 in the tree?", 17 in tree)
print("Tree is", list(tree))
>>>
LRR is 7
Index 0 is 2
Index 1 is 5
11 in the tree? True
17 in the tree? False
Tree is [2, 5, 6, 7, 10, 11, 15]
```

The problem is that implementing `__getitem__` isn’t enough to provide all of the sequence semantics Python expects from a `list` instance:

问题是，仅实现 `__getitem__` 不足以提供 Python 对 `list` 实例所期望的所有序列语义：

```
len(tree)
>>>
Traceback ...
TypeError: object of type 'IndexableNode' has no len() 
```

The `len` built-in function requires another special method, named `__len__` , that must have an implementation for a custom sequence type:

`len` 内置函数需要另一个名为 `__len__` 的特殊方法，这是自定义序列类型必须实现的：

```
class SequenceNode(IndexableNode):
    def __len__(self):
        count = 0
        for _ in self._traverse():
            count += 1
        return count

tree = SequenceNode(
    10,
    left=SequenceNode(
        5,
        left=SequenceNode(2),
        right=SequenceNode(6, right=SequenceNode(7)),
    ),
    right=SequenceNode(15, left=SequenceNode(11)),
)

print("Tree length is", len(tree))
>>>
Tree length is 7
```

Unfortunately, this still isn’t enough for the class to fully act as a valid sequence. Also missing are the `count` and `index` methods that a Python programmer would expect to see on a sequence like `list` or `tuple` . It turns out that defining your own container types is much harder than it seems.

不幸的是，这仍然不足以让类完全充当有效的序列。还缺少 Python 程序员在序列如 `list` 或 `tuple` 上期望看到的 `count` 和 `index` 方法。事实证明，定义你自己的容器类型比看起来要难得多。

To avoid this difficulty throughout the Python universe, the `collections.abc` built-in module defines a set of abstract base classes that provide all of the typical methods for each container type. When you subclass from these abstract base classes and forget to implement required methods, the module tells you something is wrong:

为了避免整个 Python 世界中的这种困难，`collections.abc` 内置模块定义了一组抽象基类，它们为每种容器类型提供了所有典型的方法。当你从这些抽象基类中继承并忘记实现必需的方法时，模块会告诉你哪里出了问题：

```
from collections.abc import Sequence
    
class BadType(Sequence):
    pass

foo = BadType()
>>>
Traceback ...
TypeError: Can't instantiate abstract class BadType without an implementation for abstract methods '__getitem__', '__len__'
```

When you do implement all of the methods required by an abstract base class from `collections.abc` , as I did above with `SequenceNode` , it provides all of the additional methods, like `index` and `count` , for free:

当你确实实现了来自 `collections.abc` 的抽象基类所需的所有方法时，如上面的 `SequenceNode` 所做的那样，它会免费提供所有附加方法，如 `index` 和 `count`：

```
class BetterNode(SequenceNode, Sequence):
    pass

tree = BetterNode(
    10,
    left=BetterNode(
        5,
        left=BetterNode(2),
        right=BetterNode(6, right=BetterNode(7)),
    ),
    right=BetterNode(15, left=BetterNode(11)),
)

print("Index of 7 is", tree.index(7))
print("Count of 10 is", tree.count(10))
>>>
Index of 7 is 3
Count of 10 is 1
```

The benefit of using these abstract base classes is even greater for more complex container types such as `Set` and `MutableMapping` , which have a large number of special methods that need to be implemented to match Python conventions. Beyond the `collections.abc` module, Python also uses a variety of special methods for object comparisons and sorting, which may be provided by container classes and non-container classes alike (see Item 103: “Know How to Use heapq for Priority Queues” and Item 51: “Prefer dataclasses For Defining Light-Weight Classes” for examples).

使用这些抽象基类的好处对于更复杂的容器类型来说甚至更大，比如 `Set` 和 `MutableMapping`，它们需要实现大量的特殊方法才能符合 Python 的约定。除了 `collections.abc` 模块之外，Python 还使用各种特殊方法来进行对象比较和排序，而这些方法可以由容器类和非容器类 alike 提供（请参阅条目103：“了解如何使用 heapq 实现优先队列”和条目51：“为定义轻量级类优先使用 dataclasses”以获得示例）。

**Things to Remember**

- For simple use-cases, it’s fine to inherit directly from Python’s container types (like `list` or `dict` ) to utilize their fundamental behavior.
- Beware of the large number of methods required to implement custom container types correctly when not inheriting from a built-in type.
- To ensure that your custom container classes match the required behaviors, have them inherit from the interfaces defined in `collections.abc` .

**注意事项**

- 对于简单的用例，直接从 Python 的容器类型（如 `list` 或 `dict`）继承是可以的，以利用它们的基本行为。
- 警惕在不继承内置类型的情况下正确实现自定义容器类型所需的大量方法。
- 为确保您的自定义容器类符合所需的行为，请使其继承自 `collections.abc` 中定义的接口。