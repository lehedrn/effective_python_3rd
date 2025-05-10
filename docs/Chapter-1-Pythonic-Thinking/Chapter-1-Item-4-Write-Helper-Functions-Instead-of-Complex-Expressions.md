# Chapter 1: Pythonic Thinking (第一章 用Pythonic方式来思考)

## Item 4: Write Helper Functions Instead of Complex Expressions (使用辅助函数而不是复杂表达式)

Python’s pithy syntax makes it easy to write single-line expressions that implement a lot of logic. For example, say that I want to decode the query string from a website URL. Here, each query string parameter represents an integer value:

Python简洁的语法使得编写实现大量逻辑的单行表达式变得非常容易。例如，假设我想要解码网站URL中的查询字符串。在这里，每个查询字符串参数代表一个整数值：

```bash
from urllib.parse import parse_qs
my_values = parse_qs("red=5&blue=0&green=", keep_blank_values=True)
print(repr(my_values))
>>>
{'red': ['5'], 'blue': ['0'], 'green': ['']}
```

Some query string parameters may have multiple values, some may have single values, some may be present but have blank values, and some may be missing entirely. Using the get method on the result dictionary will return different values in each circumstance:

有些查询字符串参数可能有多个值，有些可能只有一个值，有些可能存在但具有空值，而有些则可能完全缺失。在不同情况下，使用get方法返回的结果也不同：

```bash
print("Red: ", my_values.get("red"))
print("Green: ", my_values.get("green"))
print("Opacity:", my_values.get("opacity"))
>>>
Red: ['5']
Green: ['']
Opacity: None
```

It’d be nice if a default value of 0 were assigned when a parameter isn’t supplied or is blank. I might initially choose to do this with Boolean expressions because it feels like this logic doesn’t merit a whole if statement or helper function quite yet.

如果某个参数没有提供或者为空，则赋予默认值0会更方便一些。我可能会最初选择使用布尔表达式来做这件事，因为它似乎还不值得使用整个if语句或辅助函数。

Python’s syntax makes this choice all too easy. The trick here is that the empty string, the empty `list` , and zero all evaluate to `False` implicitly. Thus, the expressions below will evaluate to the subexpression after the `or` operator when the first subexpression is `False` :

Python 的语法让这种选择变得过于简单。诀窍在于，空字符串、空列表和零都会隐式地被求值为 False。因此，当第一个子表达式为 False 时，or 运算符后的子表达式将作为结果返回：

```bash
# For query string 'red=5&blue=0&green='
red = my_values.get("red", [""])[0] or 0
green = my_values.get("green", [""])[0] or 0
opacity = my_values.get("opacity", [""])[0] or 0
print(f"Red: {red!r}")
print(f"Green: {green!r}")
print(f"Opacity: {opacity!r}")
>>>
Red: '5'
Green: 0
Opacity: 0
```

The `red` case works because the key `"red"` is present in the `my_values` dictionary. The value retrieved by the get method is a `list` with one member: the string `"5"` . This item is retrieved by accessing index zero in the list. Then, the `or` expression determines that the string is not empty and thus is the resulting value of that operation. Finally, the variable `red` is assigned to the value `"5"` .

red 的情况有效是因为字典 my_values 中存在键 "red"。通过 get 方法检索到的值是一个包含一个成员（字符串 "5"）的列表。通过访问列表索引0可以获取这个项。然后，or 表达式判断该字符串不为空，因此操作的结果是该表达式的左侧部分。最后，变量 red 被赋值为 "5"。

The green case works because the value in the my_values dictionary is a list with one member: an empty string. The item at index zero in the list is retrieved. The or expression determines the string is empty and thus its return value should be the right side argument to the operation, which is zero. Finally, the variable green is assigned to the value 0 .

green 的情况有效是因为 my_values 字典中的值是一个包含一个空字符串的列表。通过访问列表索引0获取该项。or 表达式判断字符串为空，因此其返回值应该是操作的右侧参数，即零。最后，变量 green 被赋值为 0。

The opacity case works because the value in the my_values dictionary is missing altogether. The behavior of the get method is to return its second argument if the key doesn’t exist in the dictionary (see Item 26: “Prefer get Over in and KeyError to Handle Missing Dictionary Keys”). The default value in this case is a list with one member: an empty string. Thus, when opacity isn’t found in the dictionary, this code does exactly the same thing as the green case.

opacity 的情况有效是因为 my_values 字典中根本没有对应的值。当字典中不存在该键时，get 方法的行为是返回其第二个参数（参见第26条：“优先使用 get 而不是 in 和 KeyError 来处理缺失的字典键”）。在这种情况下，默认值是一个包含一个空字符串的列表。因此，当 opacity 在字典中找不到时，这段代码的作用与 green 情况完全相同。

The complex expression with get , [""] , [0] , and or is difficult to read, and yet it still doesn’t do everything I need. I also want to ensure that all the parameter values are converted to integers so I can immediately use them in mathematical expressions. To do that, I wrap each expression with the int built-in function to parse the string as an integer:

带有 get、[""]、[0] 和 or 的复杂表达式很难阅读，而且它仍然没有完成我需要的所有事情。我还希望确保所有参数值都被转换为整数，以便我可以立即将它们用于数学表达式。为此，我将每个表达式用 int 内置函数包裹以将字符串解析为整数：

```bash
red = int(my_values.get("red", [""])[0] or 0)
```

This logic is now extremely hard to read. There’s so much visual noise. The code isn’t approachable. A new reader of the code would have to spend too much time picking apart the expression to figure out what it actually does. Even though it’s nice to keep things short, it’s not worth trying to fit this all on one line.

现在这段代码变得极其难以阅读。视觉噪音太多。代码不可接近。新读者必须花费太多时间去拆解表达式才能弄清楚它实际做了什么。尽管保持简短很好，但把所有内容都压缩在一行上并不值得。

Although Python does support conditional expressions for inline if / else behavior, using them in this situation only results in code that’s barely more readable than the Boolean operator example above (see Item 7: “Consider Conditional Expressions for Simple Inline if Statements”):

尽管 Python 支持条件表达式来进行内联的 if / else 行为，但在这种情况下使用它们只会导致代码比上面的布尔运算符示例略好读一点（参见第7条：“对于简单的内联 if 语句考虑使用条件表达式”）：

```bash
red_str = my_values.get("red", [""])
red = int(red_str[0]) if red_str[0] else 0
```

Alternatively, I can use a full if statement over multiple lines to implement the same logic. Seeing all of the steps spread out like this makes the dense version seem even more complex:

或者，我可以使用多行的完整 if 语句来实现相同的逻辑。看到所有步骤这样展开后，密集版本似乎更加复杂：

```bash
green_str = my_values.get("green", [""])
if green_str[0]:
    green = int(green_str[0])
else:
    green = 0
```

Now that this logic is spread across multiple lines, it’s a bit harder to copy and paste for assigning other variables (e.g., red ). If I want to reuse this functionality repeatedly—even just two or three times, as in this example—then writing a helper function is the way to go:

现在这段逻辑分布在多行上后，复制粘贴来分配其他变量（如 red）变得更加困难。如果我希望多次重复使用此功能——即使只是两三次，如本例所示——那么编写一个辅助函数是最好的选择：

```bash
def get_first_int(values, key, default=0):
    found = values.get(key, [""])
    if found[0]:
        return int(found[0])
     return default
```

The calling code is much clearer than the complex expression using or and the two-line version using the conditional expression:

调用代码比使用 or 和条件表达式的复杂表达式要清晰得多：

```bash
green = get_first_int(my_values, "green")
```

As soon as your expressions get complicated, it’s time to consider splitting them into smaller pieces—such as intermediate variables—and moving logic into helper functions. What you gain in readability always outweighs what brevity may have afforded you. Avoid letting Python’s pithy syntax for complex expressions from getting you into a mess like this. Follow the DRY principle: Don’t repeat yourself.

一旦你的表达式变得复杂，就该考虑将它们拆分为更小的部分——比如中间变量，并将逻辑移入辅助函数中。你获得的可读性总是超过简写所带来的优势。避免让 Python 简洁的语法使你陷入这样的混乱之中。遵循 DRY 原则：不要重复自己。

**Things to Remember**
- Python’s syntax makes it all too easy to write single-line expressions that are overly complicated and difficult to read.
- Move complex expressions into helper functions, especially if you need to use the same logic repeatedly.

**注意事项**
- Python 的语法使得编写过于复杂且难以阅读的单行表达式变得太容易。
- 将复杂的表达式移入辅助函数中，尤其是当你需要反复使用相同逻辑时。