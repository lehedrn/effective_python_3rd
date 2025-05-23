"""
本文件展示了 Python 中 `eval` 和 `exec` 的使用方式，并通过示例说明了它们的潜在风险以及推荐用法。
同时提供了安全替代方案，帮助开发者理解为何应避免在生产代码中滥用这些函数。

示例内容包括：
1. `eval` 的基本用法和错误使用场景
2. `exec` 的基本用法及其作用域控制
3. 使用 `eval` 或 `exec` 可能导致的安全隐患
4. 推荐做法：动态编程特性替代方案（如 getattr、importlib 等）

所有示例均包含清晰注释与日志输出，便于调试与理解。
"""

import logging
import importlib.util

# 配置日志输出
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def example_eval_basic_usage():
    """
    示例 1: eval 的基本用法
    eval 用于执行单个表达式字符串并返回结果。
    """
    logger.info("=== 示例 1: eval 基本用法 ===")
    try:
        result = eval("1 + 2 * 3")
        logger.info(f"eval('1 + 2 * 3') 返回结果: {result}")
    except Exception as e:
        logger.error(f"eval 执行出错: {e}")


def example_eval_invalid_usage():
    """
    示例 2: eval 错误使用 —— 尝试执行多行语句
    eval 不支持多行语句，会抛出语法错误。
    """
    logger.info("=== 示例 2: eval 错误使用 ===")
    try:
        # 下面的代码会引发异常
        eval(
            """
if True:
    print('hello')
else:
    print('world')
"""
        )
    except SyntaxError as se:
        logger.warning(f"eval 多行语句导致语法错误: {se}")
    except Exception as e:
        logger.error(f"未知错误: {e}")


def example_exec_basic_usage():
    """
    示例 3: exec 的基本用法
    exec 可以执行多行代码块，并影响局部/全局作用域。
    """
    logger.info("=== 示例 3: exec 基本用法 ===")
    global_scope = {"my_condition": True}
    local_scope = {}

    exec_code = """
if my_condition:
    x = 'yes'
else:
    x = 'no'
    """

    exec(exec_code, global_scope, local_scope)

    logger.info(f"exec 执行后 local_scope 内容: {local_scope}")


def example_exec_security_risk():
    """
    示例 4: exec 的安全风险演示
    模拟用户输入被恶意构造，可能导致任意代码执行。
    """
    logger.info("=== 示例 4: exec 安全风险演示 ===")

    user_input = "__import__('os').system('echo 访问敏感数据或执行危险操作')"
    try:
        # 模拟执行用户输入内容
        exec(f"x = {user_input}")
    except Exception as e:
        logger.warning(f"exec 安全测试异常: {e}")
    else:
        logger.critical("⚠️ 警告：exec 允许执行任意系统命令！")


def example_safe_alternative_getattr():
    """
    示例 5: 使用 getattr 替代 eval/exec 动态访问属性
    推荐做法：避免使用 eval 获取对象属性。
    """
    logger.info("=== 示例 5: 使用 getattr 替代 eval ===")

    class MyClass:
        def __init__(self):
            self.name = "Lingma"

    obj = MyClass()
    attr_name = "name"
    value = getattr(obj, attr_name, None)
    logger.info(f"getattr(obj, '{attr_name}') 返回值: {value}")


def example_safe_alternative_dynamic_import():
    """
    示例 6: 使用 importlib 替代 exec 实现插件加载
    推荐做法：避免使用 exec 加载模块，改用 importlib。
    """

    logger.info("=== 示例 6: 使用 importlib 替代 exec 动态导入模块 ===")

    module_name = "math"
    function_name = "sqrt"

    try:
        module = importlib.import_module(module_name)
        func = getattr(module, function_name)
        result = func(16)
        logger.info(f"调用 {module_name}.{function_name}(16) 结果: {result}")
    except ImportError as ie:
        logger.error(f"模块导入失败: {ie}")
    except AttributeError as ae:
        logger.error(f"函数不存在: {ae}")


def main():
    """
    主函数：运行所有示例
    """
    logger.info("🚀 开始运行所有示例 🚀")
    example_eval_basic_usage()
    example_eval_invalid_usage()
    example_exec_basic_usage()
    example_exec_security_risk()
    example_safe_alternative_getattr()
    example_safe_alternative_dynamic_import()
    logger.info("✅ 所有示例运行完毕")


if __name__ == "__main__":
    main()

