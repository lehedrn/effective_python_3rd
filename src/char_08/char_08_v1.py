"""
## 脚本功能说明
这是一个模拟电商平台商品管理系统的脚本，展示了如何利用Python的高级特性实现一个灵活、可扩展的商品信息管理系统。
系统涵盖了从商品定义、验证、序列化到动态扩展的完整生命周期。

## 条目应用位置详解

### Item 58: Use Plain Attributes Instead of Setter and Getter Methods
- **位置**: `Product` 类中的 `product_id`, `name`, `_created_at` 属性
- **解释**: 使用直接的属性访问而非getter/setter方法，保持代码简洁易读。对于简单的属性不需要复杂的封装。

### Item 59: Consider @property Instead of Refactoring Attributes
- **位置**: `ValidatedProduct` 类的 `price` 和 `stock` 属性，以及 `created_at`
- **解释**: 使用@property在不改变接口的情况下添加验证逻辑和特殊行为，实现了平滑的属性升级。

### Item 60: Use Descriptors for Reusable @property Methods
- **位置**: `DiscountedProduct.PercentageDescriptor` 类
- **解释**: 定义了一个可重用的描述符来处理所有百分比类型的属性（如折扣率和税率），避免重复代码。

### Item 61: Use __getattr__, __getattribute__, and __setattr__ for Lazy Attributes
- **位置**: `ProductSerializer.__getattr__` 方法
- **解释**: 实现了延迟加载的序列化方法，根据需要动态生成不同的序列化格式。

### Item 62: Validate Subclasses with init_subclass
- **位置**: `ValidatedProduct.__init_subclass__` 方法
- **解释**: 在子类定义时自动验证规则，确保价格不能为负数等业务规则。

### Item 63: Register Class Existence with init_subclass
- **位置**: `ProductRegistry.__init_subclass__` 方法
- **解释**: 自动注册所有商品类型，方便后续查找和实例化。

### Item 64: Annotate Class Attributes with set_name
- **位置**: `PercentageDescriptor.__set_name__` 方法
- **解释**: 使用__set_name__自动注解属性名称，使描述符能了解其在包含类中的位置。

### Item 65: Consider Class Body Definition Order to Establish Relationships Between Attributes
- **位置**: 多处体现，特别是在商品类的定义中
- **解释**: 通过合理的属性定义顺序建立属性间的关系，比如先定义基础属性再定义派生属性。

### Item 66: Prefer Class Decorators over Metaclasses for Composable Class Extensions
- **位置**: `ProductDecorator` 类和 `@add_features` 装饰器
- **解释**: 使用类装饰器实现功能扩展，相比元类更加清晰和模块化。
"""

import json
import logging
import random
from datetime import datetime
from typing import Dict, List, Optional, Type

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Product:
    """
    电商商品基类，展示Item 58: Use Plain Attributes Instead of Setter and Getter Methods

    使用普通属性而不是setter/getter方法，保持代码简洁直观。
    这样可以更自然地进行属性访问和修改，提高代码可读性。
    """
    def __init__(self, product_id: str, name: str, price: float):
        self.product_id = product_id  # Item 58: 直接使用普通属性
        self.name = name              # Item 58: 避免使用getter/setter
        self.price = price            # Item 58: 简化属性访问

        # 创建时间是只读属性，使用@property实现
        self._created_at = datetime.now()

    @property
    def created_at(self):
        """Item 59: Consider @property Instead of Refactoring Attributes"""
        return self._created_at.strftime("%Y-%m-%d %H:%M:%S")

    def __repr__(self):
        return f"Product({self.product_id}, {self.name}, {self.price})"

class ValidatedProduct(Product):
    """
    带验证的商品类，展示：
    - Item 62: Validate Subclasses with init_subclass
    - Item 59: 使用@property实现属性验证
    """

    def __init_subclass__(cls, **kwargs):
        """Item 62: 在子类定义时自动验证"""
        super().__init_subclass__(**kwargs)
        if not hasattr(cls, 'validation_rules'):
            raise TypeError("Missing validation_rules attribute")

        logger.info(f"Validating subclass {cls.__name__}")
        if 'price' in cls.validation_rules and cls.validation_rules['price'].get('min', 0) < 0:
            raise ValueError("Price cannot be negative")

    validation_rules = {
        'price': {'min': 0.01, 'max': 100000},
        'stock': {'min': 0, 'max': 10000}
    }

    def __init__(self, product_id: str, name: str, price: float, stock: int = 0):
        super().__init__(product_id, name, price)
        self.stock = stock  # 将通过@property进行验证

    @property
    def price(self):
        """Item 59: 添加特殊行为到属性访问"""
        logger.debug("Accessing price property")
        return self._price

    @price.setter
    def price(self, value: float):
        """Item 59: 实现价格验证逻辑"""
        min_price = self.validation_rules['price']['min']
        max_price = self.validation_rules['price']['max']

        if not (min_price <= value <= max_price):
            raise ValueError(f"Price must be between {min_price} and {max_price}")
        self._price = value

    @property
    def stock(self):
        """Item 59: 添加延迟计算属性"""
        return self._stock

    @stock.setter
    def stock(self, value: int):
        """Item 59: 实现行号验证"""
        rules = self.validation_rules.get('stock', {})
        min_stock = rules.get('min', 0)
        max_stock = rules.get('max', 10000)

        if not (min_stock <= value <= max_stock):
            raise ValueError(f"Stock must be between {min_stock} and {max_stock}")
        self._stock = value

    @property
    def is_in_stock(self) -> bool:
        """Item 61: 使用__getattr__实现延迟属性"""
        return self.stock > 0

class DiscountedProduct(ValidatedProduct):
    """
    折扣商品类，展示：
    - Item 60: Use Descriptors for Reusable @property Methods
    - Item 64: Annotate Class Attributes with set_name
    """

    class PercentageDescriptor:
        """
        百分比描述符，用于折扣率和税率等属性
        Item 60: 可复用的@property方法
        Item 64: 使用__set_name__注解类属性
        """

        def __init__(self, default=0.0):
            self.default = default

        def __set_name__(self, owner, name):
            """Item 64: 自动注解属性名称"""
            self.public_name = name
            self.private_name = '_' + name

        def __get__(self, instance, owner):
            return getattr(instance, self.private_name, self.default)

        def __set__(self, instance, value):
            if not (0 <= value <= 1):
                raise ValueError(f"{self.public_name} must be between 0 and 1")
            setattr(instance, self.private_name, value)

    discount_rate = PercentageDescriptor()  # Item 60 & 64: 可复用的百分比属性
    tax_rate = PercentageDescriptor(0.07)  # Item 60 & 64: 带默认值的描述符

    def __init__(self, product_id: str, name: str, price: float,
                 stock: int = 0, discount_rate: float = 0.0, tax_rate: float = 0.07):
        super().__init__(product_id, name, price, stock)
        self.discount_rate = discount_rate  # 使用PercentageDescriptor
        self.tax_rate = tax_rate            # 使用PercentageDescriptor

    @property
    def final_price(self):
        """计算最终价格（考虑折扣和税）"""
        discounted = self.price * (1 - self.discount_rate)
        taxed = discounted * (1 + self.tax_rate)
        return round(taxed, 2)

class ProductRegistry:
    """
    商品注册器，展示 Item 63: Register Class Existence with init_subclass
    """

    _registry: Dict[str, Type[Product]] = {}

    def __init_subclass__(cls, **kwargs):
        """Item 63: 自动注册所有子类"""
        super().__init_subclass__(**kwargs)
        if cls.__name__ != "BaseProduct":
            ProductRegistry._registry[cls.__name__] = cls
            logger.info(f"Registered product type: {cls.__name__}")

    @classmethod
    def get_product_class(cls, class_name: str) -> Optional[Type[Product]]:
        """获取已注册的商品类"""
        return cls._registry.get(class_name)

class BaseProduct(ProductRegistry):
    """
    所有商品的基础类，用于演示类注册功能
    """
    pass

class PhysicalProduct(BaseProduct, ValidatedProduct):
    """
    实体商品类，展示多继承组合
    """

    def __init__(self, product_id: str, name: str, price: float,
                 stock: int = 0, weight: float = 0.0):
        ValidatedProduct.__init__(self, product_id, name, price, stock)
        self.weight = weight  # 实体商品特有的重量属性

class DigitalProduct(BaseProduct, ValidatedProduct):
    """
    数字商品类，展示多继承组合
    """

    def __init__(self, product_id: str, name: str, price: float,
                 download_link: str = ""):
        ValidatedProduct.__init__(self, product_id, name, price)
        self.download_link = download_link  # 数字商品特有的下载链接

class ProductSerializer:
    """
    商品序列化器，展示：
    - Item 61: Use getattr, getattribute, and setattr for Lazy Attributes
    - Item 59: 使用@property实现序列化逻辑
    """

    def __init__(self, product: Product):
        self.product = product

    def __getattr__(self, name: str):
        """Item 61: 实现延迟属性访问"""
        if name.startswith('serialize_'):
            format_type = name[len('serialize_'):]
            return lambda: self._serialize(format_type)

        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

    def _serialize(self, format_type: str) -> str:
        """通用序列化方法"""
        data = {
            'class': type(self.product).__name__,
            'product_id': self.product.product_id,
            'name': self.product.name,
            'price': self.product.price,
            'created_at': self.product.created_at
        }

        if hasattr(self.product, 'stock'):
            data['stock'] = self.product.stock

        if isinstance(self.product, DiscountedProduct):
            data['discount_rate'] = self.product.discount_rate
            data['tax_rate'] = self.product.tax_rate
            data['final_price'] = self.product.final_price

        if hasattr(self.product, 'weight'):
            data['weight'] = self.product.weight

        if hasattr(self.product, 'download_link'):
            data['download_link'] = self.product.download_link

        if format_type == 'json':
            return json.dumps(data, indent=2)

        raise ValueError(f"Unsupported format: {format_type}")

class ProductDecorator:
    """
    商品装饰器工厂，展示 Item 66: Prefer Class Decorators over Metaclasses
    """

    @staticmethod
    def add_features(**features):
        """Item 66: 使用类装饰器实现功能扩展"""
        def decorator(cls):
            for key, value in features.items():
                setattr(cls, key, value)
            return cls
        return decorator

@ProductDecorator.add_features(supports_return=True, warranty_months=12)
class ExtendedPhysicalProduct(PhysicalProduct):
    """
    扩展的实体商品类，展示类装饰器的功能
    """
    pass

def generate_mock_products(count: int = 100000) -> List[Product]:
    """生成模拟商品数据，展示各种商品类型的创建"""
    products = []

    product_names = [
        "Wireless Headphones", "Smartphone", "Laptop", "Tablet",
        "Smart Watch", "Gaming Console", "Digital Camera"
    ]

    for i in range(count):
        product_id = f"PROD-{i+1:06d}"
        name = random.choice(product_names)
        base_price = random.uniform(10, 1000)

        if i % 3 == 0:
            # 创建折扣商品
            discount_rate = random.uniform(0, 0.5)
            product = DiscountedProduct(
                product_id=product_id,
                name=name,
                price=base_price,
                stock=random.randint(0, 100),
                discount_rate=discount_rate
            )
        elif i % 3 == 1:
            # 创建实体商品
            product = PhysicalProduct(
                product_id=product_id,
                name=name,
                price=base_price,
                stock=random.randint(0, 100),
                weight=round(random.uniform(0.1, 10), 2)
            )
        else:
            # 创建数字商品
            product = DigitalProduct(
                product_id=product_id,
                name=name,
                price=base_price,
                download_link=f"https://example.com/downloads/{product_id}"
            )

        products.append(product)

    logger.info(f"Generated {len(products)} mock products")
    return products

def analyze_products(products: List[Product]):
    """分析商品数据，展示属性访问和序列化"""
    registry_stats = {}
    total_price = 0
    low_stock_count = 0

    for product in products:
        # 使用普通的属性访问
        total_price += product.price

        # 使用@property属性
        product_type = type(product).__name__
        registry_stats[product_type] = registry_stats.get(product_type, 0) + 1

        if hasattr(product, 'stock'):
            if product.stock < 10:
                low_stock_count += 1

        # 使用序列化器
        serializer = ProductSerializer(product)
        json_data = serializer.serialize_json()

        # 模拟JSON处理
        assert '"price"' in json_data
        if 'final_price' in json_data:
            assert '"discount_rate"' in json_data

    avg_price = total_price / len(products)
    logger.info(f"Average product price: ${avg_price:.2f}")
    logger.info(f"Low stock items count: {low_stock_count}")
    logger.info(f"Product type distribution: {registry_stats}")

def main():
    """主流程：展示所有Effective Python第8章的技术"""
    try:
        # 生成模拟数据（Item 58, 59, 60, 61）
        products = generate_mock_products(1000000)

        # 分析产品数据（Item 62, 63, 64, 65, 66）
        analyze_products(products)

        # 示例商品输出
        example_product = products[0]
        logger.info(f"Example product: {example_product}")

        serializer = ProductSerializer(example_product)
        logger.debug(f"Serialized product:\n{serializer.serialize_json()}")

        if isinstance(example_product, DiscountedProduct):
            logger.info(f"Discount rate: {example_product.discount_rate*100}%")
            logger.info(f"Final price: ${example_product.final_price}")

        if hasattr(example_product, 'supports_return'):
            logger.info(f"Supports return: {example_product.supports_return}")

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()
