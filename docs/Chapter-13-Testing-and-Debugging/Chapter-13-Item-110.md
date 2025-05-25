# Chapter 13: Testing and Debugging (测试与调试)

## Item 110: Isolate Tests From Each Other with `setUp`, `tearDown`, `setUpModule`, and `tearDownModule` (使用 `setUp`、`tearDown`、`setUpModule` 和 `tearDownModule` 将测试彼此隔离)

`TestCase` subclasses (see Item 108: “Verify Related Behaviors in `TestCase` Subclasses”) often need to have the test enviornment set up before test methods can be run; this is sometimes called the test harness. To do this, you can override the `setUp` and `tearDown` methods of the `TestCase` parent class. These methods are called before and after each test method, respectively, allowing you to ensure that each test runs in isolation, which is an important best practice of proper testing.

`TestCase` 子类（参见条目 108：“在 `TestCase` 子类中验证相关行为”）通常需要在运行测试方法之前设置测试环境；这有时被称为测试夹具。为此，你可以重写 `TestCase` 父类的 `setUp` 和 `tearDown` 方法。这些方法分别在每个测试方法之前和之后调用，使你能够确保每个测试独立运行，这是良好测试的重要最佳实践。

For example, here I define a `TestCase` subclass that creates a temporary directory before each test and deletes its contents after each test finishes:

例如，这里我定义了一个 `TestCase` 子类，在每次测试之前创建一个临时目录，并在每次测试结束后删除其内容：

```
# environment_test.py
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase, main

class EnvironmentTest(TestCase):
    def setUp(self):
        self.test_dir = TemporaryDirectory()
        self.test_path = Path(self.test_dir.name)

    def tearDown(self):
        self.test_dir.cleanup()

    def test_modify_file(self):
        with open(self.test_path / "data.bin", "w") as f:
            f.write("hello")

if __name__ == "__main__":
    main()
```

When programs get complicated, you’ll want additional tests to verify the end-to-end interactions between your modules, instead of only testing code in isolation (see Item 109: “Prefer Integration Tests Over Unit Tests”). One common problem is that setting up your test environment for integration tests can be computationally expensive and may require a lot of wall-clock time. For example, you might need to start a database process and wait for it to finish loading indexes before you can run your integration tests. This type of latency makes it impractical to do test preparation and cleanup for every test in the `TestCase` subclass’s `setUp` and `tearDown` methods.

当程序变得复杂时，你可能需要更多的测试来验证模块之间的端到端交互，而不是仅仅测试代码的孤立部分（参见条目 109：“优先选择集成测试而非单元测试”）。一个常见的问题是，为集成测试设置测试环境可能会消耗大量计算资源并需要较长的实际时间。例如，你可能需要启动一个数据库进程并等待它完成索引加载后才能运行你的集成测试。这种延迟使得在 `TestCase` 子类的 `setUp` 和 `tearDown` 方法中进行测试准备和清理变得不切实际。

To handle this situation, the `unittest` module also supports module-level test harness initialization. You can configure expensive resources a single time, and then have all `TestCase` classes and their test methods run without repeating that initialization. Later, when all tests in the module are finished, the test harness can be torn down a single time. Here, I take advantage of this behavior by defining `setUpModule` and `tearDownModule` functions within the module containing the TestCase subclasses:

为处理这种情况，`unittest` 模块还支持模块级别的测试夹具初始化。你可以配置昂贵的资源一次，然后让所有 `TestCase` 类及其测试方法运行而无需重复该初始化。稍后，当模块中的所有测试完成后，可以仅进行一次测试夹具的清理。在此处，我通过在包含 `TestCase` 子类的模块中定义 `setUpModule` 和 `tearDownModule` 函数来利用此行为：

```
# integration_test.py
from unittest import TestCase, main

def setUpModule():
    print("* Module setup")

def tearDownModule():
    print("* Module clean-up")

class IntegrationTest(TestCase):
    def setUp(self):
        print("* Test setup")

    def tearDown(self):
        print("* Test clean-up")

    def test_end_to_end1(self):
        print("* Test 1")

    def test_end_to_end2(self):
        print("* Test 2")

if __name__ == "__main__":
    main()
    
$ python3 integration_test.py
* Module setup
* Test setup
* Test 1
* Test clean-up
.* Test setup
* Test 2
* Test clean-up
.* Module clean-up
-------------------------------------------------
Ran 2 tests in 0.000s
OK    
```

The `setUpModule` function is run by `unittest` only once, and it happens before any `setUp` methods are called. Similarly, `tearDownModule` happens after the `tearDown` method is called.

`setUpModule` 函数仅由 `unittest` 运行一次，并且它会在任何 `setUp` 方法被调用之前发生。类似地，`tearDownModule` 会在 `tearDown` 方法被调用之后发生。

**Things to Remember**
- Use the `setUp` and `tearDown` methods of `TestCase` to make sure your tests are isolated from each other and have a clean test environment.
- For integration tests, use the `setUpModule` and `tearDownModule` module-level functions to manage any test harnesses you need for the entire lifetime of a test module and all of the `TestCase` subclasses that it contains.

**注意事项**
- 使用 `TestCase` 的 `setUp` 和 `tearDown` 方法以确保测试彼此隔离，并具有干净的测试环境。
- 对于集成测试，请使用 `setUpModule` 和 `tearDownModule` 模块级函数来管理你需要在整个测试模块及其包含的所有 `TestCase` 子类生命周期中使用的测试夹具。