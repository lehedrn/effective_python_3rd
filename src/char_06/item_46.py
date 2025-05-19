"""
本文件演示了 Python 生成器中 `yield` 和 `send` 的使用，以及与 `yield from` 结合时的潜在问题。
同时展示了通过传递迭代器来替代 `send` 方法的更清晰、推荐的方式。

主要内容包括：
1. 基础生成器示例（wave）
2. 使用 send 方法进行双向通信（wave_modulating）
3. yield from 与 send 结合的问题（complex_wave_modulating）
4. 推荐方式：通过参数传递迭代器（wave_cascading）
"""

import math
import logging

# 配置日志输出
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def wave(amplitude, steps):
    """
    基础波形生成器：根据指定幅度和步数生成正弦波值。

    Args:
        amplitude (float): 波形的最大幅度
        steps (int): 正弦波的一个周期内的采样点数量

    Yields:
        float: 当前步骤对应的正弦波输出值
    """
    step_size = 2 * math.pi / steps
    for step in range(steps):
        radians = step * step_size
        fraction = math.sin(radians)
        output = amplitude * fraction
        yield output


def transmit(output):
    """
    模拟信号传输函数，将生成器输出打印/记录为日志信息。

    Args:
        output (float or None): 要传输的输出值
    """
    if output is None:
        logger.info("Output is None")
    else:
        logger.info(f"Output: {output:>5.1f}")


def run(it):
    """
    运行基础波形生成器并逐个输出结果。

    Args:
        it (iterator): 一个生成器或可迭代对象
    """
    for output in it:
        transmit(output)


def wave_modulating(steps):
    """
    使用 send 方法调节幅度的波形生成器。

    Args:
        steps (int): 正弦波的一个周期内的采样点数量

    Yields:
        float: 当前步骤对应的正弦波输出值
    """
    step_size = 2 * math.pi / steps
    amplitude = yield  # 接收初始幅度
    for step in range(steps):
        radians = step * step_size
        fraction = math.sin(radians)
        output = amplitude * fraction
        amplitude = yield output  # 接收下一次的幅度


def run_modulating(it):
    """
    使用 send 方法运行调制波形生成器。

    Args:
        it (generator): 使用 send 方法的生成器
    """
    amplitudes = [None, 7, 7, 7, 2, 2, 2, 2, 10, 10, 10, 10, 10]
    for amplitude in amplitudes:
        output = it.send(amplitude)
        transmit(output)


def complex_wave_modulating():
    """
    使用 yield from 组合多个调幅波形生成器。
    展示了 yield from 与 send 方法结合使用时可能出现的问题。

    Yields:
        float: 不同阶段的波形输出值
    """
    yield from wave_modulating(3)
    yield from wave_modulating(4)
    yield from wave_modulating(5)


def wave_cascading(amplitude_it, steps):
    """
    推荐方式：使用外部迭代器控制幅度的波形生成器。

    Args:
        amplitude_it (iterator): 提供当前幅度的迭代器
        steps (int): 正弦波的一个周期内的采样点数量

    Yields:
        float: 当前步骤对应的正弦波输出值
    """
    step_size = 2 * math.pi / steps
    for _ in range(steps):
        fraction = math.sin(step_size * _)
        amplitude = next(amplitude_it)  # 获取下一个输入幅度
        yield amplitude * fraction


def complex_wave_cascading(amplitude_it):
    """
    推荐方式：使用 yield from 组合多个波形生成器。

    Args:
        amplitude_it (iterator): 提供当前幅度的迭代器

    Yields:
        float: 不同阶段的波形输出值
    """
    yield from wave_cascading(amplitude_it, 3)
    yield from wave_cascading(amplitude_it, 4)
    yield from wave_cascading(amplitude_it, 5)


def run_cascading():
    """
    使用迭代器运行组合波形生成器。
    """
    amplitudes = [7, 7, 7, 2, 2, 2, 2, 10, 10, 10, 10, 10]
    it = complex_wave_cascading(iter(amplitudes))
    for _ in amplitudes:
        output = next(it)
        transmit(output)


def main():
    """
    主函数：运行所有示例
    """
    logger.info("=== 基础波形生成器 ===")
    run(wave(3.0, 8))

    logger.info("\n=== 使用 send 方法的调幅波形 ===")
    modulating_gen = wave_modulating(12)
    run_modulating(modulating_gen)

    logger.info("\n=== 使用 yield from + send 的组合波形（包含意外 None 输出）===")
    complex_modulating_gen = complex_wave_modulating()
    run_modulating(complex_modulating_gen)

    logger.info("\n=== 推荐方式：使用迭代器控制幅度的组合波形 ===")
    run_cascading()


if __name__ == "__main__":
    main()
