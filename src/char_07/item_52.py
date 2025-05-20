"""
本文件演示了如何使用 `@classmethod` 多态来通用地构造对象。

内容涵盖：
1. 原始方式：手动构建对象连接，不具备通用性。
2. 正确方式：使用 `@classmethod` 实现类多态，实现通用的工厂方法。
3. 错误示例：展示因不使用类多态导致难以扩展的问题。
4. 正确重构：通过类方法多态使 `mapreduce` 逻辑对子类透明。

目标是展示 Python 中 `@classmethod` 在构建和连接多个具体子类时的优势。
"""

import os
import logging
import shutil
from threading import Thread
from abc import ABC, abstractmethod

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# ————————————————————————————————
# 示例1：原始非通用实现（错误示例）
# ————————————————————————————————

class InputData:
    def read(self):
        raise NotImplementedError


class PathInputData(InputData):
    def __init__(self, path):
        self.path = path

    def read(self):
        with open(self.path) as f:
            return f.read()


class Worker:
    def __init__(self, input_data):
        self.input_data = input_data
        self.result = None

    def map(self):
        raise NotImplementedError

    def reduce(self, other):
        raise NotImplementedError


class LineCountWorker(Worker):
    def map(self):
        data = self.input_data.read()
        self.result = data.count("\n")

    def reduce(self, other):
        self.result += other.result


def generate_inputs(data_dir):
    for name in os.listdir(data_dir):
        yield PathInputData(os.path.join(data_dir, name))


def create_workers(input_list):
    workers = []
    for input_data in input_list:
        workers.append(LineCountWorker(input_data))
    return workers


def execute(workers):
    threads = [Thread(target=w.map) for w in workers]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    first, *rest = workers
    for worker in rest:
        first.reduce(worker)
    return first.result


def mapreduce(data_dir):
    inputs = generate_inputs(data_dir)
    workers = create_workers(inputs)
    return execute(workers)


def example_non_generic():
    """
    错误示例：硬编码依赖 PathInputData 和 LineCountWorker，
    扩展新子类需要重写辅助函数。
    """
    tmpdir = "test_inputs"
    os.makedirs(tmpdir, exist_ok=True)

    for i in range(5):
        with open(os.path.join(tmpdir, str(i)), "w") as f:
            f.write("\n" * i)

    result = mapreduce(tmpdir)
    logger.info(f"[非通用示例] 总行数: {result}")


# ————————————————————————————————
# 示例2：正确使用 @classmethod 多态（通用实现）
# ————————————————————————————————

class GenericInputData(ABC):
    @abstractmethod
    def read(self):
        pass

    @classmethod
    @abstractmethod
    def generate_inputs(cls, config):
        pass


class GenericWorker(ABC):
    def __init__(self, input_data):
        self.input_data = input_data
        self.result = None

    @abstractmethod
    def map(self):
        pass

    @abstractmethod
    def reduce(self, other):
        pass

    @classmethod
    def create_workers(cls, input_class, config):
        workers = []
        for input_data in input_class.generate_inputs(config):
            workers.append(cls(input_data))
        return workers


class PathInputData(GenericInputData):
    def __init__(self, path):
        self.path = path

    def read(self):
        with open(self.path) as f:
            return f.read()

    @classmethod
    def generate_inputs(cls, config):
        data_dir = config["data_dir"]
        for name in os.listdir(data_dir):
            yield cls(os.path.join(data_dir, name))


class LineCountWorker(GenericWorker):
    def map(self):
        data = self.input_data.read()
        self.result = data.count("\n")

    def reduce(self, other):
        self.result += other.result


def mapreduce_generic(worker_class, input_class, config):
    workers = worker_class.create_workers(input_class, config)
    return execute(workers)


def example_generic():
    """
    正确示例：使用 @classmethod 实现类多态，mapreduce 泛化为任意子类组合。
    """
    tmpdir = "test_inputs_generic"
    os.makedirs(tmpdir, exist_ok=True)

    for i in range(5):
        with open(os.path.join(tmpdir, str(i)), "w") as f:
            f.write("\n" * (i + 10))

    config = {"data_dir": tmpdir}
    result = mapreduce_generic(LineCountWorker, PathInputData, config)
    logger.info(f"[通用示例] 总行数: {result}")


# ————————————————————————————————
# 示例3：扩展更多子类验证通用性
# ————————————————————————————————

class StringInputData(GenericInputData):
    def __init__(self, content):
        self.content = content

    def read(self):
        return self.content

    @classmethod
    def generate_inputs(cls, config):
        contents = config.get("contents", [])
        for content in contents:
            yield cls(content)


class WordCountWorker(GenericWorker):
    def map(self):
        data = self.input_data.read()
        self.result = len(data.split())

    def reduce(self, other):
        self.result += other.result


def example_extensible():
    """
    扩展示例：新增 StringInputData 和 WordCountWorker，
    无需修改 mapreduce 或其他辅助函数。
    """
    config = {
        "contents": [
            "hello world",
            "this is a test",
            "python class method polymorphism",
        ]
    }

    result = mapreduce_generic(WordCountWorker, StringInputData, config)
    logger.info(f"[扩展示例] 单词总数: {result}")

def relase():
    """
    清理生成的模拟数据文件
    """
    tmpdir = "test_inputs"
    if os.path.exists(tmpdir):
        shutil.rmtree(tmpdir)
    tmpdir_generic = "test_inputs_generic"
    if os.path.exists(tmpdir_generic):
        shutil.rmtree(tmpdir_generic)

# ————————————————————————————————
# 主运行函数
# ————————————————————————————————

def main():
    logger.info("开始执行错误示例（非通用）")
    example_non_generic()

    logger.info("开始执行正确示例（通用）")
    example_generic()

    logger.info("开始执行扩展示例（多态扩展）")
    example_extensible()

    relase()
    logger.info("清理临时文件")

    logger.info("所有示例运行完毕")


if __name__ == "__main__":
    main()
