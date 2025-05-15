# Chapter 4: Dictionaries (字典)

A natural complement to lists and sequences in Python is the dictionary type, which stores lookup keys mapped to corresponding values (in what is often called an associative array or a hash table). The versatility of dictionaries makes them ideal for bookkeeping: dynamically keeping track of new and changing pieces of data and how they related to each other. When writing a new program, using dictionaries is a great way to start before you're sure what other data structures or classes you might need.

在 Python 中，列表和序列的自然补充是字典类型，它存储了查找键与相应值的映射（通常称为关联数组或哈希表）。字典的多功能性使它们非常适合记账：动态跟踪新数据和变化的数据及其相互关系。在编写新程序时，在确定需要其他什么数据结构或类之前，使用字典是一个很好的起点。

Dictionaries provide constant time (amortized) performance for adding, removing, modifying, and retrieving items, which is far better than what simple lists can achieve on their own. Thus, it's understandable that dictionaries are the core data structure that Python uses to implement its object-oriented features. Python also has special syntax and related built-in modules that enhance dictionaries with additional capabilities beyond what you might expect from a simple hash table type in other languages.

字典提供了常数时间（摊销）性能以进行添加、删除、修改和检索项，这比简单列表所能实现的要好得多。因此，可以理解字典是 Python 使用来实现其面向对象特性的核心数据结构。Python 还具有特殊的语法和相关的内置模块，为字典增添了超出你对其他语言中简单哈希表类型的期望的额外功能。


1. [Item 25: Be Cautious when Relying on Dictionary Insertion Ordering](Chapter-4-Item-25.md)
2. [Item 26: Prefer get over in and KeyError to Handle Missing Dictionary Keys](Chapter-4-Item-26.md)
3. [Item 27: Prefer defaultdict over setdefault to Handle Missing Items in Internal State](Chapter-4-Item-27.md)
4. [Item 28: Know How to Construct Key-Dependent Default Values with __missing__](Chapter-4-Item-28.md)
5. [Item 29: Compose Classes Instead of Deeply Nesting Dictionaries, Lists, and Tuples](Chapter-4-Item-29.md)

1. [条目25：依赖字典插入顺序时要谨慎](Chapter-4-Item-25.md)
2. [条目26：处理缺失字典键时优先使用 get 而不是 in 和 KeyError](Chapter-4-Item-26.md)
3. [条目27：在内部状态中处理缺失项目时优先使用 defaultdict 而不是 setdefault](Chapter-4-Item-27.md)
4. [条目28：了解如何使用 `__missing__` 构造依赖键的默认值](Chapter-4-Item-28.md)
5. [条目29：组合类而不是深度嵌套字典、列表和元组](Chapter-4-Item-29.md)
