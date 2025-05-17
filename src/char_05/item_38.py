"""
本模块演示了 Python 中使用装饰器时为什么需要 `functools.wraps` 的原因，以及不使用 `wraps` 会带来的问题。
包括函数元信息丢失、help() 失效、pickle 序列化失败等。同时提供了错误示例和正确示例，并通过 logging 模块记录日志。

包含以下示例：
1. 错误示例：未使用 wraps 的 trace 装饰器
2. 正确示例：使用 wraps 的 trace 装饰器
3. 验证 help() 是否正常显示 docstring
4. 验证 pickle 是否能序列化装饰器函数

所有示例都封装在单独的函数中，并在 main 函数中统一调用执行。
"""
import io
import logging
import pickle
import sys
from functools import wraps

# 设置 logging 基础配置
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# 示例 1: 错误示例 - 不使用 wraps 的装饰器
def bad_trace(func):
    def wrapper(*args, **kwargs):
        args_repr = repr(args)
        kwargs_repr = repr(kwargs)
        result = func(*args, **kwargs)
        logging.info(f"{func.__name__}({args_repr}, {kwargs_repr}) -> {result!r}")
        return result

    return wrapper


@bad_trace
def bad_fibonacci(n):
    """Return the n-th Fibonacci number"""
    if n in (0, 1):
        return n
    return bad_fibonacci(n - 2) + bad_fibonacci(n - 1)


# 示例 2: 正确示例 - 使用 wraps 的装饰器
def good_trace(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        args_repr = repr(args)
        kwargs_repr = repr(kwargs)
        result = func(*args, **kwargs)
        logging.info(f"{func.__name__}({args_repr}, {kwargs_repr}) -> {result!r}")
        return result

    return wrapper


@good_trace
def good_fibonacci(n):
    """Return the n-th Fibonacci number"""
    if n in (0, 1):
        return n
    return good_fibonacci(n - 2) + good_fibonacci(n - 1)


# 示例 3: 验证 help() 是否正常输出 docstring

def test_help():
    logging.info("=== 测试 help() 输出 ===")

    # 捕获 help(bad_fibonacci) 的输出
    logging.info("错误示例（无 wraps）的 help() 输出:")
    f = io.StringIO()
    sys.stdout = f  # 将 stdout 重定向到 StringIO 对象
    help(bad_fibonacci)
    sys.stdout = sys.__stdout__  # 恢复 stdout
    logging.info(f"\n {f.getvalue()}")  # 将捕获的内容通过 logging 输出

    # 捕获 help(good_fibonacci) 的输出
    logging.info("正确示例（有 wraps）的 help() 输出:")
    f = io.StringIO()
    sys.stdout = f
    help(good_fibonacci)
    sys.stdout = sys.__stdout__
    logging.info(f"\n {f.getvalue()}")


# 示例 4: 验证 pickle 是否可以序列化函数
def test_pickle():
    logging.info("=== 测试 pickle 序列化 ===")

    try:
        logging.info("尝试序列化未使用 wraps 的函数...")
        serialized = pickle.dumps(bad_fibonacci)
        logging.info(f"未使用 wraps 的函数序列化成功: {serialized[:50]}...")  # 只显示部分数据
    except Exception as e:
        logging.error(f"未使用 wraps 的函数序列化失败: {e}")

    try:
        logging.info("尝试序列化使用 wraps 的函数...")
        serialized = pickle.dumps(good_fibonacci)
        logging.info(f"使用 wraps 的函数序列化成功: {serialized[:50]}...")  # 只显示部分数据
    except Exception as e:
        logging.error(f"使用 wraps 的函数序列化失败: {e}")


# 主函数，运行所有示例
def main():
    logging.info("=== 错误示例：未使用 wraps 的装饰器 ===")
    bad_fibonacci(3)

    logging.info("=== 正确示例：使用 wraps 的装饰器 ===")
    good_fibonacci(3)

    logging.info("=== 测试 help() 输出 ===")
    test_help()

    logging.info("=== 测试 pickle 序列化 ===")
    test_pickle()


if __name__ == "__main__":
    main()
