# Chapter 8: Metaclasses and Attributes (元类和属性)

## Item 64: Annotate Class Attributes with `__set_name__` (使用 `__set_name__` 注解类属性)

One more useful feature enabled by metaclasses (see Item 62: “Validate Subclasses with `__init_subclass__` ” for background) is the ability to modify or annotate properties after a class is defined but before the class is actually used. This approach is commonly used with descriptors (see Item 60: “Use Descriptors for Reusable `@property` Methods” for details) to give these attributes more introspection into how they’re being used within their containing class.

元类提供的另一个有用的特性（背景请参见条目62：“使用`__init_subclass__` 验证子类”）是在类定义之后但在类实际使用之前，修改或注解属性的能力。这种方法通常与描述符一起使用（详情请参见条目60：“使用描述符实现可复用的 `@property` 方法”），以让这些属性能够更好地了解它们在其包含类中的使用方式。

For example, say that I want to define a new class that represents a row in a customer database. I’d like to have a corresponding property on the class for each column in the database table. Here, I define a descriptor class to connect attributes to column names:

例如，假设我想要定义一个新类来表示客户数据库中的一行。我希望在类上为数据库表中的每个列都有一个对应的属性。在这里，我定义了一个描述符类将属性连接到列名：

```
class Field:
    def __init__(self, column_name):
        self.column_name = column_name
        self.internal_name = "_" + self.column_name
```

I can use the column name to save all of the per-instance state directly in the instance dictionary as protected fields by using the `setattr` built-in function, and later I can load state with `getattr` (see Item 61: “Use `__getattr__` , `__getattribute__` , and `__setattr__` for Lazy Attributes” for background):

我可以使用列名通过内置函数 `setattr` 将每个实例的状态直接保存在实例字典中作为受保护字段，并且稍后可以使用 `getattr` 加载状态（背景知识请参见条目61：“使用 `__getattr__`、`__getattribute__` 和 `__setattr__` 实现延迟属性”）：

```
    def __get__(self, instance, instance_type):
        if instance is None:
            return self
        return getattr(instance, self.internal_name, "")

    def __set__(self, instance, value):
        setattr(instance, self.internal_name, value)
```

Defining the class representing a row requires supplying the database table’s column name for each descriptor attribute:

定义表示一行的类需要为每个描述符属性提供数据库表的列名：

```
class Customer:
    # Class attributes
    first_name = Field("first_name")
    last_name = Field("last_name")
    prefix = Field("prefix")
    suffix = Field("suffix")
```

Using the row class is simple. Here, the `Field` descriptors modify the instance dictionary `__dict__` as expected:

使用该行类很简单。这里的 `Field` 描述符按预期修改了实例字典 `__dict__`：

```
cust = Customer()
print(f"Before: {cust.first_name!r} {cust.__dict__}")
cust.first_name = "Euclid"
print(f"After:  {cust.first_name!r} {cust.__dict__}")
>>>
Before: '' {}
After: 'Euclid' {'_first_name': 'Euclid'}
```

But the code for this class definition seems redundant. I already declared the name of the field for the class on the left ( `field_name =` ). Why do I also have to pass a string containing the same information to the `Field` constructor ( `Field("first_name")` ) on the right?

但是此类定义中的代码似乎有些冗余。我已经在左边声明了类的字段名称（`field_name =`）。为什么还要在右边传递相同的字符串信息给 `Field` 构造函数（`Field("first_name")`）？

```
class Customer:
    # Left side is redundant with right side
    first_name = Field("first_name")
    ...
```


The problem is that the order of evaluation for the `Customer` class definition is the opposite of how it reads from left to right. First, the `Field` constructor is called as `Field("first_name")` . Then, the return value of that is assigned to the `Customer.first_name` class attribute. There’s no way for a `Field` instance to know upfront which class attribute it will be assigned to.

问题是 `Customer` 类定义的求值顺序与其从左到右的阅读顺序相反。首先调用 `Field` 构造函数如 `Field("first_name")`，然后将其返回值分配给 `Customer.first_name` 类属性。因此，`Field` 实例无法预先知道它将被分配到哪个类属性。

To eliminate this redundancy, I can use a metaclass. Metaclasses let you hook the `class` statement directly and take action as soon as a `class` body is finished. In this case, I can use the metaclass to assign `Field.column_name` and `Field.internal_name` on the descriptor automatically instead of manually specifying the field name multiple times:

为了消除这种冗余，我可以使用元类。元类允许你直接挂钩 `class` 语句，并在类体完成后立即采取行动。在这种情况下，我可以使用元类自动分配 `Field.column_name` 和 `Field.internal_name` 而不是手动多次指定字段名：

```
class Meta(type):
    def __new__(meta, name, bases, class_dict):
        for key, value in class_dict.items():
            if isinstance(value, Field):
                value.column_name = key
                value.internal_name = "_" + key
        cls = type.__new__(meta, name, bases, class_dict)
        return cls
```

Here, I define a base class that uses the metaclass. All classes representing database rows should inherit from this class to ensure that they use the metaclass:

在这里，我定义了一个使用该元类的基础类。所有代表数据库行的类都应从此基础类继承，以确保使用该元类：

```
class DatabaseRow(metaclass=Meta):
    pass
```

To work with the metaclass, the field descriptor is largely unchanged. The only difference is that it no longer requires any arguments to be passed to its constructor. Instead, its attributes are set by the `Meta.__new__` method above:

为了与元类协同工作，字段描述符基本不变。唯一不同的是其构造函数不再要求传递任何参数。相反，其属性由上面的 `Meta.__new__` 方法设置：

```
class Field:
    def __init__(self):
        # These will be assigned by the metaclass.
        self.column_name = None
        self.internal_name = None

    def __get__(self, instance, instance_type):
        if instance is None:
            return self
        return getattr(instance, self.internal_name, "")

    def __set__(self, instance, value):
        setattr(instance, self.internal_name, value)
```

By using the metaclass, the new `DatabaseRow` base class, and the new `Field` descriptor, the class definition for a database row no longer has the redundancy from before:

通过使用元类、新的 `DatabaseRow` 基础类和新的 `Field` 描述符，数据库行的新类定义不再存在之前的冗余：

```
class BetterCustomer(DatabaseRow):
    first_name = Field()
    last_name = Field()
    prefix = Field()
    suffix = Field()
```

The behavior of the new class is identical to the behavior of the old one:

新类的行为与旧类完全相同：

```
cust = BetterCustomer()
print(f"Before: {cust.first_name!r} {cust.__dict__}")
cust.first_name = "Euler"
print(f"After:  {cust.first_name!r} {cust.__dict__}")

>>>
Before: '' {}
After: 'Euler' {'_first_name': 'Euler'}
```

The trouble with this approach is that you can’t use the `Field` class for properties unless you also inherit from `DatabaseRow` . If you somehow forget to subclass `DatabaseRow` , or if you don’t want to due to other structural requirements of the class hierarchy, the code will break:

这种方法的问题在于，除非还继承自 `DatabaseRow`，否则不能使用 `Field` 类的属性。如果由于忘记继承 `DatabaseRow` 或者因为类层次结构的其他结构性要求而不愿这么做，代码将会出错：

```
class BrokenCustomer:  # Missing inheritance
    first_name = Field()
    last_name = Field()
    prefix = Field()
    suffix = Field()

cust = BrokenCustomer()
cust.first_name = "Mersenne"

>>>
Traceback ...
TypeError: attribute name must be string, not 'NoneType'
```

The solution to this problem is to use the `__set_name__` special method for descriptors. This method, introduced in Python 3.6, is called on every descriptor instance when its containing class is defined. It receives as parameters the owning class that contains the descriptor instance and the attribute name to which the descriptor instance was assigned. Here, I avoid defining a metaclass entirely and move what the `Meta.__new__` method from above was doing into the `__set_name__` method:

解决此问题的方法是使用描述符的 `__set_name__` 特殊方法。这个方法在 Python 3.6 中引入，在其包含类定义完成时会被调用。它接收包含描述符实例的所有者类以及描述符实例被分配到的属性名作为参数。在这里，我完全避免定义元类，并将 `Meta.__new__` 方法中的功能移到 `__set_name__` 方法中：

```
class Field:
    def __init__(self):
        self.column_name = None
        self.internal_name = None

    def __set_name__(self, owner, column_name):
        # Called on class creation for each descriptor
        self.column_name = column_name
        self.internal_name = "_" + column_name

    def __get__(self, instance, instance_type):
        if instance is None:
            return self
        return getattr(instance, self.internal_name, "")

    def __set__(self, instance, value):
        setattr(instance, self.internal_name, value)
```

Now, I can get the benefits of the `Field` descriptor without having to inherit from a specific parent class or having to use a metaclass:

现在，我可以不继承特定父类也不使用元类的情况下获得 `Field` 描述符的好处：

```
class FixedCustomer:  # No parent class
    first_name = Field()
    last_name = Field()
    prefix = Field()
    suffix = Field()

cust = FixedCustomer()
print(f"Before: {cust.first_name!r} {cust.__dict__}")
cust.first_name = "Mersenne"
print(f"After:  {cust.first_name!r} {cust.__dict__}")

>>>
Before: '' {}
After: 'Mersenne' {'_first_name': 'Mersenne'}
```


**Things to Remember**
- Metaclasses enable you to modify a class’s attributes before the class is fully defined.
- Descriptors and metaclasses make a powerful combination for declarative behavior and runtime introspection.
- Define `__set_name__` on your descriptor classes to allow them to take into account their surrounding class and its property names.

**注意事项**
- 元类使您能够在类完全定义之前修改类的属性。
- 描述符和元类结合起来，对于声明性行为和运行时内省具有强大的能力。
- 在描述符类上定义 `__set_name__` 以使其能够考虑其周围类及其属性名的影响。