"""
本文件演示了为何应避免使用 `time` 模块进行时区转换，以及如何正确使用 `datetime` 和 `zoneinfo` 模块来处理本地时间。
示例包括：
1. 使用 `time` 模块将 UTC 时间戳转换为本地时间；
2. 使用 `time` 模块将本地时间字符串解析回 UTC 时间戳；
3. 错误地尝试使用 `time` 模块在不同时区之间转换（如 PST 到 EDT）；
4. 正确使用 `datetime` 和 `zoneinfo` 模块在多个时区之间转换（如 US/Eastern 到 US/Pacific）；
5. 将时间始终表示为 UTC，并在最后一步转换为本地时间以供展示。

所有函数都定义清晰，main 函数运行完整示例，并使用 logging 替代 print 进行输出。
"""

import logging
import time
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

# 配置日志
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def example_time_utc_to_local() -> None:
    """
    使用 `time` 模块将 UTC 时间戳转换为本地时间并格式化输出。
    """
    logger.info("示例 1: 使用 `time` 模块将 UTC 转换为本地时间")

    now = 1710047865.0  # 示例时间戳
    local_tuple = time.localtime(now)
    time_format = "%Y-%m-%d %H:%M:%S"
    time_str = time.strftime(time_format, local_tuple)
    logger.info(f"本地时间: {time_str}")


def example_time_local_to_utc() -> None:
    """
    使用 `time` 模块将本地时间字符串解析为时间元组，并转换为 UTC 时间戳。
    """
    logger.info("示例 2: 使用 `time` 模块将本地时间转为 UTC 时间戳")

    time_format = "%Y-%m-%d %H:%M:%S"
    time_str = "2024-03-09 21:17:45"
    time_tuple = time.strptime(time_str, time_format)
    utc_now = time.mktime(time_tuple)
    logger.info(f"UTC 时间戳: {utc_now}")


def example_time_timezone_conversion_wrong() -> None:
    """
    错误尝试使用 `time` 模块解析带时区的字符串（PST/EDT），演示其不可靠性。
    """
    logger.info("示例 3: 错误使用 `time` 解析带时区的时间字符串（如 EDT）")

    parse_format = "%Y-%m-%d %H:%M:%S %Z"

    # 成功解析 PST
    depart_sfo = "2024-03-09 21:17:45 PST"
    try:
        time_tuple = time.strptime(depart_sfo, parse_format)
        logger.info(f"成功解析 PST 时间: {time.strftime('%Y-%m-%d %H:%M:%S', time_tuple)}")
    except Exception as e:
        logger.error(f"解析 PST 失败: {e}")

    # 失败解析 EDT
    arrival_nyc = "2024-03-10 03:31:18 EDT"
    try:
        time_tuple = time.strptime(arrival_nyc, parse_format)
    except ValueError as e:
        logger.warning(f"解析 EDT 异常: {e} (平台依赖导致)")


def example_datetime_correct_timezone_conversion() -> None:
    """
    正确使用 `datetime` 和 `zoneinfo` 在不同时间区间转换。
    """
    logger.info("示例 4: 使用 `datetime` 和 `zoneinfo` 正确转换时区")

    time_format = "%Y-%m-%d %H:%M:%S"
    arrival_nyc_str = "2024-03-10 03:31:18"

    # 解析纽约时间（US/Eastern）
    nyc_dt_naive = datetime.strptime(arrival_nyc_str, time_format)
    eastern = ZoneInfo("US/Eastern")
    nyc_dt = nyc_dt_naive.replace(tzinfo=eastern)
    utc_dt = nyc_dt.astimezone(timezone.utc)

    logger.info(f"纽约时间 (EDT): {nyc_dt}")
    logger.info(f"UTC 时间: {utc_dt}")

    # 转换为旧金山时间（US/Pacific）
    pacific = ZoneInfo("US/Pacific")
    sf_dt = utc_dt.astimezone(pacific)
    logger.info(f"旧金山时间 (PST): {sf_dt}")

    # 转换为尼泊尔时间（Asia/Katmandu）
    nepal = ZoneInfo("Asia/Katmandu")
    nepal_dt = utc_dt.astimezone(nepal)
    logger.info(f"尼泊尔时间 (NPT): {nepal_dt}")


def example_always_use_utc_internally() -> None:
    """
    始终以 UTC 表示时间，并在最终步骤转换为本地时间用于展示。
    """
    logger.info("示例 5: 始终内部使用 UTC，仅展示时转换为本地时间")

    now_utc = datetime.now(timezone.utc)
    logger.info(f"当前 UTC 时间: {now_utc}")

    # 展示给用户时才转换为本地时间
    now_local = now_utc.astimezone()
    logger.info(f"展示用本地时间: {now_local}")


def main() -> None:
    """
    主函数，运行所有示例。
    """
    logger.info("开始执行完整示例...")

    example_time_utc_to_local()
    example_time_local_to_utc()
    example_time_timezone_conversion_wrong()
    example_datetime_correct_timezone_conversion()
    example_always_use_utc_internally()

    logger.info("完整示例执行完成。")


if __name__ == "__main__":
    main()
