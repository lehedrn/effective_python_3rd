# Chapter 13: Testing and Debugging (测试与调试)

## Item 109: Prefer Integration Tests over Unit Tests (优先使用集成测试而非单元测试)

There are many approaches to software testing that are far broader than Python, including test-driven development, property-based testing, mutation testing, code and branch coverage reporting, etc. You will find great tools for writing every type and style of automated test imaginable in Python’s built-in and community packages (see Item 116: “Know Where to Find Community-Built Modules”). So the question in Python isn’t whether you can and should write tests, but instead: how much testing is enough and what exactly should your tests verify?

软件测试有许多方法，这些方法远远超出了Python的范畴，包括测试驱动开发、基于属性的测试、变异测试、代码和分支覆盖率报告等。你会发现，在Python的内置和社区包中，有很棒的工具可以编写各种类型和风格的自动化测试（参见条目116：“知道在哪里找到社区构建的模块”）。因此在Python中的问题不是你能否以及是否应该编写测试，而是：足够的测试是什么样的，你的测试究竟应该验证什么？

It’s best to think of tests in Python as an insurance policy on your code. Good tests give you confidence that your code is correct. If you refactor or expand your code, tests that verify behavior—not implementation—make it easy to identify what’s changed. It sounds counter-intuitive, but having well-built tests actually makes it easier to modify Python code, not harder.

最好将Python中的测试视为对你的代码的一种保险策略。好的测试能让你确信你的代码是正确的。如果你重构或扩展代码，那些验证行为而不是实现的测试使得识别变化变得容易。听起来可能有些违反直觉，但拥有良好的测试实际上会使修改Python代码变得更加容易，而不是更难。

As in other languages, testing can exercise many different levels of a codebase. Unit tests verify focused pieces of a much larger system. They are useful when you have a lot of edge cases and you need to ensure that everything is handled properly. They are fast to run because they only use a small part of the program. Often they’re built using mocks (see Item 111: “Use Mocks to Test Code with Complex Dependencies”).

与其他语言一样，测试可以在代码库的多个不同层次上进行。单元测试验证的是更大系统中的小部分。当你有很多边界情况并且需要确保一切都处理得当时，它们非常有用。它们运行速度快，因为只使用了程序的一小部分。通常它们使用mock来构建（参见条目111：“使用Mock来测试具有复杂依赖关系的代码”）。

Integration tests verify that multiple components work together. They’re often slower to run and harder to write (see Item 110: “Isolate Tests From Each Other with `setUp` , `tearDown` , `setUpModule` , and `tearDownModule` ” for an example). However, integration tests are especially important in Python because you have no guarantee that your subsystems will actually interoperate unless you prove it (see Item 3: “Never Expect Python to Detect Errors at Compile Time”). Statically typed languages can use type information to approximate rough fitting of components, but doing so in dynamic languages can be more difficult (see Item 124: “Consider Static Analysis via `typing` to Obviate Bugs”) or impractical.

集成测试验证多个组件是否能够一起工作。它们通常运行较慢且难以编写（参见条目110：“使用`setUp`、`tearDown`、`setUpModule`和`tearDownModule`隔离测试以避免相互影响”）。然而，集成测试在Python中尤其重要，因为你无法保证你的子系统确实能够互操作，除非你证明它（参见条目3：“永远不要期望Python在编译时检测错误”）。静态类型的语言可以使用类型信息来近似组件的大致适配性，但在动态语言中这样做可能更加困难（参见条目124：“考虑通过`typing`进行静态分析以避免错误”）或者不切实际。

Generally in Python it’s best to write integration tests. But if you notice that some parts of your code also have a lot of boundary conditions to explore, then it might be worth writing unit tests for those behaviors as well. What you don’t want to do is only write unit tests. For example, imagine that I’m building embedded software to control a toaster. Here, I define a toaster class that lets me set the "doneness" level, push down the bread, or pop up the toast:

通常在Python中最好编写集成测试。但是如果你注意到代码的某些部分也有很多边界条件需要探索，那么为这些行为编写单元测试可能是值得的。你不应该做的就是仅编写单元测试。例如，想象一下我在构建用于控制烤面包机的嵌入式软件。在这里，我定义了一个烤面包机类，让我设置“烘烤程度”级别，按下面包，或者弹出烤面包：

```
class Toaster:
    def __init__(self, timer):
        self.timer = timer
        self.doneness = 3
        self.hot = False

    def _get_duration(self):
        return max(0.1, min(120, self.doneness * 10))

    def push_down(self):
        if self.hot:
            return

        self.hot = True
        self.timer.countdown(self._get_duration(), self.pop_up)

    def pop_up(self):
        print("Pop!")  # Release the spring
        self.hot = False
        self.timer.end()
```

The `Toaster` class relies on a timer that ejects the toast when it’s done. It should be possible to reset the timer any number of times. Here, I use the `Timer` class from the `threading` built-in module to implement this:

`Toaster`类依赖于一个计时器，在烤好后弹出烤面包。它应该可以随时重置计时器。在这里，我使用`threading`内置模块中的`Timer`类来实现这一点：

```
import threading

class ReusableTimer:
    def __init__(self):
        self.timer = None

    def countdown(self, duration, callback):
        self.end()
        self.timer = threading.Timer(duration, callback)
        self.timer.start()

    def end(self):
        if self.timer:
            self.timer.cancel()
```

With these two classes defined, I can easily exercise the toaster’s functionality to show that it can apply heat to bread and pop it up before burning it:

有了这两个类的定义，我可以轻松地测试烤面包机的功能，以展示它可以给面包加热并在烧焦之前弹出：

```
toaster = Toaster(ReusableTimer())
print("Initially hot:  ", toaster.hot)
toaster.doneness = 5
toaster.doneness = 0
toaster.push_down()
print("After push down:", toaster.hot)
# Time passes
toaster.timer.timer.join()
print("After time:     ", toaster.hot)

>>>
Initially hot: False
After push down: True
Pop!
After time: False
```

If I wanted to write a unit test for the `Toaster` class, I might do something like this with the built-in `unittest` module (see Item 108: “Verify Related Behaviors in `TestCase` Subclasses”), where I mock out the `ReusableTimer` class entirely:

如果我想为`Toaster`类编写一个单元测试，可能会像这样使用内置的`unittest`模块（参见条目108：“在`TestCase`子类中验证相关行为”），其中完全模拟出`ReusableTimer`类：

```
from unittest import TestCase
from unittest.mock import Mock

class ToasterUnitTest(TestCase):

    def test_start(self):
        timer = Mock(spec=ReusableTimer)
        toaster = Toaster(timer)
        toaster.push_down()
        self.assertTrue(toaster.hot)
        timer.countdown.assert_called_once_with(30, toaster.pop_up)

    def test_end(self):
        timer = Mock(spec=ReusableTimer)
        toaster = Toaster(timer)
        toaster.hot = True
        toaster.pop_up()
        self.assertFalse(toaster.hot)
        timer.end.assert_called_once()

>>>
Pop!
..
-------------------------------------------------
Ran 2 tests in 0.000s
OK
```

Writing a unit test for the `ReusableTimer` class could similarly mock its dependencies:

同样，编写`ReusableTimer`类的单元测试也可以模拟其依赖项：

```
from unittest import mock

class ReusableTimerUnitTest(TestCase):

    def test_countdown(self):
        my_func = lambda: None
        with mock.patch("threading.Timer"):
            timer = ReusableTimer()
            timer.countdown(0.1, my_func)
            threading.Timer.assert_called_once_with(0.1, my_func)
            timer.timer.start.assert_called_once()

    def test_end(self):
        my_func = lambda: None
        with mock.patch("threading.Timer"):
            timer = ReusableTimer()
            timer.countdown(0.1, my_func)
            timer.end()
            timer.timer.cancel.assert_called_once()
            
>>>
..
-------------------------------------------------
Ran 2 tests in 0.001s
OK
```

These unit tests work, but they require quite a lot of set up and fiddling with mocks. Instead, consider this single integration test that verifies the `Toaster` and `ReusableTimer` classes together, without using any mocks:

这些单元测试有效，但需要相当多的设置和摆弄mock。相反，考虑以下单一的集成测试，该测试在不使用任何mock的情况下验证`Toaster`和`ReusableTimer`类的协同工作：

```
class ToasterIntegrationTest(TestCase):

    def setUp(self):
        self.timer = ReusableTimer()
        self.toaster = Toaster(self.timer)
        self.toaster.doneness = 0

    def test_wait_finish(self):
        self.assertFalse(self.toaster.hot)
        self.toaster.push_down()
        self.assertTrue(self.toaster.hot)
        self.timer.timer.join()
        self.assertFalse(self.toaster.hot)

    def test_cancel_early(self):
        self.assertFalse(self.toaster.hot)
        self.toaster.push_down()
        self.assertTrue(self.toaster.hot)
        self.toaster.pop_up()
        self.assertFalse(self.toaster.hot)

>>>
Pop!
.Pop!
.
-------------------------------------------------
Ran 2 tests in 0.108s
OK
```

This test is clear, concise, and focused on the end-to-end behavior instead of implementation details. Perhaps the only gripe I have with it is that it accesses the internals of the `ReusableTimer` class in order to properly wait for the `threading.Timer` instance to finish (using the `join` method). But this is Python—having that kind of access for testing is one of the language’s primary benefits.

这个测试清晰、简洁，并专注于端到端的行为，而不是实现细节。也许我对它的唯一抱怨是为了正确等待`threading.Timer`实例完成而必须访问`ReusableTimer`类的内部（使用`join`方法）。但这正是Python的优势之一——为了测试而拥有这种访问权限是这门语言的主要优势之一。

The earlier unit tests for the `Toaster` and `ReusableTimer` classes, respectively, appear redundant and unnecessarily complex in comparison to this single integration test. However, there is one potential benefit that a unit test could bring to this code: testing the boundaries of the `doneness` setting to make sure it’s never too long or too short:

与这个单一的集成测试相比，前面分别为`Toaster`和`ReusableTimer`类编写的单元测试显得冗余且不必要的复杂。然而，单元测试对于这段代码来说有一个潜在的好处：测试`doneness`设置的边界，以确保它不会太长或太短：

```
class DonenessUnitTest(TestCase):
    def setUp(self):
        self.toaster = Toaster(ReusableTimer())

    def test_min(self):
        self.toaster.doneness = 0
        self.assertEqual(0.1, self.toaster._get_duration())

    def test_max(self):
        self.toaster.doneness = 1000
        self.assertEqual(120, self.toaster._get_duration())

>>>
..
-------------------------------------------------
Ran 2 tests in 0.000s
OK
```

This is the right balance for the tests you should write in Python: definitely have integration tests for end-to-end behaviors, and maybe have unit tests for intricate edge cases. It’s easy to avoid mocks most of the time and only use them when there’s a compelling reason (see Item 112: “Encapsulate Dependencies to Facilitate Mocking and Testing”). Otherwise, don’t forget that you’ll still need even larger system tests to verify how your Python programs interact with corresponding web clients, API endpoints, mobile applications, databases, etc.

这是你应该在Python中编写的测试的正确平衡：肯定要为端到端的行为编写集成测试，也许还要为复杂的边界情况编写单元测试。大多数时候很容易避免使用mock，只有在有令人信服的理由时才使用它们（参见条目112：“封装依赖以方便Mock和测试”）。否则，不要忘记你仍然需要更大的系统测试来验证你的Python程序如何与相应的Web客户端、API端点、移动应用程序、数据库等交互。

**Things to Remember**
- Integration tests verify the behavior of multiple components together, whereas unit tests only verify individual components on their own.
- Due to the highly dynamic nature of Python, integration tests are the best way——sometimes the only way——to gain confidence in the correctness of a program.
- Unit tests can be useful, in addition to integration tests, for verifying parts of a code base that have a lot of edge cases or boundary conditions.

**注意事项**
- 集成测试验证多个组件一起工作的行为，而单元测试仅验证单个组件。
- 由于Python的高度动态特性，集成测试通常是获得程序正确性信心的最佳方式，有时甚至是唯一方式。
- 单元测试除了集成测试外，还可以用来验证具有大量边界情况或边界条件的代码库部分。