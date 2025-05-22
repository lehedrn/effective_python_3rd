# Chapter 9: Concurrency and Parallelism (并发与并行)

## Item 67: Use `subprocess` to Manage Child Processes (使用 `subprocess` 管理子进程)

Python has battle-hardened libraries for running and managing child processes. This makes Python a great language for gluing together other tools, such as command-line utilities. When existing shell scripts get complicated, as they often do over time, graduating them to a rewrite in Python for the sake of readability and maintainability is a natural choice.

Python 拥有经过实践检验的库来运行和管理子进程。这使得 Python 成为粘合其他工具（如命令行实用程序）的绝佳语言。当现有的 shell 脚本随着时间推移变得复杂时，将其升级为用 Python 重写以提高可读性和可维护性是一个自然的选择。

Child processes started by Python are able to run in parallel, enabling you to use Python to consume all of the CPU cores of your machine and maximize the throughput of your programs. Although Python itself may be CPU bound (see Item 68: “Use Threads for Blocking I/O, Avoid for Parallelism”), it’s easy to use Python to drive and coordinate CPU-intensive workloads.

由 Python 启动的子进程能够并行运行，使您能够利用 Python 使用机器的所有 CPU 核心，并最大化程序的吞吐量。尽管 Python 本身可能是受 CPU 限制的语言（参见条目68：“对阻塞 I/O 使用线程，避免用于并行”），但使用 Python 驱动和协调 CPU 密集型工作负载却很容易。

Python has many ways to run subprocesses (e.g., `os.popen` , `os.exec*` ), but the best choice for managing child processes is to use the `subprocess` built-in module. Running a child process with `subprocess` is simple. Here, I use the module’s `run` convenience function to start a process, read its output, and verify that it terminated cleanly:

Python 有许多方式可以运行子进程（例如 `os.popen`、`os.exec*`），但是管理子进程的最佳选择是使用内置的 `subprocess` 模块。使用 `subprocess` 运行一个子进程很简单。在这里，我使用模块的 `run` 便捷函数启动一个进程，读取其输出，并验证它是否干净地终止：

```
import subprocess

# Enable these lines to make this example work on Windows
# import os
# os.environ['COMSPEC'] = 'powershell'
result = subprocess.run(
    ["echo", "Hello from the child!"],
    capture_output=True,
    # Enable this line to make this example work on Windows
    # shell=True,
    encoding="utf-8",
)

result.check_returncode()  # No exception means it exited cleanly
print(result.stdout)
>>>
Hello from the child!
```

---

> Note  
The examples in this item assume that your system has the `echo` , `sleep` , and `openssl` commands available. On Windows, this may not be the case. Please refer to the full example code for this item online to see specific directions on how to run these snippets on Windows.

> 注意  
该条目中的示例假设您的系统上可用 `echo`、`sleep` 和 `openssl` 命令。在 Windows 上可能不是这样。请参考在线的本条目完整示例代码，查看如何在 Windows 上运行这些片段的具体说明。
---

Child processes run independently from their parent process, the Python interpreter. If you create a subprocess using the `Popen` class instead of the `run` function, you can poll child process status periodically while Python does other work:

子进程独立于它们的父进程（即 Python 解释器）运行。如果您使用 `Popen` 类而不是`run`函数创建子进程，则可以在 Python 执行其他工作时定期轮询子进程状态：

```
# Use this line instead to make this example work on Windows
# proc = subprocess.Popen(['sleep', '1'], shell=True)
proc = subprocess.Popen(["sleep", "1"])
while proc.poll() is None:
    print("Working...")
    # Some time-consuming work here
    import time

    time.sleep(0.3)

print("Exit status", proc.poll())

>>>
Working...
Working...
Working...
Working...
Exit status 0
```

Decoupling the child process from the parent frees up the parent process to run many child processes in parallel. Here, I do this by starting all the child processes together with `Popen` upfront:

将子进程从父进程中解耦释放了父进程，使其可以并行运行许多子进程。在这里，我通过提前使用 `Popen` 一起启动所有子进程来实现这一点：

```
import time

start = time.perf_counter()
sleep_procs = []
for _ in range(10):
    # Use this line instead to make this example work on Windows
    # proc = subprocess.Popen(['sleep', '1'], shell=True)
    proc = subprocess.Popen(["sleep", "1"])
    sleep_procs.append(proc)
```

Later, I can wait for them to finish their I/O and terminate with the `communicate` method:

稍后，我可以使用 `communicate` 方法等待它们完成其 I/O 并终止：

```
for proc in sleep_procs:
    proc.communicate()

end = time.perf_counter()
delta = end - start
print(f"Finished in {delta:.3} seconds")

>>>
Finished in 1.01 seconds
```

If these processes ran in sequence, the total delay would be 10 seconds or more rather than the ~1 second that I measured.

如果这些进程按顺序运行，总延迟将是10秒或更长时间，而不是我测量的大约1秒。

You can also pipe data from a Python program into a subprocess and retrieve its output. This allows you to utilize many other programs to do work in parallel. For example, say that I want to use the `openssl` command-line tool to encrypt some data. Starting the child process with command-line arguments and I/O pipes is easy:

还可以将数据从 Python 程序管道传输到子进程并检索其输出。这允许您利用许多其他程序并行执行工作。例如，假设我想使用 `openssl` 命令行工具加密一些数据。使用命令行参数和 I/O 管道启动子进程非常简单：

```
import os

# On Windows, after installing OpenSSL, you may need to
# alias it in your PowerShell path with a command like:
# $env:path = $env:path + ";C:\Program Files\OpenSSL-Win64\bin"

def run_encrypt(data):
    env = os.environ.copy()
    env["password"] = "zf7ShyBhZOraQDdE/FiZpm/m/8f9X+M1"
    proc = subprocess.Popen(
        ["openssl", "enc", "-des3", "-pbkdf2", "-pass", "env:password"],
        env=env,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )
    proc.stdin.write(data)
    proc.stdin.flush()  # Ensure that the child gets input
    return proc
```

Here, I pipe random bytes into the encryption function, but in practice this input pipe would be fed data from user input, a file handle, a network socket, and so on:

这里，我将随机字节传入加密函数，但在实践中，这个输入管道会接收用户输入、文件句柄、网络套接字等数据：

```
procs = []
for _ in range(3):
    data = os.urandom(10)
    proc = run_encrypt(data)
    procs.append(proc)
```

The child processes run in parallel and consume their input. Here, I wait for them to finish and then retrieve their final output. The output is random encrypted bytes as expected:

子进程并行运行并消费它们的输入。在这里，我等待它们完成然后获取它们的最终输出。输出是预期的随机加密字节：

```
for proc in procs:
    out, _ = proc.communicate()
    print(out[-10:])

>>>
b'\x02a_\xd3\xd3\x9a\xd0\x8f\x14|'
b'S\x9c\x1a\x919\x9a-P\x0c\x1f'
b'\x1a\x7f\x1e\xbf\xac\xe5A>\xa3\xdd'
```

It’s also possible to create chains of parallel processes, just like UNIX pipelines, connecting the output of one child process to the input of another, and so on. Here’s a function that starts the `openssl` command-line tool as a subprocess to generate a Whirlpool hash of the input stream:

也可以创建类似于 UNIX 管道链的并行进程，将一个子进程的输出连接到另一个子进程的输入，依此类推。以下是一个函数，它启动 `openssl` 命令行工具作为一个子进程，生成输入流的 Whirlpool 哈希：

```
def run_hash(input_stdin):
    return subprocess.Popen(
        ["openssl", "dgst", "-sha256", "-binary"],
        stdin=input_stdin,
        stdout=subprocess.PIPE,
    )
```

Now, I can kick off one set of processes to encrypt some data and another set of processes to subsequently hash their encrypted output. Note that I have to be careful with how the `stdout` instance of the upstream process is retained by the Python interpreter process that’s starting this pipeline of child processes:

现在，我可以启动一组进程来加密一些数据，另一组进程随后对其加密输出进行哈希处理。请注意，我必须小心 Python 解释器进程如何保留上游进程的 `stdout` 实例：

```
encrypt_procs = []
hash_procs = []
for _ in range(3):
    data = os.urandom(100)

    encrypt_proc = run_encrypt(data)
    encrypt_procs.append(encrypt_proc)

    hash_proc = run_hash(encrypt_proc.stdout)
    hash_procs.append(hash_proc)

    # Ensure that the child consumes the input stream and
    # the communicate() method doesn't inadvertently steal
    # input from the child. Also lets SIGPIPE propagate to
    # the upstream process if the downstream process dies.
    encrypt_proc.stdout.close()
    encrypt_proc.stdout = None
```

The I/O between the child processes happens automatically once they are started. All I need to do is wait for them to finish and print the final output:

一旦它们被启动，子进程之间的 I/O 就会自动发生。我需要做的就是等待它们完成并打印最终输出：

```
for proc in encrypt_procs:
    proc.communicate()
    assert proc.returncode == 0

for proc in hash_procs:
    out, _ = proc.communicate()
    print(out[-10:])
    assert proc.returncode == 0

>>>
b'\xc6\n\x8a"cg\x85\xd2\x81|'
b'\x14\r\xc6J\xb0\xb0\xbf\x0c2X'
b'@\x90$\xcc\xc7\xf4\x08\x19Y\x0b'
```

If I’m worried about the child processes never finishing or somehow blocking on input or output pipes, I can pass the `timeout` parameter to the `communicate` method. This causes an exception to be raised if the child process hasn’t finished within the time period, giving me a chance to terminate the misbehaving subprocess:

如果担心子进程永远不会完成，或者可能在输入或输出管道上阻塞，可以向 `communicate` 方法传递 `timeout` 参数。这会在子进程未在规定时间内完成时引发异常，给我机会终止行为异常的子进程：

```
proc = subprocess.Popen(["sleep", "10"])
try:
    proc.communicate(timeout=0.1)
except subprocess.TimeoutExpired:
    proc.terminate()
    proc.wait()

print("Exit status", proc.poll())

>>>
Exit status -15
```

**Things to Remember**
- Use the `subprocess` module to run child processes and manage their input and output streams.
- Child processes run in parallel with the Python interpreter, enabling you to maximize your usage of CPU cores.
- Use the `run` convenience function for simple usage, and the `Popen` class for advanced usage like UNIX-style pipelines.
- Use the `timeout` parameter of the communicate method to avoid deadlocks and hanging child processes.

**注意事项**
- 使用 `subprocess` 模块运行子进程并管理其输入和输出流。
- 子进程与 Python 解释器并行运行，使您能够最大化 CPU 核心的使用。
- 对于简单的用法，请使用 `run` 便捷函数；对于高级用法（如 UNIX 风格的管道），请使用 `Popen` 类。
- 使用 `communicate` 方法的 `timeout` 参数以避免死锁和挂起的子进程。