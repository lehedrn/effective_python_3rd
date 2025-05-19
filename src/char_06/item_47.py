"""
本文件展示了关于 Python 生成器的 `throw` 方法以及使用类替代 `throw` 的最佳实践。
包含了错误示例和推荐做法示例，并使用 logging 替代 print 输出信息。
每个示例封装在独立函数中，main 函数统一调用运行。
"""

import logging

# 配置日志输出格式
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# 示例1：基础 throw 使用
def example_basic_throw_usage():
    """
    展示最简单的 generator 中 throw 的使用方式。
    """

    def my_generator():
        yield 1
        yield 2
        yield 3

    gen = my_generator()
    logging.info(f'Yield: {next(gen)}')  # 输出 1
    logging.info(f'Yield: {next(gen)}')  # 输出 2
    try:
        gen.throw(ValueError("手动抛出异常"))
    except ValueError as e:
        logging.error(f"捕获到异常: {e}")


# 示例2：generator 捕获 throw 抛出的异常
def example_generator_catch_thrown_exception():
    """
    展示 generator 如何捕获由 throw 抛出的异常。
    """

    class MyError(Exception):
        pass

    def my_generator():
        yield 1
        try:
            yield 2
        except MyError:
            logging.info("捕获到 MyError")
        yield 4

    gen = my_generator()
    logging.info(f'Yield: {next(gen)}')
    logging.info(f'Yield: {next(gen)}')
    logging.info(f'Yield after throw: {gen.throw(MyError("测试"))}')
    try:
        logging.info(f'Yield: {next(gen)}')
    except StopIteration:
        logging.info("Generator has finished")


# 示例3：使用 throw 实现计时器重置（非推荐写法）
def example_timer_with_throw():
    """
    使用 throw 实现定时器重置逻辑（不推荐）。
    """

    class Reset(Exception):
        pass

    def timer(period):
        current = period
        while current > 0:
            try:
                yield current
            except Reset:
                logging.info("Resetting timer")
                current = period
            else:
                current -= 1

    resets = [False, False, False, True, False, True]

    def check_for_reset():
        if resets:
            return resets.pop(0)
        return False

    def announce(ticks):
        logging.info(f"{ticks} ticks remaining")

    def run():
        gen = timer(4)
        while True:
            try:
                if check_for_reset():
                    current = gen.throw(Reset())
                else:
                    current = next(gen)
            except StopIteration:
                break
            announce(current)

    logging.info("=== 使用 throw 的计时器 ===")
    run()


# 示例4：使用类实现相同功能（推荐写法）
def example_timer_with_class():
    """
    使用 Timer 类实现计时器及其重置功能（推荐做法）。
    """

    class Timer:
        def __init__(self, period):
            self.current = period
            self.period = period

        def reset(self):
            logging.info("Resetting timer")
            self.current = self.period

        def tick(self):
            before = self.current
            self.current -= 1
            return before

        def __bool__(self):
            return self.current > 0

    resets = [False, False, False, True, False, True]

    def check_for_reset():
        if resets:
            return resets.pop(0)
        return False


    def announce(ticks):
        logging.info(f"{ticks} ticks remaining")

    def run():
        timer = Timer(4)
        while timer:
            if check_for_reset():
                timer.reset()
            announce(timer.tick())

    logging.info("=== 使用类的计时器 ===")
    run()


# 主函数：运行所有示例
def main():
    logging.info("=== 示例1: 基础 throw 使用 ===")
    example_basic_throw_usage()

    logging.info("\n=== 示例2: generator 捕获 throw 异常 ===")
    example_generator_catch_thrown_exception()

    logging.info("\n=== 示例3: 使用 throw 实现计时器 ===")
    example_timer_with_throw()

    logging.info("\n=== 示例4: 推荐做法 - 使用类实现计时器 ===")
    example_timer_with_class()


if __name__ == '__main__':
    main()
