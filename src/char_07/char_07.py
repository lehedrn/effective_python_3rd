"""
电商订单分析系统

该脚本模拟一个电商平台的订单处理模块，演示了多个 Effective Python 面向对象相关条目的实际应用。
包含订单生成、多态处理、函数式单分派统计、工厂构造、Mix-in 组合、不可变类、自定义容器等功能。

所体现的条目：
Item 48 - 接受函数而非类作为简单接口
Item 49 - 面向对象多态优于 isinstance 判断
Item 50 - 使用 singledispatch 替代面向对象多态
Item 51 - 使用 dataclass 定义轻量类
Item 52 - 使用 @classmethod 构造对象
Item 53 - 使用 super 初始化父类
Item 54 - 使用 Mix-in 组合功能
Item 55 - 优先使用公共属性
Item 56 - 使用 dataclass 创建不可变对象
Item 57 - 继承 collections.abc 定义自定义容器
"""

import logging
import random
from collections.abc import MutableSequence
from dataclasses import dataclass
from datetime import datetime
from functools import singledispatch
from typing import List, Dict

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ==================== 数据构造区 ====================

# Item 56: Prefer dataclasses for Creating Immutable Objects
@dataclass(frozen=True)
class OrderMetadata:
    """
    不可变订单元数据类（ID、时间戳）
    """
    order_id: str
    timestamp: datetime


# Item 54: Consider Composing Functionality with Mix-in Classes
class DiscountMixin:
    """
    折扣计算 Mix-in，提供默认折扣函数
    """
    def apply_discount(self) -> float:
        return 1.0  # 默认无折扣


class TimestampMixin:
    """
    时间戳 Mix-in，记录订单创建时间
    """
    def __post_init__(self):
        object.__setattr__(self, 'created_at', datetime.now())


# Item 51: Prefer dataclasses for Defining Lightweight Classes
# Item 55: Prefer Public Attributes over Private Ones
@dataclass
class OrderBase:
    """
    所有订单的基类，使用 dataclass 简化定义
    公共字段便于访问
    """
    order_id: str
    customer_id: str
    amount: float
    status: str = "pending"


# Item 48: Accept Functions Instead of Classes for Simple Interfaces
def calculate_discount(order_type: str) -> float:
    """
    简单折扣函数接口，替代使用类定义
    """
    discounts = {
        "vip": 0.9,
        "promo": 0.8,
        "regular": 1.0
    }
    return discounts.get(order_type, 1.0)


# Item 49: Prefer Object-Oriented Polymorphism over Functions with isinstance Checks
@dataclass
class RegularOrder(OrderBase, DiscountMixin):
    """
    普通订单，继承 Mix-in 提供折扣功能
    """
    def apply_discount(self) -> float:
        return 1.0


@dataclass
class VIPOrder(OrderBase, DiscountMixin):
    """
    会员订单，覆盖 Mix-in 方法实现定制折扣
    """
    def apply_discount(self) -> float:
        return 0.9


@dataclass
class PromoOrder(OrderBase, DiscountMixin):
    """
    促销订单，同样覆盖 Mix-in 方法
    """
    def apply_discount(self) -> float:
        return 0.8


# Item 52: Use @classmethod Polymorphism to Construct Objects Generically
class OrderFactory:
    """
    通用订单工厂，使用类方法多态构建不同类型的订单
    """
    @classmethod
    def create_order(cls, order_type: str, order_id: str, customer_id: str, amount: float):
        if order_type == "regular":
            return RegularOrder(order_id=order_id, customer_id=customer_id, amount=amount)
        elif order_type == "vip":
            return VIPOrder(order_id=order_id, customer_id=customer_id, amount=amount)
        elif order_type == "promo":
            return PromoOrder(order_id=order_id, customer_id=customer_id, amount=amount)
        else:
            raise ValueError(f"Unsupported order type: {order_type}")


# Item 50: Consider functools.singledispatch for Functional-Style Programming
# Item 57: Inherit from collections.abc Classes for Custom Container Types
# 使用 singledispatch 基于单个订单类型分派
@singledispatch
def process_order(order: OrderBase):
    """默认订单处理函数，抛出异常"""
    raise NotImplementedError(f"不支持的订单类型: {type(order)}")

@process_order.register(RegularOrder)
def _(order: RegularOrder):
    amount = order.amount * order.apply_discount()
    return {"type": "regular", "amount": amount}

@process_order.register(VIPOrder)
def _(order: VIPOrder):
    amount = order.amount * order.apply_discount()
    return {"type": "vip", "amount": amount}

@process_order.register(PromoOrder)
def _(order: PromoOrder):
    amount = order.amount * order.apply_discount()
    return {"type": "promo", "amount": amount}

def analyze_orders(orders: List[OrderBase]) -> Dict[str, float]:
    """分析订单列表，调用 process_order 处理每个订单"""
    if not orders:
        return {"type": "unknown", "total": 0.0, "count": 0, "avg": 0.0}

    # 确保列表中的订单类型一致
    order_type = process_order(orders[0])["type"]
    total = 0.0
    count = 0

    for order in orders:
        result = process_order(order)
        if result["type"] != order_type:
            raise ValueError(f"订单列表中包含多种类型: 期望 {order_type}, 实际 {result['type']}")
        total += result["amount"]
        count += 1

    avg = total / count if count > 0 else 0
    logger.info(f"[{order_type.capitalize()}] 总金额: {total:.2f}, 订单数: {count}, 平均金额: {avg:.2f}")
    return {"type": order_type, "total": total, "count": count, "avg": avg}

# Item 57: 自定义订单集合容器类，继承 MutableSequence
class OrderCollection(MutableSequence):
    """
    自定义订单集合类，封装基础列表操作
    """

    def __init__(self):
        self._items = []

    def insert(self, index: int, value: OrderBase) -> None:
        self._items.insert(index, value)

    def __delitem__(self, index: int) -> None:
        del self._items[index]

    def __setitem__(self, index: int, value: OrderBase) -> None:
        self._items[index] = value

    def __getitem__(self, index: int) -> OrderBase:
        return self._items[index]

    def __len__(self) -> int:
        return len(self._items)

    def add(self, order: OrderBase) -> None:
        self.append(order)

    def __repr__(self):
        return f"OrderCollection({len(self)} items)"


# ==================== 主流程控制区 ====================

def generate_orders(n: int = 100000) -> OrderCollection:
    """
    生成 n 条订单数据
    """
    logger.info(f"开始生成 {n} 条订单数据...")
    order_types = ["regular", "vip", "promo"]
    collection = OrderCollection()
    for i in range(n):
        order_id = f"ORD{i:06d}"
        customer_id = f"CUST{random.randint(1000, 9999)}"
        amount = round(random.uniform(50, 1000), 2)
        order_type = random.choice(order_types)
        order = OrderFactory.create_order(order_type, order_id, customer_id, amount)
        collection.add(order)
    logger.info(f"生成完成，共 {len(collection)} 条订单")
    return collection


def categorize_orders(collection: OrderCollection) -> Dict[str, List[OrderBase]]:
    """
    将订单按类型分类
    """
    categorized = {
        "regular": [],
        "vip": [],
        "promo": []
    }
    for order in collection:
        if isinstance(order, RegularOrder):
            categorized["regular"].append(order)
        elif isinstance(order, VIPOrder):
            categorized["vip"].append(order)
        elif isinstance(order, PromoOrder):
            categorized["promo"].append(order)
    return categorized


def main():
    orders = generate_orders(100000)
    categorized = categorize_orders(orders)

    logger.info("开始分析订单数据...")

    regular_report = analyze_orders(categorized["regular"])
    vip_report = analyze_orders(categorized["vip"])
    promo_report = analyze_orders(categorized["promo"])

    total_sales = regular_report["total"] + vip_report["total"] + promo_report["total"]
    total_count = regular_report["count"] + vip_report["count"] + promo_report["count"]
    avg_sales = total_sales / total_count if total_count > 0 else 0

    logger.info(f"【汇总报告】总销售额：{total_sales:.2f}，订单总数：{total_count}，平均销售额：{avg_sales:.2f}")


if __name__ == "__main__":
    main()
