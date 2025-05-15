# Chapter 4: Dictionaries (字典)

## Item 26: Prefer get over in and KeyError to Handle Missing Dictionary Keys (优先使用 get 方法而不是 in 和 KeyError 来处理缺失的字典键)

The three fundamental operations for interacting with dictionaries are accessing, assigning, and deleting keys and their associated values. The contents of dictionaries are dynamic, and thus it’s entirely possible—even likely—that when you try to access or delete a key, it won’t already be present.

与字典交互的三个基本操作是访问、赋值以及删除键及其关联的值。字典的内容是动态的，因此当你尝试访问或删除某个键时，该键很可能并不存在。

For example, say that I’m trying to determine people’s favorite type of bread to devise the menu for a sandwich shop. Here, I define a dictionary of counters with the current votes for each loaf’s style:

例如，假设我正在试图确定人们最喜欢的面包类型，以便为三明治店设计菜单。这里，我定义了一个计数器字典来记录每种面包风格当前的投票数：

```
counters = {
    "pumpernickel": 2,
    "sourdough": 1,
}
```

To increment the counter for a new vote, I need to see if the key exists, insert the key with a default counter value of zero if it’s missing, and then increment the counter’s value. This requires accessing the key two times and assigning it once. Here, I accomplish this task using an `if` statement with an `in` operator that returns `True` when the key is present:

为了增加一个新的投票计数，我需要查看这个键是否存在，如果不存在，则插入一个默认计数值为零的键。这需要访问键两次并赋值一次。在这里，我使用带有 `in` 运算符的 `if` 语句来完成此任务，当键存在时返回 `True`：

```
key = "wheat"
if key in counters:
    count = counters[key]
else:
    count = 0
counters[key] = count + 1
print(counters)
>>>
{'pumpernickel': 2, 'sourdough': 1, 'wheat': 1}
```

Another way to accomplish the same behavior is by relying on how dictionaries raise a `KeyError` exception when you try to get the value for a key that doesn’t exist. Putting aside the cost of raising and catching exceptions (see Item 80: “Take Advantage of Each Block in `try / except / else / finally` ”), this approach is more efficient, in theory, because it requires only one access and one assignment:

另一种实现相同行为的方法是依赖于字典在你尝试获取不存在键的值时引发 `KeyError` 异常的方式。暂且不谈引发和捕获异常的成本（参见条目80），这种方法理论上更高效，因为它只需要一次访问和一次赋值：

```
try:
    count = counters[key]
except KeyError:
    count = 0
counters[key] = count + 1
```

This flow of fetching a key that exists or returning a default value is so common that the `dict` built-in type provides the `get` method to accomplish this task. The second parameter to `get` is the default value to return in the case that the key—the first parameter—isn’t present (see Item 32: “Prefer Raising Exceptions to Returning None ” on whether that's a good interface). This approach also requires only one access and one assignment, but it’s much shorter than the `KeyError` example and avoids the exception handling overhead:

这种获取存在键或返回默认值的流程非常常见，以至于内置的 `dict` 类型提供了 `get` 方法来完成这一任务。`get` 的第二个参数是在第一个参数（即键）不存在的情况下返回的默认值（参见条目32）。这种方法也只需要一次访问和一次赋值，但比 `KeyError` 示例短得多，并且避免了异常处理的开销：

```
count = counters.get(key, 0)
counters[key] = count + 1
```

It’s possible to shorten the `in` operator and `KeyError` approaches in various ways, but all of these alternatives suffer from requiring code duplication for the assignments, which makes them less readable and worth avoiding:

可以以各种方式缩短 `in` 运算符和 `KeyError` 方法的写法，但所有这些替代方案都需要对赋值进行代码重复，使得它们的可读性较差，应尽量避免：

```
if key not in counters:
    counters[key] = 0
counters[key] += 1
if key in counters:
    counters[key] += 1
else:
    counters[key] = 1
try:
    counters[key] += 1
except KeyError:
    counters[key] = 1
```

Thus, for a dictionary with simple types, using the `get` method is the shortest and clearest option.

因此，对于具有简单类型的字典，使用 `get` 方法是最简短且最清晰的选择。

---

> Note
If you’re maintaining dictionaries of counters like this, it’s worth considering the `Counter` class from the `collections` built-in module, which provides most of the functionality you're likely to need.

> 注意
如果你正在维护类似计数器的字典，值得考虑使用 `collections` 内置模块中的 `Counter` 类，它提供了你可能需要的大部分功能。

---

What if the values in a dictionary are a more complex type, like a `list` ? For example, say that instead of only counting votes, I also want to know who voted for each type of bread. Here, I do this by associating a `list` of names with each key:

如果字典中的值是一种更复杂的类型，比如 `list` 呢？例如，假设除了仅计算投票外，我还想知道谁投了每一类面包。这里，我通过将每个键关联一个名字列表来实现这一点：

```
votes = {
    "baguette": ["Bob", "Alice"],
    "ciabatta": ["Coco", "Deb"],
}
key = "brioche"
who = "Elmer"
if key in votes:
    names = votes[key]
else:
    votes[key] = names = []
names.append(who)
print(votes)
>>>
{'baguette': ['Bob', 'Alice'],
 'ciabatta': ['Coco', 'Deb'],
 'brioche': ['Elmer']}
```

Relying on the `in` operator requires two accesses if the key is present, or one access and one assignment if the key is missing. This example is different from the counters example above because the value for each key can be assigned blindly to the default value of an empty `list` if the key doesn’t already exist. The triple assignment statement ( `votes[key] = names = []` ) populates the key in one line instead of two. Once the default value has been inserted into the dictionary, I don’t need to assign it again because the `list` is modified by reference in the later call to `append` (see Item 30: “Know That Function Arguments Can Be Mutated” for background).

依赖 `in` 运算符在键存在时需要两次访问，或者在键不存在时需要一次访问和一次赋值。此示例不同于上面的计数器示例，因为如果键不存在，可以盲目地将每个键的值分配为空 `list` 的默认值。三重赋值语句 (`votes[key] = names = []`) 在一行中填充键而不是两行。一旦默认值被插入到字典中，就不需要再次分配它，因为在后续调用 `append` 时，列表是通过引用来修改的（参见条目30）。

It’s also possible to rely on the `KeyError` exception being raised when the dictionary value is a `list` . This approach requires one key access if the key is present, or one key access and one assignment if it’s missing, which makes it more efficient than the `in` operator (ignoring the cost of the exception handling machinery):

也可以依靠当字典值为 `list` 时引发的 `KeyError` 异常。这种方法在键存在时需要一次键访问，或者在键不存在时需要一次键访问和一次赋值，这使得它比 `in` 运算符更高效（忽略异常处理机制的成本）：

```
try:
    names = votes[key]
except KeyError:
    votes[key] = names = []
names.append(who)
```

Similarly, I can use the `get` method to fetch a `list` value when the key is present, or do one fetch and one assignment if the key isn’t present:

同样，我可以使用 `get` 方法在键存在时获取一个 `list` 值，或者在键不存在时进行一次获取和一次赋值：

```
names = votes.get(key)
if names is None:
    votes[key] = names = []
names.append(who)
```

The approach that involves using `get` to fetch `list` values can further be shortened by one line if you use an assignment expression (introduced in Python 3.8; see Item 8: “Prevent Repetition with Assignment Expressions”) in the `if` statement, which improves readability:

涉及使用 `get` 获取 `list` 值的方法可以通过在 `if` 语句中使用赋值表达式（在Python 3.8中引入；参见条目8）进一步缩短一行，从而提高可读性：

```
if (names := votes.get(key)) is None:
    votes[key] = names = []
names.append(who)
```

Notably, the `dict` type also provides the `setdefault` method to help shorten this pattern even further. `setdefault` tries to fetch the value of a key in the dictionary. If the key isn’t present, the method assigns that key to the default value provided. And then the method returns the value for that key: either the originally present value or the newly inserted default value. Here, I use `setdefault` to implement the same logic as in the `get` example above:

值得注意的是，`dict` 类型还提供了 `setdefault` 方法，以帮助进一步缩短这种模式。`setdefault` 尝试获取字典中键的值。如果键不存在，该方法会将该键分配给提供的默认值。然后该方法返回该键的值：要么是最初存在的值，要么是新插入的默认值。在这里，我使用 `setdefault` 实现与上面 `get` 示例相同的逻辑：

```
names = votes.setdefault(key, [])
names.append(who)
```

This works as expected, and it is shorter than using `get` with an assignment expression. However, the readability of this approach isn’t ideal. The method name `setdefault` doesn’t make its purpose immediately obvious. Why is it set when what it’s doing is getting a value? Why not call it `get_or_set` ? I’m arguing about the color of the bike shed here, but the point is that if you were a new reader of the code and not completely familiar with Python, you might have trouble understanding what this code is trying to accomplish because `setdefault` isn’t self-explanatory.

这正如预期那样工作，并且比使用赋值表达式的 `get` 更短。然而，这种方法的可读性并不理想。方法名 `setdefault` 并不能立即使其目的变得明显。为什么要在做获取值的时候叫设置呢？为什么不叫它 `get_or_set`？我在这里争论自行车棚的颜色问题，但重点是，如果你是一个新的代码读者，而不是完全熟悉 Python，你可能会难以理解这段代码试图完成的任务，因为 `setdefault` 并不直观。

There’s also one important gotcha: The default value passed to `setdefault` is assigned directly into the dictionary when the key is missing instead of being copied. Here, I demonstrate the effect of this when the value is a `list` :

还有一个重要的注意事项：传递给 `setdefault` 的默认值在键缺失时直接分配到字典中，而不是复制。在这里，我演示了当值是一个 `list` 时的效果：

```
data = {}
key = "foo"
value = []
data.setdefault(key, value)
print("Before:", data)
value.append("hello")
print("After: ", data)
>>>
Before: {'foo': []}
After: {'foo': ['hello']}
```

This means that I need to make sure that I’m always constructing a new default value for each key I access with `setdefault` . This leads to a significant performance overhead in this example because I have to allocate a `list` instance for each call. If I reuse an object for the default value——which I might try to do to increase efficiency or readability——I might introduce strange behavior and bugs (see Item 36: “Use `None` and Docstrings to Specify Dynamic Default Arguments” for another example of this problem).

这意味着我需要确保始终为每次使用 `setdefault` 访问的键构建一个新的默认值。这会导致此示例中显著的性能开销，因为我必须为每次调用分配一个新的 `list` 实例。如果我为默认值重用一个对象——这可能是为了提高效率或可读性而尝试做的事情——可能会引入奇怪的行为和错误（另一个示例参见条目36）。

Going back to the earlier example that used counters for dictionary values instead of lists of who voted: Why not also use the `setdefault` method in that case? Here, I reimplement the same example using this approach:

回到前面使用字典计数器的例子而不是列表记录投票者的名字：为什么在这种情况下也不使用 `setdefault` 方法呢？在这里，我使用这种方法重新实现了同样的例子：

```
count = counters.setdefault(key, 0)
counters[key] = count + 1
```

The problem here is that the call to `setdefault` is superfluous. You always need to assign the key in the dictionary to a new value after you increment the counter, so the extra assignment done by `setdefault` is unnecessary. The earlier approach of using `get` for counter updates requires only one access and one assignment, whereas using `setdefault` requires one access and two assignments.

这里的问题在于对 `setdefault` 的调用是多余的。你总是在递增计数器之后需要将键分配给字典中的一个新值，所以 `setdefault` 所做的额外分配是没有必要的。早期使用 `get` 更新计数器的方法只需要一次访问和一次赋值，而使用 `setdefault` 则需要一次访问和两次赋值。

There are only a few circumstances in which using `setdefault` is the shortest way to handle missing dictionary keys, such as when the default values are cheap to construct, mutable, and there’s no potential for raising exceptions (e.g., `list` instances). In these very specific cases, it might seem worth accepting the confusing method name `setdefault` instead of having to write more characters and lines to use `get` . However, often what you really should do in these situations is to use `defaultdict` instead (see Item 27: “Prefer `defaultdict` Over `setdefault` to Handle Missing Items in Internal State”).

只有在少数情况下使用 `setdefault` 是处理缺失字典键的最简短方式，比如当默认值易于构造、可变，并且没有引发异常的潜在可能性时（如 `list` 实例）。在这些非常特定的情况下，接受混乱的方法名 `setdefault` 可能似乎值得，而不是不得不写更多的字符和行来使用 `get`。但是，在这些情况下，你真正应该做的是改用 `defaultdict`（参见条目27）。


**Things to Remember**
- There are four common ways to detect and handle missing keys in dictionaries: using `in` operators, `KeyError` exceptions, the `get` method, and the `setdefault` method.
- The `get` method is best for dictionaries that contain basic types like counters, and it is preferable along with assignment expressions when creating dictionary default values has a high cost or might raise exceptions.
- When the `setdefault` method of `dict` seems like the best fit for your problem, you should consider using `defaultdict` instead.

**注意事项**
- 处理字典中缺失键有四种常见的方法：使用 `in` 操作符、`KeyError` 异常、`get` 方法和 `setdefault` 方法。
- 对于包含基本类型如计数器的字典，`get` 方法最佳，当创建字典默认值成本高或可能引发异常时，建议结合使用 `get` 和赋值表达式。
- 当 `dict` 的 `setdefault` 方法似乎是你的问题的最佳解决方案时，你应该考虑改用 `defaultdict`。