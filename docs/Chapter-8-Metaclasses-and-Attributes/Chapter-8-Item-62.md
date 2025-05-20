# Chapter 8: Metaclasses and Attributes (元类和属性)

## Item 62: Validate Subclasses with `__init_subclass__` (使用 `__init_subclass__` 验证子类)

One of the simplest applications of metaclasses is verifying that a class was defined correctly. When you’re building a complex class hierarchy, you may want to enforce style, require overriding methods, or have strict relationships between class attributes. Metaclasses enable these use cases by providing a reliable way to run your validation code each time a new subclass is defined.

元类最简单的应用之一就是验证一个类的定义是否正确。当你构建复杂的类层次结构时，你可能希望强制执行编码风格、要求重写方法，或者在类属性之间建立严格的关系。元类通过提供一种可靠的方式，在每次定义新子类时运行你的验证代码来实现这些用例。

Often a class’s validation code runs in the `__init__` method, when an object of the class’s type is constructed at runtime (see Item 58: “Use Plain Attributes Instead of Setter and Getter Methods” for an example). Using metaclasses for validation can raise errors much earlier, such as when the module containing the class is first imported at program startup.

通常，类的验证代码会在运行时构造该类的对象时在 `__init__` 方法中运行（参见Item 58：“Use Plain Attributes Instead of Setter and Getter Methods”中的示例）。使用元类进行验证可以在更早的时候引发错误，例如在程序启动时首次导入包含该类的模块时。

Before I get into how to define a metaclass for validating subclasses, it’s important to understand what a metaclass does for standard objects. A metaclass is defined by inheriting from `type` . A class indicates its metaclass with the `metaclass` keyword argument in its inheritance argument list. In the typical case, a metaclass has its `__new__` method called with the contents of any associated `class` statements when they occur. Here, I use a basic metaclass to inspect a class' information before the type is actually constructed:

在我深入讲解如何定义用于验证子类的元类之前，理解元类对标准对象做了什么非常重要。元类通过继承 `type` 来定义。一个类通过其继承参数列表中的 `metaclass` 关键字参数指明其元类。在典型情况下，当任何相关的 `class` 语句发生时，元类的 `__new__` 方法会以该类的内容调用。在此处，我使用一个基本的元类在类型实际构建之前检查类的信息：

```
class Meta(type):
    def __new__(meta, name, bases, class_dict):
        global print
        orig_print = print
        print(f"* Running {meta}.__new__ for {name}")
        print("Bases:", bases)
        print = pprint
        print(class_dict)
        print = orig_print
        return type.__new__(meta, name, bases, class_dict)

class MyClass(metaclass=Meta):
    stuff = 123
    def foo(self):
        pass

class MySubclass(MyClass):
    other = 567
    def bar(self):
        pass

>>>
* Running <class '__main__.Meta'>.__new__ for MyClass
Bases: ()
{'__module__': '__main__',
 '__qualname__': 'MyClass',
 'foo': <function MyClass.foo at 0x00000172070E6F20>,
 'stuff': 123}

* Running <class '__main__.Meta'>.__new__ for MySubclass
Bases: (<class '__main__.MyClass'>,)
{'__module__': '__main__',
 '__qualname__': 'MySubclass',
 'bar': <function MySubclass.bar at 0x0000017207479620>,
 'other': 567}
```

The metaclass has access to the name of the class, the parent classes it inherits from ( `bases` ), and all of the class attributes that were defined in the class’s body. All classes inherit from `object` , so it’s not explicitly listed in the `tuple` of base classes.

元类可以访问类的名称、它继承的父类（`bases`）以及在类体中定义的所有类属性。所有类都继承自 `object`，因此它不会显式列在基类的 `tuple` 中。

I can add functionality to the `Meta.__new__` method in order to validate all of the parameters of an associated subclass before it’s defined. For example, say that I want to represent any type of multi-sided polygon. I can do this by defining a special validating metaclass and using it in the base class of my polygon class hierarchy. Note that it’s important not to apply the same validation to the base class:

我可以向 `Meta.__new__` 方法中添加功能，以便在关联的子类定义之前验证其所有参数。例如，假设我想表示任何类型的多边形。我可以通过定义一个特殊的验证元类并在我的多边形类层次结构的基类中使用它来实现。请注意，不需要对基类应用相同的验证：

```
class ValidatePolygon(type):
    def __new__(meta, name, bases, class_dict):
        # Only validate subclasses of the Polygon class
        if bases:
            if class_dict["sides"] < 3:
                raise ValueError("Polygons need 3+ sides")
        return type.__new__(meta, name, bases, class_dict)

class Polygon(metaclass=ValidatePolygon):
    sides = None  # Must be specified by subclasses
    
    @classmethod
    def interior_angles(cls):
        return (cls.sides - 2) * 180

class Triangle(Polygon):
    sides = 3

class Rectangle(Polygon):
    sides = 4

class Nonagon(Polygon):
    sides = 9

assert Triangle.interior_angles() == 180
assert Rectangle.interior_angles() == 360
assert Nonagon.interior_angles() == 1260
```

If I try to define a polygon with fewer than three sides, the validation logic will cause the `class` statement to fail immediately after the `class` statement body. This means the program will not even be able to start running when I define such a class (unless it’s defined in a dynamically imported module; see Item 97: “Lazy-load Modules with Dynamic Imports to Reduce Startup Time” for how this can happen):

如果我尝试定义一个少于三边的多边形，验证逻辑将导致 `class` 语句在其主体之后立即失败。这意味着当我定义此类时，除非在动态导入的模块中定义（参见Item 97：“Lazy-load Modules with Dynamic Imports to Reduce Startup Time”），否则程序甚至无法运行：

```
print("Before class")
    
class Line(Polygon):
    print("Before sides")
    sides = 2
    print("After sides")

print("After class")

>>>
Before class
Before sides
After sides
Traceback ...
ValueError: Polygons need 3+ sides
```

This seems like quite a lot of machinery in order to get Python to accomplish such a basic task. Luckily, Python 3.6 introduced simplified syntax—the `__init_subclass__` special class method—for achieving the same behavior while avoiding metaclasses entirely. Here, I use this mechanism to provide the same level of validation as before:

为了完成如此基本的任务，这似乎需要大量的机制。幸运的是，Python 3.6 引入了简化的语法——`__init_subclass__` 特殊类方法——来实现相同的行为，同时完全避免使用元类。在这里，我使用这种机制来提供与之前相同的验证级别：

```
class BetterPolygon:
    sides = None  # Must be specified by subclasses
    
    def __init_subclass__(cls):
        super().__init_subclass__()
        if cls.sides < 3:
            raise ValueError("Polygons need 3+ sides")
    
    @classmethod
    def interior_angles(cls):
        return (cls.sides - 2) * 180

class Hexagon(BetterPolygon):
    sides = 6

assert Hexagon.interior_angles() == 720
```

The code is much shorter now, and the `ValidatePolygon` metaclass is gone entirely. It’s also easier to follow since I can access the `sides` attribute directly on the `cls` instance in `__init_subclass__` instead of having to go into the class’s dictionary with `class_dict["sides"]` . If I define an invalid subclass of `BetterPolygon` , the same exception is raised as before:

现在的代码要短得多，并且完全去掉了 `ValidatePolygon` 元类。它也更容易跟随，因为可以直接在 `__init_subclass__` 的 `cls` 实例上访问 `sides` 属性，而无需通过 `class_dict["sides"]` 进入类的字典。如果我定义了一个无效的 `BetterPolygon` 子类，同样会抛出异常：

```
print("Before class")
class Point(BetterPolygon):
    sides = 1
print("After class")
>>>
Before class
Traceback ...
ValueError: Polygons need 3+ sides
```

Another problem with the standard Python metaclass machinery is that you can only specify a single metaclass per class definition. Here, I define a second metaclass that I’d like to use for validating the fill color used for a region (not necessarily just polygons):

另一个问题在于标准 Python 元类机制：每个类定义只能指定一个元类。在此处，我定义了第二个我希望用于验证区域填充颜色的元类（不一定只是多边形）：

```
class ValidateFilled(type):
    def __new__(meta, name, bases, class_dict):
        # Only validate subclasses of the Filled class
        if bases:
            if class_dict["color"] not in ("red", "green"):
                raise ValueError("Fill color must be supported")
        return type.__new__(meta, name, bases, class_dict)

class Filled(metaclass=ValidateFilled):
    color = None  # Must be specified by subclasses
```

When I try to use the `Polygon` metaclass and `Filled` metaclass together, I get a cryptic error message:

当我尝试一起使用 `Polygon` 元类和 `Filled` 元类时，会出现一个晦涩的错误消息：

```
class RedPentagon(Filled, Polygon):
    color = "blue"
    sides = 5
>>>
Traceback ...
TypeError: metaclass conflict: the metaclass of a derived class must be a (non-strict) subclass of the metaclasses of all its bases
```

It’s possible to fix this by creating a complex hierarchy of metaclass `type` definitions to layer validation:

可以通过创建复杂的元类 `type` 定义层次结构来修复这个问题，以分层验证：

```
class ValidatePolygon(type):
    def __new__(meta, name, bases, class_dict):
        # Only validate non-root classes
        if not class_dict.get("is_root"):
            if class_dict["sides"] < 3:
                raise ValueError("Polygons need 3+ sides")
        return type.__new__(meta, name, bases, class_dict)

class Polygon(metaclass=ValidatePolygon):
    is_root = True
    sides = None  # Must be specified by subclasses

class ValidateFilledPolygon(ValidatePolygon):
    def __new__(meta, name, bases, class_dict):
        # Only validate non-root classes
        if not class_dict.get("is_root"):
            if class_dict["color"] not in ("red", "green"):
                raise ValueError("Fill color must be supported")
        return super().__new__(meta, name, bases, class_dict)

class FilledPolygon(Polygon, metaclass=ValidateFilledPolygon):
    is_root = True
    color = None  # Must be specified by subclasses
```

This requires every FilledPolygon instance to be a Polygon instance:

这要求每个 `FilledPolygon` 实例必须是一个 `Polygon` 实例：

```
class GreenPentagon(FilledPolygon):
    color = "green"
    sides = 5

greenie = GreenPentagon()
assert isinstance(greenie, Polygon)
```

Validation works for colors:

颜色验证有效：

```
class OrangePentagon(FilledPolygon):
    color = "orange"
    sides = 5
>>>
Traceback ...
ValueError: Fill color must be supported
```

Validation also works for number of sides:

边数验证也有效：

```
class RedLine(FilledPolygon):
    color = "red"
    sides = 2
>>>
Traceback ...
ValueError: Polygons need 3+ sides
```

However, this approach ruins composability, which is often the purpose of class validation like this (similar to mix-ins; see Item 54: “Consider Composing Functionality with Mix-in Classes”). If I want to apply the color validation logic from `ValidateFilledPolygon` to another hierarchy of classes, I’ll have to duplicate all of the logic again, which reduces code reuse and increases boilerplate.

然而，这种方法破坏了可组合性，而这通常是此类类验证的目的（类似于混合类；参见Item 54：“Consider Composing Functionality with Mix-in Classes”）。如果我想要将来自 `ValidateFilledPolygon` 的颜色验证逻辑应用于其他类层次结构，则必须再次复制所有逻辑，这减少了代码复用并增加了样板代码。

The `__init_subclass__` special class method can also be used to solve this problem. It can be defined by multiple levels of a class hierarchy as long as the `super` built-in function is used to call any parent or sibling `__init_subclass__` definitions. Here, I define a class to represent a region’s fill color that can be composed with the `BetterPolygon` class from before:

`__init_subclass__` 特殊类方法也可以用来解决这个问题。只要使用 `super` 内置函数调用任何父类或兄弟类的 `__init_subclass__` 定义，就可以在类层次结构的多个层级中定义它。在此处，我定义了一个表示区域填充颜色的类，它可以与之前的 `BetterPolygon` 类组合使用：

```
class Filled:
    color = None  # Must be specified by subclasses

    def __init_subclass__(cls):
        super().__init_subclass__()
        if cls.color not in ("red", "green", "blue"):
            raise ValueError("Fills need a valid color")
```

I can inherit from both classes to define a new class. Both classes call `super().__init_subclass__()` , causing their corresponding validation logic to run when the subclass is created:

我可以从这两个类继承以定义一个新类。两个类都调用 `super().__init_subclass__()`，从而在创建子类时运行它们的相应验证逻辑：

```
class RedTriangle(Filled, BetterPolygon):
    color = "red"
    sides = 3

ruddy = RedTriangle()
assert isinstance(ruddy, Filled)
assert isinstance(ruddy, BetterPolygon)
```

If I specify the number of sides incorrectly, I get a validation error:

如果我错误地指定了边数，我会得到一个验证错误：

```
print("Before class")
class BlueLine(Filled, BetterPolygon):
    color = "blue"
    sides = 2
print("After class")
>>>
Before class
Traceback ...
ValueError: Polygons need 3+ sides
```

If I specify the color incorrectly, I also get a validation error:

如果我错误地指定了颜色，也会得到一个验证错误：

```
print("Before class")
class BeigeSquare(Filled, BetterPolygon):
    color = "beige"
    sides = 4
print("After class")
>>>
Before class
Traceback ...
ValueError: Fills need a valid color
```

You can even use `__init_subclass__` in complex cases like multiple inheritance and diamond inheritance (see Item 53: “Initialize Parent Classes with `super` ” for background). Here, I define a basic diamond hierarchy to show this in action:

你甚至可以在多重继承和菱形继承等复杂情况下使用 `__init_subclass__`（参见Item 53：“Initialize Parent Classes with `super`”了解背景信息）。在此处，我定义了一个基本的菱形层次结构来展示这一点：

```
class Top:
    def __init_subclass__(cls):
        super().__init_subclass__()
        print(f"Top for {cls}")

class Left(Top):
    def __init_subclass__(cls):
        super().__init_subclass__()
        print(f"Left for {cls}")

class Right(Top):
    def __init_subclass__(cls):
        super().__init_subclass__()
        print(f"Right for {cls}")

class Bottom(Left, Right):
    def __init_subclass__(cls):
        super().__init_subclass__()
        print(f"Bottom for {cls}")

>>>
Top for <class '__main__.Left'>
Top for <class '__main__.Right'>
Top for <class '__main__.Bottom'>
Right for <class '__main__.Bottom'>
Left for <class '__main__.Bottom'>
```


As expected, `Top.__init_subclass__` is called only a single time for each class, even though there are two paths to it for the `Bottom` class through its `Left` and `Right` parent classes.

正如预期的那样，对于每个类，`Top.__init_subclass__` 只被调用一次，即使对于 `Bottom` 类来说，通过其 `Left` 和 `Right` 父类有两条路径到达它也是如此。

**Things to Remember**
- The `__new__` method of metaclasses is run after the `class` statement’s entire body has been processed.
- Metaclasses can be used to inspect or modify a class after it’s defined but before it’s created, but they’re often more heavyweight than what you need.
- Use `__init_subclass__` to ensure that subclasses are well formed at the time they are defined, before objects of their type are constructed.
- Be sure to call `super().__init_subclass__` from within your class’s `__init_subclass__` definition to enable composable validation in multiple layers of classes and multiple inheritance.

**注意事项**
1. 元类的 `__new__` 方法在 `class` 语句的整个主体处理完成后运行。
2. 元类可用于在类定义后但在创建之前对其进行检查或修改，但它们往往比你需要的更重量级。
3. 使用 `__init_subclass__` 来确保子类在定义时就处于良好状态，在构造其类型的对象之前。
4. 在定义类的 `__init_subclass__` 时，请务必调用 `super().__init_subclass__`，以便在多层类和多重继承中启用可组合的验证。