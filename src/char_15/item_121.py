"""
本模块演示了如何在 Python 中定义和使用自定义异常层次结构，以增强 API 的健壮性和可维护性。
- 展示了根异常的定义及其作用：隔离调用者、发现调用代码中的 bug、支持未来扩展。
- 包含错误示例与正确示例，并通过 main 函数运行完整的测试流程。
- 所有异常捕获均使用 logging 来记录错误信息以便调试。

主要知识点：
1. 定义模块级根异常 `Error`，所有其他异常继承该类。
2. 捕获根异常可以隔离意外情况并帮助识别调用代码中的问题。
3. 捕获 Python 内置的 `Exception` 基类用于检测 API 实现中的 bug。
4. 使用中间层级的根异常（如 WeightError）来组织更具体的异常类型。
"""

import logging

# 配置日志输出
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 自定义异常层级
class Error(Exception):
    """模块中所有异常的基类。"""
    pass


class InvalidDensityError(Error):
    """提供的密度值有问题。"""
    pass


class InvalidVolumeError(Error):
    """提供的体积值有问题。"""
    pass


class NegativeDensityError(InvalidDensityError):
    """提供的密度值为负数。"""
    pass


class WeightError(Error):
    """重量计算错误的基类。"""
    pass


class VolumeError(Error):
    """体积计算错误的基类。"""
    pass


class DensityError(Error):
    """密度计算错误的基类。"""
    pass


# 示例函数：基本异常使用
def example_basic_exceptions():
    """
    错误示例：直接抛出内置异常 ValueError。
    正确做法应是抛出自定义异常 InvalidDensityError。
    """
    def determine_weight(volume, density):
        if density <= 0:
            raise ValueError("Density must be positive")

    try:
        determine_weight(1, 0)
    except ValueError as e:
        logging.exception("捕获到 ValueError: %s", e)


# 示例函数：定义根异常并抛出自定义子类
def example_root_exception():
    """
    正确示例：定义模块级根异常 Error 及其子类，并使用它们抛出异常。
    调用者通过捕获根异常 Error 来隔离 API 异常。
    """

    def determine_weight(volume, density):
        if density < 0:
            raise InvalidDensityError("Density must be positive")
        if volume < 0:
            raise InvalidVolumeError("Volume must be positive")
        if volume == 0:
            1 / 0  # 故意引发未处理的异常

    try:
        determine_weight(1, -1)
    except Error as e:
        logging.exception("捕获到模块异常: %s", e)


# 示例函数：捕获根异常以发现调用代码中的 bug
def example_catch_root_for_caller_bug():
    """
    正确示例：仅捕获特定子类 InvalidDensityError，
             其他异常会传播至根异常 Error，提示调用代码存在问题。
    """

    def determine_weight(volume, density):
        if density < 0:
            raise InvalidDensityError("Density must be positive")
        if volume < 0:
            raise InvalidVolumeError("Volume must be positive")

    SENTINEL = object()
    weight = SENTINEL

    try:
        weight = determine_weight(-1, 1)
    except InvalidDensityError:
        weight = 0
    except Error as e:
        logging.exception("调用代码存在 bug: %s", e)

    print(f"Weight: {weight}")


# 示例函数：捕获 Exception 以发现 API 实现中的 bug
def example_catch_exception_for_api_bug():
    """
    正确示例：额外捕获 Exception 类型以识别 API 实现中的 bug。
    这里故意引发 ZeroDivisionError。
    """

    def determine_weight(volume, density):
        if density < 0:
            raise InvalidDensityError("Density must be positive")
        if volume == 0:
            density / volume  # 引发 ZeroDivisionError

    SENTINEL = object()
    weight = SENTINEL

    try:
        weight = determine_weight(0, 1)
    except InvalidDensityError:
        weight = 0
    except Error as e:
        logging.exception("调用代码存在 bug: %s", e)
    except Exception as e:
        logging.exception("API 实现存在 bug: %s", e)
        raise  # 重新抛出以供上层处理或调试


# 示例函数：未来扩展异常类型而不破坏现有代码
def example_future_proofing():
    """
    正确示例：新增具体异常类型 NegativeDensityError，
             现有代码仍能正常工作（因为它捕获父类 InvalidDensityError）。
    """

    class NegativeDensityError(InvalidDensityError):
        """提供的密度值为负数。"""
        pass

    def determine_weight(volume, density):
        if density < 0:
            raise NegativeDensityError("Density must be positive")

    try:
        determine_weight(1, -1)
    except InvalidDensityError as e:
        logging.exception("捕获到 InvalidDensityError: %s", e)


# 示例函数：使用中间根异常组织不同功能域的异常
def example_intermediate_root_exceptions():
    """
    正确示例：使用中间根异常（如 WeightError）将不同功能域的异常分类管理。
    """

    class WeightCalculationError(WeightError):
        """重量计算失败。"""
        pass

    class VolumeCalculationError(VolumeError):
        """体积计算失败。"""
        pass

    def calculate_weight(volume, density):
        if volume <= 0 or density <= 0:
            raise WeightCalculationError("体积或密度无效")
        return volume * density

    def calculate_volume(mass, density):
        if mass <= 0 or density <= 0:
            raise VolumeCalculationError("质量或密度无效")
        return mass / density

    try:
        calculate_volume(10, 0)
    except VolumeError as e:
        logging.exception("体积相关异常: %s", e)


# 主函数运行所有示例
def main():
    try:
        logging.info("开始运行示例 1：错误使用内置异常")
        example_basic_exceptions()
    except Exception as e:
        logging.exception("示例 1 出现异常: %s", e)

    try:
        logging.info("开始运行示例 2：使用模块根异常")
        example_root_exception()
    except Exception as e:
        logging.exception("示例 2 出现异常: %s", e)

    try:
        logging.info("开始运行示例 3：捕获根异常以发现调用代码中的 bug")
        example_catch_root_for_caller_bug()
    except Exception as e:
        logging.exception("示例 3 出现异常: %s", e)

    try:
        logging.info("开始运行示例 4：捕获 Exception 以发现 API 实现中的 bug")
        example_catch_exception_for_api_bug()
    except Exception as e:
        logging.exception("示例 4 出现异常: %s", e)

    try:
        logging.info("开始运行示例 5：未来扩展异常类型而不破坏现有代码")
        example_future_proofing()
    except Exception as e:
        logging.exception("示例 5 出现异常: %s", e)

    try:
        logging.info("开始运行示例 6：使用中间根异常组织不同功能域的异常")
        example_intermediate_root_exceptions()
    except Exception as e:
        logging.exception("示例 6 出现异常: %s", e)



if __name__ == "__main__":
    main()
