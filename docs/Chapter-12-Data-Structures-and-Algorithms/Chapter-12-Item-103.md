# Chapter 12: Data Structures and Algorithms (数据结构与算法)

## Item 103: Prefer `deque` for Producer-Consumer Queues (对于生产者-消费者队列优先使用 `deque`)

A common need in writing programs is a first-in-first-out (FIFO) queue, which is also known as a producer-consumer queue. FIFO queues are used when one function gathers values to process and another function handles them in the order in which they were received. Often, programmers turn to Python’s built-in `list` type to act as a FIFO queue.

编写程序时一个常见的需求是使用先进先出（FIFO）队列，这也可以被称为生产者-消费者队列。当一个函数收集需要处理的值，而另一个函数按照接收到的顺序来处理这些值时，就会用到FIFO队列。通常情况下，程序员会使用Python内置的`list`类型来充当FIFO队列。

For example, say that I’m writing a program that processes incoming emails for long-term archival, and it’s using a `list` for a producer-consumer queue. Here, I define a class to represent the messages:

例如，假设我正在编写一个将接收到的电子邮件进行长期归档的程序，并且该程序使用了一个`list`作为生产者-消费者队列。这里，我定义了一个类来表示消息：

```
class Email:
    def __init__(self, sender, receiver, message):
        self.sender = sender
        self.receiver = receiver
        self.message = message
```

I also define a placeholder function for receiving a single email, presumably from a socket, the file system, or some other type of I/O system. The implementation of this function doesn’t matter—what’s important is its interface: It will either return an `Email` instance or raise a `NoEmailError` exception (see Item 32: “Prefer Raising Exceptions to Returning `None` ” for more about this convention):

我还定义了一个用于接收单封邮件的占位函数，可能是从套接字、文件系统或其他类型的I/O系统中接收。这个函数的具体实现并不重要——重要的是它的接口：它要么返回一个`Email`实例，要么抛出一个`NoEmailError`异常（详见条目32：“偏好抛出异常而不是返回`None`”以了解更多关于这一惯例的信息）：

```
def get_emails():
    yield Email("foo@example.com", "bar@example.com", "hello1")
    yield Email("baz@example.com", "banana@example.com", "hello2")
    yield None
    yield Email("meep@example.com", "butter@example.com", "hello3")
    yield Email("stuff@example.com", "avocado@example.com", "hello4")
    yield None
    yield Email("thingy@example.com", "orange@example.com", "hello5")
    yield Email("roger@example.com", "bob@example.com", "hello6")
    yield None
    yield Email("peanut@example.com", "alice@example.com", "hello7")
    yield None

EMAIL_IT = get_emails()

class NoEmailError(Exception):
    pass

def try_receive_email():
    # Returns an Email instance or raises NoEmailError
    try:
        email = next(EMAIL_IT)
    except StopIteration:
        email = None

    if not email:
        raise NoEmailError

    print(f"Produced email: {email.message}")
    return email
```

The producing function receives emails and enqueues them to be consumed at a later time. This function uses the `append` method on the `list` to add new messages to the end of the queue so they are processed after all messages that were previously received:

生产函数接收邮件并将它们排队以便之后处理。此函数使用`list`上的`append`方法将新消息添加到队列的末尾，这样它们会在所有之前接收到的消息之后被处理：

```
def produce_emails(queue):
    while True:
        try:
            email = try_receive_email()
        except NoEmailError:
            return
        else:
            queue.append(email)  # Producer
```

The consuming function is what does something useful with the emails. This function calls `pop(0)` on the queue, which removes the very first item from the `list` and returns it to the caller. By always processing items from the beginning of the queue, the consumer ensures that the items are processed in the order in which they were received:

消费函数是对邮件执行有用操作的函数。这个函数调用队列上的`pop(0)`，它会移除列表中最前面的项目并将其返回给调用者。通过始终从队列的开头处理项目，消费者可以确保项目是按照接收顺序进行处理的：

```
def consume_one_email(queue):
    if not queue:
        return
    email = queue.pop(0)  # Consumer
    # Index the message for long-term archival
    print(f"Consumed email: {email.message}")
```

Finally, I need a looping function that connects the pieces together. This function alternates between producing and consuming until the `keep_running` function returns `False` (see Item 75: “Achieve Highly Concurrent I/O with Coroutines” on how to do this concurrently):

最后，我需要一个连接各个部分的循环函数。这个函数在生产者和消费者之间交替运行，直到`keep_running`函数返回`False`为止（参见条目75：“使用协程实现高度并发的I/O”了解如何并发地执行此操作）：

```
def loop(queue, keep_running):
    while keep_running():
        produce_emails(queue)
        consume_one_email(queue)


def make_test_end():
    count = list(range(10))

    def func():
        if count:
            count.pop()
            return True
        return False

    return func


def my_end_func():
    pass

my_end_func = make_test_end()
loop([], my_end_func)
```

Why not process each `Email` message in `produce_emails` as they’re returned by `try_receive_email` ? It comes down to the trade-off between latency and throughput. When using producer-consumer queues, you often want to minimize the latency of accepting new items so they can be collected as fast as possible. The consumer can then process through the backlog of items at a consistent pace——one item per loop in this case——which provides a stable performance profile and consistent throughput at the cost of end-to-end latency (see Item 70: “Use `Queue` to Coordinate Work Between Threads” for related best practices).

为什么不直接在`produce_emails`中处理每个由`try_receive_email`返回的`Email`消息呢？这取决于延迟与吞吐量之间的权衡。当使用生产者-消费者队列时，你通常希望最小化接受新项目的延迟，以便能够尽可能快地收集新项目。然后，消费者可以以一致的速度处理积压的项目——在这种情况下，每次循环处理一个项目——这提供了稳定的性能概况，并以端到端的延迟为代价实现了一致的吞吐量（参见条目70：“使用`Queue`协调线程间的工作”了解相关的最佳实践）。

Using a `list` for a producer-consumer queue like this works fine up to a point, but as the cardinality——the number of items in the list——increases, the `list` type’s performance can degrade superlinearly. To analyze the performance of using `list` as a FIFO queue, I can run some microbenchmarks using the `timeit` built-in module (see Item 93: “Optimize Performance-Critical Code Using `timeit` Microbenchmarks” for details). Here, I define a benchmark for the performance of adding new items to the queue using the `append` method of `list` (matching the producer function’s usage):

对于这种用途，使用`list`作为生产者-消费者队列在一定程度上是可以正常工作的，但随着基数（即列表中的项目数量）的增加，`list`类型的性能可能会超线性地退化。为了分析使用`list`作为FIFO队列的性能，我可以使用内置模块`timeit`运行一些微基准测试（详情请参见条目93：“使用`timeit`微基准优化性能关键代码”）。在这里，我定义了一个针对使用`list`的`append`方法（匹配生产函数的用法）向队列添加新项的性能基准测试：

```
import timeit

def list_append_benchmark(count):
    def run(queue):
        for i in range(count):
            queue.append(i)

    return timeit.timeit(
        setup="queue = []",
        stmt="run(queue)",
        globals=locals(),
        number=1,
    )
```

Running this benchmark function with different levels of cardinality lets me compare its performance in relationship to data size:

通过不同级别的基数运行此基准函数让我可以比较其与数据大小的关系中的性能：

```
for i in range(1, 6):
    count = i * 1_000_000
    delay = list_append_benchmark(count)
    print(f"Count {count:>5,} takes: {delay*1e3:>6.2f}ms")
>>>
Count 1,000,000 takes: 13.23ms
Count 2,000,000 takes: 26.50ms
Count 3,000,000 takes: 39.06ms
Count 4,000,000 takes: 51.98ms
Count 5,000,000 takes: 65.19ms
```

This shows that the `append` method takes roughly constant time for the `list` type, and the total time for enqueueing scales linearly as the data size increases. There is overhead for the `list` type to increase its capacity under the covers as new items are added, but it’s reasonably low and is amortized across repeated calls to `append` .

这表明`append`方法对`list`类型来说大致需要恒定的时间，并且入队的总时间随着数据大小的增加而线性扩展。虽然`list`类型在幕后增加容量时会有开销，但这是相当低的并且通过重复调用`append`进行了摊销。

Here, I define a similar benchmark for the `pop(0)` call that removes items from the beginning of the queue (matching the consumer function’s usage):

这里，我定义了类似的基准测试来测量`pop(0)`调用从队列开始处移除项目的性能（匹配消费函数的用法）：

```
def list_pop_benchmark(count):
    def prepare():
        return list(range(count))

    def run(queue):
        while queue:
            queue.pop(0)

    return timeit.timeit(
        setup="queue = prepare()",
        stmt="run(queue)",
        globals=locals(),
        number=1,
    )

```

I can similarly run this benchmark for different size queues to see how performance is affected by cardinality:

同样，我可以为不同大小的队列运行此基准测试以查看性能如何受到基数的影响：

```
for i in range(1, 6):
    count = i * 10_000
    delay = list_pop_benchmark(count)
    print(f"Count {count:>5,} takes: {delay*1e3:>6.2f}ms")
>>>
Count 10,000 takes: 4.98ms
Count 20,000 takes: 22.21ms
Count 30,000 takes: 60.04ms
Count 40,000 takes: 109.96ms
Count 50,000 takes: 176.92ms
```

Surprisingly, this shows that the total time for dequeuing items from a `list` with `pop(0)` scales quadratically as the length of the queue increases. The cause is that `pop(0)` needs to move every item in the `list` back an index, effectively reassigning the entire list’s contents. I need to call `pop(0)` for every item in the `list` , thus I end up doing roughly `len(queue) * len(queue)` operations to consume the queue. This doesn’t scale.

令人惊讶的是，这表明从`list`中通过`pop(0)`出队项目所需的时间随着队列长度的增加呈二次方增长。原因是`pop(0)`需要将列表中的每个项目后移一个索引，实际上重新分配整个列表的内容。我需要为列表中的每个项目调用`pop(0)`，因此最终完成的运算次数大约是`len(queue) * len(queue)`。这种方式不可扩展。

Python provides the `deque` class from the `collections` built-in module to solve this problem. `deque` is a double-ended queue implementation. It provides constant time operations for inserting or removing items from its beginning or end. This makes it ideal for FIFO queues.

Python 提供了来自 `collections` 内建模块的 `deque` 类来解决这个问题。`deque` 是双端队列的实现。它提供常数时间的操作来从头或尾插入或删除项目。这使其非常适合 FIFO 队列。

To use the `deque` class, the call to `append` in `produce_emails` can stay the same as it was when using a `list` for the queue. The `list.pop` method call in `consume_one_email` must change to call the `deque.popleft` method with no arguments instead. And the `loop` method must be called with a `deque` instance instead of a `list` . Everything else stays the same. Here, I redefine the one function affected to use the new method and run `loop` again:

要使用 `deque` 类，在 `produce_emails` 中对 `append` 的调用可以保持不变，就像使用 `list` 作为队列时一样。在 `consume_one_email` 中对 `list.pop` 方法的调用必须改为调用没有参数的 `deque.popleft` 方法。并且`loop`方法必须使用 `deque` 实例而不是 `list` 来调用。其他一切保持不变。在这里，我重新定义受影响的一个函数以使用新方法并再次运行 `loop`：

```
import collections

def consume_one_email(queue):
    if not queue:
        return
    email = queue.popleft()  # Consumer
    # Process the email message
    print(f"Consumed email: {email.message}")

def my_end_func():
    pass

my_end_func = make_test_end()
EMAIL_IT = get_emails()
loop(collections.deque(), my_end_func)
```

I can run another version of the benchmark to verify that `append` performance (matching the producer function’s usage) has stayed roughly the same (modulo a constant factor):

我可以运行另一个版本的基准测试以验证 `append` 性能（匹配生产函数的使用情况）大致保持相同（常数因子以内）：

```
def deque_append_benchmark(count):
    def prepare():
        return collections.deque()

    def run(queue):
        for i in range(count):
            queue.append(i)

    return timeit.timeit(
        setup="queue = prepare()",
        stmt="run(queue)",
        globals=locals(),
        number=1,
    )

for i in range(1, 6):
    count = i * 100_000
    delay = deque_append_benchmark(count)
    print(f"Count {count:>5,} takes: {delay*1e3:>6.2f}ms")
>>>
Count 100,000 takes: 1.68ms
Count 200,000 takes: 3.16ms
Count 300,000 takes: 5.05ms
Count 400,000 takes: 6.81ms
Count 500,000 takes: 8.43ms
```

And I can also benchmark the performance of calling `popleft` to mimic the consumer function’s usage of `deque` :

我还可以对调用 `popleft` 进行基准测试以模仿 `deque` 的消费函数使用情况：

```
def dequeue_popleft_benchmark(count):
    def prepare():
        return collections.deque(range(count))

    def run(queue):
        while queue:
            queue.popleft()

    return timeit.timeit(
        setup="queue = prepare()",
        stmt="run(queue)",
        globals=locals(),
        number=1,
    )

for i in range(1, 6):
    count = i * 100_000
    delay = dequeue_popleft_benchmark(count)
    print(f"Count {count:>5,} takes: {delay*1e3:>6.2f}ms")
>>>
Count 100,000 takes: 1.67ms
Count 200,000 takes: 3.59ms
Count 300,000 takes: 5.65ms
Count 400,000 takes: 7.50ms
Count 500,000 takes: 9.58ms
```

The `popleft` usage scales linearly instead of the superlinear behavior of `pop(0)` that I measured before—hooray! If you know that the performance of your program critically depends on the speed of your producer-consumer queues, then `deque` is a great choice. If you’re not sure, then you should instrument your program to find out (see Item 92: “Profile Before Optimizing”).

`popleft` 的使用情况随着数据量的增加而线性扩展，而不是之前测量到的 `pop(0)` 的超线性行为——太棒了！如果你知道你的程序的性能严重依赖于生产者-消费者队列的速度，那么 `deque` 是一个绝佳的选择。如果你不确定，则应该对你的程序进行剖析以确定（参见条目92：“在优化前进行剖析”）。

**Things to Remember**
- The `list` type can be used as a FIFO queue by having the producer call `append` to add items and the consumer call `pop(0)` to receive items. However, this may cause problems because the performance of `pop(0)` degrades superlinearly as the queue length increases.
- The `deque` class from the `collections` built-in module takes constant time—regardless of length—for `append` and `popleft` , making it ideal for FIFO queues.

**注意事项**
- 可以通过让生产者调用 `append` 添加项目，让消费者调用 `pop(0)` 接收项目的方式将 `list` 类型用作 FIFO 队列。然而，由于随着队列长度的增加，`pop(0)` 的性能会显著下降，这可能会引起问题。
- `collections` 内建模块中的 `deque` 类无论队列多长，都对 `append` 和 `popleft` 提供常数时间操作，这使得它非常适合用作 FIFO 队列。