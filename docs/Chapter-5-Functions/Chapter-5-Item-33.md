# Chapter 5: Functions (函数)

## Item 33: Know How Closures Interact with Variable Scope and `nonlocal` (了解闭包如何与变量作用域和nonlocal交互)

Imagine that I want to sort a `list` of numbers but prioritize one group of numbers to come first. This pattern is useful when you’re rendering a user interface and want important messages or exceptional events to be displayed before everything else. A common way to do this is to pass a helper function as the `key` argument to a list’s `sort` method (see Item 100: “Sort by Complex Criteria Using the key Parameter” for details). The helper’s return value will be used as the value for sorting each item in the `list` . The helper can check whether the given item is in the important group and can vary the sorting value accordingly:

假设我想要对一个数字列表进行排序，但优先将一组数字排在前面。这种模式在渲染用户界面时非常有用，可以将重要消息或异常事件显示在所有其他内容之前。一种常见的做法是将辅助函数作为`key`参数传递给列表的`sort`方法（详情请参见条目100：“使用key参数通过复杂准则排序”）。辅助函数的返回值将用作列表中每个项目的排序依据：

```
def sort_priority(values, group):
    def helper(x):
        if x in group:
            return (0, x)
        return (1, x)

    values.sort(key=helper)
```

This function works for simple inputs:

这个函数对于简单输入是有效的：

```
numbers = [8, 3, 1, 2, 5, 4, 7, 6]
group = {2, 3, 5, 7}
sort_priority(numbers, group)
print(numbers)
>>>
[2, 3, 5, 7, 1, 4, 6, 8]
```

There are three reasons this function operates as expected:

此函数能够按预期运行有三个原因：

- Python supports closures—that is, functions that refer to variables from the scope in which they were defined. This is why the `helper` function is able to access the `group` argument for the `sort_priority` function.

- Python 支持闭包——即引用定义它们的作用域中的变量的函数。这就是为什么 `helper` 函数能够访问 `sort_priority` 函数的 `group` 参数。

- Functions are first-class objects in Python, which means you can refer to them directly, assign them to variables, pass them as arguments to other functions, compare them in expressions and `if` statements, and so on. This is how the `sort` method can accept a closure function as the `key` argument.

- 在 Python 中，函数是一等公民，这意味着你可以直接引用它们，将它们赋值给变量，作为参数传递给其他函数，在表达式和 `if` 语句中比较它们等等。这使得 `sort` 方法可以接受一个闭包函数作为 `key` 参数。

- Python has specific rules for comparing sequences (including tuples). It first compares items at index zero; then, if those are equal, it compares items at index one; if they are still equal, it compares items at index two, and so on. This is why the return value from the `helper` closure causes the sort order to have two distinct groups.

- Python 对于比较序列（包括元组）有特定规则。它首先比较索引为零的项目；如果这些相等，则比较索引为一的项目；如果仍然相等，则比较索引为二的项目，依此类推。这就是为什么从 `helper` 闭包返回的值会导致排序顺序有两个不同的组。

It’d be nice if this function returned whether higher-priority items were seen at all so the user interface code can act accordingly. Adding such behavior seems straightforward. There’s already a closure function for deciding which group each number is in. Why not also use the closure to flip a flag when high-priority items are seen? Then, the function can return the flag value after it’s been modified by the closure.

如果此函数能返回是否看到更高优先级的项目就更好了，这样用户界面代码就可以据此采取行动。添加这样的行为看似直接。已经有一个闭包函数来决定每个数字属于哪个组。为什么不也使用闭包来翻转标志，当发现高优先级项目时呢？然后，该函数可以在被闭包修改后返回标志值。

Here, I try to do that in a seemingly obvious way:

下面尝试以一种看似明显的方式实现这一点：

```
def sort_priority2(numbers, group):
    found = False         # Flag initial value

    def helper(x):
        if x in group:
            found = True  # Flip the flag
            return (0, x)
        return (1, x)

    numbers.sort(key=helper)
    return found          # Flag final value
```

I can run the function on the same inputs as before:

可以用之前的相同输入运行该函数：

```
found = sort_priority2(numbers, group)
print("Found:", found)
print(numbers)
>>>
Found: False
[2, 3, 5, 7, 1, 4, 6, 8]
```

The sorted results are correct, which means items from `group` were definitely found in `numbers` . Yet the `found` result returned by the function is `False` when it should be `True` . How could this happen? When you reference a variable in an expression, the Python interpreter traverses the nested scopes to resolve the reference in this order:

排序结果是正确的，这意味着在 `numbers` 中确实找到了 `group` 中的项目。然而，由函数返回的 `found` 结果却是 `False` 而不是 `True`。怎么会这样呢？当你在一个表达式中引用一个变量时，Python 解释器会按照以下顺序遍历嵌套作用域来解析该引用：

1. The current function’s scope.
2. Any enclosing scopes (such as other containing functions).
3. The scope of the module that contains the code (also called the global scope).
4. The built-in scope (that contains functions like len and str ).

1. 当前函数的作用域。
2. 任何封闭作用域（如包含的其他函数）。
3. 包含代码的模块的作用域（也称为全局作用域）。
4. 内建作用域（包含诸如 len 和 str 这样的函数）。

If none of these places has defined a variable with the referenced name, then a `NameError` exception is raised:

如果这些位置都没有定义具有所引用名称的变量，则会引发 `NameError` 异常：

```
foo = does_not_exist * 5
>>>
Traceback ...
NameError: name 'does_not_exist' is not defined
```

Assigning a value to a variable works differently. If the variable is already defined in the current scope, that name will take on the new value in that scope. If the variable doesn’t exist in the current scope, Python treats the assignment as a variable definition. Critically, the scope of the newly defined variable is the function that contains the assignment, not an enclosing scope with an earlier assignment.

赋值给一个变量的工作方式不同。如果变量已经在当前作用域中定义，那么该名称将在该作用域中取新的值。如果变量在当前作用域中不存在，Python 会将赋值视为新变量的定义。关键在于，新定义的变量的作用域是包含赋值的函数，而不是先前赋值的封闭作用域。

This assignment behavior explains the wrong return value of the `sort_priority2` function. The `found` variable is assigned to `True` in the `helper` closure. The closure’s assignment is treated as a new variable definition within the scope of `helper` , not as an assignment within the scope of `sort_priority2` :

这种赋值行为解释了 `sort_priority2` 函数返回错误值的原因。在 `helper` 闭包中将 `found` 变量赋值为 `True`。闭包的赋值被视为在 `helper` 的作用域内一个新的变量定义，而不是在 `sort_priority2` 的作用域内的赋值：

```
def sort_priority2(numbers, group):
    found = False          # Scope: 'sort_priority2'

    def helper(x):
        if x in group:
            found = True   # Scope: 'helper' -- Bad!
            return (0, x)
        return (1, x)

    numbers.sort(key=helper)
    return found
```

This problem is sometimes called the scoping bug because it can be so surprising to newbies. But this behavior is the intended result: It prevents local variables in a function from polluting the containing module. Otherwise, every assignment within a function would put garbage into the global module scope. Not only would that be noise, but the interplay of the resulting global variables could cause obscure bugs.

这个问题有时被称为作用域 bug，因为它可能让新手感到惊讶。但是这种行为是有意为之的：它可以防止函数中的局部变量污染包含模块。否则，每次函数内的赋值都会将垃圾放入全局模块作用域中。不仅会产生噪音，由此产生的全局变量之间的相互作用可能导致晦涩难懂的错误。

In Python, there is special syntax for assigning data outside of a closure’s scope. The `nonlocal` statement is used to indicate that scope traversal should happen upon assignment for a specific variable name. The only limit is that `nonlocal` won’t traverse up to the module-level scope (to avoid polluting globals).

在 Python 中，有一种特殊的语法用于在闭包外的作用域中赋值。`nonlocal` 语句用于指示在特定变量名上进行赋值时应该发生作用域遍历。唯一的限制是 `nonlocal` 不会上溯到模块级作用域（以避免污染全局变量）。

Here, I define the same function again, now using `nonlocal` :

下面再次定义相同的函数，现在使用 `nonlocal`：

```
def sort_priority3(numbers, group):
    found = False

    def helper(x):
        nonlocal found  # Added
        if x in group:
            found = True
            return (0, x)
        return (1, x)

    numbers.sort(key=helper)
    return found

```

Now the found flag works as expected:

现在 `found` 标志按预期工作：

```
found = sort_priority3(numbers, group)
print("Found:", found)
print(numbers)
>>>
Found: True
[2, 3, 5, 7, 1, 4, 6, 8]
```

The `nonlocal` statement makes it clear when data is being assigned out of a closure and into another scope. It’s complementary to the `global` statement, which indicates that a variable’s assignment should go directly into the module scope.

`nonlocal` 语句明确了数据在闭包之外赋值到另一个作用域的情况。它与 `global` 语句相对应，后者表示变量的赋值应该直接进入模块作用域。

However, much as with the anti-pattern of global variables, I’d caution against using `nonlocal` for anything beyond simple functions. The side effects of `nonlocal` can be hard to follow. It’s especially hard to understand in long functions where the `nonlocal` statements and assignments to associated variables are far apart.

不过，正如全局变量的反模式一样，我建议不要在简单的函数之外使用 `nonlocal`。`nonlocal` 的副作用很难跟踪。特别是在长函数中，当 `nonlocal` 语句和相关变量的赋值相隔很远时，尤其难以理解。

When your usage of `nonlocal` starts getting complicated, it’s better to wrap your state in a helper class. Here, I define a class that can be called like a function; it achieves the same result as the `nonlocal` approach by assigning an object’s attribute during sorting (see Item 55: “Prefer Public Attributes Over Private Ones”):

当你的 `nonlocal` 使用开始变得复杂时，最好将状态包装在一个帮助类中。这里定义了一个可以像函数一样调用的 `Sorter` 类；它通过在排序期间分配对象属性来实现与 `nonlocal` 相同的结果（有关 call 特殊方法的详细信息，请参见条目 55：“偏好使用公共属性而非私有属性”）：

```
class Sorter:
    def __init__(self, group):
        self.group = group
        self.found = False

    def __call__(self, x):
        if x in self.group:
            self.found = True
            return (0, x)
        return (1, x)
```

It’s a little longer than before, but it’s much easier to reason about and extend if needed (see Item 48: “Accept Functions Instead of Classes for Simple Interfaces” for details on the `__call__` special method). I can access the `found` attribute on the `Sorter` instance to get the result:

虽然比以前略长一些，但如果需要的话，它更容易理解和扩展（有关详细信息，请参见条目 48：“对于简单接口，首选函数而不是类”）。我可以访问 `Sorter` 实例上的 `found` 属性来获取结果：

```
sorter = Sorter(group)
numbers.sort(key=sorter)
print("Found:", sorter.found)
print(numbers)
>>>
Found: True
[2, 3, 5, 7, 1, 4, 6, 8]
```

**Things to Remember**
- Closure functions can refer to variables from any of the enclosing scopes in which they were defined.
- By default, closures can’t affect enclosing scopes by assigning variables.
- Use the `nonlocal` statement to indicate when a closure can modify a variable in its enclosing scopes. Use the `global` statement to do the same thing for module-level names.
- Avoid using nonlocal statements for anything beyond simple functions.

**注意事项**
- 闭包函数可以引用其定义所在的任何封闭作用域中的变量。
- 默认情况下，闭包不能通过赋值变量影响封闭作用域。
- 使用 `nonlocal` 语句来表示闭包可以修改其封闭作用域中的变量。使用 `global` 语句对模块级别的名称执行相同操作。
- 避免在除简单函数之外的任何地方使用 `nonlocal` 语句。