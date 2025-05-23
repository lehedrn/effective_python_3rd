# Chapter 9: Concurrency and Parallelism  (并发与并行)

## Item 79: Consider `concurrent.futures` for True Parallelism (考虑使用`concurrent.futures`实现真正的并行化)

At some point in writing Python programs, you might hit the performance wall. Even after optimizing your Python code (see Item 92: “Profile Before Optimizing”), your program’s execution might still be too slow for your needs. On modern computers that have an increasing number of CPU cores, it’s reasonable to assume that one solution could be parallelism. What if you could split your code’s computation into independent pieces of work that run simultaneously across multiple CPU cores?

在编写Python程序的过程中，你可能会遇到性能瓶颈。即使在优化了Python代码之后（参见条目92：“优化前先进行性能分析”），程序的执行速度可能仍然无法满足需求。在现代拥有越来越多CPU核心的计算机上，一个合理的解决方案可能是并行化。如果可以将程序的计算任务拆分成独立的工作块，并在多个CPU核心上同时运行，那会怎样呢？

Unfortunately, Python’s global interpreter lock (GIL) prevents true CPU parallelism in Python threads in most cases (see Item 68: “Use Threads for Blocking I/O, Avoid for Parallelism”). But the `multiprocessing` built-in module, which is easily accessed via the `concurrent.futures` built-in module, might be exactly what you need (see Item 74: “Consider `ThreadPoolExecutor` When Threads Are Necessary for Concurrency” for a related example). `multiprocessing` enables Python to utilize multiple CPU cores in
parallel by running additional interpreters as child processes. These child processes are separate from the main interpreter, so their global interpreter locks are also separate. Each child can fully utilize one CPU core. Each child also has a link to the main process where it receives instructions to do computation and returns results.

不幸的是，在大多数情况下，Python的全局解释器锁（GIL）阻止了Python线程中的真正CPU并行化（参见条目68：“对阻塞I/O使用线程，避免用于并行化”）。但是，通过 `concurrent.futures` 内置模块很容易访问的 `multiprocessing` 内置模块，可能正是你需要的（参见条目74：“在线程必要时使用`ThreadPoolExecutor`进行并发”以获取相关示例”）。 `multiprocessing` 使得Python能够通过作为子进程运行额外的解释器来利用多个CPU核心。这些子进程与主解释器分离，因此它们的全局解释器锁也是分开的。每个子进程都可以完全利用一个CPU核心。每个子进程也都有一个链接到主进程的地方，从那里接收执行计算的指令并返回结果。

For example, say that I want to do something computationally intensive with Python and utilize multiple CPU cores. I’ll use an implementation of finding the greatest common divisor of two numbers as a proxy for a more computationally intense algorithm (like simulating fluid dynamics with the Navier-Stokes equation):

例如，假设我想用Python做一些计算密集型的事情并利用多个CPU核心。我将使用查找两个数的最大公约数的实现作为更复杂算法的代理（比如用纳维-斯托克斯方程模拟流体动力学）：

```
# my_module.py
def gcd(pair):
    a, b = pair
    low = min(a, b)
    for i in range(low, 0, -1):
        if a % i == 0 and b % i == 0:
            return i
    raise RuntimeError("Not reachable")
```

Running this function in serial takes a linearly increasing amount of time because there is no parallelism:

按顺序运行此函数需要线性增加的时间，因为没有并行性：

```
# run_serial.py
import my_module
import time

NUMBERS = [
    (19633090, 22659730),
    (20306770, 38141720),
    (15516450, 22296200),
    (20390450, 20208020),
    (18237120, 19249280),
    (22931290, 10204910),
    (12812380, 22737820),
    (38238120, 42372810),
    (38127410, 47291390),
    (12923910, 21238110),
]

def main():
    start = time.perf_counter()
    results = list(map(my_module.gcd, NUMBERS))
    end = time.perf_counter()
    delta = end - start
    print(f"Took {delta:.3f} seconds")

if __name__ == "__main__":
    main()

>>>
Took 5.643 seconds
```

Running this code on multiple Python threads will yield no speed improvement because the GIL prevents Python from using multiple CPU cores in parallel. Here, I do the same computation as above using the `concurrent.futures` module with its `ThreadPoolExecutor` class and eight worker threads (to match the number of CPU cores on my computer):

由于GIL防止Python并行使用多个CPU核心，因此使用多个Python线程运行此代码不会带来任何速度提升。这里，我使用`concurrent.futures`模块及其`ThreadPoolExecutor`类和八个工作者线程（与我的计算机上的CPU核心数量匹配）完成了上面的相同计算：

```
# run_threads.py
import my_module
from concurrent.futures import ThreadPoolExecutor
import time

NUMBERS = [
    (19633090, 22659730),
    (20306770, 38141720),
    (15516450, 22296200),
    (20390450, 20208020),
    (18237120, 19249280),
    (22931290, 10204910),
    (12812380, 22737820),
    (38238120, 42372810),
    (38127410, 47291390),
    (12923910, 21238110),
]

def main():
    start = time.perf_counter()
    pool = ThreadPoolExecutor(max_workers=8)
    results = list(pool.map(my_module.gcd, NUMBERS))
    end = time.perf_counter()
    delta = end - start
    print(f"Took {delta:.3f} seconds")

if __name__ == "__main__":
    main()
>>>
Took 5.810 seconds
```

It’s even slower this time because of the overhead of starting and communicating with the pool of threads.

这次甚至更慢了，这是由于启动和与线程池通信的开销所致。

Now for the surprising part: Changing a single line of code causes something magical to happen. If I replace the `ThreadPoolExecutor` with the `ProcessPoolExecutor` from the `concurrent.futures` module, everything speeds up:

现在是令人惊讶的部分：改变一行代码会导致神奇的事情发生。如果我用`concurrent.futures`模块中的`ProcessPoolExecutor`替换`ThreadPoolExecutor`，一切都加快了：

```
# run_parallel.py
import my_module
from concurrent.futures import ProcessPoolExecutor
import time

NUMBERS = [
    (19633090, 22659730),
    (20306770, 38141720),
    (15516450, 22296200),
    (20390450, 20208020),
    (18237120, 19249280),
    (22931290, 10204910),
    (12812380, 22737820),
    (38238120, 42372810),
    (38127410, 47291390),
    (12923910, 21238110),
]

def main():
    start = time.perf_counter()
    pool = ProcessPoolExecutor(max_workers=8)  # The one change
    results = list(pool.map(my_module.gcd, NUMBERS))
    end = time.perf_counter()
    delta = end - start
    print(f"Took {delta:.3f} seconds")

if __name__ == "__main__":
    main()
>>>
Took 1.684 seconds
```

Running on my multi-core machine, this is significantly faster! How is this possible? Here’s what the `ProcessPoolExecutor` class actually does (via the low-level constructs provided by the `multiprocessing` module):

1. It takes each item from the `numbers` input data to `map` .
2. It serializes the item into binary data by using the `pickle` module (see Item 106: “Make `pickle` Reliable with `copyreg` ”).
3. It copies the serialized data from the main interpreter process to a child interpreter process over a local socket.
4. It deserializes the data back into Python objects, using `pickle` in the child process.
5. It then imports the Python module containing the `gcd` function.
6. It runs the function on the input data in parallel with other child processes.
7. It serializes the result back into binary data.
8. It copies that binary data back through the socket.
9. It deserializes the binary data back into Python objects in the parent process.
10. It merges the results from multiple children into a single `list` to return.

在我的多核机器上运行，这明显更快！这是如何实现的？以下是`ProcessPoolExecutor`类实际做的事情（通过`multiprocessing`模块提供的低级构造）：

1. 它从提供给`map`的输入数据中取出每一项。
2. 使用`pickle`模块（参见条目106：“使用`copyreg`使`pickle`可靠”）将其序列化为二进制数据。
3. 通过本地套接字将序列化的数据从主解释器进程复制到子解释器进程。
4. 在子进程中使用`pickle`将数据反序列化回Python对象。
5. 然后导入包含`gcd`函数的Python模块。
6. 在其他子进程中并行地在输入数据上运行该函数。
7. 将结果再次序列化为二进制数据。
8. 通过套接字将该二进制数据复制回来。
9. 在父进程中使用`pickle`将二进制数据反序列化回Python对象。
10. 将来自多个子进程的结果合并成一个`list`返回。

Although it looks simple to the programmer, the `multiprocessing` module and `ProcessPoolExecutor` class do a huge amount of work to make parallelism possible. In most other languages, the only touch point you need to coordinate two threads is a single lock or atomic operation (see Item 69: “Use Lock to Prevent Data Races in Threads” for an example). The overhead of using `multiprocessing` via `ProcessPoolExecutor` is high because of all of the serialization and deserialization that must happen between the parent and child processes.

虽然对于程序员来说看起来很简单，但`multiprocessing`模块和`ProcessPoolExecutor`类做了大量的工作以实现并行化。在大多数其他语言中，协调两个线程所需的唯一触点是一个单独的锁或原子操作（参见条目69：“使用Lock防止线程中的数据竞争”以获取示例）。通过`ProcessPoolExecutor`使用`multiprocessing`的开销很高，因为必须在父进程和子进程之间进行所有这些序列化和反序列化。

This scheme is well suited to certain types of isolated, high-leverage tasks. By isolated, I mean functions that don’t need to share state with other parts of the program. By high-leverage, I mean situations in which only a small amount of data must be transferred between the parent and child processes to enable a large amount of computation. The greatest common divisor algorithm is one example of this, but many other mathematical algorithms work similarly.

这种方案非常适合某些类型的孤立、高杠杆任务。所谓孤立，是指那些不需要与其他程序部分共享状态的函数。所谓高杠杆，是指父进程和子进程之间只需要传输少量数据即可启用大量计算的情况。最大公约数算法就是这样一个例子，但许多其他数学算法也类似。

If your computation doesn’t have these characteristics, then the overhead of `ProcessPoolExecutor` may prevent it from speeding up your program through parallelization. When that happens, `multiprocessing` provides more advanced facilities for shared memory, cross-process locks, queues, and proxies. But all of these features are very complex. It’s hard enough to reason about such tools in the memory space of a single process shared between Python threads. Extending that complexity to other processes and involving sockets makes this much more difficult to understand.

如果你的计算不具备这些特点，那么`ProcessPoolExecutor`的开销可能会妨碍通过并行化来提高程序的速度。当这种情况发生时，`multiprocessing`提供了更高级的设施，如共享内存、跨进程锁、队列和代理。但所有这些功能都非常复杂。在一个由Python线程共享的内存空间中思考这样的工具已经足够困难了。扩展到其他进程并涉及套接字会使理解变得更加困难。

I suggest that you initially avoid all parts of the `multiprocessing` built-in module. You can start by using the `ThreadPoolExecutor` class to run isolated, high-leverage functions in threads. Later you can move to the `ProcessPoolExecutor` to get a speedup. Finally, when you’ve completely exhausted the other options, you can consider using the `multiprocessing` module directly, or more advanced techniques (see Item 94: “Know When and How to Replace Python with Another Programming Language”).

我建议你最初避免使用`multiprocessing`内置模块的所有部分。你可以首先使用`ThreadPoolExecutor`类在线程中运行孤立、高杠杆的函数。随后你可以转向`ProcessPoolExecutor`以获得速度提升。最后，当你彻底耗尽了其他所有选项时，才可以考虑直接使用`multiprocessing`模块，或者更高级的技术（参见条目94：“知道何时以及如何用另一种编程语言替换Python”）。

**Things to Remember**
- The `multiprocessing` module provides powerful tools that can parallelize certain types of Python computation with minimal effort.
- The power of `multiprocessing` is best accessed through the `concurrent.futures` built-in module and its simple `ProcessPoolExecutor` class.
- Avoid the advanced (and complicated) parts of the `multiprocessing` module until you’ve exhausted all other options.

**注意事项**

- `multiprocessing`模块提供了强大的工具，可以在最小努力下并行化某些类型的Python计算。
- `multiprocessing`的强大功能最好通过`concurrent.futures`内置模块及其简单的`ProcessPoolExecutor`类来访问。
- 在你耗尽所有其他选项之前，应避免使用`multiprocessing`模块的高级（且复杂的）部分。