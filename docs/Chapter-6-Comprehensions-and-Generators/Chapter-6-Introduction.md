# Chapter 6: Comprehensions and Generators (推导式和生成器)

Many programs are built around processing lists, dictionary key-value pairs, and sets. Python provides a special syntax, called comprehensions, for succinctly iterating through these types and creating derivative data structures. Comprehensions can significantly increase the readability of code performing these common tasks and provide a number of other benefits.

许多程序都是围绕处理列表、字典键值对和集合构建的。Python 提供了一种特殊的语法，称为“推导式”，用于简洁地遍历这些数据类型并创建派生的数据结构。推导式可以显著提高执行这些常见任务的代码可读性，并带来其他诸多优势。

This style of processing is extended to functions with generators, which enable a stream of values to be incrementally returned by a function. The result of a call to a generator function can be used anywhere an iterator is appropriate (e.g., `for` loops, starred unpacking expressions). Generators can improve performance, reduce memory usage, increase readability, and simplify implementations.

这种处理方式通过“生成器”扩展到了函数中，生成器允许函数逐步返回一系列值。调用生成器函数的结果可以在任何适用迭代器的地方使用（例如 `for` 循环、带星号的解包表达式）。生成器可以提升性能、减少内存使用、增加代码可读性，并简化实现方式。

1. [Item 40: Use Comprehensions Instead of map and filter](Chapter-6-Item-40.md) 优先使用推导式而非 map 和 filter
2. [Item 41: Avoid More Than Two Control Subexpressions in Comprehensions](Chapter-6-Item-41.md) 避免在推导式中使用超过两个控制子表达式
3. [Item 42: Reduce Repetition in Comprehensions with Assignment Expressions](Chapter-6-Item-42.md) 使用赋值表达式减少推导式中的重复
4. [Item 43: Consider Generators Instead of Returning Lists](Chapter-6-Item-43.md) 考虑使用生成器替代返回列表
5. [Item 44: Consider Generator Expressions for Large List Comprehensions](Chapter-6-Item-44.md) 对于大型列表推导式，考虑使用生成器表达式
6. [Item 45: Compose Multiple Generators with yield from](Chapter-6-Item-45.md) 使用 yield from 组合多个生成器
7. [Item 46: Pass Iterators into Generators as Arguments Instead of Calling the send Method](Chapter-6-Item-46.md) 将迭代器作为参数传入生成器，而不是调用 send 方法
8. [Item 47: Manage Iterative State Transitions with a Class Instead of the Generator throw Method](Chapter-6-Item-47.md) 使用类管理迭代状态转换，而非使用生成器的 throw 方法
