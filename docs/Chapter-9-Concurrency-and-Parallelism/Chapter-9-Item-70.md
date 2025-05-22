# Chapter 9: Concurrency and Parallelism (并发与并行)

## Item 70: Use `Queue` to Coordinate Work Between Threads (使用 `Queue` 协调线程间的工作)

Python programs that do many things concurrently often need to coordinate their work. One of the most useful arrangements for concurrent work is a pipeline of functions.

进行许多操作的Python程序通常需要协调它们的工作。并发工作最有效的安排之一是流水线函数。

A pipeline works like an assembly line used in manufacturing. Pipelines have many phases in serial, with a specific function for each phase. New pieces of work are constantly added to the beginning of the pipeline. The functions can operate concurrently, each processing the piece of work in its phase. The work moves forward as each function completes until there are no phases remaining. This approach is especially good for work that includes blocking I/O or subprocesses—activities that can easily be parallelized using Python (see Item 67: “Use `subprocess` to Manage Child Processes” and Item 68: “Use Threads for Blocking I/O, Avoid for Parallelism”).

流水线就像制造业中的装配线一样运作。流水线有许多按顺序排列的阶段，每个阶段都有特定的功能。新的工作任务不断添加到流水线的开始处。各阶段的函数可以同时运行，各自处理任务。当每个函数完成时，任务向前移动，直到没有剩余阶段为止。这种方法特别适用于涉及阻塞I/O或子进程的工作——这些工作可以轻松地使用Python进行并行化（参见条目67：“使用`subprocess`管理子进程”和条目68：“对阻塞I/O使用线程，避免用于并行”）。

For example, say that I want to build a system that will take a constant stream of images from my digital camera, resize them, and then add them to a photo gallery online. Such a program could be split into three phases of a pipeline. New images are retrieved in the first phase. The downloaded images are passed through the resize function in the second phase. The resized images are consumed by the upload function in the final phase. Imagine that I’ve already written Python functions that execute the phases: `download` , `resize` , `upload` . How do I assemble a pipeline to do the work concurrently?

例如，假设我想构建一个系统，该系统将从我的数码相机中持续获取图像，调整其大小，然后将其添加到在线相册中。这样的程序可以分为流水线的三个阶段。在第一阶段获取新图像。下载的图像通过第二阶段的resize函数传递。调整大小的图像由最终阶段的upload函数消费。假设我已经编写了执行各个阶段的Python函数：`download`、`resize`、`upload`。如何组装一个能够并发工作的流水线？

```
def download(item):
    return item

def resize(item):
    return item

def upload(item):
    return item
```

The first thing I need is a way to hand off work between the pipeline phases. This can be modeled as a thread-safe producer-consumer queue (see Item 69: “Use `Lock` to Prevent Data Races in Threads” to understand the importance of thread safety in Python; see Item 104: “Prefer `deque` for Producer-Consumer Queues” to understand queue performance):

我首先需要一种方式来在流水线阶段之间交接工作。这可以建模为一个线程安全的生产者-消费者队列（参见条目69：“使用`Lock`防止线程中的数据竞争”以了解线程安全性在Python中的重要性；参见条目104：“对生产者-消费者队列首选`deque`”以了解队列性能）：

```
from collections import deque
from threading import Lock

class MyQueue:
    def __init__(self):
        self.items = deque()
        self.lock = Lock()
```

The producer, my digital camera, adds new images to the end of the `deque` of pending items:

生产者，即我的数码相机，将新图像添加到待处理项目的`deque`末尾：

```
from collections import deque
from threading import Lock

class MyQueue:
    def __init__(self):
        self.items = deque()
        self.lock = Lock()

    def put(self, item):
        with self.lock:
            self.items.append(item)
```

The consumer, the first phase of the processing pipeline, removes images from the front of the `deque` of pending items:

消费者，即处理流水线的第一阶段，从待处理项目的`deque`前端移除图像：

```
from collections import deque
from threading import Lock

class MyQueue:
    def __init__(self):
        self.items = deque()
        self.lock = Lock()
        
    def put(self, item):
        with self.lock:
            self.items.append(item)

    def get(self):
        with self.lock:
            return self.items.popleft()
```

Here, I represent each phase of the pipeline as a Python thread that takes work from one queue like this, runs a function on it, and puts the result on another queue. I also track how many times the worker has checked for new input and how much work it’s completed:

在这里，我将流水线的每个阶段表示为一个Python线程，它从一个队列中取工作，对其运行一个函数，并将结果放在另一个队列上。我还跟踪了工作者检查新输入的次数以及已完成的工作量：

```
from threading import Thread
import time

class Worker(Thread):
    def __init__(self, func, in_queue, out_queue):
        super().__init__()
        self.func = func
        self.in_queue = in_queue
        self.out_queue = out_queue
        self.polled_count = 0
        self.work_done = 0
```

The trickiest part is that the worker thread must properly handle the case where the input queue is empty because the previous phase hasn’t completed its work yet. This happens where I catch the `IndexError` exception below. You can think of this as a holdup in the assembly line:

最棘手的部分是工作者线程必须正确处理输入队列为空的情况，因为前一阶段尚未完成其工作。这发生在下面捕获`IndexError`异常的地方。你可以将其视为装配线上的延误：

```
from threading import Thread
import time

class Worker(Thread):
    def __init__(self, func, in_queue, out_queue):
        super().__init__()
        self.func = func
        self.in_queue = in_queue
        self.out_queue = out_queue
        self.polled_count = 0
        self.work_done = 0

    def run(self):
        while True:
            self.polled_count += 1
            try:
                item = self.in_queue.get()
            except IndexError:
                time.sleep(0.01)  # No work to do
            except AttributeError:
                # The magic exit signal to make this easy to show in
                # example code, but don't use this in practice.
                return
            else:
                result = self.func(item)
                self.out_queue.put(result)
                self.work_done += 1
```

Now, I can connect the three phases together by creating the queues for their coordination points and the corresponding worker threads:

现在，我可以将三个阶段连接起来，通过创建它们的协调点队列和相应的工作者线程：

```
download_queue = MyQueue()
resize_queue = MyQueue()
upload_queue = MyQueue()
done_queue = MyQueue()
threads = [
    Worker(download, download_queue, resize_queue),
    Worker(resize, resize_queue, upload_queue),
    Worker(upload, upload_queue, done_queue),
]
```

I can start the threads and then inject a bunch of work into the first phase of the pipeline. Here, I use a plain `object` instance as a proxy for the real data required by the `download` function:

我可以启动线程，然后向流水线的第一个阶段注入大量工作。在这里，我使用一个普通的`object`实例作为`download`函数所需的代理数据：

```
for thread in threads:
    thread.start()

for _ in range(1000):
    download_queue.put(object())
```

Now, I wait for all of the items to be processed by the pipeline and end up in the `done_queue` .

现在，我等待所有项目被流水线处理并最终进入`done_queue`。

```
while len(done_queue.items) < 1000:
    # Do something useful while waiting
    time.sleep(0.1)
# Stop all the threads by causing an exception in their
# run methods.
for thread in threads:
    thread.in_queue = None
    thread.join()
```

This runs properly, but there’s an interesting side effect caused by the threads polling their input queues for new work. The tricky part, where I catch `IndexError` exceptions in the `run` method, executes a large number of times:

这运行正常，但有一个有趣的副作用，由线程轮询其输入队列以获取新工作引起。在`run`方法中捕获`IndexError`异常的棘手部分执行了很多次：

```
processed = len(done_queue.items)
polled = sum(t.polled_count for t in threads)
print(f"Processed {processed} items after " f"polling {polled} times")

>>>
Processed 1000 items after polling 3033 times
```

When the worker functions vary in their respective speeds, an earlier phase can prevent progress in later phases, backing up the pipeline. This causes later phases to starve and constantly check their input queues for new work in a tight loop. The outcome is that worker threads waste CPU time doing nothing useful; they’re constantly raising and catching `IndexError` exceptions.

当工作函数的速度不一时，早期阶段可能会阻止后续阶段的进展，导致流水线堵塞。这会导致后续阶段饥饿并不断在其输入队列上进行紧密循环检查。结果是工作者线程浪费CPU时间不做任何有用的事情；他们不断地引发并捕获`IndexError`异常。

But that’s just the beginning of what’s wrong with this implementation. There are three more problems that you should also avoid. First, determining that all of the input work is complete requires yet another busy wait on the `done_queue` . Second, in `Worker` , the `run` method will execute forever in its busy loop. There’s no obvious way to signal to a worker thread that it’s time to exit.

但这只是这个实现问题的开始。还有三个更严重的问题你应该避免。首先，确定所有输入工作已经完成需要再次对`done_queue`进行忙等待。其次，在 `Worker` 中，`run` 方法将在其忙循环中无限执行下去。没有明显的方法告诉工作者线程该退出了。

Third, and worst of all, a backup in the pipeline can cause the program to crash arbitrarily. If the first phase makes rapid progress but the second phase makes slow progress, then the queue connecting the first phase to the second phase will constantly increase in size. The second phase won’t be able to keep up. Given enough time and input data, the program will eventually run out of memory and terminate.

第三，也是最糟糕的，流水线中的堵塞可能导致程序随意崩溃。如果第一阶段快速进展但第二阶段缓慢，则连接第一阶段到第二阶段的队列将持续增长。第二阶段无法跟上进度。经过足够的时间和输入数据后，程序最终会耗尽内存并终止。

The lesson here isn’t that pipelines are bad; it’s that it’s hard to build a good producer-consumer queue yourself. So why even try?

这里的教训不是流水线不好；而是很难自己构建一个好的生产者-消费者队列。那为什么还要尝试呢？

### `Queue` to the Rescue (`Queue` 救场)

The `Queue` class from the `queue` built-in module provides all of the functionality you need to solve the problems outlined above.

`queue`内置模块中的`Queue`类提供了上述所有问题所需的功能。

`Queue` eliminates busy waiting for new items by making the `get` method block the calling thread until data is available. For example, here I start a thread that waits for some input data on a queue:

`Queue`通过使`get`方法阻塞调用线程直到有数据可用，消除了对新项目的忙等待。例如，这里我启动一个线程，该线程在队列上等待一些输入数据：

```
from queue import Queue

my_queue = Queue()

def consumer():
    print("Consumer waiting")
    my_queue.get()  # Runs after put() below
    print("Consumer done")

thread = Thread(target=consumer)
thread.start()
```

Even though the consumer thread is running first, it won’t finish until an item is `put` on the `Queue` instance and the `get` method has something to return:

即使消费者线程先运行，它也不会完成，直到在`Queue`实例上`put()`了一个项目并且`get()`方法有了返回的内容：

```
print("Producer putting")
my_queue.put(object()) # Runs before get() above
print("Producer done")
thread.join()
>>>
Consumer waiting
Producer putting
Producer done
Consumer done
```

To solve the pipeline backup issue and avoid out-of-memory errors, the `Queue` class lets you specify the maximum amount of pending work to allow between two phases. This buffer size causes calls to `put` to block when the queue is already full (sometimes this behavior is called back pressure). For example, here I define a thread that waits for a while before consuming a queue:

为了解决流水线积压问题并避免内存溢出错误，`Queue`类允许您指定两个阶段之间允许的最大未完成工作量。此缓冲区大小导致当队列已满时对`put`的调用被阻塞（有时这种行为被称为反压力）。例如，这里我定义了一个线程，该线程在消费队列之前等待一段时间：

```
my_queue = Queue(1)  # Buffer size of 1

def consumer():
    time.sleep(0.1)  # Wait
    my_queue.get()   # Runs second
    print("Consumer got 1")
    my_queue.get()   # Runs fourth
    print("Consumer got 2")
    print("Consumer done")

thread = Thread(target=consumer)
thread.start()
```

The wait should allow the producer thread to `put` both objects on the queue before the consumer thread ever calls `get` . But the `Queue` size is 1. This means that the producer adding items to the queue will have to wait for the consumer thread to call `get` at least once before the second call to `put` will stop blocking and actually add the second item to the queue:

等待应该允许生产者线程在消费者线程调用`get`之前将两个对象都放入队列。但是`Queue`的大小是1。这意味着生产者向队列中添加项目时，必须等到消费者线程至少调用一次`get`，第二次调用`put`才会停止阻塞并将第二个项目添加到队列中：

```
my_queue.put(object()) # Runs first
print("Producer put 1")
my_queue.put(object()) # Runs third
print("Producer put 2")
print("Producer done")
thread.join()
>>>
Producer put 1
Consumer got 1
Producer put 2
Producer done
Consumer got 2
Consumer done
```

The `Queue` class can also track the progress of work using the `task_done` method. This lets you wait for a phase’s input queue to drain (using hte `join` method) and eliminates the need to poll for the last phase of a pipeline (as with the `done_queue` in the section above). For example, here I define a consumer thread that calls `task_done` when it finishes working on an item:

`Queue`类还可以使用`task_done`方法跟踪工作进度。这使您可以等待某个阶段的输入队列排空（使用`join`方法），从而消除了轮询管道最后一个阶段的需求（如上面提到的`done_queue`）。例如，这里我定义了一个消费者线程，该线程在其处理完一个项目后调用`task_done`：

```
in_queue = Queue()

def consumer():
    print("Consumer waiting")
    work = in_queue.get()      # Runs second
    print("Consumer working")
    # Doing work
    print("Consumer done")
    in_queue.task_done()       # Runs third

thread = Thread(target=consumer)
thread.start()
```

Now, the producer code doesn’t have to call `join` on the consumer thread or poll. The producer can just wait for the `in_queue` to finish by calling `join` on the `Queue` instance. Even once it’s empty, the in_queue won’t be joinable until after `task_done` is called for every item that was ever enqueued:

现在，生产者代码不必对消费者线程调用`join`或进行轮询。生产者只需等待`in_queue`完成，通过对`Queue`实例调用`join`即可。即使一旦队列为空，`in_queue`在所有曾经排队的项目都调用了`task_done`之前不会被`join`成功：

```
print("Producer putting")
in_queue.put(object()) # Runs first
print("Producer waiting")
in_queue.join() # Runs fourth
print("Producer done")
thread.join()
>>>
Consumer waiting
Producer putting
Producer waiting
Consumer working
Consumer done
Producer done
```

The `Queue` class also allows for easy termination of worker threads by calling the `shutdown` method (a feature added in Python version 3.13). After the shutdown signal is received, all calls to `put` on the queue will raise an exception, but the queue will permit `get` calls to drain the queue and complete pending work. Once the queue is fully empty, a `ShutDown` exception will be raised by `get` in the worker thread, giving it a chance to clean up and exit (see Item 80: “Take Advantage of Each Block in `try` / `except` / `else` / `finally` ” for background). For example, here I show how a thread continues to process work after `shutdown` is called:

`Queue`类还允许通过调用`shutdown`方法轻松终止工作者线程（此功能在Python版本3.13中添加）。关闭信号接收后，所有对队列的`put`调用都将引发异常，但队列将允许`get`调用清空队列并完成挂起的工作。一旦队列完全为空，`get`将在工作者线程中引发`ShutDown`异常，给予它清理和退出的机会（请参阅条目80：“利用`try` / `except` / `else` / `finally`中的每个块”了解背景）。例如，这里我展示了在调用`shutdown`后线程如何继续处理工作：


```
from queue import ShutDown

my_queue2 = Queue()

def consumer():
    while True:
        try:
            item = my_queue2.get()
        except ShutDown:
            print("Terminating!")
            return
        else:
            print("Got item", item)
            my_queue2.task_done()

thread = Thread(target=consumer)
my_queue2.put(1)
my_queue2.put(2)
my_queue2.put(3)
my_queue2.shutdown()

thread.start()

my_queue2.join()
thread.join()
print("Done")

>>>
Got item 1
Got item 2
Got item 3
Terminating!
Done
```

I can bring all of these behaviors together into a new worker thread class that processes input items one at a time, puts the results on an output queue, marks the input items as done, and terminates when the `ShutDown` exception is raised:

我可以将所有这些行为整合到一个新的工作者线程类中，该类一次处理一个输入项，将结果放在输出队列上，标记输入项为已完成，并在引发`ShutDown`异常时终止：

```
class StoppableWorker(Thread):
    def __init__(self, func, in_queue, out_queue):
        super().__init__()
        self.func = func
        self.in_queue = in_queue
        self.out_queue = out_queue

    def run(self):
        while True:
            try:
                item = self.in_queue.get()
            except ShutDown:
                return
            else:
                result = self.func(item)
                self.out_queue.put(result)
                self.in_queue.task_done()
```

Now, I can create a set of pipeline threads and queues using the new worker class; the `resize` and `upload` phases have a maximum number of items specified to prevent the program from running out of memory:

现在，我可以使用新的工作者类创建一组管道线程和队列；`resize`和`upload`阶段指定了最大项目数以防止程序耗尽内存：

```
download_queue = Queue()
resize_queue = Queue(100)
upload_queue = Queue(100)
done_queue = Queue()

threads = [
    StoppableWorker(download, download_queue, resize_queue),
    StoppableWorker(resize, resize_queue, upload_queue),
    StoppableWorker(upload, upload_queue, done_queue),
]

for thread in threads:
    thread.start()
```

To start processing, I inject all of the input work into the beginning of the pipeline:

为了开始处理，我将所有输入工作注入到管道线的开头：

```
for _ in range(1000):
    download_queue.put(object())
```

Then, I wait for the work in each phase to finish. I’m careful to call `shutdown` for each queue in the pipeline only after all work for that phase has been `put` into the corresponding queue. I use the `join` method to ensure that I wait for all of the work in the queue to be completed before sending the termination signal for the next phase:

然后，我等待每个阶段的工作完成。我小心地只在所有针对该阶段的put工作完成后才对该阶段的队列发送shutdown信号。我使用join方法确保我在等待该队列的所有工作完成后再发送下一个阶段的终止信号：

```
download_queue.shutdown()
download_queue.join()
resize_queue.shutdown()
resize_queue.join()
upload_queue.shutdown()
upload_queue.join()
```

Once the prior phases are complete, I send the shutdown signal to the final queue, receive each of the output items in the main thread, and wait for the worker threads to terminate:

一旦前面的阶段完成，我就向最终队列发送关闭信号，在主线程中接收每个输出项，并等待工作者线程终止：

```
done_queue.shutdown()

counter = 0

while True:
    try:
        item = done_queue.get()
    except ShutDown:
        break
    else:
        # Process the item
        done_queue.task_done()
        counter += 1

done_queue.join()

for thread in threads:
    thread.join()

print(counter, "items finished")

>>>
1000 items finished
```

This approach can be extended to use multiple worker threads per phase, which can increase I/O parallelism and speed up this type of program significantly. To do this, first I define helper functions for starting replicas of worker threads and draining the final queue:

这种方法可以扩展到每个阶段使用多个工作者线程，这可以增加I/O并行性并显著加快此类程序的速度。要做到这一点，首先我定义用于启动工作者线程副本和排空最终队列的帮助函数

```
def start_threads(count, *args):
    threads = [StoppableWorker(*args) for _ in range(count)]
    for thread in threads:
        thread.start()
    return threads

def drain_queue(input_queue):
    input_queue.shutdown()

    counter = 0

    while True:
        try:
            item = input_queue.get()
        except ShutDown:
            break
        else:
            input_queue.task_done()
            counter += 1

    input_queue.join()

    return counter
```

Then, I connect the queues together as before and start the workers:

然后，像以前一样连接队列并启动工作者：

```
download_queue = Queue()
resize_queue = Queue(100)
upload_queue = Queue(100)
done_queue = Queue()

threads = (
    start_threads(3, download, download_queue, resize_queue)
    + start_threads(4, resize, resize_queue, upload_queue)
    + start_threads(5, upload, upload_queue, done_queue)
)

```

Following the same order of calls to `put` , `shutdown` , `get` , and `join` as the example above, I can drive the work through the pipeline, but this time using multiple workers for each intermediate phase:

按照与上面相同的顺序调用`put`、`shutdown`、`get`和`join`，我可以驱动工作通过管道，但这次每个中间阶段使用多个工作者：

```
for _ in range(2000):
    download_queue.put(object())

download_queue.shutdown()
download_queue.join()

resize_queue.shutdown()
resize_queue.join()

upload_queue.shutdown()
upload_queue.join()

counter = drain_queue(done_queue)

for thread in threads:
    thread.join()

print(counter, "items finished")

>>>
2000 items finished
```

Although `Queue` works well in this case of a linear pipeline, there are other tools that you should consider using in different situations (see Item 75: “Achieve Highly Concurrent I/O with Coroutines” for an example).

尽管`Queue`在这种线性管道的情况下效果很好，但在不同情况下应考虑使用其他工具（参见条目75：“使用协程实现高度并发的I/O”了解示例）。

**Things to Remember**
- Pipelines are a great way to organize sequences of work——especially I/O-bound programs——that run concurrently using multiple Python threads.
- Be aware of the many problems in building concurrent pipelines: busy waiting, telling workers to stop, knowing when work is done, and memory explosion.
- The `Queue` class has all of the facilities you need to build robust pipelines: blocking operations, buffer sizes, joining, and shutdown.

**注意事项**
- 管道是组织并发运行的序列化工作的绝佳方式——尤其是I/O密集型程序——使用多个Python线程。
- 注意构建并发管道时的许多问题：忙等待、通知工作者停止、知道工作何时完成和内存爆炸。
- `Queue`类拥有构建健壮管道所需的所有功能：阻塞操作、缓冲区大小、加入和关闭。
