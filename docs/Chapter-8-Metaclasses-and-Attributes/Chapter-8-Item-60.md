# Chapter 8: Metaclasses and Attributes (元类和属性)

## Item 60: Use Descriptors for Reusable `@property` Methods (使用描述符实现可复用的 `@property` 方法)

The big problem with the `@property` built-in (see Item 58: “Use Plain Attributes Instead of Setter and Getter Methods” and Item 59: “Consider `@property` Instead of Refactoring Attributes”) is reuse. The methods it decorates can’t be reused for multiple attributes of the same class. They also can’t be reused by unrelated classes.

`@property` 内置方法最大的问题（见第58条：“优先使用普通属性而不是设值/取值方法” 和 第59条：“考虑使用 `@property` 而不是重构属性”）是**复用性差**。它所装饰的方法无法被同一个类中的多个属性复用，也无法被不相关的类复用。

For example, say I want a class to validate that the grade received by a student on a homework assignment is a percentage:

例如，我们希望一个类能验证学生成绩是否为百分制：

```
class Homework:
    def __init__(self):
        self._grade = 0
    @property
    def grade(self):
        return self._grade
    @grade.setter
    def grade(self, value):
        if not (0 <= value <= 100):
            raise ValueError("Grade must be between 0 and 100")
        self._grade = value
```

Using `@property` makes this class easy to use:

使用 `@property` 让这个类很容易使用：

```
galileo = Homework()
galileo.grade = 95
```

Say that I also want to give the student a grade for an exam, where the exam has multiple subjects, each with a separate grade:

现在，如果还想让学生考试中各科成绩也使用相同的验证逻辑，比如语文和数学成绩：

```
class Exam:
    def __init__(self):
        self._writing_grade = 0
        self._math_grade = 0
    @staticmethod
    def _check_grade(value):
        if not (0 <= value <= 100):
            raise ValueError("Grade must be between 0 and 100")
```

This quickly gets tedious. For each section of the exam I need to add a new `@property` and related validation:

这样很快就会变得非常繁琐。每增加一个科目就需要添加一个新的 `@property` 和对应的 setter 方法：

```
@property
def writing_grade(self):
    return self._writing_grade

@writing_grade.setter
def writing_grade(self, value):
    self._check_grade(value)
    self._writing_grade = value

@property
def math_grade(self):
    return self._math_grade

@math_grade.setter
def math_grade(self, value):
    self._check_grade(value)
    self._math_grade = value
```

Also, this approach is not general. If I want to reuse this percentage validation in other classes beyond homework and exams, I’ll need to write the `@property` boilerplate and _`check_grade` method over and over again.

此外，这种方法不具备通用性。如果你想将这种百分比验证用于其他类（如作业以外的场景），你就必须一遍又一遍地重复编写这些 `@property` 方法和 `_check_grade` 方法。

The better way to do this in Python is to use a descriptor. The descriptor protocol defines how attribute access is interpreted by the language. A descriptor class can provide `__get__` and `__set__` methods that let you reuse the grade validation behavior without any boilerplate. For this purpose, descriptors are also better than mix-ins (see Item 54: “Consider Composing Functionality with Mix-in Classes”) because they let you reuse the same logic for many different attributes in a single class.

在 Python 中更好的做法是使用**描述符（Descriptor）**。描述符协议定义了语言如何解释属性访问。通过描述符，可以复用相同的验证逻辑而无需重复代码。对于这种情况，描述符甚至比混入类（Mix-in，见第54条：“考虑使用 Mix-in 类组合功能”）更优秀，因为它们允许你在同一个类中对多个属性复用相同的逻辑。

Here, I define a new class called `Exam` with class attributes that are `Grade` instances. The `Grade` class implements the descriptor protocol:

下面定义了一个新的 `Exam` 类，其类属性是 `Grade` 实例。`Grade` 类实现了描述符协议：

```
class Grade:
    def __get__(self, instance, instance_type):
        pass

    def __set__(self, instance, value):
        pass

class Exam:
    # Class attributes
    math_grade = Grade()
    writing_grade = Grade()
    science_grade = Grade()
```

Before I explain how the `Grade` class works, it’s important to understand what Python will do when such descriptor attributes are accessed on an `Exam` instance. When I assign a property:

在讲解 `Grade` 类的工作原理之前，理解以下内容很重要：当访问 `Exam` 实例的属性时，Python 是如何处理的。

```
exam = Exam()
exam.writing_grade = 40
```

it is interpreted as:

实际上等价于：

```
Exam.__dict__["writing_grade"].__set__(exam, 40)
```

When I retrieve a property:

当你获取属性值：

```
exam.writing_grade
```

it is interpreted as:

相当于：

```
Exam.__dict__["writing_grade"].__get__(exam, Exam)
```

What drives this behavior is the `__getattribute__` method of object (see Item 61: “Use `__getattr__` , `__getattribute__` , and `__setattr__` for Lazy Attributes” for background). In short, when an `Exam` instance doesn’t have an attribute named `writing_grade` , Python falls back to the `Exam` class’s attribute instead. If this class attribute is an object that has `__get__` and `__set__` methods, Python assumes that you want to follow the descriptor protocol.

驱动这一行为的是对象的 `__getattribute__` 方法（详见 第61条：“使用 `__getattr__`, `__getattribute__` 和 `__setattr__` 延迟加载属性”）。简而言之，当某个实例没有名为 `writing_grade` 的属性时，Python 会回退到该实例所属类的属性。如果该类属性是一个实现了 `__get__` 和 `__set__` 方法的对象，Python 就认为你希望遵循描述符协议。

Knowing this behavior and how I used @property for grade validation in the Homework class, here’s a reasonable first attempt at implementing the Grade descriptor:

了解了上述行为以及我们在 `Homework` 类中是如何使用 `@property` 进行成绩验证后，我们可以尝试初步实现 `Grade` 描述符：

```
class Grade:
    def __init__(self):
        self._value = 0

    def __get__(self, instance, instance_type):
        return self._value

    def __set__(self, instance, value):
        if not (0 <= value <= 100):
            raise ValueError("Grade must be between 0 and 100")
        self._value = value
```

Unfortunately, this is wrong and results in broken behavior. Accessing multiple attributes on a single `Exam` instance works as expected:

不幸的是，这种方式是错误的，会产生异常行为。访问单个 `Exam` 实例上的多个属性是正常的：

```
class Exam:
    math_grade = Grade()
    writing_grade = Grade()
    science_grade = Grade()

first_exam = Exam()
first_exam.writing_grade = 82
first_exam.science_grade = 99
print("Writing", first_exam.writing_grade)
print("Science", first_exam.science_grade)

>>>
Writing 82
Science 99
```

But accessing these attributes on multiple `Exam` instances results in surprising behavior:

但访问多个 `Exam` 实例的属性则会出现意料之外的行为：

```
second_exam = Exam()
second_exam.writing_grade = 75
print(f"Second {second_exam.writing_grade} is right")
print(f"First  {first_exam.writing_grade} is wrong; " f"should be 82")
>>>
Second 75 is right
First 75 is wrong; should be 82
```

The problem is that a single `Grade` instance is shared across all `Exam` instances for the class attribute `writing_grade` . The `Grade` instance for this attribute is constructed once in the program lifetime, when the `Exam` class is first defined, not each time an `Exam` instance is created.

问题在于，所有 `Exam` 实例共享了同一个 `Grade` 实例的状态。`Grade` 实例是在 `Exam` 类首次定义时创建的，并不会随着每次 `Exam` 实例的创建而重新构造。

To solve this, I need the `Grade` class to keep track of its value for each unique `Exam` instance. I can do this by saving the per-instance state in a dictionary:

要解决这个问题，我们需要让 `Grade` 类能够为每个不同的 `Exam` 实例保存独立的值。可以通过字典来保存每个实例对应的状态：

```
class DictGrade:
    def __init__(self):
        self._values = {}

    def __get__(self, instance, instance_type):
        if instance is None:
            return self
        return self._values.get(instance, 0)

    def __set__(self, instance, value):
        if not (0 <= value <= 100):
            raise ValueError("Grade must be between 0 and 100")
        self._values[instance] = value
```

This implementation is simple and works well, but there’s still one gotcha: It leaks memory. The `_values` dictionary holds a reference to every instance of `Exam` ever passed to `__set__` over the lifetime of the program. This causes instances to never have their reference count go to zero, preventing cleanup by the garbage collector (see Item 115: “Use `tracemalloc` to Understand Memory Usage and Leaks” for how to detect this type of problem).

这个实现简单有效，但仍有一个问题：**内存泄漏**。`_values` 字典持有程序运行期间传给 `__set__` 的每一个 `Exam` 实例的引用，这会导致这些实例永远无法被垃圾回收器回收（详见 第115条：“使用 tracemalloc 理解内存使用和泄漏”）。

Instead, you should rely on Python’s `__set_name__` special method for descriptors (see Item 64: “Annotate Class Attributes with `__set_name__` ” for background). This method is called on each descriptor instance after a class is defined. Critically, the name of the class attribute assigned to the descriptor instance is supplied by Python. This allows you to compute a string to use for the per-object attribute name (in this case, a protected field starting with `"_"` ):

因此，我们应该依赖 Python 的 `__set_name__` 特殊方法（详见 第64条：“使用 `__set_name__` 注解类属性”）。该方法会在类定义完成后被调用，参数包括当前类和类属性名称。这使得你可以动态计算每个属性存储时所使用的字段名（例如以 `"_"` 开头的受保护字段）：

```
class NamedGrade:
    def __set_name__(self, owner, name):
        self.internal_name = "_" + name
```

I can call `setattr` and `getattr` on the object with the `internal_name` from the descriptor to store and retrieve the corresponding attribute data:

我可以使用描述器中的 `internal_name` 对对象调用 `setattr` 和 `getattr`，以存储和获取对应的属性数据。

```
def __get__(self, instance, instance_type):
    if instance is None:
        return self
    return getattr(instance, self.internal_name)

def __set__(self, instance, value):
    if not (0 <= value <= 100):
        raise ValueError("Grade must be between 0 and 100")
    setattr(instance, self.internal_name, value)
```

Now I can define a new class with this improved descriptor and see how the attribute data for the descriptor resides inside the object’s instance dictionary ( `__dict__` ):

现在我们可以用这个改进后的描述符定义一个类，并查看其实例数据存储在对象的 `__dict__` 中：

```
class NamedExam:
    math_grade = NamedGrade()
    writing_grade = NamedGrade()
    science_grade = NamedGrade()

first_exam = NamedExam()
first_exam.math_grade = 78
first_exam.writing_grade = 89
first_exam.science_grade = 94
print(first_exam.__dict__)
>>>
{'math_grade': 78, 'writing_grade': 89, 'science_grade': 94}
```

Unlike the earlier implementation, this won’t leak memory because when a `NamedExam` object is garbage collected all of its attribute data, including values assigned by descriptors, will be freed too.

与之前的实现不同，这种方式不再导致内存泄漏，因为当 `NamedExam` 对象被销毁时，其所有属性数据（包括描述符设置的值）也会随之释放。

**Things to Remember**
- Reuse the behavior and validation of `@property` methods by defining your own descriptor classes.
- Use `__set_name__` along with `setattr` and `getattr` to store the data needed by descriptors in object instance dictionaries in order to avoid memory leaks.
- Don’t get bogged down trying to understand exactly how `__getattribute__` uses the descriptor protocol for getting and setting attributes.

**注意事项**
- 通过自定义描述符类，可以复用 `@property` 的行为和验证逻辑。
- 使用 `__set_name__` 结合 `setattr` 和 `getattr`，将描述符所需的数据存储在对象实例的字典中，避免内存泄漏。
- 不必深究 `__getattribute__` 如何使用描述符协议进行属性访问和设置。