# Chapter 13: Testing and Debugging (测试与调试)

## Item 111: Use Mocks to Test Code with Complex Dependencies (使用 Mock 测试具有复杂依赖的代码)

Another common need when writing tests (see Item 108: “Verify Related Behaviors in `TestCase` Subclasses”) is to use mocked functions and classes to simulate behaviors when it’s too difficult or slow to use the real thing. For example, say that I need a program to maintain the feeding schedule for animals at the zoo. Here, I define a function to query a database for all of the animals of a certain species, and then return when they most recently ate:

编写测试时（参见条目 108：“在 `TestCase` 子类中验证相关行为”）另一个常见的需求是使用模拟函数和类来模拟行为，当使用真实对象过于困难或缓慢时。例如，我需要一个程序来维护动物园里动物的喂食时间表。这里，我定义了一个函数来查询数据库中的特定物种动物，然后返回它们最近一次进食的时间：

```
class DatabaseConnection:
    def __init__(self, host, port):
        pass
class DatabaseConnectionError(Exception):
    pass
def get_animals(database, species):
    # Query the Database
    raise DatabaseConnectionError("Not connected")
    # Return a list of (name, last_mealtime) tuples
```

How do I get a `DatabaseConnection` instance to use for testing this function? Here, I try to create one and pass it into the function being tested:


如何获得一个用于测试此函数的 `DatabaseConnection` 实例？在这里，我尝试创建一个并将其传递给正在测试的函数：

```
database = DatabaseConnection("localhost", "4444")
get_animals(database, "Meerkat")

>>>
Traceback ...
DatabaseConnectionError: Not connected
```

There’s no database running, so of course this fails. One solution is to actually stand up a database server and connect to it in the test. However, it’s a lot of work to fully automate starting up a database, configuring its schema, populating it with data, and so on in order to just run a simple unit test. Further, it will probably take a lot of wall-clock time to set up a database server, which would slow down these unit tests and make them harder to maintain (see Item 110: “Isolate Tests From Each Other with `setUp` , `tearDown` , `setUpModule` , and `tearDownModule` ” for one potential solution).

当然，由于没有运行数据库，这会失败。一种解决方案是实际启动一个数据库服务器，并在测试中连接它。然而，为了仅仅运行一个简单的单元测试而完全自动化地启动数据库、配置其模式、填充数据等是一项相当大的工作。此外，设置数据库服务器可能需要很多墙钟时间，这会减慢这些单元测试的速度并使它们更难维护（有关潜在解决方案，请参见条目 110：“使用 `setUp`、`tearDown`、`setUpModule` 和 `tearDownModule` 将测试彼此隔离”）。

An alternative approach is to mock out the database. A mock lets you provide expected responses for dependent functions, given a set of expected calls. It’s important not to confuse mocks with fakes. A fake would provide most of the behavior of the `DatabaseConnection` class, but with a simpler implementation, such as a basic in-memory, single-threaded database with no persistence.

另一种方法是模拟数据库。mock 让您可以为依赖函数提供预期响应，给定一组预期调用。重要的是不要将 mock 与假货混淆。假货将提供 `DatabaseConnection` 类的大部分行为，但使用更简单的实现，例如一个基本的内存中、单线程数据库，无持久性。

Python has the `unittest.mock` built-in module for creating mocks and using them in tests. Here, I define a `Mock` instance that simulates the `get_animals` function without actually connecting to the database:

Python 有内置模块 `unittest.mock` 用于创建 mock 并在测试中使用它们。在这里，我定义了一个 `Mock` 实例，该实例模拟了 `get_animals` 函数而不实际连接到数据库：

```
from datetime import datetime
from unittest.mock import Mock

mock = Mock(spec=get_animals)
expected = [
    ("Spot", datetime(2024, 6, 5, 11, 15)),
    ("Fluffy", datetime(2024, 6, 5, 12, 30)),
    ("Jojo", datetime(2024, 6, 5, 12, 45)),
]
mock.return_value = expected
```

The `Mock` class creates a mock function. The `return_value` attribute of the mock is the value to return when it is called. The `spec` argument indicates that the mock should act like the given object, which is a function in this case, and error if it’s used in the wrong way. For example, here I try to treat the mock function as if it were a mock object with attributes:

`Mock` 类创建一个 mock 函数。mock 的 `return_value` 属性是在被调用时返回的值。`spec` 参数表示 mock 应该像给定的对象一样行为，在本例中是一个函数，并且如果以错误的方式使用它则报错。例如，这里我尝试将 mock 函数视为具有属性的 mock 对象：

```
mock.does_not_exist
>>>
Traceback ...
AttributeError: Mock object has no attribute 'does_not_exist'
```

Once it’s created, I can call the mock, get its return value, and verify that what it returns matches expectations. I use a unique `object()` value as the `database` argument because it won’t actually be used by the mock to do anything; all I care about is that the `database` parameter was correctly plumbed through to any dependent functions that needed a `DatabaseConnection` instance in order to work:

一旦创建，我可以调用这个 mock，获取它的返回值，并验证它返回的内容是否符合预期。我使用一个唯一的 `object()` 值作为 `database` 参数，因为它实际上不会被 mock 使用来做任何事情；我关心的只是 `database` 参数是否正确地传递到了需要 `DatabaseConnection` 实例才能工作的任何依赖函数中：

```
database = object()
result = mock(database, "Meerkat")
assert result == expected
```

This verifies that the mock responded correctly, but how do I know if the code that called the mock provided the correct arguments? For this, the `Mock` class provides the `assert_called_once_with` method, which verifies that a single call with exactly the given parameters was made:

这验证了 `mock` 正确响应，但是如何知道调用 `mock` 的代码提供的参数是否正确呢？为此，`Mock` 类提供了 `assert_called_once_with` 方法，该方法验证确实进行了恰好给定参数的单次调用：

```
mock.assert_called_once_with(database, "Meerkat")
```

If I supply the wrong parameters, an exception is raised, and any `TestCase` that the assertion is used in fails:

如果我提供了错误的参数，则会引发异常，并且使用该断言的任何 `TestCase` 都会失败：

```
mock.assert_called_once_with(database, "Giraffe")
>>>
Traceback ...
AssertionError: expected call not found.
Expected: mock(<object object at 0x000002D0660A0D00>, 'Giraffe')
  Actual: mock(<object object at 0x000002D0660A0D00>, 'Meerkat')
```

If I actually don’t care about some of the individual parameters, such as exactly which `database` object was used, then I can indicate that any value is okay for an argument by using the `unittest.mock.ANY` constant. I can also use the `assert_called_with` method of `Mock` to verify that the most recent call to the mock—and there may have been multiple calls in this case—matches my expectations:

如果我真的不关心某些参数，比如确切使用了哪个 `database` 对象，则可以使用 `unittest.mock.ANY` 常量指示该参数接受任何值。还可以使用 `Mock` 的 `assert_called_with` 方法验证 mock 最近的一次调用（在这种情况下可能有多次调用）是否符合我的期望：

```
from unittest.mock import ANY
mock = Mock(spec=get_animals)
mock("database 1", "Rabbit")
mock("database 2", "Bison")
mock("database 3", "Meerkat")
mock.assert_called_with(ANY, "Meerkat")
```

`ANY` is useful in tests when a parameter is not core to the behavior that’s being tested. It’s often worth erring on the side of under-specifying tests by using `ANY` more liberally instead of over-specifying tests and having to plumb through various test parameter expectations.

当参数不是正在测试的行为的核心时，`ANY` 在测试中非常有用。通常值得通过更广泛地使用 `ANY` 来偏向于过度简化测试而不是过度指定测试并不得不处理各种测试参数期望。

The Mock class also makes it easy to mock exceptions being raised:

`Mock` 类还使得模拟异常变得容易：

```
class MyError(Exception):
    pass

mock = Mock(spec=get_animals)
mock.side_effect = MyError("Whoops! Big problem")
result = mock(database, "Meerkat")

>>>
Traceback ...
MyError: Whoops! Big problem
```

There are many more features available, so be sure to see the module documentation for the full range of options (https://docs.python.org/3/library/unittest.mock.html).
还有许多其他功能可用，所以一定要查看模块文档以了解完整的选项范围（`https://docs.python.org/3/library/unittest.mock.html`）。

Now that I’ve shown the mechanics of how a `Mock` works, I can apply it to an actual testing situation to show how to use it effectively in writing tests. Here, I define a function to do the rounds of feeding animals at the zoo, given a set of database-interacting functions:

现在我已经展示了 `Mock` 是如何工作的机制，我可以将其应用到实际的测试情况中，以展示如何有效地编写测试。在这里，我定义了一个函数来巡视喂养动物园里的动物，给定一组与数据库交互的函数：

```
def get_food_period(database, species):
    # Query the Database
    pass
    # Return a time delta

def feed_animal(database, name, when):
    # Write to the Database
    pass

def do_rounds(database, species):
    now = datetime.now()
    feeding_timedelta = get_food_period(database, species)
    animals = get_animals(database, species)
    fed = 0

    for name, last_mealtime in animals:
        if (now - last_mealtime) > feeding_timedelta:
            feed_animal(database, name, now)
            fed += 1

    return fed
```

The goal of my test is to verify that the when `do_rounds` is run, the right animals got fed, that the latest feeding time was recorded to the database, and that the total number of animals fed returned by the function matches the correct total.

我的测试目标是验证运行 `do_rounds` 时，正确的动物得到了喂养，最新的喂养时间记录到了数据库，并且由函数返回的已喂养动物总数与正确总数匹配。

In order to do all this, I need to mock out `datetime.now` so my tests can expect a stable time that isn’t affected by when the program is executed. I need to mock out `get_food_period` and `get_animals` to return values that would have come from the database. And I need to mock out `feed_animal` to accept data that would have been written back to the database.

为了做到这一切，我需要模拟 `datetime.now` 以便我的测试可以期待一个稳定的时间，不受程序执行时间的影响。我需要模拟 `get_food_period` 和 `get_animals` 以返回原本来自数据库的值。我还需要模拟 `feed_animal` 以接受本来写回数据库的数据。

The question is: Even if I know how to create these mock functions and set expectations, how do I get the `do_rounds` function that’s being tested to use the mock dependent functions instead of the real versions? One approach is to inject everything as keyword only arguments (see Item 37: “Enforce Clarity with Keyword-Only and Positional-Only Arguments” for background):

问题是：即使我知道如何创建这些模拟函数并设定期望，如何让正在测试的 `do_rounds` 函数使用这些模拟的依赖函数而不是真实的版本？一种方法是将所有内容作为仅限关键字参数注入（有关背景，请参见条目 37：“使用仅限关键字和仅限位置参数增强清晰度”）：

```
def do_rounds(
    database,
    species,
    *,
    now_func=datetime.now,
    food_func=get_food_period,
    animals_func=get_animals,
    feed_func=feed_animal
):
    now = now_func()
    feeding_timedelta = food_func(database, species)
    animals = animals_func(database, species)
    fed = 0

    for name, last_mealtime in animals:
        if (now - last_mealtime) > feeding_timedelta:
            feed_func(database, name, now)
            fed += 1

    return fed
```

To test this function, I need to create all of the `Mock` instances upfront and set their expectations:

要测试此函数，我需要预先创建所有 `Mock` 实例并设定它们的期望：

```
from datetime import timedelta

now_func = Mock(spec=datetime.now)
now_func.return_value = datetime(2024, 6, 5, 15, 45)

food_func = Mock(spec=get_food_period)
food_func.return_value = timedelta(hours=3)

animals_func = Mock(spec=get_animals)
animals_func.return_value = [
    ("Spot", datetime(2024, 6, 5, 11, 15)),
    ("Fluffy", datetime(2024, 6, 5, 12, 30)),
    ("Jojo", datetime(2024, 6, 5, 12, 45)),
]

feed_func = Mock(spec=feed_animal)
```

Then, I can run the test by passing the mocks into the `do_rounds` function to override the defaults:

然后，我可以通过将 mocks 传递到 `do_rounds` 函数中覆盖默认值来运行测试：

```
result = do_rounds(
    database,
    "Meerkat",
    now_func=now_func,
    food_func=food_func,
    animals_func=animals_func,
    feed_func=feed_func,
)

assert result == 2
```

Finally, I can verify that all of the calls to dependent functions matched my expectations:

最后，我可以验证对依赖函数的所有调用是否符合我的期望：

```
from unittest.mock import call

food_func.assert_called_once_with(database, "Meerkat")

animals_func.assert_called_once_with(database, "Meerkat")

feed_func.assert_has_calls(
    [
        call(database, "Spot", now_func.return_value),
        call(database, "Fluffy", now_func.return_value),
    ],
    any_order=True,
)
```

I don’t verify the parameters to the `datetime.now` mock or how many times it was called because that’s indirectly verified by the return value of the function. For `get_food_period` and `get_animals` , I verify a single call with the specified parameters by using `assert_called_once_with` . For the `feed_animal` function, I verify that two calls were made——and their order didn’t matter——to write to the database using the `unittest.mock.call` helper and the `assert_has_calls` method.

我不验证对 `datetime.now` 模拟的参数或调用次数，因为这是通过函数的返回值间接验证的。对于 `get_food_period` 和 `get_animals`，我通过使用 `assert_called_once_with` 验证了一次带有指定参数的调用。对于 `feed_animal` 函数，我验证了两次调用——顺序无关紧要——使用 `unittest.mock.call` 辅助工具和 `assert_has_calls` 方法写入数据库。

This approach of using keyword-only arguments for injecting mocks works, but it’s quite verbose and requires changing every function you want to test. The `unittest.mock.patch` family of functions makes injecting mocks easier. It temporarily reassigns an attribute of a module or class, such as the database-accessing functions that I defined above. For example, here I override `get_animals` to be a mock using `patch` :

这种使用仅限关键字参数注入 mocks 的方法有效，但它非常冗长并且需要更改每个想要测试的函数。`unittest.mock.patch` 系列函数使得注入 mocks 更加简便。它临时重新分配模块或类的一个属性，例如上面定义的数据库访问函数。例如，这里我使用 `patch` 覆盖 `get_animals` 为一个 mock：

```
from unittest.mock import patch

print("Outside patch:", get_animals)

with patch("__main__.get_animals"):
    print("Inside patch: ", get_animals)

print("Outside again:", get_animals)

>>>
Outside patch: <function get_animals at 0x000002D066827880>
Inside patch:  <MagicMock name='get_animals' id='3094130020368'>
Outside again: <function get_animals at 0x000002D066827880>
```

`patch` works for many modules, classes, and attributes. It can be used in `with` statements (see Item 82: “Consider `contextlib` and `with` Statements for Reusable `try` / `finally` Behavior”), as a function decorator (see Item 38: “Define Function Decorators with `functools.wraps` ”), or in the `setUp` and `tearDown` methods of `TestCase` classes (see Item 110: “Isolate Tests From Each Other with `setUp` , `tearDown` , `setUpModule` , and `tearDownModule` ”).

`patch` 可用于许多模块、类和属性。它可以用于 `with` 语句中（参见条目 82：“考虑 `contextlib` 和 `with` 语句以重用 `try` / `finally` 行为”），作为函数装饰器（参见条目 38：“使用 `functools.wraps` 定义函数装饰器”）或在 `TestCase` 类的 `setUp` 和 `tearDown` 方法中（参见条目 110：“使用 `setUp`、`tearDown`、`setUpModule` 和 `tearDownModule` 将测试彼此隔离”）。

However, `patch` doesn’t work in all cases. For example, to test `do_rounds` I need to mock out the current time returned by the `datetime.now` class method. Python won’t let me do that because the `datetime` class is defined in a C-extension module, which can’t be modified in this way:

然而，`patch` 并非适用于所有情况。例如，要测试 `do_rounds` 我需要模拟由 `datetime.now` 类方法返回的当前时间。Python 不允许我这样做，因为 `datetime` 类是在 C 扩展模块中定义的，无法以这种方式修改：

```
fake_now = datetime(2024, 6, 5, 15, 45)
with patch("datetime.datetime.now"):
    datetime.now.return_value = fake_now

>>>
Traceback ...
TypeError: cannot set 'now' attribute of immutable type 'datetime.datetime'
During handling of the above exception, another exception occurred:
Traceback ...
TypeError: cannot set 'now' attribute of immutable type 'datetime.datetime'
```

To work around this, I can either create another helper function to fetch time that can be patched:

解决此问题的方法之一是创建另一个可打补丁的获取时间的帮助函数：

```
def get_do_rounds_time():
    return datetime.now()

def do_rounds(database, species):
    now = get_do_rounds_time()

with patch("__main__.get_do_rounds_time"):
    pass
```

Alternatively, I can use a keyword-only argument for the `datetime.now` mock and use `patch` for all of the other mocks:

或者，我可以为 `datetime.now` 模拟使用一个仅限关键字的参数，并为所有其他模拟使用 `patch`：

```
def do_rounds(database, species, *, now_func=datetime.now):
    now = now_func()
    feeding_timedelta = get_food_period(database, species)
    animals = get_animals(database, species)
    fed = 0

    for name, last_mealtime in animals:
        if (now - last_mealtime) > feeding_timedelta:
            feed_animal(database, name, now)
            fed += 1

    return fed
```

I’m going to go with the latter approach. Now, I can use the `patch.multiple` function to create many mocks, and then set their expectations:

我将采用后一种方法。现在，我可以使用 `patch.multiple` 函数创建多个 mocks，然后设置它们的期望：

```
from unittest.mock import DEFAULT

with patch.multiple(
    "__main__",
    autospec=True,
    get_food_period=DEFAULT,
    get_animals=DEFAULT,
    feed_animal=DEFAULT,
):
    now_func = Mock(spec=datetime.now)
    now_func.return_value = datetime(2024, 6, 5, 15, 45)
    get_food_period.return_value = timedelta(hours=3)
    get_animals.return_value = [
        ("Spot", datetime(2024, 6, 5, 11, 15)),
        ("Fluffy", datetime(2024, 6, 5, 12, 30)),
        ("Jojo", datetime(2024, 6, 5, 12, 45)),
    ]
```

The keyword arguments to `patch.multiple` correspond to names in the `__main__` module that I want to override during the test. The `DEFAULT` value indicates that I want a standard `Mock` instance to be created for each name. All of the generated mocks will adhere to the specification of the objects they are meant to simulate, thanks to the `autospec=True` parameter.

`patch.multiple` 的关键字参数对应于我想要在测试期间覆盖的 `__main__` 模块中的名称。`DEFAULT` 值表示我希望为每个名称创建一个标准的 `Mock` 实例。由于 `autospec=True` 参数，所有生成的 mocks 都将遵循它们应该模拟的对象的规范。

With the setup ready, I can run the test and verify that the calls were correct inside the `with` statement that used `patch.multiple` :

准备就绪后，我可以在使用 `patch.multiple` 的 `with` 语句内运行测试并验证调用是否正确：

```
    result = do_rounds(database, "Meerkat", now_func=now_func)
    assert result == 2

    get_food_period.assert_called_once_with(database, "Meerkat")
    get_animals.assert_called_once_with(database, "Meerkat")
    feed_animal.assert_has_calls(
        [
            call(database, "Spot", now_func.return_value),
            call(database, "Fluffy", now_func.return_value),
        ],
        any_order=True,
    )
```

These mocks work as expected, but it’s important to realize that it’s possible to further improve the readability of these tests and reduce boilerplate by refactoring your code to be more testable by design (see Item 112: “Encapsulate Dependencies to Facilitate Mocking and Testing”).

这些 mocks 如预期般工作，但重要的是要意识到可以通过重构代码使其更具可测试性从而进一步提高这些测试的可读性并减少样板代码（参见条目 112：“封装依赖项以方便 mocking 和测试”）。

**Things to Remember**
- The `unittest.mock` module provides a way to simulate the behavior of interfaces using the `Mock` class. Mocks are useful in tests when it’s difficult to set up the dependencies that are required by the code that’s being tested.
- When using mocks, it’s important to verify both the behavior of the code being tested and how dependent functions were called by that code, using the `Mock.assert_called_once_with` family of methods.
- Keyword-only arguments and the `unittest.mock.patch` family of functions can be used to inject mocks into the code being tested.

**注意事项**
- `unittest.mock` 模块提供了一种使用 `Mock` 类模拟接口行为的方法。当很难设置被测代码所需的依赖时，mocks 在测试中非常有用。
- 使用 mocks 时，重要的是验证被测代码的行为以及依赖函数是如何被调用的，使用 `Mock.assert_called_once_with` 系列方法。 
- 可以使用仅限关键字参数和 `unittest.mock.patch` 系列函数将 mocks 注入被测代码中。