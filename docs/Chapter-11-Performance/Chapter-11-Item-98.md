# Chapter 11: Performance (性能)

## Item 98: Lazy-Load Modules with Dynamic Imports to Reduce Startup Time (通过动态导入延迟加载模块以减少启动时间)

The previous item investigated how Python program initialization can be slow, and considered ways to improve performance (see Item 97: “Rely on Precompiled Bytecode and File System Caching to Improve Startup Time”). After following those best practices and further optimizing (see Item 92: “Profile Before Optimizing”), your Python programs might still feel like they take too long to start. Fortunately, there is one more technique to try: dynamic imports.

前一条目探讨了Python程序初始化可能缓慢的问题，并考虑了提升性能的方法（参见条目97：“依赖预编译的字节码和文件系统缓存以提升启动时间”）。在遵循这些最佳实践并进一步优化后（参见条目92：“优化之前进行性能分析”），您的Python程序可能仍然感觉启动时间过长。幸运的是，还有一个技巧可以尝试：动态导入。

For example, imagine that I’m building an image processing tool with two features. The first module adjusts an image’s brightness and contrast based on user-supplied settings:

例如，假设我正在构建一个具有两个功能的图像处理工具。第一个模块根据用户提供的设置调整图像的亮度和对比度：

```
# adjust.py
# Fast initialization

def do_adjust(path, brightness, contrast):
    print(f"Adjusting! {brightness=} {contrast=}")
```

The second module intelligently enhances an image a given amount. To demonstrate a realistic situation, I’m going to assume that this requires loading a large native image processing library, and thus initializes slowly:

第二个模块智能地增强给定程度的图像。为了演示一个现实情况，我假设这需要加载一个大型的本地图像处理库，因此初始化速度较慢：

```
# enhance.py
# Very slow initialization
import time

time.sleep(1)

def do_enhance(path, amount):
    print(f"Enhancing! {amount=}")
```

I can make these functions available as a command-line utility with the `argparse` built-in module. Here, I use the `add_subparsers` feature to require a different set of flags depending on the user-specified command. The `adjust` command accepts the `--brightness` and `--contrast` flags, while the `enhance` command only needs the `--amount` flag:

我可以使用`argparse`内置模块将这些功能作为命令行工具提供。在这里，我使用`add_subparsers`功能要求根据用户指定的命令接受不同的标志集。`adjust`命令接受`--brightness`和`--contrast`标志，而`enhance`命令只需要`--amount`标志：

```
# parser.py
import argparse

PARSER = argparse.ArgumentParser()
PARSER.add_argument("file")

sub_parsers = PARSER.add_subparsers(dest="command")

enhance_parser = sub_parsers.add_parser("enhance")
enhance_parser.add_argument("--amount", type=float)

adjust_parser = sub_parsers.add_parser("adjust")
adjust_parser.add_argument("--brightness", type=float)
adjust_parser.add_argument("--contrast", type=float)
```

In the `main` function, I parse the arguments and then call into the `enhance` and `adjust` modules accordingly:

在`main`函数中，我解析参数然后根据情况调用`enhance`和`adjust`模块：

```
# mycli.py
import adjust
import enhance
import parser

def main():
    args = parser.PARSER.parse_args()

    if args.command == "enhance":
        enhance.do_enhance(args.file, args.amount)
    elif args.command == "adjust":
        adjust.do_adjust(args.file, args.brightness, args.contrast)
    else:
        raise RuntimeError("Not reachable")

if __name__ == "__main__":
    main()
```

Although the functionality here works well, the program is slow. For example, here I run the `enhance` command and observe that it takes over 1 second to complete:

尽管此处的功能运行良好，但程序很慢。例如，这里我运行`enhance`命令并观察到它花费超过1秒钟完成：

```
$ time python3 ./mycli.py my_file.jpg enhance --amount
...
real 0m1.089s
user 0m0.035s
sys 0m0.022s
```

The cause of this long execution time is probably the dependency on the large native image processing library in the `enhance` module. I don’t use that library for the `adjust` command, so I’d expect that it will go faster:

造成此长时间执行的原因可能是`enhance`模块中对大型本地图像处理库的依赖。我没有在`adjust`命令中使用该库，所以我期望它会更快：

```
$ time python3 ./mycli.py my_file.jpg adjust --brightness
contrast -0.1
...
real 0m1.064s
user 0m0.040s
sys 0m0.016s
```

Unfortunately, it appears the `enhance` and `adjust` commands are similarly slow. Upon closer inspection, the problem is that I’m importing all of the modules that might ever be used by the command-line tool at the top of the main module, in keeping with PEP 8 style (see Item 2: “Follow the PEP 8 Style Guide”). On start, my program pays the computational cost of preparing all functionality even when only part of it is actually used.

不幸的是，看起来`enhance`和`adjust`命令同样慢。仔细检查后，问题在于我在主模块顶部导入了所有可能会被命令行工具使用的模块，这是符合PEP 8风格的（参见条目2：“遵守PEP 8样式指南”）。在启动时，我的程序支付了准备所有功能的计算成本，即使只使用了一部分。

The CPython implementation of Python (see Item 1: “Know Which Version of Python You’re Using”) supports the `-X importtime` flag that directly measures the performance of module loading. Here, I use it to diagnose the slowness of my command-line tool:

Python 的 CPython 实现支持 `-X importtime` 标志，可以直接测量模块加载的性能。在这里，我使用它来诊断命令行工具的缓慢：

```
$ python3 -X importtime mycli.py
import time: self [us] | cumulative | imported pa
...
import time: 553 | 553 | adjust
import time: 1005348 | 1005348 | enhance
...
import time: 3347 | 14762 | parser
```

The `self` column shows how much time (in microseconds) each module took to execute all of its global statements, excluding imports. The `cumulative` column is how much time it took to load each module, including all of its dependencies. Clearly, the `enhance` module is the culprit.

`self` 列显示每个模块执行其所有全局语句所花的时间（以微秒为单位），不包括导入。`cumulative` 列是加载每个模块所需的时间，包括其所有依赖项。显然，`enhance` 模块是罪魁祸首。

One solution is to delay importing dependencies until you actually need to use them. This is possible because Python supports importing modules at runtime—inside of functions—in addition to module-scoped `import` statements at program start (see Item 122: “Know How to Break Circular Dependencies” for another use of this dynamism). Here, I modify the command-line tool to only import the `adjust` module or the enhance module inside the `main` function after the command is dispatched:

一种解决方案是在实际需要使用它们时才延迟导入依赖项。这是可能的，因为 Python 支持在运行时——在函数内部——导入模块，除了程序启动时的模块作用域 `import` 语句外（另请参见条目 122：“知道如何打破循环依赖”了解这种动态性的另一个用途）。在这里，我修改了命令行工具，仅在 `main` 函数内分派命令后导入 `adjust` 模块或 `enhance` 模块：

```
# mycli_faster.py
import parser

def main():
    args = parser.PARSER.parse_args()

    if args.command == "enhance":
        import enhance  # Changed

        enhance.do_enhance(args.file, args.amount)
    elif args.command == "adjust":
        import adjust   # Changed

        adjust.do_adjust(args.file, args.brightness, args.contrast)
    else:
        raise RuntimeError("Not reachable")

if __name__ == "__main__":
    main()
```

With this modification in place, the `adjust` command runs very quickly because the initialization of `enhance` can be skipped:

有了这个修改，`adjust` 命令运行得非常快，因为可以跳过 `enhance` 的初始化：

```
$ time python3 ./mycli_faster.py my_file.jpg adjust
.3 --contrast -0.1
...
real 0m0.049s
user 0m0.032s
sys 0m0.013s
```

The `enhance` command remains as slow as before:

`enhance` 命令依然像以前一样慢：

```
$ time python3 ./mycli_faster.py my_file.jpg enha
...
real 0m1.059s
user 0m0.036s
sys 0m0.014s
```

I can also use `-X importtime` to confirm that the `adjust` and enhance modules are not loaded when no command is specified:


我还可以使用 `-X importtime` 来确认在未指定命令时不会加载 `adjust` 和 `enhance` 模块：

```
$ time python3 -X importtime ./mycli_faster.py -h
import time: self [us] | cumulative | imported pa
...
import time: 1118 | 6015 | parser
...
real 0m0.049s
user 0m0.032s
sys 0m0.013s
```

Lazy-loading modules works great for command-line tools like this that carry out a single task to completion and then terminate. But what if I need to reduce the latency of cold starts in a web application? Ideally, the cost of loading the `enhance` module wouldn’t be incurred until the feature is actually requested by a user. Luckily, the same approach also works inside of request handlers. Here, I create a `flask` web application with one handler for each feature that dynamically imports the corresponding module:

对于像这样执行单个任务并随后终止的命令行工具而言，延迟加载模块效果很好。但如果我需要减少 Web 应用程序冷启动的延迟呢？理想情况下，加载 `enhance` 模块的成本直到用户实际请求该功能时才会产生。幸运的是，同样的方法也适用于请求处理程序。在这里，我创建了一个 `flask` 网络应用程序，其中每个功能都有一个处理程序，动态导入相应的模块：

```
# server.py
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/adjust", methods=["GET", "POST"])
def do_adjust():
    if request.method == "POST":
        the_file = request.files["the_file"]
        brightness = request.form["brightness"]
        contrast = request.form["contrast"]
        import adjust   # Dynamic import

        return adjust.do_adjust(the_file, brightness, contrast)
    else:
        return render_template("adjust.html")

@app.route("/enhance", methods=["GET", "POST"])
def do_enhance():
    if request.method == "POST":
        the_file = request.files["the_file"]
        amount = request.form["amount"]
        import enhance  # Dynamic import

        return enhance.do_enhance(the_file, amount)
    else:
        return render_template("enhance.html")
```

When the `do_enhance` request handler is executed in the Python process for the first time, it will import the `enhance` module and pay the high initialization cost of 1 second. On subsequent calls to `do_enhance` , the `import enhance` statement will cause the Python process to merely verify that the module has already been loaded and then assign the `enhance` identifier in the local scope to the corresponding module object.

当第一次在 Python 进程中执行 `do_enhance` 请求处理程序时，它将导入 `enhance` 模块并支付 1 秒的高初始化成本。在后续调用 `do_enhance` 时，`import enhance` 语句将导致 Python 进程仅验证该模块是否已加载，然后将局部作用域中的 `enhance` 标识符分配给相应的模块对象。

You might assume that the cost of a dynamic `import` statement is high, but it’s actually not that bad. Here, I use the `timeit` built-in module (see Item 93: “Optimize Performance-Critical Code Using `timeit` Microbenchmarks”) to measure how much time it takes to dynamically import a previously-imported module:

您可能会认为动态 `import` 语句的成本很高，但实际上并不是那么糟糕。在这里，我使用 `timeit` 内置模块（参见条目 93：“使用 `timeit` 微基准测试优化性能关键代码”）来测量动态导入先前导入模块所需的时间：

```
# import_perf.py
import timeit

trials = 10_000_000

result = timeit.timeit(
    setup="import enhance",
    stmt="import enhance",
    globals=globals(),
    number=trials,
)

print(f"{result/trials * 1e9:2.1f} nanos per call")

>>>
52.8 nanos per call
```

To put this overhead (52 nanoseconds) in perspective, here’s another example that replaces the dynamic `import` statement with a lock-protected global variable (this is a common way to prevent multiple threads from dog-piling during program initialization):

为了将此开销（52纳秒）置于上下文中，下面是一个例子，它用受锁保护的全局变量替换了动态`import`语句（这是一种防止多个线程在程序初始化期间堆积的常见方式）：

```
# global_lock_perf.py
import timeit
import threading

trials = 100_000_000

initialized = False
initialized_lock = threading.Lock()

result = timeit.timeit(
    stmt="""
global initialized
# Speculatively check without the lock
if not initialized:
    with initialized_lock:
        # Double check after holding the lock
        if not initialized:
            # Do expensive initialization
            initialized = True
""",
    globals=globals(),
    number=trials,
)

print(f"{result/trials * 1e9:2.1f} nanos per call")
>>>
5.5 nanos per call
```

The dynamic import version takes 10x more time than the approach using globals, so it’s definitely much slower. Without any lock contention——which will be the common case due to the speculative `if not initialized` statement`——the global variable version is about the same speed as adding together two integers in Python. But the dynamic import version is much simpler code that doesn’t require any boilerplate. You wouldn’t want a dynamic import to be present in CPU-bound code like a kernel function’s inner loop (see Item 94: “Know When and How to Replace Python with Another Programming Language” for details), but it seems reasonable to do it once per web request.

动态导入版本比使用全局变量的方法要慢10倍，所以它确实要慢得多。但在没有锁竞争的情况下——由于推测性的`if not initialized`语句——全局变量版本的速度与在Python中加两个整数差不多。但是动态导入版本的代码更简单，不需要任何样板代码。您不会希望在一个CPU密集型的代码中（如内核函数的内层循环中）进行动态导入（详情请参见条目94：“知道何时以及如何用其他编程语言替换Python”），但在每次网络请求中做一次似乎是合理的。

**Things to Remember**

- The CPython `-X importtime` flag causes a Python program to print out how much time it takes to load imported modules and their dependencies, making it easy to diagnose the cause of startup time slowness.
- Modules can be imported dynamically inside of a function, which makes it possible to delay the expensive initialization of dependencies until functionality actually needs to be used.
- The overhead of dynamically importing a module and checking that it was previously loaded is on the order of 20 addition operations, making it well worth the incremental cost if it can significantly improve the latency of cold starts.

**注意事项**

- CPython 的 `-X importtime` 标志会导致 Python 程序打印出加载导入模块及其依赖项所需的时间，从而轻松诊断启动时间缓慢的原因。
- 模块可以在函数内部动态导入，这使得可以延迟昂贵的依赖项初始化，直到实际需要使用功能时。
- 动态导入模块并检查其是否已先前加载的开销大约是20次加法操作，如果能够显著改善冷启动延迟的话，这点增量成本是值得的。