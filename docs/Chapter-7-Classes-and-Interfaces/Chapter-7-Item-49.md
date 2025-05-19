# Chapter 7: Classes and Interfaces (类与接口)

## Item 49: Prefer Object-Oriented Polymorphism over Functions with `isinstance` Checks (优先使用面向对象的多态性而不是带有`isinstance`检查的函数)

Imagine I want to create a pocket calculator that receives simple formulas as input and computes the solution. To do this, I would normally tokenize and parse the provided text and create an abstract syntax tree (AST) to represent the operations to perform, similar to what the Python compiler does when it’s loading programs. For example, here I define three AST classes for the addition and multiplication of two integers:

假设我想创建一个口袋计算器，它接收简单的公式作为输入并计算解决方案。为此，我通常会对提供的文本进行分词和解析，并创建一个抽象语法树（AST）来表示要执行的操作，这类似于Python编译器在加载程序时所做的工作。例如，我为两个整数的加法和乘法定义了三个AST类：

```
class Integer:
    def __init__(self, value):
        self.value = value

class Add:
    def __init__(self, left, right):
        self.left = left
        self.right = right

class Multiply:
    def __init__(self, left, right):
        self.left = left
        self.right = right
```

For a basic equation like `2 + 9` , I can create the AST (bypassing tokenization and parsing) by directly instantiating objects:

对于像`2 + 9`这样的基本方程，我可以绕过分词和解析，通过直接实例化对象来创建AST：

```
tree = Add(
    Integer(2),
    Integer(9),
)
```

A recursive function can be used to evaluate an AST like this. For each type of operation it might encounter, I need to add another branch to one compound `if` statement. I can use the `isinstance` built-in function to direct control flow based on the type of AST object being evaluated (see Item 9: “Consider match for Destructuring in Flow Control, Avoid When if Statements Are Sufficient” for another way to do this):

可以使用递归函数来评估这样的AST。对于它可能遇到的每种操作类型，我需要向一个复合的`if`语句中添加另一个分支。我可以使用内置的`isinstance`函数根据正在评估的AST对象的类型来指导控制流（参见条目9：“考虑在流程控制中使用match进行解构，当if语句足够时避免使用”以了解另一种做法）：

```
def evaluate(node):
    if isinstance(node, Integer):
        return node.value
    elif isinstance(node, Add):
        return evaluate(node.left) + evaluate(node.right)
    elif isinstance(node, Multiply):
        return evaluate(node.left) * evaluate(node.right)
    else:
        raise NotImplementedError
```

And indeed, this approach to interpreting the AST—often called tree walking—works as expected:

实际上，这种解释AST的方法——通常称为树遍历——按预期工作：

```
print(evaluate(tree))
>>>
11
```

By calling the same `evaluate` function for every type of node, the system can support arbitrary nesting without additional complexity. For example, here I define an AST for the equation `(3 + 5) * (4 + 7)` and evaluate it without having to make any other code changes:

通过为每种类型的节点调用相同的`evaluate`函数，系统可以在不增加额外复杂性的情况下支持任意嵌套。例如，这里我定义了一个方程`(3 + 5) * (4 + 7)`的AST，并在不需要做任何其他代码更改的情况下对其进行评估：

```
tree = Multiply(
    Add(Integer(3), Integer(5)),
    Add(Integer(4), Integer(7)),
)
print(evaluate(tree))
>>>
88
```

Now, imagine that the number of nodes I need to consider in the tree is significantly more than three. I need to handle subtraction, division, logarithms, and on and on—mathematics has an enormous surface area and there could be hundreds of node types. If I need to do everything in this one `evaluate` function, it’s going to get extremely long. Even if I add helper functions and call them inside the `elif` blocks, the overall `if` compound statement would be huge. There must be a better way.

现在，想象一下我需要考虑的树中的节点数量远远超过三个。我需要处理减法、除法、对数等等——数学有巨大的覆盖面，可能会有数百种节点类型。如果我需要在这个单一的`evaluate`函数中完成所有事情，它将会变得极其冗长。即使我添加辅助函数并在`elif`块内调用它们，整体的`if`复合语句也会非常庞大。必须有更好的方法。

One common approach to solving this problem is object oriented programming (OOP). Instead of having one function that does everything for all types of objects, you encapsulate the functionality for each type right next to its data (in methods). Then you rely on polymorphism to dynamically dispatch method calls to the right subclass implementation at runtime. This has the same effect as the `if` compound statement and `isinstance` checks, but does it in a way that doesn’t require defining everything in one gigantic function.

解决这个问题的一个常见方法是面向对象编程（OOP）。不是有一个函数处理所有类型的对象，而是将每种类型的功能封装在其数据旁边（在方法中）。然后依赖于多态，在运行时动态地将方法调用分派到正确的子类实现。这种方法具有与`if`复合语句和`isinstance`检查相同的效果，但它是以一种不要求在单个巨大的函数中定义一切的方式实现的。

For this pocket calculator example, using OOP would begin by defining a superclass (see Item 53: “Initialize Parent Classes with super ” for background) with the methods that should be common among all objects the AST:

对于这个口袋计算器的例子，使用OOP将从定义一个包含所有AST对象共通方法的超类开始（背景信息请参阅条目53：“使用super初始化父类”）：

```
class Node:
    def evaluate(self):
        raise NotImplementedError
```

Each type of node would need to implement the `evaluate` method to compute the result corresponding to the data contained within the object. Here, I define this method for integers:

每种类型的节点都需要实现`evaluate`方法，以计算其内部包含的数据对应的结果。在这里，我为整数定义了此方法：

```
class IntegerNode(Node):
    def __init__(self, value):
        self.value = value

    def evaluate(self):
        return self.value
```

And here’s the implementation of evaluate for addition and multiplication operations:

下面是加法和乘法运算的`evaluate`实现：

```
class AddNode(Node):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def evaluate(self):
        left = self.left.evaluate()
        right = self.right.evaluate()
        return left + right

class MultiplyNode(Node):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def evaluate(self):
        left = self.left.evaluate()
        right = self.right.evaluate()
        return left * right
```

Creating objects representing the AST is straightforward like before, but this time I can directly call the `evaluate` method on the tree object instead of having to use a separate helper function:

创建代表AST的对象就像以前一样简单，但这次可以直接调用树对象上的`evaluate`方法，而不必使用单独的辅助函数：

```
tree = MultiplyNode(
    AddNode(IntegerNode(3), IntegerNode(5)),
    AddNode(IntegerNode(4), IntegerNode(7)),
)
print(tree.evaluate())
>>>
88
```

The way this works is the call to `tree.evaluate` will call the `MultiplyNode.evaluate` method with the tree instance. Then the `AddNode.evaluate` method will be called for the left node, which in turn calls `IntegerNode.evaluate` for values `3` and `5` . After that, the `AddNode.evaluate` method is called for the right node, which similarly calls `IntegerNode.evaluate` for values `4` and `7` . Critically, all of the decisions on which `evaluate` method implementation to call for each `Node` subclass occurs at runtime—this is the key benefit of object-oriented polymorphism.

其工作原理是，对`tree.evaluate`的调用会用tree实例调用`MultiplyNode.evaluate`方法。接着左节点会调用`AddNode.evaluate`方法，该方法又调用值`3`和`5`的`IntegerNode.evaluate`方法。之后右节点的`AddNode.evaluate`方法被调用，类似地调用值`4`和`7`的`IntegerNode.evaluate`方法。关键的是，每个`Node`子类应调用哪个`evaluate`方法实现的决定发生在运行时 - 这是面向对象多态性的关键优势。

As with all programs, I might need to extend the pocket calculator with more features. For example, I could add the ability for the calculator to print the formula that was inputted, but with pretty formatting that’s consistent and easy to read. With OOP, I’d accomplish this by adding another abstract method to the superclass, and implement it in each of the subclasses. Here, I add the `pretty` method for this new purpose:

与所有程序一样，我可能需要扩展口袋计算器的功能。例如，我可以给计算器添加打印输入公式的功能，但格式要美观一致且易于阅读。在OOP中，我会通过向超类添加另一个抽象方法并在每个子类中实现它来实现这一新目的。在这里，我为这个新目的添加了`pretty`方法：

```
class NodeAlt:
    def evaluate(self):
        raise NotImplementedError

    def pretty(self):
        raise NotImplementedError
```

The implementation for integers is very simple:

整数的实现非常简单：

```
class IntegerNodeAlt(NodeAlt):
    def __init__(self, value):
        self.value = value

    def evaluate(self):
        return self.value


    def pretty(self):
        return repr(self.value)
```

The add and multiply operations descend into their left and right branches to produce a formatted result:

加法和乘法操作会进入它们的左右分支以生成格式化结果：

```
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

Similar to the `evaluate` method above, I can call the `pretty` method on the tree root in order to format the whole AST as a string:

类似于上面的`evaluate`方法，我可以在树根上调用`pretty`方法以便将整个AST格式化为字符串：

```
tree = MultiplyNodeAlt(
    AddNodeAlt(IntegerNodeAlt(3), IntegerNodeAlt(5)),
    AddNodeAlt(IntegerNodeAlt(4), IntegerNodeAlt(7)),
)
print(tree.pretty())

>>>
((3 + 5) * (4 + 7))
```

With OOP you can add more and more AST methods and subclasses as the needs of your program grows. There’s no need to maintain one enormous function with dozens of `isinstance` checks. Each of the types can have their own self-contained implementation, making the code relatively easy to organize, extend, and test. Python also provides many additional features to make polymorphic code more useful (see Item 52: “Use `@classmethod` Polymorphism to Construct Objects Generically” and Item 57: “Inherit from `collections.abc` Classes for Custom Container Types”).

借助OOP，随着程序需求的增长，您可以不断增加AST方法和子类。无需维护一个包含数十个`isinstance`检查的庞大函数。每种类型都可以拥有自己的自包含实现，使代码相对容易组织、扩展和测试。Python还提供了许多附加功能，使多态代码更加有用（请参阅条目52：“使用`@classmethod`多态以通用方式构造对象”和条目57：“继承`collections.abc`类以自定义容器类型”）。

However, it’s also important to understand that OOP has serious limitations when solving certain types of problems, especially in large programs (see Item 50: “Consider `functools.singledispatch` for Functional￾Style Programming Instead of Object-Oriented Polymorphism”).

然而，同样重要的是要认识到OOP在解决某些类型的问题时存在严重的局限性，尤其是在大型程序中（请参阅条目50：“考虑使用`functools.singledispatch`来进行功能性风格编程而非面向对象的多态”）。

**Things to Remember**
- Python programs can use the `isinstance` built-in function to alter behavior at runtime based on the type of objects.
- Polymorphism is an object-oriented programming (OOP) technique for dispatching a method call to the most specific subclass implementation at runtime.
- Code that uses polymorphism among many classes instead of `isinstance` checks can be much easier to read, maintain, extend, and test.

**注意事项**
- Python程序可以使用`isinstance`内置函数根据对象的类型在运行时改变行为。
- 多态是一种面向对象编程（OOP）技术，用于在运行时将方法调用分派到最具体的子类实现。
- 使用多态的代码相比于使用`isinstance`检查的代码更容易阅读、维护、扩展和测试。