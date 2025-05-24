# Chapter 12: Data Structures and Algorithms (数据结构与算法)

When you’re implementing Python programs that handle a non-trivial amount of data, you’ll often encounter slowdowns caused by the algorithmic complexity of your code. For example, programs you expected to scale linearly in the size of input data might actually grow quadratically, causing problems in production. Luckily, Python includes optimized implementations of many standard data structures and algorithms that can help you achieve high performance with minimal effort.

当你在实现处理大量数据的Python程序时，经常会遇到由于代码的算法复杂度导致的性能下降问题。例如，你原本期望随着输入数据线性扩展的程序实际上可能会出现二次方级别的增长，从而在生产环境中引发问题。幸运的是，Python 包含了许多标准数据结构和算法的优化实现，可以帮助你以最小的努力实现高性能。

Similarly, Python provides built-in data types and helper functions for handling common tasks that frequently come up in programs: manipulating dates, times, and timezones; working with money values while preserving precision and controlling rounding behavior; and saving and restoring program state for users even as your software evolves over time. Writing code to handle these situations is fiddly and hard to get right. Having battle-tested implementations built into the language to handle them is a blessing.

同样，Python 提供了内置的数据类型和辅助函数来处理程序中频繁出现的常见任务：操作日期、时间及时区；处理货币值同时保持精度并控制舍入行为；即使在软件不断演进的过程中也能为用户保存和恢复程序状态。编写处理这些情况的代码是繁琐且难以正确实现的。而语言内置经过实战检验的实现来处理这些问题则是一种福音。

1. [Item 100: Sort by Complex Criteria Using the key Parameter](Chapter-12-Item-100.md) 使用 key 参数按复杂条件排序
2. [Item 101: Know the Difference Between sort and sorted](Chapter-12-Item-101.md) 了解 sort 和 sorted 的区别
3. [Item 102: Consider Searching Sorted Sequences with bisect](Chapter-12-Item-102.md) 考虑使用 bisect 搜索已排序序列
4. [Item 103: Prefer deque for Producer-Consumer Queues](Chapter-12-Item-103.md) 优先选择 deque 实现生产者-消费者队列
5. [Item 104: Know How to Use heapq for Priority Queues](Chapter-12-Item-104.md) 知道如何使用 heapq 实现优先队列
6. [Item 105: Use datetime Instead of time for Local Clocks](Chapter-12-Item-105.md) 使用 datetime 而非 time 处理本地时钟
7. [Item 106: Use decimal When Precision Is Paramount](Chapter-12-Item-106.md) 在需要精确计算时使用 decimal
8. [Item 107: Make pickle Serialization Maintainable with copyreg](Chapter-12-Item-107.md) 使用 copyreg 维护 pickle 序列化的可维护性