# Chapter 1: Pythonic Thinking (第一章 用Pythonic方式来思考)

## Item 9: Consider match for Destructuring in Flow Control, Avoid When if Statements Are Sufficient (考虑在流程控制中使用 match 进行解构，避免使用 if 来满足需求)

The match statement is a relatively new Python feature, introduced in version 3.10. With so many distinct capabilities, the learning curve for match is steep—it feels like another mini-language embedded within Python, similar to the unique ergonomics of comprehensions (see Item 40: “Use Comprehensions Instead of map and filter ” and Item 44: “Consider Generator Expressions for Large List Comprehensions”). At first glance, match statements appear to provide Python with long-sought￾after behavior that’s similar to switch statements from other programming languages (see Item 8: “Prevent Repetition with Assignment Expressions” for another approach).

match 语句是 Python 中相对较新的特性，它在 Python 3.10 版本中被引入。由于其功能众多，学习 match 的曲线比较陡峭——它感觉就像是嵌入在 Python 中的另一个迷你语言，类似于推导式（comprehensions）的独特操作体验（参见条目 40：“优先使用推导式而不是 map 和 filter”，以及条目 44：“考虑生成器表达式用于大型列表推导”）。乍一看，match 语句似乎为 Python 提供了长期以来所期望的功能，这与其他编程语言中的 switch 语句类似（参见条目 8：“使用赋值表达式防止重复代码”以了解另一种方法）。

For example, say that I’m writing a vehicle assistant program that reacts to a traffic light’s color. Here, I use a simple Python if statement for this purpose:

例如，假设我正在编写一个车辆助手程序，该程序对交通灯的颜色做出反应。在这里，我使用了一个简单的 Python if 语句来实现这个目的：

```python
def take_action(light):
    if light == "red":
        print("Stop")
    elif light == "yellow":
        print("Slow down")
    elif light == "green":
        print("Go!")
    else:
        raise RuntimeError
```

I can confirm this function works as expected:

我可以确认此函数按预期工作：

```
take_action("red")
take_action("yellow")
take_action("green")
>>>
Stop
Slow down
Go!
```

To use the match statement, I can create case clauses corresponding to each of the if , elif , and else conditions:

为了使用 match 语句，我可以创建对应于每个 if、elif 和 else 条件的 case 子句：

```python
def take_match_action(light):
    match light:
        case "red":
            print("Stop")
        case "yellow":
            print("Slow down")
        case "green":
            print("Go!")
        case _:
            raise RuntimeError
```

Using a match statement seems better than an if statement because I can remove repeated references to the light variable, and I can leave out the == operator for each conditional branch. However, this code still isn’t ideal because of how it uses string literals for everything. To fix this, what I’d normally do is create a constant at the module level for each light color and modify the code to use them, like this:

使用 match 语句看起来比 if 语句更好，因为我可以删除对 light 变量的重复引用，并且可以在每个条件分支中省略 == 运算符。然而，这段代码仍然不是理想的，因为它对所有内容都使用了字符串字面量。为了修复这个问题，通常我会在模块级别为每种灯光颜色创建一个常量，并修改代码以使用它们，如下所示：

```
# Added these constants
RED = "red"
YELLOW = "yellow"
GREEN = "green"
def take_constant_action(light):
    match light:
        case RED: # Changed
            print("Stop")
        case YELLOW: # Changed
            print("Slow down")
        case GREEN: # Changed
            print("Go!")
        case _:
            raise RuntimeError
>>>
Traceback ...
SyntaxError: name capture 'RED' makes remaining ...
```

Unfortunately, this code has an error, and a cryptic one at that. The issue is that the match statement assumes that simple variable names that come after the case keyword are capture patterns. To demonstrate what this means, here I shorten the match statement to only have a single branch that should match RED :

不幸的是，这段代码有一个错误，而且是一个晦涩的错误。问题在于，match 语句假定紧跟 case 关键字后的简单变量名是捕获模式。为了演示这意味着什么，这里我缩短了 match 语句，只保留应该匹配 RED 的一个分支：

```python
def take_truncated_action(light):
    match light:
        case RED:
            print("Stop")
```

Now, I call the function by passing GREEN . I expect the match light clause is evaluated first, and the light variable lookup in the current scope resolves to "green" . Next, I expect the case RED clause is evaluated, and the RED variable lookup resolves to "red" . These two values don’t match (i.e., "green" vs. "red" ), thus I expect no output:

现在，我通过传递 GREEN 调用该函数。我期望首先评估 match light 子句，并且当前作用域内的 light 变量查找解析为 "green"。接下来，我期望评估 case RED 子句，并且 RED 变量查找解析为 "red"。这两个值不匹配（即 "green" 对应 "red"），因此我期望没有输出：

```
take_truncated_action(GREEN)
>>>
Stop
```

Surprisingly, the match statement executed the RED branch. Here, I use print to figure out what’s happening:

令人惊讶的是，match 语句执行了 RED 分支。在这里，我使用 print 来弄清楚发生了什么：

```
def take_debug_action(light):
    match light:
        case RED:
            print(f"{RED=}, {light=}")

take_debug_action(GREEN)

>>>
RED='green', light='green'
```

The case clause didn’t look up the value of RED —instead, it assigned RED to the value of the light variable! What the match statement is doing is similar to the behavior of unpacking (see Item 5: “Prefer Multiple Assignment Unpacking Over Indexing”). Instead of case RED translating to light == RED , Python determines if the multiple assignment (RED,) = (light,) would execute without an error, similar to this:

case 子句并没有查找 RED 的值——相反，它将 RED 赋值给了 light 变量！match 语句所做的行为类似于解包（参见条目 5：“优先使用多重赋值解包而不是索引”）。case RED 并没有翻译成 light == RED，Python 确定是否多个赋值 (RED,) = (light,) 将在没有错误的情况下执行，类似于以下内容：

```python
def take_unpacking_action(light):
    try:
        (RED,) = (light,)
    except TypeError:
        # Did not match
        ...
    else:
        # Matched
        print(f"{RED=}, {light=}")
```

The original syntax error above occurred because Python determines at compile time that the assignment (RED,) = (light,) will work for any value of light , thus the subsequent clauses with case YELLOW and case GREEN are unreachable.

上面出现的原始语法错误是因为 Python 在编译时确定 (RED,) = (light,) 的赋值将在任何 light 值下都成功，因此后续带有 case YELLOW 和 case GREEN 的子句不可达。

One work-around for this problem is to ensure a . character is in the case clause’s variable reference. The presence of a dot operator causes Python to look up the attribute and do an equality test instead of treating the variable name as a capture pattern. For example, here I achieve the original intended behavior by using the enum built-in module and the dot operator to access each constant name:

解决此问题的一个变通方法是确保在 case 子句的变量引用中包含一个 . 字符。点运算符的存在会导致 Python 查找属性并进行相等性测试，而不是将变量名视为捕获模式。例如，这里我通过使用内置的 enum 模块和点运算符访问每个常量名称来实现最初预期的行为：

```python
import enum # Added
class ColorEnum(enum.Enum): # Added
    RED = "red"
    YELLOW = "yellow"
    GREEN = "green"

def take_enum_action(light):
    match light:
        case ColorEnum.RED: # Changed
            print("Stop")
        case ColorEnum.YELLOW: # Changed
            print("Slow down")
        case ColorEnum.GREEN: # Changed
            print("Go!")
        case _:
            raise RuntimeError
```

Although this code now works as expected, it’s hard to see the benefits of the match version over the simpler if version in the take_action function above. The if version is 9 lines versus 10 lines with match . The if version repeats the light == prefix for each branch, but the match version repeats the ColorEnum. prefix for the constants.

尽管这段代码现在如预期般运行，但很难看到 match 版本相对于上面 take_action 函数中更简单的 if 版本的优势。if 版本有 9 行，而 match 版本有 10 行。if 版本在每个分支中重复了 light == 前缀，但 match 版本对常量重复了 ColorEnum. 前缀。 表面上看，这似乎势均力敌。为什么 Python 在语言中添加 match 语句，如果它们并不是一个具有说服力的特性？

Superficially, it seems like a wash. Why did Python add match statements to the language if they’re not a compelling feature?

表面上看，这似乎势均力敌。为什么 Python 在语言中添加 match 语句，如果它们并不是一个具有说服力的特性？

**match is for Destructuring**

**match 是用于解构**

Destructuring is a programming language technique for extracting components from a complex nested data structure with minimal syntax. Python programmers use destructuring all the time without even thinking about it. For example, the multiple assignment of index, value to the return value of enumerate in this for loop is a form of destructuring (see Item 17: “Prefer enumerate Over range ”):

解构是一种编程语言技术，用于从复杂嵌套的数据结构中提取组件，同时使用最少的语法。Python 程序员经常使用解构而不去过多思考它。例如，在这个 for 循环中，将 index, value 多重赋值给 enumerate 的返回值就是一种解构形式（参见条目 17：“优先使用 enumerate 而不是 range”）：

```
for index, value in enumerate("abc"):
    print(f"index {index} is {value}")
>>>
index 0 is a
index 1 is b
index 2 is c
```

Python has supported destructuring assignments for deeply nested tuples and lists for a long time (see Item 16: “Prefer Catch-All Unpacking Over Slicing”). The match statement extends the language to also support this unpacking-like behavior for dictionaries, sets, and user-defined classes solely for the purpose of control flow. The structural pattern matching technique that match enables is especially valuable when your code needs to deal with heterogeneous object graphs and semi-structured data
(similar idioms in functional-style programming are algebraic data types, sum types, and tagged unions).

Python 长期以来一直支持深度嵌套元组和列表的解构赋值（参见条目 16：“优先使用全包裹解包而不是切片”）。match 语句扩展了语言，使其还支持这种类似解包的行为，适用于字典、集合和用户定义的类，仅用于控制流的目的。match 启用的结构性模式匹配技术在你的代码需要处理异构对象图和半结构化数据时尤其有价值（函数式风格编程中的类似习惯用法是代数数据类型、求和类型和标签联合）。

For example, say that I want to search a binary tree and determine if it contains a given value. I can represent the binary tree as a three-item tuple , where the first index is the value, the second index is the left (lower value) child, and the third index is the right (higher value) child. None in the second or third positions indicates the absence of a child node. In the case of a leaf node, I can just put the value inline instead of another nested tuple . Here, I define a nested tree this way containing five values (7, 9, 10, 11, 13):

例如，假设我想搜索二叉树并确定它是否包含给定值。我可以将二叉树表示为三元素元组，其中第一个索引是值，第二个索引是左（较小值）子节点，第三个索引是右（较大值）子节点。在第二或第三位置上的 None 表示缺少子节点。对于叶节点，我可以直接放置值而不是另一个嵌套元组。在这里，我以这种方式定义一个包含五个值（7、9、10、11、13）的嵌套树：

```
my_tree = (10, (7, None, 9), (13, 11, None))
```

I can implement a recursive function to test if a tree contains a value by using simple if statements. The tree argument might be None (for an absent child node) or a non-tuple (for a leaf node), so this code needs to ensure those conditions are handled before unpacking the three-tuple node representation:

我可以使用简单的 if 语句实现递归函数来测试树是否包含值。tree 参数可能是 None（对于不存在的子节点）或非元组（对于叶节点），所以这段代码需要确保在解包三元组节点表示之前处理这些条件：

```
def contains(tree, value):
    if not isinstance(tree, tuple):
        return tree == value
    pivot, left, right = tree
    if value < pivot:
        return contains(left, value)
    elif value > pivot:
        return contains(right, value)
    else:
        return value == pivot
```

This function works as expected when the node values are comparable:

当节点值可比较时，此函数按预期工作：

```
assert contains(my_tree, 9)
assert not contains(my_tree, 14)
```

Now, I can rewrite this function using the match statement:

现在，我可以使用 match 语句重写此函数：

```
def contains_match(tree, value):
    match tree:
        case pivot, left, _ if value < pivot:
            return contains_match(left, value)
        case pivot, _, right if value > pivot:
            return contains_match(right, value)
        case (pivot, _, _) | pivot:
            return pivot == value
```

Using match , the call to isinstance is eliminated, the unpacking assignment can be avoided, the structure of the code (using case clauses) is more regular, the logic is simpler and easier to follow, and the function is only 7 lines of code instead of the 9 lines required for the if version. This makes the match statement appear quite compelling (see Item 76: “Know How to Port Threaded I/O to asyncio ” for another example).

使用 match，消除了对 isinstance 的调用，可以避免解包赋值，代码的结构（使用 case 子句）更加规则，逻辑更简单易懂，并且该函数只有 7 行代码，而 if 版本需要 9 行。这使得 match 语句显得非常吸引人（参见条目 76：“知道如何将线程 I/O 移植到 asyncio”以获取另一个示例）。

In this function, the way that match works is each of the case clauses tries to extract the contents of the tree argument using the given destructuring pattern. After Python determines that the structure matches, it evaluates any subsequent if clauses, which work similarly to if clauses in comprehensions. When the if clause, sometimes called a guard expression, evaluates to True , then the indented statements for that case block will be executed and the rest will be skipped. If no case clauses match the input value, then the match statement will do nothing and fall through.

在此函数中，match 的工作方式是每个 case 子句尝试使用给定的解构模式提取 tree 参数的内容。在 Python 确定结构匹配后，它会评估任何后续的 if 子句，这与理解中的 if 子句的工作方式类似。当 if 子句（有时称为守护表达式）评估为 True 时，则该 case 块的缩进语句将被执行，其余的将被跳过。如果没有 case 子句匹配输入值，则 match 语句将不执行任何操作并继续执行下去。

This code also uses the | pipe operator to add an or pattern to the final case branch. This allows the case clause to match either of the given patterns: (pivot, _, _) or pivot . As you might recall from the traffic light example above that tried to reference the RED constant, the second pattern ( pivot ) is a capture pattern that will match any value. Thus, when tree is not a tuple with the right structure, the code assumes it’s a leaf value that should be tested for equality.

此代码还使用 | 管道运算符向最终的 case 分支添加一个 or 模式。这允许 case 子句匹配给定模式中的任何一个：(pivot, _, _) 或 pivot。正如你可能从上面尝试引用 RED 常量的交通灯示例中回忆起来的那样，第二个模式（pivot）是一个捕获模式，它将匹配任何值。因此，当 tree 不是一个具有正确结构的元组时，代码假定它是一个叶值，应测试其相等性。

Now imagine that my requirements change yet again, and I want to use a class instead of a tuple to represent the nodes in my binary tree (see Item 29: “Compose Classes Instead of Deeply Nesting Dictionaries, Lists, and Tuples” for how to make that choice). Here, I define a new class for nodes:

现在想象一下我的需求再次改变，我想要使用类而不是元组来表示我的二叉树中的节点（参见条目 29：“组合类而不是深层嵌套的字典、列表和元组”以了解如何做出该选择）。在这里，我为节点定义了一个新类：

```python
class Node:
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right
```

I can create another instance of the tree using this class. Again, I specify leaf nodes simply by providing their value instead of wrapping them in an additional Node object:

我可以使用此类创建另一个树实例。同样，我通过提供其值来指定叶节点，而不是将其包装在额外的 Node 对象中：

```
obj_tree = Node(
 value=10,
 left=Node(value=7, right=9),
 right=Node(value=13, left=11),
)
```

Modifying the if statement version of the contains function to handle the Node class is straightforward:

修改 if 语句版本的 contains 函数以处理 Node 类是直接的：

```
def contains_class(tree, value):
    if not isinstance(tree, Node):
        return tree == value
    elif value < tree.value:
        return contains_class(tree.left, value)
    elif value > tree.value:
        return contains_class(tree.right, value)
    else:
        return tree.value == value
```

The resulting code is similarly complex to the earlier version that used three-tuples. In some ways the class makes the function better (e.g.,accessing object attributes instead of unpacking), and in other ways makes it worse (e.g., repetitive tree. prefixes).

结果代码的复杂程度与早期使用三元组的版本相似。在某些方面，类使函数变得更好（例如，访问对象属性而不是解包），而在其他方面则变得更糟（例如，重复的 tree. 前缀）。

I can also adapt the match version of the contains function to use the Node class:

我也可以调整 match 版本的 contains 函数以使用 Node 类：

```
def contains_match_class(tree, value):
    match tree:
        case Node(value=pivot, left=left) if value < pivot:
            return contains_match_class(left, value)
        case Node(value=pivot, right=right) if value > pivot:
            return contains_match_class(right, value)
        case Node(value=pivot) | pivot:
            return pivot == value
```

The way this works is each case clause implicitly does an isinstance check to test if the value of tree is a Node . Then, it extracts object attributes using the capture patterns ( pivot , left , right ), similar to how tuple destructuring works. The capture variables can be used in guard expressions and case blocks to avoid more verbose attribute accesses (e.g., tree.left ). The power and clarity provided by match works just as well with objects as it does with nested built-in data structures.

这样工作的原理是每个 case 子句隐式地进行 isinstance 检查，以测试 tree 的值是否为 Node。然后，它使用捕获模式（pivot, left, right）提取对象属性，类似于元组解构的工作方式。捕获变量可以在守卫表达式和 case 块中使用，以避免更冗长的属性访问（例如，tree.left）。match 提供的力量和清晰度与处理嵌套内置数据结构一样，也适用于对象。

**Semi-Structured Data Versus Encapsulated Data**

**半结构化数据 vs 封装数据**

match also excels when the structure of data and its interpretation are decoupled. For example, a deserialized JSON object is merely a nesting of dictionaries, lists, strings, and numbers (see Item 54: “Consider Composing Functionality with Mix-in Classes” for an example). It lacks the clear encapsulation of responsibilities provided by an explicit class hierarchy (see Item 53: “Initialize Parent Classes with super ”). But the way in which these basic JSON types are nested—the keys, values, and elements that are present at each level—gives the data semantic meaning that programs can interpret.

match 在数据结构及其解释解耦时也非常出色。例如，反序列化的 JSON 对象仅仅是字典、列表、字符串和数字的嵌套（参见条目 54：“考虑使用 mix-in 类组合功能性”以获取示例）。它缺乏显式类层次结构提供的明确封装责任（参见条目 53：“使用 super 初始化父类”）。 但是这些基本 JSON 类型的嵌套方式——每一层存在的键、值和元素——赋予了数据语义意义，程序可以解释这些意义。

For example, imagine that I’m building billing software, and I need to deserialize customer records that are stored as JSON. Some of the records are for customers who are individuals, and other records are for customers that are businesses:

例如，假设我正在构建计费软件，并且我需要反序列化存储为 JSON 的客户记录。有些记录是针对个人客户的，而其他记录是针对企业的：

```
record1 = """{"customer": {"last": "Ross", "first": "Bob"}}"""
record2 = """{"customer": {"entity": "Steve's Painting Co."}}"""
```

I’d like to take these records and turn them into well-defined Python objects that I can use with my program’s data processing features, UI widgets, etc (see Item 51: “Prefer dataclasses For Defining Light-Weight Classes” for background):

我希望将这些记录转换为明确定义的 Python 对象，以便在我的程序的数据处理功能、UI 小部件等中使用（参见条目 51：“优先使用 dataclasses 定义轻量级类”以获取背景知识）：

```python
from dataclasses import dataclass
@dataclass
class PersonCustomer:
    first_name: str
    last_name: str
@dataclass
class BusinessCustomer:
    company_name: str
```

I can use the match statement to interpret the structure and values within the JSON data and map it to the concrete PersonCustomer and BusinessCustomer classes. This uses the match statements unique syntax for destructuring dictionary literals with capture patterns:

我可以使用 match 语句来解释 JSON 数据中的结构和值，并将其映射到具体的 PersonCustomer 和 BusinessCustomer 类。这使用了 match 语句独特的解构字典字面量与捕获模式的语法：

```
import json
def deserialize(data):
    record = json.loads(data)
    match record:
        case {"customer": {"last": last_name, "first": first_name}}:
            return PersonCustomer(first_name, last_name)
        case {"customer": {"entity": company_name}}:
            return BusinessCustomer(company_name)
        case _:
            raise ValueError("Unknown record type")

```

This function works as expected on the records defined above and produces the objects that I need:

此函数在上面定义的记录上按预期工作，并产生我需要的对象：

```
print("Record1:", deserialize(record1))
print("Record2:", deserialize(record2))
>>>
Record1: PersonCustomer(first_name='Bob', last_na
Record2: BusinessCustomer(company_name="Steve's P
```

These examples are merely a small taste of what’s possible with match statements. There’s also support for set patterns, as patterns, positional constructor patterns (with __match_args__ customization), exhaustiveness checking with type annotations (see Item 124: “Consider Static Analysis via typing to Obviate Bugs”), and more. Given the intricacies, it’s best to refer to the official tutorial (https://peps.python.org/pep-0636/) to determine how to leverage match for your specific use case.

这些示例只是 match 语句可能性的一小部分。还有对 set 模式、as 模式、位置构造函数模式（使用 match_args 自定义）、带类型注释的详尽检查（参见条目 124：“考虑通过 typing 进行静态分析以消除错误”）等的支持。鉴于这些复杂性，最好参考官方教程 [match以确定如何根据您的特定用例利用](https://peps.python.org/pep-0636/) 。

**Things to Remember**
- Although match statements can be used to replace simple if statements, doing so is error prone. The structural nature of capture patterns in case clauses is unintuitive for Python programmers who aren’t already familiar with the gotchas of match .
- match statements provide a concise syntax for combining isinstance checks and destructuring behaviors with flow control. They’re especially useful when processing heterogeneous object graphs and interpreting the semantic meaning of semi-structured data.
- case patterns can be used effectively with built-in data structures (lists, tuples, dictionaries) and user-defined classes, but each type has unique semantics that aren’t immediately obvious.

**注意事项**
- 虽然 match 语句可用于替换简单的 if 语句，但这样做容易出错。对于尚未熟悉 match 的陷阱的 Python 程序员来说，case 子句中捕获模式的结构性质并不直观。
- match 语句为结合 isinstance 检查和解构行为与流程控制提供了简洁的语法。它们在处理异构对象图和解释半结构化数据的语义含义时特别有用。 
- case 模式可以有效地与内置数据结构（列表、元组、字典）和用户定义的类一起使用，但每种类型都有其独特的语义，这些语义并不总是立即明显。