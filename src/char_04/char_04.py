"""
业务场景说明：
本脚本模拟一个电商平台的订单处理系统，用于统计商品类别下的热销品牌，并为后续推荐系统提供基础数据。
脚本中融合了以下条目：

- Item25: 谨慎依赖字典插入顺序 —— 使用 OrderedDict 确保按添加顺序返回热销品牌
- Item26: 优先使用 get 方法处理缺失键 —— 在读取品牌销量时避免 KeyError
- Item27: 优先使用 defaultdict 处理内部状态缺失项 —— 统计各品类下品牌销量
- Item28: 使用 __missing__ 构造键依赖的默认值 —— 模拟首次访问未知品类时自动初始化
- Item29: 使用类组合代替深层嵌套结构 —— 避免直接用 dict 嵌套 dict 存储品类/品牌关系

所有逻辑服务于实际业务需求，确保代码可维护性和健壮性。
"""

import logging
import random
from collections import defaultdict, OrderedDict
from dataclasses import dataclass
from typing import Dict, List

# 设置日志配置
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')


@dataclass
class BrandSale:
    """表示单个品牌的销售记录（Item29 类组合）"""
    brand: str
    quantity: int


class CategorySales:
    """
    表示某个商品品类的销售统计信息（Item28 键依赖默认值）
    当访问未出现过的品类时，自动初始化空的品牌销量字典
    """

    def __init__(self):
        self._brands = {}  # 内部品牌字典

    def __missing__(self, key):
        """当品类不存在时自动创建一个新的品牌字典（Item28）"""
        logging.info(f"检测到新品类 '{key}'，正在初始化品牌统计")
        self._brands[key] = defaultdict(int)  # 初始化该品类下的品牌销量
        return self._brands[key]

    def report_sale(self, category: str, brand: str, quantity: int):
        """上报某品牌在某品类的销售数量（Item26 使用 get 安全访问）"""
        self.__missing__(category)  # 确保品类存在
        self._brands[category][brand] += quantity

    def top_brands(self, category: str, top_n=5) -> List[BrandSale]:
        """获取某品类下销量前 N 的品牌（Item25 插入顺序保留）"""
        if category not in self._brands:
            return []

        brand_dict = self._brands[category]
        # 使用 OrderedDict 保证排序后仍保持插入顺序（Item25）
        ordered = OrderedDict(sorted(brand_dict.items(), key=lambda x: x[1], reverse=True))
        return [BrandSale(brand, quantity) for brand, quantity in list(ordered.items())[:top_n]]


def generate_sales_data(num_records=10000):
    """生成模拟销售数据（Item27 使用 defaultdict 初步统计）"""
    categories = ['手机', '电脑', '家电', '服饰', '图书']
    brands = {
        '手机': ['华为', '苹果', '小米', 'OPPO', 'vivo'],
        '电脑': ['联想', '戴尔', '惠普', '华硕', 'MacBook'],
        '家电': ['海尔', '美的', '格力', '松下', '索尼'],
        '服饰': ['李宁', '安踏', '耐克', '阿迪达斯', '优衣库'],
        '图书': ['人民邮电', '机械工业', '电子工业', '高等教育', '清华大学']
    }

    sales_data = []
    for _ in range(num_records):
        category = random.choice(categories)
        brand = random.choice(brands[category])
        quantity = random.randint(1, 10)
        sales_data.append((category, brand, quantity))

    logging.info(f"已生成 {num_records} 条销售记录")
    return sales_data


def process_sales_data(sales_data):
    """处理销售数据并统计各品类下品牌销量（Item27 使用 defaultdict）"""
    stats = defaultdict(lambda: defaultdict(int))  # 品类 -> 品牌 -> 数量（Item27）

    for category, brand, quantity in sales_data:
        stats[category][brand] += quantity

    logging.info("已完成初步销售数据统计")
    return stats


def build_category_sales(stats: Dict[str, Dict[str, int]]) -> CategorySales:
    """将统计数据封装进 CategorySales 类实例（Item29 类组合）"""
    cs = CategorySales()
    for category, brand_dict in stats.items():
        for brand, quantity in brand_dict.items():
            cs.report_sale(category, brand, quantity)
    logging.info("已构建 CategorySales 实例")
    return cs


def main():
    # 数据构造区
    sales_data = generate_sales_data(10000000)

    # 主流程控制区
    stats = process_sales_data(sales_data)
    category_sales = build_category_sales(stats)

    # 展示结果（Item25 OrderedDict 插入顺序保留）
    for category in ['手机', '电脑', '家电']:
        top_brands = category_sales.top_brands(category, top_n=3)
        logging.info(f"\n【{category}】热销品牌TOP3：")
        for idx, brand_sale in enumerate(top_brands, 1):
            logging.info(f"{idx}. {brand_sale.brand}: {brand_sale.quantity} 件")

    # 验证 Item28 是否体现
    try:
        category_sales.top_brands('美妆')  # 尝试访问不存在的品类
    except Exception as e:
        logging.warning(f"Item28 尚未体现，请检查品类缺失处理逻辑:{e}")


if __name__ == '__main__':
    main()

