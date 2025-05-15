# Chapter 4: Dictionaries (字典)

## Item 29: Compose Classes Instead of Deeply Nesting Dictionaries, Lists, and Tuples (使用类组合代替深层嵌套的字典、列表和元组)

Python’s built-in dictionary type is wonderful for maintaining dynamic internal state over the lifetime of an object. By dynamic, I mean situations in which you need to do bookkeeping for an unexpected set of identifiers. For example, say that I want to record the grades of a set of students whose names aren’t known in advance. I can define a class to store the names in a dictionary instead of using a predefined attribute for each student:

Python内置的字典类型在对象生命周期内维护动态内部状态时非常出色。所谓动态，指的是需要为一组不可预知的标识符进行簿记的情况。例如，假设我想记录一组学生（其名字是未知的）的成绩。我可以定义一个类将这些名字存储在一个字典中，而不是为每个学生使用预定义属性：

```
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
```

Using the class is simple:

使用这个类很简单：

```
book = SimpleGradebook()
book.add_student("Isaac Newton")
book.report_grade("Isaac Newton", 90)
book.report_grade("Isaac Newton", 95)
book.report_grade("Isaac Newton", 85)

print(book.average_grade("Isaac Newton"))
>>>
90.0
```

Dictionaries, lists, tuples, and sets are so easy to use that there’s a danger they’ll cause you to write brittle code. For example, say that I want to extend the `SimpleGradebook` class to keep a `list` of grades by subject, not just overall. I can do this by changing the `_grades` dictionary to map student names (its keys) to yet another dictionary (its values). The innermost dictionary will map subjects (its keys) to a `list` of grades (its values). Here, I do this by using a `defaultdict` instance for the inner dictionary to handle missing subjects (see Item 27: “Prefer `defaultdict` Over `setdefault` to Handle Missing Items in Internal State” for background):

字典、列表、元组和集合之所以易于使用，是因为它们很容易导致你编写出脆弱的代码。例如，假设我想要扩展`SimpleGradebook`类以按学科记录成绩，而不仅仅是整体成绩。我可以通过更改`_grades`字典来实现这一点，使其将学生姓名（键）映射到另一个字典（值）。最内层的字典将把学科（键）映射到成绩列表（值）。在这里，我通过为内层字典使用`defaultdict`实例来处理内部状态中的缺失项（请参见条目27）：

```
from collections import defaultdict
class BySubjectGradebook:
    def __init__(self):
        self._grades = {}                       # Outer dict

    def add_student(self, name):
        self._grades[name] = defaultdict(list)  # Inner dict

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
```

This is straightforward enough. The `report_grade` and `average_grade` methods gained quite a bit of complexity to deal with the multilevel dictionary, but it’s seemingly manageable. Using the class remains simple:

这已经足够简单了。`report_grade`和`average_grade`方法为了处理多级字典增加了很多复杂性，但看起来还是可以管理的。使用该类仍然很简单：

```
book = BySubjectGradebook()
book.add_student("Albert Einstein")
book.report_grade("Albert Einstein", "Math", 75)
book.report_grade("Albert Einstein", "Math", 65)
book.report_grade("Albert Einstein", "Gym", 90)
book.report_grade("Albert Einstein", "Gym", 95)
print(book.average_grade("Albert Einstein"))
>>>
81.25
```

Now, imagine that the requirements change again. I also want to track the weight of each score toward the overall grade in the class so that midterm and final exams are more important than pop quizzes. One way to implement this feature is to change the innermost dictionary; instead of mapping subjects (its keys) to a `list` of grades (its values), I can use a `tuple` of `(score, weight)` in the values `list` . Although the changes to `report_grade` seem simple—just make the `grade_list` store `tuple` instances—the `average_grade` method now has a loop within a loop and is difficult to read:

现在，想象一下需求再次改变。我还想跟踪每项得分在整个课程成绩中的权重，这样期中考试和期末考试比突击小测验更重要。实现此功能的一种方法是更改最内层的字典；与其让学科（键）映射到成绩列表（值），不如在值列表中使用包含`(score, weight)`的元组。虽然对`report_grade`的修改看似简单——只需让`grade_list`存储元组实例——但`average_grade`方法现在有一个循环嵌套循环，难以阅读：

```
class WeightedGradebook:
    def __init__(self):
        self._grades = {}

    def add_student(self, name):
        self._grades[name] = defaultdict(list)

    def report_grade(self, name, subject, score, weight):
        by_subject = self._grades[name]
        grade_list = by_subject[subject]
        grade_list.append((score, weight))    # Changed

    def average_grade(self, name):
        by_subject = self._grades[name]

        score_sum, score_count = 0, 0
        for scores in by_subject.values():
            subject_avg, total_weight = 0, 0
            for score, weight in scores:      # Added inner loop
                subject_avg += score * weight
                total_weight += weight

            score_sum += subject_avg / total_weight
            score_count += 1

        return score_sum / score_count
```

Using the class has also gotten more difficult. It’s unclear what all of the numbers in the positional arguments mean:

使用此类也变得更加困难。不清楚位置参数中的所有数字代表什么：

```
book = WeightedGradebook()
book.add_student("Albert Einstein")
book.report_grade("Albert Einstein", "Math", 75, 0.05)
book.report_grade("Albert Einstein", "Math", 65, 0.15)
book.report_grade("Albert Einstein", "Math", 70, 0.80)
book.report_grade("Albert Einstein", "Gym", 100, 0.40)
book.report_grade("Albert Einstein", "Gym", 85, 0.60)
print(book.average_grade("Albert Einstein"))

>>>
80.25
```

When you see complexity like this, it’s time to make the leap from built-in types like dictionaries, lists, tuples, and sets to a hierarchy of classes.

当你看到这样的复杂度时，就该从字典、列表、元组和集合等内置类型转向类层次结构了。

In the grades example, at first I didn’t know I’d need to support weighted grades, so the complexity of creating other classes seemed unwarranted. Python’s built-in dictionary and `tuple` types made it easy to keep going, adding layer after layer to the internal bookkeeping. But you should avoid doing this for more than one level of nesting; using dictionaries that contain dictionaries makes your code hard to read by other programmers and sets you up for a maintenance nightmare (see Item 9: “Consider `match` for Destructuring in Flow Control, Avoid When `if` Statements Are Sufficient” for another way to deal with this).

在成绩示例中，起初我不知道我需要支持加权成绩，因此创建其他类的复杂性似乎不必要。Python的内置字典和`tuple`类型使我可以轻松地继续下去，在内部簿记中添加一层又一层。但是你应该避免对此类嵌套超过一级；使用包含字典的字典会使你的代码难以被其他程序员阅读，并为你设置了一个维护噩梦（另请参见条目9）。

As soon as you realize that your bookkeeping is getting complicated, break it all out into classes. You can then provide well-defined interfaces that better encapsulate your data. This approach also enables you to create a layer of abstraction between your interfaces and your concrete implementations.

一旦意识到簿记变得复杂，就应该将其全部拆分为类。然后你可以提供更好地封装数据的明确定义的接口。这种方法还使你能够在接口和具体实现之间创建抽象层。

**Refactoring to Classes**

**重构为类**

There are many approaches to refactoring (see Item 123: “Consider `warnings` to Refactor and Migrate Usage” for another). In this case, I can start moving to classes at the bottom of the dependency tree: a single grade. A class seems too heavyweight for such simple information. A `tuple` , though, seems appropriate because grades are immutable. Here, I use a `tuple` of `(score, weight)` to track grades in a list:

有多种方法可以重构（另请参见条目123）。在这种情况下，我可以从依赖树底部开始移至类：单个成绩。对于如此简单的信息，类似乎过于重量级。由于成绩是不可变的，因此使用`tuple`似乎是合适的。这里，我使用包含`(score, weight)`的`tuple`来追踪列表中的成绩：

```
grades = []
grades.append((95, 0.45))
grades.append((85, 0.55))
total = sum(score * weight for score, weight in grades)
total_weight = sum(weight for _, weight in grades)
average_grade = total / total_weight
print(average_grade)
```

I used `_` (the underscore variable name, a Python convention for unused variables) to capture the first entry in each grade’s `tuple` and ignore it when calculating the `total_weight` .

我使用了`_`（下划线变量名，这是Python中用于未使用的变量的约定）来捕获每个成绩`tuple`的第一个条目并在计算`total_weight`时忽略它。

The problem with this code is that `tuple` instances are positional. For example, if I want to associate more information with a grade, such as a set of notes from the teacher, I need to rewrite every usage of the two-tuple to be aware that there are now three items present instead of two, which means I need to use `_` further to ignore certain indexes:

这段代码的问题在于`tuple`实例是基于位置的。例如，如果我想关联更多信息与成绩，比如教师的评语，我需要重写每一个两元组的用法，以意识到现在存在三个项目而不是两个，这意味着我需要用更多的`_`来忽略某些索引：

```
grades = []
grades.append((95, 0.45, "Great job"))
grades.append((85, 0.55, "Better next time"))
total = sum(score * weight for score, weight, _ in grades)
total_weight = sum(weight for _, weight, _ in grades)
average_grade = total / total_weight
```

This pattern of extending tuples longer and longer is similar to deepening layers of dictionaries. As soon as you find yourself going longer than a two￾tuple, it’s time to consider another approach. The `dataclasses` built-in module does exactly what I need in this case: It lets me easily define a small immutable class for storing values in attributes (see Item 56: “Prefer `dataclasses` for Creating Immutable Objects”):

这种将元组扩展得越来越长的模式类似于加深字典层级。一旦发现自己使用超过二元组，就该考虑另一种方法了。在这种情况下，`dataclasses`标准库正好能满足我的需求：它让我轻松定义一个小而不可变的类，用于存储属性值（另请参见条目56）：

```
from dataclasses import dataclass
@dataclass(frozen=True)
class Grade:
    score: int
    weight: float
```

Next, I can write a class to represent a single subject that contains a set of `Grade` instances:

接下来，我可以编写一个类来表示包含一组`Grade`实例的单个科目：

```
class Subject:
    def __init__(self):
        self._grades = []

    def report_grade(self, score, weight):
        self._grades.append(Grade(score, weight))

    def average_grade(self):
        total, total_weight = 0, 0
        for grade in self._grades:
            total += grade.score * grade.weight
            total_weight += grade.weight
        return total / total_weight
```

Then, I write a class to hold the set of subjects that are being studied by a single student:

然后，我编写一个类来保存单个学生正在学习的所有科目的集合：

```
class Student:
    def __init__(self):
        self._subjects = defaultdict(Subject)

    def get_subject(self, name):
        return self._subjects[name]

    def average_grade(self):
        total, count = 0, 0
        for subject in self._subjects.values():
            total += subject.average_grade()
            count += 1
        return total / count
```

Finally, I’d write a container for all of the students, keyed dynamically by their names:

最后，我编写一个容器来保存所有学生，根据他们的名字动态键入：

```
class Gradebook:
    def __init__(self):
        self._students = defaultdict(Student)
    def get_student(self, name):
        return self._students[name]
```

The line count of these classes is almost double the previous implementation’s size. But this code is much easier to read. The example driving the classes is also more clear and extensible:

这些类的代码行数几乎是前一实现的两倍。但这段代码更易于阅读。驱动这些类的示例也更加清晰且可扩展：

```
book = Gradebook()
albert = book.get_student("Albert Einstein")
math = albert.get_subject("Math")
math.report_grade(75, 0.05)
math.report_grade(65, 0.15)
math.report_grade(70, 0.80)
gym = albert.get_subject("Gym")
gym.report_grade(100, 0.40)
gym.report_grade(85, 0.60)
print(albert.average_grade())
>>>
80.25
```

It would also be possible to write backward-compatible methods to help migrate usage of the old API style to the new hierarchy of objects.

同样也可以编写向后兼容的方法，帮助迁移旧API风格的使用到新的对象层次结构。

**Things to Remember**
- Avoid making dictionaries with values that are dictionaries, long tuples, or complex nestings of other built-in types.
- Use the `dataclasses` built-in module for lightweight, immutable data containers before you need the flexibility of a full class.
- Move your bookkeeping code to using multiple classes when your internal state dictionaries get complicated.

**注意事项**
- 避免创建值为字典、长元组或复杂嵌套的其他内置类型的字典。
- 在需要完整类的灵活性之前，使用`dataclasses`标准库作为轻量级、不可变的数据容器。
- 当你的内部状态字典变得复杂时，将簿记代码转移到多个类中使用。