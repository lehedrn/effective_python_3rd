# Chapter 9: Concurrency and Parallelism (并发与并行)

Concurrency enables a computer to do many different things seemingly at the same time. For example, on a computer with one CPU core, the operating system rapidly changes which program is running on the single processor. In doing so, it interleaves execution of the programs, providing the illusion that the programs are running simultaneously.

并发使得计算机可以看似同时执行许多不同的任务。例如，在一台单核CPU的计算机上，操作系统会快速切换在单一处理器上运行的程序。通过这种方式，程序的执行相互交织，营造出这些程序同时运行的假象。

Parallelism, in contrast, involves actually doing many different things at the same time. Computers with multiple CPU cores can execute multiple programs simultaneously. Each CPU core runs the instructions of a separate program, allowing each program to make forward progress during the same instant.

相比之下，并行实际上是在同一时间执行多个不同的任务。具有多个CPU核心的计算机可以同时执行多个程序。每个CPU核心运行不同程序的指令，允许每个程序在同一时刻取得进展。

Within a single program, concurrency is a tool that makes it easier for programmers to solve certain types of problems. Concurrent programs enable many distinct paths of execution, including separate streams of I/O, to make forward progress in a way that seems to be both simultaneous and independent.

在一个单独的程序中，并发是一种帮助程序员解决某些类型问题的工具。并发程序允许多个独立的执行路径，包括不同的I/O流，以看似同时且独立的方式取得进展。

The key difference between parallelism and concurrency is speedup. When two distinct paths of execution in a program make forward progress in parallel, the time it takes to do the total work is cut in half; the speed of execution is faster by a factor of two. In contrast, concurrent programs may run thousands of separate paths of execution seemingly in parallel but provide no speedup for the total work.

并行和并发之间的关键区别在于加速。当一个程序中的两个不同执行路径并行执行时，完成总工作所需的时间减少了一半；执行速度提高了两倍。相反，并发程序可能运行着数千个看似并行的独立执行路径，但对总体工作的执行速度没有提升。

Python makes it easy to write concurrent programs in a variety of styles. Threads support a relatively small amount of concurrency, while asynchronous coroutines enable vast numbers of concurrent functions. Python can also be used to do parallel work through system calls, subprocesses, and C extensions. But it can be very difficult to make concurrent Python code truly run in parallel. It’s important to understand how to best utilize Python in these different situations.

Python使得以多种风格编写并发程序变得简单。线程支持相对少量的并发，而异步协程能够实现大量并发函数。Python还可以通过系统调用、子进程和C扩展来执行并行工作。但是，要使并发的Python代码真正并行运行可能非常困难。了解如何在不同情况下最好地利用Python是非常重要的。

1. [Item 67: Use subprocess to Manage Child Processes](Chapter-9-Item-67.md) 使用subprocess管理子进程
2. [Item 68: Use Threads for Blocking I/O; Avoid for Parallelism](Chapter-9-Item-68.md) 为阻塞I/O使用线程；避免用于并行
3. [Item 69: Use Lock to Prevent Data Races in Threads](Chapter-9-Item-69.md) 使用Lock防止线程中的数据竞争
4. [Item 70: Use Queue to Coordinate Work Between Threads](Chapter-9-Item-70.md) 使用Queue协调线程间的工作
5. [Item 71:Know How to Recognize When Concurrency Is Necessary](Chapter-9-Item-71.md) 知道何时需要并发
6. [Item 72: Avoid Creating New Thread Instances for On-demand Fan-out](Chapter-9-Item-72.md) 避免为按需扇出创建新的线程实例
7. [Item 73: Understand How Using Queue for Concurrency Requires Refactoring](Chapter-9-Item-73.md) 理解使用队列进行并发需要重构的情况
8. [Item 74: Consider ThreadPoolExecutor When Threads Are Necessary for Concurrency](Chapter-9-Item-74.md) 当线程对于并发是必要时考虑使用ThreadPoolExecutor
9. [Item 75: Achieve Highly Concurrent I/O with Coroutines](Chapter-9-Item-75.md) 通过协程实现高度并发的I/O
10. [Item 76: Know How to Port Threaded I/O to asyncio](Chapter-9-Item-76.md) 知道如何将线程I/O移植到asyncio
11. [Item 77: Mix Threads and Coroutines to Ease the Transition to asyncio](Chapter-9-Item-77.md) 混合使用线程和协程以简化向asyncio的过渡
12. [Item 78: Maximize Responsiveness of asyncio Event Loops with async-friendly Worker Threads](Chapter-9-Item-78.md) 使用async友好型工作线程最大化asyncio事件循环的响应性
13. [Item 79: Consider concurrent.futures for True Parallelism](Chapter-9-Item-79.md) 考虑使用concurrent.futures实现真正的并行