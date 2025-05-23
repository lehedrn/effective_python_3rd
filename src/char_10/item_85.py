"""
本模块演示了在 Python 中使用 `try/except` 捕获异常时的最佳实践。
重点包括：
- 不要盲目捕获所有异常（如直接使用 `Exception` 类）
- 捕获宽泛的异常可能会掩盖代码中的严重错误
- 推荐记录详细的异常信息，而不是简单忽略或打印
- 示例中包含错误示例与正确示例，并通过 main 函数运行展示行为差异

该文件结构如下：
1. 定义多个函数来模拟不同场景下的异常处理方式
2. 包括不推荐的做法（错误示例）和推荐做法（正确示例）
3. 所有输出都使用 logging 模块替代 print 输出
"""

import logging

# 配置日志系统
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# -----------------------------
# 示例 1：基本错误捕获（仅捕获特定异常）
# -----------------------------

def load_data(path):
    """模拟加载数据，可能引发 FileNotFoundError"""
    with open(path, 'r') as file:
        return file.read()


def analyze_data(data):
    """模拟分析数据"""
    return "每日销售报告摘要"


def run_report_good(path):
    """正确版本：调用正确的 analyze_data 函数"""
    data = load_data(path)
    summary = analyze_data(data)
    return summary


def example_specific_exception_handling():
    """
    正确示例：只捕获已知的异常类型 FileNotFoundError。
    当文件不存在时，可以安全地处理，而其他错误（如 NameError）会抛出。
    """
    try:
        summary = run_report_good("nonexistent_file.txt")
        logging.info(f"报告生成成功: {summary}")
    except FileNotFoundError:
        logging.warning("警告：数据文件未找到，可能是临时问题。")


# -----------------------------
# 示例 2：捕获 Exception 的风险（宽泛异常捕获）
# -----------------------------

def run_report_bad(path):
    """
    错误版本：存在逻辑错误，调用了不存在的 analyze 函数。
    这将导致 NameError 异常。
    """
    data = load_data(path)
    summary = analyze(data)  # analyze 未定义，会抛出 NameError
    return summary


def example_broad_exception_catching():
    """
    错误示例：使用 `except Exception` 捕获所有异常，包括 NameError。
    这会导致程序无法发现代码中的逻辑错误。
    """
    try:
        summary = run_report_bad("some_file.txt")
        logging.info(f"报告生成成功: {summary}")
    except Exception:
        logging.error("发生异常：可能是临时问题或代码错误被掩盖")


# -----------------------------
# 示例 3：改进版宽泛异常捕获（记录详细信息）
# -----------------------------

def example_broad_exception_with_details():
    """
    改进示例：虽然仍使用 `Exception`，但记录了异常类型和消息，
    帮助识别潜在的代码错误，避免完全隐藏问题。
    """
    try:
        summary = run_report_bad("some_file.txt")
        logging.info(f"报告生成成功: {summary}")
    except Exception as e:
        logging.error(f"捕获到异常: 类型={type(e).__name__}, 消息={str(e)}")


# -----------------------------
# 示例 4：推荐做法 - 明确捕获多个具体异常
# -----------------------------

def run_report_multiple_exceptions(path):
    """
    模拟多种异常来源：
    - FileNotFoundError：文件未找到
    - ValueError：数据格式错误
    """
    data = load_data(path)
    if not data.startswith("valid"):
        raise ValueError("数据格式不正确")
    return analyze_data(data)


def example_multiple_specific_exceptions():
    """
    推荐做法：明确捕获多个具体异常类型，
    并对每种异常进行不同的处理。
    """
    try:
        summary = run_report_multiple_exceptions("invalid_data.txt")
        logging.info(f"报告生成成功: {summary}")
    except FileNotFoundError:
        logging.warning("警告：数据文件未找到")
    except ValueError as ve:
        logging.error(f"数据错误: {ve}")
    except Exception as e:
        logging.critical(f"未知异常: {e}")


# -----------------------------
# 主函数：运行所有示例
# -----------------------------

def main():
    logging.info("---------- 示例 1：捕获特定异常 ----------")
    example_specific_exception_handling()

    logging.info("---------- 示例 2：错误捕获宽泛异常 ----------")
    example_broad_exception_catching()

    logging.info("---------- 示例 3：改进版宽泛异常捕获（带详细信息）----------")
    example_broad_exception_with_details()

    logging.info("---------- 示例 4：推荐做法 - 多个具体异常处理 ----------")
    example_multiple_specific_exceptions()


if __name__ == "__main__":
    main()
