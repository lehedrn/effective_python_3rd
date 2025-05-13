# Chapter 3: Loops and Iterators (循环和迭代器)

## Item 19: Avoid else Blocks After for and while Loops (避免在 for 和 while 循环后使用 else 块)

Python loops have an extra feature that is not available in most other programming languages: You can put an else block immediately after a loop’s repeated interior block:

Python 的循环有一个其他大多数编程语言都没有的特殊功能：你可以在循环体之后直接放置一个 `else` 块：

```
for i in range(3):
    print("Loop", i)
else:
    print("Else block!")
>>>
Loop 0
Loop 1
Loop 2
Else block!
```

Surprisingly, the `else` block runs immediately after the loop finishes. Why is the clause called “else”? Why not “and”? In an `if / else` statement, `else` means: “Do this if the block before this doesn’t happen” (see Item 7: “Avoid Conditional Expressions in Favor of if Statements”). In a `try / except` statement, `except` has the same definition: “Do this if trying the block before this failed.”

令人意外的是，`else` 块会在循环结束后立即执行。为什么这个子句叫做“else”而不是“and”呢？在一个 `if/else` 语句中，`else` 表示：“如果前面的块没有执行的话，就执行这个”（参见条目7）。在 `try/except` 语句中，`except` 具有同样的含义：“如果尝试前面的块失败了，就执行这个”。

 Similarly, `else` from `try / except / else` follows this pattern (see Item 80: “Take Advantage of Each Block in `try / except / else / finally` ”) because it means “Do this if there was no exception to handle.” `try / finally` is also intuitive because it means “Always do this after trying the block before.”

类似地，`try/except/else` 中的 `else` 也遵循这种模式（参见条目80），因为它表示“如果没有异常需要处理的话，就执行这个”。`try/finally` 也很直观，因为它表示“在尝试执行前面的块之后，总是要执行这个”。

Given all of the uses of `else` , `except` , and `finally` in Python, a new programmer might assume that the `else` part of `for` / `else` means “Do this if the loop wasn’t completed.” In reality, it does exactly the opposite. Using a `break` statement in a loop actually skips the `else` block:

鉴于 Python 中 `else`、`except` 和 `finally` 的所有这些用法，一个新手程序员可能会认为 `for/else` 中的 `else` 部分意味着“如果循环未完成，则执行这个”。实际上，它正好相反。在循环中使用 `break` 语句会跳过 `else` 块：

```
for i in range(3):
    print("Loop", i)
    if i == 1:
        break
else:
    print("Else block!")
>>>
Loop 0
Loop 1
```

Another surprise is that the `else` block runs immediately if you loop over an empty sequence:

另一个让人惊讶的情况是，如果你遍历一个空序列，`else` 块会立即执行：

```
for x in []:
    print("Never runs")
else:
    print("For else block!")
>>>
For else block!
```

The `else` block also runs when `while` loops are initially `False` :

当 `while` 循环初始值为 `False` 时，`else` 块也会运行：

```
while False:
    print("Never runs")
else:
    print("While else block!")
>>>
While else block!
```

The rationale for these behaviors is that `else` blocks after loops are useful when you’re searching for something. For example, say that I want to determine whether two numbers are coprime (that is, their only common divisor is 1). Here, I iterate through every possible common divisor and test the numbers. After every option has been tried, the loop ends. The `else` block runs when the numbers are coprime because the loop doesn’t encounter a `break` :

这些行为背后的原因是，在搜索某些内容时，循环后的 `else` 块非常有用。例如，假设我想确定两个数字是否互质（也就是说，它们的唯一公约数是 `1`）。在这里，我遍历每一个可能的公约数并进行测试。在每一种可能性都尝试过后，循环结束。当这两个数字互质时，`else` 块会运行，因为循环没有遇到 `break`：

```
a = 4
b = 9

for i in range(2, min(a, b) + 1):
    print("Testing", i)
    if a % i == 0 and b % i == 0:
        print("Not coprime")
        break
else:
    print("Coprime")
>>>
Testing 2
Testing 3
Testing 4
Coprime
```

In practice, I wouldn’t write the code this way. Instead, I’d write a helper function to do the calculation. Such a helper function is written in two common styles.

在实际应用中，我不会这样编写代码。相反，我会写一个辅助函数来进行计算。这样的辅助函数有两种常见的写法。

The first approach is to return early when I match the condition I’m looking for. I only return the default outcome if I fall through the loop:

第一种方法是在匹配到所需条件时提前返回。只有在我未能找到的情况下才返回默认的结果：

```
def coprime(a, b):
    for i in range(2, min(a, b) + 1):
        if a % i == 0 and b % i == 0:
            return False
    return True

assert coprime(4, 9)
assert not coprime(3, 6)
```

The second way is to have a result variable that indicates whether I’ve found what I’m looking for in the loop. Here, I `break` out of the loop as soon as I find something and then return that indicator variable:

第二种方法是使用一个结果变量来指示我在循环中是否找到了所需条件。在这种情况下，一旦找到，我就跳出循环，并返回该标志变量：

```
def coprime_alternate(a, b):
    is_coprime = True
    for i in range(2, min(a, b) + 1):
        if a % i == 0 and b % i == 0:
            is_coprime = False
            break
    return is_coprime

assert coprime_alternate(4, 9)
assert not coprime_alternate(3, 6)
```

Both of these approaches are much clearer to readers of unfamiliar code. Depending on the situation, either may be a good choice. However, the expressivity you gain from the `else` block doesn’t outweigh the burden you put on people (including yourself) who want to understand your code in the future. Simple constructs like loops should be self-evident in Python. You should avoid using `else` blocks after loops entirely.

这两种方法对于不熟悉这段代码的读者来说都更加清晰。根据具体情况，其中任何一种方式都可能是不错的选择。然而，从 `else` 块中获得的表现力并不值得给那些（包括你自己）将来想要理解你的代码的人带来负担。在 Python 中，像循环这样的简单结构应该是显而易见的。你应该完全避免在循环后使用 `else` 块。

**Things to Remember**

- Python has special syntax that allows `else` blocks to immediately follow for and while loop interior blocks.
- The `else` block after a loop runs only if the loop body did not encounter a `break` statement.
- Avoid using `else` blocks after loops because their behavior isn’t intuitive and can be confusing.

**注意事项**
- Python 有一种特殊的语法允许 `else` 块紧跟在 `for` 或 `while` 循环体之后。
- 只有在循环体中没有遇到 `break` 语句时，循环后的 `else` 块才会运行。
- 应避免在循环后使用 `else` 块，因为其行为并不直观且容易造成混淆。