# Chapter 2: Strings and Slicing (字符串和切片操作)

## Item 12: Understand the Difference Between repr and str When Printing Objects (理解打印对象时`repr`和`str`的区别)

While debugging a Python program, the `print` function and format strings (see Item 11: “Prefer Interpolated F-Strings Over C-style Format Strings and str.format ”), or output via the `logging` built-in module, will get you surprisingly far. Python internals are often easy to access via plain attributes (see Item 54: “Prefer Public Attributes Over Private Ones”). All you need to do is `print` how the state of your program changes while it runs and see where it goes wrong (see Item 114: "Consider Interactive Debugging with pdb“ for a more advanced approach).

在调试一个Python程序时，使用`print`函数和格式化字符串（参见条目11），或者通过内置的`logging`模块输出信息，都能让你事半功倍。Python的内部机制通常可以通过简单的属性访问来实现（参见条目54）。你所需要做的就是用`print`输出程序运行过程中状态的变化，然后查看哪里出错了（对于更高级的方法，请参见条目114）。

The `print` function outputs a human-readable string version of whatever you supply it. For example, printing a basic string will show the contents of the string without the surrounding quote characters:

`print`函数会以人类可读字符串输出你提供给它的任何内容。例如，打印一个基本的字符串将显示字符串的内容而不包括周围的引号字符：

```
print("foo bar")
>>>
foo bar
```

This is equivalent to all of these alternatives:

- Calling the `str` function before passing the value to `print` .
- Using the `'%s'` format string with the `%` operator.
- Default formatting of the value with an f-string.
- Calling the `format` built-in function.
- Explicitly calling the `__format__` special method.
- Explicitly calling the `__str__` special method.

这等价于以下所有替代方法：

- 在将值传递给`print`之前调用`str`函数。
- 使用`'%s'`格式字符串与`%`运算符。
- 使用`f-string`默认格式化值。
- 调用内置的`format`函数。
- 显式调用`__format__`特殊方法。
- 显式调用`__str__`特殊方法。

Here, I show that they all produce the same output:

这里我展示了它们如何产生相同的输出：

```
my_value = "foo bar"
print(str(my_value))
print("%s" % my_value)
print(f"{my_value}")
print(format(my_value))
print(my_value.__format__("s"))
print(my_value.__str__())
>>>
foo bar
foo bar
foo bar
foo bar
foo bar
foo bar
```

The problem is that the human readable string for a value doesn’t make it clear what the actual type and specific composition of the value is. For example, notice how in the default output of `print` you can’t distinguish between the types of the number `5` and the string `'5'` :

问题是，值的人类可读字符串并不能清楚地表明该值的实际类型和具体组成。例如，注意在`print`的默认输出中，你无法区分数字`5`和字符串`'5'`的类型：

```
int_value = 5
str_value = "5"
print(int_value)
print(str_value)
print(f"Is {int_value} == {str_value}?")

>>>
5
5
Is 5 == 5?
```

If you’re debugging a program with `print` , these type differences matter. What you almost always want while debugging is to see the `repr` version of an `object` . The `repr` built-in function returns the printable representation of an `object` , which should be its most clearly understandable string serialization. For many built-in types, the string returned by `repr` is a valid Python expression:

如果你正在使用`print`调试程序，这些类型的差异是很重要的。你在调试时几乎总是想要看到的是`object`的`repr`版本。内置的`repr`函数返回一个`object`的可打印表示，它应该是最易于理解的字符串序列化形式。对于许多内置类型来说，由`repr`返回的字符串是一个有效的Python表达式：

```
a = "\x07"
print(repr(a))
>>>
'\x07'
```

Passing the value returned by `repr` to the `eval` built-in function often results in the same Python object you started with (of course, in practice you should only use `eval` with extreme caution; see Item 90: "Avoid exec and eval Unless You’re Building a Developer Tool"):

将`repr`返回的值传递给内置的`eval`函数通常会导致得到你最初使用的相同的Python对象（当然，在实践中你应该只在极端谨慎的情况下使用`eval`；请参见条目90）：

```
b = eval(repr(a))
assert a == b
```

When you’re debugging with `print` , you can `repr` the value before printing to ensure that any difference in types is clear:

当你使用`print`进行调试时，可以先对值进行`repr`处理以确保任何类型的差异都是清晰的：

```
print(repr(int_value))
print(repr(str_value))

>>>
5
'5'
```

This is equivalent to using the `'%r'` format string with the `%` operator, or an f-string with the `!r` type conversion:

这相当于使用带有`%r`格式字符串的%运算符，或带有`!r`类型转换的`f-string`：

```
print("Is %r == %r?" % (int_value, str_value))
print(f"Is {int_value!r} == {str_value!r}?")

>>>
Is 5 == '5'?
Is 5 == '5'?
```

When the `str` built-in function is given an instance of a user-defined class it will first try to call the `__str__` special method. If that’s not defined, it will fall back to call the `__repr__` special method instead. If `__repr__` also wasn’t implemented by the class, then it will go through method resolution (see Item 52: "Initialize Parent Classes with super"), eventually calling the default implementation from the `object` parent class. Unfortunately, the default implementation of `repr` by `object` isn’t especially helpful. For example, here I define a simple class and then print one of its instances, which ultimately leads to a call to `object.__repr__` :

当`str`内建函数被赋予一个用户定义类的实例时，它会首先尝试调用`__str__`特殊方法。如果未定义该方法，则会回退到调用`__repr__`特殊方法。如果`__repr__`也未被该类实现，则它将通过方法解析（参见条目52）最终调用来自`object`父类的默认实现。不幸的是，默认的`repr`实现并不特别有用。例如，这里我定义了一个简单的类，然后打印了它的一个实例，这最终导致调用了`object.__repr__`：

```
class OpaqueClass:
    def __init__(self, x, y):
        self.x = x
        self.y = y

obj = OpaqueClass(1, "foo")
print(obj)

>>>
<__main__.OpaqueClass object at 0x000002A79F3F24B0>
```

This output can’t be passed to the `eval` function, and it says nothing about the instance fields of the object. To improve this, here I define my own `__repr__` special method that returns a string containing the Python expression that recreates the object (see Item 50: "Prefer dataclasses For Defining Light-Weight Classes" for another approach to defining `__repr__` ):

这个输出不能传递给`eval`函数，并且它没有说明对象的实例字段。为了改进这一点，我在下面定义了自己的`__repr__`特殊方法，该方法返回包含用于重新创建对象的Python表达式的字符串（参见条目50）：

```
class BetterClass:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __repr__(self):
        return f"BetterClass({self.x!r}, {self.y!r})"
```

Now the `repr` value is much more useful:

现在`repr`的值更有用了：

```
obj = BetterClass(2, "bar")
print(obj)
>>>
BetterClass(2, 'bar')
```

Calling `str` on an instance of this class will produce the same result because the `__str__` special method isn’t defined, causing Python to fall back to `__repr__` :

对这个类的实例调用`str`会产生相同的结果，因为没有定义`__str__`特殊方法，导致Python回退到`__repr__`：

```
print(str(obj))

>>>
BetterClass(2, 'bar')
```

To have `str` print out a different human-readable format of the string——for example, to display in a UI element——I can define the corresponding `__str__` special method:

为了让`str`打印出不同的人类可读的字符串格式——例如，在UI元素中显示——我可以定义相应的`__str__`特殊方法：

```
class StringifiableBetterClass(BetterClass):
    def __str__(self):
        return f"({self.x}, {self.y})"
```

Now calling `repr` and `str` on the object return different human￾readable strings for each of the different purposes:

现在对对象调用`repr`和`str`会为不同目的返回不同的可读字符串：

```
obj2 = StringifiableBetterClass(2, "bar")
print("Human readable:", obj2)
print("Printable: ", repr(obj2))

>>>
Human readable: (2, bar)
Printable: BetterClass(2, 'bar')
```

**Things to Remember**

- Calling `print` on built-in Python types will produce the human￾readable string version of a value, which hides type information.
- Calling `repr` on built-in Python types will produce a string containing the printable representation of a value. These `repr` strings can often be passed to the `eval` built-in function to get back the original value.
- `%s` in format strings will produce human-readable strings like `str` . `%r` will produce printable strings like `repr` . f-strings produce human readable strings for replacement text expressions unless you specify the `!r` conversion suffix.
- You can define the `__repr__` and `__str__` special methods on your classes to customize the printable and human-readable representations of instances, which can help with debugging and can simplify integrating objects into human interfaces.

**注意事项**

- 对内置Python类型调用`print`将生成值的人类可读字符串版本，这会隐藏类型信息。
- 对内置Python类型调用`repr`将生成包含值的可打印表示的字符串。这些`repr`字符串经常可以传递给内置的`eval`函数以获得原始值。
- 格式字符串中的`%s`将生成像`str`一样的人类可读字符串。`%r`将生成像`repr`一样的可打印字符串。`f-string`在替换文本表达式时生成人类可读的字符串，除非你指定`!r`转换后缀。
- 您可以在自己的类上定义`__repr__`和`__str__`特殊方法，以自定义实例的可打印和人类可读表示形式，这有助于调试并可以简化将对象集成到人类界面中。