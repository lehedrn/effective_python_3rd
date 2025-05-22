# Chapter 9: Concurrency and Parallelism (并发与并行)

## Item 69: Use `Lock` to Prevent Data Races in Threads (使用 `Lock` 防止线程中的数据竞争)

After learning about the global interpreter lock (GIL) (see Item 68: “Use Threads for Blocking I/O, Avoid for Parallelism”), many new Python programmers assume they can forgo using mutual-exclusion locks (also called mutexes) in their code altogether. If the GIL is already preventing Python threads from running on multiple CPU cores in parallel, it must also act as a lock for a program’s data structures, right? Some testing on types like lists and dictionaries may even show that this assumption appears to hold.

在了解了全局解释器锁（GIL）之后（参见条目68：“对阻塞I/O使用线程，避免并行”），许多新的Python程序员会认为他们完全可以不在代码中使用互斥锁（也称为互斥体）。如果GIL已经阻止了Python线程并行运行在多个CPU核心上，那它肯定也会充当程序数据结构的锁，对吧？一些针对列表和字典等类型的测试甚至可能显示这种假设似乎成立。

But beware, this is not truly the case. The GIL will not protect you. Although only one Python thread runs at a time, a thread’s operations on data structures can be interrupted between any two bytecode instructions in the Python interpreter. This is dangerous if you access the same objects from multiple threads simultaneously. The invariants of your data structures could be violated at practically any time because of these interruptions, potentially putting your program in a corrupted state.

但是请注意，这并不是真实情况。GIL不会保护你。尽管一次只运行一个Python线程，但由于Python解释器可以在任何两个字节码指令之间中断线程的操作，线程对数据结构的操作可能会被中断。如果你从多个线程同时访问相同的对象，这是很危险的。由于这些中断，你的数据结构不变性实际上随时都可能被破坏，可能导致程序处于损坏状态。

For example, say that I want to write a program that counts many things in parallel, like sampling light levels from a network of sensors. Imagine that each sensor has its own worker thread because reading from the sensor requires blocking I/O. After each sensor measurement, the worker thread increments a shared counter variable with the number of photons received:

例如，假设我想编写一个并行计数很多事物的程序，比如从传感器网络采样光水平。想象一下每个传感器都有自己的工作线程，因为读取传感器需要阻塞I/O。每次传感器测量后，工作线程会根据接收到的光子数量递增一个共享计数器变量：

```
counter = 0

def read_sensor(sensor_index):
    # Returns sensor data or raises an exception
    # Nothing actually happens here, but this is where
    # the blocking I/O would go.
    pass

def get_offset(data):
    # Always returns 1 or greater
    return 1

def worker(sensor_index, how_many):
    global counter
    # I have a barrier in here so the workers synchronize
    # when they start counting, otherwise it's hard to get a race
    # because the overhead of starting a thread is high.
    BARRIER.wait()
    for _ in range(how_many):
        data = read_sensor(sensor_index)
        # Note that the value passed to += must be a function call or other
        # non-trivial expression in order to cause the CPython eval loop to
        # check whether it should release the GIL. This is a side-effect of
        # an optimization. See https://github.com/python/cpython/commit/4958f5d69dd2bf86866c43491caf72f774ddec97 for details.
        counter += get_offset(data)
```

Here, I run one `worker` thread for each sensor in parallel and wait for them all to finish their readings:

这里，我为每个传感器并行运行一个`worker`线程，并等待它们全部完成其读取操作：

```
from threading import Thread

how_many = 10**6
sensor_count = 4

from threading import Barrier

BARRIER = Barrier(sensor_count)

threads = []
for i in range(sensor_count):
    thread = Thread(target=worker, args=(i, how_many))
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()

expected = how_many * sensor_count
print(f"Counter should be {expected}, got {counter}")

>>>
Counter should be 4000000, got 1980032
```

Given how `get_offset` always returns 1 or more, it appears that the result is way off! What happened here? How could something so simple go so wrong, especially since only one Python interpreter thread can run at a time due to the GIL?

鉴于`get_offset`始终返回1或更大的值，结果显然大错特错了！发生了什么？如此简单的东西怎么会出错呢？特别是因为由于GIL的存在，只有一个Python解释器线程可以运行？

The answer is preemption. The Python interpreter enforces fairness between all of the threads that are executing to ensure they get a roughly equal amount of processing time. To do this, Python suspends a thread as it’s running and resumes another thread in turn. The problem is that you don’t know exactly when Python will suspend your threads. A thread can even be paused seemingly halfway through what looks like an atomic operation.

答案就是抢占。Python解释器在执行的所有线程之间强制公平以确保它们获得大致相等的处理时间。为此，Python会在运行时暂停一个线程并依次恢复另一个线程。问题是，你不知道Python何时会暂停你的线程。即使在一个看似原子操作的中间，线程也可能被暂停。

That’s what happened in this case, on this line in the worker function from above:

这就是在这种情况下发生的情况，在上面的worker函数中的这一行：

```
counter += get_offset(data)
```

The `+=` operator used on the `counter` variable actually instructs Python to do three separate operations behind the scenes. The statement above is equivalent to this:

在`counter`变量上使用的`+=`运算符实际上指示Python在幕后执行三个独立的操作。上述语句相当于以下内容：

```
value = counter
delta = get_offset(data)
result = value + delta
counter = result
```

Python threads incrementing the counter might be suspended between any two of these operations. This is problematic if the way the operations interleave causes old versions of `value` to be assigned to the counter. Here’s an example of bad interaction between two threads, A and B:

正在递增计数器的Python线程可能在这三个操作之间的任何时候被挂起。如果操作的交错方式导致旧版本的 `value` 被分配给计数器，这就会出现问题。以下是两个线程A和B之间的不良交互示例：

```
# Running in Thread A
value_a = counter
delta_a = get_offset(data_a)
# Context switch to Thread B
value_b = counter
delta_b = get_offset(data_b)
result_b = value_b + delta_b
counter = result_b
# Context switch back to Thread A
result_a = value_a + delta_a
counter = result_a
```

Thread B interrupted thread A before it had completely finished. Thread B ran and finished, but then thread A resumed mid-execution, overwriting all of thread B’s progress in incrementing the counter. This is exactly what happened in the light sensor example above.

线程B在线程A尚未完全完成之前中断了它。线程B运行并完成了，但随后线程A恢复执行，覆盖了线程B对计数器递增的所有进展。这正是上面提到的光传感器示例中发生的情况。

To prevent data races like these, and other forms of data structure corruption, Python includes a robust set of tools in the `threading` built-in module. The simplest and most useful of them is the Lock class, a mutual-exclusion lock (mutex).

为了防止此类数据竞争以及其他形式的数据结构损坏，Python在`threading`内置模块中包含了一套强大的工具。其中最简单且最有用的是Lock类，一种互斥锁。

By using a lock, I can have the `Counter` class protect its current value against simultaneous accesses from multiple threads. Only one thread will be able to acquire the lock at a time. Here, I use a `with` statement to acquire and release the lock; the extra level of indentation makes it easier to see which code is executing while the lock is held (see Item 82: “Consider `contextlib` and `with` Statements for Reusable `try / finally` Behavior” for background):

通过使用锁，我可以使`Counter`类保护其当前值免受多个线程的同时访问。一次只有一个线程能够获取锁。在此处，我使用`with`语句来获取和释放锁；额外的缩进级别使得更容易看到哪些代码是在持有锁时执行的（有关背景，请参见条目82：“考虑使用`contextlib`和`with`语句以实现可重用的`try / finally`行为”）：

```
from threading import Lock

counter = 0
counter_lock = Lock()

def locking_worker(sensor_index, how_many):
    global counter
    BARRIER.wait()
    for _ in range(how_many):
        data = read_sensor(sensor_index)
        with counter_lock:                  # Added
            counter += get_offset(data)
```

Now, I run the senor threads as before, but use a `locking_worker` instead:

现在，我像以前一样运行传感器线程，但使用`locking_worker`：

```
BARRIER = Barrier(sensor_count)

for i in range(sensor_count):
    thread = Thread(target=locking_worker, args=(i, how_many))
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()

expected = how_many * sensor_count
print(f"Counter should be {expected}, got {counter}")

>>>
Counter should be 4000000, got 4000000
```

The result is exactly what I expect. The `Lock` solved the problem.

结果正好是我期望的。`Lock`解决了问题。

**Things to Remember**

- Even though Python has a global interpreter lock, you’re still responsible for protecting against data races between the threads in your programs.
- Your programs will corrupt their data structures if you allow multiple threads to modify the same objects without mutual exclusion locks (mutexes).
- Use the `Lock` class from the `threading` built-in module to enforce your program’s invariants between multiple threads.

**注意事项**

- 即使Python有全局解释器锁，您仍需负责保护程序中线程间的数据竞争。
- 如果允许多个线程在没有互斥锁的情况下修改同一对象，您的程序将破坏其数据结构。
- 使用`threading`内置模块中的`Lock`类在多个线程之间强制执行程序的不变性。