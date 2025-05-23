"""
本文件展示了如何在 Python 中编写健壮的异常处理代码，重点强调了始终让 `try` 块尽可能短的重要性。
通过错误示例和正确示例对比，说明了将多个可能引发异常的操作放在同一个 `try` 块中可能导致的问题，
并演示了如何使用 `else` 和嵌套 `try` 来实现更清晰、可维护的异常处理逻辑。

包含以下示例：
1. 错误示例：将多个潜在异常源放入一个 `try` 块。
2. 正确示例：将每个潜在异常源单独处理，使用 `else` 或后续 `try` 块。
3. 使用 logging 替代 print，提升日志专业性。
"""

import logging

# 配置 logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class RpcError(Exception):
    """模拟远程调用错误"""
    pass


def lookup_request(connection):
    """
    模拟远程请求，抛出 RpcError 异常。
    """
    logging.info("lookup_request called")
    raise RpcError("From lookup_request")


def is_cached(connection, request):
    """
    模拟缓存检查，抛出 RpcError 异常。
    """
    logging.info("is_cached called")
    raise RpcError("From is_cached")


def close_connection(connection):
    """
    关闭连接。
    """
    logging.info("Connection closed")


# -------------------------------
# 示例 1：错误示例 - 多个异常源在一个 try 块中
# -------------------------------

def bad_example():
    """
    错误示例：将多个可能引发异常的调用放在同一个 try 块中。
    导致无法判断具体是哪个函数引发了异常。
    """
    connection = object()
    try:
        request = lookup_request(connection)
        if is_cached(connection, request):  # 也可能引发异常
            request = None
    except RpcError:
        logging.error("Encountered error in bad_example!")
        close_connection(connection)


# -------------------------------
# 示例 2：正确示例 - 每个异常源独立处理
# -------------------------------

def good_example_separate_try():
    """
    正确示例：为每个可能引发异常的调用使用独立的 try 块。
    这样可以明确知道是哪个函数引发了异常。
    """
    connection = object()

    try:
        request = lookup_request(connection)
    except RpcError as e:
        logging.error(f"lookup_request failed: {e}")
        close_connection(connection)
        return

    try:
        if is_cached(connection, request):
            request = None
    except RpcError as e:
        logging.error(f"is_cached failed: {e}")
        close_connection(connection)
        return

    logging.info("No errors encountered.")


# -------------------------------
# 示例 3：正确示例 - 使用 else 分离非异常逻辑
# -------------------------------

def good_example_with_else():
    """
    正确示例：使用 else 块来分离不会引发异常的逻辑。
    如果 lookup_request 成功执行，则进入 else 块继续处理。
    """
    connection = object()

    try:
        request = lookup_request(connection)
    except RpcError as e:
        logging.error(f"lookup_request failed: {e}")
        close_connection(connection)
        return
    else:
        # 不会在这里捕获到 RpcError，除非 lookup_request 抛出了异常
        try:
            if is_cached(connection, request):
                request = None
        except RpcError as e:
            logging.error(f"is_cached failed: {e}")
            close_connection(connection)
            return

    logging.info("No errors encountered.")


# -------------------------------
# 主函数入口：运行所有示例
# -------------------------------

def main():
    logging.info("# 错误示例：多个异常源在一个 try 块中")
    bad_example()

    logging.info("# 正确示例：每个异常源独立处理")
    good_example_separate_try()

    logging.info("# 正确示例：使用 else 分离非异常逻辑")
    good_example_with_else()


if __name__ == '__main__':
    main()
