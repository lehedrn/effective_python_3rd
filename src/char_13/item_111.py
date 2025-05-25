"""
本文件演示了如何使用 Python 的 unittest.mock 模块来模拟复杂依赖项进行单元测试。
内容覆盖：
- Mock 的基本使用方法
- 使用 assert_called_once_with 验证调用参数
- 使用 ANY 忽略某些参数验证
- 使用 side_effect 模拟异常
- 使用 keyword-only 参数注入 mock 以提高可测试性
- 使用 patch 和 patch.multiple 替换模块级别的函数

每个示例都定义为一个独立的函数，并通过 main 函数运行完整示例。
"""

import logging
import datetime
from unittest.mock import Mock, patch, call, DEFAULT

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# 示例中使用的模块级函数必须定义在顶层作用域，以便被 patch 使用
def get_animals(database, species):
    return []

def get_now():
    """用于替换 datetime.datetime.now 的辅助函数，便于测试"""
    return datetime.datetime.now()

def get_food_period(db, sp):
    return None

def feed_animal(db, name, when):
    pass


def example_mock_basics():
    """示例1：Mock 基础使用"""
    logger.info("开始执行 Mock 基础示例")

    mock_get_animals = Mock(spec=lambda db, species: None)
    mock_get_animals.return_value = [
        ("Spot", datetime.datetime(2024, 6, 5, 11, 15)),
        ("Fluffy", datetime.datetime(2024, 6, 5, 12, 30))
    ]

    database = object()
    result = mock_get_animals(database, "Meerkat")

    assert result == mock_get_animals.return_value
    logger.info("mock 返回值验证通过")

    try:
        mock_get_animals.assert_called_once_with(database, "Meerkat")
        logger.info("mock 调用参数验证通过")
    except AssertionError as e:
        logger.error(f"mock 调用参数验证失败: {e}")

    try:
        mock_get_animals.assert_called_once_with(database, "Giraffe")
    except AssertionError as e:
        logger.warning(f"错误调用验证失败（预期行为）: {e}")


def example_mock_any_and_multiple_calls():
    """示例2：使用 ANY 忽略部分参数验证，处理多次调用"""
    logger.info("开始执行 Mock ANY 和多次调用示例")

    from unittest.mock import ANY

    mock_func = Mock(spec=lambda db, species: None)

    mock_func("db1", "Rabbit")
    mock_func("db2", "Bison")
    mock_func("db3", "Meerkat")

    try:
        mock_func.assert_called_with("db3", "Meerkat")
        logger.info("最后一次调用验证通过")
    except AssertionError as e:
        logger.error(f"最后一次调用验证失败: {e}")

    # ✅ 正确使用 ANY
    try:
        mock_func.assert_called_with(ANY, "Meerkat")
        logger.info("ANY 参数验证通过")
    except AssertionError as e:
        logger.warning(f"ANY 参数验证失败（预期行为）: {e}")


def example_mock_exception():
    """示例3：模拟异常抛出"""
    logger.info("开始执行 Mock 异常模拟示例")

    mock_func = Mock(spec=lambda db, species: None)
    mock_func.side_effect = ConnectionError("数据库连接失败")

    try:
        mock_func(object(), "Meerkat")
    except ConnectionError as e:
        logger.info(f"捕获到预期异常: {e}")
    else:
        logger.error("未捕获到预期异常")


def example_inject_mocks_with_kwargs():
    """示例4：使用 keyword-only 参数注入 mocks"""
    logger.info("开始执行 keyword-only 参数注入示例")

    def do_rounds(database, species, *, now_func=get_now,
                  get_food_period=None, get_animals=None, feed_animal=None):
        now = now_func()
        animals = get_animals(database, species)
        fed = 0
        for name, last_mealtime in animals:
            if (now - last_mealtime).seconds > 3 * 3600:
                feed_animal(database, name, now)
                fed += 1
        return fed

    now_value = datetime.datetime(2024, 6, 5, 15, 45)

    now_mock = Mock(return_value=now_value)
    food_mock = Mock(return_value=datetime.timedelta(hours=3))
    animals_mock = Mock(return_value=[
        ("Spot", datetime.datetime(2024, 6, 5, 11, 15)),
        ("Fluffy", datetime.datetime(2024, 6, 5, 12, 30)),
        ("Jojo", datetime.datetime(2024, 6, 5, 12, 45)),
    ])
    feed_mock = Mock()

    database = object()

    result = do_rounds(
        database,
        "Meerkat",
        now_func=now_mock,
        get_food_period=food_mock,
        get_animals=animals_mock,
        feed_animal=feed_mock
    )

    assert result == 2
    logger.info("do_rounds 返回值验证通过")

    try:
        animals_mock.assert_called_once_with(database, "Meerkat")
        logger.info("get_animals 调用验证通过")
    except AssertionError as e:
        logger.error(f"get_animals 调用验证失败: {e}")

    feed_mock.assert_has_calls([
        call(database, "Spot", now_value),
        call(database, "Fluffy", now_value)
    ], any_order=True)
    logger.info("feed_animal 调用验证通过")


def example_patch_usage():
    """示例5：使用 patch 替换模块级函数"""
    logger.info("开始执行 patch 使用示例")

    try:
        with patch('datetime.datetime.now'):
            pass
    except TypeError as e:
        logger.warning(f"datetime.now patch 失败（预期行为）: {e}")

    with patch('__main__.get_animals') as mock_get_animals:
        mock_get_animals.return_value = [("Spot", get_now())]
        result = get_animals(object(), "Meerkat")
        assert result == mock_get_animals.return_value
        logger.info("patch 替换函数成功")


def example_patch_multiple_usage():
    """示例6：使用 patch.multiple 替换多个函数"""
    logger.info("开始执行 patch.multiple 使用示例")

    with patch.multiple('__main__', autospec=True,
                        get_food_period=DEFAULT,
                        get_animals=DEFAULT,
                        feed_animal=DEFAULT,
                        get_now=DEFAULT):

        get_food_period.return_value = datetime.timedelta(hours=3)
        get_animals.return_value = [
            ("Spot", datetime.datetime(2024, 6, 5, 11, 15)),
            ("Fluffy", datetime.datetime(2024, 6, 5, 12, 30)),
        ]
        get_now.return_value = datetime.datetime(2024, 6, 5, 15, 45)

        database = object()
        now = get_now()
        fed = 0

        animals = get_animals(database, "Meerkat")
        food_time = get_food_period(database, "Meerkat")

        for name, last_mealtime in animals:
            delta = now - last_mealtime
            if delta > food_time:
                feed_animal(database, name, now)
                fed += 1

        assert fed == 2
        logger.info("patch.multiple 替换多个函数测试通过")


def main():
    """主函数：运行所有示例"""
    logger.info("开始执行示例程序")

    logger.info("\n=== 示例1：Mock 基础使用 ===")
    example_mock_basics()

    logger.info("\n=== 示例2：使用 ANY 和多次调用 ===")
    example_mock_any_and_multiple_calls()

    logger.info("\n=== 示例3：模拟异常 ===")
    example_mock_exception()

    logger.info("\n=== 示例4：keyword-only 参数注入 mocks ===")
    example_inject_mocks_with_kwargs()

    logger.info("\n=== 示例5：使用 patch 替换函数 ===")
    example_patch_usage()

    logger.info("\n=== 示例6：使用 patch.multiple 替换多个函数 ===")
    example_patch_multiple_usage()

    logger.info("\n所有示例执行完毕")


if __name__ == "__main__":
    main()
