"""
本文件演示了如何将基于线程的阻塞I/O代码移植到使用asyncio模块的异步I/O代码。
包含原始线程版本和转换后的异步版本，以及常见的错误示例和正确用法。

主要包含以下内容：
1. 原始线程版TCP服务器/客户端实现
2. 转换为asyncio的异步版本
3. 常见错误示例及正确写法
4. 完整可运行的示例

注意：所有示例都实现了相同的功能 - 一个"猜数字"游戏服务器和客户端
"""

import asyncio
import logging
import random
import socket
import time
from threading import Thread
from contextlib import contextmanager, asynccontextmanager
import math

# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 全局常量
WARMER = "Warmer"
COLDER = "Colder"
SAME = "Same"
UNSURE = "Unsure"
CORRECT = "Correct"


# ========================
# 原始线程版实现
# ========================

class EOFError(Exception):
    """连接关闭异常"""
    pass


class Connection:
    """同步TCP连接类"""

    def __init__(self, connection):
        self.connection = connection
        self.file = connection.makefile("rb")

    def send(self, command):
        """发送命令"""
        line = command + "\n"
        data = line.encode()
        self.connection.send(data)

    def receive(self):
        """接收响应"""
        line = self.file.readline()
        if not line:
            raise EOFError("Connection closed")
        return line[:-1].decode()


class UnknownCommandError(Exception):
    """未知命令异常"""
    pass


class ServerSession(Connection):
    """服务器会话处理类"""

    def __init__(self, *args):
        super().__init__(*args)
        self.clear_state()

    def loop(self):
        """主循环处理命令"""
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

    def set_params(self, lower, upper):
        """设置参数范围"""
        self.clear_state()
        self.lower = int(lower)
        self.upper = int(upper)

    def next_guess(self):
        """生成下一个猜测"""
        if self.secret is not None:
            return self.secret

        while True:
            guess = random.randint(self.lower, self.upper)
            if guess not in self.guesses:
                return guess

    def send_number(self):
        """发送猜测结果"""
        guess = self.next_guess()
        self.guesses.append(guess)
        self.send(str(guess))

    def receive_report(self, decision):
        """接收报告结果"""
        last = self.guesses[-1]
        if decision == CORRECT:
            self.secret = last
        logger.info(f"Server: {last} is {decision}")

    def clear_state(self):
        """清除状态"""
        self.lower = None
        self.upper = None
        self.secret = None
        self.guesses = []


@contextmanager
def new_game(connection, lower, upper, secret):
    """启动新游戏上下文管理器"""
    logger.info(f"Guess a number between {lower} and {upper}! Shhhhh, it's {secret}.")
    connection.send(f"PARAMS {lower} {upper}")
    try:
        yield ClientSession(
            connection.send,
            connection.receive,
            secret,
        )
    finally:
        # 等待确保输出顺序
        time.sleep(0.1)
        connection.send("CLEAR")


class ClientSession:
    """客户端会话类"""

    def __init__(self, send, receive, secret):
        self.send = send
        self.receive = receive
        self.secret = secret
        self.last_distance = None

    def request_number(self):
        """请求猜测"""
        self.send("NUMBER")
        data = self.receive()
        return int(data)

    def report_outcome(self, number):
        """报告结果"""
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

    def __iter__(self):
        """迭代协议"""
        while True:
            number = self.request_number()
            decision = self.report_outcome(number)
            yield number, decision
            if decision == CORRECT:
                return


def handle_connection(connection):
    """处理客户端连接"""
    with connection:
        session = ServerSession(connection)
        try:
            session.loop()
        except EOFError:
            pass


def run_server(address):
    """运行服务器"""
    with socket.socket() as listener:
        # 允许端口复用
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind(address)
        listener.listen()
        logger.info(f"Server started on {address}")
        while True:
            connection, _ = listener.accept()
            thread = Thread(
                target=handle_connection,
                args=(connection,),
                daemon=True,
            )
            thread.start()


def run_client(address):
    """运行客户端"""
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


# ========================
# 异步版本实现
# ========================

class AsyncConnection:
    """异步TCP连接类"""

    def __init__(self, reader, writer):
        self.reader = reader
        self.writer = writer

    async def send(self, command):
        """异步发送命令"""
        line = command + "\n"
        data = line.encode()
        self.writer.write(data)
        await self.writer.drain()

    async def receive(self):
        """异步接收响应"""
        line = await self.reader.readline()
        if not line:
            raise EOFError("Connection closed")
        return line[:-1].decode()


class AsyncServerSession(AsyncConnection):
    """异步服务器会话类"""

    def __init__(self, *args):
        super().__init__(*args)
        self.clear_state()

    async def loop(self):
        """异步主循环"""
        while command := await self.receive():
            match command.split(" "):
                case "PARAMS", lower, upper:
                    self.set_params(lower, upper)
                case ["NUMBER"]:
                    await self.send_number()
                case "REPORT", decision:
                    self.receive_report(decision)
                case ["CLEAR"]:
                    self.clear_state()
                case _:
                    raise UnknownCommandError(command)

    def set_params(self, lower, upper):
        """设置参数范围"""
        self.clear_state()
        self.lower = int(lower)
        self.upper = int(upper)

    def next_guess(self):
        """生成下一个猜测"""
        if self.secret is not None:
            return self.secret

        while True:
            guess = random.randint(self.lower, self.upper)
            if guess not in self.guesses:
                return guess

    async def send_number(self):
        """异步发送猜测"""
        guess = self.next_guess()
        self.guesses.append(guess)
        await self.send(str(guess))

    def receive_report(self, decision):
        """接收报告结果"""
        last = self.guesses[-1]
        if decision == CORRECT:
            self.secret = last
        logger.info(f"Server: {last} is {decision}")

    def clear_state(self):
        """清除状态"""
        self.lower = None
        self.upper = None
        self.secret = None
        self.guesses = []


@asynccontextmanager
async def new_async_game(connection, lower, upper, secret):
    """异步启动新游戏"""
    logger.info(f"Guess a number between {lower} and {upper}! Shhhhh, it's {secret}.")
    await connection.send(f"PARAMS {lower} {upper}")
    try:
        yield AsyncClientSession(
            connection.send,
            connection.receive,
            secret,
        )
    finally:
        # 等待确保输出顺序
        await asyncio.sleep(0.1)
        await connection.send("CLEAR")


class AsyncClientSession:
    """异步客户端会话类"""

    def __init__(self, send, receive, secret):
        self.send = send
        self.receive = receive
        self.secret = secret
        self.last_distance = None

    async def request_number(self):
        """异步请求猜测"""
        await self.send("NUMBER")
        data = await self.receive()
        return int(data)

    async def report_outcome(self, number):
        """异步报告结果"""
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
        await self.send(f"REPORT {decision}")
        return decision

    async def __aiter__(self):
        """异步迭代协议"""
        while True:
            number = await self.request_number()
            decision = await self.report_outcome(number)
            yield number, decision
            if decision == CORRECT:
                return


async def handle_async_connection(reader, writer):
    """异步处理客户端连接"""
    session = AsyncServerSession(reader, writer)
    try:
        await session.loop()
    except EOFError:
        pass


async def run_async_server(address):
    """运行异步服务器"""
    server = await asyncio.start_server(
        handle_async_connection, *address
    )
    logger.info(f"Async server started on {address}")
    async with server:
        await server.serve_forever()


async def run_async_client(address):
    """运行异步客户端"""
    # 等待服务器启动
    await asyncio.sleep(0.1)

    streams = await asyncio.open_connection(*address)
    client = AsyncConnection(*streams)

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

    _, writer = streams
    writer.close()
    await writer.wait_closed()

    return results


async def main_async():
    """异步主函数"""
    address = ("127.0.0.1", 4321)

    # 创建并启动服务器任务
    server_task = asyncio.create_task(run_async_server(address))

    # 运行客户端
    results = await run_async_client(address)

    # 输出结果
    for number, outcome in results:
        logger.info(f"Client: {number} is {outcome}")

    # 取消服务器任务
    server_task.cancel()
    try:
        await server_task
    except asyncio.CancelledError:
        pass


def main():
    """主函数运行完整示例"""
    logger.info("=== 启动同步服务器测试 ===")

    # 同步服务器测试
    address = ("127.0.0.1", 1234)
    server_thread = Thread(
        target=run_server, args=(address,), daemon=True
    )
    server_thread.start()

    try:
        results = run_client(address)
        for number, outcome in results:
            logger.info(f"Sync Client: {number} is {outcome}")
    except Exception as e:
        logger.error(f"同步测试出错: {e}")

    logger.info("=== 启动异步服务器测试 ===")

    # 异步服务器测试
    try:
        asyncio.run(main_async())
    except Exception as e:
        logger.error(f"异步测试出错: {e}")


# ========================
# 错误示例演示
# ========================

def bad_example_1():
    """错误示例1：在异步代码中忘记使用await"""
    logger.info("=== 错误示例1：在异步代码中忘记使用await ===")

    async def faulty_code():
        # 错误：忘记使用await
        time.sleep(1)
        logger.info("Done")

    try:
        # 这里不会抛出异常，但sleep不会生效
        faulty_code()
    except Exception as e:
        logger.error(f"错误示例1出错: {e}")


def bad_example_2():
    """错误示例2：在非协程函数中调用异步代码"""
    logger.info("=== 错误示例2：在非协程函数中调用异步代码 ===")

    async def wait_sometime():
        await asyncio.sleep(1)
        return "Done"

    def faulty_code():
        # 错误：在普通函数中直接调用协程
        result = wait_sometime()
        logger.info(f"Result type: {type(result)}")  # 实际上得到的是协程对象

    try:
        faulty_code()
    except Exception as e:
        logger.error(f"错误示例2出错: {e}")


def bad_example_3():
    """错误示例3：在列表推导式中使用异步迭代"""
    logger.info("=== 错误示例3：在列表推导式中使用异步迭代 ===")

    class AsyncIterator:
        def __init__(self):
            self.count = 0

        def __aiter__(self):
            return self

        async def __anext__(self):
            self.count += 1
            if self.count > 3:
                raise StopAsyncIteration
            return self.count

    async def faulty_code():
        # 错误：在普通列表推导式中使用异步迭代
        iterator = AsyncIterator()
        # 下面是错误的写法
        results = [x async for x in iterator]  # 正确写法应该是async for

        for result in results:
            logger.info(f"Result: {result}")

    try:
        asyncio.run(faulty_code())
    except Exception as e:
        logger.error(f"错误示例3出错: {e}")


def bad_examples():
    """运行错误示例"""
    bad_example_1()
    bad_example_2()
    bad_example_3()


if __name__ == "__main__":
    # 运行完整示例
    main()

    # 运行错误示例
    bad_examples()
