"""
本文件演示了如何使用类组合代替深层嵌套的字典、列表和元组。文档中提到了多个示例，包括：
1. 使用字典维护动态状态（SimpleGradebook）。
2. 深层嵌套的字典结构（BySubjectGradebook）。
3. 添加权重支持的复杂嵌套（WeightedGradebook）。
4. 使用类层次结构重构代码以提高可读性和可维护性。

每个示例都包含错误示例（基于内置类型嵌套实现）和正确示例（使用类组合实现），并附有完整的中文解释。
"""

import logging
from collections import defaultdict
from dataclasses import dataclass

# 设置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# 示例 1: SimpleGradebook - 基于字典维护学生整体成绩
class SimpleGradebook:
    def __init__(self):
        self._grades = {}

    def add_student(self, name):
        self._grades[name] = []

    def report_grade(self, name, score):
        self._grades[name].append(score)

    def average_grade(self, name):
        grades = self._grades[name]
        return sum(grades) / len(grades)


def example_simple_gradebook():
    """错误示例：使用简单字典存储学生整体成绩"""
    logging.info("示例 1: 错误示例 - 使用 SimpleGradebook 记录学生成绩")
    book = SimpleGradebook()
    book.add_student("Isaac Newton")
    book.report_grade("Isaac Newton", 90)
    book.report_grade("Isaac Newton", 95)
    book.report_grade("Isaac Newton", 85)
    logging.info(f"Isaac Newton 的平均成绩为: {book.average_grade('Isaac Newton')}")  # 应输出 90.0


# 示例 2: BySubjectGradebook - 支持按学科记录成绩
class BySubjectGradebook:
    def __init__(self):
        self._grades = {}  # 外层字典，键是学生姓名

    def add_student(self, name):
        self._grades[name] = defaultdict(list)  # 内层字典，键是科目

    def report_grade(self, name, subject, grade):
        by_subject = self._grades[name]
        grade_list = by_subject[subject]
        grade_list.append(grade)

    def average_grade(self, name):
        by_subject = self._grades[name]
        total, count = 0, 0
        for grades in by_subject.values():
            total += sum(grades)
            count += len(grades)
        return total / count


def example_by_subject_gradebook():
    """错误示例：使用多级嵌套字典来按学科记录成绩"""
    logging.info("示例 2: 错误示例 - 使用 BySubjectGradebook 按学科记录成绩")
    book = BySubjectGradebook()
    book.add_student("Albert Einstein")
    book.report_grade("Albert Einstein", "Math", 75)
    book.report_grade("Albert Einstein", "Math", 65)
    book.report_grade("Albert Einstein", "Gym", 90)
    book.report_grade("Albert Einstein", "Gym", 95)
    logging.info(f"Albert Einstein 的平均成绩为: {book.average_grade('Albert Einstein')}")  # 应输出 81.25


# 示例 3: WeightedGradebook - 支持加权成绩
class WeightedGradebook:
    def __init__(self):
        self._grades = {}

    def add_student(self, name):
        self._grades[name] = defaultdict(list)

    def report_grade(self, name, subject, score, weight):
        by_subject = self._grades[name]
        grade_list = by_subject[subject]
        grade_list.append((score, weight))  # 存储 (score, weight)

    def average_grade(self, name):
        by_subject = self._grades[name]

        score_sum, score_count = 0, 0
        for scores in by_subject.values():
            subject_avg, total_weight = 0, 0
            for score, weight in scores:
                subject_avg += score * weight
                total_weight += weight

            score_sum += subject_avg / total_weight
            score_count += 1

        return score_sum / score_count


def example_weighted_gradebook():
    """错误示例：使用 tuple 来存储带权重的成绩"""
    logging.info("示例 3: 错误示例 - 使用 WeightedGradebook 记录带权重的成绩")
    book = WeightedGradebook()
    book.add_student("Albert Einstein")
    book.report_grade("Albert Einstein", "Math", 75, 0.05)
    book.report_grade("Albert Einstein", "Math", 65, 0.15)
    book.report_grade("Albert Einstein", "Math", 70, 0.80)
    book.report_grade("Albert Einstein", "Gym", 100, 0.40)
    book.report_grade("Albert Einstein", "Gym", 85, 0.60)
    logging.info(f"Albert Einstein 的加权平均成绩为: {book.average_grade('Albert Einstein')}")  # 应输出 80.25


# 示例 4: 使用类组合重构 Grade、Subject、Student 和 Gradebook 类
@dataclass(frozen=True)
class Grade:
    """不可变的数据容器，用于表示单个成绩项（分数和权重）"""
    score: int
    weight: float


class Subject:
    """表示一个学科，包含一组 Grade 实例"""
    def __init__(self):
        self._grades = []

    def report_grade(self, score, weight):
        self._grades.append(Grade(score, weight))

    def average_grade(self):
        total, total_weight = 0, 0
        for grade in self._grades:
            total += grade.score * grade.weight
            total_weight += grade.weight
        return total / total_weight if total_weight else 0


class Student:
    """表示一个学生，包含多个学科"""
    def __init__(self):
        self._subjects = defaultdict(Subject)

    def get_subject(self, name):
        return self._subjects[name]

    def average_grade(self):
        total, count = 0, 0
        for subject in self._subjects.values():
            total += subject.average_grade()
            count += 1
        return total / count if count else 0


class Gradebook:
    """表示所有学生的成绩簿，通过名字动态索引"""
    def __init__(self):
        self._students = defaultdict(Student)

    def get_student(self, name):
        return self._students[name]


def example_refactored_gradebook():
    """正确示例：使用类组合重构代码"""
    logging.info("示例 4: 正确示例 - 使用类组合重构 Grade、Subject、Student 和 Gradebook")
    book = Gradebook()
    albert = book.get_student("Albert Einstein")
    math = albert.get_subject("Math")
    math.report_grade(75, 0.05)
    math.report_grade(65, 0.15)
    math.report_grade(70, 0.80)
    gym = albert.get_subject("Gym")
    gym.report_grade(100, 0.40)
    gym.report_grade(85, 0.60)
    logging.info(f"Albert Einstein 的平均成绩为: {albert.average_grade()}")  # 应输出 80.25


# 主函数运行完整示例
def main():
    example_simple_gradebook()
    example_by_subject_gradebook()
    example_weighted_gradebook()
    example_refactored_gradebook()


if __name__ == "__main__":
    main()
