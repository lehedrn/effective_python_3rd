# Chapter 7: Classes and Interfaces (类与接口)

## Item 56: Prefer `dataclasses` for Creating Immutable Objects (优先使用 `dataclasses` 创建不可变对象)

Nearly everything in Python can be modified at runtime, which is a fundamental part of the language’s philosophy (see Item 55: “Prefer Public Attributes Over Private Ones” and Item 3: “Never Expect Python to Detect Errors at Compile Time”). However, this flexibility often causes problems that are difficult to debug.

Python 中几乎所有内容都可以在运行时修改，这是该语言哲学的一个基本部分（参见条目55：“优先使用公共属性而非私有属性” 和 条目3：“不要期望 Python 在编译时检测错误”）。然而，这种灵活性常常导致难以调试的问题。

One way to reduce the scope of what can go wrong is to not allow changes to objects after they’re created. This requirement forces code to be written in a functional style, where the primary purpose of functions and methods is to consistently map inputs to outputs, kind of like mathematical equations.

减少可能出错范围的一种方法是在创建对象后不允许对其进行更改。这一要求迫使代码以函数式风格编写，函数和方法的主要目的是像数学方程式一样将输入一致地映射到输出。

A function written in this style is easy to test. You only need to consider the equivalence of arguments and return values instead of worrying about object references and identities. It’s straightforward to reason about and modify a function that doesn’t make mutable state transitions or cause external side effects. And by returning values that can’t be modified later, functions can avoid downstream surprises.

以这种方式编写的函数易于测试。您只需要考虑参数和返回值的等价性，而无需担心对象引用和标识。推理和修改一个不进行可变状态转换或引起外部副作用的函数是直截了当的。通过返回以后无法修改的值，函数可以避免下游的意外情况。

You can benefit from these advantages with your own data types by creating immutable objects. The `dataclasses` built-in module (see Item 51: “Prefer `dataclasses` For Defining Light-Weight Classes” for background) provides a way to define such classes that is far more productive than using Python’s standard object-oriented features. `dataclasses` also enables other functionality out of the box, such as the ability to use value objects as keys in dictionaries and members in sets.

通过创建不可变对象，您可以从这些优势中受益。`dataclasses` 内置模块（参见条目51：“优先使用 `dataclasses` 定义轻量级类”了解背景）提供了一种定义此类类的方式，比使用 Python 的标准面向对象特性更为高效。`dataclasses` 还提供了其他开箱即用的功能，例如能够将值对象用作字典中的键和集合中的成员。

**Preventing Objects from Being Modified (防止对象被修改)**

In Python, all arguments to functions are passed by reference, which, unfortunately, enables a caller’s data to be changed by any callee (see Item 30: “Know That Function Arguments Can Be Mutated” for details). This behavior can cause all kinds of confusing bugs. For example, here I define a standard class that represents the location of a labeled point in two￾dimensional space:

在 Python 中，所有函数参数都是通过引用传递的，这不幸地使得调用者的数据可以被任何被调用者更改（参见条目30：“知道函数参数可能会被修改”了解详情）。这种行为可能导致各种令人困惑的错误。例如，这里我定义了一个标准类，表示二维空间中标记点的位置：

```
class Point:
    def __init__(self, name, x, y):
        self.name = name
        self.x = x
        self.y = y
```

I can define a well-behaved helper function that calculates the distance between two points and doesn’t modify its inputs:

我可以定义一个表现良好的辅助函数，计算两点之间的距离而不修改其输入：

```
def distance(left, right):
    return ((left.x - right.x) ** 2 + (left.y - right.y) ** 2) ** 0.5

origin1 = Point("source", 0, 0)
point1 = Point("destination", 3, 4)
print(distance(origin1, point1))
>>>
5.0
```

I can also define a poorly-behaved function that overwrites the value of the `x` attribute for the first parameter:

我也可以定义一个表现不佳的函数，该函数会覆盖第一个参数的 `x` 属性的值：

```
def bad_distance(left, right):
    left.x = -3
    return distance(left, right)
```

This modification causes the wrong calculation to be made and permanently changes the state of the `origin` object so subsequent calculations will also be incorrect:

此修改会导致错误的计算，并永久更改 `origin` 对象的状态，因此后续计算也将不正确：

```
print(bad_distance(origin1, point1))
print(origin1.x)
>>>
7.211102550927978
-3
```

I can prevent these types of modifications in a standard class by implementing the `__setattr__` and `__delattr__` special methods and having them raise an AttributeError exception (see Item 61: “Use `__getattr__` , `__getattribute__` , and `__setattr__` for Lazy Attributes” for background). To set the initial attribute values, Idirectly assign keys in the `__dict__` instance dictionary:

我可以通过实现 `__setattr__` 和 `__delattr__` 特殊方法并让它们引发 `AttributeError` 异常来防止对标准类的此类修改（参见条目61：“使用 `__getattr__`, `__getattribute__` 和 `__setattr__` 实现延迟属性”了解背景）。为了设置初始属性值，我直接在 `__dict__` 实例字典中分配键：

```
class ImmutablePoint:
    def __init__(self, name, x, y):
        self.__dict__.update(name=name, x=x, y=y)
    def __setattr__(self, key, value):
        raise AttributeError("Immutable object: set not allowed")
    def __delattr__(self, key):
        raise AttributeError("Immutable object: del not allowed")
```

Now, I can do the same distance calculation as before and get the right answer:

现在，我可以进行与之前相同的距离计算并得到正确的答案：

```
origin2 = ImmutablePoint("source", 0, 0)
assert distance(origin2, point1) == 5
```

But using the poorly-behaved function that modifies its inputs will raise an exception:

但使用不良行为的修改输入的函数会引发异常：

```
bad_distance(origin2, point1)
>>>
Traceback ...
AttributeError: Immutable object: set not allowed
```

To achieve the same behavior with the `dataclasses` built-in module, all I have to do is pass the `frozen` flag to the `dataclass` decorator:

要使用 `dataclasses` 内置模块实现相同的行为，我只需将 `frozen` 标志传递给 `dataclass` 装饰器：

```
from dataclasses import dataclass

@dataclass(frozen=True)
class DataclassImmutablePoint:
    name: str
    x: float
    y: float
origin3 = DataclassImmutablePoint("origin", 0, 0)
assert distance(origin3, point1) == 5
```

Trying to modify the attributes of this new `dataclass` will raise a similar `AttributeError` error at runtime:

尝试修改这个新 `dataclass` 的属性会在运行时引发类似的 `AttributeError` 错误：

```
bad_distance(origin3, point1)
>>>
Traceback ...
FrozenInstanceError: cannot assign to field 'x'
```

As an added benefit, the `dataclass` approach also enables static analysis tools to detect this problem before program execution (see Item 124: “Consider Static Analysis via `typing` to Obviate Bugs” for details):

此外，`dataclass` 方法还允许静态分析工具在程序执行前检测此问题（参见条目124：“考虑通过 `typing` 进行静态分析以消除错误”了解详情）：

```
from dataclasses import dataclass

@dataclass(frozen=True)
class DataclassImmutablePoint:
    name: str
    x: float
    y: float

origin = DataclassImmutablePoint("origin", 0, 0)
origin.x = -3
>>>
$ python3 -m mypy --strict example.py
.../example.py:10 error: Property "x" defined in "DataclassImmutablePoint" is read-only  [misc]
Found 1 error in 1 file (checked 1 source file)
```

You can also use the the `Final` and `Never` annotations from the `typing` built-in module to make standard classes similarly fail static analysis, but much more code is required:

您还可以使用 `typing` 内置模块中的 `Final` 和 `Never` 注释使标准类类似地在静态分析中失败，但需要更多的代码：

```
from typing import Any, Final, Never

class ImmutablePoint:
    name: Final[str]
    x: Final[int]
    y: Final[int]

    def __init__(self, name: str, x: int, y: int) -> None:
        self.name = name
        self.x = x
        self.y = y

    def __setattr__(self, key: str, value: Any) -> None:
        if key in self.__annotations__ and key not in dir(self):
            # Allow the very first assignment to happen
            super().__setattr__(key, value)
        else:
            raise AttributeError("Immutable object: set not allowed")

    def __delattr__(self, key: str) -> Never:
        raise AttributeError("Immutable object: del not allowed")
```

**Creating Copies of Objects with Replaced Attributes (创建具有替换属性的对象副本)**

When objects are immutable, a natural questions arises: How are you supposed to write code that accomplishes anything when modifications to data structures aren’t possible? For example, here I have another helper function that moves a `Point` object by a relative amount:

当对象不可变时，自然会出现一个问题：当数据结构无法修改时，如何编写能够完成任务的代码？例如，这里我有另一个辅助函数，它将 `Point` 对象按相对量移动：

```
def translate(point, delta_x, delta_y):
    point.x += delta_x
    point.y += delta_y
```

As expected, it fails when the input object is immutable:

正如预期的那样，当输入对象不可变时它会失败：

```
point1 = ImmutablePoint("destination", 5, 3)
translate(point1, 10, 20)
>>>
Traceback ...
AttributeError: Immutable object: set not allowed
```

One way to work around this limitation is to return a copy of the given argument with updated attribute values:

解决此限制的一种方法是返回具有更新属性值的给定参数的副本：

```
def translate_copy(point, delta_x, delta_y):
    return ImmutablePoint(
        name=point.name,
        x=point.x + delta_x,
        y=point.y + delta_y,
    )
```

However, this is error-prone because you need to copy all of the attributes that you’re not trying to modify, such as `name` in this case. Over time, as the class adds, removes, or changes attributes, this copying code might get out of sync and cause mysterious bugs in your program.

但是，这容易出错，因为您需要复制所有未尝试修改的属性，例如本例中的 `name`。随着时间推移，当类添加、删除或更改属性时，此复制代码可能会不同步，并导致程序中出现神秘的错误。

To reduce the risk of such errors in a standard class, here I add a method that knows how to create copies of an object with a given set of attribute overrides:

为了减少标准类中此类错误的风险，我在其中添加了一个方法，该方法知道如何创建带有给定属性覆盖集的对象副本：

```
class ImmutablePoint:
    def __init__(self, name, x, y):
        self.__dict__.update(name=name, x=x, y=y)

    def __setattr__(self, key, value):
        raise AttributeError("Immutable object: set not allowed")

    def __delattr__(self, key):
        raise AttributeError("Immutable object: del not allowed")


    def _replace(self, **overrides):
        fields = dict(
            name=self.name,
            x=self.x,
            y=self.y,
        )
        fields.update(overrides)
        cls = type(self)
        return cls(**fields)
```

Now code can rely on the `_replace` method to ensure all attributes are properly accounted for. Here, I define another version of the `translate` function that uses this method—note how the name attribute is no longer mentioned:

现在代码可以依赖 `_replace` 方法来确保所有属性都得到了适当的处理。在这里，我定义了 `translate` 函数的另一个版本，该版本使用此方法——注意 `name` 属性不再提及：

```
def translate_replace(point, delta_x, delta_y):
    return point._replace(  # Changed
        x=point.x + delta_x,
        y=point.y + delta_y,
    )
```

But this approach still isn’t ideal. Although I’ve centralized the field copying code to one location inside the class, it’s still possible for the `_replace` method to get out of sync because it needs to be manually maintained. Further, each class that needs this functionality must define its own `_replace` method, which leads to more boilerplate code to manage.

但这仍然不是理想的方法。尽管我已经将字段复制代码集中到了类内部的一个位置，但由于需要手动维护，`_replace` 方法仍有可能不同步。此外，每个需要此功能的类都必须定义自己的 `_replace` 方法，这会导致更多的样板代码需要管理。

To accomplish the same behavior with a `dataclass` I can simply use the `replace` helper function from the `dataclasses` module; no changes to the class definition are required, no custom `_replace` method needs to be defined, and there’s no chance for the method to get out of sync:

要使用 `dataclass` 实现相同的行为，我只需简单地使用 `dataclasses` 模块中的 `replace` 辅助函数；不需要对类定义进行任何更改，也不需要定义自定义的 `_replace` 方法，且没有方法不同步的可能性：

```
import dataclasses

def translate_dataclass(point, delta_x, delta_y):
    return dataclasses.replace(  # Changed
        point,
        x=point.x + delta_x,
        y=point.y + delta_y,
    )
```

**Using Immutable Objects in Dictionaries and Sets (在字典和集合中使用不可变对象)**

When you assign the same key to different values in a `dict` , you expect only the final mapping to be preserved:

当您向字典中分配同一个键的不同值时，您期望只有最后的映射被保留：

```
my_dict = {}
my_dict["a"] = 123
my_dict["a"] = 456
print(my_dict)
>>>
{'a': 456}
```

Similarly, when you add a value to a `set` , you expect that all subsequent additions of the same value will result in no changes to the set because the item is already present:

同样，当您向集合中添加一个值时，您期望之后对该值的所有添加操作都不会导致集合发生变化，因为该项已经存在：

```
my_set = set()
my_set.add("b")
my_set.add("b")
print(my_set)
>>>
{'b'}
```

These stable mapping and deduplication behaviors are critical expectations for how these data structures work. Surprisingly, by default, user-defined objects can’t be used as dictionary keys or set values in the same way the simple values `"a"` and `"b"` were in the code above.

这些稳定的映射和去重行为对于这些数据结构的工作方式至关重要。令人惊讶的是，默认情况下，用户定义的对象不能像上面代码中的简单值 `"a"` 和 `"b"` 那样用作字典的键或集合的值。

For example, say I want to write a program that simulates the physics of electricity. Here, I create a dictionary that maps `Point` objects to the amount of charge at that location (there could be other dictionaries that map the same `Point` objects to other quantities like magnetic flux, etc):

例如，假设我想编写一个模拟电学物理的程序。这里，我创建了一个字典，将 `Point` 对象映射到该位置的电荷量（可能还有其他字典将相同的 `Point` 对象映射到其他量如磁通量等）：

```
point1 = Point("A", 5, 10)
point2 = Point("B", -7, 4)
charges = {
 point1: 1.5,
 point2: 3.5,
}
```

Retrieving the value for a given `Point` in the dictionary seems to work:

检索字典中给定 `Point` 的值似乎有效：

```
print(charges[point1])
>>>
1.5
```

But if I create another `Point` object that appears equivalent to the first one—the same coordinates and name—a `KeyError` exception is raised by dictionary lookup:

但如果我创建另一个看起来等效的第一个 `Point` 对象——具有相同的坐标和名称——字典查找会引发 `KeyError` 异常：

```
point3 = Point("A", 5, 10)
charges[point3]
>>>
Traceback ...
KeyError: <__main__.Point object at 0x100e85eb0>
```

Upon further inspection, the `Point` objects aren’t considered equivalent because I haven’t implemented the `__eq__` special method for the class:

进一步检查发现，`Point` 对象不被认为是相等的，因为我没有为类实现 `__eq__`特殊方法：

```
assert point1 != point3
```

The default implementation of the `==` operator for objects is the same as the `is` operator that only compares their identities. Here, I implement the `__eq__` special method so it compares the values of the objects' attributes instead:

默认情况下，`==` 运算符对对象的实现与 `is` 运算符相同，后者仅比较它们的身份。这里，我实现了 `__eq__`特殊方法，使其比较对象属性的值：

```
class Point:
    def __init__(self, name, x, y):
        self.name = name
        self.x = x
        self.y = y


    def __eq__(self, other):
        return (
            type(self) == type(other)
            and self.name == other.name
            and self.x == other.x
            and self.y == other.y
        )
```

Now, two `Point` objects that appear equivalent will also be treated as such by the `==` operator:

现在，两个看起来等效的 `Point` 对象也会被 `==` 运算符视为相等：

```
point4 = Point("A", 5, 10)
point5 = Point("A", 5, 10)
assert point4 == point5
```

However, even with these new equivalent objects the dictionary lookup from earlier still fails:
然而，即使有了这些新的等效对象，前面的字典查找仍然失败：

```
other_charges = {
 point4: 1.5,
}
other_charges[point5]
>>>
Traceback ...
TypeError: unhashable type: 'Point'
```

The issue is that the `Point` class doesn’t implement the `__hash__` special method. Python’s implementation of the dictionary type relies on the integer value returned by the `__hash__` method to maintain its internal lookup table. In order for dictionaries to work properly, this hash value must be stable and unchanging for individual objects, and the same for equivalent objects. Here, I implement the `__hash__` method by putting the object’s attributes in a `tuple` and passing it to the `hash` built-in function:

问题是 `Point` 类没有实现 `__hash__`特殊方法。Python 的字典类型实现依赖于 `__hash__`方法返回的整数值来维护其内部查找表。为了使字典正常工作，单个对象的哈希值必须稳定且不变，并且等效对象的哈希值必须相同。在这里，我通过将对象的属性放入 `tuple` 并将其传递给 `hash` 内建函数来实现 `__hash__`方法：

```
class Point:
    def __init__(self, name, x, y):
        self.name = name
        self.x = x
        self.y = y

    def __eq__(self, other):
        return (
            type(self) == type(other)
            and self.name == other.name
            and self.x == other.x
            and self.y == other.y
        )


    def __hash__(self):
        return hash((self.name, self.x, self.y))
```

Now the dictionary lookup works as expected:

现在字典查找如预期般工作：

```
point6 = Point("A", 5, 10)
point7 = Point("A", 5, 10)
more_charges = {
 point6: 1.5,
}
value = more_charges[point7]
assert value == 1.5
```

With `dataclasses` , none of this effort is required in order to use an immutable object as a key in a dictionary. When you provide the `frozen` flag to the `dataclass` decorator, you get all of these behaviors (e.g., `__eq__` , `__hash__` ) automatically:

使用 `dataclasses` ，无需进行所有这些努力即可将不可变对象用作字典中的键。当您将 `frozen` 标志提供给 `dataclass` 装饰器时，您会自动获得所有这些行为（例如，`__eq__`, `__hash__`：

```
point8 = DataclassImmutablePoint("A", 5, 10)
point9 = DataclassImmutablePoint("A", 5, 10)
easy_charges = {
 point8: 1.5,
}
assert easy_charges[point9] == 1.5
```

These immutable objects can also be used as values in a `set` and will properly deduplicate:

这些不可变对象还可以用作集合中的值，并能正确去重：

```
my_set = {point8, point9}
assert my_set == {point8}
```

---

What about `namedtuple` ?
关于 `namedtuple`？

Before `dataclasses` was added to the Python standard library (in version 3.7), a good choice for creating immutable objects was the `namedtuple` function from the `collections` built-in module. `namedtuple` provides many of the same benefits as the `dataclass` decorator using the `frozen` flag, including:

在 `dataclasses` 被添加到 Python 标准库（3.7 版本）之前，创建不可变对象的一个好选择是 `collections` 内建模块中的 `namedtuple` 函数。`namedtuple` 提供了许多与使用 `frozen` 标志的 `dataclass` 装饰器相同的优势，包括：

- Construction of objects with positional or keyword arguments, default values provided when attributes are unspecified.
- Automatic definition of object-oriented special methods(e.g., `__init__` , `__repr__` , `__eq__` , `__hash__` , `__lt__` ).
- Built-in helper methods `_replace` and `_dict` , runtime introspection with the `_fields` and `_field_defaults` class attributes.
- Support for static type checking when using the `NamedTuple` class from the `typing` built-in module.
- Low memory usage by avoiding `__dict__` instance dictionaries (i.e., similar to using `dataclasses` with `slots=True` ).

- 使用位置或关键字参数构造对象，默认值在属性未指定时提供。
- 自动定义面向对象的特殊方法（例如，`__init__`,`__repr__`, `__eq__`, `__hash__`, `__lt__`。
- 内建的 `_replace` 和 `_dict` 辅助方法，使用 `_fields` 和 `_field_defaults` 类属性进行运行时内省。
- 支持在使用 `typing` 内建模块中的 `NamedTuple` 类时进行静态类型检查。
- 通过避免 `__dict__` 实例字典来实现低内存使用（即，类似于使用 `dataclasses` 且 `slots=True`）。

Additionally, all fields of a `namedtuple` are accessible by positional index, which can be ideal for wrapping sequential data structures like lines from a CSV (comma-separated values) file or rows from database query results—with a `dataclass` you must call the `_astuple` method.

此外，`namedtuple` 的所有字段都可以通过位置索引访问，这对于包装顺序数据结构（如 CSV（逗号分隔值）文件的行或数据库查询结果的行）非常理想——使用 `dataclass` 必须调用 `_astuple`方法。

However, the sequential nature of a `namedtuple` can lead to unintentional usage (i.e., numerical indexing and iteration) that can cause bugs and make it difficult to migrate to a standard class later, especially for external APIs (see Item 119: “Use Packages to Organize Modules and Provide Stable APIs”). If your data structure is sequential, then `namedtuple` might be a good choice, but otherwise it’s best to go with `dataclasses` or a standard class (see Item 65: “Consider Class Body Definition Order to Establish Sequential Relationships Between Attributes”).

然而，`namedtuple` 的顺序性质可能导致无意的使用（即，数字索引和迭代），从而导致错误并使迁移到标准类变得困难，尤其是对外部 API（参见条目119：“使用包组织模块并提供稳定的 API”）。如果您的数据结构是顺序的，那么 `namedtuple` 可能是一个不错的选择，否则最好选择 `dataclasses` 或标准类（参见条目65：“考虑类体定义顺序以建立属性之间的顺序关系”）。

---

**Things to remember**
- Functional-style code that uses immutable objects is often more robust than imperative style code that modifies state and causes side effects.
- The easiest way to make your own immutable objects is using the `dataclasses` built-in module; simply apply the `dataclass` decorator when defining a class and pass the `frozen=True` argument.
- The `replace` helper function from the `dataclasses` module allows you to create copies of immutable objects with some attributes changed, making it easier to write functional-style code.
- Immutable objects created with `dataclass` are comparable for equivalence by value and have stable hashes, which allows them to be used as keys in dictionaries and values in sets.

**注意事项**
- 使用不可变对象的函数式风格代码通常比修改状态并产生副作用的命令式风格代码更健壮。
- 创建自己的不可变对象的最简单方法是使用 `dataclasses` 内建模块；只需在定义类时应用 `dataclass` 装饰器并传递 `frozen=True` 参数。
- `dataclasses` 模块中的 `replace` 辅助函数允许您创建一些属性更改的不可变对象的副本，从而更容易编写函数式风格的代码。
- 使用 `dataclass` 创建的不可变对象可以通过值进行等效比较，并具有稳定的哈希值，这允许它们用作字典中的键和集合中的值。