"""
测试示例模块

本模块提供多个测试相关的代码示例，用于演示单元测试和集成测试的使用场景。
同时涵盖错误示例与正确示例，帮助理解测试的重要性以及如何编写有效的测试用例。

功能包括：
- Toaster 和 ReusableTimer 类定义
- 单元测试（unittest）示例
- 集成测试示例
- 错误示例与修复方案
"""

import logging
import threading
import unittest
from unittest import mock
from typing import Optional


# 设置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ReusableTimer:
    """
    可重用的计时器类，基于 threading.Timer 实现。
    """

    def __init__(self):
        self.timer: Optional[threading.Timer] = None

    def countdown(self, duration: float, callback) -> None:
        """
        启动一个倒计时，执行回调函数。

        :param duration: 倒计时时间（秒）
        :param callback: 计时结束后执行的回调函数
        """
        self.end()
        self.timer = threading.Timer(duration, callback)
        logger.info(f"Starting timer with duration={duration:.2f} seconds")
        self.timer.start()

    def end(self) -> None:
        """
        取消当前计时器。
        """
        if self.timer:
            logger.info("Cancelling current timer.")
            self.timer.cancel()


class Toaster:
    """
    烤面包机类，控制烘烤过程。
    """

    def __init__(self, timer: ReusableTimer):
        self.timer = timer
        self.doneness = 3  # 烘焙程度，默认为3
        self.hot = False  # 是否正在烘烤

    def _get_duration(self) -> float:
        """
        根据 doneness 计算烘烤时间。

        :return: 烘烤时间（秒），范围 [0.1, 120]
        """
        return max(0.1, min(120, self.doneness * 10))

    def push_down(self) -> None:
        """
        按下烤面包机按钮开始烘烤。
        """
        if self.hot:
            return

        logger.info("Toaster pushed down. Starting baking.")
        self.hot = True
        self.timer.countdown(self._get_duration(), self.pop_up)

    def pop_up(self) -> None:
        """
        烘烤完成，弹出面包。
        """
        logger.info("Pop!")
        self.hot = False
        self.timer.end()


# -----------------------------
# 示例运行函数
# -----------------------------


def run_example() -> None:
    """
    示例运行：展示 Toaster 的基本行为。
    """
    logger.info("Running basic example...")
    timer = ReusableTimer()
    toaster = Toaster(timer)

    print("Initially hot:", toaster.hot)
    toaster.doneness = 5
    toaster.push_down()
    print("After push down:", toaster.hot)

    # 加入 timeout 避免永久卡住
    if toaster.timer.timer and toaster.timer.timer.is_alive():
        logger.info("Waiting for timer to finish (max 60s)...")
        toaster.timer.timer.join(timeout=60)
        if toaster.timer.timer.is_alive():
            logger.warning("Timer did not finish within the timeout.")

    print("After time:", toaster.hot)


# -----------------------------
# 单元测试类（Bad Example）
# -----------------------------


class BadToasterTest(unittest.TestCase):
    """
    错误的单元测试示例：过度依赖 mocks，导致测试复杂且脆弱。
    """

    def test_push_down(self):
        timer = mock.Mock(spec=ReusableTimer)
        toaster = Toaster(timer)
        toaster.push_down()
        self.assertTrue(toaster.hot)
        timer.countdown.assert_called_once_with(30, toaster.pop_up)


# -----------------------------
# 集成测试类（Good Example）
# -----------------------------


class ToasterIntegrationTest(unittest.TestCase):
    """
    良好的集成测试示例：验证 Toaster 和 ReusableTimer 的协作行为。
    """

    def setUp(self):
        self.timer = ReusableTimer()
        self.toaster = Toaster(self.timer)
        self.toaster.doneness = 0

    def test_wait_finish(self):
        self.assertFalse(self.toaster.hot)
        self.toaster.push_down()
        self.assertTrue(self.toaster.hot)

        if self.toaster.timer.timer and self.toaster.timer.timer.is_alive():
            logger.info("Waiting for integration timer to finish (max 60s)...")
            self.toaster.timer.timer.join(timeout=60)

        self.assertFalse(self.toaster.hot)

    def test_cancel_early(self):
        self.assertFalse(self.toaster.hot)
        self.toaster.push_down()
        self.assertTrue(self.toaster.hot)
        self.toaster.pop_up()
        self.assertFalse(self.toaster.hot)


# -----------------------------
# 边界条件测试类
# -----------------------------


class DonenessBoundaryTest(unittest.TestCase):
    """
    边界条件测试示例：验证 doneness 的最小和最大值处理是否正确。
    """

    def setUp(self):
        self.toaster = Toaster(ReusableTimer())

    def test_min_doneness(self):
        self.toaster.doneness = 0
        self.assertEqual(0.1, self.toaster._get_duration())

    def test_max_doneness(self):
        self.toaster.doneness = 1000
        self.assertEqual(120, self.toaster._get_duration())


# -----------------------------
# 主函数入口
# -----------------------------


def main():
    """
    主函数：依次运行所有示例和测试。
    """
    logger.info("Starting all examples and tests...")

    run_example()

    logger.info("Running unit tests...")

    loader = unittest.TestLoader()
    runner = unittest.TextTestRunner()

    runner.run(loader.loadTestsFromTestCase(BadToasterTest))
    runner.run(loader.loadTestsFromTestCase(ToasterIntegrationTest))
    runner.run(loader.loadTestsFromTestCase(DonenessBoundaryTest))


if __name__ == '__main__':
    main()
