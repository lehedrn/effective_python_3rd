"""
本文件展示了如何使用 Python 的 unittest 模块编写测试用例，涵盖以下内容：
1. 使用 TestCase 子类组织相关测试。
2. 使用 assertEqual、assertTrue 等断言方法代替内置的 assert 语句。
3. 使用 subTest 编写数据驱动的测试以减少样板代码。
4. 使用 assertRaises 验证异常行为。
5. 定义自定义测试辅助方法以提高可读性。
6. 包含正确和错误示例以便理解不同情况下的测试输出。

"""

import unittest
import logging

# 设置日志格式
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class TestCaseExamples(unittest.TestCase):
    def test_case_organization(self):
        """
        示例 1: 测试方法以 'test_' 开头，TestCase 组织多个测试方法
        """
        logger.info("运行 test_case_organization")
        self.assertEqual(1 + 1, 2)
        self.assertNotEqual(1 + 1, 3)

    def test_assert_methods_vs_builtin_assert(self):
        """
        示例 2: 使用 TestCase 的断言方法 vs 内置 assert
        """
        logger.info("运行 test_assert_methods_vs_builtin_assert")

        expected = 10
        found = 5 * 2

        # 正确示例：使用 TestCase 断言方法
        self.assertEqual(expected, found)  # 提供详细的失败信息

        # 错误示例：使用内置 assert
        try:
            assert expected == 9  # 这将抛出 AssertionError，但不会显示具体值
        except AssertionError as e:
            logger.error("内置 assert 抛出异常，但不显示具体值", exc_info=True)

    def test_assert_raises_for_exception(self):
        """
        示例 3: 使用 assertRaises 验证异常
        """
        logger.info("运行 test_assert_raises_for_exception")

        # 正确示例：使用 assertRaises 捕获预期异常
        with self.assertRaises(TypeError):
            to_str(object())

        # 错误示例：未使用 assertRaises，手动 try-except
        try:
            to_str(object())
        except TypeError:
            pass  # 虽然能捕获异常，但无法清晰表达意图

    def test_subtest_for_data_driven(self):
        """
        示例 4: 使用 subTest 编写数据驱动测试
        """
        logger.info("运行 test_subtest_for_data_driven")

        cases = [
            (b"hello", "hello"),
            ("world", "world"),
            ("incorrect", "wrong"),  # 这个会失败
        ]

        for value, expected in cases:
            with self.subTest(value=value):  # 即使某个子测试失败，其他仍继续执行
                self.assertEqual(expected, to_str(value))

    def test_custom_helper_method(self):
        """
        示例 5: 自定义测试辅助方法验证复杂逻辑
        """
        logger.info("运行 test_custom_helper_method")

        values = [1.1, 2.2, 3.3]
        expected_results = [
            1.1 ** 2,
            1.1 ** 2 + 2.2 ** 2,
            1.1 ** 2 + 2.2 ** 2 + 3.3 ** 2,
        ]

        # 正确示例：期望匹配
        self.verify_sum_squares(values, expected_results)

        # 错误示例：期望不匹配
        wrong_expected = expected_results.copy()
        wrong_expected[2] += 1  # 修改最后一个结果
        try:
            self.verify_sum_squares(values, wrong_expected)
        except AssertionError as e:
            logger.error(f"自定义辅助方法验证失败: {e}", exc_info=True)

    def verify_sum_squares(self, values, expected):
        """
        自定义测试辅助方法，验证生成器 sum_squares 的行为
        """
        expect_it = iter(expected)
        found_it = iter(sum_squares(values))
        test_it = zip(expect_it, found_it, strict=True)

        for i, (expect, found) in enumerate(test_it):
            if found != expect:
                self.fail(f"索引 {i} 不匹配: {found} != {expect}")


def to_str(data):
    """
    将输入转换为字符串的实用函数
    """
    if isinstance(data, str):
        return data
    elif isinstance(data, bytes):
        return data.decode("utf-8")
    else:
        raise TypeError(f"必须提供 str 或 bytes，找到的数据类型为: {data}")


def sum_squares(values):
    """
    计算平方和的生成器
    """
    cumulative = 0
    for value in values:
        cumulative += value ** 2
        yield cumulative


if __name__ == "__main__":
    unittest.main()
