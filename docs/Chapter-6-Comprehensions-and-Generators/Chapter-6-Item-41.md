# Chapter 6: Comprehensions and Generators (推导式和生成器)

## Item 41: Avoid More Than Two Control Subexpressions in Comprehensions (在推导式中避免使用两个以上的控制子表达式)

Beyond basic usage (see Item 40: “Use Comprehensions Instead of map and filter ”), comprehensions also support multiple levels of looping. For example, say that I want to simplify a matrix (a `list` containing other `list` instances) into one flat `list` of all items. Here, I do this with a list comprehension by including two `for` subexpressions. These subexpressions run in the order provided, from left to right:

除了基本用法之外（参见条目40：“使用推导式代替map和filter”），推导式还支持多层循环。例如，假设我想将一个矩阵（包含其他`list`实例的`list`）简化成一个包含所有项目的平面`list`。在这里，我通过包含两个`for`子表达式的列表推导式来实现这一点。这些子表达式按照从左到右的顺序运行：

```
matrix = [
 [1, 2, 3],
 [4, 5, 6],
 [7, 8, 9],
]
flat = [x for row in matrix for x in row]
print(flat)
>>>
[1, 2, 3, 4, 5, 6, 7, 8, 9]
```

This example is simple, readable, and a reasonable usage of multiple loops in a comprehension. Another reasonable usage of multiple loops involves replicating the two-level-deep layout of the input `list` . For example, say that I want to square the value in each cell of a two-dimensional matrix. This comprehension is noisier because of the extra `[]` characters, but it’s still relatively easy to read:

这个例子简单、可读性强，是推导式中多层循环的一个合理用法。涉及复制输入`list`的两层布局是另一个多层循环的合理用法。例如，假设我想对二维矩阵中的每个单元格的值进行平方。由于额外的`[]`字符，这个推导式会更嘈杂，但仍然相对容易阅读：

```
squared = [[x**2 for x in row] for row in matrix]
print(squared)
>>>
[[1, 4, 9], [16, 25, 36], [49, 64, 81]]
```

If this comprehension included another loop, it would get so long that I’d have to split it over multiple lines:

如果此推导式包含另一个循环，它将变得非常长，以至于我必须将其拆分为多行：

```
my_lists = [
    [[1, 2, 3], [4, 5, 6]],
    [[7, 8, 9], [10, 11, 12]],
]
flat = [x for sublist1 in my_lists
        for sublist2 in sublist1
        for x in sublist2]
```

At this point, the multiline comprehension isn’t much shorter than the alternative. Here, I produce the same result using normal loop statements. The indentation of this version makes the looping clearer than the three￾level-list comprehension above:

此时，此多行推导式并不比替代方案短多少。在这里，我使用正常的循环语句产生相同的结果。此版本的缩进使循环更加清晰，而不是上面的三层推导式：

```
flat = []
for sublist1 in my_lists:
    for sublist2 in sublist1:
        flat.extend(sublist2)
```

Comprehensions support multiple `if` conditions. Multiple conditions at the same loop level have an implicit `and` expression. For example, say that I want to filter a `list` of numbers to only even values greater than 4. These two list comprehensions are equivalent:

推导式支持多个`if`条件。同一循环级别的多个条件具有隐含的`and`表达式。例如，假设我想过滤一个数字列表，仅保留大于4的偶数值。这两个列表推导式是等效的：

```
a = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
b = [x for x in a if x > 4 if x % 2 == 0]
c = [x for x in a if x > 4 and x % 2 == 0]
```

Conditions can be specified at each level of looping after the `for` subexpression. For example, say I want to filter a matrix so the only cells remaining are those divisible by 4 in rows that sum to 10 or higher. Expressing this with a list comprehension does not require a lot of code, but it is extremely difficult to read:

可以在每个循环级别之后指定条件。例如，假设我想要过滤一个矩阵，使得剩下的单元格仅是那些在行中总和为10或更高的情况下能被4整除的单元格。用列表推导式表达这不需要大量代码，但它极其难以阅读：

```
matrix = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9],
]
filtered = [[x for x in row if x % 4 == 0]
            for row in matrix if sum(row) >= 10]
print(filtered)
>>>
[[4], [8]]
```

Although this example is a bit convoluted, in practice you’ll see situations arise where such comprehensions seem like a good fit. I strongly encourage you to avoid using `list` , `dict` , or `set` comprehensions that look like this. The resulting code is very difficult for new readers to understand. The potential for confusion is even worse for `dict` comprehensions since they already need an extra parameter to represent both the key and the value for each item.

尽管这个例子有点复杂，在实践中你可能会遇到这样的情况。我强烈建议你避免使用像这样的`list`、`dict`或`set`推导式。这样的代码对于新读者来说非常难以理解。对于需要额外参数表示每个项的键和值的字典推导式来说，潜在的混淆甚至更糟。

The rule of thumb is to avoid using more than two control subexpressions in a comprehension. This could be two conditions, two loops, or one condition and one loop. As soon as it gets more complicated than that, you should use normal `if` and `for` statements and write a helper function (see Item 43: “Consider Generators Instead of Returning Lists”).

经验法则是避免在推导式中使用超过两个控制子表达式。这可以是两个条件，两个循环，或者一个条件和一个循环。一旦它变得更加复杂，你应该使用正常的`if`和`for`语句并编写一个辅助函数（参见条目43：“考虑使用生成器代替返回列表”）。

**Things to Remember**
- Comprehensions support multiple levels of loops and multiple conditions per loop level.
- Comprehensions with more than two control subexpressions are very difficult to read and should be avoided.

**注意事项**
- 推导式支持多个层级的循环和每个循环层级的多个条件。
- 包含两个以上控制子表达式的推导式非常难以阅读，应予以避免。