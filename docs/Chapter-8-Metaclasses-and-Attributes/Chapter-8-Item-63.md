# Chapter 8: Metaclasses and Attributes (元类和属性)

## Item 63: Register Class Existence with `__init_subclass__` (利用 `__init_subclass__` 构建类的注册机制)

Another common use of metaclasses (see Item 62: “Validate Subclasses with `__init_subclass__` ” for background) is to automatically register types in a program. Registration is useful for doing reverse lookups, where you need to map an identifier back to a corresponding class.

元类的另一个常见用途（背景见条目62：“使用 `__init_subclass__` 验证子类”）是自动注册程序中的类型。注册对于执行反向查找非常有用，即你需要将标识符映射回相应的类。

For example, say that I want to implement my own serialized representation of a Python object using JSON. I need a way to turn an `object` into a JSON string. Here, I do this generically by defining a base class that records the constructor parameters and turns them into a JSON dictionary (see Item 54: “Consider Composing Functionality with Mix-in Classes” for another approach):

例如，假设我想使用JSON实现自己的Python对象序列化表示形式。我需要一种方法将一个`object`转换为JSON字符串。在这里，我通过定义一个记录构造函数参数并将其转换为JSON字典的基类来通用地实现这一点（另请参见条目54：“考虑使用Mix-in类组合功能”）：

```
import json

class Serializable:
    def __init__(self, *args):
        self.args = args

    def serialize(self):
        return json.dumps({"args": self.args})
```

This class makes it easy to serialize simple data structures to a string, like this one:

此类使得将简单数据结构序列化为字符串变得容易，比如下面这个：

```
class Point2D(Serializable):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Point2D({self.x}, {self.y})"

point = Point2D(5, 3)
print("Object:    ", point)
print("Serialized:", point.serialize())

>>>
Object: Point2D(5, 3)
Serialized: {"args": [5, 3]}
```

Now, I need to deserialize this JSON string and construct the `Point2D` object it represents. Here, I define another class that can deserialize the data from its `Serializable` parent class (see Item 52: “Use `@classmethod` Polymorphism to Construct Objects Generically” for background):

现在，我需要反序列化此JSON字符串并构建其代表的`Point2D`对象。在这里，我定义了另一个类，可以从其父类`Serializable`中反序列化数据（背景信息请参见条目52：“使用`@classmethod`多态性以通用方式构造对象”）：

```
class Deserializable(Serializable):
    @classmethod
    def deserialize(cls, json_data):
        params = json.loads(json_data)
        return cls(*params["args"])
```

Using `Deserializable` as a parent class makes it easy to serialize and deserialize simple objects in a generic way:

使用`Deserializable`作为父类可以方便地以通用方式序列化和反序列化简单对象：

```
class BetterPoint2D(Deserializable):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Point2D({self.x}, {self.y})"

before = BetterPoint2D(5, 3)
print("Before:    ", before)
data = before.serialize()
print("Serialized:", data)
after = BetterPoint2D.deserialize(data)
print("After:     ", after)

>>>
Before: Point2D(5, 3)
Serialized: {"args": [5, 3]}
After: Point2D(5, 3)
```

The problem with this approach is that it works only if you know the intended type of the serialized data ahead of time (e.g., `Point2D` , `BetterPoint2D` ). Ideally, you’d have a large number of classes serializing to JSON and one common function that could deserialize any of them back to a corresponding Python `object` (see Item 50: “Consider `functools.singledispatch` for Functional-Style Programming Instead of Object-Oriented Polymorphism” for a similar example).

这种方法的问题在于它只有在您提前知道序列化数据的预期类型时才有效（例如，`Point2D`, `BetterPoint2D`）。理想情况下，您会有大量类将数据序列化为JSON，并且有一个通用函数能够将它们反序列化回对应的Python `object`（参见条目50：“考虑使用`functools.singledispatch`进行函数式编程而非面向对象的多态性”中的类似示例）。

To do this, I can include the serialized object’s class name in the JSON data:

为此，我可以将序列化对象的类名包含在JSON数据中：

```
class BetterSerializable:
    def __init__(self, *args):
        self.args = args

    def serialize(self):
        return json.dumps(
            {
                "class": self.__class__.__name__,
                "args": self.args,
            }
        )

    def __repr__(self):
        name = self.__class__.__name__
        args_str = ", ".join(str(x) for x in self.args)
        return f"{name}({args_str})"
```

Then, I can maintain a mapping of class names back to constructors for those objects. The general `deserialize` function works for any classes passed to `register_class` :

然后，我可以维护一个从类名到这些对象构造器的映射。通用的 `deserialize` 函数适用于传递给 `register_class` 的任何类：

```
REGISTRY = {}

def register_class(target_class):
    REGISTRY[target_class.__name__] = target_class

def deserialize(data):
    params = json.loads(data)
    name = params["class"]
    target_class = REGISTRY[name]
    return target_class(*params["args"])
```

To ensure that `deserialize` always works properly, I must call `register_class` for every class I might want to deserialize in the future:

为了确保 `deserialize` 始终正常工作，我必须对每个将来可能想要反序列化的类调用 `register_class` ：

```
class EvenBetterPoint2D(BetterSerializable):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.x = x
        self.y = y

register_class(EvenBetterPoint2D)
```

Now, I can deserialize an arbitrary JSON string without having to know which class it contains:

现在，我可以反序列化任意JSON字符串而无需知道它包含哪个类：

```
before = EvenBetterPoint2D(5, 3)
print("Before: ", before)
data = before.serialize()
print("Serialized:", data)
after = deserialize(data)
print("After: ", after)
>>>
Before: EvenBetterPoint2D(5, 3)
Serialized: {"class": "EvenBetterPoint2D", "args": [5, 3]}
After: EvenBetterPoint2D(5, 3)
```

The problem with this approach is that it’s possible to forget to call `register_class` :

这种方法的问题是我可能会忘记调用`register_class`:

```
class Point3D(BetterSerializable):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.x = x
        self.y = y
        self.z = z

# Forgot to call register_class! Whoops!
```

This causes the code to break at runtime when I try to deserialize an object of a class I forgot to register:

这会导致我在尝试反序列化忘记注册的类的对象时代码在运行时崩溃：

```
point = Point3D(5, 9, -4)
data = point.serialize()
deserialize(data)
>>>
Traceback ...
KeyError: 'Point3D'
```

Even though I chose to subclass `BetterSerializable` , I don’t actually get all of its features if I forget to call `register_class` after the `class` statement body. This approach is error prone and especially challenging for beginners to debug. The same omission can happen with class decorators (see Item 66: “Prefer Class Decorators Over Metaclasses for Composable Class Extensions” for when those are appropriate).

即使我选择继承`BetterSerializable`，如果我忘记在`class`语句体后调用`register_class`，我也实际上没有获得它的所有功能。这种方法容易出错，尤其是对初学者来说很难调试。同样的遗漏也可能发生在类装饰器上（何时适用请参见条目66：“对于可组合的类扩展，优先使用类装饰器而不是元类”）。

What if I could somehow act on the programmer’s intent to use `BetterSerializable` and ensure that `register_class` is called in all cases? Metaclasses enable this by intercepting the `class` statement when subclasses are defined. Here, I use a metaclass and corresponding superclass to register any child classes immediately after their class statements end:

如果我能以某种方式拦截程序员使用`BetterSerializable`的意图，并确保在所有情况下都调用`register_class`，那会怎么样呢？元类通过在子类定义时拦截`class`语句使这成为可能。在这里，我使用一个元类及其对应的超类，在子类的类语句结束后立即注册它们：

```
class Meta(type):
    def __new__(meta, name, bases, class_dict):
        cls = type.__new__(meta, name, bases, class_dict)
        register_class(cls)
        return cls

class RegisteredSerializable(BetterSerializable, metaclass=Meta):
    pass
```

When I define a subclass of `RegisteredSerializable` , I can be confident that the call to `register_class` happens and `deserialize` will always work as expected:

当我定义 `RegisteredSerializable` 的子类时，我可以确信调用了`register_class`，并且 `deserialize` 将始终按预期工作：

```
class Vector3D(RegisteredSerializable):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.x, self.y, self.z = x, y, z

before = Vector3D(10, -7, 3)
print("Before:    ", before)
data = before.serialize()
print("Serialized:", data)
print("After:     ", deserialize(data))

>>>
Before: Vector3D(10, -7, 3)
Serialized: {"class": "Vector3D", "args": [10, -7, 3]}
After: Vector3D(10, -7, 3)
```

An even better approach is to use the `__init_subclass__` special class method. This simplified syntax, introduced in Python 3.6, reduces the visual noise of applying custom logic when a class is defined. It also makes it more approachable to beginners who may be confused by the complexity of metaclass syntax. Here, I implement a new superclass to automatically call `register_class` and a subclass that uses it:

更好的方法是使用`__init_subclass__`特殊类方法。这种简化的语法是在Python 3.6中引入的，减少了在定义类时应用自定义逻辑的视觉干扰。对于那些可能被复杂元类语法搞糊涂的初学者来说，这也更容易接近。在这里，我实现了一个新的超类来自动调用`register_class`，以及使用它的子类：

```
class BetterRegisteredSerializable(BetterSerializable):
    def __init_subclass__(cls):
        super().__init_subclass__()
        register_class(cls)

class Vector1D(BetterRegisteredSerializable):
    def __init__(self, magnitude):
        super().__init__(magnitude)
        self.magnitude = magnitude
```

Serialization and deserialization works as expected for this new class:

此类的序列化和反序列化按预期工作：

```
before = Vector1D(6)
print("Before: ", before)
data = before.serialize()
print("Serialized:", data)
print("After: ", deserialize(data))
>>>
Before: Vector1D(6)
Serialized: {"class": "Vector1D", "args": [6]}
After: Vector1D(6)
```

By using `__init_subclass__` (or metaclasses) for class registration, you can ensure that you’ll never miss registering a class as long as the inheritance tree is right. This works well for serialization, as I’ve shown, and also applies to database object-relational mappings (ORMs), extensible plug-in systems, and callback hooks.

通过使用`__init_subclass__`（或元类）进行类注册，只要继承树正确，就可以确保永远不会错过注册调用。这不仅适用于我所展示的序列化，也适用于数据库对象关系映射（ORM）、可扩展的插件系统和回调钩子。

**Things to Remember**
- Class registration is a helpful pattern for building modular Python programs.
- Metaclasses let you run registration code automatically each time your base class is subclassed in a program.
- Using metaclasses for class registration helps you avoid errors by ensuring that you never miss a registration call.
- Prefer `__init_subclass__` over standard metaclass machinery because it’s clearer and easier for beginners to understand.

**注意事项**
- 类注册是一种有助于构建模块化Python程序的有用模式。
- 元类允许你在程序中每次子类化你的基类时自动运行注册代码。
- 使用元类进行类注册可以帮助你避免错误，确保你永远不会错过一次注册调用。
- 倾向于使用`__init_subclass__`而不是标准的元类机制，因为它的清晰度更高，对于初学者来说更易于理解。