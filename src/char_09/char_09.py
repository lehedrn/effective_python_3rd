"""
物流订单并发处理系统

功能：
- 模拟生成10万条物流订单数据
- 使用subprocess调用外部命令行工具压缩归档历史数据
- 多线程并发处理订单状态更新
- 使用Lock保护共享的库存资源
- 使用Queue协调线程间工作分配
- ThreadPoolExecutor管理固定数量的工作线程池
- asyncio实现高度并发的I/O操作
- concurrent.futures实现真正的并行计算

涉及Effective Python第9章并发与并行相关条目：
Item 67: 使用subprocess管理子进程
Item 68: 对阻塞I/O使用线程；避免用于并行
Item 69: 使用Lock防止线程中的数据竞争
Item 70: 使用Queue协调线程间的工作
Item 71: 知道何时需要并发
Item 72: 避免为按需扇出创建新的线程实例
Item 73: 理解使用队列进行并发需要重构
Item 74: 考虑ThreadPoolExecutor当线程对于并发是必要时
Item 75: 通过协程实现高度并发的I/O
Item 76: 知道如何将线程I/O移植到asyncio
Item 77: 混合同步线程和协程简化向asyncio过渡
Item 78: 使用async友好型工作线程最大化asyncio事件循环响应性
Item 79: 考虑使用concurrent.futures实现真正的并行
"""

import logging
import random
import string
import json
from datetime import datetime, timedelta
import subprocess
from threading import Thread, Lock, Barrier
from queue import Queue, Empty
import os
import time
import asyncio
import aiofiles
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed


# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('LogisticsSystem')

# 全局变量
INVENTORY_LOCK = Lock()
ORDER_QUEUE = Queue(maxsize=1000)
RESULT_QUEUE = Queue(maxsize=1000)
PROCESSED_COUNT = 0
PROCESSED_LOCK = Lock()
BARRIER = None
CURRENT_INVENTORY = 100000  # 初始库存


def generate_mock_data(count=100000):
    """
    生成模拟的物流订单数据

    Item 71: 知道何时需要并发
    - 当需要处理大量订单数据时，并发处理成为必要选择
    """
    logger.info(f"开始生成{count}条模拟订单数据")

    status_options = ['PENDING', 'PROCESSING', 'SHIPPED', 'DELIVERED', 'CANCELLED']

    orders = []
    for i in range(count):
        order_id = f"ORD{i:06d}"
        customer_id = f"CUST{random.randint(1000, 9999)}"
        product_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        create_time = datetime.now() - timedelta(days=random.randint(0, 30))

        order = {
            'order_id': order_id,
            'customer_id': customer_id,
            'product_code': product_code,
            'quantity': random.randint(1, 20),
            'status': random.choice(status_options),
            'create_time': create_time.isoformat(),
            'update_time': create_time.isoformat()
        }
        orders.append(order)

    logger.info("模拟数据生成完成")
    return orders


def update_inventory(quantity):
    """
    更新库存（受锁保护）

    Item 69: 使用Lock防止线程中的数据竞争
    - 库存更新操作必须是原子性的
    """
    with INVENTORY_LOCK:
        # 模拟实际库存管理系统
        global CURRENT_INVENTORY
        if CURRENT_INVENTORY >= quantity:
            CURRENT_INVENTORY -= quantity
            success = True
        else:
            success = False
    return success


def process_order(order):
    """
    处理单个订单

    Item 68: 对阻塞I/O使用线程
    - 订单处理包含数据库访问等阻塞操作
    """
    try:
        # 模拟数据库查询
        time.sleep(0.001)

        # 更新库存
        if order['status'] == 'PROCESSING' and not update_inventory(order['quantity']):
            order['status'] = 'PENDING'

        # 模拟其他业务逻辑
        order['update_time'] = datetime.now().isoformat()
        return order
    except Exception as e:
        logger.error(f"处理订单 {order['order_id']} 时发生错误: {str(e)}", exc_info=True)
        return order


def worker_thread():
    """
    工作线程函数

    Item 72: 避免为按需扇出创建新的线程实例
    - 使用预定义的线程池而不是动态创建线程
    """
    while True:
        try:
            order = ORDER_QUEUE.get(timeout=1)  # 添加超时防止线程卡死

            processed_order = process_order(order)

            with PROCESSED_LOCK:
                global PROCESSED_COUNT
                PROCESSED_COUNT += 1
                if PROCESSED_COUNT % 1000 == 0:
                    logger.info(f"已处理订单数: {PROCESSED_COUNT}")

            RESULT_QUEUE.put(processed_order)
            ORDER_QUEUE.task_done()
        except Empty:
            # 超时后检查是否应该退出
            if BARRIER.wait(timeout=0.1) == 0:
                break
        except Exception as e:
            logger.error(f"工作线程发生错误: {str(e)}", exc_info=True)


async def async_process_order(loop, order, executor):
    """
    异步处理订单

    Item 75: 通过协程实现高度并发的I/O
    - 协程更适合处理高并发的I/O操作
    """
    try:
        # 在线程池中执行阻塞操作
        processed_order = await loop.run_in_executor(executor, process_order, order)

        # 异步写入文件
        filename = f"output/order_{processed_order['order_id']}.json"
        async with aiofiles.open(filename, 'w') as f:
            await f.write(json.dumps(processed_order))

        return processed_order
    except Exception as e:
        logger.error(f"异步处理订单时发生错误: {str(e)}", exc_info=True)
        return order


def parallel_process_orders(orders):
    """
    并行处理订单

    Item 79: 考虑使用concurrent.futures实现真正的并行
    - 使用ProcessPoolExecutor实现真正的并行计算
    """
    logger.info("开始并行处理订单")

    # 分割任务
    chunks = [orders[i:i + 1000] for i in range(0, len(orders), 1000)]

    results = []
    # 使用进程池执行器
    with ProcessPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(parallel_process_chunk, chunk) for chunk in chunks]

        for future in as_completed(futures):
            try:
                chunk_results = future.result()
                results.extend(chunk_results)
            except Exception as e:
                logger.error(f"并行处理发生错误: {str(e)}", exc_info=True)

    logger.info("并行处理完成")
    return results


def parallel_process_chunk(chunk):
    """并行处理单个订单块"""
    return [process_order(order) for order in chunk]


def setup_worker_threads(num_workers):
    """
    设置工作线程池

    Item 74: 在需要线程时考虑ThreadPoolExecutor
    - 使用线程池管理固定数量的工作线程
    """
    logger.info(f"启动 {num_workers} 个工作线程")

    workers = []
    for _ in range(num_workers):
        t = Thread(target=worker_thread)
        t.start()
        workers.append(t)

    return workers


def shutdown_workers(workers):
    """关闭工作线程"""
    for _ in workers:
        ORDER_QUEUE.put(None)

    for t in workers:
        t.join()

    logger.info("所有工作线程已关闭")


async def monitor_progress(total_orders):
    """监控处理进度"""
    while True:
        with PROCESSED_LOCK:
            current_count = PROCESSED_COUNT

        if current_count >= total_orders:
            break

        logger.info(f"当前处理进度: {current_count}/{total_orders}")
        await asyncio.sleep(1)


async def run_async_processing(loop, orders, executor):
    """
    运行异步订单处理流程

    Item 76: 知道如何将线程I/O移植到asyncio
    - 将传统的线程I/O操作移植到asyncio框架
    """
    logger.info("开始异步订单处理")

    tasks = [async_process_order(loop, order, executor) for order in orders]
    results = await asyncio.gather(*tasks)

    logger.info("异步处理完成")
    return results


def run_queue_based_processing(orders):
    """
    基于队列的订单处理流程

    Item 73: 理解使用队列进行并发需要重构
    - 使用队列需要对程序结构进行适当重构
    """
    logger.info("开始基于队列的订单处理")

    # 启动工作线程
    num_workers = 5
    workers = setup_worker_threads(num_workers)

    # 提交任务
    for order in orders:
        ORDER_QUEUE.put(order)

    # 等待处理完成
    ORDER_QUEUE.join()

    # 收集结果
    results = []
    while not RESULT_QUEUE.empty():
        results.append(RESULT_QUEUE.get())
        RESULT_QUEUE.task_done()

    # 关闭工作线程
    shutdown_workers(workers)

    logger.info("基于队列的处理完成")
    return results


async def mixed_mode_processing(orders):
    """
    混合模式处理订单

    Item 77: 混合同步线程和协程简化向asyncio过渡
    - 同时使用传统线程和asyncio协程
    """
    logger.info("开始混合模式处理")

    # 创建线程池执行器
    executor = ThreadPoolExecutor(max_workers=3)

    # 启动队列处理
    queue_thread = Thread(target=run_queue_based_processing, args=(orders[:len(orders)//2],))
    queue_thread.start()

    # 启动异步处理
    loop = asyncio.get_event_loop()
    async_results = await run_async_processing(loop, orders[len(orders)//2:], executor)

    # 等待线程完成
    queue_thread.join()

    # 关闭执行器
    executor.shutdown()

    logger.info("混合模式处理完成")
    return async_results


async def responsive_event_loop(orders):
    """
    实现响应性强的事件循环

    Item 78: 使用async友好型工作线程最大化asyncio事件循环响应性
    - 通过线程池保持事件循环的响应性
    """
    logger.info("开始响应性强的事件循环处理")

    # 创建线程池
    executor = ThreadPoolExecutor(max_workers=4)

    # 处理订单
    loop = asyncio.get_event_loop()
    tasks = [loop.run_in_executor(executor, process_order, order) for order in orders]

    results = []
    for task in asyncio.as_completed(tasks):
        results.append(await task)

    logger.info("事件循环处理完成")
    return results


def archive_processed_data(data, filename):
    """
    归档已处理的数据

    Item 67: 使用subprocess管理子进程
    - 使用gzip压缩处理结果
    """
    try:
        # 将数据写入临时文件
        temp_file = f"{filename}.json"
        with open(temp_file, 'w') as f:
            json.dump(data, f)

        # 使用gzip压缩文件
        subprocess.run(['gzip', '-f', temp_file], check=True)
        logger.info(f"已归档处理结果到 {temp_file}.gz")
    except Exception as e:
        logger.error(f"归档数据时发生错误: {str(e)}", exc_info=True)


def delete_data():
    """
    删除已归档的数据
    """
    if os.path.exists('output'):
        # 清理测试文件
        for file in os.listdir('output'):
            os.remove(os.path.join('output', file))

        os.rmdir('output')

    if os.path.exists('responsive_processed.json.gz'):
        os.remove('responsive_processed.json.gz')

    logger.info("清理测试文件完成")

def main():
    global BARRIER

    logger.info("=== 物流订单处理系统启动 ===")

    # 初始化库存
    global CURRENT_INVENTORY
    CURRENT_INVENTORY = 100000

    # 生成模拟数据
    orders = generate_mock_data(100000)

    # 创建屏障
    # BARRIER = Barrier(len(orders) // 1000 + 1)

    # 方法一：基于队列的处理
    # logger.info("=== 开始基于队列的处理 ===")
    # queue_results = run_queue_based_processing(orders)
    # archive_processed_data(queue_results, "queue_processed")

    # # 方法二：异步处理
    # logger.info("=== 开始异步处理 ===")
    # loop = asyncio.new_event_loop()
    # asyncio.set_event_loop(loop)
    # async_results = loop.run_until_complete(run_async_processing(loop, orders[:1000], None))
    # archive_processed_data(async_results, "async_processed")

    # # 方法三：混合模式
    # logger.info("=== 开始混合模式处理 ===")
    # loop = asyncio.new_event_loop()
    # asyncio.set_event_loop(loop)
    # loop.run_until_complete(mixed_mode_processing(orders))

    # 方法四：并行优化
    # logger.info("=== 开始并行优化处理 ===")
    # parallel_results = parallel_process_orders(orders[:10000])  # 只取前1万条做演示
    # archive_processed_data(parallel_results, "parallel_processed")

    # 方法五：高响应事件循环
    logger.info("=== 开始高响应事件循环处理 ===")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    responsive_results = loop.run_until_complete(responsive_event_loop(orders[:5000]))
    archive_processed_data(responsive_results, "responsive_processed")

    logger.info("=== 所有处理完成 ===")

    # 清理测试文件
    delete_data()


if __name__ == "__main__":
    # 创建输出目录
    if not os.path.exists('output'):
        os.makedirs('output')

    main()
