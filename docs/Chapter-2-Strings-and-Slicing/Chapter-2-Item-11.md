# Chapter 2: Strings and Slicing (字符串和切片操作)

## Item 11: Prefer Interpolated F-Strings Over C-style Format Strings and str.format (优先使用插值格式化字符串（f-strings）而不是 C 风格的格式化字符串和 str.format)

Strings are present throughout Python codebases. They’re used for rendering messages in user interfaces and command-line utilities. They’re used for writing data to files and sockets. They’re used for specifying what’s gone wrong in Exception details (see Item 87: “Consider Explicitly Chaining Exceptions to Clarify Tracebacks”). They’re used in logging and debugging (see Item 12: “Understand the Difference Between repr and str When Printing Objects”).

字符串在 Python 的代码库中无处不在。它们用于渲染用户界面和命令行工具中的消息，用于向文件和套接字写入数据，用于异常信息中说明问题所在（参见条目 87），也用于日志记录和调试（参见条目 12）。

Formatting is the process of combining predefined text with data values into a single human-readable message that’s stored as a string. Python has four different ways of formatting strings that are built into the language and standard library. All but one of them, which is covered last in this item, have serious shortcomings that you should understand and avoid.

格式化是指将预定义文本与数据值结合成一个单一的人类可读的字符串消息的过程。Python 提供了四种内置的语言和标准库支持的字符串格式化方式。其中只有一种方式没有严重的缺陷——这也是本条目最后要介绍的方式。

**C-style Formatting**

**C 风格的格式化**

The most common way to format a string in Python is by using the `%` formatting operator. A predefined text template is provided on the left side of the operator in a format string. Values to insert into the template are provided as a single value or tuple of multiple values on the right side of the format operator. For example, here I use the `%` operator to convert difficult-to-read binary and hexadecimal values to integer strings:

Python 中最常见的字符串格式化方法是使用 % 格式化运算符。在运算符左侧提供一个预定义的模板，在右侧提供一个单个值或多个值组成的元组。例如，这里我使用 % 运算符将难以阅读的二进制和十六进制值转换为整数字符串：

```
a = 0b10111011
b = 0xC5F
print("Binary is %d, hex is %d" % (a, b))

>>>
Binary is 187, hex is 3167
```

The format string uses format specifiers (like %d ) as placeholders that will be replaced by values from the right side of the formatting expression. The syntax for format specifiers comes from C’s printf function, which has been inherited by Python (as well as by other programming languages). Python supports all of the usual options you’d expect from printf , such as %s , %x , and %f format specifiers, as well as control over decimal places, padding, fill, and alignment. Many programmers who are new to Python start with C-style format strings because they’re familiar and simple to use.

格式字符串使用像 `%d` 这样的格式说明符作为占位符，这些占位符会被右侧表达式的值替换。这种语法来源于 C 的 `printf` 函数，并被 Python（以及其他语言）继承。Python 支持所有你期望的标准选项，如 `%s`,` %x`, `%f` 等，以及对小数点、填充、对齐等的控制。许多刚接触 Python 的程序员会使用 C 风格的格式字符串，因为它们熟悉且易于使用。

There are four problems with C-style format strings in Python.

然而，C 风格的格式字符串在 Python 中存在四个主要问题。

The first problem is that if you change the type or order of data values in the tuple on the right side of a formatting expression, you can get errors due to type conversion incompatibility. For example, this simple formatting expression works:

第一个问题: 如果你改变了右侧元组中数据值的类型或顺序，可能会因类型转换不兼容而导致错误。例如，这个简单的格式化表达式可以正常工作：

```
key = "my_var"
value = 1.234
formatted = "%-10s = %.2f" % (key, value)
print(formatted)

>>>
my_var = 1.23
```

But if you swap key and value , you get an exception at runtime:

但如果你交换 key 和 value 的位置，就会在运行时抛出异常：

```
reordered_tuple = "%-10s = %.2f" % (value, key)

>>>
Traceback ...
TypeError: must be real number, not str
```

Similarly, leaving the right side parameters in the original order but changing the format string results in the same error.

同样，如果保持参数顺序不变但修改格式字符串，也会导致相同的错误：

```
reordered_string = "%.2f = %-10s" % (key, value)

>>>
Traceback ...
TypeError: must be real number, not str
```

To avoid this gotcha, you need to constantly check that the two sides of the `%` operator are in sync; this process is error prone because it must be done manually for every change.

为了避免这个问题，你需要不断检查 % 运算符两边是否同步；这是一个容易出错的过程，因为每次更改都必须手动完成。

The second problem with C-style formatting expressions is that they become difficult to read when you need to make small modifications to values before formatting them into a string—and this is an extremely common need. Here, I list the contents of my kitchen pantry without making any inline changes to the values:

第二个问题: 当需要在格式化之前对值做一些小的修改时，C 风格的格式化字符串变得难以阅读。例如，这里我列出厨房储藏室的内容，没有任何修改：

```
pantry = [
 ("avocados", 1.25),
 ("bananas", 2.5),
 ("cherries", 15),
]

for i, (item, count) in enumerate(pantry):
 print("#%d: %-10s = %.2f" % (i, item, count))
>>>
#0: avocados = 1.25
#1: bananas = 2.50
#2: cherries = 15.00
```

Now, I make a few modifications to the values that I’m formatting to make the printed message more useful. This causes the tuple in the formatting expression to become so long that it needs to be split across multiple lines, which hurts readability:

现在，我做了一些修改以使输出更有用。这会导致格式化表达式中的元组变得很长，不得不跨多行书写，从而影响可读性：

```
for i, (item, count) in enumerate(pantry):
 print(
 "#%d: %-10s = %d"
 % (
 i + 1,
 item.title(),
 round(count),
 )
 )
>>>
#1: Avocados = 1
#2: Bananas = 2
#3: Cherries = 15
```

The third problem with formatting expressions is that if you want to use the same value in a format string multiple times, you have to repeat it in the right side `tuple` :

第三个问题: 如果你想在一个格式字符串中多次使用同一个值，你就必须在右侧的 tuple 中重复它：

```
template = "%s loves food. See %s cook."
name = "Max"
formatted = template % (name, name)
print(formatted)

>>>
Max loves food. See Max cook.
```

This is especially annoying and error prone if you have to repeat small modifications to the values being formatted. For example, here I call the `title()` method on one reference to name but not the other, causing mismatched output:

如果你不小心重复的是稍作修改后的值，就可能导致输出不一致。例如，下面我只对其中一个 name 调用了 title() 方法：

```
name = "brad"
formatted = template % (name.title(), name)
print(formatted)

>>>
Brad loves food. See brad cook.
```

To help solve some of these problems, the `%` operator in Python has the ability to also do formatting with a dictionary instead of a `tuple` . The keys from the dictionary are matched with format specifiers that have the same name, such as `%(key)s` . Here, I use this functionality to change the order of values on the right side of the formatting expression with no effect on the output, thus solving problem #1 from above:

为了解决这些问题，Python 的 `%` 运算符还支持使用字典进行格式化。你可以通过 `%(key)s` 的形式引用字典中的键。例如，这样可以解决上面提到的第一个问题：

```
key = "my_var"
value = 1.234
old_way = "%-10s = %.2f" % (key, value)
new_way = "%(key)-10s = %(value).2f" % {
 "key": key, # Key first
 "value": value,
}
reordered = "%(key)-10s = %(value).2f" % {
 "value": value,
 "key": key, # Key second
}
assert old_way == new_way == reordered
```

Using dictionaries in formatting expressions also solves problem #3 from above by allowing multiple format specifiers to reference the same value, thus making it unnecessary to supply that value more than once:

使用字典还可以解决第三个问题，即允许格式字符串中多次引用同一个值，而无需重复传入：

```
name = "Max"
template = "%s loves food. See %s cook."
before = template % (name, name)   # Tuple
template = "%(name)s loves food. See %(name)s cook."
after = template % {"name": name}  # Dictionary
assert before == after
```

However, dictionary format strings introduce and exacerbate other issues. For problem #2 above, regarding small modifications to values before formatting them, formatting expressions become longer and more visually noisy because of the presence of the dictionary key and colon operator on the right side. Here, I render the same string with and without dictionaries to show this problem:

然而，使用字典格式化引入并加剧了其他问题。对于第二个问题（格式化前的小修改），由于字典中每个键都需要写一次，表达式变得更长更混乱：

```
for i, (item, count) in enumerate(pantry):
    before = "#%d: %-10s = %d" % (
        i + 1,
        item.title(),
        round(count),
    )

    after = "#%(loop)d: %(item)-10s = %(count)d" % {
        "loop": i + 1,
        "item": item.title(),
        "count": round(count),
    }

    assert before == after
```

Using dictionaries in formatting expressions also increases verbosity, which is problem #4 with C-style formatting expressions in Python. Each key must be specified at least twice—once in the format specifier, once in the dictionary as a key, and potentially once more for the variable name that contains the dictionary value:

此外，使用字典还会增加冗余，这是第四个问题。每个键至少要写两次 —— 一次在格式字符串中，一次在字典中，甚至可能还有变量名：

```
soup = "lentil"
formatted = "Today's soup is %(soup)s." % {"soup": soup}
print(formatted)

>>>
Today's soup is lentil.
```

Besides the duplicative characters, this redundancy causes formatting expressions that use dictionaries to be long. These expressions often must span multiple lines, with the format strings being concatenated across multiple lines, and the dictionary assignments having one line per value to use in formatting:

除了重复字符外，这种冗余还会导致格式化表达式变长，经常需要跨多行书写：

```
menu = {
    "soup": "lentil",
    "oyster": "kumamoto",
    "special": "schnitzel",
}
template = (
    "Today's soup is %(soup)s, "
    "buy one get two %(oyster)s oysters, "
    "and our special entrée is %(special)s."
)
formatted = template % menu
print(formatted)

>>>
Today's soup is lentil, buy one get two kumamoto oysters, and our special entrée is schnitzel.
```

To understand what this formatting expression is going to produce, your eyes have to keep going back and forth between the lines of the format string and the lines of the dictionary. This disconnect makes it hard to spot bugs, and readability gets even worse if you need to make small modifications to any of the values before formatting.

为了理解这段格式化表达式的结果，你的目光需要在格式字符串和字典之间来回切换，这使得 bug 更难发现，特别是在有修改需求时。

There must be a better way.

因此，我们迫切需要一种更好的方式。

---

**The `format` Built-in and `str.format`**

**format 内置函数和 str.format**

Python 3 added support for advanced string formatting that is more expressive than the old `C-style` format strings that use the % operator. For individual Python values, this new functionality can be accessed through the `format` built-in function. For example, here I use some of the new options ( `,` for thousands separators and `^` for centering) to format values:

Python 3 添加了对高级字符串格式化的支持，比使用 `%` 运算符的旧 C 风格格式字符串更具表现力。对于单个 Python 值，可以通过 `format` 内建函数访问此新功能。例如，我使用一些新选项（, 表示千位分隔符和 ^ 表示居中）来格式化值：

```
a = 1234.5678
formatted = format(a, ",.2f")
print(formatted)

b = "my string"
formatted = format(b, "^20s")
print("*", formatted, "*")

>>>
1,234.57
*      my string       *
```

You can use this functionality to format multiple values together by calling the new `format` method of the `str` type. Instead of using `C-style` format specifiers like `%d` , you can specify placeholders with `{}` . By default the placeholders in the format string are replaced by the corresponding positional arguments passed to the `format` method in the order in which they appear:

你可以通过调用 `str` 类型的新 `format` 方法将此功能用于一起格式化多个值。代替使用像 `%d` 这样的 C 风格格式指定符，您可以指定带有 `{}` 的占位符。默认情况下，格式字符串中的占位符按它们出现的顺序由传递给 `format` 方法的位置参数替换：

```
key = "my_var"
value = 1.234
formatted = "{} = {}".format(key, value)
print(formatted)

>>>
my_var = 1.234
```

Within each placeholder you can optionally provide a colon character followed by format specifiers to customize how values will be converted into strings (see `https://docs.python.org/3/library/string.html#format-specification-mini-language` for the full range of options):

在每个占位符中，你可以选择性地提供一个冒号字符，后跟格式指定符来自定义值如何转换为字符串（有关完整的选项范围，请参阅 `https://docs.python.org/3/library/string.html#format-specification-mini-language` ）：

```
formatted = "{:<10} = {:.2f}".format(key, value)
print(formatted)

>>>
my_var = 1.23
```

The way to think about how this works is that the `format` specifiers will be passed to the format built-in function along with the value ( `format(value, ".2f")` in the example above). The result of that function call is what replaces the placeholder in the overall formatted string. The formatting behavior can be customized per class using the `__format__` special method.

思考其工作原理的方式是，格式指定符将连同值一起传递给 format 内建函数（如上面的 format(value, '.2f')）。该函数调用的结果替换了整体格式化字符串中的占位符。可以通过 format 特殊方法自定义每类的格式化行为。

Another detail with `str.format` to be careful of is escaping braces ( `{` ). You need to double them ( `{{` ) so they’re not interpreted as a placeholder accidentally, similar to how with C-style format strings you need to double the `%` character to escape it properly:

需要注意的是，`str.format` 中的大括号需要用双大括号 `{{}}` 来转义：

```
print("%.2f%%" % 12.5)
print("{} replaces {{}}".format(1.23))

>>>
12.50%
1.23 replaces {}
```

Within the braces you may also specify the positional index of an argument passed to the `format` method to use for replacing the placeholder. This allows the format string to be updated to reorder the output without requiring you to also change the right side of the formatting expression, thus addressing problem #1 from above:

在花括号内，你还可以指定传递给 `format` 方法的参数的位置索引，以用于替换占位符。这允许你在更新格式字符串以重新排序输出时，不需要同时更改格式表达式的右侧，从而解决了上面的问题 #1：

```
formatted = "{1} = {0}".format(key, value)
print(formatted)

>>>
1.234 = my_var
```

The same positional index may also be referenced multiple times in the format string without the need to pass the value to the `format` method more than once, which solves problem #3 from above:

同一位置索引也可以在格式字符串中多次引用，而无需多次将值传递给 `format` 方法，从而解决了上面的问题 #3：

```
formatted = "{0} loves food. See {0} cook.".format(name)
print(formatted)

>>>
Max loves food. See Max cook.
```

Unfortunately, the new `format` method does nothing to address problem #2 from above, leaving your code difficult to read when you need to make small modifications to values before formatting them. There’s little difference in readability between the old and new options, which are similarly noisy:

不幸的是，新的 `format` 方法无法解决上面的问题 #2，当你需要在格式化前对值进行小修改时，会使你的代码难以阅读。旧选项和新选项之间的可读性几乎没有差异，它们都同样嘈杂：

```
for i, (item, count) in enumerate(pantry):
    old_style = "#%d: %-10s = %d" % (
        i + 1,
        item.title(),
        round(count),
    )

    new_style = "#{}: {:<10s} = {}".format(
        i + 1,
        item.title(),
        round(count),
    )

    assert old_style == new_style
```

There are even more advanced specifier options for the `str.format` method, such as using combinations of dictionary keys and list indexes in placeholders, and coercing values to Unicode and repr strings:

`str.format` 方法使用的指定符还有更多高级选项，例如在占位符中使用字典键和列表索引的组合，以及强制值为 `Unicode` 和 `repr` 字符串：

```
formatted = "First letter is
{menu[oyster][0]!r}".format(menu=menu)
print(formatted)

>>>
First letter is 'k'
```

But these features don’t help reduce the redundancy of repeated keys from problem #4 above. For example, here I compare the verbosity of using dictionaries in C-style formatting expressions to the new style of passing keyword arguments to the `format` method:

但是这些特性并不能帮助减少上述问题 #4 中重复键的冗余。例如，这里我比较了在 C 风格格式表达式中使用字典的冗余与将关键字参数传递给 `format` 方法的新样式：

```
old_template = (
    "Today's soup is %(soup)s, "
    "buy one get two %(oyster)s oysters, "
    "and our special entrée is %(special)s."
)
old_formatted = old_template % {
    "soup": "lentil",
    "oyster": "kumamoto",
    "special": "schnitzel",
}

new_template = (
    "Today's soup is {soup}, "
    "buy one get two {oyster} oysters, "
    "and our special entrée is {special}."
)
new_formatted = new_template.format(
    soup="lentil",
    oyster="kumamoto",
    special="schnitzel",
)

assert old_formatted == new_formatted
```

This style is slightly less noisy because it eliminates some quotes in the dictionary and a few characters in the format specifiers, but it’s hardly compelling. Further, the advanced features of using dictionary keys and indexes within placeholders only provides a tiny subset of Python’s expression functionality. This lack of expressiveness is so limiting that it undermines the value of the `str.format` method overall.

这种风格稍微不那么嘈杂，因为它消除了字典中的一些引号和格式指定符中的一些字符，但这几乎不令人信服。此外，在占位符中使用字典键和索引的高级特性只提供了 Python 表达式功能的一小部分。这种缺乏表现力的情况限制了 str.format 方法的整体价值。

Given these shortcomings and the problems from C-style formatting expressions that remain (problems #2 and #4 from above), I suggest that you avoid the `str.format` method in general. It’s important to know about the new mini-language used in format specifiers (everything after the colon) and how to use the `format` built-in function. But the rest of the `str.format` method should be treated as a historical artifact to help you understand how Python’s new f-strings work and why they’re so great.

鉴于这些不足和仍然存在的 C 风格格式字符串的问题（上面的问题 #2 和 #4），我建议你一般避免使用 str.format 方法。重要的是要知道 format 指定符迷你语言（冒号后的所有内容）以及如何使用 format 内建函数。但 str.format 方法的其余部分应该被视为历史遗留物，以帮助你了解 Python 的新 `f-strings` 如何工作及其为何如此出色。

**Interpolated Format Strings**

**插值格式化字符串（f-strings）**

Python 3.6 added interpolated format strings—f-strings for short—to solve these issues once and for all. This new language syntax requires you to prefix format strings with an `f` character, which is similar to how byte strings are prefixed with a `b` character and raw (unescaped) strings are prefixed with an `r` character.

Python 3.6 添加了插值格式字符串——简称 f-strings——一次性解决这些问题。这种新语言语法要求你使用 `f` 字符作为格式字符串的前缀，这类似于字节字符串前面加 `b` 字符和原始（未转义）字符串前面加 `r` 字符。

F-strings take the expressiveness of format strings to the extreme, solving problem #4 from above by completely eliminating the redundancy of providing keys and values to be formatted. They achieve this pithiness by allowing you to reference all names in the current Python scope as part of a formatting expression:

F-strings 将格式字符串的表现力推向极致，通过完全消除提供键和值进行格式化的冗余来解决上述问题 #4。它们通过允许你引用当前 Python 作用域中的所有名称作为格式化表达式的一部分来实现这一简洁性：

```
key = "my_var"
value = 1.234
formatted = f"{key} = {value}"
print(formatted)

>>>
my_var = 1.234
```

All of the same options from the new `format` built-in mini-language are available after the colon in the placeholders within an f-string, as is the ability to coerce values to Unicode and repr strings similar to the `str.format` method (i.e., with `!r` and `!s` ):

所有来自新的 `format` 内置迷你语言的相同选项都可以在 `f-strings` 的占位符后面的冒号之后使用，正如可以强制值转换为 Unicode 和 repr 字符串一样，类似于 `str.format` 方法：

```
formatted = f"{key!r:<10} = {value:.2f}"
print(formatted)

>>>
'my_var' = 1.23
```

Formatting with f-strings is shorter than using C-style format strings with the `%` operator and the `str.format` method in all cases. Here, I show every option together in order of shortest to longest, and line up the left side of the assignment so you can easily compare them:

与使用 `%` 运算符的 C 风格格式字符串和 `str.format` 方法相比，`f-strings` 的格式化在所有情况下都更短。这里，我按最短到最长的顺序显示所有这些选项，并将赋值左边对齐以便于比较它们：

```
f_string = f"{key:<10} = {value:.2f}"

c_tuple  = "%-10s = %.2f" % (key, value)

str_args = "{:<10} = {:.2f}".format(key, value)

str_kw   = "{key:<10} = {value:.2f}".format(key=key, value=value)

c_dict   = "%(key)-10s = %(value).2f" % {"key": key, "value": value}

assert c_tuple == c_dict == f_string
assert str_args == str_kw == f_string
```

F-strings also enable you to put a full Python expression within the placeholder braces, solving problem #2 from above by allowing small modifications to the values being formatted with concise syntax. What took multiple lines with C-style formatting and the `str.format` method now easily fits on a single line:

`F-strings` 还使你能够在占位符大括号内放置完整的 Python 表达式，通过允许使用简洁语法对格式化值进行小修改来解决上述问题 #2。以前需要多行的 C 风格格式化和 `str.format` 方法现在轻松适应单行：

```
for i, (item, count) in enumerate(pantry):
    old_style = "#%d: %-10s = %d" % (
        i + 1,
        item.title(),
        round(count),
    )

    new_style = "#{}: {:<10s} = {}".format(
        i + 1,
        item.title(),
        round(count),
    )

    f_string = f"#{i+1}: {item.title():<10s} = {round(count)}"

    assert old_style == new_style == f_string
```

Or, if it’s clearer, you can split an f-string over multiple lines by relying on adjacent-string concatenation (see Item 13: “Prefer Explicit String Concatenation Over Implicit, Especially In Lists”). Even though this is longer than the single-line version, it’s still much clearer than any of the other multiline approaches:

或者，如果这样更清晰，你可以依赖相邻字符串串联（类似于 C）将 `f-string` 拆分为多行。尽管这比单行版本更长，但仍远比其他任何多行方法清晰得多：

```
for i, (item, count) in enumerate(pantry):
    print(f"#{i+1}: "
          f"{item.title():<10s} = "
          f"{round(count)}")

>>>
#1: Avocados = 1
#2: Bananas = 2
#3: Cherries = 15
```

Python expressions may also appear within the format specifier options. For example, here I parameterize the number of digits to print by using a variable instead of hard-coding it in the format string:

Python 表达式也可以出现在格式指定符选项中。例如，这里我通过使用变量而不是硬编码在格式字符串中来参数化要打印的小数位数：

```
places = 3
number = 1.23456
print(f"My number is {number:.{places}f}")

>>>
My number is 1.235
```

The combination of expressiveness, terseness, and clarity provided by f-strings makes them the best built-in option for Python programmers. Any time you find yourself needing to format values into strings, choose f-strings over the alternatives.

`F-strings` 所提供的表现力、简洁性和清晰度的结合使它们成为 Python 程序员的最佳内置选项。每当发现自己需要将值格式化为字符串时，请选择 `f-strings` 而不是替代方案。

**Things to Remember**
- C-style format strings that use the `%` operator suffer from a variety of gotchas and verbosity problems.
- The str.format method introduces some useful concepts in its formatting specifiers mini-language, but it otherwise repeats the mistakes of C-style format strings and should be avoided.
- F-strings are a new syntax for formatting values into strings that solves the biggest problems with C-style format strings.
- F-strings are succinct yet powerful because they allow for arbitrary Python expressions to be directly embedded within format specifiers.

**注意事项**
- 使用 `%` 运算符的 C 风格格式字符串存在各种陷阱和冗长问题。
- `str.format` 引入了一些有用的格式说明符概念，但整体上仍存在与 C 风格相同的问题，应避免使用。
- `F-strings` 是一种新的格式化值为字符串的语法，解决了 C 风格格式字符串的最大问题。
- `F-strings` 简洁而强大，因为它们允许直接在格式指定符中嵌入任意 Python 表达式。