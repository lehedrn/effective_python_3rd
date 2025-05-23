# Chapter 10: Robustness (健壮性)

## Item 91: Avoid `exec` and `eval` Unless You’re Building a Developer Tool (除非您正在构建开发者工具，否则应避免使用 `exec` 和 `eval`)

Python is a dynamic language that lets you do nearly anything at runtime (which can cause problems; see Item 3: “Never Expect Python to Detect Errors at Compile Time”). Many of its features enable these extremely flexible capabilities, such as `setattr` / `getattr` / `hasattr` (see Item 61: “Use `__getattr__` , `__getattribute__` , and `__setattr__` for Lazy Attributes”), metaclasses (see Item 64: “Annotate Class Attributes with `__set_name__` ”), and descriptors (see Item 60: “Use Descriptors for Reusable `@property` Methods”).

Python 是一门动态语言，它几乎允许您在运行时做任何事情（这可能会导致问题；参见条目3：“不要期望 Python 在编译时检测错误”）。它的许多特性都启用了这些极其灵活的功能，例如 `setattr` / `getattr` / `hasattr`（参见条目61：“将 `__getattr__`、`__getattribute__` 和 `__setattr__` 用于延迟属性”）、元类（参见条目64：“用 `__set_name__` 注释类属性”）和描述符（参见条目60：“使用描述符为 `@property` 方法提供可重用性”）。

However, the most dynamic capability of all is executing arbitrary code from a string at runtime. This is possible in Python with the `eval` and `exec` built-in functions.

然而，其中最强大的动态功能是能够在运行时从字符串执行任意代码。这在 Python 中可以通过内置的 `eval` 和 `exec` 函数实现。

`eval` takes a single expression as a string and returns the result of its evaluation as a normal Python object:

`eval` 接收一个单一表达式作为字符串，并返回其评估结果作为一个普通的 Python 对象：

```
x = eval("1 + 2")
print(x)
>>>
3
```

Passing a statement to `eval` will result in an error:

传递给 `eval` 语句会导致错误：

```
eval(
    """
if True:
    print('okay')
else:
    print('no')
"""
)

>>>
Traceback ...
SyntaxError: invalid syntax (<string>, line 2)
```

Instead, you can use `exec` to dynamically evaluate larger chunks of Python code. `exec` always returns `None` , so to get data out of it you need to use the global and local scope dictionary arguments. Here, when I access the `my_condition` variable it bubbles up to the global scope to be resolved, and my assignment of the `x` variable is made in the local scope (see Item 33: “Know How Closures Interact with Variable Scope and `nonlocal` ” for background):

相反，您可以使用 `exec` 来动态评估更大块的 Python 代码。 `exec` 总是返回 `None`，因此要从中获取数据，您需要使用全局和局部作用域字典参数。在这里，当我访问 `my_condition` 变量时，它会上溯到全局作用域以进行解析，并且我在本地作用域中分配了 `x` 变量（参见条目33：“了解闭包如何与变量作用域和 `nonlocal` 关键字交互”以获得背景信息）：

```
global_scope = {"my_condition": False}
local_scope = {}

exec(
    """
if my_condition:
    x = 'yes'
else:
    x = 'no'
""",
    global_scope,
    local_scope,
)

print(local_scope)

>>>
{'x': 'no'}
```


If you discover `eval` or `exec` in an otherwise normal application codebase, it’s often a red flag indicating that something is seriously wrong. These features can cause severe security issues if they are inadvertently connected to an input channel that gives access to an attacker. Even for plug-in architectures, where these features might seem like a natural fit, Python has better ways to achieve similar outcomes (see Item 97: “Lazy-load Modules with Dynamic Imports to Reduce Startup Time”).

如果您在一个正常的程序代码库中发现了 `eval` 或 `exec`，通常这是一个红色警报，表明某些地方出现了严重的问题。如果这些功能无意中连接到了给攻击者访问权限的输入通道，它们可能导致严重的安全问题。即使是插件架构，这些功能看似自然合适的选择，但 Python 有更好的方法来实现类似的结果（参见条目97：“使用动态导入懒加载模块以减少启动时间”）。

The only time it’s actually appropriate to use `eval` and `exec` is in code that supports your application with an improved development experience, such as a debugger, notebook system, run-eval-print-loop (REPL), performance benchmarking tool, code generation utility, etc. For any other purpose, avoid these insecure functions and use Python’s other dynamic and metaprogramming features instead.

实际上只有在支持应用程序提高开发体验的情况下，才适合使用 `eval` 和 `exec`，例如调试器、笔记本系统、运行-计算-打印循环（REPL）、性能基准测试工具、代码生成实用程序等。对于其他任何用途，都应该避免使用这些不安全的函数，并转而使用 Python 提供的其他动态和元编程功能。

**Things to Remember**
- `eval` allows you to execute a string containing a Python expression and capture its return value.
- `exec` allows you to execute a block of Python code and affect variable scope and the surrounding environment.
- Due to potential security risks, these features should be rarely or never used, limited only to improving the development experience.

**注意事项**
- `eval` 允许执行包含 Python 表达式的字符串并捕获其返回值。
- `exec` 允许执行一段 Python 代码并影响变量的作用域和周围环境。
- 由于潜在的安全风险，这些功能应很少或永不被使用，仅限于改善开发体验时使用。