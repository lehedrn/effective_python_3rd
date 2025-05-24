# Chapter 11: Performance (性能)

## Item 94: Know When and How to Replace Python with Another Programming Language (知道何时以及如何用其他编程语言替代Python)

At some point while using Python you might feel that you’re pushing the envelope of what the it can do. It’s understandable, because in order to provide Python’s enhanced developer productivity and ease of use, the language’s execution model must be limiting in other ways. The CPython implementation’s bytecode virtual machine and global interpreter lock, for example, negatively impact straight-line CPU performance, CPU parallelism, program start-up time, and overall efficiency (see Item 68: “Use Threads for Blocking I/O, Avoid for Parallelism”).

在使用Python的过程中，您可能会觉得正在挑战其能力极限。这种感觉是可以理解的，因为为了提供增强的开发者生产力和易用性，Python的执行模型必然会在其他方面有所限制。例如，CPython实现的字节码虚拟机和全局解释器锁（Global Interpreter Lock）对直线型CPU性能、CPU并行性、程序启动时间和整体效率产生了负面影响（参见条目68：“为阻塞I/O使用线程，避免用于并行”）。

One potential solution is to rewrite all of your code in another programming language and move away from Python. This might be the right choice in many circumstances, including:

- Your priority is critical path latency or 99th percentile latency, and you can’t tolerate garbage collection pauses or non-deterministic data structure behaviors (such as dictionary resizes).
- You care a lot about program start-up delay, and techniques like precompilation, zip imports, and late module loading fall short (see Item 97: “Rely on Precompiled Bytecode and File System Caching to Improve Startup Time” and Item 98: “Lazy-load Modules with Dynamic Imports to Reduce Startup Time”).
- You need to take advantage of libraries with APIs that are tightly coupled to an implementation language, such as platform-specific GUI frameworks, and it’s impractical to bridge through C extensions (see details below).
- You need to target uncommon architectures like supercomputers or embedded systems, and the Python packages that support these environments (such as `https://mpi4py.github.io` and `https://micropython.org`) are insufficient.
- You need to distribute your program as an installable executable, and bundling tools (see Item 125: “Prefer Open Source Projects for Bundling Python Programs Over `zipimport` and `zipapp` ”) don’t meet your requirements.
- You’ve tried all of the optimization techniques listed below, as well as alternative implementations of the Python language that can achieve better performance (such as [PyPy](https://www.pypy.org)), and you’re still hitting a performance ceiling.
- You’ve tried to distribute computation across many Python processes on the same machine (see Item 79: “Consider `concurrent.futures` for True Parallelism”) or spanning multiple computers using tools like [Dask](https://www.dask.org) to no avail.

一种可能的解决方案是将所有代码重写为另一种编程语言并远离Python。这可能是许多情况下的正确选择，包括：

- 您关注的是关键路径延迟或第99百分位延迟，而无法容忍垃圾回收暂停或非确定性数据结构行为（如字典调整大小）。
- 您非常关心程序启动延迟，而预编译、zip导入和延迟模块加载等技术无法满足需求（参见条目97：“依赖预编译字节码和文件系统缓存以改善启动时间”和条目98：“使用动态导入进行懒加载以减少启动时间”）。
- 您需要利用与特定实现语言紧密耦合的库API，例如平台相关的GUI框架，并且通过C扩展桥接不切实际（详情见下文）。
- 您需要针对超级计算机或嵌入式系统等不常见架构，并且支持这些环境的Python包（如 `https://mpi4py.github.io` 和 `https://micropython.org`）不足。
- 您需要将程序分发为可安装的可执行文件，而打包工具（参见条目125：“对于捆绑Python程序，优先考虑开源项目而不是`zipimport`和`zipapp`”）无法满足您的需求。
- 您已经尝试了下面列出的所有优化技术，以及可以实现更好性能的Python语言替代实现（如 [PyPy](https://www.pypy.org)），但仍然遇到了性能瓶颈。
- 您已经尝试在同一台机器上使用多个Python进程（参见条目79：“考虑使用`concurrent.futures`来实现真正的并行”）或使用像 [Dask](https://www.dask.org) 这样的工具跨多台计算机分布计算，但未取得成效。

However, before you commit to a full rewrite of the software you’ve built, it’s important to consider doing pinpointed optimizations using a variety of techniques, which each have unique trade-offs. What’s possible largely depends on how much Python code you have, how complex it is, the constraints you’re under, and the requirements you need to satisfy.

然而，在决定完全重写所构建的软件之前，重要的是考虑使用一系列有针对性的优化技术，每种技术都有独特的权衡。可能性很大程度上取决于您拥有多少Python代码、其复杂程度、所面临的约束条件以及需要满足的需求。

The cause of many performance issues in Python programs is non-obvious. It’s important to profile and benchmark your code (see Item 92: “Profile Before Optimizing” and Item 93: “Optimize Performance-Critical Code Using `timeit` Microbenchmarks”) to find the true source of slowness or excess memory consumption (see Item 115: “Use `tracemalloc` to Understand Memory Usage and Leaks”). You should also seriously investigate replacing your program’s core algorithms and data structures with better alternatives (see Item 103: “Know How to Use `heapq` for Priority Queues” and Item 102: “Consider Searching Sorted Sequences with `bisect` ”), which can improve program performance by many orders of magnitude with surprisingly little effort.

Python程序中许多性能问题的原因并不明显。重要的是要对代码进行剖析和基准测试（参见条目92：“优化前先进行剖析”和条目93：“使用`timeit`微基准测试优化性能关键代码”），以找到缓慢或过度内存消耗的真正来源（参见条目115：“使用`tracemalloc`了解内存使用和泄漏”）。您还应认真研究替换程序核心算法和数据结构的最佳替代方案（参见条目103：“知道如何使用`heapq`实现优先队列”和条目102：“考虑使用`bisect`搜索已排序序列”），这可以用令人惊讶的少量努力提高程序性能几个数量级。

Once you’ve fully exhausted these paths, migrating to another programming language or execution model can be achieved in many ways. For example, a common source of performance problems in Python is tight loops, which you often see in mathematical kernel functions. The following code, which computes the dot product of two vectors, will run orders of magnitude slower in Python compared to similar behavior implemented in C:

一旦您彻底穷尽了这些途径，迁移到另一种编程语言或执行模型可以通过多种方式实现。例如，Python中的一个常见的性能问题源是紧循环，这在数学内核函数中经常看到。以下代码计算两个向量的点积，相比在C中实现的类似行为，它在Python中运行的速度会慢几个数量级：

```
def dot_product(a, b):
    result = 0
    for i, j in zip(a, b):
        result += i * j
    return result

print(dot_product([1, 2], [3, 4]))

>>>
11
```

Luckily, kernel functions like this also define a clear interface that can serve as a seam between the slow and fast parts of a program. If you can find a way to accelerate the interior implementation of the `dot_product` function, then all of its callers can benefit without having to make any other changes to the codebase. The same approach also works for much larger subcomponents if your program’s structure is amenable. The standard version of Python (see Item 1: “Know Which Version of Python You’re Using”) provides two tools to help improve performance in this way:

- The `ctypes` built-in module makes it easy to describe the interface of native libraries on your system and call the functions they export (see Item 95: “Consider `ctypes` to Rapidly Integrate with Native Libraries” for details). These libraries can be implemented in any language that’s compatible with the C calling convention (e.g., C, C++, Rust) and can leverage native threads, SIMD intrinsics, GPUs, etc. No additional build system, compiler, or packaging is required.
- The Python C extension API allows you to create fully Pythonic APIs——taking advantage of all of Python’s dynamic features——that are actually implemented in C to achieve better performance (see Item 96: “Consider Extension Modules to Maximize Performance and Ergonomics” for details). This approach often requires more work upfront, but it provides vastly improved ergonomics. However, you’ll have to deal with additional build complexities, which can be difficult. The larger Python ecosystem has also responded to the need for performance optimization by creating excellent libraries and tools. Here are a few highlights you should know about, but there are many others (see Item 116: “Know Where to Find Community-Built Modules”):
- The NumPy module (`https://numpy.org`) enables you to operate on arrays of values with ergonomic Python function calls that, under the covers, use the BLAS (Basic Linear Algebra Subprograms) to achieve high performance and CPU parallelism. You’ll need to rewrite some of your data structures in order to use it, but the speedups can be enormous.
- The Numba module (`https://numba.pydata.org`) takes your existing Python functions and JIT (just-in-time) compiles them at runtime into highly optimized machine instructions. Some of your code might need to be slightly modified to use less dynamism and simpler data types. Like `ctypes` , Numba avoids additional build complexity, which is a huge benefit.
- The Cython tool (`https://cython.org`) provides a superset of the Python language with extra features that make it easy to create C extension modules without actually writing C code. It shares the build complexity of standard C extensions, but can be much easier than using the Python C API directly.
- Mypyc (`https://github.com/mypyc/mypyc`) is similar to Cython, but it uses standard annotations from the `typing` module (see Item 124: “Consider Static Analysis via `typing` to Obviate Bugs”) instead of requiring non￾standard syntax. This can make it easier to adopt without code changes. It can also AOT (ahead-of-time) compile whole programs for faster start-up time. Mypyc has similar build complexity to C extensions and doesn’t include Cython’s C integration features.
- The CFFI module (`https://cffi.readthedocs.io`) is similar to the `ctypes` built-in module, except that it can read C header files directly in order to understand the interface of functions you want to call. This automatic mapping significantly reduces the developer toil of calling into native libraries that contain a lot of functions and data structures.
- SWIG (`https://www.swig.org`) is a tool that can automatically generate Python interfaces for C and C++ native libraries. It’s similar to CFFI in this way, but the translation happens explicitly instead of at runtime, which can be more efficient. SWIG supports other target languages besides Python and a variety of customization options. It also requires build complexity like C extensions.

幸运的是，这样的内核函数也定义了一个清晰的接口，可以在程序的慢速和快速部分之间作为一个分界点。如果您能找到一种方法加速`dot_product`函数的内部实现，那么所有调用者都可以受益，而无需对代码库进行任何其他更改。如果程序结构合适，同样的方法也适用于更大的子组件。标准版本的Python（参见条目1：“知道您使用的Python版本”）提供了两种工具，可以帮助以这种方式提高性能：

- `ctypes`内置模块使得描述系统上本地库的接口并调用它们导出的函数变得简单（参见条目95：“考虑`ctypes`快速集成本地库”详细信息）。这些库可以用任何兼容C调用约定的语言实现（例如C、C++、Rust），并且可以利用原生线程、SIMD内在函数、GPU等。不需要额外的构建系统、编译器或打包。
- Python C扩展API允许您创建完全Pythonic的API——充分利用Python所有动态特性——实际上是在C中实现的，从而获得更好的性能（参见条目96：“考虑扩展模块以最大化性能和用户体验”详细信息）。这种方法通常需要更多的前期工作，但它提供了显著改进的用户体验。但是，您必须处理额外的构建复杂性，这可能很困难。更大的Python生态系统也通过创建优秀的库和工具来响应性能优化的需求。以下是几个您应该知道的重点内容（但还有更多，参见条目116：“知道在哪里找到社区构建的模块”）：
  - NumPy模块 (`https://numpy.org`) 允许您使用数组操作值，通过用户友好的Python函数调用，实际上使用BLAS（基本线性代数子程序）来实现高性能和CPU并行性。您需要重写一些数据结构才能使用它，但速度提升可能是巨大的。
  - Numba模块 (`https://numba.pydata.org`) 接受现有的Python函数并在运行时将其即时（JIT）编译成高度优化的机器指令。有些代码可能需要稍作修改以使用较少的动态性和更简单的数据类型。与`ctypes`一样，Numba避免了额外的构建复杂性，这是一个巨大的优势。
  - Cython工具 (`https://cython.org`) 提供了Python语言的一个超集，具有额外的功能，使其易于创建C扩展模块，而无需实际编写C代码。它与标准C扩展共享构建复杂性，但相比直接使用Python C API可能更容易。
  - Mypyc (`https://github.com/mypyc/mypyc`) 类似于Cython，但它使用`typing`模块的标准注释（参见条目124：“考虑通过`typing`进行静态分析以消除错误”），而不需要非标准语法。这可以使采用更加容易而不改变代码。它还可以提前（AOT）编译整个程序以加快启动时间。Mypyc的构建复杂性类似于C扩展，不包含Cython的C集成功能。
  - CFFI模块 (https://cffi.readthedocs.io) 类似于`ctypes`内置模块，不同之处在于它可以直接读取C头文件以了解您想要调用的函数接口。这种自动映射显著减少了调用包含大量函数和数据结构的本地库所需的开发工作。
  - SWIG (https://www.swig.org) 是一个工具，可以自动生成C和C++本地库的Python接口。在这方面它类似于CFFI，但翻译是在显式而非运行时发生，这可能更高效。SWIG除了Python之外还支持其他目标语言和各种定制选项。它也需要像C扩展一样的构建复杂性。

One important caveat to note is that these tools and libraries might require a non-trivial amount of developer time to learn and use effectively. It might be easier to rewrite components of a program from scratch in another language, especially given how great Python is at gluing systems together. You can use what you learned from building the Python implementation to inform the design of the rewrite.

需要注意的一个重要警告是，这些工具和库可能需要相当多的开发人员时间来学习和有效使用。从头开始重写程序的某些组件可能更容易，尤其是考虑到Python在粘合系统方面的卓越能力。您可以利用从构建Python实现中学到的知识来指导重写的设计。

That said, rewriting any of your Python code in C (or another language) also has a high cost. Code that is short and understandable in Python can become verbose and complicated in other languages. Porting also requires extensive testing to ensure that the functionality remains equivalent to the original Python code and that no bugs have been introduced.

尽管如此，将任何Python代码重写为C（或其他语言）也有很高的成本。在Python中简短且易于理解的代码可能在其他语言中变得冗长且复杂。移植还需要广泛的测试，以确保功能与原始Python代码保持一致，并且没有引入任何错误。

Sometimes rewrites are worth it, which explains the large ecosystem of C extension modules in the Python community that speed up things like text parsing, image compositing, and matrix math. For your own code, you’ll need to consider the risks vs. the potential rewards and decide on the best trade-off that’s unique to you.

有时重写是值得的，这就解释了为什么Python社区中存在大量的C扩展模块生态系统，这些模块加速了文本解析、图像合成和矩阵数学等任务。对于您自己的代码，您需要权衡风险与潜在回报，并决定最适合您的折衷方案。

**Things to Remember**

- There are many valid reasons to rewrite Python code in another language, but you should investigate all of the optimization techniques available before pursuing that option.
- Moving CPU bottlenecks to C extension modules and native libraries can be an effective way to improve performance while maximizing your investment in Python code. However, doing so has a high cost and may introduce bugs.
- There are a large number of tools and libraries available in the Python ecosystem that can accelerate the slow parts of a Python program with surprisingly few changes.

**注意事项**

- 有很多合理的原因将Python代码重写为另一种语言，但在追求该选项之前，应调查所有可用的优化技术。
- 将CPU瓶颈移动到C扩展模块和本地库中可以是一种有效的提高性能的方法，同时最大化您对Python代码的投资。然而，这样做成本高昂，可能会引入错误。
- Python生态系统中有大量可用的工具和库，可以用惊人的少量更改来加速Python程序的缓慢部分。