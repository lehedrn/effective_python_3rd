# Chapter 14: Collaboration (协作)

## Item 123: Consider `warnings` to Refactor and Migrate Usage (考虑使用 `warnings` 来重构和迁移用法)

It’s natural for APIs to change in order to satisfy new requirements that meet formerly unanticipated needs. When an API is small and has few upstream or downstream dependencies, making such changes is straightforward. One programmer can often update a small API and all of its callers in a single commit to the source code repository.

为了满足之前未预料到的新需求，API 发生变化是很自然的事情。当一个 API 很小且上下游依赖较少时，进行这种更改是直接且简单的。通常，一个程序员可以在一次提交中更新一个小的 API 及其所有调用者。

However, as a codebase grows, the number of callers of an API can become so large or fragmented across repositories that it’s infeasible or impractical to make API changes in lockstep with updating callers to match. Instead, you need a way to notify and encourage the people that you collaborate with to refactor their code and migrate their API usage to the latest forms.

然而，随着代码库的增长，API 的调用者数量可能会变得非常庞大或分散在多个仓库中，使得同步更新 API 和调用者变得不可行或不切实际。因此，你需要一种方式来通知并与你的合作伙伴沟通，鼓励他们重构代码并将其 API 使用迁移到最新的形式。

For example, say that I want to provide a module for calculating how far a car will travel at a given average speed and duration. Here, I define such a function and assume that speed is in miles per hour and duration is in hours:

例如，假设我想要提供一个模块来计算一辆汽车在给定平均速度和持续时间下行驶的距离。在这里，我定义了一个这样的函数，并假设速度是以英里每小时为单位，持续时间是以小时为单位：

```
def print_distance(speed, duration):
    distance = speed * duration
    print(f"{distance} miles")

print_distance(5, 2.5)
>>>
12.5 miles
```

Imagine that this works so well that I quickly gather a large number of dependencies on this function. Other programmers that I collaborate with need to calculate and print distances like this all across our shared codebase.

想象一下，这工作得很好，以至于我迅速积累了大量对该函数的依赖。我和我合作的其他程序员需要在整个共享代码库中计算和打印距离。

Despite its success, this implementation is error prone because the units for the arguments are implicit. For example, if I wanted to see how far a bullet travels in 3 seconds at 1000 meters per second, I would get the wrong result:

尽管它很成功，但这个实现容易出错，因为参数的单位是隐含的。例如，如果我想知道一颗子弹以 1000 米每秒的速度在 3 秒内飞行多远，我会得到错误的结果：

```
print_distance(1000, 3)
>>>
3000 miles
```

I can address this problem by expanding the API of `print_distance` to include optional keyword arguments (see Item 37: “Enforce Clarity with Keyword-Only and Positional-Only Arguments”) for the units of `speed` , `duration` , and the computed distance to print out:

我可以通过扩展 `print_distance` 的 API 来解决这个问题，添加可选的关键字参数（参见 Item 37：“通过关键字限定和位置限定参数强制清晰度”）来表示 `speed`、`duration` 和计算输出的距离的单位：

```
CONVERSIONS = {
    "mph": 1.60934 / 3600 * 1000,  # m/s
    "hours": 3600,                 # seconds
    "miles": 1.60934 * 1000,       # m
    "meters": 1,                   # m
    "m/s": 1,                      # m/s
    "seconds": 1,                  # s
}

def convert(value, units):
    rate = CONVERSIONS[units]
    return rate * value

def localize(value, units):
    rate = CONVERSIONS[units]
    return value / rate

def print_distance(
    speed,
    duration,
    *,
    speed_units="mph",
    time_units="hours",
    distance_units="miles",
):
    norm_speed = convert(speed, speed_units)
    norm_duration = convert(duration, time_units)
    norm_distance = norm_speed * norm_duration
    distance = localize(norm_distance, distance_units)
    print(f"{distance} {distance_units}")
```

Now, I can modify the speeding bullet call and produce an accurate result with a unit conversion to miles:

现在，我可以修改该函数的高速子弹调用，并通过转换成英里来产生准确的结果：

```
print_distance(
    1000,
    3,
    speed_units="meters",
    time_units="seconds",
)
>>>
1.8641182099494205 miles
```

It seems like requiring units to be specified for this function is a much better way to go. Making them explicit reduces the likelihood of errors and is easier for new readers of the code to understand. But how can I migrate all callers of the API over to always specifying units? How do I minimize breakage of any code that’s dependent on `print_distance` while also encouraging callers to adopt the new units arguments as soon as possible?

似乎要求指定此函数的单位是一个更好的方法。使其明确减少了错误的可能性，并且对于代码的新读者来说更容易理解。但是，如何将所有调用者迁移到始终指定单位？如何最小化对任何依赖 `print_distance` 的代码造成破坏的同时，尽快鼓励调用者采用新的单位参数？

For this purpose, Python provides the built-in `warnings` module. Using `warnings` is a programmatic way to inform other programmers that their code needs to be modified due to a change to an underlying library that they depend on. While exceptions are primarily for automated error handling by machines (see Item 81: “ `assert` Internal Assumptions, `raise` Missed Expectations”), warnings are all about communication between humans about what to expect in their collaboration with each other.

为此，Python 提供了内置的 `warnings` 模块。使用 `warnings` 是一种程序化的方式，告知其他程序员他们的代码需要由于底层库的变化而进行修改。虽然异常主要用于由机器自动处理的错误（参见 Item 81：“使用 `assert` 断言内部假设，使用 `raise` 抛出未预期的情况”），警告主要是关于人们之间就彼此协作中的期待交流信息。

I can modify `print_distance` to issue warnings when the optional keyword arguments for specifying units are not supplied. This way, the arguments can continue being optional temporarily, while providing an explicit notice to people running dependent programs that they should expect breakage in the future if they fail to take action:

我可以修改 `print_distance`，在没有提供用于指定单位的可选关键字参数时发出警告。这样，这些参数可以暂时保持可选状态，同时向运行依赖程序的人明确通知，如果不采取行动，将来可能会发生中断：

```
import warnings

def print_distance(
    speed,
    duration,
    *,
    speed_units=None,
    time_units=None,
    distance_units=None,
):
    if speed_units is None:
        warnings.warn(
            "speed_units required",
            DeprecationWarning,
        )
        speed_units = "mph"

    if time_units is None:
        warnings.warn(
            "time_units required",
            DeprecationWarning,
        )
        time_units = "hours"

    if distance_units is None:
        warnings.warn(
            "distance_units required",
            DeprecationWarning,
        )
        distance_units = "miles"

    norm_speed = convert(speed, speed_units)
    norm_duration = convert(duration, time_units)
    norm_distance = norm_speed * norm_duration
    distance = localize(norm_distance, distance_units)
    print(f"{distance} {distance_units}")
```

I can verify that this code issues a warning by calling the function with the same arguments as before and capturing the `sys.stderr` output from the `warnings` module:

我可以验证这段代码是否发出警告，方法是像以前一样调用函数并捕获来自 `warnings` 模块的 `sys.stderr` 输出：

```
import contextlib
import io

fake_stderr = io.StringIO()
with contextlib.redirect_stderr(fake_stderr):
    print_distance(
        1000,
        3,
        speed_units="meters",
        time_units="seconds",
    )

print(fake_stderr.getvalue())

>>>
1.8641182099494205 miles
.../example.py:121: DeprecationWarning: distance_
 warnings.warn(
```

Adding warnings to this function required quite a lot of repetitive boilerplate that’s hard to read and maintain. Also, the warning message indicates the line where `warning.warn` was called, but what I really want to point out is where the call to `print_distance` was made without soon-to-be-required keyword arguments.

向此函数添加警告需要相当多的重复样板代码，难以阅读和维护。此外，警告消息指出的是调用 `warning.warn` 的那一行，但我真正想指出的是在哪里调用了没有即将成为必需的关键字参数的 `print_distance`。

Luckily, the `warnings.warn` function supports the `stacklevel` parameter, which makes it possible to report the correct place in the stack as the cause of the warning. `stacklevel` also makes it easy to write functions that can issue warnings on behalf of other code, reducing boilerplate. Here, I define a helper function that warns if an optional argument wasn’t supplied and then provides a default value for it:

幸运的是，`warnings.warn` 函数支持 `stacklevel` 参数，这使得可以报告堆栈中的正确位置作为警告的原因。`stacklevel` 还使得编写代表其他代码发出警告的函数变得简单，从而减少样板代码。在这里，我定义了一个辅助函数，如果没有提供可选参数，则发出警告，然后为其提供默认值：

```
def require(name, value, default):
    if value is not None:
        return value
    warnings.warn(
        f"{name} will be required soon, update your code",
        DeprecationWarning,
        stacklevel=3,
    )
    return default

def print_distance(
    speed,
    duration,
    *,
    speed_units=None,
    time_units=None,
    distance_units=None,
):
    speed_units = require(
        "speed_units",
        speed_units,
        "mph",
    )
    time_units = require(
        "time_units",
        time_units,
        "hours",
    )
    distance_units = require(
        "distance_units",
        distance_units,
        "miles",
    )

    norm_speed = convert(speed, speed_units)
    norm_duration = convert(duration, time_units)
    norm_distance = norm_speed * norm_duration
    distance = localize(norm_distance, distance_units)
    print(f"{distance} {distance_units}")
```

I can verify that this propagates the proper offending line by inspecting the captured output:

我可以检查捕获的输出来验证这一点是否传播到了正确的行：

```
import contextlib
import io

fake_stderr = io.StringIO()
with contextlib.redirect_stderr(fake_stderr):
    print_distance(
        1000,
        3,
        speed_units="meters",
        time_units="seconds",
    )

print(fake_stderr.getvalue())

>>>
1.8641182099494205 miles
.../example.py:208: DeprecationWarning: distance_
 print_distance(
```

The `warnings` module also lets you configure what should happen when a warning is encountered. One option is to make all warnings become errors, which raises the warning as an exception instead of printing it out to `sys.stderr` :

`warnings` 模块还允许你配置遇到警告时应该发生的事情。其中一个选项是让所有警告都变成错误，这会将警告作为异常抛出而不是打印到 `sys.stderr`：

```
warnings.simplefilter("error")
try:
    warnings.warn(
        "This usage is deprecated",
        DeprecationWarning,
    )
except DeprecationWarning:
    pass  # Expected
```

This exception-raising behavior is especially useful for automated tests in order to detect changes in upstream dependencies and fail tests accordingly. Using such test failures is a great way to make it clear to the people who you collaborate with that they will need to update their code. You can use the `-W error` command-line argument to the Python interpreter or the `PYTHONWARNINGS` environment variable to apply this policy:

这种引发异常的行为在自动化测试中特别有用，用来检测上游依赖的变化并相应地使测试失败。利用这种测试失败是一种很好的方式，让与你合作的人清楚地知道他们需要更新他们的代码。你可以使用 Python 解释器的 `-W error` 命令行参数或 `PYTHONWARNINGS` 环境变量来应用此策略：

```
$ python3 -W error example_test.py
Traceback (most recent call last):
 File ".../example_test.py", line 6, in <module>
 warnings.warn("This might raise an exception
UserWarning: This might raise an exception!
```

Once the people responsible for code that depends on a deprecated API are aware that they’ll need to do a migration, they can tell the warnings module to ignore the error by using the `simplefilter` and `filterwarnings` functions (see `https://docs.python.org/3/library/warnings` for details):

一旦负责依赖于已弃用 API 的代码的人意识到他们需要进行迁移，他们可以通过使用 `simplefilter` 和 `filterwarnings` 函数告诉 warnings 模块忽略错误（详情请参阅 [https://docs.python.org/3/library/warnings](https://docs.python.org/3/library/warnings)）：

```
warnings.simplefilter("ignore")
warnings.warn("This will not be printed to stderr
```

After a program is deployed into production, it doesn’t make sense for warnings to cause errors because they might crash the program at a critical time. Instead, a better approach is to replicate warnings into the `logging` built-in module. Here, I accomplish this by calling the `logging.captureWarnings` function and configuring the corresponding `"py.warnings"` logger:

在程序部署到生产环境后，警告不应该导致错误，因为它们可能在关键时刻导致程序崩溃。相反，更好的方法是将警告复制到 `logging` 内置模块中。在这里，我通过调用 `logging.captureWarnings` 函数并配置相应的 `"py.warnings"` logger 来实现这一点：

```
import logging

fake_stderr = io.StringIO()
handler = logging.StreamHandler(fake_stderr)
formatter = logging.Formatter("%(asctime)-15s WARNING] %(message)s")
handler.setFormatter(formatter)

logging.captureWarnings(True)
logger = logging.getLogger("py.warnings")
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

warnings.resetwarnings()
warnings.simplefilter("default")
warnings.warn("This will go to the logs output")

print(fake_stderr.getvalue())

warnings.resetwarnings()

>>>
2019-06-11 19:48:19,132 WARNING] .../example.py:2
This will go to the logs output
 warnings.warn("This will go to the logs output"
```

Using logging to capture warnings ensures that any error reporting systems that my program already has in place will also receive notice of important warnings in production. This can be especially useful if my tests don’t cover every edge case that I might see when the program is undergoing real usage.

使用 logging 来捕获警告确保了我程序中已经存在的任何错误报告系统也会接收到生产环境中重要的警告。如果我的测试没有覆盖到在程序实际使用中可能遇到的每一个边缘情况，这尤其有用。

API library maintainers should also write unit tests to verify that warnings are generated under the correct circumstances with clear and actionable messages (see Item 108: “Verify Related Behaviors in `TestCase` Subclasses”). Here, I use the `warnings.catch_warnings` function as a context manager (see Item 82: “Consider `contextlib` and `with` Statements for Reusable `try` / `finally` Behavior” for background) to wrap a call to the `require` function that I defined above:

API 库的维护者还应编写单元测试，以验证在正确的情况下生成具有清晰且可操作性消息的警告（参见 Item 108：“在 `TestCase` 子类中验证相关行为”）。在这里，我使用 `warnings.catch_warnings` 函数作为一个上下文管理器（参见 Item 82：“考虑 `contextlib` 和 `with` 语句用于可重用的 `try` / `finally` 行为”了解背景信息）来包裹对上面定义的 `require` 函数的调用：

```
with warnings.catch_warnings(record=True) as found_warnings:
    found = require("my_arg", None, "fake units")
    expected = "fake units"
    assert found == expected
```

Once I’ve collected the warning messages, I can verify that their number, detail messages, and categories match my expectations:

在我收集了警告消息之后，我可以验证它们的数量、详细消息和类别是否符合我的预期：

```
assert len(found_warnings) == 1
single_warning = found_warnings[0]
assert str(single_warning.message) == (
    "my_arg will be required soon, update your code"
)
assert single_warning.category == DeprecationWarning
```

**Things to Remember**
- The `warnings` module can be used to notify callers of your API about deprecated usage. Warning messages encourage such callers to fix their code before later changes break their programs.
- Raise warnings as errors by using the `-W error` command-line argument to the Python interpreter. This is especially useful in automated tests to catch potential regressions of dependencies.
- In production, you can replicate warnings into the `logging` module to ensure that your existing error reporting systems will capture warnings at runtime.
- It’s useful to write tests for the warnings that your code generates to make sure that they’ll be triggered at the right time in any of your downstream dependencies.

**注意事项**
- `warnings` 模块可用于通知 API 的调用者有关已弃用的用法。警告消息鼓励这些调用者在后续更改破坏其程序之前修复其代码。
- 通过使用 `-W error` 命令行参数将警告作为错误提出解释器。这在自动化测试中特别有用，可以捕捉依赖项的潜在回归问题。
- 在生产环境中，您可以将警告复制到 `logging` 模块中，以确保您的现有错误报告系统将在运行时捕获警告。
- 编写代码生成的警告测试很有用，以确保它们会在任何下游依赖关系的正确时机被触发。

