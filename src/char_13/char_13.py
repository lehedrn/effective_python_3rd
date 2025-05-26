"""
在线零售订单处理系统

功能：
    该脚本实现了一个在线零售订单处理系统，用于生成模拟订单数据、计算折扣后的订单总价、
    与支付网关交互、更新订单状态，并通过测试验证逻辑正确性、监控内存使用和支持交互式调试。

业务场景：
    系统模拟一个在线零售平台，处理包含订单ID、时间戳、商品列表、总价和状态的订单数据。
    系统需支持高并发订单处理、复杂依赖（如支付网关）、浮点数精度控制、内存监控和调试。

条目体现位置：
    - Item 108: 在 TestCase 子类中验证相关行为（OrderProcessorTestCase 和 OrderIntegrationTestCase）
    - Item 109: 优先集成测试（OrderIntegrationTestCase 验证端到端行为）
    - Item 110: 使用 setUp/tearDown/setUpModule/tearDownModule 隔离测试（OrderIntegrationTestCase）
    - Item 111: 使用 Mock 测试复杂依赖（mock 支付网关在 OrderProcessorTestCase）
    - Item 112: 封装依赖以便于模拟（PaymentGateway 类）
    - Item 113: 使用 assertAlmostEqual 控制浮点数精度（OrderProcessorTestCase.test_discount）
    - Item 114: 使用 pdb 交互式调试（OrderProcessor.process_order 的条件断点）
    - Item 115: 使用 tracemalloc 监控内存使用（run_order_processing 函数中的内存分析）

"""

import logging
import random
import tracemalloc
import uuid
from datetime import datetime, timedelta
from tempfile import TemporaryDirectory
from unittest import TestCase, main as unittest_main
from unittest.mock import Mock

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# ---------------- 数据构造区 ----------------

def generate_order_data(num_orders=100000):
    """
    生成模拟订单数据，包含订单ID、时间戳、商品列表、总价和状态。

    :param num_orders: 生成订单数量，默认为100000
    :return: 订单数据列表
    """
    orders = []
    for _ in range(num_orders):
        order = {
            "order_id": str(uuid.uuid4()),
            "timestamp": datetime.now() - timedelta(minutes=random.randint(1, 10080)),
            "items": [
                {"name": f"Product_{random.randint(1, 100)}", "price": round(random.uniform(10.0, 100.0), 2)}
                for _ in range(random.randint(1, 5))
            ],
            "status": "pending",
            "total_price": 0.0  # 初始总价，需后续计算
        }
        order["total_price"] = sum(item["price"] for item in order["items"])
        orders.append(order)
    logger.info(f"生成了 {num_orders} 条订单数据")
    return orders

# ---------------- 类与函数定义区 ----------------

class PaymentGateway:
    """
    支付网关类，封装与外部支付系统的交互逻辑。
    体现 Item 112：通过类封装复杂依赖，便于后续模拟和测试。
    """
    def process_payment(self, order_id: str, amount: float) -> bool:
        """
        模拟支付处理逻辑。
        :param order_id: 订单ID
        :param amount: 支付金额
        :return: 支付是否成功
        """
        # 模拟支付网关调用，实际实现可能涉及网络请求
        logger.info(f"处理订单 {order_id} 的支付，金额: {amount:.2f}")
        return random.choice([True, False])  # 模拟支付成功或失败

class OrderProcessor:
    """
    订单处理器，负责计算折扣、调用支付网关、更新订单状态。
    """
    def __init__(self, payment_gateway: PaymentGateway):
        self.payment_gateway = payment_gateway

    def calculate_discount(self, total_price: float, discount_rate: float = 0.1) -> float:
        """
        计算折扣后的价格。
        :param total_price: 原始总价
        :param discount_rate: 折扣率，默认为0.1
        :return: 折扣后价格
        """
        # 体现 Item 113：浮点数计算可能引入精度问题，后续测试中使用 assertAlmostEqual
        return total_price * (1 - discount_rate)

    def process_order(self, order: dict) -> bool:
        """
        处理单个订单：计算折扣、发起支付、更新状态。
        :param order: 订单数据
        :return: 处理是否成功
        """
        try:
            # 计算折扣后价格
            discounted_price = self.calculate_discount(order["total_price"])
            logger.info(f"订单 {order['order_id']} 折扣后价格: {discounted_price:.2f}")

            # 体现 Item 114：条件断点，当折扣价格异常（例如负数）时启动调试
            if discounted_price < 0:
                logger.warning(f"订单 {order['order_id']} 折扣价格异常: {discounted_price}")
                breakpoint()  # 交互式调试，允许检查变量状态

            # 调用支付网关
            payment_success = self.payment_gateway.process_payment(order["order_id"], discounted_price)
            if not payment_success:
                logger.error(f"订单 {order['order_id']} 支付失败")
                return False

            # 更新订单状态
            order["status"] = "completed"
            logger.info(f"订单 {order['order_id']} 处理完成，状态: {order['status']}")
            return True
        except Exception as e:
            logger.error(f"订单 {order['order_id']} 处理失败: {str(e)}")
            return False

# ---------------- 测试区 ----------------

def setUpModule():
    """
    模块级初始化，设置测试环境。
    体现 Item 110：使用 setUpModule 进行模块级测试夹具初始化。
    """
    logger.info("初始化测试模块：设置全局测试环境")
    # 模拟初始化数据库或外部服务（此处仅记录日志）
    global TEST_DIR
    TEST_DIR = TemporaryDirectory()
    logger.info(f"创建临时目录: {TEST_DIR.name}")

def tearDownModule():
    """
    模块级清理，释放测试资源。
    体现 Item 110：使用 tearDownModule 清理模块级资源。
    """
    logger.info("清理测试模块：释放临时目录")
    TEST_DIR.cleanup()

class OrderProcessorTestCase(TestCase):
    """
    单元测试类，验证 OrderProcessor 的相关行为。
    体现 Item 108：通过 TestCase 子类验证相关行为。
    体现 Item 111：使用 Mock 测试复杂依赖（支付网关）。
    体现 Item 113：使用 assertAlmostEqual 控制浮点数精度。
    """
    def setUp(self):
        """
        测试前初始化，确保测试隔离。
        体现 Item 110：使用 setUp 隔离测试环境。
        """
        self.payment_gateway = Mock(spec=PaymentGateway)
        self.processor = OrderProcessor(self.payment_gateway)
        self.test_order = {
            "order_id": "test-123",
            "total_price": 100.0,
            "items": [{"name": "Test Product", "price": 100.0}],
            "status": "pending"
        }
        logger.info("初始化单元测试环境")

    def tearDown(self):
        """
        测试后清理，释放资源。
        体现 Item 110：使用 tearDown 清理测试环境。
        """
        logger.info("清理单元测试环境")

    def test_calculate_discount(self):
        """
        测试折扣计算逻辑。
        体现 Item 113：使用 assertAlmostEqual 验证浮点数计算。
        """
        result = self.processor.calculate_discount(100.0, 0.1)
        self.assertAlmostEqual(result, 90.0, places=2)  # 允许两位小数精度
        logger.info("折扣计算测试通过")

    def test_process_order_success(self):
        """
        测试订单处理成功场景。
        体现 Item 108：验证订单处理的相关行为。
        体现 Item 111：Mock 支付网关行为。
        """
        self.payment_gateway.process_payment.return_value = True
        success = self.processor.process_order(self.test_order)
        self.assertTrue(success)
        self.assertEqual(self.test_order["status"], "completed")
        self.payment_gateway.process_payment.assert_called_once_with("test-123", 90.0)
        logger.info("订单处理成功测试通过")

    def test_process_order_failure(self):
        """
        测试订单处理失败场景。
        体现 Item 108：验证失败情况下的行为。
        体现 Item 111：Mock 支付网关失败行为。
        """
        self.payment_gateway.process_payment.return_value = False
        success = self.processor.process_order(self.test_order)
        self.assertFalse(success)
        self.assertEqual(self.test_order["status"], "pending")
        self.payment_gateway.process_payment.assert_called_once_with("test-123", 90.0)
        logger.info("订单处理失败测试通过")

class OrderIntegrationTestCase(TestCase):
    """
    集成测试类，验证 OrderProcessor 和 PaymentGateway 的端到端行为。
    体现 Item 109：优先集成测试验证多组件协作。
    体现 Item 110：使用 setUp/tearDown 隔离测试。
    """
    def setUp(self):
        """
        测试前初始化真实 PaymentGateway。
        体现 Item 110：隔离测试环境。
        """
        self.payment_gateway = PaymentGateway()  # 使用真实支付网关
        self.processor = OrderProcessor(self.payment_gateway)
        self.test_order = {
            "order_id": "integ-123",
            "total_price": 200.0,
            "items": [{"name": "Integ Product", "price": 200.0}],
            "status": "pending"
        }
        logger.info("初始化集成测试环境")

    def tearDown(self):
        """
        测试后清理。
        体现 Item 110：清理测试环境。
        """
        logger.info("清理集成测试环境")

    def test_full_order_processing(self):
        """
        测试完整的订单处理流程（端到端）。
        体现 Item 109：验证多组件协作行为。
        """
        success = self.processor.process_order(self.test_order)
        # 由于 PaymentGateway 使用随机结果，检查状态是否符合预期
        if success:
            self.assertEqual(self.test_order["status"], "completed")
        else:
            self.assertEqual(self.test_order["status"], "pending")
        logger.info("集成测试：订单处理流程测试通过")

# ---------------- 主流程控制区 ----------------

def run_order_processing():
    """
    主函数：生成订单数据，处理订单，监控内存使用。
    体现 Item 115：使用 tracemalloc 监控内存使用。
    """
    logger.info("启动在线零售订单处理系统")

    # 启动 tracemalloc 监控内存
    tracemalloc.start(10)  # 设置堆栈深度
    snapshot1 = tracemalloc.take_snapshot()
    logger.info("获取内存快照：处理前")

    # 生成订单数据
    orders = generate_order_data()

    # 初始化处理器
    payment_gateway = PaymentGateway()  # 体现 Item 112：使用封装的依赖
    processor = OrderProcessor(payment_gateway)

    # 处理订单
    success_count = 0
    for order in orders[:1000]:  # 限制处理1000条以节省时间
        if processor.process_order(order):
            success_count += 1
    logger.info(f"成功处理 {success_count} 条订单")

    # 内存分析
    snapshot2 = tracemalloc.take_snapshot()
    stats = snapshot2.compare_to(snapshot1, "lineno")
    logger.info("内存使用分析：前3个主要内存占用者")
    for stat in stats[:3]:
        logger.info(f"{stat}")

    # 运行测试
    logger.info("开始运行单元测试和集成测试")
    try:
        unittest_main()
    except SystemExit:
        logger.info("测试运行完成")

if __name__ == "__main__":
    run_order_processing()