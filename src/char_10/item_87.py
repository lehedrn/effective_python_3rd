"""
本模块演示了如何使用 Python 内置的 `traceback` 模块来增强异常报告，适用于单线程和并发程序。
示例包括：
- 默认的异常堆栈跟踪输出
- 在 try/except 中捕获异常但不打印回溯信息的问题
- 使用 traceback.print_tb() 打印详细的堆栈信息
- 提取并处理 traceback 信息（如函数名）
- 将异常信息记录到文件中

注意事项：
- 代码符合 PEP8 规范
- 使用 logging 替代 print 进行日志记录
"""

import logging
import traceback
import json

# 配置日志系统
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ==============================
# 示例 1：默认的异常堆栈跟踪输出
# ==============================

def example_default_exception():
    """
    示例说明：
    展示当未捕获异常时，Python 默认打印的堆栈跟踪。
    """

    def inner_func(message):
        assert False, message

    def outer_func(message):
        inner_func(message)

    try:
        outer_func("Oops! (Default Exception)")
    except AssertionError as e:
        logging.error("发生异常: %s", e)
        raise  # 重新抛出以触发默认的 traceback 输出


# ==============================
# 示例 2：在 try/except 中捕获异常但不打印回溯信息
# ==============================

def example_catch_without_traceback():
    """
    示例说明：
    当异常被捕获但只打印 repr(e)，无法获取完整的堆栈跟踪，调试困难。
    """

    class Request:
        def __init__(self, body):
            self.body = body
            self.response = None

    def do_work(data):
        assert False, data

    def handle(request):
        try:
            do_work(request.body)
        except BaseException as e:
            logging.warning("仅打印异常字符串表示: %s", repr(e))
            request.response = 400  # 错误请求

    request = Request("My message")
    handle(request)
    logging.info("响应状态码: %d", request.response)


# ==============================
# 示例 3：使用 traceback.print_tb() 打印详细的堆栈信息
# ==============================

def example_print_traceback():
    """
    示例说明：
    使用 traceback.print_tb() 显式打印堆栈跟踪信息，帮助定位问题源头。
    """

    class Request:
        def __init__(self, body):
            self.body = body
            self.response = None

    def do_work(data):
        assert False, data

    def handle2(request):
        try:
            do_work(request.body)
        except BaseException as e:
            logging.error("异常发生，正在打印堆栈跟踪:")
            traceback.print_tb(e.__traceback__)
            logging.warning("异常内容: %s", repr(e))
            request.response = 400

    request = Request("My message 2")
    handle2(request)
    logging.info("响应状态码: %d", request.response)


# ==============================
# 示例 4：提取并处理 traceback 信息（如函数名）
# ==============================

def example_extract_function_names():
    """
    示例说明：
    使用 traceback.extract_tb() 提取堆栈帧中的函数名，用于分析调用链。
    """

    class Request:
        def __init__(self, body):
            self.body = body
            self.response = None

    def do_work(data):
        assert False, data

    def handle3(request):
        try:
            do_work(request.body)
        except BaseException as e:
            stack = traceback.extract_tb(e.__traceback__)
            logging.info("异常堆栈中的函数名:")
            for frame in stack:
                logging.info("- %s", frame.name)
            logging.warning("异常内容: %s", repr(e))
            request.response = 400

    request = Request("My message 3")
    handle3(request)
    logging.info("响应状态码: %d", request.response)


# ==============================
# 示例 5：将异常信息记录到文件中
# ==============================

def example_log_to_file():
    """
    示例说明：
    使用 traceback 模块提取堆栈信息，并将异常信息格式化为 JSON 写入日志文件。
    """

    import os

    LOG_FILE = "my_log.jsonl"

    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)  # 清空旧日志

    def log_if_error(file_path, target, *args, **kwargs):
        try:
            target(*args, **kwargs)
        except BaseException as e:
            stack = traceback.extract_tb(e.__traceback__)
            stack_without_wrapper = stack[1:]  # 去除 wrapper 自身的堆栈帧
            trace_dict = {
                'stack': [item.name for item in stack_without_wrapper],
                'error_type': type(e).__name__,
                'error_message': str(e),
            }
            json_data = json.dumps(trace_dict, ensure_ascii=False)
            with open(file_path, "a", encoding="utf-8") as f:
                f.write(json_data + "\n")

    def do_work(data):
        assert False, data

    log_if_error(LOG_FILE, do_work, "First error")
    log_if_error(LOG_FILE, do_work, "Second error")

    logging.info("已写入异常日志至 %s", LOG_FILE)
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            logging.info("读取日志: %s", line.strip())


# ==============================
# 主函数入口
# ==============================

def main():
    logging.info("开始执行示例 1：默认异常堆栈跟踪输出")
    try:
        example_default_exception()
    except Exception as e:
        logging.exception("示例 1 异常: %s", e)

    logging.info("\n开始执行示例 2：捕获异常但不打印回溯信息")
    example_catch_without_traceback()

    logging.info("\n开始执行示例 3：使用 traceback.print_tb() 打印堆栈信息")
    example_print_traceback()

    logging.info("\n开始执行示例 4：提取函数名")
    example_extract_function_names()

    logging.info("\n开始执行示例 5：记录异常到文件")
    example_log_to_file()


if __name__ == "__main__":
    main()
