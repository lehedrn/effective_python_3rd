"""
本文件演示了如何使用 Python 的 warnings 模块来通知 API 使用者进行代码重构和迁移。
它展示了：
1. 基础示例：原始的 `print_distance` 函数及其问题；
2. 问题暴露：展示单位隐含导致的错误；
3. 改进后的版本：使用关键字参数明确单位；
4. 使用 warnings 发出警告；
5. 使用 stacklevel 提高警告可读性；
6. 将警告转换为错误；
7. 忽略警告；
8. 将警告写入日志；
9. 编写警告测试。

所有示例均包含错误用法和正确用法，并通过 main 函数统一运行。
"""

import warnings
import io
import logging
from contextlib import redirect_stderr


# 配置 logging 系统
def setup_logging():
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()]
    )


# 示例 1: 原始实现 - 隐式单位导致的问题
def print_distance_original(speed, duration):
    """
    原始版本，单位是隐式的（mph 和 hours）。
    容易因单位不匹配而导致计算错误。
    """
    distance = speed * duration
    logging.info(f"{distance} miles")


# 示例 2: 问题暴露 - 单位错误导致的结果偏差
def demonstrate_implicit_units_issue():
    """
    展示原始函数在单位不匹配时的错误结果。
    """
    logging.info("错误示例 - 子弹速度 1000 m/s，时间 3 秒，但结果被误认为是英里：")
    print_distance_original(1000, 3)


# 示例 3: 改进版本 - 显式指定单位
CONVERSIONS = {
    "mph": 1.60934 / 3600 * 1000,  # m/s
    "hours": 3600,                 # seconds
    "miles": 1.60934 * 1000,       # m
    "meters": 1,                   # m
    "m/s": 1,                      # m/s
    "seconds": 1,                  # s
}

def convert(value, units):
    rate = CONVERSIONS[units]
    return rate * value

def localize(value, units):
    rate = CONVERSIONS[units]
    return value / rate

def print_distance_explicit(
    speed,
    duration,
    *,
    speed_units="mph",
    time_units="hours",
    distance_units="miles",
):
    """
    改进版：显式传递单位，避免单位混淆。
    """
    norm_speed = convert(speed, speed_units)
    norm_duration = convert(duration, time_units)
    norm_distance = norm_speed * norm_duration
    distance = localize(norm_distance, distance_units)
    logging.info(f"{distance} {distance_units}")


# 示例 4: 使用 warnings 发出警告
def print_distance_with_warning(
    speed,
    duration,
    *,
    speed_units=None,
    time_units=None,
    distance_units=None,
):
    """
    添加警告提示调用者尽快更新代码以提供单位。
    """
    if speed_units is None:
        warnings.warn("speed_units will be required soon", DeprecationWarning)
        speed_units = "mph"

    if time_units is None:
        warnings.warn("time_units will be required soon", DeprecationWarning)
        time_units = "hours"

    if distance_units is None:
        warnings.warn("distance_units will be required soon", DeprecationWarning)
        distance_units = "miles"

    norm_speed = convert(speed, speed_units)
    norm_duration = convert(duration, time_units)
    norm_distance = norm_speed * norm_duration
    distance = localize(norm_distance, distance_units)
    logging.info(f"{distance} {distance_units}")

def demonstrate_deprecation_warning():
    """
    展示带有警告的函数调用。
    """
    fake_stderr = io.StringIO()
    with redirect_stderr(fake_stderr):
        logging.info("错误示例 - 不传单位参数，触发 DeprecationWarning：")
        print_distance_with_warning(1000, 3)

    logging.info(fake_stderr.getvalue())


# 示例 5: 使用 stacklevel 提升警告信息可读性
def require(name, value, default):
    """
    辅助函数，用于检测是否提供了参数，若未提供则发出警告。
    """
    if value is not None:
        return value
    warnings.warn(
        f"{name} will be required soon, update your code",
        DeprecationWarning,
        stacklevel=3,
    )
    return default

def print_distance_with_stacklevel(
    speed,
    duration,
    *,
    speed_units=None,
    time_units=None,
    distance_units=None,
):
    speed_units = require("speed_units", speed_units, "mph")
    time_units = require("time_units", time_units, "hours")
    distance_units = require("distance_units", distance_units, "miles")

    norm_speed = convert(speed, speed_units)
    norm_duration = convert(duration, time_units)
    norm_distance = norm_speed * norm_duration
    distance = localize(norm_distance, distance_units)
    logging.info(f"{distance} {distance_units}")

def demonstrate_stacklevel():
    """
    展示使用 stacklevel 后，警告指向正确的调用位置。
    """
    fake_stderr = io.StringIO()
    with redirect_stderr(fake_stderr):
        logging.info("错误示例 - 不传单位参数，stacklevel 警告定位到调用行：")
        print_distance_with_stacklevel(1000, 3)

    logging.info(fake_stderr.getvalue())


# 示例 6: 将警告转为错误
def demonstrate_warning_as_error():
    """
    将警告转为异常，用于自动化测试中捕捉潜在问题。
    """
    warnings.simplefilter("error")
    try:
        logging.info("将警告转为错误：")
        warnings.warn("This usage is deprecated", DeprecationWarning)
    except DeprecationWarning:
        logging.info("捕获到预期的 DeprecationWarning 异常")


# 示例 7: 忽略警告
def demonstrate_ignore_warnings():
    """
    忽略警告，适用于已知且不希望处理的情况。
    """
    warnings.simplefilter("ignore")
    logging.info("忽略警告：")
    warnings.warn("This warning is ignored")


# 示例 8: 将警告记录到日志
def setup_logging_for_warnings():
    """
    设置 logging 来捕获警告信息。
    """
    fake_stderr = io.StringIO()
    handler = logging.StreamHandler(fake_stderr)
    formatter = logging.Formatter("%(asctime)-15s WARNING] %(message)s")
    handler.setFormatter(formatter)

    logging.captureWarnings(True)
    logger = logging.getLogger("py.warnings")
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    return fake_stderr

def demonstrate_log_warnings():
    """
    展示如何将警告记录到日志系统中。
    """
    fake_stderr = setup_logging_for_warnings()

    logging.info("将警告记录到日志：")
    warnings.resetwarnings()
    warnings.simplefilter("default")
    warnings.warn("This warning will be logged")

    logging.info(fake_stderr.getvalue())
    warnings.resetwarnings()


# 示例 9: 编写警告测试
def test_warning_generation():
    """
    测试是否生成了预期的警告信息。
    """
    logging.info("测试警告是否按预期生成：")
    with warnings.catch_warnings(record=True) as found_warnings:
        result = require("my_arg", None, "fake units")
        assert result == "fake units"

        assert len(found_warnings) == 1
        single_warning = found_warnings[0]
        assert str(single_warning.message) == "my_arg will be required soon, update your code"
        assert single_warning.category == DeprecationWarning
        logging.info("✅ 测试通过：警告信息符合预期")


# 主函数 - 运行所有示例
def main():
    logging.info("=== 示例 1: 原始函数 ===")
    print_distance_original(5, 2.5)

    logging.info("=== 示例 2: 问题暴露 - 单位错误 ===")
    demonstrate_implicit_units_issue()

    logging.info("=== 示例 3: 显式单位版本 ===")
    print_distance_explicit(1000, 3, speed_units="meters", time_units="seconds")

    logging.info("=== 示例 4: 使用 warnings 发出警告 ===")
    demonstrate_deprecation_warning()

    logging.info("=== 示例 5: 使用 stacklevel 提高可读性 ===")
    demonstrate_stacklevel()

    logging.info("=== 示例 6: 将警告转为错误 ===")
    demonstrate_warning_as_error()

    logging.info("=== 示例 7: 忽略警告 ===")
    demonstrate_ignore_warnings()

    logging.info("=== 示例 8: 将警告记录到日志 ===")
    demonstrate_log_warnings()

    logging.info("=== 示例 9: 编写警告测试 ===")
    test_warning_generation()


if __name__ == "__main__":
    setup_logging()
    main()
