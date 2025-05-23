"""
本模块展示了如何通过 `asyncio` 与线程协作，最大化事件循环的响应能力。
涵盖以下内容：
- 阻塞事件循环带来的问题（如延迟、响应变慢）
- 使用 `run_in_executor` 将阻塞操作移出主线程
- 构建 `WriteThread` 类来封装异步写入逻辑
- 使用 `__aenter__` 和 `__aexit__` 支持异步上下文管理
- 完整示例包含错误用法和正确用法，并附有详细说明

依赖库：asyncio, threading, logging, os, tempfile, collections
"""

import asyncio
import logging
import os
import tempfile
import time
from collections import defaultdict
from threading import Thread

# 设置日志系统
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# 错误示例：在协程中直接调用阻塞 I/O
async def bad_coroutine():
    """
    错误示例：在协程中直接使用 time.sleep 模拟阻塞 I/O。
    这会阻塞整个事件循环，影响其他任务执行。
    """
    logger.info("开始执行阻塞协程")
    time.sleep(1)  # 阻塞事件循环
    logger.info("阻塞协程完成")


# 正确示例：使用 run_in_executor 移除阻塞操作
async def good_coroutine():
    """
    正确示例：使用 loop.run_in_executor 将阻塞操作放入线程池中执行，
    避免阻塞主事件循环。
    """
    loop = asyncio.get_event_loop()
    logger.info("开始执行非阻塞协程")
    await loop.run_in_executor(None, time.sleep, 1)
    logger.info("非阻塞协程完成")


# 文件读取函数：模拟 tail -f 行为
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


# 异步尾随读取器
async def tail_async(handle, interval, write_func):
    loop = asyncio.get_event_loop()

    while not handle.closed:
        try:
            line = await loop.run_in_executor(None, readline, handle)
        except NoNewData:
            await asyncio.sleep(interval)
        else:
            await write_func(line)


# 简化的错误版本：直接使用同步文件写入
async def run_tasks_simpler(handles, interval, output_path):
    with open(output_path, "wb") as output:
        async def write_async(data):
            output.write(data)

        async with asyncio.TaskGroup() as group:
            for handle in handles:
                group.create_task(tail_async(handle, interval, write_async))


# 正确版本：使用 run_in_executor 的完整实现
async def run_tasks(handles, interval, output_path):
    loop = asyncio.get_event_loop()
    output = await loop.run_in_executor(None, open, output_path, "wb")
    try:
        async def write_async(data):
            await loop.run_in_executor(None, output.write, data)

        async with asyncio.TaskGroup() as group:
            for handle in handles:
                group.create_task(tail_async(handle, interval, write_async))
    finally:
        await loop.run_in_executor(None, output.close)


# 写入线程类：封装异步写入逻辑
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
        self.loop.run_until_complete(asyncio.sleep(0))

    async def real_write(self, data):
        self.output.write(data)

    async def write(self, data):
        coro = self.real_write(data)
        future = asyncio.run_coroutine_threadsafe(coro, self.loop)
        await asyncio.wrap_future(future)

    async def real_stop(self):
        self.loop.stop()

    async def stop(self):
        coro = self.real_stop()
        future = asyncio.run_coroutine_threadsafe(coro, self.loop)
        await asyncio.wrap_future(future)

    async def __aenter__(self):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.start)
        return self

    async def __aexit__(self, *_):
        await self.stop()


# 使用 WriteThread 的最终版本
async def run_fully_async(handles, interval, output_path):
    async with (
        WriteThread(output_path) as output,
        asyncio.TaskGroup() as group,
    ):
        for handle in handles:
            group.create_task(tail_async(handle, interval, output.write))


# 验证合并结果是否正确
def confirm_merge(input_paths, output_path):
    found = defaultdict(list)
    with open(output_path, "rb") as f:
        for line in f:
            for path in input_paths:
                if line.find(path.encode()) == 0:
                    found[path].append(line)

    expected = defaultdict(list)
    for path in input_paths:
        with open(path, "rb") as f:
            expected[path].extend(f.readlines())

    for key, expected_lines in expected.items():
        found_lines = found[key]
        assert expected_lines == found_lines, f"验证失败: {key}"


# 测试数据准备
def setup_temp_files():
    tmpdir = tempfile.TemporaryDirectory()
    input_paths = [os.path.join(tmpdir.name, f"input_{i}.txt") for i in range(3)]
    handles = []
    for i, path in enumerate(input_paths):
        with open(path, "wb") as f:
            f.write(f"{path}\n".encode())
        handles.append(open(path, "rb"))
    output_path = os.path.join(tmpdir.name, "output.txt")
    return tmpdir, input_paths, handles, output_path


# 主函数运行所有示例
async def main():
    # 示例 1：演示阻塞协程的问题
    logger.info("=== 示例 1：阻塞协程 ===")
    try:
        asyncio.run(bad_coroutine(), debug=True)
    except Exception as e:
        logger.warning(f"检测到阻塞协程警告: {e}")

    # 示例 2：使用 run_in_executor 解决阻塞问题
    logger.info("=== 示例 2：非阻塞协程 (run_in_executor) ===")
    await good_coroutine()

    # 示例 3：错误使用同步文件写入
    logger.info("=== 示例 3：错误使用同步文件写入 ===")
    tmpdir, input_paths, handles, output_path = setup_temp_files()
    try:
        await run_tasks_simpler(handles, 0.1, output_path)
        confirm_merge(input_paths, output_path)
        logger.warning("错误示例意外成功，应避免这种写法！")
    except Exception as e:
        logger.warning(f"错误示例预期失败: {e}")

    # 示例 4：正确使用 run_in_executor
    logger.info("=== 示例 4：正确使用 run_in_executor ===")
    await run_tasks(handles, 0.1, output_path)
    confirm_merge(input_paths, output_path)
    logger.info("输出验证成功")

    # 示例 5：使用 WriteThread 实现完全异步写入
    logger.info("=== 示例 5：使用 WriteThread ===")
    await run_fully_async(handles, 0.1, output_path)
    confirm_merge(input_paths, output_path)
    logger.info("WriteThread 输出验证成功")

    # 清理资源
    for h in handles:
        h.close()
    tmpdir.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
