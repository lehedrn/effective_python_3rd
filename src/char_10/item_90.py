"""
本文件演示了 Python 中 `__debug__` 标志和 `assert` 语句的行为。
通过多个函数示例，展示了如何正确使用断言进行调试、错误用法及其影响。
同时，提供了禁用断言时的运行结果对比，并建议替代方案以避免直接依赖或修改 `__debug__`。

功能包括：
- assert 的基本使用
- 使用 __debug__ 控制复杂验证逻辑
- 禁用 assert（通过 -O 参数）
- 不可变的 __debug__
- 替代 __debug__ 的自定义调试标志
"""

import logging

# 配置日志输出
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def example_assert_basic():
    """
    示例1：assert 基本使用。
    当条件不满足时抛出 AssertionError。
    """

    n = 3
    try:
        logging.info("执行 assert n % 2 == 0, f'{n=} not even'")
        assert n % 2 == 0, f"{n=} not even"
    except AssertionError as e:
        logging.error(f"捕获到 AssertionError: {e}")


def example_debug_flag_control_expensive_check():
    """
    示例2：使用 `__debug__` 来控制昂贵的验证逻辑。
    只有在 debug 模式下才会执行这些检查。
    """

    def expensive_check(x):
        logging.info(f"正在执行 expensive_check({x})")
        return x != 2

    items = [1, 2, 3]

    if __debug__:
        for i in items:
            try:
                logging.info(f"执行 assert expensive_check({i}), f'Failed {i=}'")
                assert expensive_check(i), f"Failed {i=}"
            except AssertionError as e:
                logging.error(f"捕获到 AssertionError: {e}")
    else:
        logging.info("当前处于优化模式 (__debug__ == False)，跳过 expensive_check")


def example_run_with_optimized_mode():
    """
    示例3：演示在 `-O` 模式下 assert 被完全忽略。
    此函数中的 assert 不会生效。
    """

    logging.info("进入 example_run_with_optimized_mode 函数")

    try:
        logging.info("执行 assert False, 'FAIL'")
        assert False, "FAIL"
    except AssertionError as e:
        logging.error(f"捕获到 AssertionError: {e}")

    logging.info("执行 print('OK')")
    print("OK")


# def example_cannot_set_debug_to_false():
#     """
#     示例4：尝试在运行时修改 `__debug__` 会引发 SyntaxError。
#     这是一个错误示例。
#     """
#
#     logging.info("尝试修改 __debug__ = False")
#     try:
#         # 下面这行代码将引发语法错误
#         __debug__ = False
#     except Exception as e:
#         logging.error(f"捕获到异常: {type(e).__name__} - {e}")


def example_custom_debug_flag():
    """
    示例5：推荐做法 —— 使用自定义 debug 标志代替 `__debug__`。
    便于控制调试行为，且不会受到 -O 参数影响。
    """

    enable_debug = True  # 自定义调试开关

    def custom_expensive_check(x):
        logging.info(f"执行 custom_expensive_check({x})")
        return x != 2

    items = [1, 2, 3]

    if enable_debug:
        for i in items:
            try:
                logging.info(f"执行 assert custom_expensive_check({i}), f'Check failed {i=}'")
                assert custom_expensive_check(i), f"Check failed {i=}"
            except AssertionError as e:
                logging.error(f"捕获到 AssertionError: {e}")
    else:
        logging.info("自定义调试关闭，跳过 expensive check")


def main():
    """主函数：依次调用所有示例函数以展示不同行为。"""
    logging.info("开始执行示例程序...")

    logging.info("\n--- 示例1: assert 基本使用 ---")
    example_assert_basic()

    logging.info("\n--- 示例2: 使用 __debug__ 控制昂贵检查 ---")
    example_debug_flag_control_expensive_check()

    logging.info("\n--- 示例3: 在 -O 模式下 assert 被忽略 (请使用 python -O 执行) ---")
    example_run_with_optimized_mode()

    # logging.info("\n--- 示例4: 尝试修改 __debug__ 失败 ---")
    # example_cannot_set_debug_to_false()

    logging.info("\n--- 示例5: 使用自定义 debug 标志 ---")
    example_custom_debug_flag()

    logging.info("\n--- 示例程序结束 ---")


if __name__ == "__main__":
    main()
