"""
本文件展示了如何使用 `pickle` 和 `copyreg` 模块来实现可维护的序列化和反序列化。
示例包括错误用法和正确用法，覆盖文档中提到的所有要点：
1. 使用 `pickle` 序列化和反序列化对象。
2. 处理类属性的添加和删除。
3. 使用 `copyreg` 实现向后兼容。
4. 处理类重命名问题。
5. 遵循 PEP8 规范，使用 logging 替代 print。
"""

import pickle
import copyreg
import logging

# 配置日志记录
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


# 定义不同版本的 GameState 类，避免嵌套在函数中
class GameStateV1:
    def __init__(self):
        self.level = 0
        self.lives = 4


class GameStateV2:
    def __init__(self):
        self.level = 0
        self.lives = 4
        self.points = 0


class GameStateV3:
    def __init__(self, level=0, lives=4, points=0):
        self.level = level
        self.lives = lives
        self.points = points


class GameStateV4Old:
    def __init__(self, level=0, lives=4, points=0, magic=5):
        self.level = level
        self.lives = lives
        self.points = points
        self.magic = magic


class GameStateV4New:
    def __init__(self, level=0, points=0, magic=5):
        self.level = level
        self.points = points
        self.magic = magic


class GameStateV5Old:
    def __init__(self, level=0, points=0, magic=5):
        self.level = level
        self.points = points
        self.magic = magic


class GameStateV5New:
    def __init__(self, level=0, points=0, magic=5):
        self.level = level
        self.points = points
        self.magic = magic


# 全局函数：用于 copyreg 注册
def unpickle_game_state(kwargs):
    return GameStateV3(**kwargs)


def pickle_game_state(game_state):
    kwargs = game_state.__dict__
    return unpickle_game_state, (kwargs,)

def pickle_game_state_v4(game_state):
    kwargs = game_state.__dict__
    kwargs["version"] = 2
    return unpickle_game_state_v4, (kwargs,)

def unpickle_game_state_v4(kwargs):
    version = kwargs.pop("version", 1)
    if version == 1:
        del kwargs["lives"]
    return GameStateV4New(**kwargs)
def pickle_game_state_v5(game_state):
    kwargs = game_state.__dict__
    return unpickle_game_state_v5, (kwargs,)

def unpickle_game_state_v5(kwargs):
    return GameStateV5New(**kwargs)

# 示例函数

def example_1_basic_pickle_usage():
    state = GameStateV1()
    state.level += 1
    state.lives -= 1

    serialized = pickle.dumps(state)
    state_after = pickle.loads(serialized)

    logging.info("示例 1: 反序列化后的对象属性: %s", state_after.__dict__)


def example_2_pickle_with_missing_attributes():
    # 使用旧版本类序列化
    state_v1 = GameStateV1()
    serialized = pickle.dumps(state_v1)

    try:
        state_v2 = pickle.loads(serialized)
        logging.warning("示例 2: 反序列化成功但缺少新属性: %s", state_v2.__dict__)
    except Exception as e:
        logging.error("示例 2: 反序列化失败: %s", str(e))


def example_3_copyreg_for_default_attributes():
    copyreg.pickle(GameStateV3, pickle_game_state)

    state = GameStateV3()
    state.points += 1000

    serialized = pickle.dumps(state)
    state_after = pickle.loads(serialized)

    logging.info("示例 3: 新增属性具有默认值: %s", state_after.__dict__)


def example_4_handling_removed_attributes():

    copyreg.pickle(GameStateV4New, pickle_game_state_v4)

    state_old = GameStateV4Old(level=1, lives=3, points=100)
    serialized = pickle.dumps(state_old)

    state_new = pickle.loads(serialized)
    logging.info("示例 4: 删除旧属性: %s", state_new.__dict__)


def example_5_stable_import_paths():

    # 明确声明我们要使用的是全局变量
    global GameStateV5Old
    copyreg.pickle(GameStateV5Old, pickle_game_state_v5)

    # 使用旧类序列化
    state_old = GameStateV5Old(level=1, points=100, magic=3)
    serialized = pickle.dumps(state_old)

    # 删除旧类模拟重构
    del GameStateV5Old

    # 使用新类反序列化
    state_new = pickle.loads(serialized)

    logging.info("示例 5: 类重命名后仍正常工作: %s", state_new.__dict__)


def main():
    logging.info("运行示例 1: 基本的 `pickle` 用法")
    example_1_basic_pickle_usage()

    logging.info("\n运行示例 2: 当类属性发生变化时的默认行为")
    example_2_pickle_with_missing_attributes()

    logging.info("\n运行示例 3: 使用 `copyreg` 确保默认属性值")
    example_3_copyreg_for_default_attributes()

    logging.info("\n运行示例 4: 使用 `copyreg` 处理删除的属性")
    example_4_handling_removed_attributes()

    logging.info("\n运行示例 5: 使用 `copyreg` 确保稳定的导入路径")
    example_5_stable_import_paths()


if __name__ == "__main__":
    main()
