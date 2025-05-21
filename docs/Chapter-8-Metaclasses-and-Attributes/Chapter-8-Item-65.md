# Chapter 8: Metaclasses and Attributes (元类和属性)

## Item 65: Consider Class Body Definition Order to Establish Relationships Between Attributes (考虑类体定义顺序以建立属性之间的关系)

The purpose of many classes defined in Python programs is to represent external data that is created and maintained elsewhere. For example, say that I have a CSV (comma-separated values) file containing a list of freight deliveries where each row includes the destination city, method of travel, and shipment weight. Here, I read in this data using the `csv` built-in module:

在Python程序中定义的许多类的目的，是表示在外部创建和维护的数据。例如，假设有一个包含货运交付列表的CSV（逗号分隔值）文件，其中每一行包括目的地城市、旅行方式和货物重量。这里我使用`csv`内置模块读取此数据：

```
import csv

with open("packages.csv", "w") as f:
    f.write(
        """\
Sydney,truck,25
Melbourne,boat,6
Brisbane,plane,12
Perth,road train,90
Adelaide,truck,17
"""
    )

with open("packages.csv") as f:
    for row in csv.reader(f):
        print(row)
print("...")

>>>
['Sydney', 'truck', '25']
['Melbourne', 'boat', '6']
['Brisbane', 'plane', '12']
['Perth', 'road train', '90']
['Adelaide', 'truck', '17']
...
```

I can define a new class to store this data and a helper function that creates an object given a CSV row (see Item 52: “Use `@classmethod` Polymorphism to Construct Objects Generically” for background):

我可以定义一个新类来存储这些数据，并提供一个辅助函数，该函数根据CSV行创建对象（有关背景信息，请参见条目52：“使用`@classmethod`多态性通用地构造对象”）：

```
class Delivery:
    def __init__(self, destination, method, weight):
        self.destination = destination
        self.method = method
        self.weight = weight

    @classmethod
    def from_row(cls, row):
        return cls(row[0], row[1], row[2])
```

This works as expected when provided a list of values, one for each column:

当提供一列值列表时，这按预期工作：

```
row1 = ["Sydney", "truck", "25"]
obj1 = Delivery.from_row(row1)
print(obj1.__dict__)
>>>
{'destination': 'Sydney', 'method': 'truck', 'weight': '25'}
```

If more columns are added to the CSV or the columns are reordered, with a small amount of effort I could make corresponding adjustments to the `__init__` and `from_row` methods to maintain compatibility with the file format. Now imagine that there are many kinds of CSV files that I want to process, each with different numbers of columns and types of cell values. It would be better if I could more efficiently define a new class for each CSV file without much boilerplate.

如果向CSV添加更多列或重新排序列，则只需稍作努力即可对`__init`和`from_row`方法进行相应的调整以保持与文件格式的兼容性。现在想象一下，我想处理许多不同种类的CSV文件，每个文件具有不同数量的列和类型的单元格值。最好能够更高效地为每个CSV文件定义一个新类，而不需要太多样板代码。

Here, I try to accomplish this by implementing a base class that uses the `fields` class attribute to map CSV columns (in the order they appear in the file) to object attribute names (see Item 64: “Annotate Class Attributes with `__set_name__` ” for another approach):

在这里，我尝试通过实现一个使用`fields`类属性的基类来完成这一任务，将CSV列（它们在文件中出现的顺序）映射到对象属性名称（有关另一种方法，请参见条目64：“使用`__set_name__`注释类属性”）：

```
class RowMapper:
    fields = ()  # Must be in CSV column order

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if key not in type(self).fields:
                raise TypeError(f"Invalid field: {key}")
            setattr(self, key, value)

    @classmethod
    def from_row(cls, row):
        if len(row) != len(cls.fields):
            raise ValueError("Wrong number of fields")
        kwargs = dict(pair for pair in zip(cls.fields, row))
        return cls(**kwargs)
```

Now, I can create a concrete child class for the freight CSV file format:

现在，我可以为货运CSV文件格式创建一个具体的子类：

```
class DeliveryMapper(RowMapper):
    fields = ("destination", "method", "weight")

obj2 = DeliveryMapper.from_row(row1)
assert obj2.destination == "Sydney"
assert obj2.method == "truck"
assert obj2.weight == "25"
```

If I had another CSV format to support, say, for moving-van logistics, I could quickly create another child by providing the column names:

如果我有另一个CSV格式要支持，比如说搬家车物流，我可以快速创建另一个子类，通过提供列名：

```
class MovingMapper(RowMapper):
    fields = ("source", "destination", "square_feet")
```

Although this works, it’s not Pythonic. The attributes are specified using strings instead of variable names, which makes the code difficult to read and flummoxes tools (see Item 124: “Consider Static Analysis via `typing` to Obviate Bugs” and Item 3: “Never Expect Python to Detect Errors at Compile Time”). More importantly, the `fields` tuple feels redundant with the body of the class: it’s a list of of attributes nested inside a list of attributes.

虽然这有效，但并不符合Python风格。属性是使用字符串而不是变量名指定的，这使得代码难以阅读并且让工具困惑（请参见条目124：“考虑通过`typing`进行静态分析以避免错误”和条目3：“不要期望Python在编译时检测错误”）。更重要的是，`fields`元组感觉冗余于类体内：它是一个嵌套在属性列表中的属性列表。

What would be better is if I could put the names of the CSV columns in the body of the class like this:

更好的做法是，可以将CSV列的名称放在类体中，像这样：

```
class BetterMovingMapper:
    source = ...
    destination = ...
    square_feet = ...
```

It turns out this is possible using three features of Python together (see Item 51: “Prefer `dataclasses` For Defining Light-Weight Classes” for another approach). The first feature is the `__init_subclass__` special class method, which allows you to run code when a subclass is defined (see Item 62: “Validate Subclasses with `__init_subclass__` ”). The second feature is how Python class attributes can be inspected at runtime using the `__dict__` instance dictionary of a class object (see Item 54: “Consider Composing Functionality with Mix-in Classes”). And the third feature is how Python dictionaries preserve the insertion order of key-value pairs (see Item 25: “Be Cautious When Relying on Dictionary Insertion Ordering”).

事实证明，使用Python的三个功能一起可以实现这一点（另请参见条目51：“对于轻量级类，优先考虑`dataclasses`”）。第一个特性是`__init_subclass__`特殊类方法，允许在子类定义时运行代码（请参见条目62：“使用`__init_subclass__`验证子类”）。第二个特性是Python类属性如何在运行时使用类对象的`__dict__`实例字典进行检查（请参见条目54：“考虑使用Mix-in类组合功能”）。第三个特性是Python字典如何保留键值对的插入顺序（请参见条目25：“依赖字典插入排序时要谨慎”）。

Here, I create a class that finds child attributes assigned to `...` and stores their names in the `fields` class attribute for the `RowMapper` parent class to use:

在这里，我创建了一个类，用于查找分配给`...`的子属性，并将其名称存储在`RowMapper`父类使用的`fields`类属性中：

```
class BetterRowMapper(RowMapper):
    def __init_subclass__(cls):
        fields = []
        for key, value in cls.__dict__.items():
            if value is Ellipsis:
                fields.append(key)
        cls.fields = tuple(fields)
```

Now, I can declare a concrete class like before, but using the class body with ellipses to indicate the columns of the CSV file:

现在，我可以像以前一样声明一个具体类，但使用带有省略号的类体来指示CSV文件的列：

```
class BetterDeliveryMapper(BetterRowMapper):
    destination = ...
    method = ...
    weight = ...

obj3 = BetterDeliveryMapper.from_row(row1)
assert obj3.destination == "Sydney"
assert obj3.method == "truck"
assert obj3.weight == "25"
```

If the order of the columns in the CSV file changes, I can just change the attribute definition order to compensate. For example, here I move the `destination` field to the end:

如果CSV文件中的列顺序改变，只需更改属性定义的顺序即可补偿。例如，这里我将`destination`字段移到末尾：

```
class ReorderedDeliveryMapper(BetterRowMapper):
    method = ...
    weight = ...
    destination = ...  # Moved

row4 = ["road train", "90", "Perth"]  # Different order
obj4 = ReorderedDeliveryMapper.from_row(row4)
print(obj4.__dict__)

{'method': 'road train', 'weight': '90', 'destination': 'Perth'}
```

In a real program, I would use a descriptor class instead of ellipses when declaring the fields to enable use-cases like attribute validation and data conversion (see Item 60: “Use Descriptors for Reusable `@property` Methods” for background). For example, say I want the `weight` column to be parsed into a floating point number instead of remaining as a string. Here, I implement a descriptor class that intercepts attribute accesses and converts assigned values as needed:

在一个实际的程序中，我会在声明字段时使用描述符类而不是省略号，以便启用诸如属性验证和数据转换等用例（有关背景知识，请参见条目60：“使用描述符重用@property方法”）。例如，假设我希望将`weight`列解析成浮点数而不是保持字符串。在这里，我实现了一个描述符类，该类拦截属性访问并根据需要转换分配的值：

```
class Field:
    def __init__(self):
        self.internal_name = None

    def __set_name__(self, owner, column_name):
        self.internal_name = "_" + column_name

    def __get__(self, instance, instance_type):
        if instance is None:
            return self
        return getattr(instance, self.internal_name, "")

    def __set__(self, instance, value):
        adjusted_value = self.convert(value)
        setattr(instance, self.internal_name, adjusted_value)

    def convert(self, value):
        raise NotImplementedError
```

I can implement two concrete `Field` subclasses, one for strings and another for floating point numbers:

我可以实现两个具体的`Field`子类，一个用于字符串，另一个用于浮点数：

```
class StringField(Field):
    def convert(self, value):
        if not isinstance(value, str):
            raise ValueError
        return value

class FloatField(Field):
    def convert(self, value):
        return float(value)
```

Another new base class for representing CSV files can look for `Field` instances instead of `Ellipsis` instances to discover the ordered CSV columns and populate the `fields` class attribute accordingly:

另一个新的基类用于表示CSV文件，可以在发现`Field`实例而不是`Ellipsis`实例的情况下，发现有序的CSV列，并相应地填充`fields`类属性：

```
class DescriptorRowMapper(RowMapper):
    def __init_subclass__(cls):
        fields = []
        for key, value in cls.__dict__.items():
            if isinstance(value, Field):  # Changed
                fields.append(key)
        cls.fields = tuple(fields)
```

Now, I can declare a concrete subclass for my specific CSV format, and the `weight` field will be converted to a floating point as expected:

现在，我可以为我的特定CSV格式声明一个具体的子类，`weight`字段将按预期转换为浮点数：

```
class ConvertingDeliveryMapper(DescriptorRowMapper):
    destination = StringField()
    method = StringField()
    weight = FloatField()

obj5 = ConvertingDeliveryMapper.from_row(row1)
assert obj5.destination == "Sydney"
assert obj5.method == "truck"
assert obj5.weight == 25.0  # Number, not string
```

Inspecting class attributes can also be used to discover methods. For example, imagine that I want a class that describes a sequential workflow of methods that need to run in definition order, like this:

检查类属性也可以用来发现方法。例如，想象一下，我想要一个类，描述需要按定义顺序运行的方法的工作流，比如这样：

```
class HypotheticalWorkflow:
    def start_engine(self):
        pass

    def release_brake(self):
        pass

    def run(self):
        # Runs `start_engine` then `release_brake`
        pass
```

I can make this work by first creating a simple function decorator (see Item 38: “Define Function Decorators with `functools.wraps` ”) that indicates which methods should be considered for the workflow.

通过首先创建一个简单的函数装饰器（请参见条目38：“使用`functools.wraps`定义函数装饰器”），可以实现这一点，该装饰器指示哪些方法应被视为工作流的一部分。

```
def step(func):
    func._is_step = True
    return func
```

A new base class can then look for callable class attributes (see Item 48: “Accept Functions Instead of Classes for Simple Interfaces” for background) with the `_is_step` attribute present to discover which methods should be included in workflow and the order in which they should be called:

一个新的基类然后可以寻找带有`_is_step`属性的可调用类属性（请参见条目48：“接受函数而非类用于简单接口”作为背景），以发现哪些方法应被包含在工作流中以及它们应该被调用的顺序：

```
class Workflow:
    def __init_subclass__(cls):
        steps = []
        for key, value in cls.__dict__.items():
            if callable(value) and hasattr(value, "_is_step"):
                steps.append(key)
        cls.steps = tuple(steps)
```

The `run` method only needs to iterate through the list of steps and call the methods in the saved sequence—no other boilerplate is required:

`run`方法只需要遍历步骤列表，并按照保存的顺序调用方法——不需要其他样板代码：

```
    def run(self):
        for step_name in type(self).steps:
            func = getattr(self, step_name)
            func()
```

Putting it together, here I define a simple workflow for starting a car, which includes a helper method which should be ignored by the base class:

整合起来，这里我定义了一个简单的启动汽车的工作流，其中包括一个应该被基类忽略的帮助方法：

```
class MyWorkflow(Workflow):
    @step
    def start_engine(self):
        print("Engine is on!")

    def my_helper_function(self):
        raise RuntimeError("Should not be called")

    @step
    def release_brake(self):
        print("Brake is off!")
```

Running the workflow is successful and doesn’t call the bad method.

运行工作流是成功的，并且不会调用坏方法。

```
workflow = MyWorkflow()
workflow.run()
>>>
Engine is on!
Brake is off!
...
```

**Things to Remember**
- You can examine the attributes and methods defined in a class body at runtime by inspecting the corresponding class object’s `__dict__` instance dictionary.
- The definition order of class bodies is preserved in a class object’s `__dict__` , enabling code to consider their relative position. This is especially useful for use-cases like mapping object fields to CSV column indexes, etc.
- Descriptors and method decorators can be used to further enhance the power of using the definition order of class bodies to control program behavior.

**注意事项**
- 您可以通过检查相应的类对象的`__dict__`实例字典，在运行时检查类体中定义的属性和方法。
- 类体的定义顺序保留在类对象的`__dict__`中，使代码能够考虑它们的相对位置。这对于诸如将对象字段映射到CSV列索引等情况特别有用。
- 描述符和方法装饰器可用于进一步增强利用类体定义顺序控制程序行为的功能。