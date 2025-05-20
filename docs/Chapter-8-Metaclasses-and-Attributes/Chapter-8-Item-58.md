# Chapter 8: Metaclasses and Attributes (元类和属性)

## Item 58: Use Plain Attributes Instead of Setter and Getter Methods (使用普通属性而不是Setter和Getter方法)

Programmers coming to Python from other languages might naturally try to implement explicit getter and setter methods in their classes to access protected attributes (see Item 55: “Prefer Public Attributes Over Private Ones” for background):

从其他语言转向Python的程序员可能会自然地在他们的类中实现显式的getter和setter方法来访问受保护的属性（参见条目55：“优先选择公共属性而不是私有属性”以获取背景信息）：

```
class OldResistor:
    def __init__(self, ohms):
        self._ohms = ohms
    def get_ohms(self):
        return self._ohms
    def set_ohms(self, ohms):
        self._ohms = ohms
```

Using these setters and getters is simple, but it’s not Pythonic:

使用这些setter和getter很简单，但这不是Pythonic的方式：

```
r0 = OldResistor(50e3)
print("Before:", r0.get_ohms())
r0.set_ohms(10e3)
print("After: ", r0.get_ohms())
>>>
Before: 50000.0
After: 10000.0
```

Such methods are especially clumsy for operations like incrementing in place:

对于像就地递增这样的操作，这些方法尤其笨拙：

```
r0.set_ohms(r0.get_ohms() - 4e3)
assert r0.get_ohms() == 6e3
```

These utility methods do, however, help define the interface for a class, making it easier to encapsulate functionality, validate usage, and define boundaries. Those are important goals when designing a class to ensure that you don’t break callers as the class evolves over time.

然而，这些实用方法确实有助于定义类的接口，使其更容易封装功能、验证使用情况并定义边界。这些都是设计类时的重要目标，以确保随着类的发展不会破坏调用者。

In Python, however, you never need to implement explicit setter or getter methods like this. Instead, you should always start your implementations with simple public attributes, as I do here:

然而，在Python中，你永远不需要像这样实现显式的setter或getter方法。相反，你应该始终以简单的公共属性开始你的实现，如下所示：

```
class Resistor:
    def __init__(self, ohms):
        self.ohms = ohms
        self.voltage = 0
        self.current = 0

r1 = Resistor(50e3)
r1.ohms = 10e3
```

These attributes make operations like incrementing in place natural and clear:

这些属性使得像就地递增这样的操作变得自然且清晰：

```
r1.ohms += 5e3
```

Later, if I decide I need special behavior when an attribute is set, I can migrate to the `@property` decorator (see Item 38: “Define Function Decorators with `functools.wraps` ” for background) and its corresponding `setter` attribute. Here, I define a new subclass of `Resistor` that lets me vary the `current` by assigning the `voltage` property. Note that in order for this code to work properly, the names of both the setter and the getter methods must match the intended property name ( `voltage` ):

之后，如果我决定需要在设置属性时有特殊行为，我可以迁移到`@property`装饰器（参见条目38：“使用`functools.wraps`定义函数装饰器”以获取背景信息）及其对应的`setter`属性。在这里，我定义了一个新的`Resistor`子类，它允许我在分配`voltage`属性时改变`current`。请注意，为了使此代码正常工作，setter和getter方法的名称必须与预期的属性名（`voltage`）匹配：

```
class VoltageResistance(Resistor):
    def __init__(self, ohms):
        super().__init__(ohms)
        self._voltage = 0
    @property
    def voltage(self):
        return self._voltage
    @voltage.setter
    def voltage(self, voltage):
        self._voltage = voltage
        self.current = self._voltage / self.ohms
```

Now, assigning the `voltage` property will run the `voltage` setter method, which in turn will update the `current` attribute of the object to match:

现在，分配`voltage`属性将运行`voltage` setter方法，该方法反过来会更新对象的`current`属性：

```
r2 = VoltageResistance(1e2)
print(f"Before: {r2.current:.2f} amps")
r2.voltage = 10
print(f"After: {r2.current:.2f} amps")
>>>
Before: 0.00 amps
After: 0.10 amps
```

Specifying a `setter` on a property also enables me to perform type checking and validation on values passed to the class. Here, I define a class that ensures all resistance values are above zero ohms:

在属性上指定一个`setter`还可以让我对传递给类的值执行类型检查和验证。在这里，我定义了一个类，确保所有电阻值都大于零欧姆：

```
class BoundedResistance(Resistor):
    def __init__(self, ohms):
        super().__init__(ohms)
    @property
    def ohms(self):
        return self._ohms
    @ohms.setter
    def ohms(self, ohms):
        if ohms <= 0:
            raise ValueError(f"ohms must be > 0; got {ohms}")
        self._ohms = ohms
```

Assigning an invalid resistance to the attribute now raises an exception:

现在为属性分配无效的电阻值会引发异常：

```
r3 = BoundedResistance(1e3)
r3.ohms = 0
>>>
Traceback ...
ValueError: ohms must be > 0; got 0
```

An exception is also raised if I pass an invalid value to the constructor:

如果我传递一个无效值给构造函数，也会引发异常：

```
BoundedResistance(-5)
>>>
Traceback ...
ValueError: ohms must be > 0; got -5
```

This happens because `BoundedResistance.__init__` calls `Resistor.__init__` , which assigns `self.ohms = -5` . That assignment causes the `@ohms.setter` method from `BoundedResistance` to be called, and it immediately runs the validation code before object construction has completed.

这是因为`BoundedResistance.__init__`调用了`Resistor.__init__`，后者分配了`self.ohms = -5`。该分配导致从`BoundedResistance`调用`@ohms.setter`方法，并立即运行验证代码，而在此之前对象构造尚未完成。

I can even use `@property` to make attributes from parent classes immutable (see Item 56: “Prefer `dataclasses` for Creating Immutable Objects” for another approach):

我甚至可以使用`@property`使来自父类的属性不可变（参见条目56：“优先使用dataclasses创建不可变对象”以获取另一种方法）：

```
class FixedResistance(Resistor):
    def __init__(self, ohms):
        super().__init__(ohms)
    @property
    def ohms(self):
        return self._ohms
    @ohms.setter
    def ohms(self, ohms):
        if hasattr(self, "_ohms"):
            raise AttributeError("Ohms is immutable")
        self._ohms = ohms
```

Trying to assign to the property after construction raises an exception:

尝试在构建后分配给属性会引发异常：

```
r4 = FixedResistance(1e3)
r4.ohms = 2e3
>>>
Traceback ...
AttributeError: Ohms is immutable
```

When you use `@property` methods to implement setters and getters, be sure that the behavior you implement is not surprising. For example, don’t set other attributes in getter property methods:

当你使用`@property`方法实现setter和getter时，请确保你实现的行为不令人惊讶。例如，不要在getter属性方法中设置其他属性：

```
class MysteriousResistor(Resistor):
    @property
    def ohms(self):
        self.voltage = self._ohms * self.current
        return self._ohms

    @ohms.setter
    def ohms(self, ohms):
        self._ohms = ohms
```

Setting other attributes in getter property methods leads to extremely bizarre behavior:

在getter属性方法中设置其他属性会导致极其奇怪的行为：

```
r7 = MysteriousResistor(10)
r7.current = 0.1
print(f"Before: {r7.voltage:.2f}")
r7.ohms
print(f"After: {r7.voltage:.2f}")
>>>
Before: 0.00
After: 1.00
```

The best policy is to modify only related object state in `@property.setter` methods. Be sure to also avoid any other side effects that the caller may not expect beyond the object, such as importing modules dynamically, running slow helper functions, doing I/O, or making expensive database queries. Users of a class will expect its attributes to be like any other Python object: quick and easy. Use normal methods to do anything more complex or slow.

最佳策略是在`@property.setter`方法中仅修改相关的对象状态。请务必避免任何调用者可能未预料到的其他副作用，比如动态导入模块、运行慢速辅助函数、进行I/O或执行昂贵的数据库查询。类的使用者会期望其属性像任何其他Python对象一样：快速且易于使用。对于更复杂或缓慢的操作，请使用普通方法。

The biggest shortcoming of `@property` is that the methods for an attribute can only be shared by subclasses. Unrelated classes can’t share the same implementation. However, Python also supports descriptors (see Item 60: “Use Descriptors for Reusable `@property` Methods”) that enable reusable property logic and many other use cases.

`@property`最大的缺点是属性的方法只能由子类共享。不相关的类不能共享相同的实现。然而，Python也支持描述符（参见条目60：“使用描述符实现可重用的@property方法”），这启用了可重用的属性逻辑及许多其他用例。

**Things to Remember**
- Define new class interfaces using simple public attributes, and avoid defining setter and getter methods.
- Use `@property` to define special behavior when attributes are accessed on your objects.
- Follow the rule of least surprise and avoid odd side effects in your `@property` methods.
- Ensure that `@property` methods are fast; for slow or complex work—especially involving I/O or causing side effects—use normal methods instead.

**注意事项**
- 使用简单的公共属性定义新的类接口，避免定义setter和getter方法。
- 使用`@property`在访问对象上的属性时定义特殊行为。
- 遵循最小惊喜原则，在`@property`方法中避免奇怪的副作用。
- 确保`@property`方法快速；对于缓慢或复杂的任务——特别是涉及I/O或引起副作用的任务——使用普通方法。