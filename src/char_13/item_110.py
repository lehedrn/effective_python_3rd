"""
本文件演示了如何在Python中使用unittest框架中的setUp、tearDown、setUpModule和tearDownModule方法，
以及错误示例和正确示例的对比。通过这些方法，可以确保测试用例之间相互隔离，并且可以有效地管理集成测试的环境。
"""

import unittest
import logging
from pathlib import Path
import tempfile

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class TestSetupAndTeardown(unittest.TestCase):
    """
    演示 setUp 和 tearDown 的基本用法。
    """

    def setUp(self):
        """
        在每个测试方法执行前调用，创建临时目录。
        """
        self.test_dir = tempfile.TemporaryDirectory()
        self.test_path = Path(self.test_dir.name)
        logging.info("setUp: 创建临时目录 %s", self.test_path)

    def tearDown(self):
        """
        在每个测试方法执行后调用，清理临时目录。
        """
        logging.info("tearDown: 清理临时目录 %s", self.test_path)
        self.test_dir.cleanup()

    def test_file_creation(self):
        """
        正确示例：在临时目录中创建文件并验证其存在。
        """
        file_path = self.test_path / "data.bin"
        with open(file_path, "w") as f:
            f.write("hello")
        self.assertTrue(file_path.exists())
        logging.info("test_file_creation: 文件已创建")

    def test_file_creation_with_fixed_error(self):
        """
        错误示例：先创建目录再写入文件。
        """
        file_path = self.test_path / "nonexistent" / "data.bin"
        file_path.parent.mkdir(parents=True, exist_ok=True)  # 确保目录存在
        with open(file_path, "w") as f:
            f.write("hello")
        self.assertTrue(file_path.exists())
        logging.info("test_file_creation_with_fixed_error: 文件已成功创建")


def setUpModule():
    """
    模块级初始化，在所有测试类开始前运行一次。
    """
    logging.info("setUpModule: 模块级初始化")


def tearDownModule():
    """
    模块级清理，在所有测试类结束后运行一次。
    """
    logging.info("tearDownModule: 模块级清理")


class IntegrationTest(unittest.TestCase):
    """
    演示 setUpClass/tearDownClass 及 setUp/tearDown 在集成测试中的使用。
    """

    @classmethod
    def setUpClass(cls):
        """
        类级初始化，在当前类的所有测试方法执行前运行一次。
        """
        logging.info("setUpClass: 启动数据库服务")

    @classmethod
    def tearDownClass(cls):
        """
        类级清理，在当前类的所有测试方法执行后运行一次。
        """
        logging.info("tearDownClass: 停止数据库服务")

    def setUp(self):
        """
        方法级初始化，在每个测试方法执行前运行。
        """
        logging.info("setUp: 连接到数据库")

    def tearDown(self):
        """
        方法级清理，在每个测试方法执行后运行。
        """
        logging.info("tearDown: 断开数据库连接")

    def test_integration_1(self):
        """
        测试集成逻辑 1。
        """
        logging.info("test_integration_1: 执行集成测试1")

    def test_integration_2(self):
        """
        测试集成逻辑 2。
        """
        logging.info("test_integration_2: 执行集成测试2")


if __name__ == "__main__":
    unittest.main()
