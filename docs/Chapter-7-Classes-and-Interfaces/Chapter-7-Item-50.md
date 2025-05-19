# Chapter 7: Classes and Interfaces (类与接口)

## Item 50: Consider `functools.singledispatch` for Functional-Style Programming Instead of Object-Oriented Polymorphism (考虑使用`functools.singledispatch`进行函数式编程而不是面向对象的多态性)

In the pocket calculator example from Item 49: “Prefer Object-Oriented Polymorphism Over Functions with `isinstance` Checks”, I showed how object-oriented programming (OOP) can make it easier to vary behavior based on the type of an object. At the end, I had a hierarchy of classes with different method implementations like this:

在第49条“优先使用面向对象的多态性而不是使用`isinstance`检查的函数”中的袖珍计算器示例中，我展示了面向对象编程（OOP）如何使基于对象类型改变行为变得更加容易。最后，我创建了一个具有不同方法实现的类层次结构，如下所示：

```
class NodeAlt:
    def evaluate(self):
        raise NotImplementedError

    def pretty(self):
        raise NotImplementedError

class IntegerNodeAlt(NodeAlt):
    def __init__(self, value):
        self.value = value

    def evaluate(self):
        return self.value

    def pretty(self):
        return repr(self.value)

class AddNodeAlt(NodeAlt):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def evaluate(self):
        left = self.left.evaluate()
        right = self.right.evaluate()
        return left + right

    def pretty(self):
        left_str = self.left.pretty()
        right_str = self.right.pretty()
        return f"({left_str} + {right_str})"


class MultiplyNodeAlt(NodeAlt):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def evaluate(self):
        left = self.left.evaluate()
        right = self.right.evaluate()
        return left + right

    def pretty(self):
        left_str = self.left.pretty()
        right_str = self.right.pretty()
        return f"({left_str} * {right_str})"
```

This made it possible to call the recursive methods `evaluate` and `pretty` on the root of an abstract syntax tree (AST) that represents the calculation to perform:

这使得可以在表示要执行计算的抽象语法树（AST）根部调用递归方法`evaluate`和`pretty`：

```
tree = MultiplyNodeAlt(
    AddNodeAlt(IntegerNodeAlt(3), IntegerNodeAlt(5)),
    AddNodeAlt(IntegerNodeAlt(4), IntegerNodeAlt(7)),
)
print(tree.evaluate())
print(tree.pretty())

>>>
19
((3 + 5) * (4 + 7))
```

Now, imagine that instead of there being two methods required by the superclass, there were 25 of them: one method might simplify an equation; another would check for undefined variables; yet another could calculate the derivative; still another would produce LaTeX syntax; and so on. In the typical approach to OOP, I would add 25 new methods to each class that contains a node type’s data. This would make the class definition very large, especially considering all of the helper functions and supporting data structures that might be required. With so much code, I’d want to split these node class definitions across multiple modules (e.g., one file per node type) to improve code organization:

现在，假设不是超类所需的两个方法，而是有25个：一个方法可以简化方程；另一个会检查未定义的变量；还有一个可以计算导数；另一个可以生成LaTeX语法等等。在典型的OOP方法中，我会向包含节点类型数据的每个类添加25个新方法。这将使类定义变得非常庞大，尤其是考虑到可能需要的所有辅助函数和支持数据结构。有了这么多代码，我想要将这些节点类定义拆分到多个模块中（例如，每个文件一个节点类型）以改进代码组织：

```
class NodeAlt2:
    def evaluate(self):
        raise NotImplementedError

    def pretty(self):
        raise NotImplementedError

    def solve(self):
        raise NotImplementedError

    def error_check(self):
        raise NotImplementedError

    def derivative(self):
        raise NotImplementedError

    # And 20 more methods...
```

Unfortunately, this type of module-per-class code organization can cause serious maintainability problems in production systems. The critical issue is that each of the 25 new methods might actually be quite different from one other, even though they are somehow related to a pocket calculator. When you’re editing and debugging code, the view you need is within each of the larger, independent systems (e.g., solving, error-checking), but with OOP these systems must be implemented across all of the classes. That means that in practice, for this hypothetical example, the OOP approach could cause you to jump between 25 different files in order to accomplish simple programming tasks. The code appears to be organized along the wrong axis. You’ll almost never need to look at two independent systems for a single class at the same time, but that’s how the source files are laid out.

不幸的是，在生产系统中，这种按类每文件的代码组织方式可能导致严重的可维护性问题。关键问题是，即使这25个新方法可能彼此完全不同，但它们仍以某种方式与袖珍计算器相关。当你编辑和调试代码时，你需要的视图是在每个较大的、独立的系统内（如解决、错误检查），但使用OOP这些系统必须在所有类中实现。这意味着在这个假设的例子中，OOP方法可能会导致你在完成简单编程任务时跳转到25个不同的文件。代码似乎沿错误轴进行了组织。你几乎从不需要同时查看单个类的两个独立系统，但源文件就是如此布局。

Making matters worse, OOP code organization also conflates dependencies. For this example, the LaTeX generating methods might need to import a native library for handling that format; the formula solving methods might need a heavy-weight symbolic math module; and so on. If your code organization is class-centric, that means each module defining a class needs to import all of the dependencies for all of the methods (see Item 97: “Lazy-load Modules with Dynamic Imports to Reduce Startup Time” for background). This prevents you from creating self-contained, well-factored systems of functionality, thus hampering extensibility, refactoring, and testability. Fortunately, OOP is not the only option.

更糟糕的是，OOP代码组织还混淆了依赖关系。对于这个例子，LaTeX生成方法可能需要导入用于处理该格式的原生库；公式求解方法可能需要一个重量级的符号数学模块；依此类推。如果你的代码组织是以类为中心的，那么意味着定义类的每个模块都需要导入所有方法所需的所有依赖项（有关背景，请参见第97条：“使用动态导入延迟加载模块以减少启动时间”）。这阻止了你创建自包含的、良好分解的功能系统，从而阻碍了扩展性、重构和测试能力。幸运的是，OOP并不是唯一的选择。

Single dispatch is a functional-style programming technique where a program decides which version of a function to call based on the type of one of its arguments. It behaves similarly to polymorphism, but it can also avoid many of OOP’s pitfalls. You can use single dispatch to essentially add methods to a class without modifying it. Python provides the `singledispatch` decorator in the `functools` built-in module for this purpose.

单一派遣是一种函数式编程技术，程序根据其参数之一的类型决定调用哪个版本的函数。它的行为类似于多态性，但也可以避免许多OOP的陷阱。你可以使用`functools`内置模块中的`singledispatch`装饰器来实现此目的。

To use `singledispatch` , first I need to define the function that will do the dispatching. Here, I create a function for custom object printing:

要使用`singledispatch`，首先我需要定义将执行调度的函数。在这里，我创建了一个用于自定义对象打印的函数：

```
import functools

@functools.singledispatch
def my_print(value):
    raise NotImplementedError
```

This initial version of the function will be called as a last resort if no better option is found for the type of the first argument ( `value` ). I can specialize the implementation for a particular type by using the dispatching function’s `register` method as a decorator. Here, I add implementations for the `int` and `float` built-in types:

如果没有为第一个参数`value`的类型找到更好的选项，则将调用此初始版本的函数。我可以通过使用调度函数的`register`方法作为装饰器来为特定类型专门化实现。在这里，我添加了对`int`和`float`内置类型的实现：

```
@my_print.register(int)
def _(value):
    print("Integer!", value)

@my_print.register(float)
def _(value):
    print("Float!", value)
```

These functions use the underscore ( `_` ) to indicate that their names don’t matter and they won’t be called directly; all dispatching will occur through the `my_print` function. Here, I show this working for the types I’ve registered so far:

这些函数使用下划线（`_`）表示它们的名称无关紧要且不会被直接调用；所有的调度都将通过`my_print`函数发生。在这里，我展示了我已经注册的类型的工作情况：

```
my_print(20)
my_print(1.23)
>>>
Integer! 20
Float! 1.23
```

Going back to the pocket calculator example, I can use `singledispatch` to implement the `evaluate` functionality without OOP. First, I define a new dispatching function:

回到袖珍计算器示例，我可以使用`singledispatch`在不使用OOP的情况下实现`evaluate`功能。首先，我定义一个新的调度函数：

```
@functools.singledispatch
def my_evaluate(node):
    raise NotImplementedError
```

Then I add a type-specific implementation for the simple integer data structure:

然后我为简单的整数数据结构添加特定类型的实现：

```
class Integer:
    def __init__(self, value):
        self.value = value

@my_evaluate.register(Integer)
def _(node):
    return node.value
```

And I provide similar implementations for the simple operation data structures. Note how none of the data structures define any additional methods:

我还为简单的操作数据结构提供了类似的实现。注意，这些数据结构都没有定义任何额外的方法：

```
class Add:
    def __init__(self, left, right):
        self.left = left
        self.right = right

@my_evaluate.register(Add)
def _(node):
    left = my_evaluate(node.left)
    right = my_evaluate(node.right)
    return left + right

class Multiply:
    def __init__(self, left, right):
        self.left = left
        self.right = right

@my_evaluate.register(Multiply)
def _(node):
    left = my_evaluate(node.left)
    right = my_evaluate(node.right)
    return left * right
```

These functions work as expected when I call my_evaluate :

当我调用`my_evaluate`时，这些函数按预期工作：

```
tree = Multiply(
    Add(Integer(3), Integer(5)),
    Add(Integer(4), Integer(7)),
)
result = my_evaluate(tree)
print(result)

>>>
88
```

Now, say I want to implement equation pretty-printing like in Item 49, but without using OOP. I can do this simply by defining another singledispatch function and decorating implementation functions for each type I want to handle:

现在，假设我想在不使用OOP的情况下实现类似第49条中的等式美化打印。我可以简单地定义另一个`singledispatch`函数，并为我要处理的每种类型装饰实现函数：

```
@functools.singledispatch
def my_pretty(node):
    raise NotImplementedError

@my_pretty.register(Integer)
def _(node):
    return repr(node.value)

@my_pretty.register(Add)
def _(node):
    left_str = my_pretty(node.left)
    right_str = my_pretty(node.right)
    return f"({left_str} + {right_str})"

@my_pretty.register(Multiply)
def _(node):
    left_str = my_pretty(node.left)
    right_str = my_pretty(node.right)
    return f"({left_str} * {right_str})"

>>>
((3 + 5) * (4 + 7))
```

If I create a new type that is a subclass of a type I’ve already registered, it will immediately work with `my_pretty` without additional code changes because it follows method-resolution order like inheritance (see Item 53: “Initialize Parent Classes with `super` ”). For example, here I add a subclass of the Integer type and show that it can pretty print:

如果我创建一个已经是注册过的类型的子类的新类型，它将立即与`my_pretty`一起工作，无需额外的代码更改，因为它遵循继承的方法解析顺序（参见第53条：“使用`super`初始化父类”）。例如，这里我添加了一个`Integer`类型的子类并显示它可以美观打印：

```
class PositiveInteger(Integer):
    pass

print(my_pretty(PositiveInteger(1234)))

>>>
1234
```

The difficulty with `singledispatch` arises when I create a new class. For example, calling the `my_pretty` function with a new type of object will raise a `NotImplementedError` exception because there’s no implementation registered to handle the new type:

当使用`singledispatch`时会出现困难，即当我创建一个新类时。例如，使用新的对象类型调用`my_pretty`函数会引发`NotImplementedError`异常，因为没有为处理新类型注册实现：

```
class Float:
        def __init__(self, value):
            self.value = value
    
    
    print(my_pretty(Float(5.678)))

>>>
Traceback ...
NotImplementedError
```


This is the fundamental trade-off in using function-style single dispatch: when you add a new type to the code, you need to add a corresponding implementation for every dispatch function you want to support. That might require modifying many or all of the independent modules in your program. In contrast, with object-oriented polymorphism, new classes might seem easier to add—just implement the required methods—but adding a new method to the system requires updating every class. Although there’s some friction with either approach, in my view, the burden with single dispatch is lower and the benefits are numerous.

这是使用函数式单一分派的根本权衡：当你向代码中添加新类型时，需要为希望支持的每个调度函数添加相应的实现。这可能需要修改程序中的多个或所有独立模块。相比之下，使用面向对象的多态性，新类的添加可能看起来更容易——只需实现所需的方法——但是向系统中添加新方法需要更新每个类。虽然这两种方法都有一些摩擦，但在我的观点中，单一分派的负担较低且益处众多。

With single dispatch you can have thousands of data structures and hundreds of behaviors in the program without polluting the class definitions with methods. This allows you to create independent systems of behavior in completely separate modules with no interdependencies on each other and a narrow set of external dependencies. Simple data structures can live at the bottom of your program’s dependency tree and be shared across the whole codebase without high coupling. Using the single dispatch approach like this organizes the code on the correct axis: all of the related behaviors are together instead of spread across countless modules where OOP classes reside. Ultimately, this makes it easier to maintain, debug, extend, refactor, and test your code.

使用单一分派，你的程序可以拥有数千个数据结构和数百种行为而不会污染类定义中的方法。这允许你在完全独立的模块中创建独立的行为系统，彼此之间没有相互依赖，外部依赖集狭窄。简单的数据结构可以位于程序依赖树的底部，并在整个代码库中共享而不会产生高耦合。像这样使用单一分派方法在正确的轴上组织代码：所有相关的行为都在一起，而不是散布在无数OOP类所在的模块中。最终，这使维护、调试、扩展、重构和测试代码变得更加容易。

That said, OOP can still be a good choice when your classes share common functionality and the larger systems are more interconnected. The choice between these code structures comes down to how independent the program’s components are, and how much common data or behavior they share. You can also mix OOP and single dispatch together to benefit from the best attributes of both styles. For example, you could add utility methods to the simple classes that are common across all of the independent systems.

话虽如此，当你的类共享通用功能且较大的系统更加互联时，OOP仍然可以是一个好的选择。在这两种代码结构之间的选择取决于程序组件的独立程度以及它们共享的公共数据或行为的数量。你还可以混合使用OOP和单一分派，以从两种风格的最佳属性中受益。例如，你可以向简单类添加实用方法，这些方法在所有独立系统中都是通用的。

**Things to Remember**
- Object-oriented programming leads to class-centric code organization, which can make it difficult to build and maintain large programs because behavior is spread out across many modules.
- Single dispatch is an alternative approach for achieving dynamic dispatch using functions instead method polymorphism, making it possible to bring related functionality closer together in source code.
- Python’s `functools` built-in module has a `singledispatch` decorator that can be used to implement single dispatch behaviors.
- Programs with highly independent systems that operate on the same underlying data might benefit from the functional style of single dispatch instead of OOP.

**注意事项**
- 面向对象编程导致以类为中心的代码组织，这可能使大型程序的构建和维护变得困难，因为行为分布在许多模块中。
- 单一分派是使用函数而不是方法多态性实现动态分派的另一种方法，这使得在源代码中将相关功能集中在一起成为可能。
- Python 的 `functools` 内置模块有一个 `singledispatch` 装饰器，可用于实现单一分派行为。
- 具有高度独立系统的程序，这些系统操作相同的底层数据可能受益于单一分派的函数风格而非 OOP。

