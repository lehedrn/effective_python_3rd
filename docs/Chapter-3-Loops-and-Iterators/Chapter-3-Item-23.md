# Chapter 3: Loops and Iterators (循环和迭代器)

## Item 23: Pass Iterators to any and all for Efficient Short-Circuiting Logic (用迭代器配合 any 和 all，可以更高效地进行逻辑判断)

Python is a great language for building programs that do logical reasoning. For example, imagine that I’m trying to analyze the nature of flipping a coin. I can define a function that will return a random coin flip outcome—— `True` for heads or `False` for tails—each time it’s called:

Python 是一种非常适合构建进行逻辑推理的程序的语言。例如，假设我试图分析抛硬币的本质。我可以定义一个函数，每次调用它时都会返回一个随机的硬币翻转结果 —— `True` 表示正面或 `False` 表示反面：

```
import random

def flip_coin():
    if random.randint(0, 1) == 0:
        return "Heads"
    else:
        return "Tails"

def flip_is_heads():
    return flip_coin() == "Heads"
```

If I want to flip a coin 20 times and see if every result is consecutively heads, I can use a simple list comprehension (see Item 40: “Use Comprehensions Instead of map and filter ”) and contains check with the `in` operator (see Item 57: “Inherit from collections.abc for Custom Container Types”):

如果我想连续抛20次硬币，并查看每一次是否都是正面，可以使用简单的列表推导式（参见条目40）以及使用 `in` 操作符进行包含检查（参见条目57）：

```
flips = [flip_is_heads() for _ in range(20)]
all_heads = False not in flips
assert not all_heads  # Very unlikely to be True
```

However, the chance of this sequence of 20 coin flips producing nothing but heads is roughly a one in a million—extremely rare. If coin flips were somehow expensive to do, that means I’ll almost always waste a lot of resources on unnecessary work in the list comprehension because it keeps flipping coins even after seeing a tails result. I can improve this situation by using a loop that terminates the sequence of coin flips as soon as a non￾heads outcome is seen:

然而，这20次连续正面的概率大约是百万分之一——极为罕见。如果某种方式下抛硬币的成本很高，这意味着我几乎总是会浪费大量资源在列表推导式的不必要的工作中，因为它即使看到反面结果也会继续抛硬币。为改善这种情况，可以使用一旦看到非正面结果就终止序列的循环：

```
all_heads = True
for _ in range(100):
    if not flip_is_heads():
        all_heads = False
        break
```

Although this code is more efficient, it’s much longer than the list comprehension from before. To keep the code short while also ending execution early, I can use the `all` built-in function. `all` steps through an iterator, checks if each item is truthy (see Item 7: “Avoid Conditional Expressions in Favor of if Statements”), and immediately stops processing if not. `all` always returns a Boolean value of `True` or `False` , which is different from how the `and` logical operator returns the last value that’s tested:

尽管这段代码更高效，但它比之前的列表推导式要长得多。为了保持代码简洁同时也能够提前结束执行，可以使用内置的 `all` 函数。`all` 函数逐步处理一个迭代器，检查每个项目是否为真值（参见条目7），并在遇到假值时立即停止处理。`all` 总是返回布尔值 `True` 或 `False`，这与逻辑操作符 `and` 返回最后测试的值的方式不同：

```
print("All truthy:")
print(all([1, 2, 3]))
print(1 and 2 and 3)

print("One falsey:")
print(all([1, 0, 3]))
print(1 and 0 and 3)
>>>
All truthy:
True
3
One falsey:
False
0
```

Using the `all` built-in function, I can rewrite the coin flipping loop using a generator expression (see Item 44: “Consider Generator Expressions for Large List Comprehensions”). It will stop doing more coin flips soon as the `flip_is_heads` function returns `False` :

使用内置的 `all` 函数，我可以重写使用生成器表达式的硬币翻转循环（参见条目44）。一旦 `flip_is_heads` 函数返回 `False`，它就会停止更多的硬币翻转：

```
all_heads = all(flip_is_heads() for _ in range(20))
```

Critically, if I pass a list comprehension instead of a generator expression——note the presence of the surrounding `[` and `]` square brackets—the code will create a list of 20 coin flip outcomes before passing them to the `all` function. The computed result will be the same, but the code’s performance will be far worse:

重要的是，如果我传递的是列表推导式而不是生成器表达式——注意周围存在 `[ ]` ——代码将在将它们传递给 `all` 函数之前创建一个包含20个硬币翻转结果的列表。计算的结果将是相同的，但代码的性能会差很多：

```
all_heads = all([flip_is_heads() for _ in range(20)])
```

Alternatively, I can use a yielding generator function (see Item 43: “Consider Generators Instead of Returning Lists”) or any other type of iterator to achieve similar efficiency:

或者，我可以使用一个产出的生成器函数（参见条目43）或任何其他类型的迭代器来实现类似的效率：

```
def repeated_is_heads(count):
    for _ in range(count):
        yield flip_is_heads()  # Generator

all_heads = all(repeated_is_heads(20))
```

Once `repeated_is_heads` yields a `False` value, the `all` built-in function will stop moving the generator iterator forward and return `False` . The reference to the generator’s iterator that was passed to `all` will be thrown away and garbage collected, ensuring the loop never completes (see Item 89: “Always Pass Resources into Generators and Have Callers Clean Them Up Outside” for details).

一旦 `repeated_is_heads` 产生一个 `False` 值，内置的 `all` 函数将停止移动生成器迭代器并返回 `False`。传入 `all` 的生成器迭代器的引用将被丢弃并进行垃圾回收，确保循环永远不会完成（详细信息请参见条目89）。

Sometimes, you’ll have a function that behaves in the opposite way of `flip_is_heads` , returning `False` most of the time and `True` only when a certain condition is met. Here, I define a function that behaves this way:

有时，您可能有一个行为与 `flip_is_heads` 相反的函数，在大多数情况下返回 `False`，只有在特定条件下才返回 `True`。在这里，我定义了一个这样的函数：

```
def flip_is_tails():
    return flip_coin() == "Tails"
```

In order to use this function to detect consecutive heads, `all` won’t work. Instead, I can use the `any` built-in function. `any` similarly steps through an iterator, but it terminates upon seeing the first truthy value. `any` always returns a Boolean value, unlike the `or` logical operator that it mirrors:

为了使用此函数检测连续的正面，`all` 不会起作用。相反，我可以使用内置的 `any` 函数。`any` 类似地逐步遍历一个迭代器，但是遇到第一个真值后就会终止。`any` 总是返回一个布尔值，不像它所镜像的 or 逻辑运算符：

```
print("All falsey:")
print(any([0, False, None]))
print(0 or False or None)

print("One truthy:")
print(any([None, 3, 0]))
print(None or 3 or 0)
>>>
All falsey:
False
None
One truthy:
True
3
```

With `any` , I can use `flip_is_tails` in a generator expression to compute the same results as before:

通过 `any`，我可以在生成器表达式中使用 `flip_is_tails` 来计算相同的结果：

```
all_heads = not any(flip_is_tails() for _ in range(20))
```

Or I can create a similar generator function:

或者我可以创建一个类似的生成器函数：

```
def repeated_is_tails(count):
    for _ in range(count):
        yield flip_is_tails()

all_heads = not any(repeated_is_tails(20))
```

When should you choose `any` vs. `all` ? It depends on what you’re doing and the difficulty of testing the conditions that you care about. If you want to end early with a `True` value, then use `any` . If you want to end early with a `False` value, then use `all` . Ultimately, these built-in functions are equivalent, as demonstrated by De Morgan’s laws for Boolean logic:

什么时候应该选择 `any` 而不是 `all`？这取决于你正在做的事情以及测试你关心的条件的难易程度。如果你想在遇到 `True` 值时尽早结束，请使用 `any`。如果你想在遇到 `False` 值时尽早结束，请使用 `all`。最终，这些内置函数是等效的，正如布尔逻辑中的德摩根定律所证明的那样：

```
for a in (True, False):
    for b in (True, False):
        assert any([a, b]) == (not all([not a, not b]))
        assert all([a, b]) == (not any([not a, not b]))
```

One way or another, you should be able to find a way to minimize the amount of work being done by using `any` or `all` appropriately. There are also additional built-in modules for operating on iterators and generators in intelligent ways to maximize performance and efficiency (see Item 24: “Consider itertools for Working with Iterators and Generators”).

无论哪种方式，您都应该能够找到一种方法，通过适当使用 `any` 或 `all` 来最小化所做的工作量。还有其他内置模块用于以智能方式对迭代器和生成器进行操作，以最大化性能和效率（参见条目24）。

**Things to Remember**

- The `all` built-in function returns `True` if all items provided are truthy.It stops processing input and returns `False` as soon as a falsey item is encountered.
- The `any` built-in function works similarly, but with opposite logic: it returns `False` if all items are falsey and ends early with `True` as soon as it sees a truthy value.
- `any` and `all` always return the Boolean values `True` or `False` , unlike the `or` and `and` logical operators, which return the last item that needed to be tested.
- Using list comprehensions with `any` or `all` instead of generator expression undermines the efficiency benefits of these functions.

**注意事项**
- 内置的 `all` 函数如果所有提供的项都是真值，则返回 `True`。一旦遇到假值，它就会停止处理输入并返回 `False`。
- 内置的 `any` 函数的工作原理类似，但逻辑相反：如果所有项都是假值则返回 `False`，一旦看到真值就立即返回 `True`。
- `any` 和 `all` 总是返回布尔值 `True` 或 `False`，不同于返回最后需要测试的项的 `or` 和 `and` 逻辑运算符。
- 在 `any` 或 `all` 中使用列表推导式而不是生成器表达式，会削弱这些函数的效率优势。