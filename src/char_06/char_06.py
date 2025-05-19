"""
脚本功能：
该脚本模拟一个“智能物流仓储监控系统”，用于处理和分析仓库中货物的出入库记录，展示《Effective Python》第6章关于推导式与生成器的核心实践。

所选业务场景：
- 生成10,000条模拟的货物入库日志数据（含时间戳、货品ID、数量、状态等字段）
- 使用推导式进行高效的数据筛选与转换
- 使用生成器处理大型数据集以减少内存占用
- 使用类管理状态变化，替代 generator.throw 方法

体现的条目编号及位置：

Item 40: 使用列表推导式代替 map 和 filter （见 load_filtered_items 函数）
Item 41: 避免在推导式中使用超过两个控制子表达式（见 process_large_data_with_generator_expression 函数）
Item 42: 使用赋值表达式减少推导式中的重复（见 analyze_stock_status 函数）
Item 43: 使用生成器而非返回列表（见 generate_inventory_events 函数）
Item 44: 对大型列表推导式使用生成器表达式（见 process_large_data_with_generator_expression 函数）
Item 45: 使用 yield from 组合多个生成器（见 combined_event_streams 函数）
Item 46: 将迭代器作为参数传入生成器，而不是调用 send 方法（见 stream_inventory_changes 函数）
Item 47: 使用类管理迭代状态转换，而非 throw 方法（见 InventoryMonitor 类）

"""

import logging
import random
import string
from datetime import datetime, timedelta
from typing import Generator, Dict, List, Tuple, Iterator

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# ==================== 数据构造区 ====================
def generate_inventory_logs(num_records: int) -> List[Dict]:
    """
    生成指定数量的模拟库存记录数据
    """

    def random_id(length=8):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

    statuses = ['INBOUND', 'OUTBOUND', 'STOCKED', 'DAMAGED']
    start_time = datetime.now() - timedelta(days=30)

    logs = [
        {
            "timestamp": start_time + timedelta(minutes=i * 5),
            "item_id": random_id(6),
            "quantity": random.randint(1, 200),
            "status": random.choice(statuses),
        }
        for i in range(num_records)
    ]
    logger.info(f"成功生成 {num_records} 条库存记录")
    return logs


# ==================== 函数定义区 ====================
def load_filtered_items(logs: List[Dict]) -> List[Dict]:
    """
    Item 40: 使用列表推导式代替 map 和 filter
    筛选出最近7天内入库且数量大于50的记录
    """
    seven_days_ago = datetime.now() - timedelta(days=7)
    filtered = [
        log for log in logs
        if log["status"] == "INBOUND"
        and log["timestamp"] > seven_days_ago
        and log["quantity"] > 50
    ]
    logger.info(f"筛选出符合条件的记录共 {len(filtered)} 条")
    return filtered


def analyze_stock_status(logs: List[Dict]) -> Dict[str, Dict[str, int]]:
    """
    Item 42: 使用赋值表达式减少推导式中的重复
    分析每种物品当前库存状态（净存量），包括超出阈值的具体数量
    """
    stock = {}
    for log in logs:
        item_id = log['item_id']
        quantity = log['quantity'] if log['status'] == 'INBOUND' else -log['quantity']
        stock[item_id] = stock.get(item_id, 0) + quantity

    # 使用 walrus operator 减少重复，并展示其价值
    result = {
        category: {
            k: level - thresholds['threshold']  # 多次使用 level
            for k, v in stock.items()
            if (level := v) >= thresholds['threshold']
        }
        for category, thresholds in {
            'high': {'threshold': 500},
            'medium': {'threshold': 200},
            'low': {'threshold': 0}
        }.items()
    }

    logger.info("完成库存状态分类分析")
    return result


def generate_inventory_events(logs: List[Dict]) -> Generator[Dict, None, None]:
    """
    Item 43: 使用生成器替代返回列表
    逐条生成有效的库存变动事件
    """
    logger.warning("开始按需生成库存变动事件")
    for log in logs:
        if log['status'] in ['INBOUND', 'OUTBOUND']:
            yield log


def process_large_data_with_generator_expression(logs: List[Dict]) -> Iterator[int]:
    """
    Item 41 & Item 44: 避免复杂推导式 + 使用生成器表达式处理大数据
    处理大量数据时避免嵌套过多条件，并使用生成器节省内存
    """
    logger.info("使用生成器表达式逐步处理大规模数据")
    return (
        log['quantity']
        for log in logs
        if log['status'] == 'OUTBOUND'
        if log['quantity'] > 10
    )


def event_stream_a() -> Generator[Dict, None, None]:
    """模拟第一个事件流：高价值货物出入库"""
    yield {"item": "A", "type": "INBOUND", "value": 1000}
    yield {"item": "B", "type": "OUTBOUND", "value": 500}


def event_stream_b() -> Generator[Dict, None, None]:
    """模拟第二个事件流：普通货物库存调整"""
    yield {"item": "C", "type": "STOCK_ADJUSTMENT", "value": 200}
    yield {"item": "D", "type": "STOCK_ADJUSTMENT", "value": 150}


def combined_event_streams() -> Generator[Dict, None, None]:
    """
    Item 45: 使用 yield from 组合多个生成器
    合并多个独立事件流为统一输出
    """
    logger.info("使用 yield from 合并多个事件流")
    yield from event_stream_a()
    yield from event_stream_b()


def stream_inventory_changes(data_source: Iterator[Dict]) -> Generator[Tuple, None, None]:
    """
    Item 46: 将迭代器作为参数传入生成器，而非使用 send 方法
    实时流式处理库存变化
    """
    logger.warning("将数据源作为参数传入生成器进行流式处理")
    for record in data_source:
        if record['quantity'] > 100:
            yield (record['item_id'], 'High Volume', record['quantity'])
        elif record['quantity'] > 50:
            yield (record['item_id'], 'Medium Volume', record['quantity'])
        else:
            yield (record['item_id'], 'Low Volume', record['quantity'])


class InventoryMonitor:
    """
    Item 47: 使用类管理迭代状态转换，而非 throw 方法
    模拟库存监控系统，根据输入信号切换监控模式
    """
    def __init__(self, inventory: Dict[str, int]):
        self.inventory = inventory
        self.mode = 'normal'

    def switch_mode(self, new_mode: str):
        logger.info(f"库存监控模式从 [{self.mode}] 切换至 [{new_mode}]")
        self.mode = new_mode

    def monitor(self) -> Generator[Tuple[str, str], None, None]:
        logger.info("使用类封装状态管理，启动库存实时监控")
        for item, quantity in self.inventory.items():
            if self.mode == 'normal':
                status = 'OK' if quantity > 50 else 'LOW'
            elif self.mode == 'strict':
                status = 'OK' if quantity > 100 else 'CRITICAL'
            else:
                status = 'UNKNOWN MODE'
            yield (item, status)


# ==================== 主流程控制区 ====================
def main():
    try:
        # 模拟数据生成
        logs = generate_inventory_logs(10000)

        # Item 40 & Item 42 应用
        filtered_items = load_filtered_items(logs)
        stock_analysis = analyze_stock_status(logs)

        # Item 43 & Item 44 应用
        inventory_events = list(generate_inventory_events(logs))[:10]
        large_data_gen = list(process_large_data_with_generator_expression(logs))[:10]

        # Item 45 应用
        merged_events = list(combined_event_streams())

        # Item 46 应用
        sample_data = iter(logs[:5])
        inventory_changes = list(stream_inventory_changes(sample_data))

        # Item 47 应用
        initial_stock = {'X': 120, 'Y': 70, 'Z': 30}
        monitor = InventoryMonitor(initial_stock).monitor()
        monitor_status = list(monitor)

        # 日志输出结果概览
        logger.info("===== 结果概览 =====")
        logger.info(f"筛选后的记录数: {len(filtered_items)}")
        logger.info(f"库存状态分类: {stock_analysis}")
        logger.info(f"生成的有效库存事件数: {len(inventory_events)}")
        logger.info(f"大型数据处理示例: {large_data_gen}")
        logger.info(f"合并事件流总数: {len(merged_events)}")
        logger.info(f"库存变化流示例: {inventory_changes}")
        logger.info(f"库存监控状态: {monitor_status}")

    except Exception as e:
        logger.error(f"主流程发生异常: {e}", exc_info=True)


if __name__ == "__main__":
    main()
