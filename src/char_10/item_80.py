"""
本模块展示了 Python 中 `try`/`except`/`else`/`finally` 的使用方式，涵盖以下内容：
1. `try` / `finally`：用于异常传播时执行清理逻辑。
2. `try` / `except` / `else`：明确划分异常处理与成功路径。
3. 综合使用 `try` / `except` / `else` / `finally`。
4. 包含错误示例和正确示例，每个函数独立演示一个知识点。
"""

import json
import logging
import os

# 配置日志输出
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def delete_file(filename):
    if os.path.exists(filename):
        os.remove(filename)
    logger.info(f"{filename} is deleted...")

def example_try_finally_success():
    """
    正确示例：try/finally 示例，在文件读取后关闭句柄，即使发生异常也保证关闭。
    本例模拟正常读取文件。
    """
    logger.info("example_try_finally_success: 开始")
    filename = "random_data.txt"
    # 往random_data.txt 写入数据
    with open(filename, "w") as f:
        f.write("This is a test file.")
    try:
        handle = open(filename, encoding="utf-8")
        try:
            data = handle.read()
            logger.info(f"读取到数据: {data}")
        finally:
            handle.close()
            logger.info("文件已关闭")
            delete_file(filename)
    except Exception as e:
        logger.error(f"发生异常: {e}")


def example_try_finally_error_during_read():
    """
    错误示例：try/finally 示例，文件打开成功但读取失败（编码错误），确保 finally 块仍运行。
    """
    logger.info("example_try_finally_error_during_read: 开始")
    filename = "random_data_invalid_utf8.txt"
    with open(filename, "wb") as f:
        f.write(b"\xf1\xf2\xf3\xf4\xf5")  # 无效的 UTF-8 字节序列

    try:
        handle = open(filename, encoding="utf-8")
        try:
            data = handle.read()  # 这里会抛出 UnicodeDecodeError
            logger.info(f"读取到数据: {data}")
        finally:
            handle.close()
            logger.info("文件已关闭")
            delete_file(filename)
    except UnicodeDecodeError as e:
        logger.error(f"Unicode 解码错误: {e}")


def example_try_finally_open_failed():
    """
    错误示例：try/finally 中 open 失败的情况，此时不进入 finally 块。
    """
    logger.info("example_try_finally_open_failed: 开始")
    filename = "non_existent_file.txt"

    try:
        handle = open(filename, encoding="utf-8")
        try:
            data = handle.read()
            logger.info(f"读取到数据: {data}")
        finally:
            handle.close()
            logger.info("文件已关闭")
    except FileNotFoundError as e:
        logger.error(f"文件未找到: {e}")


def example_try_except_else_success():
    """
    正确示例：try/except/else 使用，区分异常处理与成功流程。
    成功解析 JSON 并返回键值。
    """
    logger.info("example_try_except_else_success: 开始")
    data = '{"key": "value"}'

    try:
        result_dict = json.loads(data)
    except ValueError:
        logger.warning("JSON 解析失败")
        raise KeyError("key")
    else:
        value = result_dict["key"]
        logger.info(f"获取到键值: {value}")
        return value


def example_try_except_else_json_parse_error():
    """
    错误示例：try/except/else 使用，JSON 解析失败。
    捕获并转换异常。
    """
    logger.info("example_try_except_else_json_parse_error: 开始")
    data = '{"key": bad_payload}'

    try:
        result_dict = json.loads(data)
    except ValueError:
        logger.warning("JSON 解析失败，抛出 KeyError")
        raise KeyError("key")


def example_try_except_else_key_error():
    """
    错误示例：try/except/else 使用，JSON 解析成功但键不存在。
    异常不在 try 块中，直接传播。
    """
    logger.info("example_try_except_else_key_error: 开始")
    data = '{"key": "value"}'

    try:
        result_dict = json.loads(data)
    except ValueError:
        logger.warning("JSON 解析失败")
        raise KeyError("key")
    else:
        value = result_dict["missing_key"]  # KeyError 将传播出去
        logger.info(f"获取到键值: {value}")
        return value


def example_full_usage_success():
    """
    正确示例：综合使用 try/except/else/finally。
    成功读取、计算、写回 JSON 文件。
    """
    logger.info("example_full_usage_success: 开始")
    temp_path = "temp_full_usage.json"
    with open(temp_path, "w") as f:
        f.write('{"numerator": 10, "denominator": 2}')

    UNDEFINED = object()

    def divide_json(path):
        handle = open(path, "r+")
        try:
            data = handle.read()
            op = json.loads(data)
            value = op["numerator"] / op["denominator"]
            logger.info(f"计算结果: {value}")
        except ZeroDivisionError:
            logger.warning("除数为零")
            return UNDEFINED
        else:
            op["result"] = value
            result = json.dumps(op)
            handle.seek(0)
            handle.write(result)
            logger.info("写入更新后的 JSON 数据")
            return value
        finally:
            handle.close()
            logger.info("文件已关闭")

    result = divide_json(temp_path)
    logger.info(f"最终结果: {result}")

    delete_file(temp_path)


def example_full_usage_zero_division():
    """
    错误示例：综合使用 try/except/else/finally。
    除数为零，触发 ZeroDivisionError。
    """
    logger.info("example_full_usage_zero_division: 开始")
    temp_path = "temp_full_usage_zero.json"
    with open(temp_path, "w") as f:
        f.write('{"numerator": 10, "denominator": 0}')

    UNDEFINED = object()

    def divide_json(path):
        handle = open(path, "r+")
        try:
            data = handle.read()
            op = json.loads(data)
            value = op["numerator"] / op["denominator"]
            logger.info(f"计算结果: {value}")
        except ZeroDivisionError:
            logger.warning("除数为零")
            return UNDEFINED
        else:
            op["result"] = value
            result = json.dumps(op)
            handle.seek(0)
            handle.write(result)
            logger.info("写入更新后的 JSON 数据")
            return value
        finally:
            handle.close()
            logger.info("文件已关闭")

    result = divide_json(temp_path)
    logger.info(f"最终结果: {result}")

    delete_file(temp_path)


def example_full_usage_invalid_json():
    """
    错误示例：综合使用 try/except/else/finally。
    JSON 格式错误，异常在 try 块中抛出，finally 仍执行。
    """
    logger.info("example_full_usage_invalid_json: 开始")
    temp_path = "temp_full_usage_invalid.json"
    with open(temp_path, "w") as f:
        f.write('{"numerator": 10 bad_data}')

    UNDEFINED = object()

    def divide_json(path):
        handle = open(path, "r+")
        try:
            data = handle.read()
            op = json.loads(data)
            value = op["numerator"] / op["denominator"]
            logger.info(f"计算结果: {value}")
        except ZeroDivisionError:
            logger.warning("除数为零")
            return UNDEFINED
        else:
            op["result"] = value
            result = json.dumps(op)
            handle.seek(0)
            handle.write(result)
            logger.info("写入更新后的 JSON 数据")
            return value
        finally:
            handle.close()
            logger.info("文件已关闭")

    try:
        result = divide_json(temp_path)
        logger.info(f"最终结果: {result}")
    except json.JSONDecodeError as e:
        logger.error(f"JSON 解码失败: {e}")
    finally:
        delete_file(temp_path)


def main():
    logger.info("开始执行示例...")

    logger.info("\n--- 示例 1: try/finally 成功 ---")
    example_try_finally_success()

    logger.info("\n--- 示例 2: try/finally 读取错误 ---")
    example_try_finally_error_during_read()

    logger.info("\n--- 示例 3: try/finally 打开失败 ---")
    example_try_finally_open_failed()

    logger.info("\n--- 示例 4: try/except/else 成功 ---")
    example_try_except_else_success()

    logger.info("\n--- 示例 5: try/except/else JSON 解析失败 ---")
    try:
        example_try_except_else_json_parse_error()
    except KeyError as e:
        logger.error(f"捕获到 Key Error: {e}")

    logger.info("\n--- 示例 6: try/except/else 键缺失 ---")
    try:
        example_try_except_else_key_error()
    except KeyError as e:
        logger.error(f"捕获到 Key Error: {e}")

    logger.info("\n--- 示例 7: 综合使用成功 ---")
    example_full_usage_success()

    logger.info("\n--- 示例 8: 综合使用除零错误 ---")
    example_full_usage_zero_division()

    logger.info("\n--- 示例 9: 综合使用 JSON 解析失败 ---")
    example_full_usage_invalid_json()


if __name__ == "__main__":
    main()
