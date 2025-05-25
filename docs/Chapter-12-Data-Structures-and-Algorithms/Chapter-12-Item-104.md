# Chapter 12: Data Structures and Algorithms (数据结构与算法)

## Item 104: Know How to Use `heapq` for Priority Queues (了解如何使用 `heapq` 实现优先队列)

One of the limitations of Python’s other queue implementations (see Item 103: “Prefer `deque` for Producer-Consumer Queues” and Item 70: “Use `Queue` to Coordinate Work Between Threads”) is that they are first-in, first-out (FIFO) queues: Their contents are sorted by the order in which they were received. Often, you need a program to process items in order of relative importance instead. To accomplish this, a priority queue is the right tool for the job.

Python 其他队列实现的一个限制（参见条目 103：“优先使用 `deque` 处理生产者-消费者队列” 和条目 70：“使用 `Queue` 协调线程间的工作”）是它们都是先进先出（FIFO）队列：其内容按照接收顺序进行排序。通常，您需要一个程序按照相对重要性来处理项目。为此，优先队列是合适的工具。

For example, say that I’m writing a program to manage books borrowed from a library. There are people constantly borrowing new books. There are people returning their borrowed books on time. And there are people who need to be reminded to return their overdue books. Here, I define a class to represent a book that’s been borrowed:

例如，我正在编写一个程序来管理从图书馆借阅的书籍。人们不断地借新书，归还他们借阅的书籍，并有需要提醒归还逾期书籍的人。在这里，我定义了一个表示被借阅书籍的类：

```
class Book:
    def __init__(self, title, due_date):
        self.title = title
        self.due_date = due_date
```

I need a system that will send reminder messages when each book passes its due date. Unfortunately, I can’t use a FIFO queue for this because the amount of time each book is allowed to be borrowed varies based on its recency, popularity, and other factors. For example, a book that is borrowed today may be due back later than a book that’s borrowed tomorrow. Here, I achieve this behavior by using a standard `list` and sorting it by `due_date` each time a new `Book` is added:

我需要一个系统，在每本书超过截止日期时发送提醒消息。不幸的是，我不能使用 FIFO 队列，因为每本书允许借阅的时间长短取决于其新旧程度、受欢迎程度等因素。例如，今天借的一本书可能比明天借的一本书归还期限更晚。通过使用标准的 `list` 并在每次添加新的 `Book` 时按 `due_date` 排序，我可以实现这种行为：

```
def add_book(queue, book):
    queue.append(book)
    queue.sort(key=lambda x: x.due_date, reverse=True)

queue = []
add_book(queue, Book("Don Quixote", "2019-06-07"))
add_book(queue, Book("Frankenstein", "2019-06-05"))
add_book(queue, Book("Les Misérables", "2019-06-08"))
add_book(queue, Book("War and Peace", "2019-06-03"))
```

If I can assume that the queue of borrowed books is always in sorted order, then all I need to do to check for overdue books is to inspect the final element in the `list` . Here, I define a function to return the next overdue book, if any, and remove it from the queue:

如果我假设借阅书籍的队列始终按排序顺序排列，那么检查逾期书籍所需要做的就是检查 `list` 的最后一个元素。在这里，我定义了一个函数，用于返回下一个逾期的书籍（如果有的话），并将其从队列中移除：

```
class NoOverdueBooks(Exception):
    pass

def next_overdue_book(queue, now):
    if queue:
        book = queue[-1]
        if book.due_date < now:
            queue.pop()
            return book

    raise NoOverdueBooks
```

I can call this function repeatedly to get overdue books to remind people about in the order of most overdue to least overdue:

我可以反复调用这个函数，以获取最逾期到最少逾期的逾期书籍，以提醒人们：

```
now = "2019-06-10"

found = next_overdue_book(queue, now)
print(found.due_date, found.title)

found = next_overdue_book(queue, now)
print(found.due_date, found.title)

>>>
2019-06-03 War and Peace
2019-06-05 Frankenstein
```

If a book is returned before the due date, I can remove the scheduled reminder message by removing the `Book` from the `list` :

如果一本书在截止日期之前归还，我可以通过从 `list` 中移除该书来取消预定的提醒消息：

```
def return_book(queue, book):
    queue.remove(book)

queue = []
book = Book("Treasure Island", "2019-06-04")

add_book(queue, book)
print("Before return:", [x.title for x in queue])

return_book(queue, book)
print("After return: ", [x.title for x in queue])
>>>
Before return: ['Treasure Island']
After return: []
```

And I can confirm that when all books are returned, the `return_book` function will raise the right exception (see Item 32: “Prefer Raising Exceptions to Returning `None` ” for this convention):

并且我可以确认当所有书籍都归还后，`return_book` 函数会引发正确的异常（参见条目 32：“优先选择引发异常而不是返回 `None`” 了解此约定）：

```
try:
    next_overdue_book(queue, now)
except NoOverdueBooks:
    pass          # Expected
else:
    assert False  # Doesn't happen
```

However, the computational complexity of this solution isn’t ideal. Alhough checking for and removing an overdue book has a constant cost, every time I add a book, I pay the cost of sorting the whole `list` again. If I have `len(queue)` books to add, and the cost of sorting them is roughly `len(queue) * math.log(len(queue))` , that means that the time it takes to add books will grow superlinearly ( `len(queue) * len(queue) * math.log(len(queue))` ).

然而，这种解决方案的计算复杂度并不理想。虽然检查和删除逾期书籍的成本是恒定的，但每次添加书籍时，都需要重新对整个 `list` 进行排序。如果有 `len(queue)` 本书籍要添加，并且排序成本大约为 `len(queue) * math.log(len(queue))`，这意味着添加书籍所需的时间将呈超线性增长（`len(queue) * len(queue) * math.log(len(queue))`）。

Here, I define a microbenchmark to measure this performance behavior experimentally by using the `timeit` built-in module (see Item 93: “Optimize Performance-Critical Code Using `timeit` Microbenchmarks” for details):

在这里，我定义了一个微基准测试，通过使用内置模块 `timeit`（参见条目 93：“使用 `timeit` 微基准测试优化性能关键代码”）来实验性地测量这种性能行为：

```
import random
import timeit

def list_overdue_benchmark(count):
    def prepare():
        to_add = list(range(count))
        random.shuffle(to_add)
        return [], to_add

    def run(queue, to_add):
        for i in to_add:
            queue.append(i)
            queue.sort(reverse=True)

        while queue:
            queue.pop()

    return timeit.timeit(
        setup="queue, to_add = prepare()",
        stmt=f"run(queue, to_add)",
        globals=locals(),
        number=1,
    )
```

I can verify that the runtime of adding and removing books from the queue scales superlinearly as the number of books being borrowed increases:

我可以验证，随着借阅书籍数量的增加，添加和删除书籍的运行时间呈超线性增长：

```
for i in range(1, 6):
    count = i * 1_000
    delay = list_overdue_benchmark(count)
    print(f"Count {count:>5,} takes: {delay*1e3:>6.2f}ms")

>>>
Count 1,000 takes: 1.74ms
Count 2,000 takes: 5.87ms
Count 3,000 takes: 11.12ms
Count 4,000 takes: 19.80ms
Count 5,000 takes: 31.02ms
```

When a book is returned before the due date, I need to do a linear scan in order to find the book in the queue and remove it. Removing a book causes all subsequent items in the `list` to be shifted back an index, which has a high cost that also scales superlinearly. Here, I define another microbenchmark to test the performance of returning a book using this function:

当一本书在截止日期前归还时，我需要进行线性扫描以在队列中找到这本书并将其移除。删除一本书会导致列表中后续所有项目的索引回退，这具有高成本，并且也呈超线性增长。在这里，我定义了另一个微基准测试来测试使用此函数归还一本书的性能：

```
def list_return_benchmark(count):
    def prepare():
        queue = list(range(count))
        random.shuffle(queue)

        to_return = list(range(count))
        random.shuffle(to_return)

        return queue, to_return

    def run(queue, to_return):
        for i in to_return:
            queue.remove(i)

    return timeit.timeit(
        setup="queue, to_return = prepare()",
        stmt=f"run(queue, to_return)",
        globals=locals(),
        number=1,
    )
```

And again, I can verify that indeed the performance degrades superlinearly as the number of books increases:

同样，我可以验证确实随着书籍数量的增加，性能下降呈超线性：

```
for i in range(1, 6):
    count = i * 1_000
    delay = list_return_benchmark(count)
    print(f"Count {count:>5,} takes: {delay*1e3:>6.2f}ms")

>>>
Count 1,000 takes: 1.97ms
Count 2,000 takes: 6.99ms
Count 3,000 takes: 14.59ms
Count 4,000 takes: 26.12ms
Count 5,000 takes: 40.38ms
```

Using the methods of `list` may work for a tiny library, but it certainly won’t scale to the size of the Great Library of Alexandria, as I want it to!

对于小型图书馆来说，使用 `list` 的方法可能有效，但它肯定无法扩展到我希望它达到的亚历山大图书馆的规模！

Fortunately, Python has the built-in `heapq` module that solves this problem by implementing priority queues efficiently. A heap is a data structure that allows for a `list` of items to be maintained where the computational complexity of adding a new item or removing the smallest item has logarithmic computational complexity (i.e., even better than linear scaling). In this book borrowing example, smallest means the book with the earliest due date. The best part about this module is that you don’t have to understand how heaps are implemented in order to use its functions correctly.

幸运的是，Python 提供了内置的 `heapq` 模块，通过高效实现优先队列解决了这个问题。堆是一种数据结构，允许维护一个项目列表，其中添加新项目或删除最小项目的计算复杂度是对数的（即，甚至比线性缩放更好）。在这个书籍借阅示例中，最小意味着最早到期的书籍。这个模块最好的部分是您不需要了解堆是如何实现的，就可以正确使用它的函数。

Here, I reimplement the `add_book` function using the `heapq` module. The queue is still a plain `list` . The `heappush` function replaces the `list.append` call from before. And I no longer have to call `list.sort` on the queue:

在这里，我使用 `heapq` 模块重新实现了 `add_book` 函数。队列仍然是一个普通的 `list`。`heappush` 函数替换了之前的 `list.append` 调用。而且我不再需要在队列上调用 `list.sort`：

```
from heapq import heappush

def add_book(queue, book):
    heappush(queue, book)
```

If I try to use this with the `Book` class as previously defined, I get this somewhat cryptic error:

如果我尝试以前面定义的方式使用 `Book` 类，我会得到一个有些晦涩的错误：

```
queue = []
add_book(queue, Book("Little Women", "2019-06-05"))
add_book(queue, Book("The Time Machine", "2019-05-30"))
>>>
Traceback ...
TypeError: '<' not supported between instances of
'Book'
```

The cause is that the `heapq` module requires items in the priority queue to be comparable and have a natural sort order (see Item 100: “Sort by Complex Criteria Using the `key` Parameter” for details). You can quickly give the `Book` class this behavior by using the `total_ordering` class decorator from the `functools` built-in module (see Item 66: “Prefer Class Decorators Over Metaclasses for Composable Class Extensions” for background), and implementing the `__lt__` special method (see Item 57: “Inherit from `collections.abc` Classes for Custom Container Types” for background).

原因是 `heapq` 模块要求优先队列中的项目可比较并具有自然排序顺序（参见条目 100：“使用 `key` 参数按复杂标准排序” 了解详细信息）。您可以快速通过使用 `functools` 内置模块中的 `total_ordering` 类装饰器（参见条目 66：“优先使用类装饰器而非元类进行可组合的类扩展” 了解背景）并实现 `__lt__` 特殊方法（参见条目 57：“继承 `collections.abc` 类以创建自定义容器类型” 了解背景）来为 `Book` 类提供此行为。

Here, I redefine the class with a less-than method ( `__lt__` ) that simply compares the `due_date` fields between two `Book` instances:

在这里，我重新定义了类，添加了一个小于方法 (`__lt__`)，该方法简单地比较两个 `Book` 实例之间的 `due_date` 字段：

```
import functools

@functools.total_ordering
class Book:
    def __init__(self, title, due_date):
        self.title = title
        self.due_date = due_date

    def __lt__(self, other):
        return self.due_date < other.due_date
```

Now, I can add books to the priority queue without any issues by using the `heapq.heappush` function:

现在，我可以使用 `heapq.heappush` 函数无任何问题地向优先队列中添加书籍：

```
queue = []
add_book(queue, Book("Pride and Prejudice", "2019-06-01"))
add_book(queue, Book("The Time Machine", "2019-05-30"))
add_book(queue, Book("Crime and Punishment", "2019-06-06"))
add_book(queue, Book("Wuthering Heights", "2019-06-12"))
print([b.title for b in queue])
```

Alternatively, I can create a `list` with all of the books in any order and then use the `sort` method of `list` to produce the heap:

或者，我可以创建一个包含所有书籍的 `list`，然后使用 `list` 的 `sort` 方法生成堆：

```
queue = [
    Book("Pride and Prejudice", "2019-06-01"),
    Book("The Time Machine", "2019-05-30"),
    Book("Crime and Punishment", "2019-06-06"),
    Book("Wuthering Heights", "2019-06-12"),
]
queue.sort()
print([b.title for b in queue])
```

Or I can use the `heapq.heapify` function to create a heap in linear time (as opposed to the `sort` method’s `len(queue) * log(len(queue))` complexity):

或者，我可以使用 `heapq.heapify` 函数在线性时间内创建一个堆（相对于 `sort` 方法的 `len(queue) * log(len(queue))` 复杂度）：

```
from heapq import heapify

queue = [
    Book("Pride and Prejudice", "2019-06-01"),
    Book("The Time Machine", "2019-05-30"),
    Book("Crime and Punishment", "2019-06-06"),
    Book("Wuthering Heights", "2019-06-12"),
]
heapify(queue)
print([b.title for b in queue])
```

To check for overdue books, I inspect the first element in the `list` instead of the last, and then I use the `heapq.heappop` function instead of the `list.pop` function to remove the book from the heap:

为了检查逾期书籍，我查看 `list` 中的第一个元素而不是最后一个，然后使用 `heapq.heappop` 函数代替 `list.pop` 函数从堆中移除书籍：

```
from heapq import heappop

def next_overdue_book(queue, now):
    if queue:
        book = queue[0]     # Most overdue first
        if book.due_date < now:
            heappop(queue)  # Remove the overdue book
            return book

    raise NoOverdueBooks
```

Now, I can find and remove overdue books in order until there are none left for the current time:

现在，我可以查找并按顺序删除逾期书籍，直到当前时间没有剩余逾期书籍为止：

```
now = "2019-06-02"

book = next_overdue_book(queue, now)
print(book.due_date, book.title)

book = next_overdue_book(queue, now)
print(book.due_date, book.title)

try:
    next_overdue_book(queue, now)
except NoOverdueBooks:
    pass  # Expected
else:
    assert False  # Doesn't happen
>>>
2019-05-30 The Time Machine
2019-06-01 Pride and Prejudice
```

I can write another microbenchmark to test the performance of this implementation that uses the `heapq` module:

我可以编写另一个微基准测试来测试使用 `heapq` 模块的实现性能：

```
def heap_overdue_benchmark(count):
    def prepare():
        to_add = list(range(count))
        random.shuffle(to_add)
        return [], to_add

    def run(queue, to_add):
        for i in to_add:
            heappush(queue, i)
        while queue:
            heappop(queue)

    return timeit.timeit(
        setup="queue, to_add = prepare()",
        stmt=f"run(queue, to_add)",
        globals=locals(),
        number=1,
    )
```

This benchmark experimentally verifies that the heap-based priority queue implementation scales much better (roughly `len(queue) * math.log(len(queue))` ) without superlinearly degrading performance:

该基准测试实验证明，基于堆的优先队列实现可以更好地扩展（大致 `len(queue) * math.log(len(queue))`），而不会导致性能的超线性下降：

```
for i in range(1, 6):
    count = i * 10_000
    delay = heap_overdue_benchmark(count)
    print(f"Count {count:>5,} takes: {delay*1e3:>6.2f}ms")

>>>
Count 10,000 takes: 1.73ms
Count 20,000 takes: 3.83ms
Count 30,000 takes: 6.50ms
Count 40,000 takes: 8.85ms
Count 50,000 takes: 11.43ms
```

With the `heapq` implementation, one question remains: How should I handle returns that are on time? The solution is to never remove a book from the priority queue until its due date. At that time, it will be the first item in the `list` , and I can simply ignore the book if it’s already been returned. Here, I implement this behavior by adding a new field to track the book’s return status:

使用 `heapq` 实现后，还有一个问题需要解决：如何处理按时归还的书籍？解决方案是在书籍的截止日期之前不要从优先队列中移除它。届时，它将是 `list` 中的第一个项目，我可以简单地忽略已归还的书籍。在这里，我通过添加一个新字段来跟踪书籍的归还状态来实现这一行为：

```
@functools.total_ordering
class Book:
    def __init__(self, title, due_date):
        self.title = title
        self.due_date = due_date
        self.returned = False  # New field

    def __lt__(self, other):
        return self.due_date < other.due_date
```

Then, I change the `next_overdue_book` function to repeatedly ignore any book that’s already been returned:

然后，我修改 `next_overdue_book` 函数，重复忽略任何已经归还的书籍：

```
def next_overdue_book(queue, now):
    while queue:
        book = queue[0]
        if book.returned:
            heappop(queue)
            continue

        if book.due_date < now:
            heappop(queue)
            return book

        break

    raise NoOverdueBooks
```

This approach makes the `return_book` function extremely fast because it makes no modifications to the priority queue:

这种方法使 `return_book` 函数非常快，因为它不对优先队列进行任何修改：

```
def return_book(queue, book):
    book.returned = True
```

The downside of this solution for returns is that the priority queue may grow to the maximum size it would have needed if all books from the library were checked out and went overdue. Although the queue operations will be fast thanks to `heapq` , this storage overhead may take significant memory (see Item 115: “Use `tracemalloc` to Understand Memory Usage and Leaks” for how to debug such usage).

这种归还方案的缺点是，优先队列可能会增长到如果图书馆的所有书籍都被借出并过期的情况下所需的大小。尽管由于 `heapq` 的存在，队列操作速度很快，但这种存储开销可能占用显著的内存（参见条目 115：“使用 `tracemalloc` 理解内存使用和泄漏” 了解如何调试此类使用情况）。

That said, if you’re trying to build a robust system, you will need to plan for the worst-case scenario; thus, you should expect that it’s possible for every library book to go overdue for some reason (e.g., a natural disaster closes the road to the library). This memory cost is a design consideration that you should have already planned for and mitigated through additional constraints (e.g., imposing a maximum number of simultaneously lent books).

尽管如此，如果您试图构建一个健壮的系统，则需要计划最坏的情况；因此，您应该预期可能由于某些原因（例如自然灾害关闭通往图书馆的道路），图书馆中的每一本书都可能逾期。这是设计时应考虑的内存成本，并应通过额外的约束条件（例如，对同时借出的最大书籍数量进行限制）来缓解。

Beyond the priority queue primitives that I’ve used in this example, the `heapq` module also provides additional functionality for advanced use cases (see `https://docs.python.org/3/library/heapq.html`). The module is a great choice when its functionality matches the problem you’re facing (see the `queue.PriorityQueue` class for another thread-safe option).

除了在此示例中使用的优先队列原语之外，`heapq` 模块还提供了更多功能，适用于高级用例（参见 `https://docs.python.org/3/library/heapq.html`）。当其功能符合您面临的问题时，该模块是一个很好的选择（另请参见 `queue.PriorityQueue` 类以获得另一种线程安全选项）。

**Things to Remember**
- Priority queues allow you to process items in order of importance instead of in first-in, first-out order.
- If you try to use `list` operations to implement a priority queue, your program’s performance will degrade superlinearly as the queue grows.
- The `heapq` built-in module provides all of the functions you need to implement a priority queue that scales efficiently.
- To use `heapq` , the items being prioritized must have a natural sort order, which requires special methods like `__lt__` to be defined for classes.

**注意事项**
- 优先队列允许您按照重要性顺序处理项目，而不是按照先进先出的顺序。
- 如果尝试使用 `list` 操作实现优先队列，则程序的性能将在队列增长时呈超线性下降。
- `heapq` 内置模块提供了高效扩展优先队列所需的所有函数。
- 要使用 `heapq` ，被优先的项目必须具有自然的排序顺序，这要求为类定义特殊方法如 `__lt__` 。