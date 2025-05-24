"""
医院患者数据处理系统

功能说明：
- 生成模拟患者体检数据
- 写入临时文件进行备份
- 使用上下文管理器确保资源正确释放
- 解析数据并验证完整性
- 异常处理与日志记录

实现条目：
Item 80: 利用 try/except/else/finally 各个块
Item 81: 使用 assert 验证内部假设
Item 82: 使用 contextlib 和 with 管理资源
Item 83: 最小化 try 块
Item 84: 防止异常变量消失
Item 85: 警惕捕获 Exception 类本身
Item 86: 区分 Exception 和 BaseException
Item 87: 使用 traceback 获取详细错误信息
Item 88: 显式链式抛出异常
Item 89: 生成器接收外部资源
Item 90: 不设置 __debug__ = False
Item 91: 避免使用 eval/exec
"""

import logging
import os
import random
import string
import tempfile
import traceback
from datetime import datetime
from typing import Generator, List, Dict, Any
from contextlib import contextmanager

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Item 90: Never Set __debug__ to False
assert __debug__, "调试模式被禁用，这可能导致断言失效"

# 数据构造区
def generate_patient_records(count: int = 100000) -> Generator[Dict[str, Any], None, None]:
    """
    生成模拟患者体检数据（ID、时间戳、状态、血压、心率等）
    """
    statuses = ['stable', 'critical', 'recovering']
    for i in range(count):
        yield {
            'patient_id': ''.join(random.choices(string.ascii_uppercase + string.digits, k=8)),
            'timestamp': datetime.now().isoformat(),
            'status': random.choice(statuses),
            'blood_pressure': f"{random.randint(90, 180)}/{random.randint(60, 120)}",
            'heart_rate': random.randint(50, 120)
        }

# 上下文管理器：用于创建临时备份文件
@contextmanager
def TemporaryFileBackup(prefix: str = 'backup_', suffix: str = '.txt') -> str:
    """
    Item 82: 使用 contextlib 创建上下文管理器，确保临时文件关闭
    """
    temp_file = tempfile.NamedTemporaryFile(prefix=prefix, suffix=suffix, delete=False)
    try:
        logging.info(f"创建临时备份文件: {temp_file.name}")
        yield temp_file.name
    finally:
        temp_file.close()
        os.unlink(temp_file.name)
        logging.info("临时备份文件已清理")

# 数据写入与读取
def write_patient_to_file(records: Generator[Dict[str, Any], None, None], filename: str):
    """
    将患者数据写入文件
    """
    try:
        with open(filename, 'w') as f:
            for record in records:
                f.write(f"{record}\n")
    except IOError as e:
        logging.error(f"写入文件失败: {e}")
        raise

def read_patient_file(filename: str) -> List[Dict[str, Any]]:
    """
    读取患者数据文件
    """
    # Item 83: Always Make try Blocks as Short as Possible
    try:
        with open(filename, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError as e:
        logging.error(f"文件未找到: {e}")
        raise

    records = []
    for line in lines:
        try:
            # Item 88: Consider Explicitly Chaining Exceptions
            # 使用 eval 是一个潜在风险点（Item 91），这里仅用于示例
            # 在真实项目中应避免使用 eval
            record = eval(line.strip())
            records.append(record)
        except SyntaxError as e:
            logging.error(f"解析行失败: {line}")
            raise ValueError("无法解析记录") from e
    return records

# 数据校验
def validate_patient_data(records: List[Dict[str, Any]]):
    """
    校验患者数据是否完整有效
    """
    # Item 81: assert Internal Assumptions
    assert isinstance(records, list), "记录必须是列表类型"
    assert all('patient_id' in r for r in records), "每条记录必须包含 patient_id"

    if not records:
        raise ValueError("无有效记录")

# 主流程控制
def process_patient_data():
    """
    处理患者数据的主流程
    """
    try:
        # 生成模拟数据
        logging.info("开始生成模拟患者数据...")
        patient_generator = generate_patient_records(100000)

        # 使用上下文管理器创建临时文件
        with TemporaryFileBackup() as temp_filename:
            logging.info("写入临时备份文件...")
            write_patient_to_file(patient_generator, temp_filename)

            # 读取并处理数据
            logging.info("读取并处理数据...")
            records = read_patient_file(temp_filename)

            # 校验数据
            validate_patient_data(records)

            # Item 80: Use try/except/else/finally
        logging.info("所有数据处理成功")
    except ValueError as ve:
        # Item 85: Beware of Catching the Exception Class
        logging.error(f"值错误异常: {ve}")
        # Item 87: Use traceback for Enhanced Exception Reporting
        logging.debug(traceback.format_exc())
    except BaseException as be:
        # Item 86: Understand the Difference Between Exception and BaseException
        logging.critical(f"基础异常被捕获: {be}")
        logging.debug(traceback.format_exc())
        raise
    else:
        logging.info("数据处理完成，无异常发生")
    finally:
        logging.info("数据处理流程结束")

# 异常变量测试
def log_error_details():
    """
    Item 84: Beware of Exception Variables Disappearing
    """
    try:
        raise RuntimeError("这是一个测试异常")
    except Exception as e:
        exc_info = (type(e), e, e.__traceback__)
        # 模拟延迟处理异常
        logging.warning(f"捕获到异常: {e}")
        # 确保异常变量仍然可用
        logging.warning(f"异常详细信息: {exc_info}")

# 生成器接收外部资源
def generate_patient_records_from_file(file_path: str) -> Generator[Dict[str, Any], None, None]:
    """
    Item 89: Always Pass Resources into Generators and Have Callers Clean Them Up Outside
    """
    with open(file_path, 'r') as f:
        for line in f:
            yield eval(line.strip())

if __name__ == '__main__':
    # 测试异常变量是否消失
    log_error_details()

    # 主流程执行
    process_patient_data()
