# Chapter 9: Concurrency and Parallelism (并发与并行)

## Item 76: Know How to Port Threaded I/O to `asyncio` (了解如何将线程I/O移植到`asyncio`)

Once you understand the advantage of coroutines (see Item 75: “Achieve Highly Concurrent I/O with Coroutines”), it may seem daunting to port an existing codebase to use them. Luckily, Python’s support for asynchronous execution is well integrated into the language. This makes it straightforward to move code that does threaded, blocking I/O over to coroutines and asynchronous I/O.

一旦你理解了协程的优势（参见条目75：“使用协程实现高度并发的I/O”），将现有代码库迁移到使用它们可能会显得令人生畏。幸运的是，Python对异步执行的支持已经很好地集成到了语言中。这使得将进行阻塞式I/O和线程的代码迁移到协程和异步I/O变得直接明了。

For example, say that I have a TCP-based server for playing a "guess the number" game. The server takes `lower` and `upper` parameters that determine the range of numbers to consider. Then, the server returns guesses for integer values in that range as they are requested by the client.

例如，假设我有一个基于TCP的服务器，用于玩“猜数字”游戏。服务器接收确定数字范围的`lower`和`upper`参数。然后，服务器在客户端请求时返回该范围内的整数猜测值。

Finally, the server collects reports from the client on whether each of those numbers was closer (warmer) or further away (colder) from the client’s secret number.

最后，服务器从客户端收集关于每个数字是更接近（更暖）还是更远（更冷）其秘密数字的报告。

The most common way to build this type of client / server system is using blocking I/O and threads (see Item 68: “Use Threads for Blocking I/O, Avoid for Parallelism”). To do this, I need a helper class that can manage sending and receiving messages. For my purposes, each line sent or received represents a command to be processed:

构建此类客户端/服务器系统的最常见方法是使用阻塞I/O和线程（参见条目68：“为阻塞I/O使用线程，避免为并行性使用线程”）。为此，我需要一个能够管理发送和接收消息的帮助类。对于我的目的，发送或接收的每一行都代表一个要处理的命令：

```
class EOFError(Exception):
    pass

class Connection:
    def __init__(self, connection):
        self.connection = connection
        self.file = connection.makefile("rb")

    def send(self, command):
        line = command + "\n"
        data = line.encode()
        self.connection.send(data)

    def receive(self):
        line = self.file.readline()
        if not line:
            raise EOFError("Connection closed")
        return line[:-1].decode()
```

The server is implemented as a class that handles one connection at a time and maintains the game’s session state:

服务器实现为一个类，一次处理一个连接，并维护游戏会话状态：

```
import random

WARMER = "Warmer"
COLDER = "Colder"
SAME = "Same"
UNSURE = "Unsure"
CORRECT = "Correct"

class UnknownCommandError(Exception):
    pass

class ServerSession(Connection):
    def __init__(self, *args):
        super().__init__(*args)
        self.clear_state()

```

It has one primary method that handles incoming commands from the client and dispatches them to methods as needed. Here, I use a `match` statement to parse the semi-structured data (see Item 9: “Consider `match` for Destructuring in Flow Control, Avoid When `if` Statements Are Sufficient” for details):

它有一个主要的方法来处理来自客户端的传入命令，并根据需要将它们分派给相应的方法。在这里，我使用`match`语句来解析半结构化数据（有关详细信息，请参见条目9：“考虑在流程控制中解构时使用`match`，当`if`语句足够时避免使用”）：

```
class ServerSession(Connection):
    def __init__(self, *args):
        super().__init__(*args)
        self.clear_state()

    def loop(self):
        while command := self.receive():
            match command.split(" "):
                case "PARAMS", lower, upper:
                    self.set_params(lower, upper)
                case ["NUMBER"]:
                    self.send_number()
                case "REPORT", decision:
                    self.receive_report(decision)
                case ["CLEAR"]:
                    self.clear_state()
                case _:
                    raise UnknownCommandError(command)
```

The first command sets the lower and upper bounds for the numbers that the server is trying to guess:

第一个命令设置服务器尝试猜测的数字的上下限：

```
class ServerSession(Connection):
    ...
    def set_params(self, lower, upper):
        self.clear_state()
        self.lower = int(lower)
        self.upper = int(upper)
```

The second command makes a new guess based on the previous state that’s stored in the `ServerSession` instance. Specifically, this code ensures that the server will never try to guess the same number more than once per parameter assignment:

第二个命令基于存储在`ServerSession`实例中的先前状态生成一个新的猜测：

```
class ServerSession(Connection):
    ...
    def next_guess(self):
        if self.secret is not None:
            return self.secret

        while True:
            guess = random.randint(self.lower, self.upper)
            if guess not in self.guesses:
                return guess

    def send_number(self):
        guess = self.next_guess()
        self.guesses.append(guess)
        self.send(format(guess))
```

The third command receives the decision from the client of whether the guess was warmer, colder, the same, or correct, and it updates the `ServerSession` state accordingly:

第三个命令接收客户端关于猜测是否更暖、更冷、相同或正确的决定，并相应地更新`ServerSession`状态：

```
class ServerSession(Connection):
    ...
    def receive_report(self, decision):
        last = self.guesses[-1]
        if decision == CORRECT:
            self.secret = last

        print(f"Server: {last} is {decision}")
```

The last command clears the state to end a game whether it was successful or not:

最后一个命令清除状态以结束无论成功与否的游戏：

```
class ServerSession(Connection):
    ...
    def clear_state(self):
        self.lower = None
        self.upper = None
        self.secret = None
        self.guesses = []
```

Games are initiated using a `with` statement to ensure that state is correctly managed on the server side (see Item 82: “Consider `contextlib` and `with` Statements for Reusable `try` / `finally` Behavior” for background and Item 78: “Maximize Responsiveness of `asyncio` Event Loops with `async`-friendly Worker Threads” for another example). This `new_game` function sends the first and last commands to the server, and provides a context object to use for the duration of the game:

游戏通过使用`with`语句启动，以确保服务器端的状态得到正确管理（参见条目82：“考虑使用`contextlib`和`with`语句以实现可重用的`try` / `finally`行为”了解背景知识，以及条目78：“使用`async`友好的工作线程最大化`asyncio`事件循环的响应能力”作为另一个示例）。这个`new_game`函数发送游戏的第一个和最后一个命令，并提供一个在游戏持续期间使用的上下文对象：

```
import contextlib
import time

@contextlib.contextmanager
def new_game(connection, lower, upper, secret):
    print(
        f"Guess a number between {lower} and {upper}!"
        f" Shhhhh, it's {secret}."
    )
    connection.send(f"PARAMS {lower} {upper}")
    try:
        yield ClientSession(
            connection.send,
            connection.receive,
            secret,
        )
    finally:
        # Make it so the output printing matches what you expect
        time.sleep(0.1)
        connection.send("CLEAR")
```

I use a stateful class with helper methods for game actions and references to manage each game session (see Item 48: “Accept Functions Instead of Classes for Simple Interfaces” for why I pass in `send` and `receive` explicitly):

我使用一个有状态的类，带有辅助方法和引用，以管理每场游戏会话（参见条目48：“对于简单接口，接受函数而不是类”了解为什么我显式传递`send`和`receive`）：

```
import math

class ClientSession:
    def __init__(self, send, receive, secret):
        self.send = send
        self.receive = receive
        self.secret = secret
        self.last_distance = None
```

New guesses are requested from the server using a method that implements the second command:

新的猜测通过实现第二个命令的方法从服务器请求：

```
class ClientSession:
    ...
    def request_number(self):
        self.send("NUMBER")
        data = self.receive()
        return int(data)
```

Whether each guess from the server was warmer or colder than the last is reported using the third command:

服务器每次猜测的结果是否比上一次更暖或更冷，通过第三个命令报告：

```
class ClientSession:
    ...
    def report_outcome(self, number):
        new_distance = math.fabs(number - self.secret)

        if new_distance == 0:
            decision = CORRECT
        elif self.last_distance is None:
            decision = UNSURE
        elif new_distance < self.last_distance:
            decision = WARMER
        elif new_distance > self.last_distance:
            decision = COLDER
        else:
            decision = SAME

        self.last_distance = new_distance

        self.send(f"REPORT {decision}")
        return decision
```

The game session object can be iterated over (see Item 21: “Be Defensive When Iterating Over Arguments” for background) to make new, unique guesses repeatedly until the correct answer is found:

游戏会话对象可以被迭代（参见条目21：“在迭代参数时保持防御性”了解背景）以重复生成新且唯一的猜测，直到找到正确答案：

```
class ClientSession:
    ...
    def __iter__(self):
        while True:
            number = self.request_number()
            decision = self.report_outcome(number)
            yield number, decision
            if decision == CORRECT:
                return
```

I can run the server by having one thread listen on a socket and spawn additional threads to handle each new client connection:

我可以运行服务器，让一个线程监听套接字并生成额外的线程来处理每个新客户端连接：

```
import socket
from threading import Thread

def handle_connection(connection):
    with connection:
        session = ServerSession(connection)
        try:
            session.loop()
        except EOFError:
            pass

def run_server(address):
    with socket.socket() as listener:
        # Allow the port to be reused
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind(address)
        listener.listen()
        while True:
            connection, _ = listener.accept()
            thread = Thread(
                target=handle_connection,
                args=(connection,),
                daemon=True,
            )
            thread.start()
```

The client runs in the main thread and returns the results of the guessing game back to the caller. Perhaps a bit awkwardly, this code exercises a variety of Python language features ( `for` loops, `with` statements, generators, comprehensions, the iterator protocol) so that below I can show what it takes to port each of these over to using coroutines:

客户端在主线程中运行，并将猜数字游戏的结果返回给调用者。或许有些笨拙，这段代码练习了各种Python语言特性（`for`循环、`with`语句、生成器、推导式、迭代器协议），以便在下面展示将其迁移到使用协程所需的步骤：

```
def run_client(address):
    with socket.create_connection(address) as server_sock:
        server = Connection(server_sock)

        with new_game(server, 1, 5, 3) as session:
            results = [outcome for outcome in session]

        with new_game(server, 10, 15, 12) as session:
            for outcome in session:
                results.append(outcome)

        with new_game(server, 1, 3, 2) as session:
            it = iter(session)
            while True:
                try:
                    outcome = next(it)
                except StopIteration:
                    break
                else:
                    results.append(outcome)

    return results
```

Finally, I can glue all of this together and confirm that it works as expected.

最后，我可以将所有这些整合在一起并确认它按预期工作。

```
def main():
    address = ("127.0.0.1", 1234)
    server_thread = Thread(
        target=run_server, args=(address,), daemon=True
    )
    server_thread.start()

    results = run_client(address)
    for number, outcome in results:
        print(f"Client: {number} is {outcome}")

main()

>>>
Guess a number between 1 and 5! Shhhhh, it's 3.
Server: 4 is Unsure
Server: 1 is Colder
Server: 5 is Same
Server: 3 is Correct
Guess a number between 10 and 15! Shhhhh, it's 12
Server: 11 is Unsure
Server: 10 is Colder
Server: 12 is Correct
Guess a number between 1 and 3! Shhhhh, it's 2.
Server: 3 is Unsure
Server: 2 is Correct
Client: 4 is Unsure
Client: 1 is Colder
Client: 5 is Same
Client: 3 is Correct
Client: 11 is Unsure
Client: 10 is Colder
Client: 12 is Correct
Client: 3 is Unsure
Client: 2 is Correct
```

How much effort is needed to convert this example to using `async` , `await` , and the `asyncio` built-in module?

将此示例转换为使用`async`、`await`和`asyncio`内置模块需要多少努力？

First, I need to update my `Connection` class to provide coroutine methods for `send` and `receive` instead of blocking I/O methods. I’ve marked each line that’s changed with a `# Changed` comment to make it clear what the delta is between this new example and the code above:

首先，我需要更新我的`Connection`类，以提供用于`send`和`receive`的协程方法，而不是阻塞I/O方法。我在每处更改的行上标记了一个`# Changed`注释，以明确显示此新示例与上面代码之间的差异：

```
class AsyncConnection:
    def __init__(self, reader, writer):      # Changed
        self.reader = reader                 # Changed
        self.writer = writer                 # Changed

    async def send(self, command):
        line = command + "\n"
        data = line.encode()
        self.writer.write(data)              # Changed
        await self.writer.drain()            # Changed

    async def receive(self):
        line = await self.reader.readline()  # Changed
        if not line:
            raise EOFError("Connection closed")
        return line[:-1].decode()
```

I can create another stateful class to represent the server session state for a single connection. The only changes here are the class’s name and inheriting from `AsyncConnection` instead of `Connection` :

我可以创建另一个有状态的类来表示单个连接的服务器会话状态。这里唯一的更改是类的名称和继承自`AsyncConnection`而不是`Connection`：

```
class AsyncServerSession(AsyncConnection):  # Changed
    def __init__(self, *args):
        super().__init__(*args)
        self.clear_state()
```

The primary entry point for the server’s command processing loop requires only minimal changes to become a coroutine:

服务器命令处理循环的主要入口点只需要进行最小的更改即可成为协程：

```
class AsyncServerSession(AsyncConnection):  # Changed
    ...
    async def loop(self):                       # Changed
        while command := await self.receive():  # Changed
            match command.split(" "):
                case "PARAMS", lower, upper:
                    self.set_params(lower, upper)
                case ["NUMBER"]:
                    await self.send_number()    # Changed
                case "REPORT", decision:
                    self.receive_report(decision)
                case ["CLEAR"]:
                    self.clear_state()
                case _:
                    raise UnknownCommandError(command)
```

No changes are required for handling the first command:

处理第一个命令不需要任何更改：

```
class AsyncServerSession(AsyncConnection):  # Changed
    ...
    def set_params(self, lower, upper):
        self.clear_state()
        self.lower = int(lower)
        self.upper = int(upper)
```

The only change required for the second command is allowing asynchronous I/O to be used when guesses are transmitted to the client:

处理第二个命令所需的唯一更改是在将猜测传输给客户端时允许使用异步I/O：

```
class AsyncServerSession(AsyncConnection):  # Changed
    ...
    def next_guess(self):
        if self.secret is not None:
            return self.secret

        while True:
            guess = random.randint(self.lower, self.upper)
            if guess not in self.guesses:
                return guess

    async def send_number(self):                    # Changed
        guess = self.next_guess()
        self.guesses.append(guess)
        await self.send(format(guess))              # Changed
```

No changes are required in the third and fourth commands:

第三个和第四个命令不需要任何更改：

```
class AsyncServerSession(AsyncConnection):  # Changed
    ...
    def receive_report(self, decision):
        last = self.guesses[-1]
        if decision == CORRECT:
            self.secret = last

        print(f"Server: {last} is {decision}")

    def clear_state(self):
        self.lower = None
        self.upper = None
        self.secret = None
        self.guesses = []
```

Initiating a new game on the client requires a few `async` and `await` keywords to be added for sending the first and last commands. It also needs to use the `asynccontextmanager` helper function from the `contextlib` built-in module:

在客户端启动新游戏需要添加几个`async`和`await`关键字，以用于发送第一个和最后一个命令。还需要使用`contextlib`内置模块中的`asynccontextmanager`辅助函数：

```
@contextlib.asynccontextmanager                              # Changed
async def new_async_game(connection, lower, upper, secret):  # Changed
    print(
        f"Guess a number between {lower} and {upper}!"
        f" Shhhhh, it's {secret}."
    )
    await connection.send(f"PARAMS {lower} {upper}")         # Changed
    try:
        yield AsyncClientSession(
            connection.send,
            connection.receive,
            secret,
        )
    finally:
        # Make it so the output printing is in
        # the same order as the threaded version.
        await asyncio.sleep(0.1)
        await connection.send("CLEAR")                       # Changed
```

The asynchronous version of the `ClientSession` class for representing game state has the same constructor as before:

用于表示游戏状态的`ClientSession`类的异步版本具有与之前相同的构造函数：

```
class AsyncClientSession:
    def __init__(self, send, receive, secret):
        self.send = send
        self.receive = receive
        self.secret = secret
        self.last_distance = None
```

The second command only requires the addition of `async` and `await` anywhere asynchronous behavior is required:

第二个命令仅需在需要异步行为的任何地方添加`async`和`await`：

```
class AsyncClientSession:
    ...
    async def request_number(self):
        await self.send("NUMBER")    # Changed
        data = await self.receive()  # Changed
        return int(data)
```

The third command only requires adding one `async` and one `await` keyword:

第三个命令仅需添加一个`async`和一个`await`关键字：

```
class AsyncClientSession:
    ...
    async def report_outcome(self, number):    # Changed
        new_distance = math.fabs(number - self.secret)

        if new_distance == 0:
            decision = CORRECT
        elif self.last_distance is None:
            decision = UNSURE
        elif new_distance < self.last_distance:
            decision = WARMER
        elif new_distance > self.last_distance:
            decision = COLDER
        else:
            decision = SAME

        self.last_distance = new_distance

        await self.send(f"REPORT {decision}")  # Changed
        return decision
```

To enable asynchronous iteration, I need to implement `__aiter__` instead of `__iter__` , with corresponding additions of async and await :

为了启用异步迭代，我需要实现`__aiter__`而不是`__iter__`，并相应地添加`async`和`await`：

```
class AsyncClientSession:
    ...
    async def __aiter__(self):                            # Changed
        while True:
            number = await self.request_number()          # Changed
            decision = await self.report_outcome(number)  # Changed
            yield number, decision
            if decision == CORRECT:
                return
```

The code that runs the server needs to be completely reimplemented to use the `asyncio` built-in module and its `start_server` function:

运行服务器的代码需要完全重新实现，以使用`asyncio`内置模块及其`start_server`函数：

```
import asyncio

async def handle_async_connection(reader, writer):
    session = AsyncServerSession(reader, writer)
    try:
        await session.loop()
    except EOFError:
        pass

async def run_async_server(address):
    server = await asyncio.start_server(
        handle_async_connection, *address
    )
    async with server:
        await server.serve_forever()
```

The `run_client` function that initiates the game requires changes on nearly every line. Any code that previously interacted with the blocking `socket` instances has to be replaced with `asyncio` versions of similar functionality (which are marked with `# New` below). All other lines in the function that require interaction with coroutines need to use async and `await` keywords, coroutine-specific functions like `aiter` , `anext` , or async-specific constants like `StopAsyncIteration` . If you forget to add one of these keywords in a necessary place, an exception will be raised at runtime.

发起游戏的`run_client`函数几乎每一行都需要更改。以前与阻塞`socket`实例交互的代码必须替换为`asyncio`类似功能的版本（在下面标记为`# New`）。函数中其他需要与协程交互的行需要使用`async`和`await`关键字、协程专用函数如`aiter`、`anext`或异步专用常量如`StopAsyncIteration`。如果忘记在一个必要位置添加其中一个关键字，将在运行时引发异常。

```
async def run_async_client(address):
    # Wait for the server to listen before trying to connect
    await asyncio.sleep(0.1)

    streams = await asyncio.open_connection(*address)  # New
    client = AsyncConnection(*streams)                 # New

    async with new_async_game(client, 1, 5, 3) as session:
        results = [outcome async for outcome in session]

    async with new_async_game(client, 10, 15, 12) as session:
        async for outcome in session:
            results.append(outcome)

    async with new_async_game(client, 1, 3, 2) as session:
        it = aiter(session)
        while True:
            try:
                outcome = await anext(it)
            except StopAsyncIteration:
                break
            else:
                results.append(outcome)

    _, writer = streams                                # New
    writer.close()                                     # New
    await writer.wait_closed()                         # New

    return results
```

What’s most interesting about `run_async_client` is that I didn’t have to restructure any of the substantive parts of interacting with the `AsyncClient` in order to port this function over to use coroutines. Each of the language features that I needed has a corresponding asynchronous version, which made the migration straightforward to do.

关于`run_async_client`最有趣的是，在将此函数迁移到使用协程时，我不必重构与`AsyncClient`交互的实质性部分。我需要的每个语言特性都有相应的异步版本，这使得迁移变得直接明了。

This transition won’t always be easy. For example, in the standard library, there are currently no asynchronous versions of the utility functions from `itertools` (see Item 24: “Consider `itertools` for Working with Iterators and Generators”). There’s also no asynchronous version of `yield from` (see Item 45: “Compose Multiple Generators with `yield from` ”), which makes it noisier to compose generators. Many community libraries help fill these gaps (see Item 116: “Know Where to Find Community-Built Modules”), but it can still take extra work depending on the complexity of your code.

这种过渡并不总是容易的。例如，在标准库中，目前还没有`itertools`实用函数的异步版本（参见条目24：“考虑使用`itertools`处理迭代器和生成器”）。也没有`yield from`的异步版本（参见条目45：“使用`yield from`组合多个生成器”），这使得组合生成器时更加嘈杂。许多社区库帮助填补了这些空白（参见条目116：“知道在哪里寻找社区构建的模块”），但根据代码的复杂性，可能仍需要额外的工作。

Finally, the glue needs to be updated to run this new asynchronous example end-to-end. I use the `asyncio.create_task` function to enqueue the server for execution on the event loop so that it runs in parallel with the client when the `await` expression is reached. This is another approach to causing fan-out with different behavior than the `asyncio.gather` function:

最后，胶水代码需要更新，以端到端地运行这个新的异步示例。我使用`asyncio.create_task`函数将服务器排队执行在事件循环上，这样在到达`await`表达式时，它能与客户端并行运行。这是另一种导致扇出的方法，行为不同于`asyncio.gather`函数：

```
async def main_async():
    address = ("127.0.0.1", 4321)

    server = run_async_server(address)
    asyncio.create_task(server)

    results = await run_async_client(address)
    for number, outcome in results:
        print(f"Client: {number} is {outcome}")


asyncio.run(main_async())
>>>
Guess a number between 1 and 5! Shhhhh, it's 3.
Server: 5 is Unsure
Server: 4 is Warmer
Server: 2 is Same
Server: 1 is Colder
Server: 3 is Correct
Guess a number between 10 and 15! Shhhhh, it's 12
Server: 14 is Unsure
Server: 10 is Same
Server: 15 is Colder
Server: 12 is Correct
Guess a number between 1 and 3! Shhhhh, it's 2.
Server: 2 is Correct
Client: 5 is Unsure
Client: 4 is Warmer
Client: 2 is Same
Client: 1 is Colder
Client: 3 is Correct
Client: 14 is Unsure
Client: 10 is Same
Client: 15 is Colder
Client: 12 is Correct
Client: 2 is Correct
```

This works as expected. The coroutine version is easier to follow because all of the interactions with threads have been removed. The `asyncio` built-in module also provides many helper functions that shorten the amount of socket boilerplate required to write a server like this.

这正如预期那样工作。协程版本更容易遵循，因为所有与线程的交互都被移除了。`asyncio`内置模块还提供了许多帮助函数，缩短了编写此类服务器所需的套接字样板代码量。

Your use case may be more difficult to port for a variety of reasons. The `asyncio` module has a vast number of I/O, synchronization, and task management features that could make adopting coroutines easier for you (see Item 77: “Mix Threads and Coroutines to Ease the Transition to `asyncio` ” and Item 78: “Maximize Responsiveness of `asyncio` Event Loops with `async`-friendly Worker Threads”). Be sure to check out the online documentation for the library (https://docs.python.org/3/library/asyncio.html) to understand its full potential.

您的用例可能由于多种原因而更难迁移。`asyncio`模块拥有大量I/O、同步和任务管理功能，可以使采用协程变得更加容易（参见条目77：“混合使用线程和协程以简化向`asyncio`的过渡”和条目78：“使用`async`友好的工作线程最大化`asyncio`事件循环的响应能力”）。请务必查看该库的在线文档（https://docs.python.org/3/library/asyncio.html）以了解其全部潜力。

**Things to Remember**

- Python provides asynchronous versions of `for` loops, `with` statements, generators, comprehensions, iterators, and library helper functions that can be used as drop-in replacements in coroutines.
- The `asyncio` built-in module makes it straightforward to port existing code that uses threads and blocking I/O over to coroutines and asynchronous I/O.

**注意事项**

- Python提供了`for`循环、`with`语句、生成器、推导式、迭代器及库帮助函数的异步版本，可在协程中用作替代方案。
- `asyncio`内置模块使将使用线程和阻塞I/O的现有代码迁移到协程和异步I/O变得简单明了。