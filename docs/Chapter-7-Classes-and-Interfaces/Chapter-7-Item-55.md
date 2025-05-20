# Chapter 7: Classes and Interfaces (类与接口)

## Item 55: Prefer Public Attributes over Private Ones (优先使用公共属性而非私有属性)

In Python, there are only two types of visibility for a class’s attributes: public and private:

在 Python 中，类的属性可见性只有两种类型：公共和私有：

```
class MyObject:
    def __init__(self):
        self.public_field = 5
        self.__private_field = 10
    def get_private_field(self):
        return self.__private_field
```

Public attributes can be accessed by anyone using the dot operator on an object:

公共属性可以通过对象上的点操作符被任何人访问：

```
foo = MyObject()
assert foo.public_field == 5
```

Private fields are specified by prefixing an attribute’s name with a double underscore. They can be accessed directly by methods of the containing class:

私有字段通过在属性名前加上双下划线来指定。它们可以直接由包含类的方法访问：

```
assert foo.get_private_field() == 10
```

However, directly accessing private fields from outside the class raises an exception:

但是，从类的外部直接访问私有字段会引发异常：

```
foo.__private_field
>>>
Traceback ...
AttributeError: 'MyObject' object has no attribute '__private_field'. Did you mean: 'get_private_field'?
```

Class methods also have access to private attributes because they are declared within the surrounding `class` block:

类方法也可以访问私有属性，因为它们是在包围的 `class` 块中声明的：

```
class MyOtherObject:
    def __init__(self):
        self.__private_field = 71

    @classmethod
    def get_private_field_of_instance(cls, instance):
        return instance.__private_field

bar = MyOtherObject()
assert MyOtherObject.get_private_field_of_instance(bar) == 71
```

As you’d expect with private fields, a subclass can’t access its parent class’s private fields:

正如你对私有字段所期望的那样，子类无法访问其父类的私有字段：

```
class MyParentObject:
    def __init__(self):
        self.__private_field = 71

class MyChildObject(MyParentObject):
    def get_private_field(self):
        return self.__private_field

baz = MyChildObject()
baz.get_private_field()

>>>
Traceback ...
AttributeError: 'MyChildObject' object has no attribute '_MyChildObject__private_field'. Did you mean: '_MyParentObject__private_field'?
```

The private attribute behavior is implemented with a simple transformation of the attribute name. When the Python compiler sees private attribute access in methods like `MyChildObject.get_private_field` , it translates the `__private_field` attribute access to use the name `_MyChildObject__private_field` instead. In the example above, `__private_field` is only defined in `MyParentObject.__init__` , which means the private attribute’s real name is `_MyParentObject__private_field` . Accessing the parent’s private attribute from the child class fails simply because the transformed attribute name doesn’t exist ( `_MyChildObject__private_field` instead of `_MyParentObject__private_field` ).

私有属性行为是通过对属性名称的简单转换实现的。当 Python 编译器在像 `MyChildObject.get_private_field` 这样的方法中看到私有属性访问时，它会将 `__private_field` 属性访问转换为使用 `_MyChildObject__private_field` 名称。在上面的例子中，`__private_field` 只在 `MyParentObject.__init__` 中定义，这意味着私有属性的实际名称是 `_MyParentObject__private_field` 。从子类访问父类的私有属性失败仅仅是因为转换后的属性名称不存在（`_MyChildObject__private_field` 而不是 `_MyParentObject__private_field`）。

Knowing this scheme, you can easily access the private attributes of any class—from a subclass or externally—without asking for permission:

了解了这个方案后，你可以轻松地从子类或外部访问任何类的私有属性，而无需请求许可：

```
assert baz._MyParentObject__private_field == 71
```

If you look in the object’s attribute dictionary, you can see that private attributes are actually stored with the names as they appear after the transformation:

如果你查看对象的属性字典，你会发现私有属性实际上是以转换后的名称存储的：

```
print(baz.__dict__)
>>>
{'_MyParentObject__private_field': 71}
```

Why doesn’t the syntax for private attributes actually enforce strict visibility? The simplest answer is one often-quoted motto of Python: “We are all consenting adults here.” What this means is that we don’t need the language to prevent us from doing what we want to do. It’s our individual choice to extend functionality as we wish and to take responsibility for the consequences of such a risk. Python programmers believe that the benefits of being open—permitting unplanned extension of classes by default—outweigh the downsides.

为什么私有属性的语法实际上不执行严格的可见性？最简单的答案是经常引用的一句 Python 格言：“我们都是成年人。” 这意味着我们不需要语言阻止我们做我们想做的事情。这是我们个人选择扩展功能，并承担这种风险的后果。Python 程序员相信开放的好处——默认允许未计划的类扩展胜过缺点。

Beyond that, having the ability to hook language features like attribute access (see Item 61: “Use `__getattr__` , `__getattribute__` , and `__setattr__` for Lazy Attributes”) enables you to mess around with the internals of objects whenever you wish. If you can do that, what is the value of Python trying to prevent private attribute access otherwise?

除此之外，能够钩住诸如属性访问之类的语言特性（请参见条目61：“使用 `__getattr__`、`__getattribute__` 和 `__setattr__` 实现延迟属性”）使你随时都可以处理对象的内部结构。如果你能做到这一点，那么Python试图以其他方式阻止私有属性访问的价值何在？

To minimize damage from accessing internals unknowingly, Python programmers follow a naming convention defined in the style guide (see Item 2: “Follow the PEP 8 Style Guide”). Fields prefixed by a single underscore (like `_protected_field` ) are protected by convention, meaning external users of the class should proceed with caution.

为了尽量减少无意访问内部结构造成的损害，Python程序员遵循风格指南中定义的命名约定（参见条目2：“遵循PEP 8风格指南”）。以前缀单个下划线的字段（如`_protected_field`）按惯例受到保护，这意味着类的外部用户应谨慎行事。

However, programmers who are new to Python might consider using private fields to indicate an internal API that shouldn’t be accessed by subclasses or externally:

然而，刚接触Python的程序员可能会考虑使用私有字段来表示不应被子类或外部访问的内部API：

```
class MyStringClass:
    def __init__(self, value):
        self.__value = value

    def get_value(self):
        return str(self.__value)

foo = MyStringClass(5)
assert foo.get_value() == "5"
```

This is the wrong approach. Inevitably someone—maybe even you—will want to subclass your class to add new behavior or to work around deficiencies in existing methods (e.g., the way that `MyStringClass.get_value` always returns a string). By choosing private attributes, you’re only making subclass overrides and extensions cumbersome and brittle. Your potential subclassers will still access the private fields when they absolutely need to do so:

这是错误的做法。不可避免地有人——甚至可能是你自己——会想要子类化你的类以添加新行为或解决现有方法中的缺陷（例如，`MyStringClass.get_value` 总是返回字符串的方式）。通过选择私有属性，你只是让子类的覆盖和扩展变得麻烦且脆弱。当你绝对需要这样做时，你的潜在子类仍然可以访问私有字段：

```
class MyIntegerSubclass(MyStringClass):
    def get_value(self):
        return int(self._MyStringClass__value)

foo = MyIntegerSubclass("5")
assert foo.get_value() == 5
```

But if the class hierarchy changes above you, these classes will break because the private attribute references are no longer valid. Here, the `MyIntegerSubclass` class’s immediate parent, `MyStringClass` , has had another parent class added, called `MyBaseClass` :

但如果在你的上方更改了类层次结构，这些类将会中断，因为私有属性的引用不再有效。在这里，`MyIntegerSubclass` 类的直接父类 `MyStringClass` 添加了一个名为 `MyBaseClass` 的父类：

```
class MyBaseClass:
    def __init__(self, value):
        self.__value = value
    def get_value(self):
        return self.__value

class MyStringClass(MyBaseClass):
    def get_value(self):
        return str(super().get_value())         # Updated

class MyIntegerSubclass(MyStringClass):
    def get_value(self):
        return int(self._MyStringClass__value)  # Not updated
```

The `__value` attribute is now assigned in the `MyBaseClass` parent class, not the `MyStringClass` parent. This causes the private variable reference `self._MyStringClass__value` to break in `MyIntegerSubclass` :

`__value` 属性现在是在父类 `MyBaseClass` 中分配的，而不是在 `MyStringClass` 中。这导致 `MyIntegerSubclass` 中的私有变量引用 `self._MyStringClass__value` 失败：

```
foo = MyIntegerSubclass(5)
foo.get_value()
>>>
Traceback ...
AttributeError: 'MyIntegerSubclass' object has no attribute '_MyStringClass__value'. Did you mean: '_MyBaseClass__value'?
```

In general, it’s better to err on the side of allowing subclasses to do more by using protected attributes. Document each protected field and explain which fields are internal APIs available to subclasses and which should be left alone entirely. This is as much advice to other programmers as it is guidance for your future self on how to extend your own code safely:

一般来说，最好倾向于允许子类进行更多操作，使用受保护的属性。记录每个受保护的字段，并解释哪些字段是提供给子类的内部API，哪些应该完全不受影响。这不仅是对其他程序员的建议，也是对你未来自己的指导，以便安全地扩展你自己的代码：

```
class MyStringClass:
    def __init__(self, value):
        # This stores the user-supplied value for the object.
        # It should be coercible to a string. Once assigned in
        # the object it should be treated as immutable.
        self._value = value


    def get_value(self):
        return str(self._value)

class MyIntegerSubclass(MyStringClass):
    def get_value(self):
        return self._value

foo = MyIntegerSubclass(5)
assert foo.get_value() == 5
```

The only time to seriously consider using private attributes is when you’re worried about naming conflicts between subclasses. This problem occurs when a child class unwittingly defines an attribute that was already defined by its parent class:

唯一需要认真考虑使用私有属性的情况是，当你担心子类之间的命名冲突时。这个问题发生在子类无意中定义了一个父类已经定义过的属性时：

```
class ApiClass:
    def __init__(self):
        self._value = 5

    def get(self):
        return self._value

class Child(ApiClass):
    def __init__(self):
        super().__init__()
        self._value = "hello"  # Conflicts

a = Child()
print(f"{a.get()} and {a._value} should be different")
>>>
hello and hello should be different
```

This is primarily a concern with classes that are part of a public API; the subclasses are out of your control, so you can’t refactor to fix the problem. Such a conflict is especially possible with attribute names that are very common (like `value` ). To reduce the risk of this issue occurring, you can use a private attribute in the parent class to ensure that there are no attribute names that overlap with child classes:

这对于作为公共API一部分的类来说尤其重要；子类超出了你的控制范围，因此你无法重构来修复问题。这种冲突特别可能发生在非常常见的属性名称上（比如 `value` ）。为了降低发生此类问题的风险，你可以在父类中使用私有属性，以确保没有与子类重叠的属性名称：

```
class ApiClass:
    def __init__(self):
        self.__value = 5     # Double underscore

    def get(self):
        return self.__value  # Double underscore

class Child(ApiClass):
    def __init__(self):
        super().__init__()
        self._value = "hello"  # OK!

a = Child()
print(f"{a.get()} and {a._value} are different")

>>>
5 and hello are different
```

**Things to Remember**
- Private attributes aren’t rigorously enforced by the Python compiler.
- Plan from the beginning to allow subclasses to do more with your internal APIs and attributes instead of choosing to lock them out.
- Use documentation of protected fields to guide subclasses instead of trying to force access control with private attributes.
- Only consider using private attributes to avoid naming conflicts with subclasses that are out of your control.

**注意事项**
- 私有属性并不由Python编译器严格强制执行。
- 从一开始就计划好让你的内部API和属性允许子类做更多的事情，而不是选择将它们排除在外。
- 使用受保护字段的文档来指导子类，而不是试图用私有属性强制访问控制。
- 仅考虑使用私有属性来避免与你无法控制的子类的命名冲突。