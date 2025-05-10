# Chapter 1: Pythonic Thinking (第一章 用Pythonic方式来思考)

## Item 7: Consider Conditional Expressions for Simple Inline if Statements (对于简单的内联 if 语句，考虑使用条件表达式)

Python if statements are not expressions. The if block, elif blocks, and else block each can contain a number of additional statements. The whole group of blocks doesn’t evaluate to a single value that can be stored in a variable or passed as a function argument.

Python 的 if 语句不是表达式。if 块、elif 块和 else 块都可以包含多个额外的语句。整个这些块不会计算为一个可以存储在变量中或作为函数参数传递的单一值。

Python also supports conditional expressions that let you insert if / elif / else behavior nearly anywhere an expression is allowed. For example, here I use a conditional expression to assign a variable’s value depending on a Boolean test:

Python 还支持条件表达式（conditional expressions），它允许你在几乎所有可以使用表达式的地方插入 if / elif / else 的行为。例如，这里我使用条件表达式根据布尔测试来分配变量的值：

```
i = 3
x = "even" if i % 2 == 0 else "odd"
print(x)
>>>
odd
```

This expression structure seems convenient, especially for one-of-a-kind uses, and is reminiscent of the ternary operator you might know from C and other languages (e.g., condition ? true_value : false_value ). For simple assignments like this, or even in function call argument lists (e.g., my_func(1 if x else 2) ), conditional expressions can be a good choice for balancing brevity with flexibility in code.

这种结构看起来很方便，尤其是在一次性使用的情况下，它类似于你可能从 C 和其他语言中知道的三元运算符（如 condition ? true_value : false_value）。对于像这样的简单赋值，或者甚至在函数调用的参数列表中（如 my_func(1 if x else 2)），条件表达式可以在代码的简洁性和灵活性之间取得良好的平衡。

It’s important to note one key detail in how conditional expressions in Python are different than ternary operators in other languages: In C, the test expression comes first; in Python, the expression to evaluate when the test expression is truthy comes first. For example, you might expect that the following code calls the fail function and raises an exception; instead, the fail function is never executed because the test condition is False :

需要注意的一点是 Python 中的条件表达式与其它语言中的三元运算符有一个关键区别：在 C 中，测试表达式位于前面；而在 Python 中，当测试表达式为真时要执行的表达式位于前面。例如，你可能会认为以下代码会调用 fail 函数并抛出异常；实际上，由于测试条件为 False，fail 函数永远不会被执行：

```
def fail():
    raise Exception("Oops")
x = fail() if False else 20
print(x)
>>>
20
```

if clauses in Python comprehensions have similar syntax and behavior for filtering (see Item 40: “Use Comprehensions Instead of map and filter ” and Item 44: “Consider Generator Expressions for Large List Comprehensions”). For example, here I use the if clause in a list comprehension to only include even values of x when computing the resulting list:

Python 列表推导式中的 if 子句具有类似的语法和行为，用于过滤（参见条目 40：“Use Comprehensions Instead of map and filter” 和条目 44：“Consider Generator Expressions for Large List Comprehensions”）。例如，这里我在列表推导式中使用 if 子句，仅在计算结果列表时包括 x 的偶数值：

```
result = [x / 4 for x in range(10) if x % 2 == 0]
print(result)
>>>
[0.0, 0.5, 1.0, 1.5, 2.0]
```

The expression to evaluate ( x / 4 ) comes before the if test expression ( x % 2 == 0 ), just like in a conditional expression.

要评估的表达式（x / 4）出现在 if 测试表达式（x % 2 == 0）之前，这与条件表达式中的顺序相同。

Before conditional expressions were available in Python, people would sometimes use Boolean logic in order to implement similar behavior (see Item 4: “Write Helper Functions Instead of Complex Expressions” for details). For example, the following expression is equivalent to the conditional expression above:

在 Python 引入条件表达式之前，人们有时会使用布尔逻辑来实现类似的行为（详情请参见条目 4：“Write Helper Functions Instead of Complex Expressions”）。例如，下面的表达式等价于上面的条件表达式：

```
x = (i % 2 == 0 and "even") or "odd"
```

This form of logic is quite confusing because you need to know that and returns the first falsey value or the last truthy value, while or returns the first truthy value or the last falsey value (see Item 23: “Pass Iterators to any and all for Efficient Short-Circuiting Logic” for details).

这种形式的逻辑相当令人困惑，因为你需要知道 and 返回第一个假值或最后一个真值，而 or 返回第一个真值或最后一个假值（详细信息请参见条目 23：“Pass Iterators to any and all for Efficient Short-Circuiting Logic”）。

Also, the approach of using Boolean operators doesn’t work if you want to return a falsey value as a result of a truthy condition (e.g., x = (i % 2 == 0 and []) or [1] always evaluates to [1] ). It’s all non￾obvious and error prone, which is part of why conditional expressions were added to the language in the first place.

此外，如果你希望在条件为真时返回一个假值，使用布尔运算符的方法并不奏效（例如，x = (i % 2 == 0 and []) or [1] 总是返回 [1]）。这种方式既不直观又容易出错，这也是为什么条件表达式被引入到语言中的原因之一。


Now, consider the same logic as a four-line if statement instead of the earlier single-line example:

现在，考虑将相同的逻辑写成四行的 if 语句，而不是之前的单行示例：

```
if i % 2 == 0:
    x = "even"
else:
    x = "odd"
```

Although this is longer, it can be better for a few reasons. First, if I later want to do more inside each of the condition branches, like printing debugging information, I can without structurally changing the code:

虽然这段代码更长，但在某些情况下更好。首先，如果以后你想在每个条件分支中做更多事情，比如打印调试信息，你可以无需结构性地修改代码即可实现：

```
if i % 2 == 0:
    x = "even"
    print("It was even!") # Added
else:
    x = "odd"
```

I can also insert additional branches with elif blocks in the same statement:

你还可以在同一语句中插入额外的 elif 分支：

```
if i % 2 == 0:
    x = "even"
elif i % 3 == 0: # Added
    x = "divisible by three"
else:
    x = "odd"
```

If I really need to achieve brevity and put this logic in a single expression, I can do that by moving it all into a helper function that I call inline:

如果你真的需要实现简洁，并将此逻辑放在单个表达式中，你可以通过将其移动到一个辅助函数中来实现：

```
def number_group(i):
    if i % 2 == 0:
        return "even"
    else:
        return "odd"
x = number_group(i) # Short call
```

As an added benefit, the helper function can be reused in multiple places instead of being a one-off like a conditional expression would be.

此外，这个辅助函数可以在多个地方复用，而不像条件表达式那样只能是一次性的。

Whether you should use conditional expressions, full if statements, or if statements wrapped in helper functions is going to depend on the specific situation.

你是否应该使用条件表达式、完整的 if 语句，还是将 if 语句封装在辅助函数中，取决于具体情况。

You should avoid conditional expressions when they must be split over multiple lines. For example, here the function calls I make are so long that the conditional expression must be line-wrapped with surrounding parentheses:

当你必须将条件表达式拆分为多行时，应避免使用它们。例如，在以下情况中，函数调用非常长，因此条件表达式必须使用周围的括号进行换行处理：

```
x = (my_long_function_call(1, 2, 3) if i % 2 == 0 else my_other_long_function_call(4, 5, 6))
```

That’s quite difficult to read. And if you apply an auto-formatter (see Item 2: “Follow the PEP 8 Style Guide”) to this code, the conditional expression will likely be rewritten to use more lines of code than a standard if / else statement anyway:

这很难阅读。如果你对这段代码应用自动格式化工具（参见条目 2：“Follow the PEP 8 Style Guide”），条件表达式很可能会被重写为比标准的 if/else 语句更多的行数：

```
x = (
 my_long_function_call(1, 2, 3)
 if i % 2 == 0
 else my_other_long_function_call(4, 5, 6)
)
```

Another Python language feature to compare with conditional expressions is assignment expressions (see Item 8: “Prevent Repetition with Assignment Expressions”), which also allow statement-like behavior in expressions. The critical difference is that assignment expressions must be surrounded by parenthesis when they’re used in an ambiguous context; conditional expressions do not require surrounding parentheses, which can hurt readability.

另一个可以与条件表达式进行比较的 Python 特性是赋值表达式（assignment expressions）（参见条目 8：“Prevent Repetition with Assignment Expressions”），它也允许在表达式中使用类似语句的行为。关键的区别在于，当赋值表达式出现在歧义上下文中时，它们必须被括号包围；而条件表达式则不需要括号，这可能会影响可读性。

For example, this if statement with an assignment expression in parentheses is permitted:

例如，以下带有括号的 if 语句使用了赋值表达式，这是允许的：

```
x = 2
y = 1
if x and (z := x > y):
 ...
```

But this if statement without wrapping parenthesis is a syntax error:

但如果没有括号，则会出现语法错误：

```
if x and z := x > y:
 ...
>>>
Traceback ...
SyntaxError: cannot use assignment expressions wi
```

With conditional expressions, parentheses aren’t required. Thus, it’s difficult to decipher what the original intent of the programmer was since both of these forms are allowed:

而对于条件表达式来说，括号不是必需的。因此，很难辨别程序员最初的意图，因为以下两种形式都是允许的：

```
if x > y if z else w: # Ambiguous
 ...
if x > (y if z else w): # Clear
 ...
```

Assignment expressions also need surrounding parentheses when used inside a function call argument list:

赋值表达式在函数调用参数列表中也需要括号：

```
z = dict(
 your_value=(y := 1),
)
```

Leaving out the parentheses is a syntax error:

如果没有括号，就会出现语法错误：

```
w = dict(
 other_value=y := 1,
)
>>>
Traceback ...
SyntaxError: invalid syntax
```

Conditional expressions, in contrast, don’t require surrounding parentheses in this context, which can make code noisier and hard to read:

相比之下，条件表达式在这种上下文中不需要括号，这可能导致代码噪音更大且难以阅读：

```
v = dict(
 my_value=1 if x else 3,
)
```

The conclusion is: Use your judgement. In many situations, conditional expressions can be valuable and improve clarity. Sometimes they’re better with surrounding parentheses, sometimes not. Conditional expressions can all too easily be overused to write obfuscated code that’s difficult for new readers to understand. When in doubt, choose a normal if statement.

结论就是：运用你的判断力：在许多情况下，条件表达式是有价值的，并能提高代码的清晰度。有时候加上括号更好，有时则不需要。条件表达式很容易被过度使用，写出让人难以理解的晦涩代码。当你不确定时，选择标准的 if 语句。

**Things to Remember**

- Conditional expressions in Python allow you to put an if statement nearly anywhere an expression would normally go.
- The order of the test expression, true result expression, and false result expression in a conditional expression is different than ternary operators in other languages.
- Don’t use conditional expressions in places where they increase ambiguity or harm readability for new readers of the code.
- Prefer standard if statements and helper functions when it’s unclear whether conditional expressions provide a compelling benefit.

**注意事项**

- 条件表达式允许你在几乎所有可以使用表达式的地方插入 if 逻辑。
- Python 的条件表达式中，测试表达式、真值表达式和假值表达式的顺序与其他语言中的三元运算符不同。
- 不要在增加歧义或损害可读性的情况下使用条件表达式。
- 当不清楚条件表达式是否带来明显优势时，优先使用标准的 if 语句和辅助函数。