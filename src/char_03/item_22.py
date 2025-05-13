"""
本模块演示了在迭代容器时修改容器可能导致的问题以及推荐的解决方案。
包含字典、列表、集合等数据结构的错误示例和正确做法。
"""

import logging

# 设置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def bad_dict_modify_during_iteration():
    """
    错误示例：在迭代字典时添加键，引发 RuntimeError。
    """
    my_dict = {"red": 1, "blue": 2, "green": 3}
    try:
        for key in my_dict:
            if key == "blue":
                my_dict["yellow"] = 4  # 添加新键值对，引发异常
    except RuntimeError as e:
        logger.error("RuntimeError: %s", e)


def bad_dict_delete_during_iteration():
    """
    错误示例：在迭代字典时删除键，引发 RuntimeError。
    """
    my_dict = {"red": 1, "blue": 2, "green": 3}
    try:
        for key in my_dict:
            if key == "blue":
                del my_dict["green"]  # 删除键值对，引发异常
    except RuntimeError as e:
        logger.error("RuntimeError: %s", e)


def good_dict_modify_values_only():
    """
    正确示例：仅修改值而不改变字典结构是允许的。
    """
    my_dict = {"red": 1, "blue": 2, "green": 3}
    for key in my_dict:
        if key == "blue":
            my_dict["green"] = 4  # 修改现有值，不会引发异常
    logger.info("Modified dict (values only): %s", my_dict)


def good_dict_iterate_over_copy():
    """
    正确示例：迭代字典副本以安全地修改原始字典。
    """
    my_dict = {"red": 1, "blue": 2, "green": 3}
    keys_copy = list(my_dict.keys())  # 创建键的副本
    for key in keys_copy:
        if key == "blue":
            my_dict["green"] = 4  # 修改原始字典
    logger.info("Modified dict using copy: %s", my_dict)


def good_dict_use_staging_modifications():
    """
    正确示例：使用暂存字典暂存修改，最后统一更新。
    """
    my_dict = {"red": 1, "blue": 2, "green": 3}
    modifications = {}
    for key in my_dict:
        if key == "blue":
            modifications["green"] = 4  # 暂存修改
    my_dict.update(modifications)  # 应用暂存的修改
    logger.info("Modified dict using staging: %s", my_dict)


def bad_set_modify_during_iteration():
    """
    错误示例：在迭代集合时添加元素，引发 RuntimeError。
    """
    my_set = {"red", "blue", "green"}
    try:
        for color in my_set:
            if color == "blue":
                my_set.add("yellow")  # 添加新元素，引发异常
    except RuntimeError as e:
        logger.error("RuntimeError: %s", e)


def good_set_add_existing_element():
    """
    正确示例：向集合中添加已存在的元素是允许的。
    """
    my_set = {"red", "blue", "green"}
    for color in my_set:
        if color == "blue":
            my_set.add("green")  # 添加已存在的元素，不会引发异常
    logger.info("Modified set (add existing): %s", my_set)


def good_set_iterate_over_copy():
    """
    正确示例：迭代集合副本以安全地修改原始集合。
    """
    my_set = {"red", "blue", "green"}
    set_copy = set(my_set)  # 创建集合的副本
    for color in set_copy:
        if color == "blue":
            my_set.add("yellow")  # 修改原始集合
    logger.info("Modified set using copy: %s", my_set)


def bad_list_insert_before_current_index():
    """
    错误示例：在当前索引前插入元素会导致无限循环。
    """
    my_list = [1, 2, 3]
    try:
        for number in my_list:
            logger.info("Current number: %d", number)
            if number == 2:
                my_list.insert(0, 4)  # 插入到列表开头，导致无限循环
    except KeyboardInterrupt as e:
        logger.error("Exception: %s", e)


def good_list_append_after_current_index():
    """
    正确示例：在当前索引后追加元素不会导致问题。
    """
    my_list = [1, 2, 3]
    for number in my_list:
        logger.info("Current number: %d", number)
        if number == 2:
            my_list.append(4)  # 追加到列表末尾，不会引发异常
    logger.info("Modified list after appending: %s", my_list)


def good_list_iterate_over_copy():
    """
    正确示例：迭代列表副本以安全地修改原始列表。
    """
    my_list = [1, 2, 3]
    list_copy = list(my_list)  # 创建列表的副本
    for number in list_copy:
        logger.info("Current number (copy): %d", number)
        if number == 2:
            my_list.insert(0, 4)  # 修改原始列表
    logger.info("Modified list using copy: %s", my_list)


def main():
    """
    主函数，运行所有示例。
    """
    logger.info("Running bad_dict_modify_during_iteration:")
    bad_dict_modify_during_iteration()

    logger.info("\nRunning bad_dict_delete_during_iteration:")
    bad_dict_delete_during_iteration()

    logger.info("\nRunning good_dict_modify_values_only:")
    good_dict_modify_values_only()

    logger.info("\nRunning good_dict_iterate_over_copy:")
    good_dict_iterate_over_copy()

    logger.info("\nRunning good_dict_use_staging_modifications:")
    good_dict_use_staging_modifications()

    logger.info("\nRunning bad_set_modify_during_iteration:")
    bad_set_modify_during_iteration()

    logger.info("\nRunning good_set_add_existing_element:")
    good_set_add_existing_element()

    logger.info("\nRunning good_set_iterate_over_copy:")
    good_set_iterate_over_copy()

    logger.info("\nRunning bad_list_insert_before_current_index:")
    bad_list_insert_before_current_index()

    logger.info("\nRunning good_list_append_after_current_index:")
    good_list_append_after_current_index()

    logger.info("\nRunning good_list_iterate_over_copy:")
    good_list_iterate_over_copy()


if __name__ == "__main__":
    main()
