# Chapter 6: Comprehensions and Generators (列表推导式与生成器)

## Item 44: Consider Generator Expressions for Large List Comprehensions (考虑使用生成器表达式处理大型列表推导式)

One problem with list comprehensions (see Item 40: “Use Comprehensions Instead of map and filter ”) is that they create new `list` instances potentially containing an item for each value in their input sequences. This is fine for small inputs, but for large inputs, this behavior might consume significant amounts of memory and cause a program to crash.

列表推导式的一个问题是（参见条目40：“优先选择列表推导式而不是 map 和 filter”），它们会创建新的 `list` 实例，其中可能包含输入序列中每个值的元素。对于小型输入来说这没有问题，但对于大型输入来说，这种行为可能会消耗大量内存，并可能导致程序崩溃。

For example, say that I want to read a file and return the number of characters on each line. Here, I use a list comprehension to implement this logic:

例如，假设我想要读取一个文件并返回每行的字符数。这里我使用列表推导式来实现这个逻辑：

```
import random

with open("my_file.txt", "w") as f:
    for _ in range(10):
        f.write("a" * random.randint(0, 100))
        f.write("\n")

value = [len(x) for x in open("my_file.txt")]
print(value)
>>>
[100, 57, 15, 1, 12, 75, 5, 86, 89, 11]
```

This code requires holding the length of every line of the file in memory. If the file is absolutely enormous or perhaps a never-ending network socket, it won’t work. To solve this issue, Python provides generator expressions, which are a generalization of list comprehensions and generators. Generator expressions don’t materialize the whole output sequence when they’re run. Instead, generator expressions evaluate to an iterator that yields one item at
a time from the expression.

此代码需要将文件每一行的长度都保存在内存中。如果文件非常庞大，或者可能是一个无休止的网络套接字，这种方法就行不通了。为了解决这个问题，Python 提供了生成器表达式，它是列表推导式和生成器的泛化形式。生成器表达式不会在运行时实例化整个输出序列。相反，生成器表达式会计算出一个迭代器，该迭代器每次从表达式中产生一个项目。

You create a generator expression by putting list-comprehension-like syntax between `()` characters. Here, I use a generator expression that is equivalent to the code above. However, the generator expression immediately evaluates to an iterator, doesn’t make any forward progress, and has little memory overhead:

您可以通过在 `()` 字符之间放置类似列表推导式的语法来创建生成器表达式。在这里，我使用了一个等效于上面代码的生成器表达式。然而，生成器表达式立即评估为一个迭代器，不进行任何前向进展，并且几乎没有内存开销：

```
it = (len(x) for x in open("my_file.txt"))
print(it)
>>>
<generator object <genexpr> at 0x104f37510>
```

The returned iterator can be advanced one step at a time to produce the next output from the generator expression, as needed (using the `next` built-in function). I can consume as much of the generator expression as I want without risking a blowup in memory usage:

返回的迭代器可以一次前进一步以产生生成器表达式的下一个输出（使用内置的 `next` 函数）。我可以按需消费生成器表达式的任何部分，而无需担心内存使用的爆炸性增长：

```
print(next(it))
print(next(it))
>>>
100
57
```

Another powerful outcome of generator expressions is that they can be composed together. Here, I take the iterator returned by the generator expression above and use it as the input for another generator expression:

生成器表达式的另一个强大结果是它们可以一起组合使用。在这里，我拿了上面生成器表达式返回的迭代器并将其用作另一个生成器表达式的输入：

```
roots = ((x, x**0.5) for x in it)
```

Each time I advance this iterator, it also advances the interior iterator, creating a domino effect of looping, evaluating expressions, and passing around inputs and outputs, all while being as memory efficient as possible:

每次我推进这个迭代器时，它也会推进内部的迭代器，从而形成连锁的循环、表达式求值和输入输出传递，同时尽可能地节省内存：

```
print(next(roots))
>>>
(15, 3.872983346207417)
```

Chaining generators together like this executes very quickly in Python. When you’re looking for a way to compose functionality that’s operating on a large stream of input, generator expressions are the best tool for the job (see Item 23: “Pass Iterators to any and all for Efficient Short￾Circuiting Logic” and Item 24: “Consider itertools for Working with Iterators and Generators” for more examples). The only gotcha is that the iterators returned by generator expressions are stateful, so you must be careful not to use these iterators more than once (see Item 21: “Be Defensive When Iterating Over Arguments”).

像这样链接生成器在一起在 Python 中执行得非常快。当您正在寻找一种方法来组合操作大量输入流的功能时，生成器表达式是最佳选择（更多示例请参见条目23：“将迭代器传递给 any 和 all 以实现高效的短路逻辑”和条目24：“考虑使用 itertools 模块处理迭代器和生成器”）。唯一的注意事项是，生成器表达式返回的迭代器是有状态的，因此您必须小心不要重复使用这些迭代器超过一次（参见条目21：“在遍历参数时要具有防御性”）。

**Things to Remember**
- List comprehensions can cause problems for large inputs by using too much memory.
- Generator expressions avoid memory issues by producing outputs one at a time as iterators.
- Generator expressions can be composed by passing the iterator from one generator expression into the for subexpression of another.
- Generator expressions execute very quickly when chained together and are memory efficient.

**注意事项**
- 列表推导式可能因为占用太多内存而导致大型输入的问题。
- 生成器表达式通过一次产生一个输出作为迭代器，避免了内存问题。
- 可以通过将一个生成器表达式返回的迭代器传入到另一个生成器表达式的 for 子表达式中来组合它们。
- 链式连接的生成器表达式执行速度快且内存效率高。