# Chapter 10: Robustness (健壮性)

A lot of useful Python code begins its life in a haphazardly developed script that solves a particular problem as a one-off. As these scripts are expanded, repurposed, and reused, they start to evolve from being short-term, throw-away code into substantial programs that are worth maintaining over the long-term.

许多有用的 Python 代码始于一个随意编写的脚本，该脚本一次性地解决了某个特定问题。随着这些脚本的扩展、重新利用和重复使用，它们开始从短期、一次性的代码演变为值得长期维护的重要程序。

Once you’ve written a useful Python program like this, the critical next step is to productionize your code so it’s bulletproof. Making programs dependable when they encounter unexpected circumstances is just as important as making programs with correct functionality. Python has built-in features and modules that aid in hardening your programs so they are robust in a wide variety of situations.

一旦你编写了这样一个有用的 Python 程序，下一步关键就是将你的代码投入生产环境，使其坚不可摧。当程序遇到意外情况时，确保其可靠的重要性丝毫不亚于实现正确的功能。Python 提供了内置的功能和模块，有助于增强你的程序，使它们在各种情况下都具备鲁棒性。

1. [Item 80: Take Advantage of Each Block in `try`/ `except`/ `else`/ `finally`](Chapter-10-Item-80.md) 充分利用 `try/except/else/finally` 中的各个块
2. [Item 81: `assert` Internal Assumptions and `raise` Missed Expectations](Chapter-10-Item-81.md) 用 `assert` 验证内部假设，并用 `raise` 抛出未满足的期望
3. [Item 82: Consider contextlib and with Statements for Reusable try/ finally Behavior](Chapter-10-Item-82.md) 考虑为可复用的 `try/finally` 行为使用 `contextlib` 和 `with` 语句
4. [Item 83: Always Make try Blocks as Short as Possible](Chapter-10-Item-83.md) 始终让 `try` 块尽可能短小
5. [Item 84: Beware of Exception Variables Disappearing](Chapter-10-Item-84.md) 警惕异常变量消失的问题
6. [Item 85: Beware of Catching the Exception Class](Chapter-10-Item-85.md) 警惕捕获 `Exception` 类本身的问题
7. [Item 86: Understand the Difference Between Exception and BaseException](Chapter-10-Item-86.md) 理解 `Exception` 和 `BaseException` 的区别
8. [Item 87: Use traceback for Enhanced Exception Reporting](Chapter-10-Item-87.md) 使用 `traceback` 实现更详细的异常报告
9. [Item 88: Consider Explicitly Chaining Exceptions to Clarify Tracebacks](Chapter-10-Item-88.md) 考虑显式链接异常以澄清追踪信息
10. [Item 89: Always Pass Resources into Generators and Have Callers Clean Them Up Outside](Chapter-10-Item-89.md) 始终将资源传递给生成器，并由调用者在其外部清理
11. [Item 90: Never Set __debug__ to False](Chapter-10-Item-90.md) 永远不要将 `__debug__` 设置为 False
12. [Item 91: Avoid exec and eval Unless You’re Building a Developer Tool](Chapter-10-Item-91.md) 除非构建开发工具，否则应避免使用 `exec` 和 `eval`