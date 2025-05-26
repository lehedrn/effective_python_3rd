"""
本模块演示了如何在单元测试中处理浮点数精度问题。
包括使用 assertEqual 导致的失败示例，以及使用 assertAlmostEqual 的正确做法。
同时展示了 places 和 delta 参数的用法，并提供了 assertNotAlmostEqual 的示例。
"""

import unittest
import logging

# 配置日志输出
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def example_assert_equal_failure():
    """
    使用 assertEqual 测试浮点数相等的失败示例。
    因为 5/3 的结果无法精确表示为 float，导致断言失败。
    """

    class MyTestCase(unittest.TestCase):
        def test_assert_equal_failure(self):
            n = 5
            d = 3
            self.assertEqual(1.667, n / d)  # 实际值为 1.6666666666666667，会引发 AssertionError

    logging.info("运行 assertEqual 失败的测试...")
    unittest.TextTestRunner().run(
        unittest.TestLoader().loadTestsFromTestCase(MyTestCase)
    )


def example_assert_almost_equal_with_places():
    """
    使用 assertAlmostEqual 并指定 places 参数进行近似比较。
    验证小数点后两位是否相等，忽略更细微的差异。
    """

    class MyTestCase(unittest.TestCase):
        def test_assert_almost_equal_places(self):
            n = 5
            d = 3
            self.assertAlmostEqual(1.667, n / d, places=2)  # 允许误差在小数点后两位内

    logging.info("运行 assertAlmostEqual (places=2) 的测试...")
    unittest.TextTestRunner().run(
        unittest.TestLoader().loadTestsFromTestCase(MyTestCase)
    )


def example_assert_almost_equal_with_delta():
    """
    使用 assertAlmostEqual 并指定 delta 参数进行绝对差值比较。
    验证两个大数之间的差异是否在指定的容差范围内。
    """

    class MyTestCase(unittest.TestCase):
        def test_assert_almost_equal_delta(self):
            a = 1e24 / 1.1e16
            b = 1e24 / 1.101e16
            self.assertAlmostEqual(90.9e6, a, delta=0.1e6)
            self.assertAlmostEqual(90.9e6, b, delta=0.1e6)

    logging.info("运行 assertAlmostEqual (delta=0.1e6) 的测试...")
    unittest.TextTestRunner().run(
        unittest.TestLoader().loadTestsFromTestCase(MyTestCase)
    )


def example_assert_not_almost_equal():
    """
    使用 assertNotAlmostEqual 来验证两个数字不接近给定的容差或小数位数。
    """

    class MyTestCase(unittest.TestCase):
        def test_assert_not_almost_equal(self):
            a = 1.0001
            b = 1.0002
            self.assertNotAlmostEqual(a, b, places=3)  # places=3 时不接近

    logging.info("运行 assertNotAlmostEqual 的测试...")
    unittest.TextTestRunner().run(
        unittest.TestLoader().loadTestsFromTestCase(MyTestCase)
    )


def example_rounding_difference():
    """
    展示浮点运算顺序不同导致的舍入差异。
    虽然从数学上看结果应相同，但实际计算可能略有不同。
    """

    result1 = 5 / 3 * 0.1
    result2 = 0.1 * 5 / 3
    logging.info(f"5/3*0.1 的结果: {result1}")
    logging.info(f"0.1*5/3 的结果: {result2}")


def main():
    logging.info("开始运行所有示例...")

    logging.info("\n=== 示例 1: assertEqual 失败 ===")
    try:
        example_assert_equal_failure()
    except Exception as e:
        logging.error(f"assertEqual 失败示例异常: {e}")

    logging.info("\n=== 示例 2: assertAlmostEqual with places ===")
    example_assert_almost_equal_with_places()

    logging.info("\n=== 示例 3: assertAlmostEqual with delta ===")
    example_assert_almost_equal_with_delta()

    logging.info("\n=== 示例 4: assertNotAlmostEqual ===")
    example_assert_not_almost_equal()

    logging.info("\n=== 示例 5: 浮点舍入行为差异 ===")
    example_rounding_difference()

    logging.info("\n所有示例执行完毕。")


if __name__ == "__main__":
    main()
