# Chapter 7: Classes and Interfaces (类与接口)

As an object-oriented programming language, Python supports a full range of features, such as inheritance, polymorphism, and encapsulation. Getting things done in Python often requires writing new classes and defining how they interact through their interfaces and relationships.

作为一门面向对象的编程语言，Python 支持全面的功能，如继承、多态和封装。在 Python 中完成任务通常需要编写新的类，并定义它们如何通过接口和关系进行交互。

Classes and inheritance make it easy to express a Python program’s intended behaviors with objects. They allow you to improve and expand functionality over time. They provide flexibility in an environment of changing requirements. Knowing how to use them well enables you to write maintainable code.

类和继承使得用对象表达 Python 程序的预期行为变得容易。它们允许您随时间推移改进和扩展功能。它们在一个需求不断变化的环境中提供了灵活性。了解如何很好地使用它们可以使您编写出可维护的代码。

Python is also a multi-paradigm language that encourages functional-style programming. Function objects are first-class, meaning they can be passed around like normal variables. Python also allows you use a mix object-oriented-style and functional-style features in the same program, which can be even more powerful than each style on its own.

Python 同样是一种多范式语言，鼓励函数式编程。函数对象是一等公民，意味着它们可以像普通变量一样被传递。Python 也允许您在同一程序中混合使用面向对象风格和函数式风格特性，这比单独使用每种风格更加强大。

1. [Item 48: Accept Functions Instead of Classes for Simple Interfaces](Chapter-7-Item-48.md) 对于简单接口，接受函数而不是类
2. [Item 49: Prefer Object-Oriented Polymorphism over Functions with isinstance Checks](Chapter-7-Item-49.md) 优先使用面向对象的多态而不是使用 isinstance 检查的函数
3. [Item 50: Consider functools.singledispatch for Functional-Style Programming Instead of Object-Oriented Polymorphism](Chapter-7-Item-50.md) 考虑使用 functools.singledispatch 进行函数式编程而不是面向对象的多态
4. [Item 51: Prefer dataclasses for Defining Lightweight Classes](Chapter-7-Item-51.md) 优先使用 dataclasses 定义轻量级类
5. [Item 52: Use @classmethod Polymorphism to Construct Objects Generically](Chapter-7-Item-52.md) 使用 @classmethod 多态以通用方式构造对象
6. [Item 53: Initialize Parent Classes with super](Chapter-7-Item-53.md) 使用 super 初始化父类
7. [Item 54: Consider Composing Functionality with Mix-in Classes](Chapter-7-Item-54.md) 考虑使用 Mix-in 类组合功能
8. [Item 55: Prefer Public Attributes over Private Ones](Chapter-7-Item-55.md) 优先使用公共属性而不是私有属性
9. [Item 56: Prefer dataclasses for Creating Immutable Objects](Chapter-7-Item-56.md) 优先使用 dataclasses 创建不可变对象
10. [Item 57: Inherit from collections.abc Classes for Custom Container Types](Chapter-7-Item-57.md) 为自定义容器类型继承 collections.abc 类
