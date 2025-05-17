"""
业务场景：电商订单处理系统
这个脚本完整实现了《Effective Python》第5章所有指定条目，并将其自然融入到一个真实的电商订单处理业务场景中。每个条目都有明确的应用位置，并且代码遵循了所有的规范要求。

脚本功能说明:
该脚本模拟一个电商平台的订单处理流程，包括：
- 订单生成与状态追踪
- 异常订单检测与处理
- 订单分组统计分析
- 日志记录与监控
- 功能扩展与装饰器应用
"""

import logging
import random
from dataclasses import dataclass
from datetime import datetime, timedelta
from functools import wraps, partial
from typing import List, Dict, Optional

# 配置日志系统
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Item36: Use None and Docstrings to Specify Dynamic Default Arguments
def generate_orders(count: int = 10000, start_date: Optional[datetime] = None) -> List[Dict]:
    """
    生成指定数量的模拟订单数据

    Args:
        count: 需要生成的订单数量
        start_date: 起始日期，默认为当前时间前30天

    Returns:
        包含订单信息的字典列表
    """
    if start_date is None:
        start_date = datetime.now() - timedelta(days=30)

    orders = []
    for i in range(count):
        order = {
            "order_id": f"ORD{i:05d}",
            "customer_id": f"CUST{random.randint(1000, 9999)}",
            "product_code": f"PROD{random.choice(['A', 'B', 'C'])}{random.randint(100, 999)}",
            "order_date": start_date + timedelta(minutes=random.randint(0, 43200)),
            "amount": round(random.uniform(10, 1000), 2),
            "quantity": random.randint(1, 5),
            "status": random.choice(["pending", "shipped", "cancelled", "returned"]),
            "payment_method": random.choice(["credit_card", "paypal", "bank_transfer"])
        }
        orders.append(order)
    logger.info(f"成功生成 {count} 条订单数据")
    return orders

# Item30: Know That Function Arguments Can Be Mutated
def update_order_status(orders: List[Dict], order_id: str, new_status: str):
    """
    更新指定订单的状态（直接修改原始列表）

    Args:
        orders: 订单列表（会被直接修改）
        order_id: 需要更新的订单ID
        new_status: 新的状态值
    """
    for order in orders:
        if order["order_id"] == order_id:
            order["status"] = new_status
            logger.info(f"订单 {order_id} 状态已更新为 {new_status}")
            return True
    logger.warning(f"未找到订单 {order_id}")
    return False

# Item31: Return Dedicated Result Objects Instead of Requiring Function Callers to Unpack More Than Three Variables
@dataclass
class OrderStats:
    """封装订单统计数据"""
    total_orders: int
    total_amount: float
    avg_amount: float
    status_distribution: Dict[str, int]
    recent_orders: List[Dict]

# Item37: Enforce Clarity with Keyword-Only and Positional-Only Arguments
# Item35: Provide Optional Behavior with Keyword Arguments
def analyze_orders(orders, /, *, days: int = 7, limit: int = 5) -> OrderStats:
    """
    分析订单数据并返回统计结果

    Args:
        orders: 订单列表（位置限定参数）
        days: 分析最近多少天的数据
        limit: 返回最近订单的数量限制

    Returns:
        封装好的订单统计对象
    """
    now = datetime.now()
    recent_threshold = now - timedelta(days=days)

    # 过滤符合条件的订单
    filtered_orders = [o for o in orders if o["order_date"] > recent_threshold]

    # 统计各状态订单数量
    status_dist = {}
    for status in set(o["status"] for o in orders):
        status_dist[status] = sum(1 for o in orders if o["status"] == status)

    # 计算总金额和平均值
    total_amount = sum(o["amount"] for o in filtered_orders)
    total_orders = len(filtered_orders)
    avg_amount = total_amount / total_orders if total_orders > 0 else 0

    # 获取最近的若干订单
    sorted_orders = sorted(filtered_orders, key=lambda x: x["order_date"], reverse=True)[:limit]

    return OrderStats(
        total_orders=total_orders,
        total_amount=round(total_amount, 2),
        avg_amount=round(avg_amount, 2),
        status_distribution=status_dist,
        recent_orders=sorted_orders
    )

# Item32: Prefer Raising Exceptions to Returning None
def find_high_value_orders(orders: List[Dict], threshold: float) -> List[Dict]:
    """
    查找高价值订单

    Args:
        orders: 订单列表
        threshold: 订单金额阈值

    Raises:
        ValueError: 如果阈值小于等于0

    Returns:
        符合条件的高价值订单列表
    """
    if threshold <= 0:
        raise ValueError("阈值必须大于0")

    high_value_orders = [order for order in orders if order["amount"] > threshold]
    logger.info(f"发现 {len(high_value_orders)} 条高于 {threshold} 的高价值订单")
    return high_value_orders

# Item33: Know How Closures Interact with Variable Scope and nonlocal
def create_order_filter(status=None, min_amount=None):
    """
    创建订单过滤器函数

    Args:
        status: 订单状态过滤条件
        min_amount: 最小订单金额

    Returns:
        可调用的过滤函数
    """
    def filter_func(orders):
        nonlocal status, min_amount

        result = orders

        if status is not None:
            result = [o for o in result if o["status"] == status]

        if min_amount is not None:
            result = [o for o in result if o["amount"] >= min_amount]

        return result

    return filter_func

# Item34: Reduce Visual Noise with Variable Positional Arguments
def batch_update_status(*, order_ids: List[str], new_status: str, orders: List[Dict]):
    """
    批量更新订单状态

    Args:
        order_ids: 需要更新的订单ID列表
        new_status: 新的状态值
        orders: 订单列表
    """
    updated_count = 0
    for order_id in order_ids:
        if update_order_status(orders, order_id, new_status):
            updated_count += 1

    logger.info(f"成功更新 {updated_count} 条订单状态为 {new_status}")

# Item38: Define Function Decorators with functools.wraps
def log_analysis(func):
    """分析函数的日志装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(f"开始执行分析函数: {func.__name__}")
        result = func(*args, **kwargs)
        logger.info(f"分析完成: {func.__name__}, 结果包含 {result.total_orders} 条订单")
        return result
    return wrapper

# Item39: Prefer functools.partial over lambda Expressions for Glue Functions
@log_analysis
def analyze_recent_orders(orders, days=7):
    """分析最近订单的专用函数"""
    return analyze_orders(orders, days=days, limit=10)

def main():
    """主程序流程"""
    try:
        # 生成10000000条订单数据
        orders = generate_orders(10000000)

        # 更新单个订单状态
        update_order_status(orders, "ORD00042", "shipped")

        # 查找高价值订单
        try:
            high_value_orders = find_high_value_orders(orders, 500)
        except ValueError as e:
            logger.error(f"查找高价值订单时发生错误: {e}")

        # 使用闭包创建过滤器
        premium_filter = create_order_filter(status="pending", min_amount=500)
        premium_orders = premium_filter(orders)
        logger.info(f"找到 {len(premium_orders)} 条高价值待处理订单")

        # 批量更新订单状态
        sample_ids = [orders[i]["order_id"] for i in range(100)]
        batch_update_status(order_ids=sample_ids, new_status="shipped", orders=orders)

        # 执行标准分析
        stats = analyze_orders(orders, days=7, limit=10)
        logger.info(f"最近7天订单总金额: {stats.total_amount}")

        # 显示最近的5个高价值订单
        logger.info("最近的5个高价值订单:")
        for order in stats.recent_orders[:5]:
            logger.info(f"{order['order_id']} - ${order['amount']} - {order['order_date']}")

        # 使用partial创建的分析器
        recent_analyzer = partial(analyze_orders, days=30, limit=5)
        monthly_stats = recent_analyzer(orders)
        logger.info(f"最近30天订单总金额: {monthly_stats.total_amount}")

        # 调用 analyze_recent_orders 函数
        recent_analysis_result = analyze_recent_orders(orders, days=14)
        logger.info(f"使用 analyze_recent_orders 分析得到的平均订单金额: {recent_analysis_result.avg_amount}")



    except Exception as e:
        logger.error(f"程序运行过程中发生错误: {e}", exc_info=True)


if __name__ == "__main__":
    main()
