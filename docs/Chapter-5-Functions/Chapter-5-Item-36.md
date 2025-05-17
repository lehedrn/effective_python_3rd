# Chapter 5: Functions (函数)

## Item 36: Use None and Docstrings to Specify Dynamic Default Arguments (使用 None 和文档字符串来指定动态默认参数)

Sometimes it could be helpful to use a function call, a newly created object, or a container type (like an empty `list` ) as a keyword argument’s default value. For example, say I want to print logging messages that are marked with the time of the logged event. In the default case, I want the message to include the time when the function was called. I might try the following approach, which assumes that the default value for the `when` keyword argument is reevaluated each time the function is called:

有时将函数调用、新创建的对象或容器类型（如空 `list`）作为关键字参数的默认值可能会很有帮助。例如，我想打印带有事件发生时间戳的日志消息。在默认情况下，我希望该消息包含调用函数时的时间。我可能会尝试以下方法，假设 `when` 关键字参数的默认值会在每次调用函数时重新评估：

```
from time import sleep
from datetime import datetime

def log(message, when=datetime.now()):
    print(f"{when}: {message}")

log("Hi there!")
sleep(0.1)
log("Hello again!")

>>>
2024-06-28 22:44:32.157132: Hi there!
2024-06-28 22:44:32.157132: Hello again!
```

This doesn’t work as expected. The timestamps are the same because `datetime.now` is executed only a single time: when the function is defined at module import time. A default argument value is evaluated only once per module load, which usually happens when a program starts up (see Item 97: “Lazy-load Modules with Dynamic Imports to Reduce Startup Time” for details). After the module containing this code is loaded, the `datetime.now()` default argument expression will never be evaluated again.

这并没有按预期工作。时间戳是相同的，因为 `datetime.now` 只执行了一次：即在模块导入时定义函数的时候。一个默认参数值仅在模块加载时评估一次，通常发生在程序启动时（参见条目97：“使用动态导入延迟加载模块以减少启动时间”了解详情）。一旦包含此代码的模块被加载，`datetime.now()` 默认参数表达式就不会再被评估。

The convention for achieving the desired result in Python is to provide a default value of `None` and to document the actual behavior in the docstring (see Item 118: “Write Docstrings for Every Function, Class, and Module” for background). When your code sees the argument value is `None` , you allocate the default value accordingly:

在 Python 中实现所需结果的约定是提供一个 `None` 的默认值，并在文档字符串中记录实际行为（参见条目118：“为每个函数、类和模块编写文档字符串”了解背景信息）。当你的代码看到参数值为 `None` 时，你可以相应地分配默认值：

```
def log(message, when=None):
    """Log a message with a timestamp.

    Args:
        message: Message to print.
        when: datetime of when the message occurred.
            Defaults to the present time.
    """
    if when is None:
        when = datetime.now()
    print(f"{when}: {message}")
```

Now the timestamps will be different:

现在时间戳将会不同：

```
log("Hi there!")
sleep(0.1)
log("Hello again!")
>>>
2024-06-28 22:44:32.446842: Hi there!
2024-06-28 22:44:32.551912: Hello again!
```

Using `None` for default argument values is especially important when the arguments are mutable. For example, say that I want to load a value that’s encoded as `JSON` data; if decoding the data fails, I want an empty dictionary to be returned by default:

对于可变参数，使用 `None` 作为默认参数值尤其重要。例如，我想解码以 `JSON` 格式编码的数据；如果解码失败，默认返回一个空字典：

```
import json

def decode(data, default={}):
    try:
        return json.loads(data)
    except ValueError:
        return default
```

The problem here is similar to the `datetime.now` example above. The dictionary specified for `default` will be shared by all calls to `decode` because default argument values are evaluated only once (at module load time). This can cause extremely surprising behavior:

这里的问题与上面的 `datetime.now` 示例类似。为 `default` 指定的字典将被所有对 `decode` 的调用共享，因为默认参数值只评估一次（在模块加载时）。这可能导致极其令人惊讶的行为：

```
foo = decode("bad data")
foo["stuff"] = 5
bar = decode("also bad")
bar["meep"] = 1
print("Foo:", foo)
print("Bar:", bar)
>>>
Foo: {'stuff': 5, 'meep': 1}
Bar: {'stuff': 5, 'meep': 1}
```

You might expect two different dictionaries, each with a single key and value. But modifying one seems to also modify the other. The culprit is that `foo` and `bar` are both equal to the `default` parameter to the `decode` function. They are the same dictionary object:

你可能期望得到两个不同的字典，每个都只有一个键和值。但修改其中一个似乎也修改了另一个。罪魁祸首是 `foo` 和 `bar` 都等于 `decode` 函数的 `default` 参数。它们是同一个字典对象：

```
assert foo is bar
```

The fix is to set the keyword argument default value to `None` , document the actual default value in the function’s docstring, and act accordingly in the function body when the argument has the value `None` :

解决方法是将关键字参数的默认值设置为 `None`，在函数的文档字符串中记录实际默认值，并在函数体中根据参数具有 `None` 值时采取相应的措施：

```
def decode(data, default=None):
    """Load JSON data from a string.

    Args:
        data: JSON data to decode.
        default: Value to return if decoding fails.
            Defaults to an empty dictionary.
    """
    try:
        return json.loads(data)
    except ValueError:
        if default is None:  # Check here
            default = {}
        return default
```

Now, running the same test code as before produces the expected result:

现在运行之前的测试代码会产生预期的结果：

```
foo = decode("bad data")
foo["stuff"] = 5
bar = decode("also bad")
bar["meep"] = 1
print("Foo:", foo)
print("Bar:", bar)
assert foo is not bar
>>>
Foo: {'stuff': 5}
Bar: {'meep': 1}
```

This approach also works with type annotations (see Item 124: “Consider Static Analysis via typing to Obviate Bugs”). Here, the `when` argument is marked as having an `Optional` value that is a `datetime` . Thus, the only two valid choices for `when` are `None` or a `datetime` object:

这种方法也适用于类型注解（参见条目124：“通过 `typing` 进行静态分析以消除错误”）。在这里，`when` 参数标记为具有 `datetime` 类型的可选值。因此，`when` 的唯一两个有效选择是 `None` 或 `datetime` 对象：

```
from datetime import datetime
from time import sleep

def log_typed(message: str, when: datetime | None = None) -> None:
    """Log a message with a timestamp.

    Args:
        message: Message to print.
        when: datetime of when the message occurred.
            Defaults to the present time.
    """
    if when is None:
        when = datetime.now()
    print(f"{when}: {message}")


log_typed("Hi there!")
sleep(0.1)
log_typed("Hello again!")
log_typed("And one more time", when=datetime.now())
```

**Things to Remember**
- A default argument value is evaluated only once: during function definition at module load time. This can cause odd behaviors for dynamic values (like function calls, newly created objects, and container types).
- Use None as the default value for keyword arguments that have a dynamic value. Document the actual default for the argument in the function’s docstring. Check for the `None` argument value in the function body to trigger the correct default behavior.
- Using `None` to represent keyword argument default values also works correctly with type annotations.

**注意事项**
- 默认参数值仅在模块加载时函数定义期间评估一次。这可能会导致动态值（如函数调用、新创建的对象和容器类型）出现奇怪的行为。
- 对于具有动态值的关键字参数，默认值使用 `None`。在函数的文档字符串中记录参数的实际默认值。在函数体内检查 `None` 参数值以触发正确的默认行为。
- 使用 `None` 表示关键字参数默认值与类型注解一起使用也是正确的。