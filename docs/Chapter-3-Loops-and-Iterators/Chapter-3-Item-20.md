# Chapter 3: Loops and Iterators (循环和迭代器)

## Item 20: Never Use for Loop Variables After the Loop Ends (永远不要在循环结束后使用循环变量)

When you are writing a `for` loop in Python, you might notice that the variable you create for iteration continues to persist after the loop has finished:

当你在 Python 中编写 for 循环时，你可能会注意到用于迭代的变量在循环结束后仍然存在：

```
for i in range(3):
    print(f"Inside {i=}")
print(f"After  {i=}")
>>>
Inside i=0
Inside i=1
Inside i=2
After i=2
```

It’s possible to rely on this loop variable assignment behavior to your advantage. For example, here I implement an algorithm for grouping together periodic elements by searching for their index in a list:

可以利用这种循环变量赋值的行为来达到自己的目的。例如，这里实现了一种将周期性元素分组的算法，通过在列表中查找它们的索引来实现：

```
categories = ["Hydrogen", "Uranium", "Iron", "Other"]
for i, name in enumerate(categories):
    if name == "Iron":
        break
print(i)
>>>
2
```

In the case a given element isn’t found in the list, the last index will be used after iteration is exhausted, grouping the item with the "Other" catch-all category (index 3 in this case):

如果某个给定的元素在列表中找不到，则会在迭代耗尽后使用最后一个索引，将该元素归类到“其他”这一兜底类别（在这种情况下是索引3）：

```
for i, name in enumerate(categories):
    if name == "Lithium":
        break
print(i)
>>>
3
```

The assumption in this algorithm is that either the loop will find a matching item and end early from a `break` statement, or the loop will iterate through all the options and fall through. Unfortunately, there’s a third possibility where the loop never begins because the iterator is initially empty; this can result in a runtime exception:

这个算法的假设是，要么循环会找到匹配的项并通过 `break` 提前结束，要么循环会遍历所有选项并正常结束。不幸的是，还有第三种可能性，即循环从未开始，因为迭代器最初为空；这可能导致运行时异常：

```
del i
categories = []
for i, name in enumerate(categories):
    if name == "Lithium":
        break
print(i)
>>>
Traceback ...
NameError: name 'i' is not defined. Did you mean: 'id'?
```

There are alternative approaches to deal with when loop iteration never occurs (see Item 19: “Avoid else Blocks After for and while Loops”). But the point is the same: You can’t always be sure that a loop variable will exist when you try to access it after the loop, so it’s best to never do this in practice.

对于循环迭代从未发生的情况，还有其他替代方法可以处理（参见条目19）。但重点是一样的：你不能总是确定在循环结束后尝试访问循环变量时它一定存在，因此在实践中最好不要这样做。

Fortunately—or perhaps unfortunately—other Python features do not have this problem. The loop variable leakage behavior is not exhibited by list comprehensions or generator expressions (see Item 40: “Use Comprehensions Instead of map and filter ” and Item 44: “Consider Generator Expressions for Large List Comprehensions”). If you try to access a comprehension’s inner variables after execution, you’ll find that they’re never present and thus you can’t inadvertently encounter this pitfall:

幸运的是——或者可能是不幸的是——其他 Python 特性并没有这个问题。列表推导式或生成器表达式不会表现出这种循环变量泄漏的行为（参见条目40和条目44）。如果你尝试在执行后访问推导式的内部变量，你会发现它们从不存在，因此你无法无意中遇到这个陷阱：

```
my_numbers = [37, 13, 128, 21]
found = [i for i in my_numbers if i % 2 == 0]
print(i)  # Always raises
>>>
Traceback ...
NameError: name 'i' is not defined
```

However, it’s possible for assignment expressions in comprehensions to change this behavior (see Item 42: “Avoid Repeated Work in Comprehensions by Using Assignment Expressions”). Exception variables also don’t have this problem of leakage, although they are quirky in their own way (see Item 84: “Beware of Exception Variables Disappearing”.

然而，推导式中的赋值表达式可能会改变这种行为（参见条目42）。异常变量也没有这种泄漏的问题，尽管它们有自己古怪的行为（参见条目84）。

**Things to Remember**
- The loop variable from `for` loops can be accessed in the current scope even after the loop terminates.
- `for` loop variables will not be assigned in the current scope if the loop never did a single iteration.
- Generator expressions and list comprehensions do not leak loop variables by default.
- Exception handlers do not leak exception instance variables.

**注意事项**
- for 循环中的循环变量可以在循环结束后在当前作用域中被访问。
- 如果循环从未进行过一次迭代，则 for 循环变量不会在当前作用域中被赋值。
- 生成器表达式和列表推导式默认不会泄漏循环变量。
- 异常处理程序不会泄漏异常实例变量。