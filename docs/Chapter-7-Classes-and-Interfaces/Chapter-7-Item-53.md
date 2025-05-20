# Chapter 7: Classes and Interfaces (类与接口)

## Item 53: Initialize Parent Classes with `super` (使用 `super` 初始化父类)

The old, simple way to initialize a parent class from a child class is to directly call the parent class’s `__init__` method with the child instance:

旧的、简单的方法是从子类中直接调用父类的 `__init__` 方法：

```
class MyBaseClass:
    def __init__(self, value):
        self.value = value

class MyChildClass(MyBaseClass):
    def __init__(self):
        MyBaseClass.__init__(self, 5)
```

This approach works fine for basic class hierarchies but breaks in many cases.

这种方法对于基本的类层次结构来说效果很好，但在许多情况下会失效。

If a class is affected by multiple inheritance (something to avoid in general; see Item 54: “Consider Composing Functionality with Mix-in Classes”), calling the superclasses’ `__init__` methods directly can lead to unpredictable behavior.

如果一个类受到多重继承的影响（通常应避免；参见条目54：“考虑使用 Mix-in 类组合功能”），直接调用超类的 `__init__` 方法可能导致不可预测的行为。

One problem is that the `__init__` call order isn’t specified across all subclasses. For example, here I define two parent classes that operate on the instance’s `value` field:

一个问题是在所有子类之间没有指定 `__init__` 调用顺序。例如，这里定义了两个操作实例 `value` 字段的父类：

```
class TimesTwo:
    def __init__(self):
        self.value *= 2

class PlusFive:
    def __init__(self):
        self.value += 5
```

This class defines its parent classes in one ordering:

此类以一种顺序定义其父类：

```
class OneWay(MyBaseClass, TimesTwo, PlusFive):
    def __init__(self, value):
        MyBaseClass.__init__(self, value)
        TimesTwo.__init__(self)
        PlusFive.__init__(self)
```

And constructing it produces a result that matches the parent class ordering:

构建它会产生符合父类排序的结果：

```
foo = OneWay(5)
print("First ordering value is (5 * 2) + 5 =", foo.value)

>>>
First ordering value is (5 * 2) + 5 = 15
```

Here’s another class that defines the same parent classes but in a different ordering ( `PlusFive` followed by `TimesTwo` instead of the other way around):

这里是另一个类，定义了相同的父类但顺序不同（`PlusFive` 排在 `TimesTwo` 前面而不是相反）：

```
class AnotherWay(MyBaseClass, PlusFive, TimesTwo):
    def __init__(self, value):
        MyBaseClass.__init__(self, value)
        TimesTwo.__init__(self)
        PlusFive.__init__(self)
```

However, I left the calls to the parent class constructors—— `PlusFive.__init__` and `TimesTwo.__init__`——in the same order as before, which means this class’s behavior doesn’t match the order of the parent classes in its definition. The conflict here between the ordering of the inheritance base classes and the `__init__` calls is hard to spot, which makes this especially difficult for new readers of the code to understand:

然而，我保留了对父类构造函数——`PlusFive.__init__` 和 `TimesTwo.__init__` 的调用顺序如前，这意味着此类的行为与其定义中的父类顺序不匹配。此处继承基类的顺序和 `__init__` 调用之间的冲突很难察觉，这使得新读者尤其难以理解代码：

```
bar = AnotherWay(5)
print("Second ordering should be (5 + 5) * 2, but is", bar.value)

>>>
Second ordering should be (5 + 5) * 2, but is 15
```

Another problem occurs with diamond inheritance. Diamond inheritance happens when a subclass inherits from two separate classes that have the same superclass somewhere in the hierarchy. Diamond inheritance causes the common superclass’s `__init__` method to run multiple times, leading to unexpected behavior. For example, here I define two child classes that inherit from `MyBaseClass` :

另一个问题出现在菱形继承中。当一个子类从层次结构中两个不同的类继承而这两个类又具有共同的超类时，就会发生菱形继承。菱形继承会导致公共超类的 `__init__` 方法多次运行，导致意外行为。例如，这里我定义了两个从 `MyBaseClass` 继承的子类：

```
class TimesSeven(MyBaseClass):
    def __init__(self, value):
        MyBaseClass.__init__(self, value)
        self.value *= 7

class PlusNine(MyBaseClass):
    def __init__(self, value):
        MyBaseClass.__init__(self, value)
        self.value += 9
```

Then, I define a child class that inherits from both of these classes, making `MyBaseClass` the top of the diamond:

然后，我定义了一个从这两个类继承的子类，使 `MyBaseClass` 成为菱形的顶部：

```
class ThisWay(TimesSeven, PlusNine):
    def __init__(self, value):
        TimesSeven.__init__(self, value)
        PlusNine.__init__(self, value)

foo = ThisWay(5)
print("Should be (5 * 7) + 9 = 44 but is", foo.value)

>>>
Should be (5 * 7) + 9 = 44 but is 14
```

The call to the second parent class’s constructor, `PlusNine.__init__` , causes `self.value` to be reset back to `5` when `MyBaseClass.__init__` gets called a second time. That results in the calculation of `self.value` to be `5 + 9 = 14` , completely ignoring the effect of the `TimesSeven.__init__` constructor. This behavior is surprising and can be very difficult to debug in more complex cases.

调用第二个父类的构造函数 `PlusNine.__init__` 会导致 `self.value` 在第二次调用 `MyBaseClass.__init__` 时重置回 `5` 。这导致 `self.value` 的计算结果为 `5 + 9 = 14` ，完全忽略了 `TimesSeven.__init__` 构造函数的效果。这种行为令人惊讶，在更复杂的情况下可能非常难以调试。

To solve these problems, Python has the `super` built-in function and standard method resolution order (MRO). `super` ensures that common superclasses in diamond hierarchies are run only once (see Item 62: “Validate Subclasses with `__init_subclass__` ” for another example). The MRO defines the ordering in which superclasses are initialized, following an algorithm called C3 linearization.

为了解决这些问题，Python 提供了内置的 `super` 函数和标准方法解析顺序（MRO）。`super` 确保在钻石继承层次结构中公共的超类只运行一次（另请参见条目62：“使用 `__init_subclass__` 验证子类”）。MRO 定义了超类初始化的顺序，遵循称为 C3 线性化的算法。

Here, I create a diamond-shaped class hierarchy again, but this time I use `super` to initialize the parent class:

这里，我再次创建了一个菱形的类层次结构，但这次使用 `super` 来初始化父类：

```
class MyBaseClass:
    def __init__(self, value):
        self.value = value

class TimesSevenCorrect(MyBaseClass):
    def __init__(self, value):
        super().__init__(value)
        self.value *= 7

class PlusNineCorrect(MyBaseClass):
    def __init__(self, value):
        super().__init__(value)
        self.value += 9
```

Now, the top part of the diamond, `MyBaseClass.__init__` , is run only a single time. The other parent classes are run in the order specified in the `class` statement:

现在，菱形顶部的 `MyBaseClass.__init__` 只运行一次。其他父类按照 `class` 语句中指定的顺序运行：

```
class GoodWay(TimesSevenCorrect, PlusNineCorrect):
    def __init__(self, value):
        super().__init__(value)

foo = GoodWay(5)
print("Should be 7 * (5 + 9) = 98 and is", foo.value)

>>>
Should be 7 * (5 + 9) = 98 and is 98
```

This order might seem backward. Shouldn’t `TimesSevenCorrect.__init__` have run first? Shouldn’t the result be `(5 * 7) + 9 = 44` ? The answer is no. This ordering matches what the MRO defines for this class. The MRO ordering is available via a class method called `mro` or cached in a class attribute called `__mro__` :

这个顺序看起来可能是反直觉的。难道不应该首先运行 `TimesSevenCorrect.__init__` 吗？结果不应该是 `(5 * 7) + 9 = 44` 吗？答案是否定的。这个顺序符合该类的 MRO 定义。MRO 的排序可以通过名为 `mro` 的类方法或缓存在名为 `__mro__` 的类属性中来访问：

```
mro_str = "\n".join(repr(cls) for cls in GoodWay.__mro__)
print(mro_str)

>>>
<class '__main__.GoodWay'>
<class '__main__.TimesSevenCorrect'>
<class '__main__.PlusNineCorrect'>
<class '__main__.MyBaseClass'>
<class 'object'>
```

When I call `GoodWay(5)` , it in turn calls `TimesSevenCorrect.__init__` , which calls `PlusNineCorrect.__init__` , which calls `MyBaseClass.__init__` . Once this reaches the top of the diamond, all of the initialization methods actually do their work in the opposite order from how their `__init__` functions were called. `MyBaseClass.__init__` assigns `value` to `5` . `PlusNineCorrect.__init__` adds `9` to make value equal `14` . `TimesSevenCorrect.__init__` multiplies it by `7` to make `value` equal `98` .

当我调用 `GoodWay(5)` 时，它依次调用 `TimesSevenCorrect.__init__` ，接着调用 `PlusNineCorrect.__init__` ，最后调用 `MyBaseClass.__init__` 。一旦到达菱形的顶部，所有的初始化方法实际上会按照它们的 `__init__` 函数被调用的相反顺序执行工作。`MyBaseClass.__init__` 将 `value` 赋值为 `5` 。`PlusNineCorrect.__init__` 加上 `9` 使得 `value` 等于 `14` 。`TimesSevenCorrect.__init__` 将其乘以 `7` 使得 `value` 等于 `98` 。

Besides making multiple inheritance robust, the call to `super().__init__` is also much more maintainable than calling `MyBaseClass.__init__` directly from within the subclasses. I could later rename `MyBaseClass` to something else or have `TimesSevenCorrect` and `PlusNineCorrect` inherit from another superclass without having to update their `__init__` methods to match.

除了使多重继承更加稳健外，调用 `super().__init__` 相比直接从子类中调用 `MyBaseClass.__init__` 更加可维护。以后我可以将 `MyBaseClass` 重命名为其他名称，或者让 `TimesSevenCorrect` 和 `PlusNineCorrect` 继承自其他超类，而无需更新它们的 `__init__` 方法以使其匹配。

The `super` function can also be called with two parameters: first the type of the class whose MRO parent view you’re trying to access, and then the instance on which to access that view. Using these optional parameters within the constructor looks like this:

`super` 函数也可以用两个参数进行调用：第一个是您试图访问其 MRO 父视图的类类型，第二个是要在其上访问该视图的实例。在构造函数中使用这些可选参数如下所示：

```
class ExplicitTrisect(MyBaseClass):
    def __init__(self, value):
        super(ExplicitTrisect, self).__init__(value)
        self.value /= 3
```

However, these parameters are not required for object instance initialization. Python’s compiler automatically provides the correct parameters ( `__class__` and `self` ) for you when `super` is called with zero arguments within a class definition. This means all three of these usages are equivalent:

但是，这两个参数在对象实例化初始化时不是必需的。Python 编译器会在类定义内部零参数调用 `super` 时自动提供正确的参数（`__class__` 和 `self`）。这意味着以下三种用法是等效的：

```
class AutomaticTrisect(MyBaseClass):
    def __init__(self, value):
        super(__class__, self).__init__(value)
        self.value /= 3

class ImplicitTrisect(MyBaseClass):
    def __init__(self, value):
        super().__init__(value)
        self.value /= 3

assert ExplicitTrisect(9).value == 3
assert AutomaticTrisect(9).value == 3
assert ImplicitTrisect(9).value == 3
```

The only time you should provide parameters to `super` is in situations where you need to access the specific functionality of a superclass’s implementation from a child class (e.g., in order to wrap or reuse functionality).

只有在需要从子类访问特定父类实现的功能时（例如为了包装或重用功能），才应该向 `super` 提供参数。

**Things to Remember**

- Python’s standard method resolution order (MRO) solves the problems of superclass initialization order and diamond inheritance.
- Use the `super` built-in function with zero arguments to initialize parent classes and call parent methods.

**注意事项**

- Python 的标准方法解析顺序（MRO）解决了超类初始化顺序和钻石继承的问题。
- 使用无参数的内置 `super` 函数来初始化父类并调用父类方法。