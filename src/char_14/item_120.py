"""
模块作用域代码用于配置部署环境的完整示例。

本文件演示了如何使用模块作用域代码来根据不同的部署环境（如开发、测试、生产）进行动态配置。
包含以下几种场景：
1. 使用 __main__ 模块传递部署环境标志
2. 根据 sys.platform 选择平台相关的实现
3. 使用 os.environ 环境变量控制配置
4. 错误示例和正确示例对比

所有示例都封装在函数中，并通过 main 函数统一运行。
"""

import logging
import sys
import os

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# —————————————————————— 示例 1: 使用 __main__ 模块传递部署环境标志 ——————————————————————

# 错误示例：直接在模块中硬编码数据库连接，无法适应不同环境
class BadExampleDatabase:
    def connect(self):
        logger.info("Connecting to real production database...")


# 正确示例：根据 __main__.TESTING 动态选择数据库类
class TestingDatabase:
    def connect(self):
        logger.info("Using mock database for testing")


class ProductionDatabase:
    def connect(self):
        logger.info("Connecting to real production database")


def example_testing_db():
    """
    根据 TESTING 标志切换数据库实现
    开发时使用 Mock 数据库，避免真实数据库操作
    """
    main_module = sys.modules['__main__']
    if getattr(main_module, 'TESTING', False):
        db = TestingDatabase()
    else:
        db = ProductionDatabase()

    db.connect()


# —————————————————————— 示例 2: 根据 sys.platform 选择平台相关实现 ——————————————————————

def example_platform_specific():
    """
    根据操作系统平台选择不同的实现类
    Windows 和 POSIX 平台分别使用不同的数据库驱动
    """

    class Win32Database:
        def connect(self):
            logger.info("Connecting using Windows-specific driver")

    class PosixDatabase:
        def connect(self):
            logger.info("Connecting using POSIX-specific driver")

    if sys.platform.startswith('win32'):
        db = Win32Database()
    else:
        db = PosixDatabase()

    db.connect()


# —————————————————————— 示例 3: 使用 os.environ 控制模块行为 ——————————————————————

def example_env_based_config():
    """
    使用环境变量控制模块配置
    可以通过环境变量注入调试模式、自定义路径等
    """
    debug_mode = os.getenv('APP_DEBUG', 'False').lower() == 'true'

    if debug_mode:
        logger.info("Running in debug mode")
    else:
        logger.info("Running in production mode")


# —————————————————————— 主运行函数 ——————————————————————

def main():
    # 设置 TESTING 标志到主模块中
    main_module = sys.modules['__main__']
    main_module.TESTING = True  # 模拟 dev_main.py 的行为

    logger.info("——— 示例 1: 使用 __main__ 模块传递部署环境标志 ———")
    logger.info("错误示例：硬编码数据库连接")
    bad_example = BadExampleDatabase()
    bad_example.connect()

    logger.info("正确示例：根据 TESTING 标志切换数据库")
    example_testing_db()

    logger.info("\n——— 示例 2: 根据 sys.platform 选择平台相关实现 ———")
    example_platform_specific()

    logger.info("\n——— 示例 3: 使用 os.environ 控制模块行为 ———")
    # 设置环境变量模拟不同行为
    os.environ['APP_DEBUG'] = 'True'
    example_env_based_config()

    del os.environ['APP_DEBUG']
    example_env_based_config()


if __name__ == '__main__':
    main()
