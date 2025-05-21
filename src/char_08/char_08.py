"""
脚本功能：
    模拟物流订单系统，处理10万条订单数据。
    使用元类、描述符、@property、__init_subclass__等机制进行类结构设计和验证。

业务场景：
    物流公司需处理大量快递单据，包含：订单ID、收货城市、运输方式、重量、状态等字段。
    需求包括：
    - 订单验证（如重量 > 0）
    - 自动注册解析类用于不同客户模板
    - 支持延迟属性访问（如动态运费计算）
    - 统一接口定义字段顺序关系
    - 类装饰器实现订单分类扩展

所体现的 Effective Python 条目及位置说明：
- Item 58: 使用普通属性代替 Setter 和 Getter 方法（Order类）
- Item 59: 使用 @property 替代重构属性（weight）
- Item 60: 使用描述符复用 @property 方法（PositiveFloatDescriptor）
- Item 61: 使用 __getattr__ 和 __setattr__ 实现懒加载运费（LazyFreightMixin）
- Item 62: 使用 __init_subclass__ 验证子类（BaseOrder）
- Item 63: 使用 __init_subclass__ 注册类存在（OrderTypeRegistry）
- Item 64: 使用 __set_name__ 注解类属性（FieldDescriptor）
- Item 65: 利用类体定义顺序建立属性关系（DynamicOrder）
- Item 66: 优先使用类装饰器而非元类（apply_urgent_label）
"""

import logging
import random
import string
from datetime import datetime, timedelta
from functools import wraps

# 日志配置
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

# 数据模拟部分
CUSTOMERS = ['CustomerA', 'CustomerB', 'CustomerC']
CITIES = ['Beijing', 'Shanghai', 'Guangzhou', 'Chengdu', 'Xian', 'Hangzhou']
TRANSPORT_METHODS = ['Air', 'Truck', 'Railway', 'Sea']
ORDER_STATUSES = ['Pending', 'In Transit', 'Delivered', 'Failed']

def generate_mock_orders(n=100000):
    """生成10万条模拟订单数据"""
    orders = []
    for i in range(n):
        order_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        customer = random.choice(CUSTOMERS)
        destination = random.choice(CITIES)
        method = random.choice(TRANSPORT_METHODS)
        weight = round(random.uniform(0.5, 1000), 2)
        status = random.choice(ORDER_STATUSES)
        create_time = datetime.now() - timedelta(days=random.randint(0, 30))

        orders.append({
            "order_id": order_id,
            "customer": customer,
            "destination": destination,
            "method": method,
            "weight": weight,
            "status": status,
            "create_time": create_time
        })
    return orders

# Item 58: Use Plain Attributes Instead of Setter and Getter Methods
class Order:
    def __init__(self, order_id, destination, method, weight):
        self.order_id = order_id          # 普通属性直接赋值
        self.destination = destination
        self.method = method
        self.weight = weight              # 后续通过@property封装验证逻辑
        self.create_time = datetime.now()

    def __repr__(self):
        return f"Order(id={self.order_id}, dest={self.destination}, weight={self.weight})"

# Item 59: Consider @property Instead of Refactoring Attributes
# Item 60: Use Descriptors for Reusable @property Methods
class PositiveFloatDescriptor:
    """通用正浮点数验证描述符，可复用于其他字段"""
    def __init__(self, name):
        self.name = "_" + name

    def __get__(self, instance, owner):
        return getattr(instance, self.name)

    def __set__(self, instance, value):
        if not isinstance(value, (int, float)) or value <= 0:
            raise ValueError(f"{self.name[1:]} must be a positive number")
        setattr(instance, self.name, value)

class ValidatedOrder(Order):
    weight = PositiveFloatDescriptor("weight")  # 复用验证逻辑

    def __init__(self, order_id, destination, method, weight):
        super().__init__(order_id, destination, method, weight)

# Item 61: Use __getattr__, __getattribute__, and __setattr__ for Lazy Attributes
class LazyFreightMixin:
    """根据运输方式与重量计算运费，延迟加载"""
    FREIGHT_RATES = {"Air": 5.0, "Truck": 2.0, "Railway": 1.5, "Sea": 1.0}

    def __getattr__(self, item):
        if item == 'freight':
            rate = self.FREIGHT_RATES.get(self.method, 2.0)
            freight_value = self.weight * rate
            object.__setattr__(self, 'freight', freight_value)
            logging.info(f"[Lazy] Freight calculated for {self.order_id}: {freight_value}")
            return freight_value
        raise AttributeError(f"{item} not found")

# Item 62 & 63: Validate Subclasses and Register Class Existence with __init_subclass__
REGISTRY = {}

class BaseOrderMeta(type):
    def __new__(meta, name, bases, class_dict):
        cls = type.__new__(meta, name, bases, class_dict)
        if cls.__name__ != "BaseOrder":
            # 子类才参与注册
            REGISTRY[name] = cls
        return cls

class BaseOrder(metaclass=BaseOrderMeta):
    pass

class RegisteredOrder(BaseOrder):
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not hasattr(cls, "required_fields"):
            raise TypeError("Missing required_fields attribute")
        for field in cls.required_fields:
            if not hasattr(cls, field):
                raise ValueError(f"Missing required field: {field}")
        REGISTRY[cls.__name__] = cls

# Item 64: Annotate Class Attributes with __set_name__
class FieldDescriptor:
    def __init__(self):
        self.column_name = None
        self.internal_name = None

    def __set_name__(self, owner, column_name):
        self.column_name = column_name
        self.internal_name = "_" + column_name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return getattr(instance, self.internal_name, None)

    def __set__(self, instance, value):
        setattr(instance, self.internal_name, value)

# Item 65: Class Body Definition Order to Establish Relationships Between Attributes
class DynamicOrder:
    order_id = FieldDescriptor()
    destination = FieldDescriptor()
    method = FieldDescriptor()
    weight = FieldDescriptor()

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

# Item 66: Prefer Class Decorators over Metaclasses for Composable Class Extensions
def apply_urgent_label(cls):
    """类装饰器标记加急订单"""
    original_init = cls.__init__

    @wraps(cls.__init__)
    def new_init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        self.priority = 'Urgent'
        logging.warning(f"[Decorator] Marked {self.order_id} as urgent")

    cls.__init__ = new_init
    return cls

# 主流程控制区
if __name__ == "__main__":
    logging.info("Generating mock data...")
    mock_orders = generate_mock_orders(100000)
    logging.info(f"Generated {len(mock_orders)} mock orders")

    # 使用动态字段类创建实例
    order_data = mock_orders[0]
    dynamic_order = DynamicOrder(
        order_id=order_data['order_id'],
        destination=order_data['destination'],
        method=order_data['method'],
        weight=order_data['weight']
    )

    # 懒加载运费计算
    lazy_order = type('LazyOrder', (LazyFreightMixin, Order), {})(**{
        "order_id": "LAZY001",
        "destination": "Shanghai",
        "method": "Air",
        "weight": 10.0
    })

    print("Lazy freight:", lazy_order.freight)

    # 应用装饰器扩展类
    @apply_urgent_label
    class UrgentOrder(ValidatedOrder):
        required_fields = ["order_id", "destination"]

    urgent_order = UrgentOrder("URG001", "Chengdu", "Truck", 50.0)
    print("Priority:", urgent_order.priority)

    logging.info("Class registry contents:")
    for cls_name, cls in REGISTRY.items():
        logging.info(f"- {cls_name}")
