"""
本文件演示了如何使用 `yield from` 组合多个生成器的完整示例。
包含以下内容：
- 传统方式组合生成器（冗余代码）
- 使用 `yield from` 简化生成器组合
- 错误示例：手动迭代多个生成器导致代码重复且难以维护
- 正确示例：使用 `yield from` 提高可读性和性能
"""

import logging

# 设置日志配置
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# -----------------------------
# 示例1：传统方式组合生成器（错误示例）
# -----------------------------
def move(period, speed):
    """
    生成一个表示移动速度的序列，每个元素为 speed，共 period 个。
    """
    for _ in range(period):
        yield speed


def pause(delay):
    """
    生成一个表示暂停的序列，每个元素为 0，共 delay 个。
    """
    for _ in range(delay):
        yield 0


def animate():
    """
    手动组合多个生成器，代码冗余且难以维护。
    """
    for delta in move(4, 5.0):
        yield delta
    for delta in pause(3):
        yield delta
    for delta in move(2, 3.0):
        yield delta


# -----------------------------
# 示例2：使用 yield from 组合生成器（正确示例）
# -----------------------------
def animate_composed():
    """
    使用 `yield from` 组合多个生成器，消除冗余代码，提高可读性。
    """
    yield from move(4, 5.0)
    yield from pause(3)
    yield from move(2, 3.0)


# -----------------------------
# 渲染函数：用于处理生成器输出的 delta 值
# -----------------------------
def render(delta):
    """
    模拟图像渲染逻辑，接收 delta 并记录日志。
    """
    logging.info(f"Delta: {delta:.1f}")
    # 实际应用中可以在此处添加图像移动逻辑


def run(func):
    """
    运行传入的生成器函数，并逐个处理其产出的值。
    """
    for delta in func():
        render(delta)


# -----------------------------
# 主函数：运行所有示例
# -----------------------------
def main():
    logging.info("开始执行传统方式组合生成器示例")
    run(animate)

    logging.info("开始执行使用 yield from 的优化示例")
    run(animate_composed)


if __name__ == '__main__':
    main()
