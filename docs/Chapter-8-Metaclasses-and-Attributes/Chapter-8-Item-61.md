# Chapter 8: Metaclasses and Attributes (元类和属性)

## Item 61: Use `__getattr__`, `__getattribute__`, and `__setattr__` for Lazy Attributes (使用 `__getattr__`、`__getattribute__` 和 `__setattr__`实现惰性属性)

Python’s `object` base class provides hooks that make it easy to write generic code for gluing systems together. For example, say that I want to represent the records in a database as Python objects. I assume that the database has its schema already defined elsewhere. In most languages, I’d need to explicitly specify in code how the database schema maps to classes and objects in my program. However, in Python, I can do this object-relational mapping generically at runtime so no boilerplate is required.

Python 的 `object` 基类提供了钩子方法，使得编写通用代码来整合系统变得容易。例如，我想要将数据库中的记录表示为 Python 对象。我假设数据库已经有定义好的模式。在大多数语言中，我需要在代码中显式指定数据库模式如何映射到程序中的类和对象。然而，在 Python 中，我可以动态地在运行时完成这种对象-关系映射，因此不需要样板代码。

How is that possible? Plain instance attributes, `@property` methods, and descriptors can’t do this because they all need to be defined in advance. Python enables this dynamic behavior with the `__getattr__` special method. If a class defines `__getattr__` , that method is called every time an attribute can’t be found in an object’s instance dictionary. Here, I define a `__getattr__` hook that will insert an attribute into the object’s instance dictionary to prove that it ran:

这可能吗？普通的实例属性、`@property` 方法和描述符无法做到这一点，因为它们都需要预先定义好。Python 通过 `__getattr__` 特殊方法实现了这种动态行为。如果一个类定义了 `__getattr__`，每当一个属性在对象的实例字典中找不到时就会调用这个方法。在这里，我定义了一个 `__getattr__` 钩子方法，该方法会在实例字典中插入一个属性以证明它已经运行：

```
class LazyRecord:
    def __init__(self):
        self.exists = 5
    def __getattr__(self, name):
        value = f"Value for {name}"
        setattr(self, name, value)
        return value
```

When I access the missing object attribute `foo` , for example, Python calls the `__getattr__` method above, which mutates the instance dictionary `__dict__` :

例如，当我访问缺失的对象属性 `foo` 时，Python 会调用上面的 `__getattr__` 方法，该方法会修改实例字典 `__dict__`：

```
data = LazyRecord()
print("Before:", data.__dict__)
print("foo: ", data.foo)
print("After: ", data.__dict__)
>>>
Before: {'exists': 5}
foo: Value for foo
After: {'exists': 5, 'foo': 'Value for foo'}
```

I can add logging to `LazyRecord` to show when `__getattr__` is actually called. Note how in this implementation I call `super().__getattr__()` to use the superclass’s implementation of `__getattr__` in order to fetch the real property value and avoid infinite recursion (see Item 53: “Initialize Parent Classes with `super` ” for background):

我可以向 `LazyRecord` 添加日志以显示何时调用了 `__getattr__`。注意在这个实现中我如何调用 `super().__getattr__()` 来使用超类的 `__getattr__` 实现，以获取实际的属性值并避免无限递归（有关背景，请参见条目53：“使用 `super` 初始化父类”）：

```
class LoggingLazyRecord(LazyRecord):
    def __getattr__(self, name):
        print(
            f"* Called __getattr__({name!r}), "
            f"populating instance dictionary"
        )
        result = super().__getattr__(name)
        print(f"* Returning {result!r}")
        return result

data = LoggingLazyRecord()
print("exists:     ", data.exists)
print("First foo:  ", data.foo)
print("Second foo: ", data.foo)

>>>
exists:      5
* Called __getattr__('foo'), populating instance dictionary
* Returning 'Value for foo'
First foo:   Value for foo
Second foo:  Value for foo
```

The `exists` attribute is present in the instance dictionary, so `__getattr__` is never called for it. The `foo` attribute is not in the instance dictionary initially, so `__getattr__` is called the first time. But the call to `__getattr__ ` for `foo` also does a `setattr` , which populates `foo` in the instance dictionary. This is why the second time I access `foo` , it doesn’t log a call to `__getattr__` .

`exists` 属性存在于实例字典中，所以永远不会为它调用 `__getattr__`。`foo` 属性最初不在实例字典中，因此第一次访问它时会调用 `__getattr__`。但是对 `foo` 的 `__getattr__` 调用也会进行 `setattr` 操作，从而在实例字典中填充 `foo`。这就是为什么第二次访问 `foo` 时不会记录对 `__getattr__` 的调用的原因。

This behavior is especially helpful for use cases like lazily accessing schemaless data. `__getattr__` runs once to do the hard work of loading a property; all subsequent accesses retrieve the existing result.

这种行为对于诸如惰性访问无模式数据之类的用例特别有用。`__getattr__` 运行一次以执行加载属性的艰苦工作；所有后续访问都检索现有的结果。

Now imagine that I also want transactions in this database system. The next time the user accesses a dynamic attribute, I want to know whether the corresponding record in the database is still valid and whether the transaction is still open. The `__getattr__` hook won’t get called every time the attribute is accessed because it will use the object’s instance dictionary as the fast path for existing attributes.

现在设想我也希望在这个数据库系统中有事务功能。下一次用户访问动态属性时，我希望知道数据库中对应的记录是否仍然有效，以及事务是否仍然打开。由于属性存在时会使用对象的实例字典作为快速路径，`__getattr__` 钩子不会在每次访问属性时被调用。

To enable this more advanced use case, Python has another `object` hook called `__getattribute__` . This special method is called every time an attribute is accessed on an object, even in cases where it does exist in the attribute dictionary. This enables me to do things like check global transaction state on every property access. It’s important to note that such an operation can incur significant overhead and negatively impact performance, but sometimes it’s worth it. Here, I define `ValidatingRecord` to log each time `__getattribute__` is called:

为了支持这种更高级的用例，Python 有另一个名为 `__getattribute__` 的 `object` 钩子。这个特殊方法在对象上的每次属性访问时都会被调用，即使该属性确实存在于属性字典中。这使我能够执行诸如检查全局事务状态之类的操作。需要注意的是，这样的操作可能会产生显著的开销并影响性能，但有时这是值得的。这里我定义 `ValidatingRecord` 来记录每次调用 `__getattribute__` 的情况：

```
class ValidatingRecord:
    def __init__(self):
        self.exists = 5
    def __getattribute__(self, name):
        print(f"* Called __getattribute__({name!r})")
        try:
            value = super().__getattribute__(name)
            print(f"* Found {name!r}, returning {value!r}")
            return value
        except AttributeError:
            value = f"Value for {name}"
            print(f"* Setting {name!r} to {value!r}")
            setattr(self, name, value)
            return value

data = ValidatingRecord()
print("exists:     ", data.exists)
print("First foo:  ", data.foo)
print("Second foo: ", data.foo)

>>>
* Called __getattribute__('exists')
* Found 'exists', returning 5
exists: 5
* Called __getattribute__('foo')
* Setting 'foo' to 'Value for foo'
First foo: Value for foo
* Called __getattribute__('foo')
* Found 'foo', returning 'Value for foo'
Second foo: Value for foo
```

In the event that a dynamically accessed property shouldn’t exist, you can raise an `AttributeError` to cause Python’s standard missing property behavior for both `__getattr__` and `__getattribute__` :

如果某个动态访问的属性不应该存在，则可以在 `__getattr__` 和 `__getattribute__` 中引发 `AttributeError` 来导致 Python 的标准缺失属性行为：

```
class MissingPropertyRecord:
    def __getattr__(self, name):
        if name == "bad_name":
            raise AttributeError(f"{name} is missing")
        value = f"Value for {name}"
        setattr(self, name, value)
        return value

data = MissingPropertyRecord()

data.bad_name
>>>
Traceback ...
AttributeError: bad_name is missing
```

Python code implementing generic functionality often relies on the `hasattr` built-in function to determine when properties exist, and the `getattr` built-in function to retrieve property values. These functions also look in the instance dictionary for an attribute name before calling `__getattr__` :

实现通用功能的 Python 代码通常依赖内置函数 `hasattr` 来确定属性是否存在，以及内置函数 `getattr` 来检索属性值。这些函数在调用 `__getattr__` 之前也会在实例字典中查找属性名：

```
data = LoggingLazyRecord()  # Implements __getattr__
print("Before:         ", data.__dict__)
print("Has first foo:  ", hasattr(data, "foo"))
print("After:          ", data.__dict__)
print("Has second foo: ", hasattr(data, "foo"))
>>>
Before: {'exists': 5}
* Called __getattr__('foo'), populating instance 
* Returning 'Value for foo'
Has first foo: True
After:           {'exists': 5, 'foo': 'Value for foo'}
Has second foo: True
```

In the example above, `__getattr__` is called only once (for the first `hasattr` call). In contrast, classes that implement `__getattribute__` have that method called each time `hasattr` or `getattr` is used with an instance:

在上面的例子中，`__getattr__` 只会被调用一次（用于第一次 `hasattr` 调用）。相反，实现了 `__getattribute__` 的类在其每个实例上使用 `hasattr` 或 `getattr` 时都会调用该方法：

```
data = ValidatingRecord()  # Implements __getattribute__
print("Has first foo:  ", hasattr(data, "foo"))
print("Has second foo: ", hasattr(data, "foo"))
>>>
* Called __getattribute__('foo')
* Setting 'foo' to 'Value for foo'
Has first foo: True
* Called __getattribute__('foo')
* Found 'foo', returning 'Value for foo'
Has second foo: True
```

Now, say that I want to lazily push data back to the database when values are assigned to my Python object. I can do this with `__setattr__` , a similar `object` hook that lets you intercept arbitrary attribute assignments. Unlike when retrieving an attribute with `__getattr__` and `__getattribute__` , there’s no need for two separate methods. The `__setattr__` method is always called every time an attribute is assigned on an instance (either directly or through the `setattr` built-in function):

现在，假设我希望在我分配值给 Python 对象时懒惰地将数据推回数据库。我可以使用 `__setattr__` 来实现，这是一个类似的 `object` 钩子方法，它允许拦截任意的属性赋值。与通过 `__getattr__` 和 `__getattribute__` 检索属性不同，不需要两个不同的方法。无论通过直接赋值还是通过 `setattr` 内置函数，`__setattr__` 方法总是在每次实例属性赋值时被调用：

```
class SavingRecord:
    def __setattr__(self, name, value):
        # Save some data for the record
        pass
        super().__setattr__(name, value)
```


Here, I define a logging subclass of `SavingRecord` . Its `__setattr__` method is always called on each attribute assignment:

在这里，我定义了一个 `SavingRecord` 的日志子类。它的 `__setattr__` 方法在每次属性赋值时都会被调用：

```
class LoggingSavingRecord(SavingRecord):
    def __setattr__(self, name, value):
        print(f"* Called __setattr__({name!r}, {value!r})")
        super().__setattr__(name, value)

data = LoggingSavingRecord()
print("Before: ", data.__dict__)
data.foo = 5
print("After:  ", data.__dict__)
data.foo = 7
print("Finally:", data.__dict__)

>>>
Before: {}
* Called __setattr__('foo', 5)
After: {'foo': 5}
* Called __setattr__('foo', 7)
Finally: {'foo': 7}
```

The problem with `__getattribute__` and `__setattr__` is that they’re called on every attribute access for an object, even when you might not want that to happen. For example, say that attribute accesses on my object should actually look up keys in an associated dictionary:

`__getattribute__` 和 `__setattr__` 的问题是它们在每个对象的属性访问时都被调用，即使你可能不希望这样发生。例如，假设我的对象上的属性访问实际上应该在关联的字典中查找键：

```
class BrokenDictionaryRecord:
    def __init__(self, data):
        self._data = data
    def __getattribute__(self, name):
        print(f"* Called __getattribute__({name!r})")
        return self._data[name]
```

This requires accessing `self._data` from the `__getattribute__` method. However, if I actually try to do that, Python will recurse until it reaches its stack limit, and then the program will crash:

这需要从 `__getattribute__` 方法访问 `self._data`。然而，如果我真的尝试这样做，Python 将递归直到达到其堆栈限制，然后程序将崩溃：

```
data = BrokenDictionaryRecord({"foo": 3})
data.foo
>>>
* Called __getattribute__('foo')
* Called __getattribute__('_data')
* Called __getattribute__('_data')
* Called __getattribute__('_data')
...
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "<stdin>", line 6, in __getattribute__
  File "<stdin>", line 6, in __getattribute__
  File "<stdin>", line 6, in __getattribute__
  [Previous line repeated 996 more times]
RecursionError: maximum recursion depth exceeded
```

The problem is that `__getattribute__` accesses `self._data` , which causes `__getattribute__` to run again, which accesses `self._data` again, and so on. The solution is to use the `super().__getattribute__` method to fetch values from the instance attribute dictionary; this avoids the accidental recursion:

问题在于 `__getattribute__` 访问了 `self._data`，这又会导致 `__getattribute__` 再次运行，依此类推。解决方案是使用 `super().__getattribute__` 方法从实例属性字典中获取值；这可以避免意外递归：

```
class DictionaryRecord:
    def __init__(self, data):
        self._data = data

    def __getattribute__(self, name):
        # Prevent weird interactions with isinstance() used
        # by example code harness.
        if name == "__class__":
            return DictionaryRecord
        print(f"* Called __getattribute__({name!r})")
        data_dict = super().__getattribute__("_data")
        return data_dict[name]

data = DictionaryRecord({"foo": 3})
print("foo: ", data.foo)

>>>
* Called __getattribute__('foo')
foo: 3
```

`__setattr__` methods that modify attributes on an object similarly need to use `super().__setattr__` .

类似地，修改对象属性的 `__setattr__` 方法也需要使用 `super().__setattr__`。

**Things to Remember**
- Use `__getattr__` and `__setattr__` to lazily load and save attributes for an object.
- Understand that `__getattr__` only gets called when accessing a missing attribute, whereas `__getattribute__` gets called every time any attribute is accessed.
- Avoid infinite recursion in `__getattribute__` and `__setattr__` method implementations by calling `super().__getattribute__` and `super().__getattr__` to access object attributes.

**注意事项**
- 使用 `__getattr__` 和 `__setattr__` 来延迟加载和保存对象的属性。
- 理解到 `__getattr__` 只有在访问缺失属性时才会被调用，而 `__getattribute__` 则在每次访问任何属性时都会被调用。
- 在 `__getattribute__` 和 `__setattr__` 方法实现中，通过调用 `super().__getattribute__` 和 `super().__getattr__` 来访问对象属性，以避免无限递归。