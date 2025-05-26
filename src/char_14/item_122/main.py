"""
本模块演示了如何处理 Python 中的循环依赖问题。主要内容包括：

1. 循环依赖的错误示例。
2. 通过重新排序导入解决循环依赖（不推荐）。
3. 使用“导入-配置-运行”模式打破循环依赖。
4. 使用动态导入打破循环依赖。

所有示例均以一个 GUI 应用程序中对话框和全局偏好设置之间的依赖关系为例进行说明，并提供了完整的实现代码。
"""

import logging
import sys

# 配置日志输出
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# 错误示例：循环依赖导致的 AttributeError
def circular_dependency_error():
    """
    错误示例：展示循环依赖导致的异常。
    app.py 导入 dialog，dialog.py 导入 app，且在模块级别使用 app.prefs.get()。
    运行时会抛出 AttributeError。
    """

    logger.info("开始运行错误示例：循环依赖导致的 AttributeError")

    try:
        import circular_app as error_app
    except Exception as e:
        logger.error(f"发生错误: {e}")


# 不推荐方案：重新排序导入
def reorder_imports_solution():
    """
    解决方案一：将 `import dialog` 放在 app.py 的底部。
    虽然可以避免错误，但违反 PEP8 规范，不推荐使用。
    """

    logger.info("运行解决方案一：重新排序导入（不推荐）")

    from reorder_app import show_dialog

    show_dialog()


# 推荐方案一：导入-配置-运行模式
def import_configure_run_solution():
    """
    解决方案二：采用导入-配置-运行模式。
    所有模块仅定义结构，在 main 中统一调用 configure 方法进行初始化。
    """

    logger.info("运行解决方案二：导入-配置-运行模式")

    from configure_app import prefs
    from configure_dialog import save_dialog, configure as dialog_configure
    from configure_main import configure_all

    configure_all(prefs, save_dialog)
    save_dialog.show()


# 推荐方案二：动态导入
def dynamic_import_solution():
    """
    解决方案三：在函数内部使用动态导入。
    避免模块级循环依赖，延迟导入到真正需要的时候。
    """

    logger.info("运行解决方案三：动态导入")

    from dynamic_dialog import save_dialog
    save_dialog.show()


def main():
    """
    主函数，依次运行所有示例。
    """

    logger.info("开始运行主函数：执行所有示例")

    logger.info("\n--- 错误示例：循环依赖 ---")
    circular_dependency_error()

    logger.info("\n--- 解决方案一：重新排序导入（不推荐） ---")
    reorder_imports_solution()

    logger.info("\n--- 解决方案二：导入-配置-运行模式 ---")
    import_configure_run_solution()

    logger.info("\n--- 解决方案三：动态导入 ---")
    dynamic_import_solution()

    logger.info("所有示例执行完毕")


if __name__ == "__main__":
    main()
