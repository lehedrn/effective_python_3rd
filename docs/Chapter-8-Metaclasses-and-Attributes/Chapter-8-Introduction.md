# Chapter 8: Metaclasses and Attributes (元类和属性)

Metaclasses are often mentioned in lists of Python’s unique features, but few understand what they accomplish in practice. The name metaclass vaguely implies a concept above and beyond a class. Simply put, metaclasses let you intercept Python’s `class` statement and provide special behavior each time a class is defined.

元类经常出现在 Python 独特功能的列表中，但很少有人真正理解它们在实际中的作用。元类这个名字模糊地暗示了一个超越类的概念。简单来说，元类允许你在每次定义类时拦截 Python 的 class 语句并提供特殊的行为。

Similarly mysterious are Python’s built-in features for dynamically customizing attribute accesses. Along with Python’s object-oriented constructs, these facilities provide powerful tools to ease the transition from simple classes to complex ones.

同样神秘的是 Python 中动态自定义属性访问的内置特性。与 Python 的面向对象结构一起，这些功能提供了强大的工具，可以轻松实现从简单类到复杂类的过渡。

However, with these capabilities come many pitfalls. Dynamic attributes enable you to override objects and cause unexpected side effects. Metaclasses can create extremely bizarre behaviors that are unapproachable to newcomers. It’s important that you follow the rule of least surprise and only use these mechanisms to implement well-understood idioms.

然而，这些能力也带来了很多陷阱。动态属性使你可以覆盖对象并导致意外的副作用。元类可能会产生极其奇怪的行为，这对新手来说是难以理解和接触的。遵循最小意外规则，并且仅使用这些机制来实现被广泛理解的习惯用法是非常重要的。

1. [Item 58: Use Plain Attributes Instead of Setter and Getter Methods](Chapter-8-Item-58.md) 使用普通属性代替设置器和获取器方法
2. [Item 59: Consider @property Instead of Refactoring Attributes](Chapter-8-Item-59.md) 考虑使用 @property 而不是重构属性
3. [Item 60: Use Descriptors for Reusable @property Methods](Chapter-8-Item-60.md) 对可重用的 @property 方法使用描述符
4. [Item 61: Use __getattr__, __getattribute__, and __setattr__ for Lazy Attributes](Chapter-8-Item-61.md) 使用 getattr、getattribute 和 setattr 实现延迟属性
5. [Item 62: Validate Subclasses with __init_subclass__](Chapter-8-Item-62.md) 使用 init_subclass 验证子类
6. [Item 63: Register Class Existence with __init_subclass__](Chapter-8-Item-63.md) 使用 init_subclass 注册类的存在
7. [Item 64: Annotate Class Attributes with __set_name__](Chapter-8-Item-64.md) 使用 set_name 注解类属性
8. [Item 65: Consider Class Body Definition Order to Establish Relationships Between Attributes](Chapter-8-Item-65.md) 考虑类主体定义顺序以建立属性之间的关系
9. [Item 66: Prefer Class Decorators over Metaclasses for Composable Class Extensions](Chapter-8-Item-66.md) 优先使用类装饰器而不是元类进行可组合的类扩展






