"""
本文件演示了如何通过封装依赖来简化模拟和测试，包括错误示例与正确示例。
涵盖以下内容：
- 使用 Mock 类进行单元测试的基本用法。
- 封装数据库接口以简化测试。
- 使用 spec 参数防止方法名拼写错误。
- 集成测试中的依赖注入方式。

该文件包含多个函数，每个函数演示一个特定的测试场景，并在 main 函数中运行完整示例。
"""

import contextlib
import io
import logging
from datetime import datetime, timedelta
from unittest.mock import Mock, call, patch

# 设置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# ==============================
# 错误示例：未封装依赖导致测试复杂
# ==============================

class DatabaseConnection:
    def get_animals(self, species):
        pass

    def get_food_period(self, species):
        pass

    def feed_animal(self, name, when):
        pass


def do_rounds_unittest_mock(database_connection, species, *, now_func=datetime.now):
    now = now_func()
    feeding_timedelta = database_connection.get_food_period(species)
    animals = database_connection.get_animals(species)
    fed = 0

    for name, last_mealtime in animals:
        if (now - last_mealtime) >= feeding_timedelta:
            database_connection.feed_animal(name, now)
            fed += 1

    return fed


# 将 FakeDatabase 提升为模块级类（放在函数外部）
class FakeDatabase:
    @staticmethod
    def get_food_period(species):
        return timedelta(hours=3)

    @staticmethod
    def get_animals(species):
        return [
            ("Spot", datetime(2019, 6, 5, 11, 15)),
            ("Fluffy", datetime(2019, 6, 5, 12, 30)),
            ("Jojo", datetime(2019, 6, 5, 12, 55)),
        ]

    @staticmethod
    def feed_animal(name, when):
        logger.debug(f"Feeding {name} at {when}")


def bad_example_test():
    """
    错误示例：未封装依赖时，测试需要大量 patch 和 setup。
    """
    logger.info("开始执行错误示例：未封装依赖的测试")

    now_func = Mock()
    now_func.return_value = datetime(2019, 6, 5, 15, 45)

    with patch('__main__.FakeDatabase.get_food_period', return_value=timedelta(hours=3)), \
         patch('__main__.FakeDatabase.get_animals', return_value=[
             ("Spot", datetime(2019, 6, 5, 11, 15)),
             ("Fluffy", datetime(2019, 6, 5, 12, 30)),
             ("Jojo", datetime(2019, 6, 5, 12, 55)),
         ]), \
         patch('__main__.FakeDatabase.feed_animal') as mock_feed:

        result = do_rounds_unittest_mock(FakeDatabase(), "Meerkat", now_func=now_func)
        assert result == 2
        mock_feed.assert_called()
        logger.info("错误示例测试成功")


# ==============================
# 正确示例：封装依赖并使用 Mock 测试
# ==============================

class ZooDatabase:
    def get_animals(self, species):
        pass

    def get_food_period(self, species):
        pass

    def feed_animal(self, name, when):
        pass


def do_rounds(database: ZooDatabase, species, *, now_func=datetime.now):
    """
    封装后的版本，便于 Mock 测试。
    """
    now = now_func()
    feeding_timedelta = database.get_food_period(species)
    animals = database.get_animals(species)
    fed = 0

    for name, last_mealtime in animals:
        if (now - last_mealtime) >= feeding_timedelta:
            database.feed_animal(name, now)
            fed += 1

    return fed


def correct_example_test():
    """
    正确示例：封装依赖后，Mock 更加简单直观。
    """
    logger.info("开始执行正确示例：封装依赖的测试")

    now_func = Mock(spec=datetime.now)
    now_func.return_value = datetime(2019, 6, 5, 15, 45)

    database = Mock(spec=ZooDatabase)
    database.get_food_period.return_value = timedelta(hours=3)
    database.get_animals.return_value = [
        ("Spot", datetime(2019, 6, 5, 11, 15)),
        ("Fluffy", datetime(2019, 6, 5, 12, 30)),
        ("Jojo", datetime(2019, 6, 5, 12, 55)),
    ]

    result = do_rounds(database, "Meerkat", now_func=now_func)
    assert result == 2

    database.get_food_period.assert_called_once_with("Meerkat")
    database.get_animals.assert_called_once_with("Meerkat")
    database.feed_animal.assert_has_calls(
        [
            call("Spot", now_func.return_value),
            call("Fluffy", now_func.return_value),
        ],
        any_order=True,
    )

    logger.info("正确示例测试成功")


# ==============================
# 使用 spec 防止方法名拼写错误
# ==============================

def test_method_name_spelling():
    """
    示例：使用 spec 参数防止方法名拼写错误。
    """
    logger.info("开始执行 spec 防止拼写错误测试")

    database = Mock(spec=ZooDatabase)
    try:
        database.bad_method_name()  # 这个方法不存在于 spec 中
    except AttributeError as e:
        logger.warning(f"预期抛出异常：{e}")
        assert 'bad_method_name' in str(e), "异常信息未包含预期字段"
    else:
        raise AssertionError("应该抛出 AttributeError")

    logger.info("spec 防止拼写错误测试成功")


# ==============================
# 端到端集成测试示例
# ==============================

DATABASE = None


def get_database():
    global DATABASE
    if DATABASE is None:
        DATABASE = ZooDatabase()
    return DATABASE


def main(argv):
    database = get_database()
    species = argv[1]
    count = do_rounds(database, species)
    print(f"Fed {count} {species}(s)")
    return 0


def integration_test():
    """
    示例：端到端集成测试，使用 patch 注入 mock 数据库。
    """
    logger.info("开始执行集成测试")

    with patch("__main__.DATABASE", spec=ZooDatabase):
        now = datetime.now()

        DATABASE.get_food_period.return_value = timedelta(hours=3)
        DATABASE.get_animals.return_value = [
            ("Spot", now - timedelta(minutes=4.5)),
            ("Fluffy", now - timedelta(hours=3.25)),
            ("Jojo", now - timedelta(hours=3)),
        ]

        fake_stdout = io.StringIO()
        with contextlib.redirect_stdout(fake_stdout):
            main(["program name", "Meerkat"])

        found = fake_stdout.getvalue()
        expected = "Fed 2 Meerkat(s)\n"

        assert found == expected
        logger.info("集成测试成功")


# ==============================
# 主函数：运行所有示例
# ==============================

def main_function():
    logger.info("开始执行所有测试示例")
    bad_example_test()
    correct_example_test()
    test_method_name_spelling()
    integration_test()
    logger.info("所有测试示例执行完毕")


if __name__ == '__main__':
    main_function()
