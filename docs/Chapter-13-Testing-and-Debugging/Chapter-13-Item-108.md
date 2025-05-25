# Chapter 13: Testing and Debugging (测试与调试)

## Item 108: Verify Related Behaviors in `TestCase` Subclasses (在 `TestCase` 子类中验证相关行为)

The canonical way to write tests in Python is to use the `unittest` built-in module. For example, say I have the following utility function defined that I would like to verify works correctly across a variety of inputs:

在 Python 中编写测试的标准方式是使用内置的 `unittest` 模块。例如，假设我有以下定义的实用函数，我希望验证它在各种输入下是否正常工作：

```
# utils.py
def to_str(data):
    if isinstance(data, str):
        return data
    elif isinstance(data, bytes):
        return data.decode("utf-8")
    else:
        raise TypeError(f"Must supply str or bytes, found: {data}")
```

To define tests, I create a second file named `test_utils.py` or `utils_test.py`——the naming scheme is a style choice——that contains tests for each behavior that I expect:

为了定义测试，我会创建一个名为 `test_utils.py` 或 `utils_test.py` 的第二个文件（命名方案是一种风格选择），其中包含每个预期行为的测试：

```
# utils_test.py
from unittest import TestCase, main
from utils import to_str

class UtilsTestCase(TestCase):
    def test_to_str_bytes(self):
        self.assertEqual("hello", to_str(b"hello"))

    def test_to_str_str(self):
        self.assertEqual("hello", to_str("hello"))

    def test_failing(self):
        self.assertEqual("incorrect", to_str("hello"))

if __name__ == "__main__":
    main()
```

Then, I run the test file using the Python command line. In this case, two of the test methods pass and one fails, printing out a helpful error message about what went wrong:

然后，我使用 Python 命令行运行测试文件。在这种情况下，两个测试方法通过了，而一个失败了，并打印出关于问题的有用错误信息：

```
$ python3 utils_test.py
F..
======================================================================
FAIL: test_failing (__main__.UtilsTestCase.test_failing)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "D:\Workspace\Python\effective_python_3rd\src\char_13\item_108\utils_test.py", line 12, in test_failing
    self.assertEqual("incorrect", to_str("hello"))
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 'incorrect' != 'hello'
- incorrect
+ hello
----------------------------------------------------------------------
Ran 3 tests in 0.002s
FAILED (failures=1)
```

Tests are organized into `TestCase` subclasses. Each test case is a method beginning with the word `test` . If a test method runs without raising any kind of `Exception` (including `AssertionError` from `assert` statements; see Item 81: “ `assert` Internal Assumptions, `raise` Missed Expectations”), then the test is considered to have passed successfully. If one test fails, the `TestCase` subclass continues running the other test methods so you can get a full picture of how all of your tests are doing
instead of stopping at the first sign of trouble.

测试被组织成 `TestCase` 子类。每个测试用例都是以 `test` 开头的方法。如果一个测试方法在不抛出任何类型的异常（包括来自 `assert` 语句的 `AssertionError`；参见条目 81：“断言内部假设，未满足期望时抛出异常”）的情况下运行，则认为测试成功通过。如果一个测试失败，`TestCase` 子类将继续运行其他测试方法，以便您可以全面了解所有测试的情况，而不是在第一次出现问题时就停止。

If you want to iterate quickly to fix or improve a specific test, you can run only that test method by specifying its path within the test module on the command line:

如果您想快速迭代以修复或改进特定的测试，可以通过命令行指定测试模块内的路径来仅运行该测试方法：

```
$ python3 utils_test.py UtilsTestCase.test_to_str_str
.
----------------------------------------------------------------------
Ran 1 test in 0.000s
OK
```

You can also invoke the debugger from directly within test methods at specific breakpoints in order to dig more deeply into the cause of failures (see Item 114: “Consider Interactive Debugging with `pdb` ” for how to do that).

您还可以从测试方法内直接调用调试器，在特定的断点处深入挖掘失败的原因（参见条目 114：“考虑使用 `pdb` 进行交互式调试”了解具体操作方法）。

The `TestCase` class provides helper methods for making assertions in your tests, such as `assertEqual` for verifying equality, `assertTrue` for verifying Boolean expressions, `assertAlmostEqual` for when precision is a concern (see Item 113: “Use `assertAlmostEqual` to Control Precision in Floating Point Tests”), and many more (see `https://docs.python.org/3/library/unittest.html` for the full list). These are better than using the built-in `assert` statement because they print out all of the inputs and outputs to help you understand the exact reason the test is failing. For example, here I have the same test case written with and without using a helper assertion method:

`TestCase` 类提供了在测试中进行断言的帮助方法，如用于验证相等性的 `assertEqual`、用于验证布尔表达式的 `assertTrue`、用于精度问题的 `assertAlmostEqual`（参见条目 113：“在浮点数测试中使用 `assertAlmostEqual` 控制精度”），以及许多其他方法（完整列表请参阅 [https://docs.python.org/3/library/unittest.html](https://docs.python.org/3/library/unittest.html)）。这些方法比使用内置的 `assert` 语句更好，因为它们会打印出所有的输入和输出，帮助您理解测试失败的确切原因。例如，以下是使用和不使用辅助断言方法编写的相同测试用例：

```
# assert_test.py
from unittest import TestCase, main
from utils import to_str

class AssertTestCase(TestCase):
    def test_assert_helper(self):
        expected = 12
        found = 2 * 5
        self.assertEqual(expected, found)

    def test_assert_statement(self):
        expected = 12
        found = 2 * 5
        assert expected == found

if __name__ == "__main__":
    main()
```

Which of these failure messages seems more helpful to you? Note how the second message doesn’t show the values of `expected` or `found` :

哪一个失败消息对您来说更有帮助？请注意第二条消息没有显示 `expected` 或 `found` 的值：

```
$ python3 assert_test.py
FF
======================================================================
FAIL: test_assert_helper (__main__.AssertTestCase.test_assert_helper)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "D:\Workspace\Python\effective_python_3rd\src\char_13\item_108\assert_test.py", line 8, in test_assert_helper
    self.assertEqual(expected, found)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^
AssertionError: 12 != 10
======================================================================
FAIL: test_assert_statement (__main__.AssertTestCase.test_assert_statement)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "D:\Workspace\Python\effective_python_3rd\src\char_13\item_108\assert_test.py", line 13, in test_assert_statement
    assert expected == found
           ^^^^^^^^^^^^^^^^^
AssertionError
----------------------------------------------------------------------
Ran 2 tests in 0.001s
FAILED (failures=2)
```

There’s also an `assertRaises` helper method for verifying exceptions, which can be used as a context manager in `with` statements (see Item 82: “Consider `contextlib` and `with` Statements for Reusable `try` / `finally` Behavior” for how that works). This appears similar to a `try` / `except` statement, and makes it abundantly clear where the exception is expected to be raised:

还有一个 `assertRaises` 辅助方法用于验证异常，可以用作 `with` 语句中的上下文管理器（参见条目 82：“考虑使用 `contextlib` 和 `with` 语句重用 `try` / `finally` 行为”了解其工作原理）。这看起来类似于 `try` / `except` 语句，并且清楚地表明了预期引发异常的位置：

```
# utils_error_test.py
from unittest import TestCase, main
from utils import to_str

class UtilsErrorTestCase(TestCase):
    def test_to_str_bad(self):
        with self.assertRaises(TypeError):
            to_str(object())

    def test_to_str_bad_encoding(self):
        with self.assertRaises(UnicodeDecodeError):
            to_str(b"\xfa\xfa")

if __name__ == "__main__":
    main()
```

You can also define your own helper methods with complex logic in `TestCase` subclasses to make your tests more readable. Just ensure that your method names don’t begin with the word `test` , or they’ll be run as if they’re test cases. In addition to calling `TestCase` assertion methods, these custom test helpers often use the `fail` method to clarify which assumption or invariant wasn’t met. For example, here I define a custom test helper method for verifying the behavior of a generator:

您还可以在 `TestCase` 子类中定义带有复杂逻辑的自定义帮助方法，以使您的测试更具可读性。只需确保您的方法名称不以 `test` 开头，否则它们将被视为测试用例运行。除了调用 `TestCase` 断言方法外，这些自定义测试助手通常使用 `fail` 方法来澄清未满足的假设或不变条件。例如，这里我定义了一个用于验证生成器行为的自定义测试帮助方法：

```
# helper_test.py
from unittest import TestCase, main

def sum_squares(values):
    cumulative = 0
    for value in values:
        cumulative += value**2
        yield cumulative

class HelperTestCase(TestCase):
    def verify_complex_case(self, values, expected):
        expect_it = iter(expected)
        found_it = iter(sum_squares(values))
        test_it = zip(expect_it, found_it, strict=True)

        for i, (expect, found) in enumerate(test_it):
            if found != expect:
                self.fail(f"Index {i} is wrong: {found} != {expect}")

    def test_too_short(self):
        values = [1.1, 2.2]
        expected = [1.1**2]
        self.verify_complex_case(values, expected)

    def test_too_long(self):
        values = [1.1, 2.2]
        expected = [
            1.1**2,
            1.1**2 + 2.2**2,
            0,  # Value doesn't matter
        ]
        self.verify_complex_case(values, expected)

    def test_wrong_results(self):
        values = [1.1, 2.2, 3.3]
        expected = [
            1.1**2,
            1.1**2 + 2.2**2,
            1.1**2 + 2.2**2 + 3.3**2 + 4.4**2,
        ]
        self.verify_complex_case(values, expected)

if __name__ == "__main__":
    main()
```

The helper method makes the test cases short and readable, and the outputted error messages are easy to understand:

这个帮助方法使得测试用例简短且易于阅读，输出的错误消息也容易理解：

```
$ python3 helper_test.py
EEF
======================================================================
ERROR: test_too_long (__main__.HelperTestCase.test_too_long)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "D:\Workspace\Python\effective_python_3rd\src\char_13\item_108\helper_test.py", line 31, in test_too_long
    self.verify_complex_case(values, expected)
    ~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^
  File "D:\Workspace\Python\effective_python_3rd\src\char_13\item_108\helper_test.py", line 15, in verify_complex_case
    for i, (expect, found) in enumerate(test_it):
                              ~~~~~~~~~^^^^^^^^^
ValueError: zip() argument 2 is shorter than argument 1
======================================================================
ERROR: test_too_short (__main__.HelperTestCase.test_too_short)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "D:\Workspace\Python\effective_python_3rd\src\char_13\item_108\helper_test.py", line 22, in test_too_short
    self.verify_complex_case(values, expected)
    ~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^
  File "D:\Workspace\Python\effective_python_3rd\src\char_13\item_108\helper_test.py", line 15, in verify_complex_case
    for i, (expect, found) in enumerate(test_it):
                              ~~~~~~~~~^^^^^^^^^
ValueError: zip() argument 2 is longer than argument 1
======================================================================
FAIL: test_wrong_results (__main__.HelperTestCase.test_wrong_results)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "D:\Workspace\Python\effective_python_3rd\src\char_13\item_108\helper_test.py", line 40, in test_wrong_results
    self.verify_complex_case(values, expected)
    ~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^
  File "D:\Workspace\Python\effective_python_3rd\src\char_13\item_108\helper_test.py", line 17, in verify_complex_case
    self.fail(f"Index {i} is wrong: {found} != {expect}")
    ~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: Index 2 is wrong: 16.939999999999998 != 36.3
----------------------------------------------------------------------
Ran 3 tests in 0.004s
FAILED (failures=1, errors=2)
```

I usually define one `TestCase` subclass for each set of related tests. Sometimes, I have one `TestCase` subclass for each function that has many edge cases. Other times, a `TestCase` subclass spans all functions in a single module. I often create one `TestCase` subclass for testing each basic class and all of its methods (see Item 109: “Prefer Integration Tests Over Unit Tests” for more guidance).

我通常为每组相关的测试定义一个 `TestCase` 子类。有时，我为每个具有许多边界情况的函数定义一个 `TestCase` 子类。其他时候，一个 `TestCase` 子类可能涵盖单个模块中的所有函数。我经常为测试每个基本类及其所有方法创建一个 `TestCase` 子类（有关更多指导，请参见条目 109：“优先集成测试而非单元测试”）。

The `TestCase` class also provides a `subTest` helper method that enables you to avoid boilerplate by defining multiple tests within a single test method. This is especially helpful for writing data-driven tests, and it allows the test method to continue testing other cases even after one of them fails (similar to the behavior of `TestCase` with its contained test methods; see Item 110: “Isolate Tests From Each Other with `setUp` , `tearDown` , `setUpModule` , and `tearDownModule` ” for another
approach). To show this, here I define an example data-driven test:

`TestCase` 类还提供了一个 `subTest` 辅助方法，通过在一个测试方法中定义多个测试来避免样板代码。这对于编写数据驱动的测试特别有用，并且允许测试方法在一个案例失败后继续测试其他案例（类似于 `TestCase` 及其包含的测试方法的行为；参见条目 110：“使用 `setUp`、`tearDown`、`setUpModule` 和 `tearDownModule` 隔离测试”了解另一种方法）。为了展示这一点，这里我定义了一个示例数据驱动测试：

```
# data_driven_test.py
from unittest import TestCase, main
from utils import to_str

class DataDrivenTestCase(TestCase):
    def test_good(self):
        good_cases = [
            (b"my bytes", "my bytes"),
            ("no error", b"no error"),  # This one will fail
            ("other str", "other str"),
        ]
        for value, expected in good_cases:
            with self.subTest(value):
                self.assertEqual(expected, to_str(value))

    def test_bad(self):
        bad_cases = [
            (object(), TypeError),
            (b"\xfa\xfa", UnicodeDecodeError),
        ]
        for value, exception in bad_cases:
            with self.subTest(value):
                with self.assertRaises(exception):
                    to_str(value)

if __name__ == "__main__":
    main()
```

The `"no error"` test case fails, printing a helpful error message, but all of the other cases are still tested and confirmed to pass:

`"no error"` 测试用例失败了，打印出了有用的错误信息，但所有其他用例仍然进行了测试并确认通过：

```
$ python3 data_driven_test.py
.F
======================================================================
FAIL: test_good (__main__.DataDrivenTestCase.test_good) [no error]
----------------------------------------------------------------------
Traceback (most recent call last):
  File "D:\Workspace\Python\effective_python_3rd\src\char_13\item_108\data_driven_test.py", line 13, in test_good
    self.assertEqual(expected, to_str(value))
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: b'no error' != 'no error'
----------------------------------------------------------------------
Ran 2 tests in 0.002s
FAILED (failures=1)
```

At some point, depending on your project’s complexity and testing requirements, you might outgrow `unittest` and its capabilities. If and when that happens, the pytest (`https://pytest.org`) open source package and its large number of community plug-ins can be especially useful as an alternative test runner.

在某些时候，根据项目的复杂性和测试需求，您可能会超出 `unittest` 及其功能的范围。如果发生这种情况，可以考虑使用 pytest（[https://pytest.org](https://pytest.org)）开源包及其大量的社区插件作为替代测试运行器。

**Things to Remember**
- You can create tests by subclassing the `TestCase` class from the `unittest` built-in module, and defining one method per behavior you’d like to test. Test methods on `TestCase` classes must start with the word `test` .
- Use the various helper methods defined by the `TestCase` class, such as `assertEqual` , to confirm expected behaviors in your tests instead of using the built-in `assert` statement.
- Consider writing data-driven tests using the `subTest` helper method in order to reduce boilerplate.

**注意事项**
- 您可以通过从 `unittest` 内置模块继承 `TestCase` 类，并为希望测试的每个行为定义一个方法来创建测试。`TestCase` 类上的测试方法必须以 `test` 开头。
- 使用 `TestCase` 类定义的各种辅助方法（如 `assertEqual`）来确认测试中的预期行为，而不是使用内置的 `assert` 语句。
- 考虑使用 `subTest` 辅助方法编写数据驱动的测试，以减少样板代码。
