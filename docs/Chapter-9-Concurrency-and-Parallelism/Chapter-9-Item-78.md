# Chapter 9: Concurrency and Parallelism (并发与并行)

## Item 78: Maximize Responsiveness of `asyncio` Event Loops with `async`-friendly Worker Threads (让 `asyncio` 更高效响应：用兼容 `async` 的工作线程提升事件循环性能)

In the previous item I showed how to migrate to `asyncio` incrementally (see Item 77: “Mix Threads and Coroutines to Ease the Transition to `asyncio` ” for background and the implementation of various functions below). The resulting coroutine properly tails input files and merges them into a single output:

在上一个条目中，我展示了如何逐步迁移到 `asyncio`（背景和下面各种函数的实现请参见条目77：“混合使用线程和协程以简化到 `asyncio` 的迁移”）。生成的协程正确地跟踪输入文件并将它们合并成一个单一的输出：

```
import asyncio

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

This code is quite noisy and repetitive with all of the `run_in_executor` boilerplate to handle the boundary between synchronous and asynchronous function calls. The function would be a lot shorter if I accepted the fact that calls to `open` , `close` , and `write` for the `output` file handle will block the event loop—for the purpose of merging multiple file handles like this, it's functionally correct, too:

这段代码由于所有处理同步和异步函数调用边界的 `run_in_executor` 样板代码显得相当嘈杂且重复。如果接受 `output` 文件句柄的 `open`、`close` 和 `write` 调用会阻塞事件循环这一事实，这个函数会简短得多——就合并多个文件句柄而言，这在功能上也是正确的：

```
async def run_tasks_simpler(handles, interval, output_path):
    with open(output_path, "wb") as output:  # Changed

        async def write_async(data):
            output.write(data)  # Changed

        async with asyncio.TaskGroup() as group:
            for handle in handles:
                group.create_task(
                    tail_async(handle, interval, write_async)
                )
```

However, avoiding `run_in_executor` like this is bad because these operations all require making system calls to the program’s host operating system, which may block the event loop for significant amounts of time and prevent other coroutines from making progress. This could hurt overall responsiveness and increase latency, especially for programs with event loops that are shared by many components, such as highly concurrent servers.

然而，像这样避免使用 `run_in_executor` 是不好的，因为这些操作都需要对程序运行的操作系统进行系统调用，这可能会显著阻塞事件循环，并阻止其他协程继续执行。这可能会影响整体响应速度并增加延迟，尤其是在那些由许多组件共享事件循环的程序中，例如高并发服务器。

But how bad is it to block the event loop, really? And how often does it happen in practice? I can detect when this problem occurs in a real program by passing the `debug=True` parameter to the `asyncio.run` function. Here, I show how the file and line of a bad coroutine, presumably blocked on a slow system call, can be identified:

但是，阻塞事件循环实际上有多糟糕？在实践中发生得有多频繁？我可以通过将 `debug=True` 参数传递给 `asyncio.run` 函数来检测在实际程序中出现这个问题的情况。这里展示了一个坏协程（可能是阻塞在一个慢速系统调用上）的文件和行号是如何被识别出来的：

```
import time

async def slow_coroutine():
    time.sleep(0.5)  # Simulating slow I/O

asyncio.run(slow_coroutine(), debug=True)
>>>
Executing <Task finished name='Task-1' coro=<slow
done, defined at example.py:61> result=None creat
.../asyncio/runners.py:100> took 0.506 seconds
...
```

If I want the most responsive program possible, then I need to minimize the potential system calls that are made from within the main event loop. Using `run_in_executor` is one way to do that, but it requires a lot of `boilerplate`, as shown above. One potentially better alternative is to create a new Thread subclass (see Item 68: “Use Threads for Blocking I/O, Avoid for Parallelism”) that encapsulates everything required to write to the output file using its own independent event loop:

如果我希望程序尽可能具有响应性，那么就需要最小化从主事件循环内部进行的潜在系统调用。使用 `run_in_executor` 是一种方法，但如上所示，它需要大量的样板代码。一种可能更好的替代方法是创建一个新的 `Thread` 子类（参见条目68：“为阻塞 I/O 使用线程，避免用于并行”），该子类封装了使用其自己的独立事件循环写入输出文件所需的一切：

```
class WriteThread(Thread):
    def __init__(self, output_path):
        super().__init__()
        self.output_path = output_path
        self.output = None
        self.loop = asyncio.new_event_loop()

    def run(self):
        asyncio.set_event_loop(self.loop)
        with open(self.output_path, "wb") as self.output:
            self.loop.run_forever()

        # Run one final round of callbacks so the await on
        # stop() in another event loop will be resolved.
        self.loop.run_until_complete(asyncio.sleep(0))
```

Coroutines in other threads can directly call and `await` on the `write` method of this class, since it’s merely a thread-safe wrapper around the `real_write` method that actually does the I/O. This eliminates the need for a `Lock` (see Item 69: “Use `Lock` to Prevent Data Races in Threads”):

其他线程中的协程可以直接调用并 `await` 这个类的 `write` 方法，因为它只是实际进行 I/O 的 `real_write` 方法的一个线程安全包装器。这消除了对 `Lock` 的需求（参见条目69：“使用 `Lock` 防止线程中的数据竞争”）：

```
class WriteThread(Thread):
    ...
    async def real_write(self, data):
        self.output.write(data)

    async def write(self, data):
        coro = self.real_write(data)
        future = asyncio.run_coroutine_threadsafe(
            coro, self.loop)
        await asyncio.wrap_future(future)
```

Other coroutines can tell the worker thread when to stop in a thread-safe manner, using similar boilerplate:

其他协程可以以线程安全的方式告知工作线程何时停止，使用类似的样板代码：

```
class WriteThread(Thread):
    ...
    async def real_stop(self):
        self.loop.stop()

    async def stop(self):
        coro = self.real_stop()
        future = asyncio.run_coroutine_threadsafe(
            coro, self.loop)
        await asyncio.wrap_future(future)
```

I can also define the `__aenter__` and `__aexit__` methods to allow this class to be used in `with` statements (see Item 82: “Consider `contextlib` and `with` Statements for Reusable `try` / `finally` Behavior” and Item 76: “Know How to Port Threaded I/O to `asyncio` ” for background). This ensures that the worker thread starts and stops at the right times without slowing down the main event loop thread:

我还可以定义 `__aenter__` 和 `__aexit__` 方法，以允许此类在 `with` 语句中使用（参见条目82：“考虑使用 `contextlib` 和 `with` 语句以实现可重用的 `try` / `finally` 行为”和条目76：“了解如何将线程化的 I/O 移植到 `asyncio`”以获取背景信息）。这确保了工作线程在正确的时间启动和停止，而不会减慢主事件循环线程：

```
class WriteThread(Thread):
    ...
    async def __aenter__(self):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.start)
        return self

    async def __aexit__(self, *_):
        await self.stop()
```

With this new `WriteThread` class, I can refactor `run_tasks` into a fully asynchronous version that’s easy to read, doesn’t interfere with the main event loop’s default executor, and completely avoids running slow system calls in the main event loop thread:

有了这个新的 `WriteThread` 类，我可以重构 `run_tasks`，使其成为一个完全异步的版本，易于阅读，不会干扰主事件循环的默认执行器，并且完全避免在主事件循环线程中运行缓慢的系统调用：

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

async def tail_async(handle, interval, write_func):
    loop = asyncio.get_event_loop()

    while not handle.closed:
        try:
            line = await loop.run_in_executor(None, readline, handle)
        except NoNewData:
            await asyncio.sleep(interval)
        else:
            await write_func(line)

async def run_fully_async(handles, interval, output_path):
    async with (
        WriteThread(output_path) as output,
        asyncio.TaskGroup() as group,
    ):
        for handle in handles:
            group.create_task(
                tail_async(handle, interval, output.write)
            )
```

I can verify that this works as expected, given a set of input handles and an output file path:

鉴于一组输入句柄和一个输出文件路径，我可以验证这是按预期工作的：

```
def confirm_merge(input_paths, output_path):
    found = collections.defaultdict(list)
    with open(output_path, "rb") as f:
        for line in f:
            for path in input_paths:
                if line.find(path.encode()) == 0:
                    found[path].append(line)

    expected = collections.defaultdict(list)
    for path in input_paths:
        with open(path, "rb") as f:
            expected[path].extend(f.readlines())

    for key, expected_lines in expected.items():
        found_lines = found[key]
        assert expected_lines == found_lines

input_paths = ...
handles = ...
output_path = ...

tmpdir, input_paths, handles, output_path = setup()

asyncio.run(run_fully_async(handles, 0.1, output_path))

confirm_merge(input_paths, output_path)
```

**Things to Remember**

- Making system calls in coroutines——including blocking I/O and starting threads——can reduce program responsiveness and increase the perception of latency.
- Pass the `debug=True` parameter to `asyncio.run` in order to detect when certain coroutines are preventing the event loop from reacting quickly.
- To improve the readability of code that must span the boundary between asynchronous and synchronous execution, consider defining helper thread classes that provide coroutine-friendly interfaces.

**注意事项**

- 在协程中进行系统调用——包括阻塞式I/O和启动线程——可能会降低程序的响应能力，并增加感知的延迟。
- 将`debug=True`参数传给`asyncio.run`，以检测某些协程何时阻止事件循环快速响应。
- 为了提高跨越异步和同步执行边界代码的可读性，可以考虑定义提供协程友好接口的帮助线程类。