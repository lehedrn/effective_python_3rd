# Chapter 11: Performance (性能)

## Item 99: Consider `memoryview` and `bytearray` for Zero-Copy Interactions with `bytes` (在与 `bytes` 进行零拷贝交互时考虑使用 `memoryview` 和 `bytearray`)

Although Python isn’t able to parallelize CPU-bound computation without extra effort (see Item 79: “Consider `concurrent.futures` for True Parallelism” and Item 94: “Know When and How to Replace Python with Another Programming Language”), it is able to support high-throughput, parallel I/O in a variety of ways (see Item 68: “Use Threads for Blocking I/O, Avoid for Parallelism” and Item 75: “Achieve Highly Concurrent I/O with Coroutines”). That said, it’s surprisingly easy to use these I/O tools the wrong way and reach the conclusion that the language is too slow for even I/O-bound workloads.

尽管 Python 无法在没有额外努力的情况下并行化 CPU 密集型计算（参见条目79：“考虑使用 `concurrent.futures` 实现真正的并行”和条目94：“知道何时以及如何用其他编程语言替换 Python”），但它能够以多种方式支持高吞吐量的并行 I/O（参见条目68：“为阻塞 I/O 使用线程，避免用于并行”和条目75：“使用协程实现高度并发的 I/O”）。话虽如此，错误地使用这些 I/O 工具是很常见的，从而得出结论认为该语言对于即使是 I/O 密集型工作负载也太慢了。

For example, say that you’re building a media server to stream television or movies over a network to users so they can watch without having to download the video data in advance. One of the key features of such a system is the ability for users to move forward or backward in the video playback so they can skip or repeat parts. In the client program, I can implement this by requesting a chunk of data from the server corresponding to the new time index selected by the user:

例如，假设你正在构建一个媒体服务器，通过网络流式传输电视或电影给用户，以便他们无需预先下载视频数据即可观看。此类系统的关键功能之一是用户可以在视频播放中前后移动，从而跳过或重复部分。在客户端程序中，我可以通过请求服务器对应于用户选择的新时间索引的数据块来实现这一点：

```
def timecode_to_index(video_id, timecode):
    return 1234
    # Returns the byte offset in the video data

def request_chunk(video_id, byte_offset, size):
    pass
    # Returns size bytes of video_id's data from the offset

video_id = ...
timecode = "01:09:14:28"
byte_offset = timecode_to_index(video_id, timecode)
size = 20 * 1024 * 1024
video_data = request_chunk(video_id, byte_offset, size)
```

How would you implement the server-side handler that receives the `request_chunk` request and returns the corresponding 20MB chunk of video data? For the sake of this example, I assume that the command and control parts of the server have already been hooked up (see Item 76: “Know How to Port Threaded I/O to `asyncio` ” for what that requires). I focus here on the last steps where the requested chunk is extracted from gigabytes of video data that’s cached in memory, and is then sent over a socket back to the client. Here’s what the implementation would look like:

你会如何实现接收 `request_chunk` 请求并返回相应的20MB视频数据块的服务端处理程序？在这个例子中，我假设服务器的命令和控制部分已经连接好（参见条目76：“知道如何将线程化的 I/O 移植到 `asyncio` 中”了解所需内容）。这里我关注的是从缓存在内存中的数GB视频数据中提取请求的块，并通过套接字将其发送回客户端的最后步骤。以下是实现的样子：

```
class NullSocket:
    def __init__(self):
        self.handle = open(os.devnull, "wb")

    def send(self, data):
        self.handle.write(data)

socket = ...             # socket connection to client
video_data = ...         # bytes containing data for video_id
byte_offset = ...        # Requested starting position
size = 20 * 1024 * 1024  # Requested chunk size
import os

socket = NullSocket()
video_data = 100 * os.urandom(1024 * 1024)
byte_offset = 1234

chunk = video_data[byte_offset : byte_offset + size]
socket.send(chunk)
```

The latency and throughput of this code will come down to two factors: how much time it takes to slice the 20MB video `chunk` from `video_data` , and how much time the socket takes to transmit that data to the client. If I assume that the socket is infinitely fast, I can run a microbenchmark using the `timeit` built-in module to understand the performance characteristics of slicing `bytes` instances this way to create chunks (see Item 14: “Know How to Slice Sequences” for background):

此代码的延迟和吞吐量将取决于两个因素：从 `video_data` 切片出20MB的视频 `chunk` 所需的时间，以及套接字将这些数据传输给客户端所需的时间。如果假设套接字是无限快的，可以使用内置模块 `timeit` 运行微基准测试来理解以这种方式切片 `bytes` 实例以创建块的性能特征（背景请参见条目14：“知道如何切片序列”）：

```
import timeit

def run_test():
    chunk = video_data[byte_offset : byte_offset + size]
    # Call socket.send(chunk), but ignoring for benchmark

result = (
    timeit.timeit(
        stmt="run_test()",
        globals=globals(),
        number=100,
    )
    / 100
)

print(f"{result:0.9f} seconds")

>>>
0.004925669 seconds
```

It took roughly 5 milliseconds to extract the 20MB slice of data to transmit to the client. That means the overall throughput of my server is limited to a theoretical maximum of 20MB / 5 milliseconds = 4GB / second, since that’s the fastest I can extract the video data from memory. My server will also be limited to 1 CPU-second / 5 milliseconds = 200 clients requesting new chunks in parallel, which is tiny compared to the tens of thousands of simultaneous connections that tools like the `asyncio` built-in module can support. The problem is that slicing a `bytes` instance causes the underlying data to be copied, which takes CPU time.

结果大约需要5毫秒来提取要传输给客户端的20MB数据。这意味着我的服务器的整体吞吐量被限制在理论最大值20MB / 5毫秒 = 4GB / 秒，因为这是我能从内存中提取视频数据的最快速度。我的服务器还将受限于每CPU秒1 / 5毫秒 = 200个并行请求新数据块的客户端，这与像 `asyncio` 这样的内置模块能支持的数万个同时连接相比非常小。问题是切片 `bytes` 实例会导致底层数据被复制，占用CPU时间。

A better way to write this code is using Python’s built-in `memoryview` type, which exposes CPython’s high-performance buffer protocol to programs. The buffer protocol is a low-level C API that allows the Python runtime and C extensions (see Item 96: “Consider Extension Modules to Maximize Performance and Ergonomics”) to access the underlying data buffers that are behind objects like `bytes` instances. The best part about `memoryview` instances is that slicing them results in another `memoryview` instance without copying the underlying data. Here, I create a `memoryview` wrapping a `bytes` instance and inspect a slice of it:

更好的方法是使用Python的内置 `memoryview` 类型，它向程序公开了CPython的高性能缓冲区协议。缓冲区协议是一个低级的C API，允许Python运行时和C扩展（参见条目96：“考虑扩展模块以最大化性能和易用性”）访问像 `bytes` 实例背后的底层数据缓冲区。最好的部分是 `memoryview` 实例切片会生成另一个 `memoryview` 实例而不复制底层数据。在这里，我创建了一个包装 `bytes` 实例的 `memoryview` 并检查其一部分：

```
data = b"shave and a haircut, two bits"
view = memoryview(data)
chunk = view[12:19]
print(chunk)
print("Size:           ", chunk.nbytes)
print("Data in view:   ", chunk.tobytes())
print("Underlying data:", chunk.obj)

>>>
<memory at 0x105407940>
Size: 7
Data in view: b'haircut'
Underlying data: b'shave and a haircut, two bits
```

By enabling zero-copy operations, `memoryview` can provide enormous speedups for code that needs to quickly process large amounts of memory, such as numerical C-extensions like NumPy and I/O bound programs like this one. Here, I replace the simple `bytes` slicing above with `memoryview` slicing instead, and repeat the same microbenchmark:

通过启用零拷贝操作，`memoryview` 可以为需要快速处理大量内存的代码提供巨大的加速，比如像NumPy这样的数值C扩展和像这个I/O绑定程序。在这里，我用 `memoryview` 切片替换了上面简单的 `bytes` 切片，并重复相同的微基准测试：

```
video_view = memoryview(video_data)

def run_test():
    chunk = video_view[byte_offset : byte_offset + size]
    # Call socket.send(chunk), but ignoring for benchmark

result = (
    timeit.timeit(
        stmt="run_test()",
        globals=globals(),
        number=100,
    )
    / 100
)

print(f"{result:0.9f} seconds")

>>>
0.000000250 seconds
```

The result is 250 nanoseconds. Now the theoretical maximum throughput of my server is 20MB / 250 nanoseconds = 80 TB/second. For parallel clients, I can theoretically support up to 1 CPU-second / 250 nanoseconds = 4 million. That’s more like it! This means that now my program is entirely bound by the underlying performance of the socket connection to the client, not by CPU constraints.

结果是250纳秒。现在，我的服务器的理论最大吞吐量是20MB / 250纳秒 = 80 TB/秒。对于并行客户端，理论上我可以支持高达1 CPU秒 / 250纳秒 = 4百万个。这才更像样！这意味着现在我的程序完全受客户端套接字连接的基础性能限制，而不是受CPU约束。

Now, imagine that the data must flow in the other direction, where some clients are sending live video streams to the server in order to broadcast them to other users. In order to do this, I need to store the latest video data from the user in a cache that other clients can read from. Here’s what the implementation of reading 1MB of new data from the incoming client would look like:

现在，想象一下数据必须反向流动，一些客户端将实时视频流发送到服务器以便广播给其他用户。为了做到这一点，我需要将来自用户的最新视频数据存储在一个缓存中，其他客户端可以从那里读取。下面是从未知客户端读取1MB新数据的实现：

```
class FakeSocket:

    def recv(self, size):
        return video_view[byte_offset : byte_offset + size]

    def recv_into(self, buffer):
        source_data = video_view[byte_offset : byte_offset + size]
        buffer[:] = source_data

socket = ...        # socket connection to the client
video_cache = ...   # Cache of incoming video stream
byte_offset = ...   # Incoming buffer position
size = 1024 * 1024  # Incoming chunk size
socket = FakeSocket()
video_cache = video_data[:]
byte_offset = 1234

chunk = socket.recv(size)
video_view = memoryview(video_cache)
before = video_view[:byte_offset]
after = video_view[byte_offset + size :]
new_cache = b"".join([before, chunk, after])
```

The `socket.recv` method will return a `bytes` instance. I can splice the new data with the existing cache at the current `byte_offset` by using simple slicing operations and the `bytes.join` method. To understand the performance of this, I can run another microbenchmark. I’m using a dummy socket implementation so the performance test is only for the memory operations, not the I/O interaction:

`socket.recv` 方法将返回一个 `bytes` 实例。通过使用简单的切片操作和 `bytes.join` 方法，我可以将新数据与当前 `byte_offset` 处的现有缓存拼接在一起。为了了解其性能，我可以运行另一个微基准测试。我使用了一个虚拟套接字实现，因此性能测试仅针对内存操作，而不是I/O交互：

```
def run_test():
    chunk = socket.recv(size)
    before = video_view[:byte_offset]
    after = video_view[byte_offset + size :]
    new_cache = b"".join([before, chunk, after])

result = (
    timeit.timeit(
        stmt="run_test()",
        globals=globals(),
        number=100,
    )
    / 100
)

print(f"{result:0.9f} seconds")

>>>
0.033520550 seconds
```

It takes 33 milliseconds to receive 1MB and update the video cache. That means my maximum receive throughput is 1MB / 33 milliseconds = 31MB / second, and I’m limited to 31MB / 1MB = 31 simultaneous clients streaming in video data this way. This doesn’t scale.

接收1MB并更新视频缓存需要33毫秒。这意味着我的最大接收吞吐量是1MB / 33毫秒 = 31MB / 秒，并且我受限于31MB / 1MB = 31个同时通过这种方式流式传输视频数据的客户端。这并不具有可扩展性。

A better way to write this code is to use Python’s built-in `bytearray` type in conjunction with `memoryview` . One limitation with `bytes` instances is that they are read-only, and don’t allow for individual indexes to be updated:

一种更好的编写这段代码的方法是结合使用 Python 内置的 `bytearray` 类型和 `memoryview` 。`bytes` 实例的一个限制是它们是只读的，不允许单独的索引被更新：

```
my_bytes = b"hello"
my_bytes[0] = 0x79
>>>
Traceback ...
TypeError: 'bytes' object does not support item a
```

The `bytearray` type is like a mutable version of `bytes` that allows for arbitrary positions to be overwritten. `bytearray` uses integers for its values instead of `bytes`:

`bytearray` 类型类似于 `bytes` 的可变版本，允许任意位置被覆盖。`bytearray` 使用整数作为其值类型：

```
my_array = bytearray(b"hello")
my_array[0] = 0x79
print(my_array)
>>>
bytearray(b'yello')
```

A `memoryview` can also be used to wrap a `bytearray` . When you slice such a `memoryview` , the resulting object can be used to assign data to a particular portion of the underlying buffer. This avoids the copying costs from above that were required to splice the `bytes` instances back together after data was received from the client:

`memoryview` 也可以用来包装 `bytearray`。当你切分这样的 `memoryview` 时，生成的对象可以用来将数据分配给底层缓冲区的特定部分。这避免了上述从客户端接收数据后拼接 `bytes` 实例所需的复制成本：

```
my_array = bytearray(b"row, row, row your boat")
my_view = memoryview(my_array)
write_view = my_view[3:13]
write_view[:] = b"-10 bytes-"
print(my_array)
>>>
bytearray(b'row-10 bytes- your boat')
```

There are many libraries in Python that use the buffer protocol to receive or read data quickly, such as `socket.recv_into` and `RawIOBase.readinto` . The benefit of these methods is that they avoid allocating memory and creating another copy of the data——what’s received goes straight into an existing buffer. Here, I use `socket.recv_into` along with a `memoryview` slice to receive data into an underlying `bytearray` without the need for any splicing:

Python 中有许多库使用缓冲协议来快速接收或读取数据，例如 `socket.recv_into` 和 `RawIOBase.readinto`。这些方法的好处是它们避免了分配内存和创建数据的另一个副本——接收到的内容直接进入现有的缓冲区。在此，我使用 `socket.recv_into` 和 `memoryview` 片段将数据接收到基础 `bytearray` 中，而无需任何拼接：

```
video_array = bytearray(video_cache)
write_view = memoryview(video_array)
chunk = write_view[byte_offset : byte_offset + size]
socket.recv_into(chunk)
```

I can run another microbenchmark to compare the performance of this approach to the earlier example that used `socket.recv` .

我可以运行另一个微基准测试来比较这种方法与之前使用 `socket.recv` 的示例的性能。

```
def run_test():
    chunk = write_view[byte_offset : byte_offset + size]
    socket.recv_into(chunk)

result = (
    timeit.timeit(
        stmt="run_test()",
        globals=globals(),
        number=100,
    )
    / 100
)

print(f"{result:0.9f} seconds")

>>>
0.000033925 seconds
```

It took 33 microseconds to receive a 1MB video transmission. That means my server can support 1MB / 33 microseconds = 31GB / second of max throughput, and 31GB / 1MB = 31,000 parallel streaming clients. That’s the type of scalability that I’m looking for!

接收1MB的视频传输用了33微秒。这意味着我的服务器可以支持最高31GB / 秒的吞吐量，以及31GB / 1MB = 31,000个并行流媒体客户端。这才是我所追求的可扩展性！

**Things to Remember**
- The `memoryview` built-in type provides a zero-copy interface for reading and writing slices of objects that support Python’s high performance buffer protocol.
- The `bytearray` built-in type provides a mutable `bytes`-like type that can be used for zero-copy data reads with functions like `socket.recv_from` .
- A `memoryview` can wrap a `bytearray` , allowing for received data to be spliced into an arbitrary buffer location without copying costs.

**注意事项**
- `memoryview` 内建类型为读写支持 Python 高性能缓冲协议的对象的切片提供了零拷贝接口。
- `bytearray` 内建类型提供了一个类似 `bytes` 的可变类型，可用于与 `socket.recv_from` 等函数一起进行零拷贝的数据读取。
- `memoryview` 可以包装 `bytearray`，允许将接收到的数据无缝插入到任意缓冲区位置而无需复制成本。