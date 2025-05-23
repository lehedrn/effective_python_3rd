# Chapter 9: Concurrency and Parallelism (并发与并行)

## Item 77: Mix Threads and Coroutines to Ease the Transition to `asyncio` (混合使用线程和协程以简化向`asyncio`的迁移)

In the previous item (see Item 76: “Know How to Port Threaded I/O to `asyncio` ”), I ported a TCP server that does blocking I/O with threads over to use `asyncio` with coroutines. The transition was big-bang: I moved all of the code to the new style in one go. But it’s rarely feasible to port a large program this way. Instead, you usually need to incrementally migrate your codebase while also updating your tests as needed and verifying that everything works at each step along the way.

在上一条（见条目76：“了解如何将阻塞式I/O迁移到`asyncio`”）中，我将一个使用线程进行阻塞I/O的TCP服务器迁移到使用`asyncio`和协程。这次迁移是一次性完成的大规模转换。但在实际中，很少可行的方式是将大型程序一次性全部迁移。相反，通常需要逐步迁移代码库，并根据需要更新测试，确保在每个步骤都能验证一切正常运行。

In order to do that, your codebase needs to be able to use threads for blocking I/O (see Item 68: “Use Threads for Blocking I/O, Avoid for Parallelism”) and coroutines for asynchronous I/O (see Item 75: “Achieve Highly Concurrent I/O with Coroutines”) at the same time in a way that’s mutually compatible. Practically, this means that you need threads to be able to run coroutines, and you need coroutines to be able to start and wait on threads. Luckily, `asyncio` includes built-in facilities for making this
type of interoperability straightforward.

为了实现这一点，你的代码库需要能够同时使用线程进行阻塞I/O（见条目68：“对阻塞I/O使用线程，避免用于并行处理”）和协程进行异步I/O（见条目75：“通过协程实现高度并发的I/O”），并且这两种方式要相互兼容。实际上，这意味着你需要线程能够运行协程，同时协程也能够启动并等待线程。幸运的是，`asyncio`包含了一些内置设施，使得这种互操作变得简单直接。

For example, say that I’m writing a program that merges log files together into one output stream in order to aid with debugging. Given a file handle for an input log, I need a way to detect whether new data is available and return the next line of input. I can do this using the `tell` method of the file handle to check whether the current read position matches the length of the file. When no new data is present, an exception should be raised (see Item 32: “Prefer Raising Exceptions to Returning `None` ” for background):

例如，假设我在编写一个程序，该程序将日志文件合并成一个输出流，以帮助调试。给定一个输入日志的文件句柄，我需要一种方法来检测是否有新数据可用，并返回下一行输入。我可以使用文件句柄的`tell`方法来检查当前读取位置是否与文件长度匹配。当没有新数据时，应抛出异常（见条目32：“优先抛出异常而不是返回`None`”作为背景）：

```
class NoNewData(Exception):
    pass

def readline(handle):
    offset = handle.tell()
    handle.seek(0, 2)
    length = handle.tell()

    if length == offset:
        raise NoNewData

    handle.seek(offset, 0)
    return handle.readline()
```

By wrapping this function in a `while` loop, I can turn it into a worker thread. When a new line is available, I call a given callback function to write it to the output log (see Item 48: “Accept Functions Instead of Classes for Simple Interfaces” for why to use a function interface for this instead of a class). When no data is available, the thread sleeps to reduce the amount of busy waiting caused by polling for new data. When the input file handle is closed, the worker thread exits:

通过将此函数包装在一个`while`循环中，我可以将其变成一个工作线程。当有新行可用时，调用给定的回调函数将其写入输出日志（见条目48：“对于简单接口，接受函数而不是类”解释为何使用函数接口而非类）。当没有数据可用时，线程会休眠以减少轮询导致的忙等待。当输入文件句柄关闭后，工作线程退出：

```
import time

def tail_file(handle, interval, write_func):
    while not handle.closed:
        try:
            line = readline(handle)
        except NoNewData:
            time.sleep(interval)
        else:
            write_func(line)
```

Now, I can start one worker thread per input file and unify their output into a single output file. Below, the `write` closure function (see Item 33: “Know How Closures Interact with Variable Scope and `nonlocal` ”) needs to use a `Lock` instance (see Item 69: “Use `Lock` to Prevent Data Races in Threads”) in order to serialize writes to the output stream and make sure that there are no intra-line conflicts:

现在，我可以为每个输入文件启动一个工作线程，并将它们的输出统一到单个输出文件中。以下示例中，`write`闭包函数（见条目33：“了解闭包如何与变量作用域和`nonlocal`交互”）需要使用`Lock`实例（见条目69：“使用`Lock`防止线程中的数据竞争”）以序列化对输出流的写入，确保没有行内冲突：

```
from threading import Lock, Thread

def run_threads(handles, interval, output_path):
    with open(output_path, "wb") as output:
        lock = Lock()

        def write(data):
            with lock:
                output.write(data)

        threads = []
        for handle in handles:
            args = (handle, interval, write)
            thread = Thread(target=tail_file, args=args)
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()
```

As long as an input file handle is still alive, its corresponding worker thread will also stay alive. That means it’s sufficient to wait for the `join` method from each thread to complete in order to know that the whole process is done.

只要输入文件句柄仍然存活，其对应的工作线程也将保持存活。这意味着等待每个线程的`join`方法完成就足以知道整个过程已完成。

Given a set of input paths and an output path, I can call `run_threads` and confirm that it works as expected. How the input file handles are created or separately closed isn’t important in order to demonstrate this code’s behavior, nor is the output verification function—defined in `confirm_merge` that follows—which is why I’ve left them out here:

给定一组输入路径和一个输出路径，我可以调用`run_threads`并确认其按预期工作。输入文件句柄是如何创建或单独关闭的并不重要，以展示这段代码的行为；输出验证函数——定义在随后的`confirm_merge`中——也是如此，因此我在此处省略了它们：

```
def confirm_merge(input_paths, output_path):
    ...
input_paths = ...
handles = ...
output_path = ...
run_threads(handles, 0.1, output_path)
confirm_merge(input_paths, output_path)
```

With this threaded implementation as the starting point, how can I incrementally convert this code to use `asyncio` and coroutines instead? There are two approaches: top-down and bottom-up.

以这个线程实现作为起点，如何逐步将这段代码转换为使用`asyncio`和协程？有两种方法：自顶向下和自底向上。

### Top-down (自顶向下)

Top-down means starting at the highest parts of a codebase, like in the `main` entry points, and working down to the individual functions and classes that are the leaves of the call hierarchy. This approach can be useful when you maintain a lot of common modules that you use across many different programs. By porting the entry points first, you can wait to port the common modules until you’re already using coroutines everywhere else.

自顶向下意味着从代码库的最高层开始，比如在`main`入口点，然后向下工作到调用层次结构末尾的各个函数和类。这种方法在维护许多跨多个不同程序使用的通用模块时可能很有用。通过先迁移入口点，可以等到已经在其他地方使用协程后再迁移通用模块。

The concrete steps are:

1. Change a top function to use `async def` instead of `def` .
2. Wrap all of its calls that do I/O——potentially blocking the event loop——to use `asyncio.run_in_executor` instead.
3. Ensure that the resources or callbacks used by `run_in_executor` invocations are properly synchronized (i.e., using `Lock` , or the `asyncio.run_coroutine_threadsafe` function with a fan-in event loop instance).
4. Try to eliminate `get_event_loop` and `run_in_executor` calls by moving downward through the call hierarchy and converting intermediate functions and methods to coroutines (following the first three steps).

具体步骤如下：

1. 将顶级函数改为使用`async def`而不是`def`。
2. 包装所有执行I/O的操作——可能会阻塞事件循环——以使用`asyncio.run_in_executor`。
3. 确保由`run_in_executor`调用使用的资源或回调正确同步（即，使用`Lock`，或使用`asyncio.run_coroutine_threadsafe`函数与一个集中式的事件循环实例）。
4. 尝试通过调用层次结构向下移动并转换中间函数和方法来消除`get_event_loop`和`run_in_executor`调用（遵循前三个步骤）。


Here, I apply steps 1-3 to the `run_threads` function:

在这里，我对`run_threads`函数应用步骤1-3：

```
import asyncio

# TODO: Verify this is no longer needed
#
# On Windows, a ProactorEventLoop can't be created within
# threads because it tries to register signal handlers. This
# is a work-around to always use the SelectorEventLoop policy
# instead. See: https://bugs.python.org/issue33792
# policy = asyncio.get_event_loop_policy()
# policy._loop_factory = asyncio.SelectorEventLoop
async def run_tasks_mixed(handles, interval, output_path):
    loop = asyncio.get_event_loop()

    output = await loop.run_in_executor(None, open, output_path, "wb")
    try:

        async def write_async(data):
            await loop.run_in_executor(None, output.write, data)

        def write(data):
            coro = write_async(data)
            future = asyncio.run_coroutine_threadsafe(coro, loop)
            future.result()

        tasks = []
        for handle in handles:
            task = loop.run_in_executor(
                None, tail_file, handle, interval, write
            )
            tasks.append(task)

        await asyncio.gather(*tasks)
    finally:
        await loop.run_in_executor(None, output.close)
```

The `run_in_executor` method instructs the event loop to run a given function—which may include blocking I/O—using a `ThreadPoolExecutor` , ensuring it doesn’t interfere with the event loop’s thread (see Item 74: “Consider `ThreadPoolExecutor` When Threads Are Necessary for Concurrency” for background). By making multiple calls to `run_in_executor` without corresponding `await` expressions, the `run_tasks_mixed` coroutine fans-out to have one concurrent line of execution for each input file. Then, the `asyncio.gather` fans-in the `tail_file` threads until they all complete (see Item 71: “Know How to Recognize When Concurrency Is Necessary” for more about fan-out and fan-in).

`run_in_executor`方法指示事件循环使用`ThreadPoolExecutor`运行给定函数——该函数可能包括阻塞I/O——确保它不会干扰事件循环所在的线程（见条目74：“当线程对并发是必要时考虑使用`ThreadPoolExecutor`”获取背景信息）。通过多次调用`run_in_executor`而不使用相应的`await`表达式，`run_tasks_mixed`协程展开成每个输入文件的一条并发执行线。然后，`asyncio.gather`将这些`tail_file`线程集中，直到它们全部完成（见条目71：“了解何时认识到并发是必要的”了解更多关于展开和集中的内容）。

This code eliminates the need for the `Lock` instance in the `write` helper by using `asyncio.run_coroutine_threadsafe `. This function allows plain old threads to call a coroutine——`write_async` in this case——and have it execute in the event loop from the explicitly-supplied main thread. This effectively synchronizes the worker threads together, ensuring that all writes to the output file happen one at a time. Once the `asyncio.TaskGroup` awaitable is resolved, I can assume that all writes to the output file have also completed, and thus I can `close` the output file handle without having to worry about race conditions.

此代码通过使用`asyncio.run_coroutine_threadsafe`消除了`write`辅助函数中对`Lock`实例的需求。此函数允许普通旧线程调用协程——在这种情况下是`write_async`——并让它在显式提供的主线程的事件循环中执行。这有效地同步了工作线程，确保所有对输出文件的写入一次只发生一次。一旦解析了`asyncio.TaskGroup`可等待对象，就可以假定对输出文件的所有写入也已完成，因此可以在不担心竞争条件的情况下`close`输出文件句柄。

I can verify that this code works as expected. I use the `asyncio.run` function to start the coroutine and run the main event loop:

我可以验证这段代码是否按预期工作。我使用`asyncio.run`函数启动协程并运行主事件循环：

```
input_paths = ...
handles = ...
output_path = ...

tmpdir, input_paths, handles, output_path = setup()

asyncio.run(run_tasks_mixed(handles, 0.1, output_path))

confirm_merge(input_paths, output_path)
```

Now, I can apply step #4 to the `run_tasks_mixed` function by moving down the call stack. I can redefine the `tail_file` dependent function to be an asynchronous coroutine instead of doing blocking I/O by following steps 1-3:

现在，我可以通过向下移动调用栈来对`run_tasks_mixed`函数应用步骤#4。我可以重新定义依赖的`tail_file`函数，使其成为异步协程而不是执行阻塞I/O，通过遵循步骤1-3：

```
async def tail_async(handle, interval, write_func):
    loop = asyncio.get_event_loop()

    while not handle.closed:
        try:
            line = await loop.run_in_executor(None, readline, handle)
        except NoNewData:
            await asyncio.sleep(interval)
        else:
            await write_func(line)
```

The new `tail_async` function allows me to eliminate the `run_tasks_mixed` function’s calls to `run_coroutine_threadsafe` and the `write` wrapper function. I can also use `asyncio.TaskGroup` (new in Python 3.11) to manage fan-out and fan-in for the `tail_async` coroutines, further shortening the code:

新的`tail_async`函数使我能够删除`run_tasks_mixed`函数中对`run_coroutine_threadsafe`和`write`包装函数的调用。我还可以使用`asyncio.TaskGroup`（Python 3.11新增）来管理`tail_async`协程的展开和集中，进一步缩短代码：

```
async def run_tasks(handles, interval, output_path):
    loop = asyncio.get_event_loop()

    output = await loop.run_in_executor(None, open, output_path, "wb")
    try:

        async def write_async(data):
            await loop.run_in_executor(None, output.write, data)

        async with asyncio.TaskGroup() as group:
            for handle in handles:
                group.create_task(
                    tail_async(handle, interval, write_async)
                )
    finally:
        await loop.run_in_executor(None, output.close)
```

I can verify that run_tasks works as expected, too:

我也可以验证`run_tasks`是否按预期工作：

```
input_paths = ...
handles = ...
output_path = ...
asyncio.run(run_tasks(handles, 0.1, output_path))
confirm_merge(input_paths, output_path)
```

It’s possible to continue this refactoring approach and convert `readline` into an asynchronous coroutine as well. However, that function requires so many blocking file I/O operations that it doesn’t seem worth porting given how much that would reduce the clarity of the code. In some situations, it makes sense to move everything to `asyncio` , and in others it doesn’t.

继续这种重构方法并将`readline`转换为异步协程也是可能的。然而，该函数需要如此多的阻塞文件I/O操作，鉴于这样会降低代码的清晰度，似乎不值得迁移。在某些情况下，将所有内容移至`asyncio`是有意义的，在其他情况下则不然。

### Bottom-up (自底向上)

The bottom-up approach to adopting coroutines has four steps that are similar to the steps of the top-down style, but the process traverses the call hierarchy in the opposite direction: from leaves to entry points.

采用协程的自底向上方法有四个具体的步骤，类似于自顶向下的风格，但过程遍历调用层次结构的方向相反：从叶子到入口点。

The concrete steps are:

1. Create a new asynchronous coroutine version of each leaf function that you’re trying to port.
2. Change the existing synchronous functions so they call the coroutine versions and run the event loop instead of implementing any real asynchronous behavior.
3. Move up a level of the call hierarchy, make another layer of coroutines, and replace existing calls to synchronous functions with calls to the coroutines defined in step #1.
4. Delete synchronous wrappers around coroutines created in step #2 as you stop requiring them to glue the pieces together.

具体步骤如下：

1. 为您试图迁移的每个叶函数创建一个新的异步协程版本。
2. 更改现有同步函数，使它们调用协程版本并在调用事件循环时不实现任何真正的异步行为。
3. 向上调用层次结构，创建另一层协程，并将对同步函数的现有调用替换为步骤#1中定义的协程调用。
4. 当不再需要用来粘合各部分的同步包装器时，删除步骤#2中创建的同步包装器。

For the example above, I would start with the `tail_file` function since I decided that the `readline` function should keep using blocking I/O. I can rewrite `tail_file` so it merely wraps the `tail_async` coroutine that I defined above. The provided `write_func` , which uses blocking I/O, can be run by the `write_async` function using `run_in_executor` , making it compatible with what `tail_async` expects. To run each worker coroutine until it finishes, I can create an event loop for each `tail_file` thread and then call its `run_until_complete` method. This method will block the current thread and drive the event loop until the `tail_async` coroutine exits, achieving the same behavior as the threaded, blocking I/O version of `tail_file` :

对于上面的例子，我会从`tail_file`函数开始，因为我决定`readline`函数应继续使用阻塞I/O。我可以重写`tail_file`，使其仅仅是包装了上面定义的`tail_async`协程。所提供的`write_func`，使用阻塞I/O，可以通过`write_async`函数使用`run_in_executor`运行，使其与`tail_async`期望的兼容。为了运行每个工作协程直到完成，我可以为每个`tail_file`线程创建一个事件循环，然后调用它的`run_until_complete`方法。此方法将阻塞当前线程并驱动事件循环直到`tail_async`协程退出，从而实现与阻塞I/O版本的`tail_file`相同的行为：

```
def tail_file(handle, interval, write_func):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def write_async(data):
        await loop.run_in_executor(None, write_func, data)

    coro = tail_async(handle, interval, write_async)
    loop.run_until_complete(coro)
```

This new `tail_file` function is a drop-in replacement for the old one. I can verify that everything works as expected by calling `run_threads` again:

这个新的`tail_file`函数是旧函数的直接替代品。通过再次调用`run_threads`，我可以验证一切是否如预期工作：

```
input_paths = ...
handles = ...
output_path = ...

tmpdir, input_paths, handles, output_path = setup()

run_threads(handles, 0.1, output_path)

confirm_merge(input_paths, output_path)
```

After wrapping `tail_async` with `tail_file` , the next step is to convert the `run_threads` function over to a coroutine. This ends up being the same work as step 4 of the top-down approach above, so at this point, the styles converge.

在用`tail_file`包装`tail_async`之后，下一步是将`run_threads`函数转换为协程。这最终与上述自顶向下方法的第4步相同，因此此时，两种风格汇聚。

This is all a great start for adopting `asyncio` , but there’s even more that you could do in order to increase the responsiveness of your program (see Item 78: “Maximize Responsiveness of `asyncio` Event Loops with `async`-friendly Worker Threads”).

这一切都是采用`asyncio`的一个良好开端，但还有更多可以做的事情以提高程序的响应能力（见条目78：“通过`async`友好的工作线程最大化`asyncio`事件循环的响应能力”）。

**Things to Remember**

- The awaitable `run_in_executor` method of the `asyncio` event loop enables coroutines to run synchronous functions in `ThreadPoolExecutor` worker threads. This facilitates top-down migrations to `asyncio` .
- The `run_until_complete` method of the `asyncio` event loop enables synchronous code to run a coroutine until it finishes. The `asyncio.run_coroutine_threadsafe` function provides the same functionality across thread boundaries. Together these help with bottom-up migrations to `asyncio` .

**注意事项**

- `asyncio`事件循环的可等待`run_in_executor`方法使协程能够在`ThreadPoolExecutor`工作线程中运行同步函数。这有助于向`asyncio`的自顶向下迁移。
- `asyncio`事件循环的`run_until_complete`方法使同步代码能够运行协程直到其完成。`asyncio.run_coroutine_threadsafe`函数提供了跨线程边界的相同功能。一起使用它们有助于向`asyncio`的自底向上迁移。