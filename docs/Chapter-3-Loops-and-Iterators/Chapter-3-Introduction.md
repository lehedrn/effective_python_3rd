# Chapter 3: Loops and Iterators (循环和迭代器)

Processing through sequential data, of fixed or dynamic length, is a critical need in programs. Python, being a primarily imperative programming language, makes it easy to implement sequential processing using loops. The general pattern is: on each pass through a loop, read data—stored in variables, lists, dictionaries, etc—and carry out corresponding state modifications or I/O operations. Loops in Python feel natural and capable for the most common tasks involving built-in data types, container types, and user-defined classes.

处理固定或动态长度的顺序数据是程序中的关键需求。Python 作为一种主要的命令式编程语言，使得使用循环实现顺序处理变得简单。通用模式是：在每次循环中，读取存储在变量、列表、字典等中的数据，并执行相应的状态修改或输入/输出操作。对于涉及内置数据类型、容器类型和用户定义类的最常见任务，Python 中的循环感觉自然且功能强大。

Python also supports iterators, which enable a more functional-style approach to processing arbitrary streams of data. Instead of directly interacting with how the sequential data is stored, iterators provide a common abstraction that hides the details. They can make programs more efficient, easier to refactor, and capable of handling arbitrarily sized data. Python also includes functionality to compose iterators together and fully customize their behavior using generators (see more in Chapter 6).

Python 还支持迭代器，它为处理任意数据流提供了一种更函数式的编程方法。迭代器提供了一个通用的抽象，隐藏了顺序数据存储的细节，而不是直接与数据存储方式进行交互。它们可以使程序更加高效、易于重构，并能够处理任意大小的数据。Python 还包括将迭代器组合在一起的功能，并通过生成器（请参阅第6章）完全自定义其行为。


1. [Item 17: Prefer enumerate over range](Chapter-3-Item-17.md)
2. [Item 18: Use zip to Process Iterators in Parallel](Chapter-3-Item-18.md)
3. [Item 19: Avoid else Blocks After for and while Loops](Chapter-3-Item-19.md)
4. [Item 20: Never Use for Loop Variables After the Loop Ends](Chapter-3-Item-20.md)
5. [Item 21: Be Defensive when Iterating over Arguments](Chapter-3-Item-21.md)
6. [Item 22: Never Modify Containers While Iterating over Them; Use Copies or Caches Instead](Chapter-3-Item-22.md)
7. [Item 23: Pass Iterators to any and all for Efficient Short-Circuiting Logic](Chapter-3-Item-23.md)
8. [Item 24: Consider itertools for Working with Iterators and Generators](Chapter-3-Item-24.md)

1. 条目17：优先使用 enumerate 而不是 range
2. 条目18：使用 zip 并行处理迭代器
3. 条目19：避免在 for 和 while 循环后使用 else 块
4. 条目20：不要在循环结束后使用 for 循环变量
5. 条目21：迭代参数时要具有防御性
6. 条目22：在迭代容器时不要修改它们；使用副本或缓存
7. 条目23：将迭代器传递给 any 和 all 以实现高效的短路逻辑
8. 条目24：考虑使用 itertools 来处理迭代器和生成器