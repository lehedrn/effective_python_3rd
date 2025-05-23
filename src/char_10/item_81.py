"""
本模块演示了 Python 中 `assert` 和 `raise` 的使用场景和区别。
包含以下内容：
- 使用 `assert` 验证内部假设，不用于向调用者报告错误。
- 使用 `raise` 报告外部异常情况，是函数接口的一部分。
- 示例包括正确用法、错误示例以及完整的日志输出说明。

模块中每个函数代表一个完整示例，并在 main 函数中运行。
"""

import logging

# 设置日志格式
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def example_raise_for_external_api():
    """
    使用 raise 向调用者报告异常，适用于对外暴露的 API 接口。
    该示例定义了一个 Rating 类，验证输入参数并抛出明确的异常。
    """

    class RatingError(Exception):
        """自定义异常类，用于表示评分相关的错误"""
        pass

    class Rating:
        def __init__(self, max_rating):
            if not (max_rating > 0):
                raise RatingError("最大评分必须大于 0")
            self.max_rating = max_rating
            self.ratings = []

        def rate(self, rating):
            if not (0 < rating <= self.max_rating):
                raise RatingError(f"评分 {rating} 超出范围 [1, {self.max_rating}]")
            self.ratings.append(rating)

    logger.info("测试 raise 在对外 API 中的使用")

    try:
        movie = Rating(5)
        movie.rate(5)  # 正确输入
        movie.rate(7)  # 错误输入，触发异常
    except RatingError as e:
        logger.error(f"捕获到 RatingError: {e}")


def example_assert_for_internal_assumption():
    """
    使用 assert 验证内部假设，不用于向调用者报告错误。
    该示例定义了一个 RatingInternal 类，仅在开发阶段验证内部逻辑。
    """

    class RatingInternal:
        def __init__(self, max_rating):
            assert max_rating > 0, f"初始化失败：max_rating 必须大于 0，当前值为 {max_rating}"
            self.max_rating = max_rating
            self.ratings = []

        def rate(self, rating):
            assert 0 < rating <= self.max_rating, f"评分错误：rating 值为 {rating}，超出允许范围"
            self.ratings.append(rating)

    logger.info("测试 assert 在内部逻辑中的使用")

    try:
        movie = RatingInternal(5)
        movie.rate(5)  # 正确输入
        movie.rate(7)  # 错误输入，触发 AssertionError
    except AssertionError as e:
        logger.error(f"捕获到 AssertionError: {e}")


def example_catching_assertion_error():
    """
    演示如何意外捕获 AssertionError（不推荐）。
    在实际开发中应避免这样做，因为 assert 是用于调试的。
    """

    logger.info("测试捕获 AssertionError")

    try:
        assert False, "这是一个断言错误"
    except AssertionError as e:
        logger.warning(f"不应该在这里捕获 AssertionError: {e}")


def example_catching_raise_exception():
    """
    演示如何正确捕获由 raise 引发的异常。
    这是推荐的做法，因为 raise 是用于可预期的错误处理。
    """

    class CustomException(Exception):
        pass

    def faulty_function():
        raise CustomException("这是一个预期的错误")

    logger.info("测试捕获 raise 异常")

    try:
        faulty_function()
    except CustomException as e:
        logger.error(f"成功捕获由 raise 引发的异常: {e}")


def example_assert_not_disabled():
    """
    演示 assert 不应该被禁用。
    如果设置了 __debug__ == False，则 assert 会被忽略。
    本例不会设置 __debug__，因此 assert 应该正常工作。
    """

    logger.info("测试 assert 是否被禁用")

    try:
        assert False, "__debug__ 可能被设置为 False，这将导致断言失效"
    except AssertionError as e:
        logger.warning(f"断言生效，程序检测到了问题: {e}")


def main():
    """
    主函数，运行所有示例。
    每个函数代表一个独立的示例，用于展示 `assert` 和 `raise` 的不同用途。
    """
    logger.info("开始运行示例...")

    logger.info("=== 示例 1: 使用 raise 处理外部异常 ===")
    example_raise_for_external_api()

    logger.info("=== 示例 2: 使用 assert 验证内部逻辑 ===")
    example_assert_for_internal_assumption()

    logger.info("=== 示例 3: 不推荐：捕获 AssertionError ===")
    example_catching_assertion_error()

    logger.info("=== 示例 4: 推荐：捕获 raise 异常 ===")
    example_catching_raise_exception()

    logger.info("=== 示例 5: 确保 assert 未被禁用 ===")
    example_assert_not_disabled()

    logger.info("所有示例运行完毕。")


if __name__ == "__main__":
    main()
