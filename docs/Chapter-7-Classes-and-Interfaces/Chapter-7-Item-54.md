# Chapter 7: Classes and Interfaces (类与接口)

## Item 54: Consider Composing Functionality with Mix-in Classes (考虑使用混入类（Mix-in）来组合功能)

Python is an object-oriented language with built-in facilities for making multiple inheritance tractable (see Item 53: “Initialize Parent Classes with super ”). However, it’s better to avoid multiple inheritance altogether.

Python 是一种面向对象的语言，内置了使多重继承易于管理的设施（参见条目53：“使用 super 初始化父类”）。然而，最好完全避免使用多重继承。

If you find yourself desiring the convenience and encapsulation that come with multiple inheritance, but want to avoid the potential headaches, consider writing a mix-in instead. A mix-in is a class that defines only a small set of additional methods for its child classes to provide. Mix-in classes don’t define their own instance attributes nor require their `__init__` constructor to be called.

如果你发现自己想要获得多重继承带来的便利和封装特性，但又想避免潜在的问题，可以考虑编写一个混入类（mix-in）。混入类仅为其子类提供一小部分额外的方法定义。混入类不定义自己的实例属性，也不要求调用其 `__init__` 构造函数。

Writing mix-ins is easy because Python makes it trivial to inspect the current state of any object, regardless of its type. Dynamic inspection means you can write generic functionality just once, in a mix-in, and it can then be applied to many other classes. Mix-ins can be composed and layered to minimize repetitive code and maximize reuse.

编写混入类很容易，因为 Python 使得检查任何对象的当前状态变得简单，无论其类型如何。动态检查意味着你可以只编写一次通用的功能，在混入类中实现，然后将其应用于许多其他类。混入类可以组合和分层使用，以最小化重复代码并最大化重用性。

For example, say I want the ability to convert a Python object from its in￾memory representation to a dictionary that’s ready for serialization. Why not write this functionality generically so I can use it with all of my classes?

例如，假设我想要将内存中的 Python 对象转换为可序列化的字典表示形式。为什么不以通用的方式编写此功能，以便在所有类中使用呢？

Here, I define an example mix-in that accomplishes this with a new public method that’s added to any class that inherits from it. The implementation details are straightforward and rely on dynamic attribute access using `hasattr` , dynamic type inspection with `isinstance` , and accessing the instance dictionary `__dict__` :

以下是一个实现该功能的混入类示例，它通过新增一个公共方法添加到任何继承自它的类中。实现细节非常直接，依赖于使用 `hasattr` 进行动态属性访问、使用 `isinstance` 进行动态类型检查以及访问实例字典 `__dict__`：

```
class ToDictMixin:
    def to_dict(self):
        return self._traverse_dict(self.__dict__)

    def _traverse_dict(self, instance_dict):
        output = {}
        for key, value in instance_dict.items():
            output[key] = self._traverse(key, value)
        return output

    def _traverse(self, key, value):
        if isinstance(value, ToDictMixin):
            return value.to_dict()
        elif isinstance(value, dict):
            return self._traverse_dict(value)
        elif isinstance(value, list):
            return [self._traverse(key, i) for i in value]
        elif hasattr(value, "__dict__"):
            return self._traverse_dict(value.__dict__)
        else:
            return value
```

Here, I define an example class that uses the mix-in to make a dictionary representation of a binary tree:

这里定义了一个使用混入类的示例类，用于生成二叉树的字典表示：

```
class BinaryTree(ToDictMixin):
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right
```

Translating a large number of related Python objects into a dictionary becomes easy:

将大量相关的 Python 对象转换为字典变得轻而易举：

```
tree = BinaryTree(
    10,
    left=BinaryTree(7, right=BinaryTree(9)),
    right=BinaryTree(13, left=BinaryTree(11)),
)
print(tree.to_dict())

>>>
{'value': 10, 'left': {'value': 7, 'left': None, 'right': {'value': 9, 'left': None, 'right': None}}, 'right': {'value': 13, 'left': {'value': 11, 'left': None, 'right': None}, 'right': None}}
```

The best part about mix-ins is that you can make their generic functionality pluggable so behaviors can be overridden when required. For example, here I define a subclass of `BinaryTree` that holds a reference to its parent. This circular reference would cause the default implementation of `ToDictMixin.to_dict` to loop forever. The solution is to override the `BinaryTreeWithParent._traverse` method to only process values that matter, preventing cycles encountered by the mix-in. Here, the _`traverse` override inserts the parent’s numerical value, and otherwise defers to the mix-in’s default implementation by using the `super` built-in function:

混入类最好的一点是，你可以让它们的通用功能可插拔，以便在需要时覆盖行为。例如，下面定义了一个 `BinaryTree` 的子类，它持有对其父节点的引用。这种循环引用会导致默认实现的 `ToDictMixin.to_dict` 永远循环下去。解决办法是重写 `BinaryTreeWithParent._traverse` 方法，只处理重要的值，从而防止混入类遇到的循环。在这里，`_traverse` 覆盖插入了父节点的数值，并且否则会使用 `super` 内置函数延迟到混入类的默认实现：

```
class BinaryTreeWithParent(BinaryTree):
    def __init__(
        self,
        value,
        left=None,
        right=None,
        parent=None,
    ):
        super().__init__(value, left=left, right=right)
        self.parent = parent

    def _traverse(self, key, value):
        if (
            isinstance(value, BinaryTreeWithParent)
            and key == "parent"
        ):
            return value.value  # Prevent cycles
        else:
            return super()._traverse(key, value)
```

Calling `BinaryTreeWithParent.to_dict` works without issue because the circular referencing properties aren’t followed:

调用 `BinaryTreeWithParent.to_dict` 可以正常工作，因为循环引用属性没有被跟踪：

```
root = BinaryTreeWithParent(10)
root.left = BinaryTreeWithParent(7, parent=root)
root.left.right = BinaryTreeWithParent(9, parent=root.left)
print(root.to_dict())
>>>
{'value': 10, 'left': {'value': 7, 'left': None, 'right': {'value': 9, 'left': None, 'right': None, 'parent': 7}, 'parent': 10}, 'right': None, 'parent': None}
```

By defining `BinaryTreeWithParent._traverse` , I’ve also enabled any class that has an attribute of type `BinaryTreeWithParent` to automatically work with the ToDictMixin :

通过定义 `BinaryTreeWithParent._traverse` ，我还启用了任何具有 `BinaryTreeWithParent` 类型属性的类自动与 ToDictMixin 一起工作：

```
class NamedSubTree(ToDictMixin):
    def __init__(self, name, tree_with_parent):
        self.name = name
        self.tree_with_parent = tree_with_parent

my_tree = NamedSubTree("foobar", root.left.right)
orig_print = print
print = pprint
print(my_tree.to_dict())  # No infinite loop
print = orig_print

>>>
{'name': 'foobar', 'tree_with_parent': {'value': 9, 'left': None, 'right': None, 'parent': 7}}
```

Mix-ins can also be composed together. For example, say I want a mix-in that provides generic JSON serialization for any class. I can do this by assuming that a class provides a `to_dict` method (which may or may not be provided by the `ToDictMixin` class):

混入类也可以组合在一起使用。例如，假设我想编写一个为任何类提供通用 JSON 序列化的混入类。可以通过假定类提供 `to_dict` 方法来实现这一点（这个方法可能由 `ToDictMixin` 类提供，也可能不提供）：

```
import json

class JsonMixin:
    @classmethod
    def from_json(cls, data):
        kwargs = json.loads(data)
        return cls(**kwargs)

    def to_json(self):
        return json.dumps(self.to_dict())
```

Note how the `JsonMixin` class defines both instance methods and class methods. Mix-ins let you add either kind of behavior to subclasses (see Item 52: “Use @classmethod Polymorphism to Construct Objects Generically” for similar functionality). In this example, the only requirements of a `JsonMixin` subclass are providing a `to_dict` method and taking keyword arguments for the `__init__` method (see Item 35: “Provide Optional Behavior with Keyword Arguments” for background).

请注意 `JsonMixin` 类是如何定义实例方法和类方法的。混入类允许你向子类添加任意种类的行为（有关类似功能，请参见条目52：“使用 @classmethod 多态构造对象”）。在这个例子中，`JsonMixin` 子类的唯一要求是提供 `to_dict` 方法，并且其 `__init__` 方法接受关键字参数（有关背景信息，请参见条目35：“使用关键字参数提供可选行为”）。

This mix-in makes it simple to create hierarchies of utility classes that can be serialized to and from JSON with little boilerplate. For example, here I have a hierarchy of classes representing parts of a datacenter topology:

这个混入类使得创建能够轻松序列化和反序列化为 JSON 的工具类层次结构变得简单，几乎不需要样板代码。例如，我有一个代表数据中心拓扑结构的部分类层次结构：

```
class DatacenterRack(ToDictMixin, JsonMixin):
    def __init__(self, switch=None, machines=None):
        self.switch = Switch(**switch)
        self.machines = [
            Machine(**kwargs) for kwargs in machines]

class Switch(ToDictMixin, JsonMixin):
    def __init__(self, ports=None, speed=None):
        self.ports = ports
        self.speed = speed

class Machine(ToDictMixin, JsonMixin):
    def __init__(self, cores=None, ram=None, disk=None):
        self.cores = cores
        self.ram = ram
        self.disk = disk
```

Serializing these classes to and from JSON is simple. Here, I verify that the data is able to be sent round-trip through serializing and deserializing:

将这些类序列化为 JSON 并反序列化回来很简单。在这里，我验证了数据能够在序列化和反序列化过程中往返传输：

```
serialized = """{
    "switch": {"ports": 5, "speed": 1e9},
    "machines": [
        {"cores": 8, "ram": 32e9, "disk": 5e12},
        {"cores": 4, "ram": 16e9, "disk": 1e12},
        {"cores": 2, "ram": 4e9, "disk": 500e9}
    ]
}"""

deserialized = DatacenterRack.from_json(serialized)
roundtrip = deserialized.to_json()
assert json.loads(serialized) == json.loads(roundtrip)
```

When you use mix-ins like this, it’s fine if the class you apply `JsonMixin` to already inherits from `JsonMixin` higher up in the class hierarchy. The resulting class will behave the same way, thanks to the behavior of `super` .

当你像这样使用混入类时，即使你应用 `JsonMixin` 的类已经在类层次结构的更高层级继承自 `JsonMixin` 也没关系。由于 `super` 的行为，生成的类将表现相同。

**Things to Remember**
- Avoid using multiple inheritance with instance attributes and `__init__` if mix-in classes can achieve the same outcome.
- Use pluggable behaviors at the instance level to provide per-class customization when mix-in classes may require it.
- Mix-ins can include instance methods or class methods, depending on your needs.
- Compose mix-ins to create complex functionality from simple behaviors.

**注意事项**
- 如果混入类可以达到相同效果，则应避免使用带有实例属性和 `__init__` 的多重继承。
- 在实例级别使用可插拔行为，以便在混入类可能需要自定义时提供按类定制的功能。
- 混入类可以根据你的需求包含实例方法或类方法。
- 组合使用混入类，从简单行为中创建复杂功能。