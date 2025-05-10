# Chapter 1: Pythonic Thinking (第一章 用Pythonic方式来思考)

## Item 3: Never Expect Python to Detect Errors at Compile Time (不要期望Python在编译时检测错误)

When loading a Python program and preparing for execution, the source code is parsed into abstract syntax trees and checked for obvious structural errors. For example, a poorly constructed `if` statement will raise a SyntaxError exception indicating what’s wrong with the code:

在加载Python程序并准备执行时，源代码会被解析为抽象语法树，并检查明显的结构错误。例如，一个构造不当的if语句会引发一个SyntaxError异常，指出代码中的问题：

```
if True # Bad syntax
 print('hello')
>>>
Traceback ...
SyntaxError: expected ':'
```

Errors in value literals will also be detected early and raise an exception:

值字面量中的错误也会被提前检测并引发异常：

```
1.3j5 # Bad number
>>>
Traceback ...
SyntaxError: invalid imaginary literal
```

Unfortunately, that’s about all the protection you can expect from Python before execution. Anything beyond basic tokenization errors and parse errors will not be flagged as a problem.

不幸的是，这是Python在执行前能提供的一切保护。除了基本的词法分析错误和解析错误之外，其他任何问题都不会被标记为问题。

Even simple functions that seem to have obvious errors will not be reported as having problems before program execution, due to the highly dynamic nature of Python. For example, here, I define a function where the `my_var` variable is clearly not assigned before it’s passed to `print` :

由于Python的高度动态性，即使看起来明显有错误的简单函数，在程序执行之前也不会报告存在问题。例如，这里我定义了一个函数，其中my_var变量显然在传递给print之前没有被赋值：

```
def bad_reference():
    print(my_var)
    my_var = 123
```

But this won’t raise an exception until the function is executed:

但这个错误直到函数被执行时才会引发异常：

```
bad_reference()
>>>
Traceback ...
UnboundLocalError: cannot access local variable 
is not associated with a value
```

The reason this isn’t considered a static error is because it’s valid for Python programs to dynamically assign local and global variables. For example, here I define a function that is valid or not depending on the input argument:

这种情况下不被视为静态错误的原因是，对于Python程序来说，动态分配局部变量和全局变量是合法的。例如，这里我定义了一个函数，其有效性取决于输入参数：

```
def sometimes_ok(x):
    if x:
        my_var = 123
    print(my_var)
```

This call runs fine:

以下调用运行良好：

```
sometimes_ok(True)
>>>
123
```

While this one causes a runtime exception:

而以下调用则会导致运行时异常：

```
sometimes_ok(False)
>>>
Traceback ...
UnboundLocalError: cannot access local variable 
is not associated with a value
```

Python also won’t catch math errors upfront. It would seem that this is clearly an error before the program executes:

Python也不会预先捕捉数学错误。例如，在程序执行之前这显然是一个错误：

```
def bad_math():
    return 1 / 0
```

But it’s possible for the meaning of the division operator to vary based the values involved, so checking for errors like this is similarly deferred until runtime:

但由于除法运算符的含义可能根据涉及的值而变化，因此类似这样的错误检查同样会被推迟到运行时：

```
bad_math()
>>>
Traceback ...
ZeroDivisionError: division by zero
```

Python also won’t statically detect problems with undefined methods, too many or too few supplied arguments, mismatched return types, and many more seemingly obvious issues. There are community tools that can help you detect some of these errors before execution, such as [flake8] (https://github.com/PyCQA/flake8) and type checkers that work with the `typing` built-in module (see Item 124: “Consider Static Analysis via typing to Obviate Bugs”).

Python也不会静态检测未定义的方法、提供的参数过多或过少、返回类型不匹配以及许多看似明显的问题。有一些社区工具可以帮助你在执行之前发现一些最常见的错误来源，例如[flake8](https://github.com/PyCQA/flake8)和与内置模块typing一起工作的类型检查器（参见条目124：“考虑通过typing进行静态分析以消除错误”）。

Ultimately, when writing idiomatic Python you’re going to encounter most errors at runtime. The Python language prioritizes runtime flexibility over compile-time error detection. For this reason, it’s important to check that your assumptions are correct at runtime (see Item 81: “ assert Internal Assumptions, raise Missed Expectations”) and verify the correctness of your code with automated tests (see Item 109: “Prefer Integration Tests Over Unit Tests”).

最终，在编写符合Python习惯的代码时，你会在运行时遇到大多数错误。Python语言优先考虑运行时灵活性而不是编译时错误检测。因此，重要的是在运行时检查你的假设是否正确（参见条目81：“assert内部假设，raise未满足的期望”），并通过自动化测试验证代码的正确性（参见条目109：“集成测试优于单元测试”）。

**Things to Remember**

- Python defers nearly all error checking until runtime, including detection of problems that seem like they should be obvious during program start-up.
- Community projects like linters and static analysis tools can help catch some of the most common sources of errors before program execution.

**注意事项**

- Python将几乎所有错误检查推迟到运行时，包括那些在程序启动期间似乎应该是明显的错误。
- 社区项目如代码检查工具和静态分析工具可以在程序执行之前帮助捕获一些最常见的错误来源。