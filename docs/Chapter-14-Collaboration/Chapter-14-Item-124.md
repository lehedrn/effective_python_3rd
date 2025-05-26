# Chapter 14: Collaboration (协作)

## Item 124: Consider Static Analysis via `typing` to Obviate Bugs (考虑通过 `typing` 进行静态分析以避免错误)

Providing documentation is a great way to help users of an API understand how to use it properly (see Item 118: “Write Docstrings for Every Function, Class, and Module”), but often it’s not enough, and incorrect usage still causes bugs. Ideally, there would be a programmatic mechanism to verify that callers are using your APIs the right way, and that you are using your downstream dependencies correctly as well. Many programming languages address part of this need with compile-time type checking, which can identify and eliminate some categories of bugs.

提供文档是帮助API使用者正确使用的一种好方法（参见条目118：“为每个函数、类和模块编写文档字符串”），但这通常还不够，不正确的使用仍然会导致错误。理想情况下，有一种机制可以验证调用者是否以正确的方式使用您的API，并且您是否也正确地使用了下游依赖项。许多编程语言通过编译时类型检查解决了部分需求，这可以在识别并消除某些类别错误方面发挥作用。

Historically Python has focused on dynamic features, and has not provided compile-time type safety of any kind (see Item 3: “Never Expect Python to Detect Errors at Compile Time”). However, more recently Python has introduced special syntax and the built-in `typing` module, which allow you to annotate variables, class fields, functions, and methods with type information. These type hints allow for gradual typing, where a codebase can be progressively updated to specify types as desired.

历史上，Python专注于动态特性，没有提供任何形式的编译时类型安全（参见条目3：“不要期望Python在编译时检测错误”）。然而，最近Python引入了特殊语法和内置的 `typing` 模块，允许您为变量、类字段、函数和方法添加类型信息。这些类型提示允许渐进式类型化，即可以根据需要逐步更新代码库以指定类型。

The benefit of adding type information to a Python program is that you can run static analysis tools to ingest a program’s source code and identify where bugs are most likely to occur. The `typing` built-in module doesn’t actually implement any of the type checking functionality itself. It merely provides a common library for defining types that can be applied to Python code and consumed by separate tools.

在Python程序中添加类型信息的好处是可以运行静态分析工具来解析程序的源代码，并识别错误最可能发生的区域。内置的 `typing` 模块本身并没有实现任何类型检查功能。它仅仅提供了一个用于定义类型的标准库，这些类型可以应用于Python代码并被单独的工具消费。

Much as there are multiple distinct implementations of the Python interpreter (e.g., CPython, PyPy; see Item 1: “Know Which Version of Python You’re Using”), there are multiple implementations of static analysis tools for Python that use `typing` . As of the time of this writing, the most popular tools are `mypy` (https://github.com/python/mypy), `pyright` (https://github.com/microsoft/pyright), `pyre` (https://pyre-check.org/), and `pytype` (https://github.com/google/pytype). For the `typing` examples in this book, I’ve used `mypy` with the `--strict` flag, which enables all of the various warnings supported by the tool. Here’s an example of what running the command line looks like:

就像有多个不同的Python解释器实现一样（例如，CPython，PyPy；参见条目1：“知道你正在使用的Python版本”），也有多个使用 `typing` 的Python静态分析工具实现。撰写本文时，最受欢迎的工具是 [mypy](https://github.com/python/mypy)、[pyright](https://github.com/microsoft/pyright)、[pyre](https://pyre-check.org/) 和 [pytype](https://github.com/google/pytype)。对于本书中的 `typing` 示例，我使用了带有 `--strict` 标志的 `mypy`，该标志启用了该工具支持的所有各种警告。以下是命令行运行的样子：

```
$ python3 -m mypy --strict example.py
```

These tools can be used to detect a large number of common errors before a program is ever run, which can provide an added layer of safety in addition to having good tests (see Item 109: “Prefer Integration Tests Over Unit Tests”). For example, can you find the bug in this simple function that causes it to compile fine but throw an exception at runtime?

这些工具可用于在程序运行之前检测大量常见错误，这可以在拥有良好测试的基础上提供额外的安全层（参见条目109：“集成测试优于单元测试”）。例如，你能找到这个简单函数中的错误吗？它导致了在运行时抛出异常？

```
def subtract(a, b):
    return a - b

subtract(10, "5")
>>>
Traceback ...
TypeError: unsupported operand type(s) for -: 'int' and 'str'
```

Parameter and variable type annotations are delineated with a colon (such as `name: type` ). Return value types are specified with `-> type` following the argument list. Using such type annotations and `mypy` , I can easily spot the bug:

参数和变量类型注解通过冒号进行分隔（如 `name: type`）。返回值类型通过 `-> type` 在参数列表后面指定。使用这样的类型注解和 `mypy`，我可以轻松发现错误：

```
def subtract(a: int, b: int) -> int: # Function 
    return a - b
subtract(10, "5") # Oops: passed string value
$ python3 -m mypy --strict example.py
.../example.py:4: error: Argument 2 to "subtract"
incompatible type "str"; expected "int" [arg-typ
Found 1 error in 1 file (checked 1 source file)
```

Type annotations can also be applied to classes. For example, this class has two bugs in it that will raise exceptions when the program is run:

类型注解也可以应用于类。例如，此类中有两个错误，在程序运行时会引发异常：

```
class Counter:
    def __init__(self):
        self.value = 0

    def add(self, offset):
        value += offset

    def get(self) -> int:
        self.value
```

The first one happens when I call the `add` method:

第一个错误发生在调用 `add` 方法时：

```
counter = Counter()
counter.add(5)
>>>
Traceback ...
UnboundLocalError: cannot access local variable 'value' where it is not associated with a value
```

The second bug happens when I call `get` :

第二个错误发生在调用 `get` 时：

```
counter = Counter()
found = counter.get()
assert found == 0, found
>>>
Traceback ...
AssertionError: None
```

Both of these problems are easily found in advance by `mypy` :

这两个问题都可以通过 `mypy` 提前发现：

```
class Counter:
    def __init__(self) -> None:
        self.value: int = 0 # Field / variable a
    def add(self, offset: int) -> None:
        value += offset # Oops: forgot "self
    def get(self) -> int:
        self.value # Oops: forgot "retu
counter = Counter()
counter.add(5)
counter.add(3)
assert counter.get() == 8
$ python3 -m mypy --strict example.py
.../example.py:9: error: Name "value" is not defi
defined]
.../example.py:11: error: Missing return statemen
Found 2 errors in 1 file (checked 1 source file)
```

One of the strengths of Python’s dynamism is the ability to write generic functionality that operates on duck types (see Item 25: “Be Cautious When Relying on Dictionary Insertion Ordering” and Item 57: “Inherit from `collections.abc` Classes for Custom Container Types”). This allows one implementation to accept a wide range of types, saving a lot of duplicative effort and simplifying testing. Here, I’ve defined such a generic function for combining values from a `list` together. Do you understand why the final statement fails?

Python 动态性的一个优势是能够编写操作鸭子类型的通用功能（参见条目25：“依赖字典插入顺序时要谨慎”和条目57：“为自定义容器类型继承自 `collections.abc` 类”）。这允许一个实现接受广泛的类型，节省了大量的重复工作并简化了测试。在这里，我定义了一个用于将 `list` 中的值组合在一起的通用函数。你知道为什么最后一条语句失败了吗？

```
def combine(func, values):
assert len(values) > 0

result = values[0]
for next_value in values[1:]:
    result = func(result, next_value)

return result

def add(x, y):
return x + y

inputs = [1, 2, 3, 4j]
result = combine(add, inputs)
assert result == 10, result  # Fails
>>>
Traceback ...
AssertionError: (6+4j)
```

I can use the `typing` module’s support for generics to annotate this function and detect the problem statically:

我可以使用 `typing` 模块对泛型的支持来注释此函数，并静态检测到这个问题：

```
from collections.abc import Callable
from typing import TypeVar

Value = TypeVar("Value")
Func = Callable[[Value, Value], Value]

def combine(func: Func[Value], values: list[Value]) -> Value:
    assert len(values) > 0

    result = values[0]
    for next_value in values[1:]:
        result = func(result, next_value)

    return result

Real = TypeVar("Real", int, float)

def add(x: Real, y: Real) -> Real:
    return x + y

inputs = [1, 2, 3, 4j]  # Oops: included a complex number
result = combine(add, inputs)
assert result == 10
$ python3 -m mypy --strict example.py
.../example.py:22: error: Argument 1 to "combine"
incompatible type "Callable[[Real, Real], Real]";
"Callable[[complex, complex], complex]" [arg-typ
Found 1 error in 1 file (checked 1 source file)
```

Another extremely common error is to encounter a `None` value when you thought you’d have a valid object (see Item 32: “Prefer Raising Exceptions to Returning `None` ”). This problem can affect seemingly simple code. Do you see the issue here?

另一个极其常见的错误是在认为会有有效对象的时候遇到了 `None` 值（参见条目32：“优先于返回 `None` 而引发异常”）。这个问题可能影响看似简单的代码。你能看到这里的问题吗？

```
def get_or_default(value, default):
    if value is not None:
        return value
    return value

found = get_or_default(3, 5)
assert found == 3

found = get_or_default(None, 5)
assert found == 5, found  # Fails
>>>
Traceback ...
AssertionError: None
```

The `typing` module supports option types—indicated with `type | None`——which ensure that programs only interact with values after proper null checks have been performed. This allows `mypy` to infer that there’s a bug in this code: The type used in the return statement must be `None` , and that doesn’t match the `int` type required by the function signature:

`typing` 模块支持选项类型——用 `type | None` 表示——确保程序仅在执行适当的空检查后与值交互。这允许 `mypy` 推断这段代码有一个bug：返回语句中使用的类型必须是 `None`，而这与函数签名所需的 `int` 类型不匹配：

```
def get_or_default(value: int | None, default: int):
    if value is not None:
        return value
    return value # Oops: should have returned "d
$ python3 -m mypy --strict example.py
.../example.py:4: error: Incompatible return valu
"None", expected "int") [return-value]
Found 1 error in 1 file (checked 1 source file)
```

A wide variety of other options are available in the `typing` module. See `https://docs.python.org/3/library/typing.html` for all of the details. Notably, exceptions are not included. Unlike Java, which has checked exceptions that are enforced at the API boundary of every method, Python’s type annotations are more similar to C#'s: Exceptions are not considered part of an interface’s definition. Thus, if you want to verify that you’re raising and catching exceptions properly, you need to write tests.

`typing` 模块中还提供了许多其他选项。有关所有详细信息，请参阅 `https://docs.python.org/3/library/typing.html` 。值得注意的是，异常并不包括在内。与Java不同，Java具有在每个方法的API边界强制执行的已检查异常，Python的类型注解更类似于C#：异常不被视为接口定义的一部分。因此，如果您想验证是否正确地抛出和捕获异常，则需要编写测试。

One common gotcha in using the `typing` module occurs when you need to deal with forward references (see Item 122: “Know How to Break Circular Dependencies” for a similar problem). For example, imagine that I have two classes where one holds a reference to the other. Usually the definition order of these classes doesn’t matter because they will both be defined before their instances are created later in the program:

在使用 `typing` 模块时，一个常见的陷阱是需要处理前向引用（参见条目122：“了解如何打破循环依赖”以获取类似的问题）。例如，假设我有两个类，其中一个持有另一个的引用。通常情况下，这些类的定义顺序无关紧要，因为它们都将在程序稍后的实例创建之前定义：

```
class FirstClass:
    def __init__(self, value):
        self.value = value

class SecondClass:
    def __init__(self, value):
        self.value = value

second = SecondClass(5)
first = FirstClass(second)
```

If you apply type hints to this program and run `mypy` it will say that there are no issues:

如果给这个程序应用类型提示并运行 `mypy`，它会说没有问题：

```
class FirstClass:
    def __init__(self, value: SecondClass) -> Non
        self.value = value
class SecondClass:
    def __init__(self, value: int) -> None:
        self.value = value
second = SecondClass(5)
first = FirstClass(second)
$ python3 -m mypy --strict example.py
Success: no issues found in 1 source file
```

However, if you actually try to run this code, it fails because `SecondClass` is referenced by the type annotation in the `FirstClass.__init__` method’s parameters before it’s actually defined:

但是，如果您实际尝试运行这段代码，它会失败，因为在 `FirstClass.__init__` 方法的参数中引用的类型注解之前还没有定义 `SecondClass`：

```
class FirstClass:
    def __init__(self, value: SecondClass) -> Non
        self.value = value
class SecondClass:
    def __init__(self, value: int) -> None:
        self.value = value
second = SecondClass(5)
first = FirstClass(second)
>>>
Traceback ...
NameError: name 'SecondClass' is not defined
```

The recommended workaround that’s supported by these static analysis tools is to use a string as the type annotation that contains the forward reference. The string value is later parsed and evaluated to extract the type information to check:

推荐的解决方法是由这些静态分析工具支持的，即将字符串作为包含前向引用的类型注解。字符串值随后会被解析和评估以提取类型信息来进行检查：

```
class FirstClass:
    def __init__(self, value: "SecondClass") -> None:
        self.value = value
class SecondClass:
    def __init__(self, value: int) -> None:
        self.value = value
second = SecondClass(5)
first = FirstClass(second)
```

Now that you’ve seen how to use type hints and their potential benefits, it’s important to be thoughtful about when to use them. Here are some of the best practices to keep in mind:

- It’s going to slow you down if you try to use type annotations from the start when writing a new piece of code. A general strategy is to write a first version without annotations, then write tests, and then add type information where it’s most valuable.
- Type hints are most important at the boundaries of a codebase, such as an API you provide that many callers (and thus other people) depend on. Type hints complement tests (see Item 108: “Verify Related Behaviors in `TestCase` Subclasses”) and warnings (see Item 123: “Consider `warnings` to Refactor and Migrate Usage”) to ensure that your API callers aren’t surprised or broken by your changes.
- It can be useful to apply type hints to the most complex and error prone parts of your codebase that aren’t part of an API. However, it may not be worth striving for 100% coverage in your type annotations because you’ll quickly encounter diminishing returns.
- If possible, you should include static analysis as part of your automated build and test system to ensure that every commit to your codebase is vetted for errors. In addition, the configuration used for type checking should be maintained in the repository to ensure that all of the people you collaborate with are using the same rules.
- As you add type information to your code, it’s important to run the type checker as you go. Otherwise, you may nearly finish sprinkling type hints everywhere, and then be hit by a huge wall of errors from the type checking tool, which can be disheartening and make you want to abandon type hints altogether.

现在，既然您已经了解了如何使用类型提示及其潜在的好处，那么在何时使用它们上要有深思熟虑。以下是一些最佳实践：

- 如果您在编写新代码时一开始就使用类型注解，可能会减慢您的速度。一般策略是先编写一个不带注解的第一版，然后编写测试，最后在最有价值的地方添加类型信息。
- 类型提示最重要的是在代码库的边界处，比如提供给许多调用者（以及因此其他人）依赖的API。类型提示补充了测试（参见条目108：“在 `TestCase` 子类中验证相关行为”）和警告（参见条目123：“考虑使用 `warnings` 来重构和迁移使用”），以确保您的API调用者不会因您的更改而感到意外或受损。
- 将类型提示应用于代码库中最复杂和容易出错的部分可能是有用的。不过，可能没有必要追求100%的类型注解覆盖率，因为很快您会遇到收益递减的情况。
- 如果可能的话，应该将静态分析作为自动化构建和测试系统的一部分，以确保代码库中的每次提交都经过错误检查。此外，类型检查的配置应保留在存储库中，以确保所有与您合作的人都使用相同的规则。
- 随着您向代码中添加类型信息，重要的是在过程中运行类型检查器。否则，您可能几乎完成在各处撒下类型提示的工作，然后却被类型检查工具产生的一堵巨大的错误墙所击倒，这可能会令人沮丧，并使您想要放弃类型提示。

Finally, it’s important to acknowledge that in many situations, you might not need or want to use type annotations at all. For small to medium-sized programs, ad-hoc code, legacy codebases, and prototypes, type hints may require far more effort than they’re worth.

最后，重要的是承认在许多情况下，您可能根本不需要或不想使用类型注解。对于中小型程序、临时代码、遗留代码库和原型，类型提示可能需要比其价值更多的努力。

**Things to Remember**
- Python has special syntax and the `typing` built-in module for annotating variables, fields, functions, and methods with type information.
- Static type checkers can leverage this type information to help you avoid many common bugs that would otherwise happen at runtime.
- There are a variety of best practices for adopting types in your programs, using them in APIs, and making sure that they don’t get in the way of your productivity.

**注意事项**
- Python 具有特殊语法和 `typing` 内置模块，用于为变量、字段、函数和方法添加类型信息。
- 静态类型检查器可以利用这些类型信息帮助您避免许多原本会在运行时发生的常见错误。
- 采用类型的最佳实践有很多，包括在 API 中使用类型，确保类型不会妨碍您的生产力等方面。