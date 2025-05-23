# Chapter 10: Robustness (健壮性)

## Item 90: Never Set `__debug__` to `False` (永远不要将 `__debug__` 设置为 `False`)

When you add an `assert` statement like this into a Python program:

当你在Python程序中添加如下这样的`assert`语句时：

```
n = 3
assert n % 2 == 0, f"{n=} not even"
```

It’s essentially equivalent to the following code:

这基本上等价于以下代码：

```
if __debug__:
 if not (n % 2 == 0):
   raise AssertionError(f"{n=} not even")
>>>
Traceback ...
AssertionError: n=3 not even
```

You can also use the `__debug__` global built-in variable directly in order to gate the execution of more complex verification code:

你也可以直接使用`__debug__`这个全局内置变量来控制更复杂的验证代码的执行：

```
def expensive_check(x):
    return x != 2
    
items = [1, 2, 3]
if __debug__:
    for i in items:
        assert expensive_check(i), f"Failed {i=}"

>>>
Traceback ...
AssertionError: Failed i=2        
```

The only way to set the `__debug__` built-in global variable to `False` is by specifying the `-O` command-line argument at Python startup time. For example, here is a Python invocation that will start with `__debug__` equal to `True` (the default):

唯一能够将`__debug__`内置全局变量设置为`False`的方法是在Python启动时指定`-O`命令行参数。例如，下面是一个以`__debug__`默认值为`True`的Python调用示例：

```
$ python3 -c 'assert False, "FAIL"; print("OK")'
Traceback ...
AssertionError: FAIL
```

Adding the `-O` command-line option causes the `assert` statement to be skipped entirely, resulting in different output:

添加`-O`命令行选项会导致`assert`语句被完全跳过，从而产生不同的输出：

```
$ python3 -O -c 'assert False, "FAIL"; print("OK")'
OK
```

Although Python is an extremely dynamic language (see Item 3: “Never Expect Python to Detect Errors at Compile Time”) it still won’t allow you to modify the value of `__debug__` at runtime. You can be sure that if the constant is `True` it will always stay that way during the life of a program.

尽管Python是一门非常动态的语言（参见条目3：“永远不要期望Python在编译时检测错误”），它仍然不允许你在运行时修改`__debug__`的值。你可以确信，如果该常量是`True`，那么在整个程序生命周期内它都将保持不变。

```
__debug__ = False
>>>
Traceback ...
SyntaxError: cannot assign to __debug__
```

The original intention of the `__debug__` flag was to allow users to optimize the performance of their code by skipping seemingly unnecessary assertions at runtime. However, as time has gone on, more and more code, especially common frameworks and libraries, has become dependent on assertions being active in order to verify assumptions at program start-up time and runtime. By disabling the `assert` statement and other debug code, you’re undermining your program’s validity for little practical gain.

`__debug__`标志的初衷是为了让用户能够在运行时跳过看似不必要的断言以优化代码性能。然而，随着时间的推移，越来越多的代码，特别是常见的框架和库，变得依赖于断言的激活状态，以便在程序启动时间和运行时间验证假设。通过禁用`assert`语句和其他调试代码，你实际上是在削弱程序的有效性，而几乎没有实际收益。

If performance is what you’re after, there are far better approaches to making programs faster (see Item 92: “Profile Before Optimizing” and Item 94: “Know When and How to Replace Python with Another Programming Language”). If you have very expensive verification code that you need to disable at runtime, then create your own `enable_debug` helper function and associated global variables to control these debugging operations in your own code instead of relying on `__debug__` .

如果你追求的是性能，有比这更好的方法来提高程序的速度（参见条目92：“优化前先进行分析”和条目94：“知道何时以及如何用其他编程语言替换Python”）。如果你有一些非常耗时的验证代码需要在运行时禁用，那么创建自己的`enable_debug`辅助函数及相关全局变量来控制这些调试操作，而不是依赖`__debug__`。

There’s still value in always keeping assertions active, especially in low￾level code, even when you need to squeeze every ounce of performance out of your code, like when using MicroPython for microcontrollers (`https://micropython.org/`). Somewhat counter-intuitively, the presence of `assert` statements can help you debug even when they aren’t failing. When you get a bug report, you can use successfully passing assertions to rule out possibilities and narrow the scope of what’s gone wrong.

即便你需要从代码中榨取每一滴性能，在低级代码中保留断言仍然是有价值的，比如在使用MicroPython进行微控制器开发时（`https://micropython.org/`）。有些反直觉的是，即使断言没有失败，它们的存在也能帮助你进行调试。当你收到一个bug报告时，可以通过成功通过的断言来排除可能性，缩小问题范围。

Ultimately, assertions are a powerful tool for ensuring correctness, and they should be used liberally throughout your code to help make assumptions explicit.

最终，断言是一种确保正确性的强大工具，应该在你的代码中广泛使用，以帮助明确假设。

**Things to Remember**

- By default, the `__debug__` global built-in variable is `True` and Python programs will execute all `assert` statements.
- The `-O` command-line flag can be used to set `__debug__` to `False` , which causes `assert` statements to be ignored.
- Having `assert` statements present can help narrow the cause of bugs even when the assertions themselves haven’t failed.

**注意事项**

- 默认情况下，`__debug__`全局内置变量是`True`，Python程序会执行所有`assert`语句。
- 可以使用`-O`命令行标志将`__debug__`设置为`False`，这会导致忽略`assert`语句。
- 即使断言本身没有失败，存在`assert`语句可以帮助缩小bug的原因。