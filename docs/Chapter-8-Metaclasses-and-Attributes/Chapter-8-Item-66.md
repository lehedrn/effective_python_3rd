# Chapter 8: Metaclasses and Attributes (元类和属性)

## Item 66: Prefer Class Decorators over Metaclasses for Composable Class Extensions (对于可组合的类扩展，优先使用类装饰器而非元类)

Although metaclasses allow you to customize class creation in multiple ways (see Item 62: “Validate Subclasses with `__init_subclass__` ” and Item 63: “Register Class Existence with `__init_subclass__` ”), they still fall short of handling every situation that may arise.

尽管元类允许以多种方式定制类的创建过程（参见条目62：“使用 `__init_subclass__` 验证子类” 和条目63：“使用 `__init_subclass__` 注册类的存在”），但它们仍然无法处理可能出现的各种情况。

For example, say that I want to decorate all of the methods of a class with a helper function that prints arguments, return values, and any exceptions that were raised. Here, I define such a debugging decorator (see Item 38: “Define Function Decorators with `functools.wraps` ” for background):

例如，假设我希望用一个辅助函数来装饰类的所有方法，该辅助函数打印参数、返回值以及可能引发的异常。这里我定义了一个这样的调试装饰器（参见条目38：“使用 `functools.wraps` 定义函数装饰器” 了解背景）：

```
from functools import wraps

def trace_func(func):
    if hasattr(func, "tracing"):  # Only decorate once
        return func
    @wraps(func)
    def wrapper(*args, **kwargs):
        args_repr = repr(args)
        kwargs_repr = repr(kwargs)
        result = None
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            result = e
            raise
        finally:
            print(
                f"{func.__name__}"
                f"({args_repr}, {kwargs_repr}) -> "
                f"{result!r}"
            )
    wrapper.tracing = True
    return wrapper
```

I can apply this decorator to various special methods in my new `dict` subclass (see Item 57: “Inherit from `collections.abc` Classes for Custom Container Types”):

我可以将这个装饰器应用到我的新 `dict` 子类的各种特殊方法中（参见条目57：“为自定义容器类型继承 `collections.abc` 类”）：

```
class TraceDict(dict):
    @trace_func
    def __init__(self, *args, **kwargs):
        return super().__init__(*args, **kwargs)
    @trace_func
    def __setitem__(self, *args, **kwargs):
        return super().__setitem__(*args, **kwargs)
    @trace_func
    def __getitem__(self, *args, **kwargs):
        return super().__getitem__(*args, **kwargs)
```

And I can verify that these methods are decorated by interacting with an instance of the class:
通过与类实例交互，我可以验证这些方法是否被装饰：

```
trace_dict = TraceDict([("hi", 1)])
trace_dict["there"] = 2
trace_dict["hi"]
try:
    trace_dict["does not exist"]
except KeyError:
    pass  # Expected

>>>
__init__(({}, [('hi', 1)]), {}) -> None
__setitem__(({'hi': 1}, 'there', 2), {}) -> None
__getitem__(({'hi': 1, 'there': 2}, 'hi'), {}) -> 1
__getitem__(({'hi': 1, 'there': 2}, 'does not exist'), {}) -> KeyError('does not exist')
```

The problem with this code is that I had to redefine all of the methods that I wanted to decorate with `@trace_func` . This is redundant boilerplate that’s hard to read and error prone. Further, if a new method is later added to the `dict` superclass, it won’t be decorated unless I also define it in `TraceDict` .

这段代码的问题在于，我必须重新定义所有希望用 `@trace_func` 装饰的方法。这是冗余的样板代码，难以阅读且容易出错。此外，如果以后在 `dict` 超类中添加了新方法，则除非我也在 `TraceDict` 中定义它，否则不会对其进行装饰。

One way to solve this problem is to use a metaclass to automatically decorate all methods of a class. Here, I implement this behavior by wrapping each function or method in the new type with the `trace_func` decorator:

解决这个问题的一种方法是使用元类来自动生成类的所有方法的装饰。在这里，我通过使用 `trace_func` 装饰器包装新类型中的每个函数或方法来实现此行为：

```
import types

TRACE_TYPES = (
    types.MethodType,
    types.FunctionType,
    types.BuiltinFunctionType,
    types.BuiltinMethodType,
    types.MethodDescriptorType,
    types.ClassMethodDescriptorType,
    types.WrapperDescriptorType,
)

IGNORE_METHODS = (
    "__repr__",
    "__str__",
)

class TraceMeta(type):
    def __new__(meta, name, bases, class_dict):
        klass = super().__new__(meta, name, bases, class_dict)
        for key in dir(klass):
            if key in IGNORE_METHODS:
                continue
            value = getattr(klass, key)
            if not isinstance(value, TRACE_TYPES):
                continue
            wrapped = trace_func(value)
            setattr(klass, key, wrapped)
        return klass
```

Now, I can declare my `dict` subclass by using the `TraceMeta` metaclass and verify that it works as expected:

现在，我可以声明我的 `dict` 子类并使用 `TraceMeta` 元类，并验证其按预期工作：

```
class TraceDict(dict, metaclass=TraceMeta):
    pass

trace_dict = TraceDict([("hi", 1)])
trace_dict["there"] = 2
trace_dict["hi"]
try:
    trace_dict["does not exist"]
except KeyError:
    pass  # Expected

>>>
__new__((<class '__main__.TraceDict'>, [('hi', 1)]), {}) -> {}
__init__(({}, [('hi', 1)]), {}) -> None
__setitem__(({'hi': 1}, 'there', 2), {}) -> None
__getitem__(({'hi': 1, 'there': 2}, 'hi'), {}) -> 1
1
__getitem__(({'hi': 1, 'there': 2}, 'does not exist'), {}) -> KeyError('does not exist')
```

This works, and it even prints out a call to `__new__` that was missing from my earlier implementation. What happens if I try to use `TraceMeta` when a superclass already has specified a metaclass?

这有效，甚至打印出了早期实现中缺失的 `__new__` 调用。但如果我在某个已经指定了元类的父类上尝试使用 `TraceMeta` 会发生什么？

```
class OtherMeta(type):
    pass
class SimpleDict(dict, metaclass=OtherMeta):
    pass
class ChildTraceDict(SimpleDict, metaclass=TraceMeta):
    pass
>>>
Traceback ...
TypeError: metaclass conflict: the metaclass of a derived class must be a (non-strict) subclass of the metaclasses of all its bases
```

This fails because `TraceMeta` does not inherit from `OtherMeta` . In theory, I can use metaclass inheritance to solve this problem by having `OtherMeta` inherit from `TraceMeta` :

由于 `TraceMeta` 没有继承自 `OtherMeta`，所以失败了。理论上，我可以通过让 `OtherMeta` 继承自 `TraceMeta` 来解决这个问题：

```
class TraceMeta(type):
    def __new__(meta, name, bases, class_dict):
        klass = super().__new__(meta, name, bases, class_dict)
        for key in dir(klass):
            if key in IGNORE_METHODS:
                continue
            value = getattr(klass, key)
            if not isinstance(value, TRACE_TYPES):
                continue
            wrapped = trace_func(value)
            setattr(klass, key, wrapped)
        return klass


class OtherMeta(TraceMeta):
    pass

class SimpleDict(dict, metaclass=OtherMeta):
    pass

class ChildTraceDict(SimpleDict, metaclass=TraceMeta):
    pass

trace_dict = ChildTraceDict([("hi", 1)])
trace_dict["there"] = 2
trace_dict["hi"]
try:
    trace_dict["does not exist"]
except KeyError:
    pass  # Expected

>>>
__init_subclass__((), {}) -> None
__new__((<class '__main__.ChildTraceDict'>, [('hi', 1)]), {}) -> {}
__init__(({}, [('hi', 1)]), {}) -> None
__setitem__(({'hi': 1}, 'there', 2), {}) -> None
__getitem__(({'hi': 1, 'there': 2}, 'hi'), {}) -> 1
1
__getitem__(({'hi': 1, 'there': 2}, 'does not exist'), {}) -> KeyError('does not exist')
```

But this won’t work if the metaclass is from a library that I can’t modify, or if I want to use multiple utility metaclasses like `TraceMeta` at the same time. The metaclass approach puts too many constraints on the class that’s being modified.

但如果元类来自一个我无法修改的库，或者我想同时使用多个像 `TraceMeta` 这样的实用元类，这种方法就不可行了。元类方法对正在被修改的类施加了太多限制。

To solve this problem, Python supports class decorators. Class decorators work just like function decorators: They’re applied with the `@` symbol prefixing a function before the class declaration. The function is expected to modify or re-create the class accordingly and then return it, like this:

为了解决这个问题，Python 支持类装饰器。类装饰器的工作原理与函数装饰器相同：它们通过在类声明前使用带有 `@` 符号的函数来应用。该函数需要适当修改或重新创建类，然后返回它，如下所示：

```
def my_class_decorator(klass):
    klass.extra_param = "hello"
    return klass

@my_class_decorator
class MyClass:
    pass

print(MyClass)
print(MyClass.extra_param)

>>>
<class '__main__.MyClass'>
hello
```

I can implement a class decorator to apply the `trace_func` function decorator to all methods of a class by moving the core of the `TraceMeta.__new__` method above into a stand-alone function. This implementation is much shorter than the metaclass version:

我可以通过将上面 `TraceMeta.__new__` 方法的核心移动到一个独立的函数中来实现一个类装饰器来应用 `trace_func` 函数装饰器到类的所有方法上。这种实现比使用元类的版本要简短得多：

```
def trace(klass):
    for key in dir(klass):
        if key in IGNORE_METHODS:
            continue
        value = getattr(klass, key)
        if not isinstance(value, TRACE_TYPES):
            continue
        wrapped = trace_func(value)
        setattr(klass, key, wrapped)
    return klass
```

I can apply this decorator to my `dict` subclass to get the same behavior that I get by using the metaclass approach above:

我可以将此装饰器应用于我的 `dict` 子类，以获得与使用元类方法相同的行为：

```
@trace
class DecoratedTraceDict(dict):
    pass

trace_dict = DecoratedTraceDict([("hi", 1)])
trace_dict["there"] = 2
trace_dict["hi"]
try:
    trace_dict["does not exist"]
except KeyError:
    pass  # Expected
>>>
__new__((<class '__main__.DecoratedTraceDict'>, [('hi', 1)]), {}) -> {}
__init__(({}, [('hi', 1)]), {}) -> None
__setitem__(({'hi': 1}, 'there', 2), {}) -> None
__getitem__(({'hi': 1, 'there': 2}, 'hi'), {}) -> 1
1
__getitem__(({'hi': 1, 'there': 2}, 'does not exist'), {}) -> KeyError('does not exist')
```

Class decorators also work when the class being decorated already has a metaclass:

当被装饰的类已经有一个元类时，类装饰器也能正常工作：

```
class OtherMeta(type):
    pass

@trace
class HasMetaTraceDict(dict, metaclass=OtherMeta):
    pass

trace_dict = HasMetaTraceDict([("hi", 1)])
trace_dict["there"] = 2
trace_dict["hi"]
try:
    trace_dict["does not exist"]
except KeyError:
    pass  # Expected

>>>
__new__((<class '__main__.HasMetaTraceDict'>, [('hi', 1)]), {}) -> {}
__init__(({}, [('hi', 1)]), {}) -> None
__setitem__(({'hi': 1}, 'there', 2), {}) -> None
__getitem__(({'hi': 1, 'there': 2}, 'hi'), {}) -> 1
1
__getitem__(({'hi': 1, 'there': 2}, 'does not exist'), {}) -> KeyError('does not exist')
```

When you’re looking for composable ways to extend classes, class decorators are the best tool for the job. (See Item 103: “Know How to Use `heapq` for Priority Queues” for an example class decorator called `functools.total_ordering` .)

当你寻找一种可组合的方式来扩展类时，类装饰器是最好的工具。（参见条目103：“了解如何使用 `heapq` 实现优先队列” 了解名为 `functools.total_ordering` 的类装饰器示例。）

**Things to Remember**
- A class decorator is a simple function that receives a `class` instance as a parameter and returns either a new class or a modified version of the original class.
- Class decorators are useful when you want to modify every method or attribute of a class with minimal boilerplate.
- Metaclasses can’t be composed together easily, while many class decorators can be used to extend the same class without conflicts.

**注意事项**
- 类装饰器是一个简单的函数，它接收一个 `class` 实例作为参数，并返回一个新的类或原始类的修改版本。
- 当你想要以最小的样板代码修改类的每个方法或属性时，类装饰器非常有用。
- 元类之间不容易组合在一起，而许多类装饰器可以用来扩展同一个类而不发生冲突。