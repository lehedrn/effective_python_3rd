"""
本文件展示了 Python 中使用描述符（Descriptor）实现可复用的 `@property` 方法，涵盖以下内容：

- 使用 `@property` 实现属性验证（复用性差）
- 使用描述符实现属性验证（基础错误示例）
- 使用字典保存实例状态（存在内存泄漏问题）
- 使用 `__set_name__` 实现正确且安全的描述符（推荐做法）

每个示例都封装为独立函数，并在 main 函数中调用。
"""

import logging

# 设置日志配置
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def example_property_validation():
    """
    示例1：使用 @property 验证成绩属性
    说明：
        - 每个属性都需要重复编写 getter 和 setter
        - 无法跨类复用
    """

    class Homework:
        def __init__(self):
            self._grade = 0

        @property
        def grade(self):
            return self._grade

        @grade.setter
        def grade(self, value):
            if not (0 <= value <= 100):
                raise ValueError("Grade must be between 0 and 100")
            self._grade = value

    galileo = Homework()
    galileo.grade = 95
    logger.info(f"Example 1: Homework grade set to {galileo.grade}")


def example_bad_descriptor():
    """
    示例2：错误的描述符实现
    说明：
        - 描述符共享同一个 _value 状态
        - 多个实例之间会互相干扰
    """

    class Grade:
        def __init__(self):
            self._value = 0

        def __get__(self, instance, owner):
            return self._value

        def __set__(self, instance, value):
            if not (0 <= value <= 100):
                raise ValueError("Grade must be between 0 and 100")
            self._value = value

    class Exam:
        math_grade = Grade()
        writing_grade = Grade()

    first_exam = Exam()
    first_exam.writing_grade = 82
    first_exam.math_grade = 90
    logger.info(f"Bad Descriptor - First exam: writing={first_exam.writing_grade}, math={first_exam.math_grade}")

    second_exam = Exam()
    second_exam.writing_grade = 75
    logger.info(f"Bad Descriptor - Second exam: writing={second_exam.writing_grade}, first's writing={first_exam.writing_grade}")
    # 注意：此时 first_exam.writing_grade 已被修改为 75，说明状态共享了


def example_dict_descriptor():
    """
    示例3：使用字典存储实例状态的描述符
    说明：
        - 解决了多个实例之间的状态冲突
        - 存在内存泄漏风险（_values 字典持续持有实例引用）
    """

    class DictGrade:
        def __init__(self):
            self._values = {}

        def __get__(self, instance, owner):
            if instance is None:
                return self
            return self._values.get(instance, 0)

        def __set__(self, instance, value):
            if not (0 <= value <= 100):
                raise ValueError("Grade must be between 0 and 100")
            self._values[instance] = value

    class Exam:
        math_grade = DictGrade()
        writing_grade = DictGrade()

    first_exam = Exam()
    first_exam.writing_grade = 82
    first_exam.math_grade = 90
    logger.info(f"Dict Descriptor - First exam: writing={first_exam.writing_grade}, math={first_exam.math_grade}")

    second_exam = Exam()
    second_exam.writing_grade = 75
    logger.info(f"Dict Descriptor - Second exam: writing={second_exam.writing_grade}, first's writing={first_exam.writing_grade}")


def example_named_descriptor():
    """
    示例4：使用 __set_name__ 的正确描述符实现
    说明：
        - 每个实例拥有独立的状态
        - 数据存储在对象的 __dict__ 中
        - 不会造成内存泄漏
    """

    class NamedGrade:
        def __set_name__(self, owner, name):
            self.internal_name = "_" + name

        def __get__(self, instance, owner):
            if instance is None:
                return self
            return getattr(instance, self.internal_name)

        def __set__(self, instance, value):
            if not (0 <= value <= 100):
                raise ValueError("Grade must be between 0 and 100")
            setattr(instance, self.internal_name, value)

    class NamedExam:
        math_grade = NamedGrade()
        writing_grade = NamedGrade()
        science_grade = NamedGrade()

    first_exam = NamedExam()
    first_exam.math_grade = 78
    first_exam.writing_grade = 89
    first_exam.science_grade = 94
    logger.info(f"Named Descriptor - First exam dict: {first_exam.__dict__}")

    second_exam = NamedExam()
    second_exam.math_grade = 65
    logger.info(f"Named Descriptor - Second exam math grade: {second_exam.math_grade}")
    logger.info(f"Named Descriptor - First exam math grade: {first_exam.math_grade}")
    logger.info(f"Named Descriptor - First exam dict after changes: {first_exam.__dict__}")


def main():
    """主函数，运行所有示例"""
    logger.info("开始执行示例 1：使用 @property 验证属性")
    example_property_validation()

    logger.info("\n开始执行示例 2：错误的描述符实现")
    example_bad_descriptor()

    logger.info("\n开始执行示例 3：使用字典存储实例状态的描述符")
    example_dict_descriptor()

    logger.info("\n开始执行示例 4：使用 __set_name__ 的正确描述符实现")
    example_named_descriptor()


if __name__ == "__main__":
    main()
