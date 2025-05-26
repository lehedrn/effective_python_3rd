# Chapter 13: Testing and Debugging (测试与调试)

## Item 112: Encapsulate Dependencies to Facilitate Mocking and Testing (封装依赖以方便模拟和测试)

In the previous item (see Item 111: “Use Mocks to Test Code with Complex Dependencies”, I showed how to use the facilities of the `unittest.mock` built-in module—including the `Mock` class and `patch` family of functions—to write tests that have complex dependencies, such as a database. However, the resulting test code requires a lot of boilerplate, which could make it more difficult for new readers of the code to understand what the tests are trying to verify.

在上一条目中（见条目 111：“使用Mock来测试具有复杂依赖的代码”），我展示了如何使用`unittest.mock`内置模块的功能——包括`Mock`类和`patch`函数族——编写具有复杂依赖（如数据库）的测试。然而，生成的测试代码需要大量的样板代码，这可能会使新读者更难理解测试试图验证的内容。

One way to improve these tests is to use a wrapper object to encapsulate the database’s interface instead of passing a `DatabaseConnection` object to functions as an argument. It’s often worth refactoring your code (see Item 123: “Consider `warnings` to Refactor and Migrate Usage” for one approach) to use better abstractions because it facilitates creating mocks and writing tests. Here, I redefine the various database helper functions from the previous item as methods on a class instead of as independent functions:

改进这些测试的一种方法是使用包装对象来封装数据库接口，而不是将`DatabaseConnection`对象作为参数传递给函数。通常值得对代码进行重构（参见条目 123：“考虑使用`warnings`来重构和迁移用法”了解一种方法），以更好的抽象方式使用，因为它有助于创建模拟并编写测试。在这里，我重新定义了前一条目中的各种数据库辅助函数，并将其作为方法定义在类中：

```
class ZooDatabase:

    def get_animals(self, species):
        pass

    def get_food_period(self, species):
        pass

    def feed_animal(self, name, when):
        pass
```

Now, I can redefine the `do_rounds` function to call methods on a `ZooDatabase` object:

现在，我可以重新定义`do_rounds`函数以调用`ZooDatabase`对象上的方法：

```
from datetime import datetime

def do_rounds(database, species, *, now_func=datetime.now):
    now = now_func()
    feeding_timedelta = database.get_food_period(species)
    animals = database.get_animals(species)
    fed = 0

    for name, last_mealtime in animals:
        if (now - last_mealtime) >= feeding_timedelta:
            database.feed_animal(name, now)
            fed += 1

    return fed
```

Writing a test for `do_rounds` is now a lot easier because I no longer need to use `unittest.mock.patch` to inject the mock into the code being tested. Instead, I can create a `Mock` instance to represent a `ZooDatabase` and pass that in as the `database` parameter. The `Mock` class returns a mock object for any attribute name that is accessed. Those attributes can be called like methods, which I can then use to set expectations and verify calls. This makes it easy to mock out all of the methods of a class:

现在编写`do_rounds`的测试要容易得多，因为我不再需要使用`unittest.mock.patch`将mock注入被测代码中。相反，我可以创建一个代表`ZooDatabase`的`Mock`实例并将其作为`database`参数传入。`Mock`类为访问的任何属性名称返回一个mock对象。这些属性可以像方法一样被调用，我可以使用它们来设置预期并验证调用。这使得很容易mock出类的所有方法：

```
from unittest.mock import Mock

database = Mock(spec=ZooDatabase)
print(database.feed_animal)
database.feed_animal()
database.feed_animal.assert_any_call()

>>>
<Mock name='mock.feed_animal' id='4386901024'>
```

I can rewrite the `Mock` setup code using the `ZooDatabase` encapsulation:

我可以使用`ZooDatabase`封装重写`Mock`的设置代码：

```
from datetime import timedelta
from unittest.mock import call

now_func = Mock(spec=datetime.now)
now_func.return_value = datetime(2019, 6, 5, 15, 45)

database = Mock(spec=ZooDatabase)
database.get_food_period.return_value = timedelta(hours=3)
database.get_animals.return_value = [
    ("Spot", datetime(2019, 6, 5, 11, 15)),
    ("Fluffy", datetime(2019, 6, 5, 12, 30)),
    ("Jojo", datetime(2019, 6, 5, 12, 55)),
]
```

Then I can run the function being tested and verify that all dependent methods were called as expected:

然后我可以运行被测函数并验证所有依赖方法是否按预期调用：

```
result = do_rounds(database, "Meerkat", now_func=now_func)
assert result == 2

database.get_food_period.assert_called_once_with("Meerkat")
database.get_animals.assert_called_once_with("Meerkat")
database.feed_animal.assert_has_calls(
    [
        call("Spot", now_func.return_value),
        call("Fluffy", now_func.return_value),
    ],
    any_order=True,
)
```

Using the `spec` parameter to `Mock` is especially useful when mocking classes because it ensures that the code under test doesn’t call a misspelled method name by accident. This allows you to avoid a common pitfall where the same bug is present in both the code and the unit test, masking a real error that will later reveal itself in production:

在模拟类时使用`Mock`的`spec`参数特别有用，因为它确保被测代码不会意外调用拼写错误的方法名。这可以帮助避免常见的陷阱，即代码和单元测试中都存在相同的bug，从而掩盖了将在生产环境中暴露的真实错误：

```
database.bad_method_name()

>>>
Traceback ...
AttributeError: Mock object has no attribute 'bad_method_name'
```

If I want to test this program end-to-end with a mid-level integration test (see Item 109: “Prefer Integration Tests Over Unit Tests”), I still need a way to inject a mock `ZooDatabase` into the program. I can do this by creating a helper function that acts as a seam for dependency injection. Here, I define such a helper function that caches a `ZooDatabase` in module scope by using a `global` statement (see Item 120: “Consider Module-Scoped Code to Configure Deployment Environments” for background):

如果我想通过中等规模的集成测试来端到端地测试这个程序（见条目 109：“优先选择集成测试而非单元测试”），我仍然需要一种方式将mock的`ZooDatabase`注入程序中。为此，我可以创建一个作为依赖注入缝的辅助函数。这里，我定义了一个这样的辅助函数，该函数通过使用`global`语句（参见条目 120：“考虑在模块范围内编写代码以配置部署环境”）在模块作用域中缓存`ZooDatabase`：

```
DATABASE = None

def get_database():
    global DATABASE
    if DATABASE is None:
        DATABASE = ZooDatabase()
    return DATABASE

def main(argv):
    database = get_database()
    species = argv[1]
    count = do_rounds(database, species)
    print(f"Fed {count} {species}(s)")
    return 0
```

Now, I can inject the mock `ZooDatabase` using `patch` , run the test, and verify the program’s output. I’m not using a mock `datetime.now` here; instead, I’m relying on the database records returned by the mock to be relative to the current time in order to produce similar behavior to the unit test. This approach is more flaky than mocking everything, but it also tests more surface area:

现在，我可以使用`patch`注入mock的`ZooDatabase`，运行测试并验证程序的输出。这里我没有使用mock的`datetime.now`；而是依赖于mock返回的数据库记录相对于当前时间产生类似单元测试的行为。这种方法虽然比完全mock一切更容易出错，但它也测试了更多的功能面：

```
import contextlib
import io
from unittest.mock import patch

with patch("__main__.DATABASE", spec=ZooDatabase):
    now = datetime.now()

    DATABASE.get_food_period.return_value = timedelta(hours=3)
    DATABASE.get_animals.return_value = [
        ("Spot", now - timedelta(minutes=4.5)),
        ("Fluffy", now - timedelta(hours=3.25)),
        ("Jojo", now - timedelta(hours=3)),
    ]

    fake_stdout = io.StringIO()
    with contextlib.redirect_stdout(fake_stdout):
        main(["program name", "Meerkat"])

    found = fake_stdout.getvalue()
    expected = "Fed 2 Meerkat(s)\n"

    assert found == expected
```

The results match my expectations. Creating this integration test was straightforward because I designed the implementation to make it easier to test.

结果符合我的预期。创建这个集成测试非常直接，因为我在设计实现时就考虑到了测试的便利性。

**Things to Remember**

- When unit tests require a lot of repeated boilerplate to set up mocks, one solution may be to encapsulate the functionality of dependencies into classes that are more easily mocked.
- The `Mock` class of the `unittest.mock` built-in module simulates classes by returning a new mock, which can act as a mock method, for each attribute that is accessed.
- For end-to-end tests, it’s valuable to refactor your code to have more helper functions that can act as explicit seams to use for injecting mock dependencies in tests.

**注意事项**

- 当单元测试需要大量重复的样板代码来设置mock时，可能的解决方案之一是将依赖项的功能封装到类中，以便更容易进行mock。
- `unittest.mock`内置模块的`Mock`类通过为每个访问的属性返回一个新的mock对象来模拟类，这个mock对象可以作为mock方法使用。
- 对于端到端测试，重构代码以拥有更多可以作为显式缝合点的辅助函数是非常有价值的，这样可以在测试中注入mock依赖。