# Chapter 5: Functions (函数)

## Item 30: Know That Function Arguments Can Be Mutated (了解函数参数可被修改)

Python doesn’t support pointer types (beyond interfacing with C, see Item 95: “Consider `ctypes` to Rapidly Integrate with Native Libraries”). But arguments passed to functions are all passed by reference. For simple types, like integers and strings, parameters appear to be passed by value because they’re immutable objects. But more complex objects can be modified whenever they’re passed to other functions, regardless of the caller’s intent.

Python不支持指针类型（除了与C交互的情况，请参见条目95）。但是传递给函数的所有参数都是通过引用传递的。对于像整数和字符串这样的简单类型，参数似乎是以值传递的方式传递的，因为它们是不可变对象。但更复杂的对象在传递给其他函数时可以被修改，无论调用者的意图如何。

For example, if I pass a list to another function, that function has the ability to call mutation methods on the argument:

例如，如果我将一个列表传递给另一个函数，该函数有能力对参数调用变异方法：

```
def my_func(items):
    items.append(4)
x = [1, 2, 3]
my_func(x)
print(x) # 4 is now in the list
>>>
[1, 2, 3, 4]
```

The original variable `x` in this case can’t be replaced by the called function, as you might do with a C-style pointer type. But modifications to `x` can by made.

在这种情况下，原始变量`x`不能被调用函数替换，这在使用C风格的指针类型时是可以做到的。但可以对`x`进行修改。

Similarly, when one variable is assigned to another, it stores a reference, or alias, to the same underlying data structure. Thus, calling a function with what appears to be a separate variable actually allows for mutation of the original:

同样地，当一个变量被赋值给另一个变量时，它存储的是相同底层数据结构的引用或别名。因此，用看似独立的变量调用函数实际上允许修改原始数据：

```
a = [7, 6, 5]
b = a # Creates an alias
my_func(b)
print(a) # 4 is now in the list
>>>
[7, 6, 5, 4]
```

For lists and dictionaries you can work around this issue by passing a copy of the container to insulate you from the function’s behavior. Here, I create a copy using the a slice operation with no starting or ending indexes (see Item 14: “Know How to Slice Sequences”):

对于列表和字典，您可以通过传递容器的副本来避免这个问题，从而保护自己免受函数行为的影响。在这里，我使用没有起始或结束索引的切片操作创建了一个副本（请参见条目14："知道如何切片序列"）：

```
def capitalize_items(items):
    for i in range(len(items)):
        items[i] = items[i].capitalize()
my_items = ["hello", "world"]
items_copy = my_items[:] # Creates a copy
capitalize_items(items_copy)
print(items_copy)
>>>
['Hello', 'World']
```

The dictionary built-in type provides a `copy` method specifically for this purpose:

字典内置类型专门为此目的提供了一个`copy`方法：

```
def concat_pairs(items):
    for key in items:
        items[key] = f"{key}={items[key]}"
my_pairs = {"foo": 1, "bar": 2}
pairs_copy = my_pairs.copy() # Creates a copy
concat_pairs(pairs_copy)
print(pairs_copy)
>>>
{'foo': 'foo=1', 'bar': 'bar=2'}
```

User-defined classes (see Item 29: “Compose Classes Instead of Deeply Nesting Dictionaries, Lists, and Tuples”) can also be modified by callers. Any of their internal properties can be accessed or assigned by any function they’re passed to (see Item 55: “Prefer Public Attributes Over Private Ones”):

用户定义的类（请参见条目29："组合类而不是深度嵌套字典、列表和元组"）也可以被调用者修改。它们的任何内部属性都可以被传入的任何函数访问或分配（请参见条目55："优先选择公共属性而非私有属性"）：

```
class MyClass:
    def __init__(self, value):
        self.value = value

x = MyClass(10)

def my_func(obj):
    obj.value = 20 # Modifies the object

my_func(x)

print(x.value)
>>>
20
```

When implementing a function that others will call, you shouldn’t modify any mutable value provided unless that behavior is mentioned explicitly in the function name, argument names, or documentation. You might also want to make a defensive copy of any arguments you receive to avoid various pitfalls with iteration (see Item 21: “Be Defensive When Iterating Over Arguments” and Item 22: “Never Modify Containers While Iterating Over Them, Use Copies or Caches Instead”).

在实现他人将要调用的函数时，除非这种行为在函数名称、参数名称或文档中明确提及，否则不应修改提供的任何可变值。为了避免迭代中的各种陷阱，您还可能希望对接收到的任何参数做一个防御性副本（请参见条目21："在迭代参数时保持谨慎" 和 条目22："在迭代过程中永远不要修改容器，而应使用副本或缓存"）。

When calling a function, you should be careful about passing mutable arguments because your data might get modified, which can cause difficult￾to-spot bugs. For complex objects you control, it can be useful to add helper functions and methods that make it easy to create defensive copies. Alternatively, you can use a more functional style and try to leverage immutable objects and pure functions (see Item 56: “Prefer  `dataclasses` for Creating Immutable Objects”).

在调用函数时，您应该小心传递可变参数，因为您的数据可能会被修改，这可能导致难以发现的错误。对于您控制的复杂对象，添加帮助函数和方法以方便创建防御性副本可能是有用的。或者，您可以采用更函数式的风格，并尝试利用不可变对象和纯函数（请参见条目56："优先使用`dataclasses`来创建不可变对象"）。

**Things to Remember**
- Arguments in Python are passed by reference, meaning their attributes can be mutated by receiving functions and methods.
- Functions should make it clear (with naming and documentation) when they will modify input arguments, and avoid modifying arguments otherwise.
- Creating copies of collections and objects you receive as input is a reliable way to ensure your functions avoid inadvertently modifying data.

**注意事项**
- Python中的参数是通过引用传递的，这意味着接收它们的属性可以被接收函数和方法改变。
- 函数应该清楚地表明（通过命名和文档说明）它们会在何时修改输入参数，并避免在其它情况下修改参数。
- 对接收到的集合和对象创建副本是一种可靠的方法，以确保您的函数不会意外地修改数据。