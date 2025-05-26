# Chapter 13: Testing and Debugging (测试与调试)

## Item 114: Consider Interactive Debugging with `pdb` (考虑使用 `pdb` 进行交互式调试)

Everyone encounters bugs in their code while developing programs. Using the `print` function can help you track down the sources of many issues (see Item 12: “Understand the Difference Between `repr` and `str` When Printing Objects”). Writing tests for specific cases that cause trouble is another great way to identify problems (see Item 109: “Prefer Integration Tests Over Unit Tests”).

在开发程序时，每个人都会遇到代码中的错误。使用 `print` 函数可以帮助您追踪许多问题的来源（参见条目 12：“打印对象时了解 `repr` 和 `str` 的区别”）。为导致麻烦的特定情况编写测试是识别问题的另一种好方法（参见条目 109：“集成测试优于单元测试”）。

But these tools aren’t enough to find every root cause. When you need something more powerful, it’s time to try Python’s built-in interactive debugger. The debugger lets you inspect the state of a running program, print local variables, and step through execution one statement at a time.

但是，这些工具不足以找到每个根本原因。当您需要更强大的功能时，就是尝试 Python 内置交互式调试器的时候了。调试器允许您检查运行中程序的状态，打印局部变量，并逐行执行程序。

In most other programming languages, you use a debugger by specifying what line of a source file you’d like to stop on, and then execute the program. In contrast, with Python, the easiest way to use the debugger is by modifying your program to directly initiate the debugger just before you think you’ll have an issue worth investigating. This means that there is no difference between starting a Python program in order to run the debugger and starting it normally.

在大多数其他编程语言中，您通过指定想要停止的源文件行来使用调试器，然后执行程序。相比之下，在 Python 中，最简单的使用调试器的方法是通过修改您的程序，在您认为将有问题值得调查之前直接启动调试器。这意味着以调试方式启动 Python 程序和正常启动之间没有区别。

To initiate the debugger, all you have to do is call the breakpoint built￾in function. This is equivalent to importing the pdb built-in module and running its set_trace function:

要启动调试器，只需调用内置的 breakpoint 函数即可。这相当于导入 pdb 内置模块并运行其 set_trace 函数：

```
# always_breakpoint.py
import math

def compute_rmse(observed, ideal):
    total_err_2 = 0
    count = 0
    for got, wanted in zip(observed, ideal):
        err_2 = (got - wanted) ** 2
        breakpoint()  # Start the debugger here
        total_err_2 += err_2
        count += 1

    mean_err = total_err_2 / count
    rmse = math.sqrt(mean_err)
    return rmse

result = compute_rmse(
    [1.8, 1.7, 3.2, 6],
    [2, 1.5, 3, 5],
)
print(result)
```

As soon as the `breakpoint` function runs, the program pauses its execution before the line of code immediately following the `breakpoint` call. The terminal that started the program will turn into a Python debugging shell:

一旦 `breakpoint` 函数运行，程序将在紧随 `breakpoint` 调用之后的代码行之前暂停其执行。启动程序的终端将变成一个 Python 调试 shell：

```
$ python3 always_breakpoint.py
> d:\workspace\python\effective_python_3rd\src\char_13\item_114\always_breakpoint.py(8)compute_rmse()
-> breakpoint()  # Start the debugger here
(Pdb) 
```

At the (`Pdb`) prompt, you can type in the names of local variables to see their values printed out (or use `p <name>` ). You can see a list of all local variables by calling the `locals` built-in function. You can import modules, inspect global state, construct new objects, and even modify parts of the running program. Some Python statements and language features aren’t supported in this debugging prompt, but you can access a standard Python REPL with access to program state using the `interact` command.

在 `(Pdb)` 提示符下，您可以键入本地变量的名称以查看它们的值被打印出来（或使用 `p <name>`）。您可以通过调用 `locals` 内建函数看到所有本地变量的列表。您可以导入模块，检查全局状态，构造新对象，甚至可以修改运行程序的部分内容。某些 Python 语句和语言特性在此调试提示符下不受支持，但您可以使用 `interact` 命令访问具有对程序状态访问权限的标准 Python REPL。

In addition, the debugger has a variety of special commands to control and understand program execution; type `help` to see the full list. Three very useful commands make inspecting the running program easier:

- `where` : Print the current execution call stack. This lets you figure out where you are in your program and how you arrived at the `breakpoint` trigger.
- `up` : Move your scope up the execution call stack to the caller of the current function. This allows you to inspect the local variables in higher levels of the program that led to the breakpoint.
- `down` : Move your scope back down the execution call stack one level.

此外，调试器还有各种特殊命令来控制和理解程序执行；键入 `help` 可以查看完整列表。三个非常有用的命令使检查运行程序更加容易：
- `where` : 打印当前执行调用堆栈。这可以让您弄清楚自己在程序中的位置以及如何到达 `breakpoint` 触发点。
- `up` : 将作用域向上移动到当前函数的调用者。这允许您检查导致断点的程序高层部分的本地变量。
- `down` : 将作用域向下移动调用堆栈一级。

When you’re done inspecting the current state, you can use these five debugger commands to control the program’s execution in different ways:

- `step` : Run the program until the next line of execution in the program, and then return control back to the debugger prompt. If the next line of execution includes calling a function, the debugger stops within the function that was called.
- `next` : Run the program until the next line of execution in the current function, then return control back to the debugger prompt. If the next line of execution includes calling a function, the debugger will not stop until the called function has returned.
- `return` : Run the program until the current function returns, and then return control back to the debugger prompt.
- `continue` : Continue running the program until the next breakpoint is hit (either through the `breakpoint` call or one added by a debugger command).
- `quit` : Exit the debugger and end the program. Run this command if you’ve found the problem, gone too far, or need to make program modifications and try again.

当您完成对当前状态的检查后，可以使用以下五个调试器命令以不同的方式控制程序执行：

- `step`: 运行程序直到程序的下一行执行，然后返回控制权给调试器提示符。如果下一行执行包括调用一个函数，则调试器会在被调用的函数内停止。
- `next` : 运行程序直到当前函数的下一行执行，然后返回控制权给调试器提示符。如果下一行执行包括调用一个函数，则调试器不会在被调用的函数返回前停止。
- `return` : 运行程序直到当前函数返回，然后返回控制权给调试器提示符。
- `continue` : 继续运行程序直到下一个断点被命中（通过 `breakpoint` 调用或者调试器命令添加的断点）。
- `quit` : 退出调试器并结束程序。如果您已发现问题、走得太远或需要进行程序修改并再次尝试，请运行此命令。

The `breakpoint` function can be called anywhere in a program. If you know that the problem you’re trying to debug happens only under special circumstances, then you can just write plain old Python code to call `breakpoint` after a specific condition is met. For example, here I start the debugger only if the squared error for a datapoint is more than 1 :

可以在程序的任何地方调用 `breakpoint` 函数。如果您知道要调试的问题仅在特殊情况下发生，则可以编写普通的 Python 代码，在满足特定条件后调用 `breakpoint`。例如，只有当数据点的平方误差大于 1 时，我才开始调试器：

```
# conditional_breakpoint.py
import math

def compute_rmse(observed, ideal):
    total_err_2 = 0
    count = 0
    for got, wanted in zip(observed, ideal):
        err_2 = (got - wanted) ** 2
        if err_2 >= 1:  # Start the debugger if True
            breakpoint()
        total_err_2 += err_2
        count += 1
    mean_err = total_err_2 / count
    rmse = math.sqrt(mean_err)
    return rmse

result = compute_rmse(
    [1.8, 1.7, 3.2, 7],
    [2, 1.5, 3, 5],
)
print(result)
```

When I run the program and it enters the debugger, I can confirm that the condition was true by inspecting local variables:

当我运行程序并进入调试器时，我可以通过检查局部变量确认条件为真：

```
$ python3 conditional_breakpoint.py
> d:\workspace\python\effective_python_3rd\src\char_13\item_114\conditional_breakpoint.py(9)compute_rmse()
-> breakpoint()
(Pdb) wanted
5
(Pdb) got
7
(Pdb) err_2
4
(Pdb) 
```

Another useful way to reach the debugger prompt is by using post-mortem debugging. This enables you to debug a program after it’s already raised an exception and crashed. This is especially helpful when you’re not quite sure where to put the `breakpoint` function call. Here, I have a script that will crash due to the `7j` complex number being present in one of the function’s arguments:

另一种达到调试器提示符的有用方法是使用事后调试。这使您能够在程序已经引发异常并崩溃之后对其进行调试。当您不确定在哪里放置 `breakpoint` 函数调用时，这尤其有帮助。这里有一个脚本，由于其中一个函数参数中存在 `7j` 复数而导致崩溃：

```
# postmortem_breakpoint.py
import math

def compute_rmse(observed, ideal):
    total_err_2 = 0
    count = 0
    for got, wanted in zip(observed, ideal):
        err_2 = (got - wanted) ** 2
        total_err_2 += err_2
        count += 1

    mean_err = total_err_2 / count
    rmse = math.sqrt(mean_err)
    return rmse

result = compute_rmse(
    [1.8, 1.7, 3.2, 7j],  # Bad input
    [2, 1.5, 3, 5],
)
print(result)
```

I use the command line `python3 -m pdb -c continue <program path>` to run the program under control of the `pdb` module. The `continue` command tells `pdb` to get the program started immediately. Once it’s running, the program hits a problem and automatically enters the interactive debugger, at which point I can inspect the program state:

我使用命令行 `python3 -m pdb -c continue <program path>` 在 `pdb` 模块的控制下运行程序。`continue` 命令告诉 `pdb` 立即启动程序。一旦它运行起来，程序会遇到问题并自动进入交互式调试器，这时我可以检查程序状态：

```
$ python3 -m pdb -c continue postmortem_breakpoin.py
Traceback (most recent call last):
  File "D:\Tools\miniconda3\envs\python313\Lib\pdb.py", line 2480, in main
    pdb._run(target)
    ~~~~~~~~^^^^^^^^
  File "D:\Tools\miniconda3\envs\python313\Lib\pdb.py", line 2220, in _run
    self.run(target.code)
    ~~~~~~~~^^^^^^^^^^^^^
  File "D:\Tools\miniconda3\envs\python313\Lib\bdb.py", line 666, in run
    exec(cmd, globals, locals)
    ~~~~^^^^^^^^^^^^^^^^^^^^^^
  File "<string>", line 1, in <module>
  File "D:\Workspace\Python\effective_python_3rd\src\char_13\item_114\postmortem_breakpoint.py", line 15, in <module>
    result = compute_rmse(
        [1.8, 1.7, 3.2, 7j],  # Bad input
        [2, 1.5, 3, 5],
    )
  File "D:\Workspace\Python\effective_python_3rd\src\char_13\item_114\postmortem_breakpoint.py", line 12, in compute_rmse
    rmse = math.sqrt(mean_err)
TypeError: must be real number, not complex
Uncaught exception. Entering post mortem debugging
Running 'cont' or 'step' will restart the program
> d:\workspace\python\effective_python_3rd\src\char_13\item_114\postmortem_breakpoint.py(12)compute_rmse()
-> rmse = math.sqrt(mean_err)
(Pdb) mean_err
(-5.97-17.5j)
```

You can also use post-mortem debugging after hitting an uncaught exception in the interactive Python interpreter by calling the `pm` function of the `pdb` module (which is often done in a single line as `import pdb; pdb.pm()` ):

您也可以在交互式 Python 解释器中遇到未捕获的异常后通过调用 `pdb` 模块的 `pm` 函数来进行事后调试（通常单行写成 `import pdb; pdb.pm()` ）：

```
$ python3
>>> import my_module
>>> my_module.compute_stddev([5])
Traceback (most recent call last):
 File "<stdin>", line 1, in <module>
 File "my_module.py", line 20, in compute_stddev
 variance = compute_variance(data)
 ^^^^^^^^^^^^^^^^^^^^^^
 File "my_module.py", line 15, in compute_varian
 variance = err_2_sum / (len(data) - 1)
 ~~~~~~~~~~^~~~~~~~~~~~~~~~~
ZeroDivisionError: float division by zero
>>> import pdb; pdb.pm()
> my_module.py(15)compute_variance()
-> variance = err_2_sum / (len(data) - 1)
(Pdb) err_2_sum
0.0
(Pdb) len(data)
1
```

**Things to Remember**

- You can initiate the Python interactive debugger at a point of interest directly in your program by calling the `breakpoint` built-in function.
- `pdb` shell commands let you precisely control program execution and allow you to alternate between inspecting program state and progressing program execution.
- The `pdb` module can be used to debug exceptions after they happen in independent Python programs (using `python -m pdb -c continue <program path>` ) or the interactive Python interpreter (using `import pdb; pdb.pm()` ).

**注意事项**

- 您可以直接在程序中的关注点通过调用内置的 `breakpoint` 函数启动 Python 交互式调试器。
- `pdb` shell 命令允许您精确控制程序执行，并允许您在检查程序状态和推进程序执行之间切换。
- `pdb` 模块可用于在独立 Python 程序中（使用 `python -m pdb -c continue <program path>`）或交互式 Python 解释器中（使用 `import pdb; pdb.pm()`）对异常发生后的情况进行调试。