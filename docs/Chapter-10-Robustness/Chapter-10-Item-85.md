# Chapter 10: Robustness (健壮性)

## Item 85: Beware of Catching the `Exception` Class (警惕捕获 `Exception` 类)

Errors in programs—both expected and unexpected—happen frequently. These issues are an aspect of building software that programmers must accept and attempt to mitigate. For example, say that I want to analyze the sales of a pizza restaurant and generate a daily summary report. Here, I accomplish this with a simple pipeline of functions:

程序中的错误——无论是预期的还是意外的——经常发生。这些问题程序员必须接受并试图缓解的软件构建的一个方面。例如，假设我想分析一家披萨店的销售情况，并生成每日总结报告。这里，我通过一个简单的函数流水线来实现这一点：

```
def load_data(path):
    open(path).read()

def analyze_data(data):
    return "my summary"

def run_report(path):
    data = load_data(path)
    summary = analyze(data)
    return summary
```

It would be useful to have an up-to-date summary always available, so I’ll call the `run_report` function on a schedule every 5 minutes. However, sometimes transient errors might occur, such as at the beginning of the day before the restaurant opens when no transactions have yet to be recorded in the daily file:

为了确保有一份最新的摘要，我会每5分钟定时调用一次 `run_report` 函数。然而，有时可能会出现短暂性的错误，比如一天开始时餐馆尚未营业，当天文件中还没有记录任何交易：

```
summary = run_report("pizza_data-2024-01-28.csv")
print(summary)

>>>
Traceback ...
FileNotFoundError: [Errno 2] No such file or directory: 'pizza_data-2024-01-28.csv'
```

Normally, I’d solve this problem by wrapping the `run_report` call with a `try` / `except` statement that logs a failure message to the console (see Item 80: “Take Advantage of Each Block in `try` / `except` / `else` / `finally` ” for details):

通常情况下，我会通过在 `try` / `except` 语句中包裹 `run_report` 调用来解决这个问题，该语句会在控制台记录一条失败信息（有关详细信息，请参见条目80：“充分利用 `try` / `except` / `else` / `finally` 中的每个块”）：

```
try:
    summary = run_report("pizza_data.csv")
except FileNotFoundError:
    print("Transient file error")
else:
    print(summary)
    
>>>
Transient file error
```

This will avoid one kind of problem, but the pipeline might raise many other types of transient exceptions that I haven’t anticipated. I want to prevent any intermittent errors from crashing the rest of the restaurant’s point-of-sale program in which the report is running. It’s more important for transactions to keep being processed than for the periodic report to be refreshed.

这将避免一种问题，但流水线可能引发许多其他类型的瞬态异常，这些异常我没有预料到。我希望防止任何间歇性错误导致运行报告的餐厅销售点程序的其余部分崩溃。对于交易继续处理来说，比定期刷新报告更为重要。

One way to insulate the rest of the system from failures is to catch the broader `Exception` parent class instead of the more specific `FileNotFoundError` class:

隔离系统其余部分免受故障影响的一种方法是捕获更广泛的 `Exception` 父类而不是更具体的 `FileNotFoundError` 类：

```
try:
    summary = run_report("pizza_data.csv")
except Exception: # Changed
    print("Transient report issue")
else:
    print(summary)
>>>
Transient report issue
```

When an exception is raised, each of the `except` clauses is considered in order. If the exception value’s type is a subclass of the clause’s specified class, then the corresponding error handling code will be executed. By providing the `Exception` class to match, I’ll catch errors of any kind since they all inherit from this parent class.

当引发异常时，会按顺序考虑每个 `except` 子句。如果异常值的类型是子句指定类的子类，则执行相应的错误处理代码。通过提供 `Exception` 类进行匹配，我将捕获各种类型的错误，因为它们都继承自这个父类。

Unfortunately, this approach has a big problem: The `try` / `except` statement might prevent me from noticing legitimate problems with my code. Once the pizza restaurant opens and the data file is definitely present, the `run_report` function surprisingly still fails. The cause is a typo in the original definition of `run_report` that called the `analyze` function—which does not exist—instead of the correct `analyze_data` function:

不幸的是，这种方法有一个大问题：`try` / `except` 语句可能会阻止我发现代码中的真正问题。一旦披萨店开门营业且数据文件肯定存在时，`run_report` 函数仍然出人意料地失败。原因是原始定义 `run_report` 函数中调用了不存在的 `analyze` 函数，而不是正确的 `analyze_data` 函数：

```
run_report("my_data.csv")
>>>
Traceback ...
NameError: name 'analyze' is not defined
```

Due to the highly dynamic nature of Python, the interpreter will only detect that the function is missing at execution time, not when the program first loads (see Item 3: “Never Expect Python to Detect Errors at Compile Time” for details). The interpreter will raise a `NameError` in this situation, which is a subclass of the `Exception` class. Thus, the corresponding `except` clause will catch the exception and report it as a transient error even though it’s actually a critical problem.

由于 Python 的高度动态性质，解释器只会在执行时检测到缺少该函数，而不是在程序首次加载时（详情请参见条目3：“永远不要期望 Python 在编译时检测错误”）。在这种情况下，解释器将引发 `NameError`，这是 `Exception` 类的子类。因此，相应的 `except` 子句会捕获该异常并将其报告为临时错误，即使它实际上是一个严重的问题。

One way to mitigate this issue is to always print or log the exception that’s caught when matching the `Exception` class. At least that way the details about the error received will be visible; anyone looking at the console output might notice there’s a real bug in the program. For example, here I print both the exception value and its type to make it abundantly clear what went wrong:

缓解此问题的一种方法是在匹配 `Exception` 类时始终打印或记录捕获到的异常。至少这样可以看到接收到的错误细节；查看控制台输出的人可能会注意到程序中确实存在一个 bug。例如，在下面的例子中，我同时打印了异常值及其类型，以清楚说明出了什么问题：

```
try:
    summary = run_report("my_data.csv")
except Exception as e:
    print("Fail:", type(e), e)
else:
    print(summary)
>>>
Fail: <class 'NameError'> name 'analyze' is not defined
```

There other ways that overly broad exception handling can cause problems that are worth knowing as well (see Item 86: “Understand the Difference Between `Exception` and `BaseException` ” and Item 89: “Always Pass Resources into Generators and Have Callers Clean Them Up Outside”). Additionally, there are more robust ways to report and handle errors for explicit APIs that help avoid these problems (see Item 121: “Define a Root `Exception` to Insulate Callers from APIs”). Catching exceptions to isolate errors can be useful, but you need to ensure you’re not accidentally hiding issues.

还有其他方式可能导致过于宽泛的异常处理引起问题，也值得了解（详情请参见条目86：“理解 `Exception` 和 `BaseException` 之间的区别”以及条目89：“始终向生成器传入资源并在外部由调用者清理它们”）。此外，还有一些更稳健的方法可以报告和处理显式API中的错误，有助于避免这些问题（详情请参见条目121：“定义一个根 `Exception` 以保护调用者免受API的影响”）。捕捉异常以隔离错误可能很有用，但需要确保不会无意中隐藏问题。

**Things to Remember**

- Using the `Exception` class in `except` clauses can help you insulate one part of your program from the others.
- Catching broad categories of exceptions might cause your code to handle errors you didn’t intend, which can inadvertently hide problems.
- When using a broad exception handler, it’s important to print or otherwise log any errors encountered to provide visibility into what’s really happening.

**注意事项**

- 在 `except` 子句中使用 `Exception` 类可以帮助你将程序的一部分与其它部分隔离开。
- 捕获广泛类别的异常可能导致你的代码处理一些未打算处理的错误，从而可能掩盖问题。
- 使用广义异常处理器时，重要的是要打印或以其他方式记录遇到的任何错误，以便提供关于实际发生情况的可见性。