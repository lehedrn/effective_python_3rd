"""
用户行为分析系统 - 使用迭代器和循环进行数据处理

业务背景：
本系统用于分析电商平台的用户行为日志，检测异常登录模式并生成用户活跃度报告。
使用了多个Python内置模块特性，自然融合在实际业务场景中。

包含知识点：
Item 17: 使用 enumerate 替代 range 提高可读性和安全性
Item 18: 使用 zip 并行遍历多个相关序列
Item 20: 避免在循环结束后使用循环变量
Item 21: 在遍历参数时保持防御性
Item 22: 不在迭代容器时直接修改容器
Item 23: 使用 any/all 进行高效短路逻辑判断
Item 24: 使用 itertools 处理复杂迭代逻辑
Item 19: 避免在 for/while 循环后使用 else 块（通过重构避免）
"""

import itertools
import logging
import random
import time
from collections.abc import Iterator
from operator import itemgetter
from typing import List, Dict, Tuple, Union

# 配置日志系统
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def generate_user_logins(num_users: int = 1000) -> List[Dict[str, Union[str, float]]]:
    """
    生成模拟的用户登录数据

    Args:
        num_users: 要生成的用户数量

    Returns:
        包含用户登录信息的列表，每个元素是一个字典
    """
    logger.info(f"开始生成 {num_users} 条用户登录记录")

    locations = ["北京", "上海", "广州", "深圳", "杭州", "成都", "武汉"]
    devices = ["PC", "手机", "平板"]
    browsers = ["Chrome", "Firefox", "Safari", "Edge", "移动端浏览器"]

    logins = []
    for i in range(num_users):
        # 模拟用户ID、IP地址、地理位置等信息
        user_id = f"U{i:04d}"
        ip_address = f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
        location = random.choice(locations)
        device = random.choice(devices)
        browser = random.choice(browsers)
        login_time = random.uniform(0, 24)  # 登录时间 (0-24小时)

        logins.append({
            "user_id": user_id,
            "ip": ip_address,
            "location": location,
            "device": device,
            "browser": browser,
            "login_time": login_time
        })

    logger.info(f"成功生成 {len(logins)} 条用户登录记录")
    # 打印前3条用户登录信息
    logger.debug(f"前3条用户登录记录：{logins[:3]}")
    return logins


def is_suspicious_login(login: Dict) -> bool:
    """
    判断一个登录是否可疑

    Args:
        login: 用户登录信息字典

    Returns:
        是否为可疑登录
    """
    # 凌晨时段登录（0点到5点）被视为可疑
    if 0 <= login["login_time"] < 5:
        return True

    # 非常见设备或浏览器组合
    common_combinations = [("PC", "Chrome"), ("手机", "移动端浏览器"), ("平板", "Safari")]
    if (login["device"], login["browser"]) not in common_combinations:
        return True

    return False


def check_for_anomalies(logins: Union[List[Dict], Iterator]) -> List[Dict]:
    """
    检测异常登录行为

    Args:
        logins: 用户登录记录

    Returns:
        发现的异常登录记录列表
    """
    logger.info("开始检测异常登录行为")

    # Item 21: 在遍历参数时保持防御性
    if isinstance(logins, Iterator):
        logger.warning("检测到输入是迭代器，这可能导致数据耗尽问题")
        logins = list(logins)  # 将迭代器转换为列表以确保多次可用

    suspicious_logins = []

    # Item 17: 使用 enumerate 替代 range
    for index, login in enumerate(logins):  # 记录索引和登录信息
        # Item 23: 使用 any 进行高效短路逻辑判断
        if any([
            login["login_time"] < 5,  # 凌晨登录
            login["device"] == "其他" and login["browser"] == "其他",  # 异常设备/浏览器组合
            login.get("failed_attempts", 0) > 2  # 多次失败尝试（如果存在该字段）
        ]):
            suspicious_logins.append(login)

    logger.info(f"发现 {len(suspicious_logins)} 个可疑登录记录", )
    return suspicious_logins


def find_similar_login_patterns(logins: List[Dict]) -> List[Tuple[Dict, Dict]]:
    """
    查找相似的登录模式

    Args:
        logins: 用户登录记录

    Returns:
        包含相似登录模式的元组列表
    """
    logger.info("开始查找相似登录模式")

    # Item 22: 不在迭代容器时直接修改容器
    # 创建副本以避免在迭代过程中修改原数据
    login_copy = list(logins)

    similar_patterns = []

    # Item 18: 使用 zip 并行遍历多个相关序列
    # 使用 zip 将原始登录记录与其后续记录配对
    for current, next_login in zip(login_copy, login_copy[1:]):
        # 如果两个连续登录的时间差小于1小时且使用不同IP，则视为相似模式
        time_diff = abs(current["login_time"] - next_login["login_time"])
        if time_diff < 1 and current["ip"] != next_login["ip"]:
            similar_patterns.append((current, next_login))

    logger.info(f"发现 {len(similar_patterns)} 组相似登录模式", )
    return similar_patterns


def analyze_login_frequencies(logins: List[Dict]) -> Dict[str, int]:
    """
    分析各城市的登录频率

    Args:
        logins: 用户登录记录

    Returns:
        每个城市对应的登录次数
    """
    logger.info("开始分析各城市登录频率")

    # Item 24: 使用 itertools 处理复杂迭代逻辑
    # 使用 groupby 对登录按地理位置分组
    sorted_logins = sorted(logins, key=lambda x: x["location"])
    frequency = {}

    for location, group in itertools.groupby(sorted_logins, key=lambda x: x["location"]):
        count = sum(1 for _ in group)
        frequency[location] = count

    logger.info(f"完成登录频率分析，发现 {len(frequency)} 个不同地区")
    return frequency


def detect_abnormal_activity(logins: List[Dict]) -> List[Dict]:
    """
    检测异常活动模式

    O(n²) 嵌套循环效率低

    Args:
        logins: 用户登录记录

    Returns:
        包含异常活动模式的记录列表
    """
    logger.info("开始检测异常活动模式")
    start_time = time.time()

    abnormal_activities = []

    # 使用 tee 创建多个迭代器副本以便多次使用
    # Item 24: 使用 itertools 处理复杂迭代逻辑
    login_iter1, login_iter2 = itertools.tee(logins, 2)

    # 使用 islice 对登录记录进行切片分析
    night_logins = list(itertools.islice(
        (login for login in login_iter1 if 0 <= login["login_time"] < 6),
        0, None
    ))

    mobile_logins = list(itertools.islice(
        (login for login in login_iter2 if login["device"] in ["手机", "平板"]),
        0, None
    ))

    # 找出既是夜间登录又是移动设备登录的记录
    for night_login in night_logins:
        for mobile_login in mobile_logins:
            if night_login["user_id"] == mobile_login["user_id"]:
                abnormal_activities.append(night_login)
                break  # 使用 break 跳出内层循环

    end_time = time.time()
    logger.info(f"发现 {len(abnormal_activities)} 个异常活动记录，耗时 {(end_time - start_time):.4f} 秒")
    return abnormal_activities


def detect_abnormal_activity_v1(logins: List[Dict]) -> List[Dict]:
    """
    检测异常活动模式 - 使用 itertools.groupby 进行分组分析
    将登录记录按 user_id 排序后，用 groupby 聚合每个用户的所有登录行为。然后对每个用户的登录记录进行判断，是否满足“夜间+移动设备”的双重条件。

    O(n log n) 分组清晰，适合大数据
    """
    logger.info("开始检测异常活动模式")
    start_time = time.time()

    # 按 user_id 排序以便分组
    sorted_logins = sorted(logins, key=itemgetter("user_id"))

    abnormal_activities = []

    for user_id, group in itertools.groupby(sorted_logins, key=itemgetter("user_id")):
        has_night_login = False
        has_mobile_login = False

        for login in group:
            if 0 <= login["login_time"] < 6:
                has_night_login = True
            if login["device"] in ["手机", "平板"]:
                has_mobile_login = True

            if has_night_login and has_mobile_login:
                abnormal_activities.append(login)
                break

    end_time = time.time()
    logger.info(f"发现 {len(abnormal_activities)} 个异常活动记录，耗时 {(end_time - start_time):.4f} 秒")
    return abnormal_activities


def detect_abnormal_activity_v2(logins: List[Dict]) -> List[Dict]:
    """
    检测异常活动模式 - 使用 itertools.tee 进行迭代器复制
    结合集合查找与 filterfalse 筛选不符合条件的记录，提升效率的同时仍体现 itertools 的函数式编程风格。
    O(n) 函数式风格，性能最佳
    """
    logger.info("开始检测异常活动模式")
    start_time = time.time()

    # 创建两个迭代器副本
    iter1, iter2 = itertools.tee(logins)

    # 提取夜间登录和移动设备登录的用户ID集合
    night_users = set(login["user_id"] for login in itertools.filterfalse(lambda x: not (0 <= x["login_time"] < 6), iter1))
    mobile_users = set(login["user_id"] for login in itertools.filterfalse(lambda x: x["device"] not in ["手机", "平板"], iter2))

    # 找出交集
    abnormal_user_ids = night_users & mobile_users

    # 返回原始数据中符合异常条件的记录
    abnormal_activities = [login for login in logins if login["user_id"] in abnormal_user_ids]

    end_time = time.time()
    logger.info(f"发现 {len(abnormal_activities)} 个异常活动记录，耗时 {(end_time - start_time):.4f} 秒")
    return abnormal_activities


def main():
    """主函数：运行完整的用户行为分析流程"""
    logger.info("开始执行用户行为分析流程")

    # 数据生成
    logins = generate_user_logins(100000)

    # 异常登录检测
    suspicious_logins = check_for_anomalies(logins)

    # 相似登录模式检测
    similar_patterns = find_similar_login_patterns(logins)

    # 登录频率分析
    login_frequencies = analyze_login_frequencies(logins)

    # 异常活动检测
    logger.info("开始检测异常活动模式")
    logger.debug("使用嵌套循环进行异常活动检测")
    abnormal_activities = detect_abnormal_activity(logins)
    logger.debug("使用 itertools.groupby 进行异常活动检测")
    abnormal_activities_v1 = detect_abnormal_activity_v1(logins)
    logger.debug("使用 itertools.tee 进行异常活动检测")
    abnormal_activities_v2 = detect_abnormal_activity_v2(logins)

    # 输出统计摘要
    logger.info(f"总登录记录数: {len(logins)}")
    logger.info(f"可疑登录记录数: {len(suspicious_logins)}")
    logger.info(f"相似登录模式组数: {len(similar_patterns)}")
    logger.info(f"检测到的异常活动数: {len(abnormal_activities)}")
    logger.info(f"各地区登录频率: {login_frequencies}")

    # Item 20: 避免在循环结束后使用循环变量
    # 下面的循环变量不会在循环外被使用
    for last_used_index, _ in enumerate(logins):
        pass  # 只需获取最后一个索引值

    # 不会在这里使用循环变量

    # Item 19: 避免在 for/while 后使用 else 块
    # 使用更清晰的结构代替 else 块
    found_flag = False
    for login in logins:
        if login["device"] == "未知设备":
            found_flag = True
            break

    if found_flag:
        logger.warning("检测到包含未知设备的登录记录")
    else:
        logger.info("未检测到包含未知设备的登录记录")


if __name__ == "__main__":
    main()
