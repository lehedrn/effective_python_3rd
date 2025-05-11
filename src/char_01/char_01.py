"""
Chapter 1: Pythonic Thinking - 图书馆管理系统实战示例

本模块展示了 Effective Python 第一章中多个 Pythonic 思想的综合应用：
- 明确 Python 版本(Item 1)
- 遵循 PEP8 规范（Item 2）
- 使用 helper functions 替代复杂逻辑（Item 4）
- 用多重解包替代索引访问（Item 5）
- 单元素元组显式声明（Item 6）
- 条件表达式用于简单判断（Item 7）
- 海象运算符减少重复调用（Item 8）
- match 结构化解构控制流（Item 9）
"""

# Item2: 导包优先级
import logging
import sys
from dataclasses import dataclass
from typing import Optional, Dict, Tuple


# 设置日志系统
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Item 1: 明确Python版本
def check_python_version():
    """
    检查 Python 版本是否符合要求
    """
    logger.info("检查 Python 版本...")
    if not (3, 10) <= sys.version_info:
        logger.error("Python 版本不支持，请升级到3.10 + 版本")
        sys.exit(1)
    else:
        logger.info("Python 版本符合要求")

# 🔹 Item 56: 使用 dataclass 构建不可变数据模型
@dataclass(frozen=True)
class Book:
    title: str
    author: str
    available_copies: int

    def __repr__(self):
        return f"<书名: {self.title}, 作者: {self.author}, 可借数量: {self.available_copies}>"


# 模拟库存数据
inventory = {
    "001": Book(title="Python编程入门", author="Guido van Rossum", available_copies=5),
    "002": Book(title="Effective Python", author="Brett Slatkin", available_copies=2),
    "003": Book(title="Fluent Python", author="Luciano Ramalho", available_copies=0),
}

# 🔹 Item 4: 提取常量到顶层以复用
MAX_BORROW_LIMIT = 3


# 错误示例（反面教材：未使用 Pythonic 方法）
def check_book_availability_bad(book_id: str) -> bool:
    """
    ❌ 错误写法：未遵循 Pythonic 原则的地方
    """
    logger.info("开始检查书籍 %s 的可用性...", book_id)

    # ❌ Item 5: 直接用索引访问数据结构，不直观
    book_tuple = inventory.get(book_id)
    if book_tuple and book_tuple[2] > 0:
        logger.info("书籍《%s》可供借阅", book_tuple[0])
        return True
    else:
        logger.warning("书籍不可用或不存在")
        return False


# 正确实例（符合 Pythonic 规范）
def check_book_availability(book_id: str) -> Optional[Book]:
    """
    ✅ 符合 Pythonic 的写法：
    - 使用 walrus operator 减少重复调用（Item 8）
    - 使用解包提高可读性（Item 5）
    - 返回专用对象代替裸值（更清晰、更一致）
    """
    logger.info("开始检查书籍 %s 的可用性...", book_id)

    # 🔹 Item 8: 海象运算符减少冗余调用
    if (book := inventory.get(book_id)) and book.available_copies > 0:
        logger.info("书籍《%s》可供借阅", book.title)
        return book
    else:
        logger.warning("书籍不可用或不存在")
        return None


# 🔹 Item 4: 抽离常用逻辑到辅助函数
def update_inventory(inventory: Dict[str, Book], book_id: str, borrow_count: int) -> Optional[Book]:
    """
    更新库存并返回书籍状态。
    - 如果库存不足，抛出异常
    - 否则更新可借数量
    """
    logger.info("尝试更新书籍 %s 的库存，借书数量：%d", book_id, borrow_count)

    if (book := inventory.get(book_id)) is None:
        logger.error("书籍 %s 不存在！", book_id)
        return None

    # 🔹 Item 7: 简单条件表达式优化易读性
    new_copies = book.available_copies - borrow_count if book.available_copies >= borrow_count else 0

    if new_copies < 0:
        logger.error("库存不足，无法借阅《%s》", book.title)
        return None

    # 🔹 Item 56: 修改不可变对象时，生成新对象代替直接修改
    updated_book = Book(title=book.title, author=book.author, available_copies=new_copies)
    inventory[book_id] = updated_book
    logger.info("更新完成：《%s》剩下 %d 本", book.title, new_copies)
    return updated_book


# 🔹 Item 9: 使用 match 进行结构化控制流
def process_user_request(user_request: Tuple[str, str]) -> None:
    """
    根据用户请求动态选择操作类型（借用/归还/续借）
    """
    logger.info("开始处理用户请求 %s...", user_request)

    action, book_id = user_request  # 🔹 Item 5: 使用 tuple 解包提取参数

    match action:
        case "borrow" if (book := check_book_availability(book_id)):
            logger.info("用户借阅了《%s》", book.title)
            update_inventory(inventory, book_id, 1)

        case "return" if inventory.get(book_id):
            logger.info("用户归还了书籍 %s", book_id)
            update_inventory(inventory, book_id, -1)

        case "renew":
            logger.info("用户续借了书籍 %s", book_id)
            if not inventory.get(book_id):
                logger.warning("续借失败：未找到书籍")

        case _:
            logger.error("无效请求：无法识别的操作 %s", action)


# 主程序运行逻辑
if __name__ == "__main__":

    check_python_version()

    logger.info("# —— 图书馆管理系统示例 ——\n")

    # 模拟用户交互数据
    requests = [
        ("borrow", "001"),  # 借阅成功
        ("borrow", "003"),  # 借阅失败（库存不足）
        ("return", "002"),  # 归还成功
        ("renew", "001"),   # 续借成功
        ("unknown", "004")  # 无效请求
    ]

    for request in requests:
        process_user_request(request)
