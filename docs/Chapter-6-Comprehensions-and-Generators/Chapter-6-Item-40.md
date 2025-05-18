# Chapter 6: Comprehensions and Generators (推导式和生成器)

## Item 40: Use Comprehensions Instead of map and filter (使用推导式代替 `map` 和 `filter`)

Python provides compact syntax for deriving a new `list` from another sequence or iterable. These expressions are called list comprehensions. For example, say that I want to compute the square of each number in a `list` . Here, I do this by using a simple `for` loop:

Python 提供了紧凑的语法用于从另一个序列或可迭代对象中派生出新的`list`。这些表达式被称为列表推导式。例如，假设我想要计算一个列表中每个数字的平方。这里，我使用简单的`for`循环来实现：

```
a = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
squares = []
for x in a:
 squares.append(x**2)
print(squares)
>>>
[1, 4, 9, 16, 25, 36, 49, 64, 81, 100]
```

With a list comprehension, I can achieve the same outcome in a single line by specifying the expression for my computation along with the input sequence variable to loop over:

通过列表推导式，我可以使用单行代码实现相同的结果，只需指定计算表达式以及要遍历的输入序列变量即可：

```
squares = [x**2 for x in a] # List comprehension
print(squares)
>>>
[1, 4, 9, 16, 25, 36, 49, 64, 81, 100]
```

Unless you’re applying a single-argument function, list comprehensions are clearer than the `map` built-in function for simple cases. `map` requires the creation of a `lambda` function for the computation (see Item 39: “Prefer functools.partial Over lambda Expressions For Glue Functions”), which is visually noisy in comparison:

除非你正在应用一个单一参数的函数，否则在简单的情况下列表推导式比 `map` 内置函数更加清晰。对于 `map` 来说，需要为计算创建一个 `lambda` 函数（参见条目39："Prefer functools.partial Over lambda Expressions For Glue Functions"），这在视觉上显得比较杂乱：

```
alt = map(lambda x: x**2, a)
```

Unlike `map` , list comprehensions let you easily filter items from the input `list` , removing corresponding outputs from the result. For example, say I want to compute the squares of the numbers that are divisible by 2. Here, I do this by adding an `if` clause to the list comprehension after the loop:

与 `map` 不同，列表推导式可以轻松地过滤输入列表中的项目，从而从结果中移除相应的输出。例如，假设我只想计算偶数的平方。这里，我在列表推导式的循环之后添加了一个 `if` 子句来实现：

```
even_squares = [x**2 for x in a if x % 2 == 0]
print(even_squares)
>>>
[4, 16, 36, 64, 100]
```

The `filter` built-in function can be used along with `map` to achieve the same outcome, but it is much harder to read due to nesting and boilerplate:

`filter` 内建函数可以与 `map` 结合使用以达到相同的成果，但由于嵌套和样板代码的存在，其可读性远不如前者：

```
alt = map(lambda x: x**2, filter(lambda x: x % 2 == 0, a))
assert even_squares == list(alt)
```

Dictionaries and sets have their own equivalents of list comprehensions (called dictionary comprehensions and set comprehensions, respectively). These make it easy to create other types of derivative data structures when writing algorithms:

字典和集合也有它们自己的列表推导式的等价形式（分别称为字典推导式和集合推导式）。这些特性使得在编写算法时更容易创建其他类型的衍生数据结构：

```
even_squares_dict = {x: x**2 for x in a if x % 2 == 0}
threes_cubed_set = {x**3 for x in a if x % 3 == 0}
print(even_squares_dict)
print(threes_cubed_set)
>>>
{2: 4, 4: 16, 6: 36, 8: 64, 10: 100}
{216, 729, 27}
```

Achieving the same outcome is possible with `map` and `filter` if you wrap each call with a corresponding constructor. These statements get so long that you have to break them up across multiple lines, which is even noisier and should be avoided:

如果用 `map` 和 `filter` 达到同样的效果，则需要将每个调用包装在一个相应的构造函数中。这些语句会变得非常长，以至于你不得不将它们拆分成多行，这样就更加嘈杂且应避免：

```
alt_dict = dict(
    map(
        lambda x: (x, x**2),
        filter(lambda x: x % 2 == 0, a),
    )
)
alt_set = set(
    map(
        lambda x: x**3,
        filter(lambda x: x % 3 == 0, a),
    )
)
```

However, one benefit of the `map` and `filter` built-in functions is they return iterators that incrementally produce one result at a time. This enables these functions to be composed together efficiently with minimal memory usage (see Item 43: “Consider Generators Instead of Returning Lists” and Item 24: “Consider itertools for Working with Iterators and Generators” for background). List comprehensions, in contrast, materialize the entire result upon evaluation, which consumes much more memory. Luckily, Python also provides a syntax that’s very similar to list comprehensions that can create infinitely long, memory-efficient streams of values (see Item 44: “Consider Generator Expressions for Large List Comprehensions”).

然而，`map` 和 `filter` 内建函数的一个优势是它们返回的是迭代器，这些迭代器能逐次递增地产生一个结果。这使得这些函数能够高效地组合在一起使用，并占用最少的内存（有关背景信息，请参见条目43："Consider Generators Instead of Returning Lists" 和条目24："Consider itertools for Working with Iterators and Generators"）。相比之下，列表推导式在评估时会具体化整个结果，这会消耗更多的内存。幸运的是，Python 同样提供了一种与列表推导式非常相似的语法，可以创建无限长、内存效率高的值流（请参见条目44："Consider Generator Expressions for Large List Comprehensions"）。

**Things to Remember**
- List comprehensions are clearer than the `map` and `filter` built-in functions because they don’t require `lambda` expressions.
- List comprehensions allow you to easily skip items from the input `list` by using `if` clauses, a behavior that `map` doesn’t support without help from `filter` .
- Dictionaries and sets may also be created using comprehensions.
- List comprehensions materialize the full result when evaluated, which can use a significant amount of memory compared to an iterator that produces each output incrementally.

**注意事项**
- 列表推导式比 `map` 和 `filter` 内建函数更清晰，因为它们不需要 `lambda` 表达式。
- 列表推导式允许您通过使用 `if` 子句轻松跳过输入列表中的项，而 `map` 在没有 `filter` 的帮助下无法做到这一点。
- 字典和集合也可以通过推导式创建。
- 列表推导式在评估时会具体化完整的结果，这与逐步产出每个输出的迭代器相比可能会使用大量的内存。