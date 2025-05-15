"""
本文件演示了如何使用字典处理缺失键的不同方法，包括：
1. 不推荐的 `setdefault` 方法
2. 限制的 `defaultdict` 方法
3. 推荐的 `__missing__` 方法
"""

import logging
from collections import defaultdict

# 配置日志记录
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def open_picture(profile_path: str):
    """
    打开图片文件的辅助函数

    Args:
        profile_path: 文件路径

    Returns:
        file: 打开的文件对象

    Raises:
        OSError: 打开文件失败时抛出
    """
    try:
        return open(profile_path, "a+b")
    except OSError as e:
        logging.error(f"Failed to open path {profile_path}: {e}")
        raise


class Pictures(dict):
    """
    自定义字典类，用于处理缺失的图片键
    """

    def __missing__(self, key: str):
        """
        处理缺失键的自定义方法

        Args:
            key: 缺失的键

        Returns:
            value: 创建的新值
        """
        value = open_picture(key)
        self[key] = value
        return value


def bad_setdefault_example(path: str):
    """
    演示不推荐使用的 setdefault 方法的问题

    Args:
        path: 文件路径
    """
    pictures = {}

    try:
        handle = pictures.setdefault(path, open(path, "a+b"))
    except OSError as e:
        logging.error(f"Failed to open path {path}: {e}")
        raise
    else:
        handle.seek(0)
        image_data = handle.read()
        logging.info(f"Read {len(image_data)} bytes from {path}")


def better_dict_get_example(path: str):
    """
    演示更优的 dict.get 方法

    Args:
        path: 文件路径
    """
    pictures = {}

    with open(path, "wb") as f:
        f.write(b"image data here 1234")

    if (handle := pictures.get(path)) is None:
        try:
            handle = open(path, "a+b")
        except OSError as e:
            logging.error(f"Failed to open path {path}: {e}")
            raise
        else:
            pictures[path] = handle

    handle.seek(0)
    image_data = handle.read()
    logging.info(f"Read {len(image_data)} bytes from {path}")


def limited_defaultdict_example():
    """
    演示 defaultdict 的局限性
    """
    try:

        def open_picture(profile_path):
            try:
                return open(profile_path, "a+b")
            except OSError:
                print(f"Failed to open path {profile_path}")
                raise

        pictures = defaultdict(open_picture)
        handle = pictures["test.png"]
    except TypeError as e:
        logging.error(f"TypeError: {e}")


def custom_missing_method_example(path: str):
    """
    演示使用 __missing__ 方法的自定义字典类

    Args:
        path: 文件路径
    """
    pictures = Pictures()
    handle = pictures[path]
    handle.seek(0)
    image_data = handle.read()
    logging.info(f"Read {len(image_data)} bytes from {path}")


def main():
    """
    主函数，运行所有示例
    """
    path = "profile_1234.png"

    logging.info("Better dict.get example:")
    better_dict_get_example(path)

    logging.info("\nBad setdefault example (will attempt to open file twice):")
    try:
        bad_setdefault_example(path)
    except OSError:
        logging.info("As expected, OSError was raised")

    logging.info("\nDemonstrating the limitations of defaultdict:")
    limited_defaultdict_example()

    logging.info("\nCustom __missing__ method example:")
    custom_missing_method_example(path)

    # 清理测试文件
    import os
    os.remove(path)


if __name__ == "__main__":
    main()
