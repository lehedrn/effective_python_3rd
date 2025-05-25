"""
电商订单处理系统

该脚本模拟了一个电商平台的订单处理流程，包含以下核心功能：
- 使用key参数对订单进行多条件排序 (Item 100)
- 对比sort和sorted方法的应用 (Item 101)
- 在有序序列中使用bisect搜索 (Item 102)
- 使用deque实现生产者-消费者队列 (Item 103)
- 使用heapq实现优先队列 (Item 104)
- 使用datetime处理本地时钟 (Item 105)
- 使用decimal确保精确计算 (Item 106)
- 使用copyreg维护pickle序列化的可维护性 (Item 107)

所选业务场景：电商平台的订单处理系统
"""

import logging
import random
import string
from datetime import datetime, timedelta
from collections import deque
from heapq import heappush, heappop
from bisect import bisect_left
import pickle
import copyreg
from decimal import Decimal, getcontext, ROUND_HALF_UP
from functools import total_ordering

# 设置日志配置
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 设置Decimal精度
getcontext().rounding = ROUND_HALF_UP

@total_ordering
class Order:
    """订单类，表示一个电商订单"""

    def __init__(self, order_id, create_time, amount, priority, customer):
        self.order_id = order_id
        self.create_time = create_time  # UTC时间
        self.amount = amount  # 订单金额（使用Decimal）
        self.priority = priority  # 订单优先级（数字越小优先级越高）
        self.customer = customer  # 客户名称

    def __repr__(self):
        return f"Order({self.order_id}, {self.create_time}, {self.amount}, {self.priority}, {self.customer})"

    def __lt__(self, other):
        """根据优先级和创建时间排序"""
        if not isinstance(other, Order):
            return NotImplemented

        # 首先比较优先级
        if self.priority != other.priority:
            return self.priority < other.priority

        # 如果优先级相同，按创建时间排序
        return self.create_time < other.create_time


def generate_random_orders(num=100000):
    """生成指定数量的随机订单"""
    orders = []

    start_time = datetime(2023, 1, 1)
    end_time = datetime(2023, 12, 31)

    for i in range(num):
        # 随机生成订单ID
        order_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

        # 随机生成创建时间
        time_diff = (end_time - start_time).total_seconds()
        random_seconds = random.randint(0, int(time_diff))
        create_time = start_time + timedelta(seconds=random_seconds)

        # 随机生成订单金额（使用Decimal保证精度）
        amount = Decimal(str(round(random.uniform(10, 1000), 2)))

        # 随机生成优先级（1-5）
        priority = random.randint(1, 5)

        # 随机生成客户名
        customer = f"Customer_{random.randint(1000, 9999)}"

        # 创建订单对象
        orders.append(Order(order_id, create_time, amount, priority, customer))

    return orders


# 注册pickle序列化函数，维护序列化的可维护性 (Item 107)
def pickle_order(order):
    kwargs = {
        'order_id': order.order_id,
        'create_time': order.create_time,
        'amount': order.amount,
        'priority': order.priority,
        'customer': order.customer
    }
    return unpickle_order, (kwargs,)


def unpickle_order(kwargs):
    return Order(**kwargs)

copyreg.pickle(Order, pickle_order)

def process_orders(orders):
    """处理订单的主要流程"""
    logging.info("开始处理订单")

    # 使用key参数按复杂准则排序 (Item 100)
    # 按客户分组排序，然后按金额降序排列
    orders_by_customer = sorted(orders, key=lambda x: (x.customer, -x.amount))
    logging.info(f"按客户分组并按金额降序排序完成，共{len(orders_by_customer)}个订单")

    # 知道sort和sorted的区别 (Item 101)
    # 先使用sorted排序不影响原始数据
    sorted_by_amount = sorted(orders_by_customer, key=lambda x: x.amount, reverse=True)
    # 再使用sort就地排序，因为后续不再需要原始顺序
    sorted_by_amount.sort(key=lambda x: x.priority)
    logging.info(f"使用sort和sorted完成最终排序，前5个订单：{sorted_by_amount[:5]}")

    # 在有序序列中使用bisect搜索 (Item 102)
    # 假设我们要找出2023年6月1日之后的所有订单
    sorted_by_time = sorted(sorted_by_amount, key=lambda x: x.create_time)
    target_date = datetime(2023, 6, 1)

    # 使用bisect找到第一个符合条件的位置
    index = bisect_left([order.create_time for order in sorted_by_time], target_date)
    recent_orders = sorted_by_time[index:]
    logging.info(f"使用bisect找到{target_date}之后的订单{len(recent_orders)}个")

    # 使用deque实现生产者-消费者队列 (Item 103)
    # 创建两个队列：待处理和已完成
    to_process_queue = deque()
    processed_queue = deque()

    # 生产者：将最近的订单加入队列
    for order in recent_orders[:100]:  # 只处理前100个最近订单
        to_process_queue.append(order)

    # 消费者：处理订单
    while to_process_queue:
        order = to_process_queue.popleft()
        # 处理订单（这里只是简单标记为已处理）
        processed_queue.append(order)
    logging.info(f"通过deque处理了{len(processed_queue)}个订单")

    # 使用heapq实现优先队列 (Item 104)
    # 将剩余订单放入优先队列，按照优先级处理
    remaining_orders = recent_orders[100:]
    priority_queue = []

    for order in remaining_orders:
        heappush(priority_queue, order)

    # 处理高优先级订单
    high_priority_orders = []
    while priority_queue and len(high_priority_orders) < 50:
        order = heappop(priority_queue)
        high_priority_orders.append(order)

    logging.info(f"使用heapq处理了{len(high_priority_orders)}个高优先级订单，前5个：{high_priority_orders[:5]}")

    # 使用datetime处理本地时钟 (Item 105)
    # 将UTC时间转换为北京时间
    beijing_tz = timedelta(hours=8)
    local_orders = []

    for order in high_priority_orders:
        local_time = order.create_time + beijing_tz
        local_orders.append((order, local_time))

    logging.info(f"转换了{len(local_orders)}个订单的UTC时间为北京时间，前5个：{local_orders[:5]}")

    # 使用decimal确保精确计算 (Item 106)
    # 计算总销售额
    total_sales = Decimal('0')
    for order in processed_queue:
        total_sales += order.amount

    avg_sales = total_sales / len(processed_queue) if processed_queue else Decimal('0')

    logging.info(f"总销售额：{total_sales.quantize(Decimal('0.00'))}")
    logging.info(f"平均订单金额：{avg_sales.quantize(Decimal('0.00'))}")

    # 使用pickle序列化处理过的订单 (Item 107)
    serialized_data = pickle.dumps(list(processed_queue))
    deserialized_orders = pickle.loads(serialized_data)

    logging.info(f"使用copyreg维护pickle序列化，反序列化得到{len(deserialized_orders)}个订单")

    logging.info("订单处理完成")
    return deserialized_orders


def main():
    """主函数"""
    try:
        # 生成测试数据
        logging.info("开始生成测试数据...")
        orders = generate_random_orders(100000)
        logging.info(f"成功生成{len(orders)}个订单数据")

        # 处理订单
        processed_orders = process_orders(orders)

        # 输出统计信息
        logging.info(f"总共处理订单数: {len(processed_orders)}")

    except Exception as e:
        logging.error(f"处理过程中发生错误: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
