# Chapter 9: Concurrency and Parallelism (并发与并行)

## Item 68: Use Threads for Blocking I/O; Avoid for Parallelism (对阻塞I/O使用线程；避免用于并行处理)

The standard implementation of Python is called CPython. CPython runs a Python program in two steps. First, it parses and compiles the source text into bytecode, which is a low-level representation of the program as 8-bit instructions (see Item 98: “Rely on Precompiled Bytecode and File System Caching to Improve Startup Time” for background). (As of Python 3.6, it’s technically wordcode with 16-bit instructions, but the idea is the same.) Then, CPython runs the bytecode using a stack-based interpreter. The bytecode interpreter has state that must be maintained and coherent while the Python program executes. CPython enforces coherence with a mechanism called the global interpreter lock (GIL).

Python的标准实现称为CPython。CPython分两步运行一个Python程序。首先，它将源文本解析并编译为字节码，这是一种以8位指令表示的低级程序表示形式（从Python 3.6开始，技术上是16位指令的wordcode，但想法是一样的）。然后，CPython使用基于堆栈的解释器来运行字节码。字节码解释器在Python程序执行期间必须维护和保持一致性的一些状态。CPython通过一种称为全局解释器锁（Global Interpreter Lock，简称GIL）的机制来确保一致性。

Essentially, the GIL is a mutual-exclusion lock (mutex) that prevents CPython from being affected by preemptive multithreading, where one thread takes control of a program by interrupting another thread. Such an interruption could corrupt the interpreter state (e.g., garbage collection reference counts) if it comes at an unexpected time. The GIL prevents these interruptions and ensures that every bytecode instruction works correctly with the CPython implementation and its C-extension modules (see Item
96: “Consider Extension Modules to Maximize Performance and Ergonomics” for background).

本质上，GIL是一个互斥锁（mutex），它防止了CPython受到抢占式多线程的影响，在这种情况下，一个线程会在中断另一个线程时控制程序。如果在一个意外的时间发生这样的中断，可能会破坏解释器的状态（例如垃圾回收引用计数）。GIL可以防止这些中断，并确保每个字节码指令都能正确地与CPython实现及其C扩展模块协同工作。

The GIL has an important negative side effect. With programs written in languages like C++ or Java, having multiple threads of execution means that a program can utilize multiple CPU cores at the same time. Although Python supports multiple threads of execution, the GIL causes only one of them to ever make forward progress at a time. This means that when you reach for threads to do parallel computation and speed up your Python programs, you will be sorely disappointed.

GIL有一个重要的负面副作用。对于用C++或Java等语言编写支持多线程的程序时，拥有多个执行线程意味着程序可以同时利用多个CPU核心。尽管Python支持多线程执行，但GIL导致其中只有一个是真正向前推进的。这意味着当你希望通过线程进行并行计算并加快你的Python程序速度时，你会大失所望。

For example, say that I want to do something computationally intensive with Python. Here, I use a naive number factorization algorithm as a proxy:

比如说，我想用 Python 做一些计算量很大的事情。这里我用一个简单的数字因式分解算法来做个例子。

```
def factorize(number):
    for i in range(1, number + 1):
        if number % i == 0:
            yield i
```

Factoring a list of 16 numbers in serial takes quite a long time:

按顺序分解16个数字需要相当长的时间：

```
import time

numbers = [7775876, 6694411, 5038540, 5426782,
           9934740, 9168996, 5271226, 8288002,
           9403196, 6678888, 6776096, 9582542,
           7107467, 9633726, 5747908, 7613918]
start = time.perf_counter()

for number in numbers:
    list(factorize(number))

end = time.perf_counter()
delta = end - start
print(f"Took {delta:.3f} seconds")

>>>
Took 3.304 seconds
```

Using multiple threads to do this computation would make sense in other languages because I could take advantage of all the CPU cores of my computer. Let me try that in Python. Here, I define a Python thread for doing the same computation as before:

在其他语言中，使用多个线程来做这个计算是有意义的，因为这样可以利用计算机的所有CPU核心。让我尝试在Python中这样做。在这里，我定义了一个Python线程来完成相同的计算任务：

```
from threading import Thread

class FactorizeThread(Thread):
    def __init__(self, number):
        super().__init__()
        self.number = number

    def run(self):
        self.factors = list(factorize(self.number))
```

Then, I start a thread for each number to factorize in parallel:

然后，我为每个要分解的数字启动了一个线程：

```
start = time.perf_counter()

threads = []
for number in numbers:
    thread = FactorizeThread(number)
    thread.start()
    threads.append(thread)
```

Finally, I wait for all of the threads to finish:

最后，我等待所有线程完成：

```
for thread in threads:
    thread.join()

end = time.perf_counter()
delta = end - start
print(f"Took {delta:.3f} seconds")

>>>
Took 3.293 seconds
```

Surprisingly, this takes almost exactly the same amount of time as running `factorize` in serial. With one thread per number—again, 16 threads in total for this example—you might expect less than a 16x speedup in other languages due to the overhead of creating threads and coordinating with them. You might also expect only an 8x speedup on the 8-core machine I used to run this code. But you wouldn’t expect the performance of these threads to appear no better when there are multiple CPUs to utilize. This demonstrates the effect of the GIL (e.g., lock contention, scheduling overhead) on programs running in the standard CPython interpreter.

令人惊讶的是，这几乎与串行运行`factorize`所需时间相同。对于总共16个线程的例子，你可能期望由于创建线程和协调它们的开销而在其他语言中少于16倍的加速。你也可能在我的用来运行此代码的8核机器上期望仅8倍的加速。但是你不应该期望当有多个CPU可利用时这些线程的性能会没有提升。这展示了GIL (如锁竞争、调度开销) 对在标准CPython解释器中运行的程序的影响。

There are ways to get CPython to utilize multiple cores, but they don’t work with the standard `Thread` class (see Item 79: “Consider concurrent.futures for True Parallelism” and Item 94: “Know When and How to Replace Python with Another Programming Language”), and they can require substantial effort.

有一些方法可以让CPython利用多个核心，但它们不适用于标准的`Thread`类（参见条目79：“考虑使用concurrent.futures进行真正的并行”和条目94：“了解何时以及如何用另一种编程语言替换Python”），并且可能需要大量的努力。

---

> Note
Starting in CPython version 3.13, there is an experimental option to compile Python without the GIL, thus enabling programs to avoid its constraints. This can improve parallel performance with multiple threads, but there are significant downsides: many C-extension modules and common libraries aren’t yet compatible with this behavior; and the straight-line performance of individual threads is reduced because of synchronization overhead. It will be interesting to see how this experiment develops in subsequent releases.

> 注意
从CPython版本3.13开始，提供了一种实验性选项来编译没有GIL的Python，从而避免其约束。这可以改善多线程程序的并行性能，但也存在显著的缺点：许多C扩展模块和常用库尚不兼容此行为；并且由于同步开销，单个线程的直线性能会降低。看看这个实验在后续版本中的发展将会很有趣。

---

Given these limitations, why does Python support threads at all? There are two good reasons.

鉴于这些限制，为什么Python还支持线程呢？有两个好的理由。

First, multiple threads make it easy for a program to seem like it’s doing multiple things at the same time. Managing the juggling act of simultaneous tasks is difficult to implement yourself (see Item 71: “Know How to Recognize When Concurrency Is Necessary” for an example). With threads, you can leave it to Python to run your functions concurrently. This works because CPython ensures a level of fairness between Python threads of execution, even though only one of them makes forward progress at a time due to the GIL.

第一，多线程使得程序看起来像是在同时做多件事情。管理并发任务的复杂性很难自己实现（例如，见条目71：“知道如何识别何时需要并发”）。有了线程，你可以让Python为你并发运行函数。即使由于GIL的原因，只有其中一个能向前推进，CPython确保了Python执行线程之间一定层次的公平性，这也使其可行。

The second reason Python supports threads is to deal with blocking I/O, which happens when Python does certain types of system calls. A Python program uses system calls to ask the computer’s operating system to interact with the external environment on its behalf. Blocking I/O includes things like reading and writing files, interacting with networks, communicating with devices like displays, and so on. Threads help handle blocking I/O by insulating a program from the delay required for the operating system to respond to requests.

第二个原因，Python支持线程是为了处理阻塞I/O，这发生在Python执行某些类型的系统调用时。Python程序使用系统调用来请求操作系统的帮助与其外部环境交互。阻塞I/O包括读写文件、与网络交互、与显示器等设备通信等。线程通过隔离程序免受操作系统响应请求所需的延迟之苦，有助于处理阻塞I/O。

For example, say that I want to send a signal to a radio-controlled helicopter through a serial port. I’ll use a slow system call ( `select` ) as a proxy for this activity. This function asks the operating system to block for 0.1 seconds and then return control to my program, which is similar to what would happen when using a synchronous serial port:

例如，假设我想通过一个串口向无线电控制的直升机发送信号。我会使用一个慢速系统调用(`select`)作为这项活动的替代。该函数请求操作系统阻塞0.1秒，然后返回控制权给我的程序，类似于使用同步串口时会发生的情况：

```
import select
import socket

def slow_systemcall():
    select.select([socket.socket()], [], [], 0.1)
```

Running this system call in serial requires a linearly increasing amount of time—5 calls takes about 0.5 seconds:

串行运行这个系统调用需要成线性增加的时间——5次调用大约需要0.5秒：

```
start = time.perf_counter()

for _ in range(5):
    slow_systemcall()

end = time.perf_counter()
delta = end - start
print(f"Took {delta:.3f} seconds")

>>>
Took 0.525 seconds
```

The problem is that while the `slow_systemcall` function is running, my program can’t make any other progress. My program’s main thread of execution is blocked on the `select` system call. This situation is awful in practice. I need to be able to compute my helicopter’s next move while I’m sending it a signal; otherwise, it’ll crash. When you find yourself needing to do blocking I/O and computation simultaneously like this, it’s time to consider moving your system calls to threads.
问题是当`slow_systemcall`函数运行时，我的程序无法取得任何进展。我的程序主线程被阻塞在`select`系统调用上。这种情况在实践中是很糟糕的。我需要能够在发送信号给直升机的同时计算它的下一步动作，否则它就会坠毁。当你发现自己需要像这样同时进行阻塞I/O和计算时，就应当考虑将系统调用移至线程中了。

Here, I run multiple invocations of the `slow_systemcall` function in separate threads. This would allow me to communicate with multiple serial ports (and helicopters) at the same time while leaving the main thread to do whatever computation is required:

这里，我在单独的线程中运行`slow_systemcall`函数的多个调用。这样我就可以同时与多个串口（和直升机）通信，同时让主线程进行任何必要的计算：

```
start = time.perf_counter()

threads = []
for _ in range(5):
    thread = Thread(target=slow_systemcall)
    thread.start()
    threads.append(thread)
```

With the threads started, here I do some work to calculate the next helicopter move before waiting for the system call threads to finish:

在启动线程后，我现在做一些工作来计算直升机的下一个位置，然后再等待系统调用线程完成：

```
def compute_helicopter_location(index):
    pass

for i in range(5):
    compute_helicopter_location(i)

for thread in threads:
    thread.join()

end = time.perf_counter()
delta = end - start
print(f"Took {delta:.3f} seconds")

>>>
Took 0.106 seconds
```


The parallel time is ~5x less than the serial time from the example code earlier. This shows that all the system calls will run in parallel from multiple Python threads even though they’re limited by the GIL. The GIL prevents my Python code from running in parallel, but it doesn’t have an effect on system calls. Python threads release the GIL just before they make system calls, and they reacquire the GIL as soon as the system calls are done.

并行时间比之前的示例代码中的串行时间少了约5倍。这表明尽管受限于GIL，所有的系统调用将从多个Python线程中并行运行。GIL阻止了我的Python代码并行运行，但它对系统调用没有影响。Python线程在进行系统调用之前释放GIL，一旦系统调用完成就重新获取GIL。

There are many other ways to deal with blocking I/O besides using threads, such as the `asyncio` built-in module, and these alternatives have important benefits. But those options might require extra work in refactoring your code to fit a different model of execution (see Item 75: “Achieve Highly Concurrent I/O with Coroutines” and Item 77: “Mix Threads and Coroutines to Ease the Transition to asyncio ”). Using threads is the simplest way to do blocking I/O in parallel with minimal changes to your program.

除了使用线程之外，还有许多其他方式可以处理阻塞I/O，比如`asyncio`内置模块，而这些替代方案有重要好处。但这些选择可能需要额外的工作来重构你的代码以适应不同的执行模型（参见条目75：“通过协程实现高并发I/O”和条目77：“混合使用线程和协程以平滑过渡到asyncio”）。使用线程是在最小更改程序的情况下进行阻塞I/O的最简单方法。

**Things to Remember**
- Python threads can’t run in parallel on multiple CPU cores because of the global interpreter lock (GIL).
- Python threads are still useful despite the GIL because they provide an easy way to do multiple things seemingly at the same time.
- You can use Python threads to make multiple system calls in parallel, allowing you to do blocking I/O at the same time as computation.

**注意事项**
- 由于全局解释器锁（GIL）的存在，Python线程不能在多个CPU核心上并行运行。
- 尽管存在GIL，Python线程仍然有用，因为它们提供了一种容易的方法来同时进行多个操作。
- 可以使用Python线程来并行进行多个系统调用，允许你在进行计算的同时进行阻塞I/O。