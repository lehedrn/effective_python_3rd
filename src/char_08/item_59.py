"""
本模块演示了如何使用 Python 的 `@property` 装饰器来改进类的设计，包括从简单属性过渡到即时计算的示例。
同时展示了错误和正确的实现方式，并通过函数封装每个示例以便清晰理解。

主要内容：
- 使用 `@property` 为现有属性添加新功能
- 逐步改进数据模型
- 避免过度使用 `@property`
"""

import logging
from datetime import datetime, timedelta

# 设置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 示例1：原始Bucket类（错误示例）
class Bucket:
    def __init__(self, period):
        self.period_delta = timedelta(seconds=period)
        self.reset_time = datetime.now()
        self.quota = 0

    def __repr__(self):
        return f"Bucket(quota={self.quota})"


def fill(bucket, amount):
    now = datetime.now()
    if (now - bucket.reset_time) > bucket.period_delta:
        bucket.quota = 0
        bucket.reset_time = now
    bucket.quota += amount


def deduct(bucket, amount):
    now = datetime.now()
    if (now - bucket.reset_time) > bucket.period_delta:
        return False  # Bucket hasn't been filled this period
    if bucket.quota - amount < 0:
        return False  # Bucket was filled, but not enough
    bucket.quota -= amount
    return True       # Bucket had enough, quota consumed


def demo_original_bucket():
    """演示原始Bucket类的行为."""
    logging.info("初始示例: 原始Bucket类")
    bucket = Bucket(60)
    fill(bucket, 100)
    logging.info(f"填充后: {bucket}")

    if deduct(bucket, 99):
        logging.info("成功扣除99配额")
    else:
        logging.info("配额不足")
    logging.info(f"扣除后: {bucket}")

    if deduct(bucket, 3):
        logging.info("成功扣除3配额")
    else:
        logging.info("配额不足")
    logging.info(f"最终状态: {bucket}")


# 示例2：改进后的NewBucket类（正确示例）
class NewBucket:
    def __init__(self, period):
        self.period_delta = timedelta(seconds=period)
        self.reset_time = datetime.now()
        self.max_quota = 0
        self.quota_consumed = 0

    def __repr__(self):
        return f"NewBucket(max_quota={self.max_quota}, quota_consumed={self.quota_consumed})"

    @property
    def quota(self):
        return self.max_quota - self.quota_consumed

    @quota.setter
    def quota(self, amount):
        delta = self.max_quota - amount
        if amount == 0:
            # Quota being reset for a new period
            self.quota_consumed = 0
            self.max_quota = 0
        elif delta < 0:
            # Quota being filled during the period
            self.max_quota = amount + self.quota_consumed
        else:
            # Quota being consumed during the period
            self.quota_consumed = delta


def demo_improved_bucket():
    """演示改进后的NewBucket类."""
    logging.info("改进示例: NewBucket类")
    bucket = NewBucket(60)
    logging.info(f"初始化: {bucket}")

    fill(bucket, 100)
    logging.info(f"填充后: {bucket}")

    if deduct(bucket, 99):
        logging.info("成功扣除99配额")
    else:
        logging.info("配额不足")
    logging.info(f"当前状态: {bucket}")

    if deduct(bucket, 3):
        logging.info("成功扣除3配额")
    else:
        logging.info("配额不足")
    logging.info(f"最终状态: {bucket}")


# 示例3：过度使用@property的反面案例
class OverusedPropertyBucket:
    def __init__(self, period):
        self.period_delta = timedelta(seconds=period)
        self.reset_time = datetime.now()
        self._max_quota = 0
        self._quota_consumed = 0

    @property
    def quota(self):
        return self._max_quota - self._quota_consumed

    @quota.setter
    def quota(self, amount):
        delta = self._max_quota - amount
        if amount == 0:
            self._quota_consumed = 0
            self._max_quota = 0
        elif delta < 0:
            self._max_quota = amount + self._quota_consumed
        else:
            self._quota_consumed = delta

    @property
    def usage_percentage(self):
        if self._max_quota == 0:
            return 0
        return (self._quota_consumed / self._max_quota) * 100


def demo_overused_property():
    """演示过度使用@property的情况."""
    logging.info("反面示例: 过度使用@property")
    bucket = OverusedPropertyBucket(60)
    bucket.quota = 100  # 使用setter
    logging.info(f"配额: {bucket.quota}, 使用百分比: {bucket.usage_percentage:.2f}%")

    try:
        bucket.quota = -10  # 错误赋值
    except ValueError as e:
        logging.error(f"错误赋值导致异常: {e}")


# 主函数运行所有示例
def main():
    logging.info("开始运行原始Bucket示例")
    demo_original_bucket()

    logging.info("\n开始运行改进后的NewBucket示例")
    demo_improved_bucket()

    logging.info("\n开始运行过度使用@property的示例")
    demo_overused_property()


if __name__ == "__main__":
    main()
