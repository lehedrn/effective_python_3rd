# Chapter 7: Classes and Interfaces (类与接口)

## Item 51: Prefer `dataclasses` for Defining Lightweight Classes (优先使用 `dataclasses` 定义轻量级类)

It’s easy to start writing Python programs by using built-in data types (such as strings and dictionaries) and defining functions that interact with them. At some point, your code will get complex enough that creating your own types of objects to contain data and encapsulate behavior is warranted (see Item 29: “Compose Classes Instead of Deeply Nesting Dictionaries, Lists, and Tuples” for an example).

在编写 Python 程序时，很容易从使用内置数据类型（如字符串和字典）以及定义与其交互的函数开始。在某些时候，你的代码会变得足够复杂，以至于创建自己的对象类型来包含数据并封装行为是必要的（参见条目29：“通过组合类而不是深层嵌套字典、列表和元组来简化设计”中的示例）。

However, Python’s vast set of object-oriented capabilities can be overwhelming, especially for beginners. To help make these features more approachable, Python provides a variety of built-in modules (see Item 57: “Inherit from `collections.abc` Classes for Custom Container Types”), and there are many community-built packages as well (such as `attrs` and `pydantic` —see Item 116: “Know Where to Find Community-Built Modules”).

然而，Python 的面向对象功能集非常广泛，尤其是对于初学者来说可能会感到不知所措。为了帮助这些功能更容易上手，Python 提供了多种内置模块（参见条目57：“继承 `collections.abc` 类以创建自定义容器类型”），同时也有许多社区构建的包（例如 `attrs` 和 `pydantic` — 参见条目116：“了解在哪里可以找到社区构建的模块”）。

One especially valuable built-in module is `dataclasses` , which you can use to greatly reduce the amount of repetitive code in class definitions. The cost of using the module is a small performance overhead at import time due to how its implementation uses `exec` (see Item 91: “Avoid `exec` and `eval` Unless You’re Building a Developer Tool”). But it’s well worth it, especially for classes with few or no methods that exist primarily to store data in attributes.

一个特别有价值的内置模块是 `dataclasses`，它可以极大地减少类定义中重复代码的数量。使用该模块的成本是在导入时由于其实现使用了 `exec` 而带来的一点性能开销（参见条目91：“除非您正在构建开发人员工具，否则避免使用 `exec` 和 `eval`”）。但对于那些主要用来存储属性数据且方法很少或没有方法的类来说，这是非常值得的。

The potential benefits of `dataclasses` become most clear when you consider how much effort it takes to build each of its features yourself (see Item 56: “Prefer `dataclasses` for Creating Immutable Objects” for more examples). Understanding how these common object-oriented idioms work under the hood is also important so you can migrate your code away from `dataclasses` when you inevitably need more flexibility or customization.

`dataclasses` 的潜在优势在其替代常见面向对象惯用法所需的大量手动编码工作下尤为明显（参见条目56：“优先使用 `dataclasses` 创建不可变对象”获取更多示例）。理解这些常见面向对象惯用法的工作原理也很重要，这样当不可避免地需要更多的灵活性或定制性时，您可以迁离 `dataclasses`。

**Avoiding `__init__` Boilerplate (避免`__init__`模板代码)**

The first thing to do with objects is to create them. The `__init__` special method is called to construct an object when a class name is invoked like a function call. For example, here I define a simple class to store an RGB (red, green blue) color value:

为对象做的第一件事就是创建它们。`__init__` 特殊方法在调用类名像函数一样时被调用以构造对象。例如，这里我定义了一个简单的类来存储RGB（红、绿、蓝）颜色值：

```
class RGB:
    def __init__(self, red, green, blue):
        self.red = red
        self.green = green
        self.blue = blue
```

This code is verbose because it repeats the name of each attribute three times. It’s also error-prone because there are many opportunities to insert typos or accidentally assign an attribute to the wrong argument of `__init__` :

这段代码很冗长，因为它重复了每个属性名称三次。它也容易出错，因为有很多机会插入拼写错误或将属性错误地分配给 `__init__` 的参数：

```
class BadRGB:
    def __init__(self, green, red, blue):  # Bad: Order swapped
        self.red = red
        self.green = green
        self.bloe = blue                   # Bad: Typo
```

The `dataclasses` module includes a class decorator (see Item 66: “Prefer Class Decorators Over Metaclasses for Composable Class Extensions”) that provides better default behaviors for simple classes like this. Here, I define a new class similar to the one above, but I wrap it in the `@dataclass` decorator:

`dataclasses` 模块包括一个类装饰器（参见条目66：“优先使用类装饰器而非元类进行可组合的类扩展”），它为这种简单类提供了更好的默认行为。在这里，我定义了一个类似的新类，但将其包裹在 `@dataclass` 装饰器中：

```
from dataclasses import dataclass

@dataclass
class DataclassRGB:
    red: int
    green: int
    blue: int
```

To use the `dataclass` decorator, I list each attribute of the object in the class body with its corresponding type hint (see Item 124: “Consider Static Analysis via `typing` to Obviate Bugs”). I only have to identify each attribute a single time, avoiding the risk of typos. If I reorder the attributes, I only need to update the callers instead of making sure the class is consistent within itself.

要使用 `dataclass` 装饰器，我只需在类体中列出每个对象属性及其相应的类型提示（参见条目124：“考虑通过 `typing` 进行静态分析以避免错误”）。我只需要识别每个属性一次，从而避免了拼写错误的风险。如果重新排序属性，我只需更新调用者，而不必确保类本身内的一致性。

With these type annotations present, I can also use a static type checking tool to detect errors before the program is executed. For example, here I provide the wrong types when constructing an object and modifying it:

有了这些类型注解，我还可以使用静态类型检查工具在程序执行前检测错误。例如，这里我在构造对象和修改对象时提供了错误的类型：

```
from dataclasses import dataclass

@dataclass
class DataclassRGB:
    red: int
    green: int
    blue: int

obj = DataclassRGB(1, "bad", 3)
obj.red = "also bad"
```

The type checker is able to report these problems without needing more code in the class definition:

类型检查器能够在不需要类定义中添加更多代码的情况下报告这些问题：

```
>>>
$ python3 -m mypy --strict example.py
.../example.py:9: error: Argument 2 to "DataclassRGB" has incompatible type "str"; expected "int"  [arg-type]
.../example.py:10:  error: Incompatible types in assignment (expression has type "str", variable has type "int")  [assignment]
Found 2 errors in 1 file (checked 1 source file)
```

Enabling the same type checking is possible with a standard class by putting type information to the `__init__` method, but this location is cramped and visually noisy in comparison to the class body:

启用相同类型检查也是可能的，只要将类型信息放在标准类的 `__init__` 方法中，但与此相比，在类体中放置这些信息更加紧凑且视觉混乱：

```
class RGB:
    def __init__(self, *, red, green, blue):  # Changed
        self.red = red
        self.green = green
        self.blue = blue
```

If you don’t want type annotations in your project (see Item 3: “Never Expect Python to Detect Errors at Compile Time”), or you need your class' attributes to be totally flexible, you can still use the `dataclass` decorator. Simply provide the `Any` type from the built-in `typing` module for the fields:

如果您不想在项目中使用类型注解（参见条目3：“不要期望 Python 在编译时检测错误”），或者需要类的属性完全灵活，仍然可以使用 `dataclass` 装饰器。只需为字段提供来自内置 `typing` 模块的 `Any` 类型：

```
from typing import Any

@dataclass
class DataclassRGB:
    red: Any
    green: Any
    blue: Any
```

**Requiring Initialization Arguments to be Passed by Keyword (要求初始化参数必须通过关键字传递)**

Arguments are supplied to `__init__` just as they would be for any other function call, meaning both positional arguments and keyword arguments are allowed (see Item 35: “Provide Optional Behavior with Keyword Arguments” for background). For example, here I initialize the `RGB` class three different ways:

参数以与任何其他函数调用相同的方式提供给 `__init__`，这意味着允许位置参数和关键字参数（参见条目35：“通过关键字参数提供可选行为”获取背景信息）。例如，这里我以三种不同的方式初始化了 `RGB` 类：

```
color1 = RGB(red=1, green=2, blue=3)
color2 = RGB(1, 2, 3)
color3 = RGB(1, 2, blue=3)
```

However, this flexibility is error-prone because I can too easily mix up the different color component values. To address this, I can use the `*` symbol in the argument list to require that arguments to `__init__` are always supplied by keyword (see Item 37: “Enforce Clarity with Keyword-Only and Positional-Only Arguments” for details):

然而，这种灵活性容易出错，因为我可能太容易混淆不同颜色组件的值。为解决这个问题，我可以使用 `*` 符号在参数列表中要求 `__init__` 的参数总是通过关键字提供（参见条目37：“通过仅限关键字和仅限位置的参数强制清晰性”获取详细信息）：

```
class RGB:
    def __init__(self, *, red, green, blue):  # Changed
        self.red = red
        self.green = green
        self.blue = blue
```

Now, using keyword arguments is the only way to create these objects:

现在，使用关键字参数是创建这些对象的唯一方式：

```
color4 = RGB(red=1, green=2, blue=3)
```

Initializing the class with positional arguments will fail:

使用位置参数初始化类将会失败：

```
RGB(1, 2, 3)
>>>
Traceback ...
TypeError:  RGB.__init__() takes 1 positional argument but 4 were given
```

By default, classes wrapped by the `dataclass` decorator will also accept a mix of positional and keyword arguments. I can achieve the same keyword-only behavior as above by simply passing the `kw_only` flag to the decorator:

默认情况下，由 `dataclass` 装饰器包装的类也将接受混合的位置和关键字参数。我可以通过简单地将 `kw_only` 标志传递给装饰器来实现与上述相同的仅关键字行为：

```
@dataclass(kw_only=True)
class DataclassRGB:
    red: int
    green: int
    blue: int
```

Now this class must be initialized with keyword arguments:

现在这个类必须使用关键字参数进行初始化：

```
color5 = DataclassRGB(red=1, green=2, blue=3)
```

Passing any positional arguments will fail just like the standard class implementation:

传递任何位置参数将会失败，就像标准类实现一样：

```
DataclassRGB(1, 2, 3)
>>>
Traceback ...
TypeError:  DataclassRGB.__init__() takes 1 positional argument but 4 were given
```

**Providing Default Attribute Values (提供默认属性值)**

For classes that are focused on storing data, it can be useful to have default values for some attributes so they don’t need to be specified every time an object is constructed.

对于专注于存储数据的类来说，为某些属性提供默认值可能是有用的，因此每次构造对象时都不需要指定它们。

For example, say that I want to extend the `RGB` class to allow for an `alpha` field to represent the color’s level of transparency on a scale of 0 to 1. By default, I want the color to be opaque with an `alpha` of 1. Here, I achieve this by providing a default value for the corresponding argument in the `__init__` constructor:

例如，假设我想扩展 `RGB` 类以允许一个 `alpha` 字段来表示颜色在0到1的比例上的透明度。默认情况下，我希望颜色不透明，即 `alpha` 为1。在这里，我通过为 `__init__` 构造函数中的相应参数提供默认值来实现这一点：

```
class RGBA:
    def __init__(self, *, red, green, blue, alpha=1.0):
        self.red = red
        self.green = green
        self.blue = blue
        self.alpha = alpha
```

Now I can omit the alpha argument and the default value will be assigned anyway:

现在我可以省略 alpha 参数，默认值仍将被分配：

```
color1 = RGBA(red=1, green=2, blue=3)
print(
    color1.red,
    color1.green,
    color1.blue,
    color1.alpha,
)
>>>
1 2 3 1.0
```

To enable the same behavior with the `dataclass` decorator, I simply assign a default value to the attribute in the class body:

为了在使用 `dataclass` 装饰器时启用相同的行为，我只需在类体中为属性分配一个默认值：

```
@dataclass(kw_only=True)
class DataclassRGBA:
    red: int
    green: int
    blue: int
    alpha: int = 1.0
```

Creating an object with this new constructor will assign the correct default value for the `alpha` attribute:

使用这个新构造函数创建对象将为 `alpha` 属性分配正确的默认值：

```
color2 = DataclassRGBA(red=1, green=2, blue=3)
print(color2)
>>>
DataclassRGBA(red=1, green=2, blue=3, alpha=1.0)
```

However, neither of these approaches will work correctly when the default value is mutable (see Item 26: “Prefer `get` Over `in` and `KeyError` to Handle Missing Dictionary Keys” for a similar problem and Item 30: “Know That Function Arguments Can Be Mutated” for background). For example, if the default value provided is a list, a single object reference will be shared between all instances of a class, causing weird behaviors like this:

但是，当默认值是可变的时候，这两种方法都不能正常工作（参见条目26：“处理丢失的字典键时优先使用 `get` 而不是 `in` 和 `KeyError`”以获取类似的问题，以及条目30：“知道函数参数可以被修改”作为背景信息）。例如，如果提供的默认值是一个列表，则所有类实例之间将共享单个对象引用，导致如下奇怪的行为：

```
class BadContainer:
    def __init__(self, *, value=[]):
        self.value = value

obj1 = BadContainer()
obj2 = BadContainer()
obj1.value.append(1)
print(obj2.value)  # Should be empty, but isn't

>>>
[1]
```

For standard classes, you can solve this problem by providing a default value of `None` in the `__init__` method, and then dynamically
allocating the real default value (see Item 36: “Use `None` and Docstrings to Specify Dynamic Default Arguments” for background):

对于标准类，您可以通过在 `__init__` 方法中提供 `None` 默认值，并动态分配真实默认值来解决此问题（参见条目36：“使用 `None` 和文档字符串指定动态默认参数”获取背景信息）：

```
class MyContainer:
    def __init__(self, *, value=None):
        if value is None:
            value = []  # Create when not supplied
        self.value = value
```

Now each object will have a different list allocated by default:

现在每个对象都将拥有自己独立的列表：

```
obj1 = MyContainer()
obj2 = MyContainer()
obj1.value.append(1)
assert obj1.value == [1]
assert obj2.value == []
```

To achieve the same behavior with the `dataclass` decorator, I can use the `field` helper function from the `dataclasses` module. It accepts a `default_factory` argument that is the function to call in order to allocate a default value for that attribute:

为了在 `dataclass` 装饰器中实现相同的行为，我可以使用 `dataclasses` 模块中的 `field` 辅助函数。它接受一个 `default_factory` 参数，该参数是用于分配该属性默认值的函数：

```
from dataclasses import field
@dataclass
class DataclassContainer:
    value: list = field(default_factory=list)
```

This similarly fixes the implementation to ensure each new object has its own separate list instance:

这同样解决了实现问题，以确保每个新对象都有其自己的独立列表实例：

```
obj1 = DataclassContainer()
obj2 = DataclassContainer()
obj1.value.append(1)
assert obj1.value == [1]
assert obj2.value == []
```

The `dataclasses` module provides many other helpful features like this, which are covered in detail by the official documentation (https://docs.python.org/3/library/dataclasses.html).

`dataclasses` 模块还提供了许多类似的有用功能，这些都在官方文档中有详细说明（https://docs.python.org/3/library/dataclasses.html）。

**Representing Objects as Strings (将对象表示为字符串)**

When you define a new class in Python using the standard approach, even a basic feature like `print` doesn’t seem to work correctly. Instead of seeing a nice list of attributes and their values, you get the memory address of the object, which is practically useless:

当使用标准方法在 Python 中定义一个新类时，即使是像 `print` 这样基本的功能似乎也无法正常工作。而不是看到属性及其值的漂亮列表，你会得到对象的内存地址，这实际上毫无用处：

```
color1 = RGB(red=1, green=2, blue=3)
print(color1)
>>>
<__main__.RGB object at 0x1029a0b90>
```

To fix this, I can implement the `__repr__` special method (see Item 12: “Understand the Difference Between `repr` and `str` When Printing Objects” for background). Here, I add such a method to a standard Python class using one big format string (see Item 11: “Prefer Interpolated F-Strings Over C-style Format Strings and `str.format` ” for background):

为了解决这个问题，我可以实现 `__repr__` 特殊方法（参见条目12：“打印对象时了解 `repr` 和 `str` 的区别”获取背景信息）。在这里，我向标准 Python 类中添加了这样一个方法，使用一个大的格式化字符串（参见条目11：“相对于 C 风格的格式字符串和 `str.format`，优先使用插值 F-字符串”获取背景信息）：

```
class RGB:
    def __init__(self, *, red, green, blue):
        self.red = red
        self.green = green
        self.blue = blue


    def __repr__(self):
        return (
            f"{type(self).__module__}"
            f".{type(self).__name__}("
            f"red={self.red!r}, "
            f"green={self.green!r}, "
            f"blue={self.blue!r})"
        )
```

Now these objects will look good when they’re printed:

现在这些对象在打印时会看起来很好：

```
color1 = RGB(red=1, green=2, blue=3)
print(color1)
>>>
__main__.RGB(red=1, green=2, blue=3)
```

However, there are two problems with implementing `__repr__` yourself. First, it’s repetitive and verbose boilerplate that needs to be added to every class. Second, it’s error prone because I could easily forget to add new attributes, misspell attribute names, put attribute names in the wrong order for positional construction, or incorrectly insert separating commas and whitespace.

然而，自己实现 `__repr__` 存在两个问题。首先，它是一种需要添加到每个类中的重复而冗长的样板代码。其次，它容易出错，因为我可能会忘记添加新的属性，拼错属性名，把属性名放在错误的顺序里，或者错误地插入分隔符逗号和空格。

The `dataclass` decorator provides an implementation of the `__repr__` special method by default, increasing productivity and avoiding these potential bugs:

`dataclass` 装饰器默认提供了一个 `__repr__` 特殊方法的实现，提高了生产力并避免了这些潜在的错误：

```
color2 = DataclassRGB(red=1, green=2, blue=3)
print(color2)
>>>
DataclassRGB(red=1, green=2, blue=3)
```

**Converting Objects into Tuples (将对象转换为元组)**

To help with equality testing, indexing, and sorting, it can be useful to convert an object into a `tuple` . To do this with a standard Python class, here I define a new method that packs an object’s attributes together:

为了帮助进行相等性测试、索引和排序，将对象转换为 `tuple` 可能是有用的。为了在标准 Python 类中做到这一点，我定义了一个新方法来打包对象的属性：

```
class RGB:
    def __init__(self, red, green, blue):
        self.red = red
        self.green = green
        self.blue = blue


    def _astuple(self):
        return (self.red, self.green, self.blue)
```

Using this method is simple:

使用这种方法很简单：

```
color1 = RGB(1, 2, 3)
print(color1._astuple())
>>>
(1, 2, 3)
```

The `_astuple` method also allows me to copy an object by using the return value as positional arguments for the constructor using the `*` operator (see Item 34: “Reduce Visual Noise with Variable Positional Arguments” and Item 16: “Prefer Catch-All Unpacking Over Slicing” for background):

`_astuple` 方法还允许我使用返回值作为构造函数的位置参数，通过 `*` 运算符（参见条目34：“通过变量位置参数减少视觉噪声”和条目16：“优先使用通配符解包而不是切片”获取背景信息）来复制对象：

```
color2 = RGB(*color1._astuple())
print(color2.red, color2.green, color2.blue)
>>>
1 2 3
```

However, like the `__repr__` implementation for standard Python classes, the `_astuple` method requires error-prone boilerplate with all of the same pitfalls. In contrast, I can use the `astuple` function from the `dataclasses` module to achieve the same behavior for any `dataclass`-decorated class:

然而，像标准 Python 类的 `__repr__` 实现一样，`_astuple` 方法也需要容易出错的样板代码，并且有同样的缺陷。相比之下，我可以使用 `dataclasses` 模块中的 `astuple` 函数来为任何经过 `dataclass` 装饰的类实现相同的行为：

```
from dataclasses import astuple
color3 = DataclassRGB(1, 2, 3)
print(astuple(color3))
>>>
(1, 2, 3)
```

**Converting Objects into Dictionaries (将对象转换为字典)**

To help with data serialization, it can be useful to convert an object into a dictionary containing its attributes. I can achieve this with a standard Python class by defining a new method:

为了帮助数据序列化，将对象转换为包含其属性的字典可能是有用的。我可以通过定义一个新的方法来在标准 Python 类中实现这一点：

```
class RGB:
    def __init__(self, red, green, blue):
        self.red = red
        self.green = green
        self.blue = blue

    def __repr__(self):
        return (
            f"{type(self).__module__}"
            f".{type(self).__name__}("
            f"red={self.red!r}, "
            f"green={self.green!r}, "
            f"blue={self.blue!r})"
        )


    def _asdict(self):
        return dict(
            red=self.red,
            green=self.green,
            blue=self.blue,
        )
```

The return value of this method can be passed to the `dumps` function from the `json` built-in module to produce a serialized representation:

这个方法的返回值可以传递给 `json` 内建模块的 `dumps` 函数，以生成一个序列化的表示：

```
import json
color1 = RGB(red=1, green=2, blue=3)
data = json.dumps(color1._asdict())
print(data)
>>>
{"red": 1, "green": 2, "blue": 3}
```

The `_asdict` method also lets you create a copy of an object using a dictionary of keyword arguments with the `**` operator, similar to how _`astuple` works for positional arguments:

`_asdict` 方法还允许您使用带有关键字参数的字典创建对象的副本，类似于 `_astuple` 对位置参数的工作方式：

```
color2 = RGB(**color1._asdict())
print(color2)
>>>
__main__.RGB(red=1, green=2, blue=3)
```

To get the same behavior using the `dataclasses` module, I can use the `asdict` function, which avoids all of the boilerplate:

要使用 `dataclasses` 模块获得相同的行为，我可以使用 `asdict` 函数，它避免了所有的样板代码：

```
from dataclasses import asdict

color3 = DataclassRGB(red=1, green=2, blue=3)
print(asdict(color3))

>>>
{'red': 1, 'green': 2, 'blue': 3}
```

The `asdict` function from `dataclasses` is also superior to my hand-built `_asdict` method; it will automatically transform data nested in attributes, including basic container types and other `dataclass` objects. To achieve the same effect using a standard class requires much more work (see Item 54: “Consider Composing Functionality with Mix-in Classes” for details).

`dataclasses` 中的 `asdict` 函数优于我的手工构建的 `_asdict` 方法；它将自动转换属性中嵌套的数据，包括基本容器类型和其他 `dataclass` 对象。要在标准类中实现相同的效果需要更多的工作（参见条目54：“考虑使用 Mix-in 类组合功能”获取详细信息）。

**Checking If Objects are Equivalent (检查对象是否相等)**

With a standard Python class, two objects that look like they’re equivalent actually aren’t:

在标准 Python 类中，看起来相等的两个对象实际上并不相等：

```
color1 = RGB(1, 2, 3)
color2 = RGB(1, 2, 3)
print(color1 == color2)
>>>
False
```

The reason for this behavior is that the default implementation of the `__eq__` special method uses the `is` operator that tests whether the two operands have the same identity (i.e., they occupy the same location in memory):

这种行为的原因是 `__eq__` 特殊方法的默认实现使用了 `is` 运算符，该运算符测试两个操作数是否具有相同的标识（即，它们在内存中的位置相同）：

```
assert color1 == color1
assert color1 is color1
assert color1 != color2
assert color1 is not color2
```

For simple classes, it’s a lot more useful when two objects of the same type with the same attribute values are considered equivalent. Here, I implement this behavior for a standard Python class by using the `_astuple` method:

对于简单类来说，当两个具有相同属性值的同类型对象被认为是相等的时，情况会更有用。在这里，我通过使用 `_astuple` 方法为标准 Python 类实现了这种行为：

```
class RGB:
    def __init__(self, red, green, blue):
        self.red = red
        self.green = green
        self.blue = blue

    def __repr__(self):
        return (
            f"{type(self).__module__}"
            f".{type(self).__name__}("
            f"red={self.red!r}, "
            f"green={self.green!r}, "
            f"blue={self.blue!r})"
        )

    def _astuple(self):
        return (self.red, self.green, self.blue)


    def __eq__(self, other):
        return (
            type(self) == type(other)
            and self._astuple() == other._astuple()
        )
```

Now the `==` and `!=` operators work as expected:

现在 `==` 和 `!=` 运算符按预期工作：

```
color1 = RGB(1, 2, 3)
color2 = RGB(1, 2, 3)
color3 = RGB(5, 6, 7)
assert color1 == color1
assert color1 == color2
assert color1 is not color2
assert color1 != color3
```

When a class is created using the `dataclass` decorator, you get this functionality automatically and don’t need to implement `__eq__` yourself:

当使用 `dataclass` 装饰器创建类时，您将自动获得此功能，无需自行实现 `__eq__`：

```
color4 = DataclassRGB(1, 2, 3)
color5 = DataclassRGB(1, 2, 3)
color6 = DataclassRGB(5, 6, 7)
assert color4 == color4
assert color4 == color5
assert color4 is not color5
assert color4 != color6
```

**Enabling Objects to be Compared (启用对象比较)**

Beyond equivalence, it can be useful to compare two objects to see which one is bigger or smaller. For example, here I define a standard class to represent the size of a planet in the universe and its distance from Earth:

除了相等性之外，比较两个对象以查看哪个更大或更小也可能很有用。例如，这里我定义了一个标准类来表示宇宙中行星的大小及其距离地球的距离：

```
class Planet:
    def __init__(self, distance, size):
        self.distance = distance
        self.size = size

    def __repr__(self):
        return (
            f"{type(self).__module__}"
            f"{type(self).__name__}("
            f"distance={self.distance}, "
            f"size={self.size})"
        )
```

If I try to sort these planets, an exception will be raised because Python doesn’t know how to order the objects:

如果我尝试对这些行星进行排序，将引发异常，因为 Python 不知道如何对对象进行排序：

```
far = Planet(10, 5)
near = Planet(1, 2)
data = [far, near]
data.sort()
>>>
Traceback ...
TypeError: TypeError: '<' not supported between instances of 'Planet' and 'Planet'
```

There are work-arounds for this limitation that are sufficient in many cases (see Item 100: “Sort by Complex Criteria Using the `key` Parameter”). However, there are other situations where you need an object to have its own natural ordering (see Item 103: “Know How to Use `heapq` for Priority Queues” for an example).

对此限制有一些变通方案，在许多情况下已经足够（参见条目100：“使用 `key` 参数按复杂条件排序”）。然而，在其他情况下，您可能需要对象具有自己的自然排序（参见条目103：“知道如何使用 `heapq` 进行优先队列”中的示例）。

To support this behavior in a standard class, I use the `_astuple` helper method, as described above, to fill in all of the special methods that Python needs to compare objects:

为了支持标准类中的这种行为，我使用上面描述的 `_astuple` 辅助方法来填充 Python 所需的所有特殊方法来比较对象：

```
class Planet:
    def __init__(self, distance, size):
        self.distance = distance
        self.size = size

    def __repr__(self):
        return (
            f"{type(self).__module__}"
            f"{type(self).__name__}("
            f"distance={self.distance}, "
            f"size={self.size})"
        )


    def _astuple(self):
        return (self.distance, self.size)

    def __eq__(self, other):
        return (
            type(self) == type(other)
            and self._astuple() == other._astuple()
        )

    def __lt__(self, other):
        if type(self) != type(other):
            return NotImplemented
        return self._astuple() < other._astuple()

    def __le__(self, other):
        if type(self) != type(other):
            return NotImplemented
        return self._astuple() <= other._astuple()

    def __gt__(self, other):
        if type(self) != type(other):
            return NotImplemented
        return self._astuple() > other._astuple()

    def __ge__(self, other):
        if type(self) != type(other):
            return NotImplemented
        return self._astuple() >= other._astuple()
```

Python will allow comparisons between different types, so I need to return the `NotImplemented` singleton—not the same as the `NotImplementedError` exception class—to indicate when objects are not comparable.

Python 允许不同类型之间的比较，所以我需要返回 `NotImplemented` 单例（不同于 `NotImplementedError` 异常类）来指示对象何时不可比较。

Now these objects have a natural ordering given by the value returned from `_astuple` , and they can be sorted (first by distance from Earth, then by size) without any additional boilerplate:

现在这些对象有一个由 `_astuple` 返回的值给出的自然顺序，并且它们可以在没有任何额外样板的情况下进行排序（首先按距地球的距离，然后按大小）：

```
far = Planet(10, 2)
near = Planet(1, 5)
data = [far, near]
data.sort()
print(data)
>>>
[__main__Planet(distance=1, size=5), __main__Planet(distance=10, size=2)]
```

One alternative that reduces the number of special method implementations needed is the `total_ordering` class decorator from the `functools` built-in module. But achieving the same behavior with dataclass is even easier: simply pass the `order` flag:

一种可以减少所需特殊方法实现数量的替代方法是使用 `functools` 内建模块中的 `total_ordering` 类装饰器。但是使用 dataclass 实现相同的行为甚至更容易：只需传递 `order` 标志：

```
@dataclass(order=True)
class DataclassPlanet:
    distance: float
    size: float
```

These objects will be comparable using their attributes in the order they’re declared in the class body:

这些对象将按照它们在类体中声明的顺序使用其属性进行比较：

```
far2 = DataclassPlanet(10, 2)
near2 = DataclassPlanet(1, 5)
assert far2 > near2
assert near2 < far2
```

**Things to remember**
- The `dataclass` decorator from the `dataclasses` built-in module can be used to define versatile, light-weight classes without the boilerplate typically required by standard Python syntax.
- Using the `dataclasses` module can help you avoid pitfalls caused by the verbose and error-prone nature of Python’s standard object-oriented features.
- The `dataclasses` module provides additional helper functions for conversions (e.g., `asdict` , `astuple` ) and advanced attribute behavior (e.g., `field` ).
- It’s important to know how to implement object-oriented idioms yourself so you can migrate away from the `dataclasses` module once you need more customization than it allows.

**注意事项**
- `dataclass` 装饰器来自 `dataclasses` 内建模块，可用于定义多功能、轻量级的类，而无需标准 Python 语法通常所需的样板代码。
- 使用 `dataclasses` 模块可以帮助您避免由 Python 标准面向对象特性的冗长性和易错性引起的陷阱。
- `dataclasses` 模块提供了额外的辅助函数，用于转换（例如 `asdict`、`astuple`）和高级属性行为（例如 `field`）。
- 了解如何自己实现面向对象的惯用法很重要，这样一旦您需要比 `dataclasses` 允许的更多定制时，就可以迁移到别处。