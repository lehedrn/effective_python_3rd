# Chapter 11: Performance (性能)

## Item 97: Rely on Precompiled Bytecode and File System Caching to Improve Startup Time (依赖预编译字节码和文件系统缓存来改善启动时间)

Program startup time is an important performance metric to examine because it's directly observable by users. For command-line utilities, the startup time is how long it takes for a program to begin processing after you've pressed the enter key. Users often execute the same command-line tools repeatedly in rapid succession, so the accumulation of startup delays can feel like a frustrating waste of time. For a web server, the startup time is how long it takes to begin processing the first incoming request after program launch. Web servers often use multiple threads or child processes to parallelize work, which can cause a cold start delay each time a new context is spun up. The end result is that some web requests can take a lot longer than others, annoying users with unpredictable delays.

程序的启动时间是一个重要的性能指标，因为它直接由用户观察到。对于命令行工具来说，启动时间是你按下回车键后程序开始处理所需的时间。用户经常快速连续地执行相同的命令行工具，因此启动延迟的累积可能会让人感到沮丧的浪费时间。对于Web服务器来说，启动时间是程序启动后开始处理第一个传入请求所需的时间。Web服务器通常使用多个线程或子进程来并行化工作，这可能导致每次新上下文被创建时都会出现冷启动延迟。最终结果是一些Web请求可能比其他请求花费更长的时间，从而让用户感到不可预测的延迟。

Unfortunately, Python programs usually have a high startup time compared to languages that are compiled into machine code executables. There are two main contributors to this slowness in the CPython implementation of Python (see Item 1: “Know Which Version of Python You’re Using”). First, on startup, CPython will read the source code for the program and compile it into bytecode for its virtual machine interpreter, which requires both I/O and CPU processing (see Item 68: “Use Threads for Blocking I/O, Avoid for Parallelism” for details). Second, after the bytecode is ready, Python will execute all of the modules imported by the main entry point. Loading modules requires running code to initialize global variables and constants, define classes, execute assertion statements, etc——it can be a lot of work.

不幸的是，与那些被编译为机器代码可执行文件的语言相比，Python程序通常具有较高的启动时间。在CPython实现中（见条目1：“了解你使用的Python版本”），这种缓慢主要有两个原因。首先，在启动时，CPython会读取程序的源代码并将其编译成其虚拟机解释器使用的字节码，这需要I/O和CPU处理（详情请参见条目68：“对阻塞I/O使用线程，避免用于并行化”）。其次，在字节码准备就绪后，Python会执行主入口点导入的所有模块。加载模块需要运行代码以初始化全局变量和常量、定义类、执行断言语句等——这可能是一项繁重的工作。

To improve performance, modules are cached in memory after the first time they're loaded by a program and reused for subsequent loads (see Item 122: “Know How to Break Circular Dependencies” for details). CPython will also save the bytecode it generates during compilation to a cache on disk so it can be reused for subsequent program starts. The cache is stored in a directory called `__pycache__` next to the source code. Each bytecode file has a `.pyc` suffix and is usually smaller than the corresponding source file.

为了提高性能，模块在第一次被程序加载后会被缓存在内存中，并在后续加载时重复使用（详见条目122：“知道如何打破循环依赖”）。CPython还会将编译过程中生成的字节码保存到磁盘上的缓存中，以便后续程序启动时可以重复使用。缓存存储在一个名为`__pycache__`的目录中，该目录位于源代码旁边。每个字节码文件都有`.pyc`后缀，通常比相应的源文件小。

It's easy to see the effect of bytecode caching in action. For example, here I load all of the modules from the Django web framework (`https://www.djangoproject.com`) and measure how long it takes (specifically, the "real" time). This is a source-code only snapshot of the open source project, and no bytecode cache files are present:

很容易看到字节码缓存的效果。例如，这里我加载了Django Web框架中的所有模块（`https://www.djangoproject.com`）并测量了耗时（具体来说，是“实际”时间）。这是一个仅包含源代码的开源项目的快照，且没有字节码缓存文件：

```
$ time python3 -c 'import django_all'
...
real 0m0.791s
user 0m0.495s
sys 0m0.145s
```

If I run the same program again with absolutely no modifications, it starts up in 70% less time than before—over 3x faster:

如果我在不做任何修改的情况下再次运行相同的程序，它的启动时间比之前少了70%——速度提高了3倍多：

```
$ time python3 -c 'import django_all'
...
real 0m0.225s
user 0m0.182s
sys 0m0.038s
```

You might guess that this performance improvement is due to CPython using the bytecode cache the second time that the program starts. However, if I remove the `.pyc` files, performance is surprisingly still better than the first time I executed Python and imported this module:

你可能会猜测这次性能提升是因为CPython在第二次启动程序时使用了字节码缓存。然而，如果我删除`.pyc`文件，令人惊讶的是性能仍然比第一次执行Python并导入此模块时更好：

```
$ find django -name '*.pyc' -delete
$ time python3 -c 'import django_all'
real 0m0.613s
user 0m0.502s
sys 0m0.101s
```

This is a good example of why measuring performance is difficult and the effect of optimizations can be confusing. What caused the subsequent Python invocation without `.pyc` files to be faster is the filesystem cache of my operating system. The Python source code files are already in memory because I recently accessed them. When I load them again, expensive I/O operations can be shortened, speeding up program start.

这是一个很好的例子，说明为什么衡量性能是困难的，以及优化效果可能令人困惑。导致随后不带`.pyc`文件的Python调用更快的原因是我操作系统的文件系统缓存。Python源代码文件已经存在于内存中，因为我最近访问过它们。当我再次加载它们时，昂贵的I/O操作可以缩短，从而加快程序启动速度。

I can regenerate the bytecode files by using the `compileall` built-in module. This is usually done automatically when you install packages with `pip` (see Item 117: “Use Virtual Environments for Isolated and Reproducible Dependencies”) to minimize startup time. But you can create new bytecode files manually for your own codebase when needed (e.g., before deploying to production):

我可以使用内置的`compileall`模块重新生成字节码文件。这通常在使用`pip`安装包时自动完成（见条目117：“使用虚拟环境进行隔离和可重现的依赖项”），以最小化启动时间。但在必要时（例如，在部署到生产环境之前），你可以手动为自己的代码库创建新的字节码文件：

```
$ python3 -m compileall django
Listing 'django'...
Compiling 'django/__init__.py'...
Compiling 'django/__main__.py'...
Listing 'django/apps'...
Compiling 'django/apps/__init__.py'...
Compiling 'django/apps/config.py'...
Compiling 'django/apps/registry.py'...
...
```

Most operating systems provide a way to purge the file system cache, which will cause subsequent I/O operations to go to the physical disk instead of memory. Here, I force the cache to be empty (using the `purge` command) and then re-run the `django_all` import to see the performance impact of having bytecode files on disk and not in memory:

大多数操作系统提供了一种清除文件系统缓存的方法，这将导致后续的I/O操作转而访问物理磁盘而不是内存。在这里，我强制缓存为空（使用`purge`命令），然后重新运行`django_all`导入以查看磁盘上存在字节码但不在内存中的性能影响：

```
$ sudo purge
$ time python3 -c 'import django_all'
...
real 0m0.382s
user 0m0.169s
sys 0m0.085s
```

This startup time (382 milliseconds) is faster than having no bytecode and an empty filesystem cache (791 milliseconds), faster that having no bytecode and the source code cached in memory (613 milliseconds), but slower than having both bytecode and source code in memory (225 milliseconds). Ultimately, you'll get the best startup performance by ensuring your bytecode is precompiled and in the filesystem cache. For this reason, it can be valuable to put Python programs on a RAM disk so they are always in memory regardless of access patterns. The effect of this will be even more pronounced when your computer has a spinning disk—I used an SSD (solid-state drive) in these tests. When caching in memory is not possible, other approaches to reduce startup time might be valuable (see Item 98: “Lazy-load Modules with Dynamic Imports to Reduce Startup Time”).

这次启动时间（382毫秒）比没有字节码且文件系统缓存为空的情况（791毫秒）要快，比没有字节码且源代码缓存在内存中的情况（613毫秒）要快，但比同时有字节码和源代码在内存中的情况（225毫秒）要慢。最终，确保你的字节码已预编译并在文件系统缓存中，可以获得最佳的启动性能。出于这个原因，将Python程序放在RAM磁盘上可能是有价值的，这样无论访问模式如何，它们始终都在内存中。当计算机使用的是旋转磁盘时，这种效果会更加明显——我在这些测试中使用的是SSD（固态硬盘）。当内存缓存不可行时，减少启动时间的其他方法可能有价值（见条目98：“通过动态导入延迟加载模块以减少启动时间”）。

Finally, you might wonder if it's even faster to run a Python program without the source code files present at all, since it appears that the bytecode cache is all that CPython needs to execute a program. Indeed, this is possible. The trick is to use the `-b` flag when generating the bytecode, which causes the individual `.pyc` files to be placed next to source code instead of in `__pycache__` directories. Here, I modify the `django` package accordingly and then test importing the `django_all` module
again:

最后，你可能会想知道是否完全没有源代码文件的情况下运行Python程序会更快，因为看起来CPython只需要字节码缓存即可执行程序。确实如此。诀窍是在生成字节码时使用`-b`标志，这会导致单独的`.pyc`文件放置在源代码旁边而不是`__pycache__`目录中。在这里，我相应地修改了`django`包，然后再次测试导入`django_all`模块：

```
$ find django -name '*.pyc' -delete
$ python3 -m compileall -b django
$ find django -name '*.py' -delete
$ time python3 -c 'import django_all'
...
real 0m0.226s
user 0m0.183s
sys 0m0.037s
```

The startup time in this case (226 milliseconds) is almost exactly the same as when the source code files were also present. Thus, there's no value in deleting the source code unless you have other constraints you need to satisfy, such as minimizing overall storage or system memory use (see Item 125: “Prefer Open Source Projects for Bundling Python Programs Over `zipimport` and `zipapp` ” for an example).

在这种情况下，启动时间（226毫秒）几乎与源代码文件也存在的时候相同。因此，除非你有其他需要满足的约束条件，如最小化总体存储或系统内存使用（见条目125：“捆绑Python程序时优先选择开源项目而非`zipimport`和`zipapp`”中的示例），否则删除源代码并没有价值。

**Things to Remember**

- The CPython implementation of Python compiles a program's source files into bytecode that is then executed in a virtual machine.
- Bytecode is cached to disk, which enables subsequent runs of the same program, or loads of the same module, to avoid compiling bytecode again.
- With CPython, the best performance for program startup time is achieved when the program's bytecode files were generated in advance and they're already cached in operating system memory.

**注意事项**

- Python的CPython实现将程序的源文件编译成字节码，然后在虚拟机中执行。
- 字节码会被缓存到磁盘上，这使得同一程序的后续运行或同一模块的后续加载可以避免再次编译字节码。
- 使用CPython时，为了获得最佳的程序启动时间性能，应确保程序的字节码文件已预先生成并且已经在操作系统内存中缓存。