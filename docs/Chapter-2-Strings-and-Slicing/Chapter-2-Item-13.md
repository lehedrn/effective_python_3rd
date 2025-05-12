# Chapter 2: Strings and Slicing (字符串和切片操作)

## Item 13: Prefer Explicit String Concatenation Over Implicit,Especially In Lists (偏好显式的字符串连接而不是隐式，尤其是在列表中)

Earlier in its history, Python inherited many attributes directly from C, including notation for numeric literals and `printf` -like format strings. The language has evolved considerably since then; for example, octal numbers now require a `0o` prefix instead of only `0` , and the new string interpolation syntax is far superior (see Item 11: “Prefer Interpolated F￾Strings Over C-style Format Strings and str.format ”). However, one C-like feature that remains in Python is implicit string concatenation. This causes string literals that are adjacent expressions to be concatenated without the need for an infix `+` operator. That means that these two assignments actually do the same thing:

在Python早期的历史上，它从C语言直接继承了许多属性，包括数字字面量的表示法和类似`printf`的格式化字符串。自那时以来，这门语言已经进化得相当多；例如，八进制数现在需要以`0o`前缀而不是仅以`0`开头，并且新的字符串插值语法远远优于旧的方式（参见条目11）。然而，Python中仍然保留了一个类似C的功能是隐式字符串连接。这意味着相邻表达式的字符串字面量可以被合并而无需中缀`+`运算符。也就是说，以下两个赋值实际上做了同样的事情：

```
my_test1 = "hello" "world"
my_test2 = "hello" + "world"
assert my_test1 == my_test2
```

This implicit concatenation behavior can be useful when you need to combine different types of string literals with varying escaping requirements, which is a common need in programs that do text templating or code generation. For example, here I implicitly merge a raw string, f-string, and single quoted string:

这种隐式连接行为在你需要将具有不同转义需求的不同类型的字符串模板或代码生成程序中的字符串字面量结合在一起时可能是有用的。例如，这里我隐式地合并了一个原始字符串、一个f-string和一个单引号字符串：

```
x = 1
my_test1 = (
 r"first \ part is here with escapes\n, "
 f"string interpolation {x} in here, "
 'this has "double quotes" inside'
)
print(my_test1)

>>>
first \ part is here with escapes\n, string interpolation 1 in here, this has "double quotes" inside
```

Having each type of string literal on its own line makes this code easier to read, and the absence of operators reduces visual noise. In contrast, when implicit concatenation happens on a single line, it can be difficult to anticipate what the code is going to do without having to pay extra attention:

将每种类型的字符串字面量放在自己的行上使得这段代码更容易阅读，并且没有运算符减少了视觉上的干扰。相比之下，当隐式连接发生在单一行上时，如果不特别注意，就很难预测代码会做什么：

```
y = 2
my_test2 = r"fir\st" f"{y}" '"third"'
print(my_test2)
>>>
fir\st2"third"
```

Implicit concatenation like this is also error-prone. If you accidentally slip in a comma character between adjacent strings, the meaning of the code will be completely different (see a similar issue in Item 6: “Always Surround Single-Element Tuples with Parentheses”):

像这样的隐式连接也很容易出错。如果你在相邻的字符串之间不小心插入了一个逗号字符，代码的意义将会完全不同（参见与之相似的问题，条目6）：

```
my_test3 = r"fir\st", f"{y}" '"third"'
print(my_test3)

>>>
('fir\\st', '2"third"')
```

Another problem can occur if you do the opposite and accidentally delete a comma instead of adding one. For example, imagine that I want to create a list of strings to output, with one element for each line:

另一个问题可能发生在你做了相反的事情并且意外删除了逗号而不是添加它的时候。例如，假设我想创建一个要输出的字符串列表，每个元素对应一行：

```
my_test4 = [
 "first line\n",
 "second line\n",
 "third line\n",
]
print(my_test4)
>>>
['first line\n', 'second line\n', 'third line\n']
```

If I delete the middle comma, the resulting data will have similar structure, but the last two lines will be merged together silently.

如果我删除中间的逗号，结果数据将具有类似的结构，但最后两行将被静默地合并在一起。

```
my_test5 = [
 "first line\n",
 "second line\n" # Comma removed
 "third line\n",
]
print(my_test5)
>>>
['first line\n', 'second line\nthird line\n']
```

As a new reader of this code, you might not even see the missing comma at first glance. If you use an auto-formatter (see Item 2: “Follow the PEP 8 Style Guide”), it might rewrap the two lines to make this implicit behavior more discoverable, like this:

作为这段代码的新读者，你可能第一眼看不到丢失的逗号。如果你使用自动格式化工具（参见条目2：“遵循PEP 8风格指南”），它可能会重新包装这两行以使这种隐式行为更易发现，如下所示：

```
my_test5 = [
 "first line\n",
 "second line\n" "third line\n",
]
```

But even if you do notice that implicit concatenation is happening, it’s unclear whether it’s deliberate or accidental. Thus, my advice is to always use an explicit `+` operator to combine strings inside of a `list` or `tuple` literal to eliminate any ambiguity caused by implicit concatenation:

但即使你注意到正在发生隐式连接，也很难判断这是故意的还是偶然的。因此，我的建议是在`list`或`tuple`字面量内部总是使用显式的`+`运算符来组合字符串，以消除由隐式连接引起的任何歧义：

```
my_test6 = [
 "first line\n",
 "second line\n" + # Explicit
 "third line\n",
]
assert my_test5 == my_test6
```

When the `+` operator is present, an auto-formatter might still change the line wrapping, but in this state it’s at least clear what the author of the code originally intended:

当存在+运算符时，自动格式化工具可能仍会改变行的换行方式，但在这种状态下，至少清楚作者最初打算做什么：

```
my_test6 = [
 "first line\n",
 "second line\n" + "third line\n",
]
```

Another place that implicit string concatenation might cause issues is in function call argument lists. Sometimes using implicit concatenation within a call looks fine, such as with the `print` function:

另一个可能导致问题的隐式字符串连接的地方是在函数调用参数列表中。有时在调用函数时使用隐式连接看起来很好，比如对于`print`函数：

```
print("this is my long message "
      "that should be printed out")
>>>
this is my long message that should be printed out
```

Implicit concatenation can even be readable when you provide additional keyword arguments after a single positional argument:

即使你在提供额外的关键字参数后使用单个位置参数，隐式连接甚至也可以是可读的：

```
import sys

print("this is my long message "
      "that should be printed out",
      end="",
      file=sys.stderr)
```

However, when a call takes multiple positional arguments, implicit string concatenation can be confusing and error-prone just like it is with `list` and `tuple` literals. For example, here I create an instance of a class with implicit concatenation in the middle of the initialization argument list—how quickly can you spot it?

然而，当一个调用采用多个位置参数时，隐式字符串连接可能就像它在`list`和`tuple`字面量中那样令人困惑且容易出错。例如，这里我在初始化参数列表中间创建一个类实例并进行隐式连接——你能快速发现吗？

```
import sys

first_value = ...
second_value = ...

class MyData:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

value = MyData(123,
               first_value,
               f"my format string {x}"
               f"another value {y}",
               "and here is more text",
               second_value,
               stream=sys.stderr)
```

Changing the string concatenation to be explicit makes this code much easier to scan:

将字符串连接改为显式会使此代码更容易扫描：

```
value2 = MyData(123,
                first_value,
                f"my format string {x}" +  # Explicit
                f"another value {y}",
                "and here is more text",
                second_value,
                stream=sys.stderr)
```

My advice is to always use explicit string concatenation when a function call takes multiple positional arguments in order to avoid any confusion (see Item 36: “Enforce Clarity with Keyword-Only and Positional-Only Arguments” for a similar example). If there’s only a single positional argument, as with the `print` example above, then using implicit string concatenation is fine. Keyword arguments can be passed using either explicit or implicit concatenation—whichever maximizes clarity—because sibling string literals can’t be misinterpreted as positional arguments after the `=` character.

我的建议是，当一个函数调用采用多个位置参数时，应始终使用显式字符串连接以避免任何混淆（参见条目36）。如果只有一个位置参数，如上面的`print`示例，则使用隐式字符串连接是可以的。关键字参数可以用任一显式或隐式连接传递——无论哪种都能最大化清晰度——因为在`=`字符之后的兄弟字符串字面量不能被误解为位置参数。

**Things to Remember**

- When two string literals are next to each other in Python code, they will be merged as if the `+` operator were present between them, in a similar fashion to the implicit string concatenation feature of the C programming language.
- Implicit string concatenation of items in `list` and `tuple` literals should be avoided because it’s ambiguous what the original author’s intent was. Instead, you should use explicit concatenation with the `+` operator.
- In function calls, implicit string concatenation is fine to use with one positional argument and any number of keyword arguments, but explicit concatenation should be used when there are multiple positional arguments.

**注意事项**

- 当两个字符串字面量在Python代码中彼此相邻时，它们将被合并，就像它们之间有`+`运算符一样，类似于C编程语言中的隐式字符串连接功能。
- 应避免对`list`和`tuple`字面量中的项目进行隐式字符串连接，因为原作者的意图是什么并不明确。相反，你应该使用带有`+`运算符的显式连接。
- 在函数调用中，隐式字符串连接可以在有一个位置参数和任意数量的关键字参数以及任何数量的关键字参数时很好地使用，但在有多个位置参数时应该使用显式连接。