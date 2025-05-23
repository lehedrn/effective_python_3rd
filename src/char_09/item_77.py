"""
本文件演示了如何混合使用线程和协程来实现逐步迁移到 asyncio 的方法。
包括以下内容：
1. 原始的阻塞式 I/O 多线程版本（run_threads）。
2. 混合模式：协程调用线程（run_tasks_mixed）。
3. 完全异步模式（run_tasks）。
4. 自底向上迁移示例（tail_file 使用协程包装）。
5. 错误示例（如未加锁导致数据竞争）。
6. 使用 logging 代替 print，提升日志可读性。
"""

import logging
import time
from threading import Lock, Thread
from threading import current_thread
import asyncio
import os

# 配置 logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(threadName)s] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

class NoNewData(Exception):
    """表示没有新数据异常"""
    pass


def readline(handle):
    """
    从文件中读取下一行，若无新数据则抛出 NoNewData 异常
    """
    offset = handle.tell()
    handle.seek(0, 2)
    length = handle.tell()

    if length == offset:
        raise NoNewData

    handle.seek(offset, 0)
    return handle.readline()


def tail_file(handle, interval, write_func):
    """
    线程版：持续监听文件尾部并调用回调函数处理新数据
    """
    while not handle.closed:
        try:
            line = readline(handle)
        except NoNewData:
            time.sleep(interval)
        else:
            logger.info("写入原始线程数据: %s", line.strip())
            write_func(line)


def run_threads(handles, interval, output_path):
    """
    原始多线程实现，使用 Lock 来避免并发写冲突
    """
    with open(output_path, "wb") as output:
        lock = Lock()

        def write(data):
            with lock:
                output.write(data)

        threads = []
        for handle in handles:
            args = (handle, interval, write)
            thread = Thread(target=tail_file, args=args, name="Tail-Thread")
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()


# --------------------------
# 错误示例：未使用 Lock 导致的数据竞争问题
# --------------------------

def bad_tail_file(handle, interval, output):
    """
    错误示例：不安全地写入输出文件，可能导致行冲突
    """
    while not handle.closed:
        try:
            line = readline(handle)
        except NoNewData:
            time.sleep(interval)
        else:
            logger.warning("【错误示例】正在写入数据，可能引发竞争: %s", line.strip())
            output.write(line)


def bad_run_threads(handles, interval, output_path):
    """
    错误示例：多个线程同时写入一个文件而不加锁，可能发生数据交错
    """
    with open(output_path, "wb") as output:
        threads = []
        for handle in handles:
            args = (handle, interval, output)
            thread = Thread(target=bad_tail_file, args=args, name="Bad-Tail-Thread")
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()


# --------------------------
# 混合模式：协程 + 线程
# --------------------------

async def tail_async(handle, interval, write_func):
    """
    协程版 tail_file：使用 asyncio.run_in_executor 调用 readline
    """
    loop = asyncio.get_event_loop()

    while not handle.closed:
        try:
            line = await loop.run_in_executor(None, readline, handle)
        except NoNewData:
            await asyncio.sleep(interval)
        else:
            await write_func(line)


async def run_tasks_mixed(handles, interval, output_path):
    """
    混合模式：使用协程启动线程执行 tail_file，
    并通过 asyncio.run_coroutine_threadsafe 实现跨线程通信
    """
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
            task = loop.run_in_executor(None, tail_file, handle, interval, write)
            tasks.append(task)

        await asyncio.gather(*tasks)
    finally:
        await loop.run_in_executor(None, output.close)


# --------------------------
# 完全协程版本
# --------------------------

async def run_tasks(handles, interval, output_path):
    """
    完全协程模式：完全异步处理输入文件并统一输出
    """
    loop = asyncio.get_event_loop()

    output = await loop.run_in_executor(None, open, output_path, "wb")
    try:

        async def write_async(data):
            logger.info("写入协程数据: %s", data.strip())
            await loop.run_in_executor(None, output.write, data)

        async with asyncio.TaskGroup() as group:
            for handle in handles:
                group.create_task(tail_async(handle, interval, write_async))

    finally:
        await loop.run_in_executor(None, output.close)


# --------------------------
# Bottom-up 方式：线程内运行协程
# --------------------------

def wrapped_tail_file(handle, interval, write_func):
    """
    自底向上迁移方式：在同步函数中创建事件循环并运行协程
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def write_async(data):
        logger.info("自底向上写入数据: %s", data.strip())
        await loop.run_in_executor(None, write_func, data)

    coro = tail_async(handle, interval, write_async)
    loop.run_until_complete(coro)


def wrapped_run_threads(handles, interval, output_path):
    """
    自底向上版本 run_threads，在线程中启动协程
    """
    with open(output_path, "wb") as output:
        lock = Lock()

        def write(data):
            with lock:
                output.write(data)

        threads = []
        for handle in handles:
            args = (handle, interval, write)
            thread = Thread(target=wrapped_tail_file, args=args, name="Wrapped-Thread")
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()


# --------------------------
# 测试入口 main 函数
# --------------------------

def setup_test_files():
    """
    创建测试用的临时文件
    """
    tmpdir = "temp_logs"
    os.makedirs(tmpdir, exist_ok=True)

    input_paths = [os.path.join(tmpdir, f"input_{i}.log") for i in range(3)]
    output_path = os.path.join(tmpdir, "output.log")

    # 初始化输入文件
    for path in input_paths:
        with open(path, 'w') as f:
            f.write(f"初始内容 - {path}\n")

    handles = [open(path, 'rb') for path in input_paths]
    return tmpdir, input_paths, handles, output_path


def confirm_merge(input_paths, output_path):
    """
    验证输出文件是否成功合并了输入内容
    """
    with open(output_path, 'r', encoding='utf-8') as f:
        content = f.read()
    logger.info("输出文件内容验证:\n%s", content)
    for path in input_paths:
        assert os.path.exists(path), f"{path} 应该存在但未找到"


async def main():
    """
    主函数：依次运行各种示例
    """
    tmpdir, input_paths, handles, output_path = setup_test_files()

    # 原始多线程版本
    # logger.info("===== 开始运行原始多线程版本 =====")
    # run_threads(handles, 0.1, output_path)
    # confirm_merge(input_paths, output_path)

    # 错误示例：未加锁导致的数据竞争
    # logger.warning("===== 开始运行错误示例（数据竞争） =====")
    # bad_run_threads(handles, 0.1, output_path)
    # confirm_merge(input_paths, output_path)

    # 混合模式
    logger.info("===== 开始运行混合模式（协程+线程） =====")
    await run_tasks_mixed(handles, 0.1, output_path)
    confirm_merge(input_paths, output_path)

    # 完全协程版本
    # logger.info("===== 开始运行完全协程版本 =====")
    # await run_tasks(handles, 0.1, output_path)
    # confirm_merge(input_paths, output_path)

    # 自底向上版本
    # logger.info("===== 开始运行自底向上迁移版本 =====")
    # wrapped_run_threads(handles, 0.1, output_path)
    # confirm_merge(input_paths, output_path)


if __name__ == "__main__":
    asyncio.run(main())

