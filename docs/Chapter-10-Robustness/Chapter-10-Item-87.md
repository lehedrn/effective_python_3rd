# Chapter 10: Robustness (健壮性)

## Item 87: Use `traceback` for Enhanced Exception Reporting (使用 `traceback` 进行增强的异常报告)

When a Python program encounters a problem, an exception is often raised. If the exception is not caught and handled (see Item 80: “Take Advantage of Each Block in `try` / `except` / `else` / `finally` ”) it will propagate all the way up to the entry point of the program and cause it to exit with an error code. The Python interpreter will also print out a nicely formatted stack trace or traceback to aid developers in figuring out what went wrong. For example, here I use the `assert` statement to cause an exception and print out the corresponding traceback:

当 Python 程序遇到问题时，通常会引发一个异常。如果这个异常没有被捕获和处理（参见条目80：“充分利用 `try` / `except` / `else` / `finally` 中的每个块”），它将一直传播到程序的入口点，并导致程序以错误代码退出。Python 解释器还会打印出格式良好的堆栈跟踪或回溯信息，以帮助开发人员弄清楚哪里出了问题。例如，这里我使用 `assert` 语句来引发异常并打印相应的回溯信息：

```
def inner_func(message):
    assert False, message
def outer_func(message):
    inner_func(message)
outer_func("Oops!")

>>>
Traceback (most recent call last):
  File "<python-input-16>", line 1, in <module>
    outer_func("Oops!")
    ~~~~~~~~~~^^^^^^^^^
  File "<python-input-15>", line 2, in outer_func
    inner_func(message)
    ~~~~~~~~~~^^^^^^^^^
  File "<python-input-14>", line 2, in inner_func
    assert False, message
           ^^^^^
AssertionError: Oops!
```

This default printing behavior can be helpful for single-threaded code where all exceptions are happening in the main thread. But it won’t work for programs or servers that are handling many requests concurrently (see Item 71: “Know How to Recognize When Concurrency Is Necessary”). If you allow exceptions from one request to propagate all the way up to the entry point, the program will crash and cause all other requests to fail as well.

这种默认的打印行为对于所有异常都发生在主线程中的单线程代码是有帮助的。但对于处理并发请求的程序或服务器来说，这并不适用（参见条目71：“知道何时需要识别并发的必要性”）。如果你允许来自一个请求的异常传播到程序的入口点，程序将崩溃，并导致所有其他请求也失败。

One way to deal with this is to surround the root of a request handler with a blanket `try` statement (see Item 85: “Beware of Catching the `Exception` Class” and Item 86: “Understand the Difference Between `Exception` and `BaseException` ”). For example, here I define a hypothetical `Request` class and handler function. When an exception is hit, I can print it out to the console log for the developer to see, and then return an error code to the client. This ensures that all other handlers keep processing even in the presence of bad requests:

解决此问题的一种方法是用一个全面的 `try` 语句包围请求处理程序的根部（参见条目85：“警惕捕获 `Exception` 类” 和条目86：“了解 `Exception` 和 `BaseException` 之间的区别”）。例如，这里我定义了一个假想的 `Request` 类和处理函数。当遇到异常时，我可以将其打印到控制台日志中供开发人员查看，然后向客户端返回一个错误码。这确保了即使存在不良请求，所有其他处理程序也能继续处理：

```
class Request:
    def __init__(self, body):
        self.body = body
        self.response = None

def do_work(data):
    assert False, data

def handle(request):
    try:
        do_work(request.body)
    except BaseException as e:
        print(repr(e))
        request.response = 400  # Bad request error
request = Request("My message")
handle(request)
>>>
AssertionError('My message')
```

The problem with this code is that the string representation of the exception value doesn’t provide enough information to debug the issue. I don’t get a traceback like I would from an unhandled exception in the Python interpreter’s main thread. Fortunately, Python can fill this gap with the `traceback` built-in module. It allows you to extract the traceback information from an exception at runtime. Here, I use the `print_tb` function in the `traceback` built-in module to print a stack trace:

这段代码的问题在于异常值的字符串表示不足以调试问题。我不会得到像在 Python 解释器主线程中未处理异常时那样的回溯信息。幸运的是，Python 可以通过 `traceback` 内置模块填补这一空白。它允许你在运行时从异常中提取回溯信息。在这里，我使用 `traceback` 内置模块中的 `print_tb` 函数来打印堆栈跟踪：

```
import traceback

def handle2(request):
    try:
        do_work(request.body)
    except BaseException as e:
        traceback.print_tb(e.__traceback__)  # Changed
        print(repr(e))
        request.response = 400

request = Request("My message 2")
handle2(request)

>>>
  File "<python-input-25>", line 3, in handle2
    do_work(request.body)
    ~~~~~~~^^^^^^^^^^^^^^
  File "<python-input-19>", line 2, in do_work
    assert False, data
           ^^^^^
AssertionError('My message 2')
```

In addition to printing, you can process the traceback’s detailed information——including filename, line number, source code line, and containing function name——however you’d like (e.g., to display in a GUI). Here, I extract the function name for each frame in the traceback and print them to the console:

除了打印之外，你还可以以任何你喜欢的方式处理回溯的详细信息——包括文件名、行号、源代码行和包含函数名称——例如，在 GUI 中显示。在这里，我从回溯的每个帧中提取函数名称并打印到控制台：

```
def handle3(request):
    try:
        do_work(request.body)
    except BaseException as e:
        stack = traceback.extract_tb(e.__traceback__)
        for frame in stack:
            print(frame.name)
        print(repr(e))
        request.response = 400

request = Request("My message 3")
handle3(request)

>>>
handle3
do_work
AssertionError('My message 3')
```

Beyond printing to the console, I can also use the `traceback` module to provide more advanced error handling behaviors. For example, imagine that I wanted to save a log of exceptions encountered in a separate file, encoded as one JSON payload per line. Here, I accomplish this with a wrapper function that processes the traceback frames:

除了打印到控制台之外，我还可以使用 `traceback` 模块提供更高级的错误处理行为。例如，想象一下我希望将遇到的异常记录在一个单独的文件中，编码为每行一个 JSON 负载。在这里，我通过一个包装函数实现这一点，该函数处理回溯帧：

```
import json

def log_if_error(file_path, target, *args, **kwargs):
    try:
        target(*args, **kwargs)
    except BaseException as e:
        stack = traceback.extract_tb(e.__traceback__)
        stack_without_wrapper = stack[1:]
        trace_dict = dict(
            stack=[item.name for item in stack_without_wrapper],
            error_type=type(e).__name__,
            error_message=str(e),
        )
        json_data = json.dumps(trace_dict)

        with open(file_path, "a") as f:
            f.write(json_data)
            f.write("\n")
```

Calling the wrapper with the erroring `do_work` function will properly encode errors and write them to disk:

调用带有错误 `do_work` 函数的包装函数将正确编码错误并写入磁盘：

```
log_if_error("my_log.jsonl", do_work, "First error")
log_if_error("my_log.jsonl", do_work, "Second error")
with open("my_log.jsonl") as f:
    for line in f:
        print(line, end="")

>>>
{"stack": ["do_work"], "error_type": "AssertionError", "error_message": "First error"}
{"stack": ["do_work"], "error_type": "AssertionError", "error_message": "Second error"}
```

The `traceback` built-in module also includes a variety of other functions that make it easy to format, print, and traverse exception stack traces in most of the ways you’ll ever need (see `https://docs.python.org/3/library/traceback.html`). However, you’ll still need to handle some of the edge cases yourself (see Item 88: “Consider Explicitly Chaining Exceptions to Clarify Tracebacks” for one such case).

`traceback` 内建模块还包含各种其他函数，使你可以轻松地格式化、打印和遍历大多数你需要的异常堆栈追踪（请参阅 `https://docs.python.org/3/library/traceback.html`）。然而，你仍然需要自行处理一些边缘情况（参见条目88：“考虑显式链接异常以澄清堆栈追踪”）。

**Things to Remember**

- When an unhandled exception propagates up to the entry point of a Python program, the interpreter will print a nicely formatted list of the stack frames that caused the error.
- In highly concurrent programs, exception tracebacks are often not printed in the same way, making errors more difficult to understand and debug.
- The `traceback` built-in module allows you to interact with the stack frames from an `Exception` and process them in whatever way you see fit (i.e., to aid in debugging).

**注意事项**

- 当未处理的异常传播到 Python 程序的入口点时，解释器将打印出导致错误的堆栈帧的格式良好的列表。
- 在高度并发的程序中，异常堆栈追踪通常不会以相同方式打印，使得错误更难以理解和调试。
- `traceback` 内建模块允许你与 `Exception` 的堆栈帧进行交互，并以任何你认为合适的方式处理它们（即有助于调试）。