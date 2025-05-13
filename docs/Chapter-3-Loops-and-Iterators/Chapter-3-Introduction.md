# Chapter 3: Loops and Iterators

Processing through sequential data, of fixed or dynamic length, is a critical need in programs. Python, being a primarily imperative programming language, makes it easy to implement sequential processing using loops. The general pattern is: on each pass through a loop, read data—stored in variables, lists, dictionaries, etc—and carry out corresponding state modifications or I/O operations. Loops in Python feel natural and capable for the most common tasks involving built-in data types, container types, and user-defined classes.

Python also supports iterators, which enable a more functional-style approach to processing arbitrary streams of data. Instead of directly interacting with how the sequential data is stored, iterators provide a common abstraction that hides the details. They can make programs more efficient, easier to refactor, and capable of handling arbitrarily sized data. Python also includes functionality to compose iterators together and fully customize their behavior using generators (see more in Chapter 6).


1. [Item 17: Prefer enumerate over range](Chapter-3-Item-17.md)
2. [Item 18: Use zip to Process Iterators in Parallel](Chapter-3-Item-18.md)
3. [Item 19: Avoid else Blocks After for and while Loops](Chapter-3-Item-19.md)
4. [Item 20: Never Use for Loop Variables After the Loop Ends](Chapter-3-Item-20.md)
5. [Item 21: Be Defensive when Iterating over Arguments](Chapter-3-Item-21.md)
6. [Item 22: Never Modify Containers While Iterating over Them; Use Copies or Caches Instead](Chapter-3-Item-22.md)
7. [Item 23: Pass Iterators to any and all for Efficient Short-Circuiting Logic](Chapter-3-Item-23.md)
8. [Item 24: Consider itertools for Working with Iterators and Generators](Chapter-3-Item-24.md)