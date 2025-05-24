# Chapter 11: Performance (性能)

There are a wide range of metrics for judging the execution quality of a program, including CPU utilization, throughput, latency, response time, memory usage, cache hit rate, etc. These metrics can also be assessed in different ways with respect to their statistical distribution; for example, with latency, depending on your goals, you might need to consider average latency, median latency, 99th percentile latency, or worst-case latency. There are also application-specific metrics that build on these lower-level ones, such as transactions per second, time to first paint, maximum frame rate, and goodput. Achieving good performance means that code you've written meets your expectations for one or more of the quantitative measurements that you care about most. Which metrics matter will depend on the problem domain, production environment, and user profile——there's no one-size-fits-all goal. Performance engineering is the discipline of analyzing program execution behavior, identifying areas for improvement, and implementing changes——large and small——to maximize or minimize the metrics that are most important.

衡量程序执行质量的指标有很多，包括CPU利用率、吞吐量、延迟、响应时间、内存使用、缓存命中率等。这些指标也可以根据其统计分布以不同的方式进行评估；例如，对于延迟来说，根据您的目标，您可能需要考虑平均延迟、中位数延迟、99百分位延迟或最坏情况延迟。还有基于这些低级指标构建的应用特定指标，如每秒事务数、首次绘制时间、最大帧率和有效吞吐量。实现良好的性能意味着您编写的代码满足您最关心的一个或多个定量度量的预期。哪些指标重要将取决于问题领域、生产环境和用户概况——没有一种适合所有的情况。性能工程是一门分析程序执行行为、识别改进区域并实施大大小小更改的学科，以最大化或最小化最重要的指标。

Python is not considered to be a high-performance language, especially in comparison to lower-level languages built for the task. This reputation is understandable given the overhead and constraints of the Python runtime, especially when it comes to parallelism (see Item 68: “Use Threads for Blocking I/O, Avoid for Parallelism” for background). That said, Python includes a variety of capabilities that enable programs to achieve surprisingly impressive performance with relatively low amounts of effort. Using these features, it's possible to extract maximum performance from a host system while retaining the productivity gains afforded by Python's high-level nature.

Python 并不被认为是一种高性能语言，尤其是与为完成任务而构建的低级语言相比。考虑到 Python 运行时的开销和限制，尤其是涉及到并行性时（有关背景，请参见第 68 条：“对阻塞 I/O 使用线程，避免用于并行处理”），这种声誉是可以理解的。话虽如此，Python 包含各种功能，使程序能够以相对较少的努力实现令人印象深刻的性能。利用这些特性，可以在保留 Python 高级别特性带来的生产力优势的同时，从主机系统中提取最大性能。

1. [Item 92: Profile Before Optimizing](Chapter-11-Item-92.md) 优化前先进行性能分析
2. [Item 93: Optimize Performance-Critical Code Using timeit Microbenchmarks](Chapter-11-Item-93.md) 使用 timeit 微基准测试优化性能关键代码
3. [Item 94: Know When and How to Replace Python with Another Programming Language](Chapter-11-Item-94.md) 知道何时以及如何用其他编程语言替换 Python
4. [Item 95: Consider ctypes to Rapidly Integrate with Native Libraries](Chapter-11-Item-95.md) 考虑使用 ctypes 快速集成本地库
5. [Item 96: Consider Extension Modules to Maximize Performance and Ergonomics](Chapter-11-Item-96.md) 考虑使用扩展模块来最大化性能和用户体验
6. [Item 97: Rely on Precompiled Bytecode and File System Caching to Improve Startup Time](Chapter-11-Item-97.md) 依赖预编译字节码和文件系统缓存来提高启动时间
7. [Item 98: Lazy-Load Modules with Dynamic Imports to Reduce Startup Time](Chapter-11-Item-98.md) 通过动态导入懒加载模块以减少启动时间
8. [Item 99: Consider memoryview and bytearray for Zero-Copy Interactions with bytes](Chapter-11-Item-99.md) 考虑使用 memoryview 和 bytearray 实现与 bytes 的零拷贝交互