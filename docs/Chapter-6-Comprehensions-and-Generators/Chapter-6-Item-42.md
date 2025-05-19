# Chapter 6: Comprehensions and Generators (推导式与生成器)

## Item 42: Reduce Repetition in Comprehensions with Assignment Expressions (使用赋值表达式减少推导式中的重复)

A common pattern with comprehensions—including `list` , `dict` , and `set` variants—is the need to reference the same computation in multiple places. For example, say that I’m writing a program to manage orders for a fastener company. As new orders come in from customers, I need to be able to tell them whether or not I can fulfill their orders. Concretely, imagine that I need to verify that a request is sufficiently in stock and above the minimum threshold for shipping (e.g., in batches of 8), like this:

一个常见的模式是需要在多个地方引用同一个计算结果，这适用于包括 `list`、`dict` 和 `set` 变体的推导式。例如，我正在编写一个程序来管理一家紧固件公司的订单。当客户下新订单时，我需要能够告诉他们是否可以满足他们的订单需求。具体来说，假设我需要验证请求是否库存充足且超过了最低运输门槛（例如，以8个为一批次）：

```
stock = {
 "nails": 125,
 "screws": 35,
 "wingnuts": 8,
 "washers": 24,
}
order = ["screws", "wingnuts", "clips"]
def get_batches(count, size):
    return count // size

result = {}
for name in order:
     count = stock.get(name, 0)
     batches = get_batches(count, 8)
     if batches:
        result[name] = batches

print(result)
>>>
{'screws': 4, 'wingnuts': 1}
```

Here, I implement this looping logic more succinctly using a dictionary comprehension (see Item 40: “Use Comprehensions Instead of map and filter ” for best practices):

在这里，我使用字典推导式更简洁地实现了循环逻辑（参见条目40：“使用推导式代替 map 和 filter”了解最佳实践）：

```
found = {name: get_batches(stock.get(name, 0), 8)
         for name in order
         if get_batches(stock.get(name, 0), 8)}

print(found)
>>>
{'screws': 4, 'wingnuts': 1}
```

Although this code is more compact, the problem with it is that the `get_batches(stock.get(name, 0), 8)` expression is repeated. This hurts readability by adding visual noise and is technically unnecessary. The duplication also increases the likelihood of introducing a bug if the two expressions aren’t kept in sync. For example, here I’ve changed the first `get_batches` call to have `4` as its second parameter instead of `8` , which causes the results to be different:

虽然这段代码更加紧凑，但问题是 `get_batches(stock.get(name, 0), 8)` 这个表达式被重复了。这通过增加视觉噪音损害了可读性，并且技术上也是不必要的。此外，如果两个表达式没有保持同步，重复也会增加了引入错误的可能性。例如，在下面的例子中，我错误地将第一个 `get_batches` 调用的第二个参数改成了 `4` 而不是 `8`，这导致了结果的不同：

```
has_bug = {name: get_batches(stock.get(name, 0), 4)  # Wrong
           for name in order
           if get_batches(stock.get(name, 0), 8)}
print("Expected:", found)
print("Found: ", has_bug)
>>>
Expected: {'screws': 4, 'wingnuts': 1}
Found: {'screws': 8, 'wingnuts': 2}
```

An easy solution to these problems is to use an assignment expression——often called the walrus operator—as part of the comprehension (see Item 8: “Prevent Repetition with Assignment Expressions” for background):

解决这些问题的一个简单方法是在推导式中使用赋值表达式——通常称为海象运算符（参见条目8：“使用赋值表达式防止重复”了解背景信息）：

```
found = {name: batches for name in order
         if (batches := get_batches(stock.get(name, 0), 8))}
```

The assignment expression ( `batches := get_batches(...)` ) allows me to look up the value for each `order` key in the `stock` dictionary a single time, call `get_batches` once, and then store its corresponding value in the `batches` variable. I can then reference that variable elsewhere in the comprehension to construct the `dict` ’s contents instead of having to call `get_batches` a second time. Eliminating the redundant calls to `get` and `get_batches` may also improve performance by avoiding unnecessary computations for each item in order .

赋值表达式 (`batches := get_batches(...)`) 允许我在查找每个 `order` 键在 `stock` 字典中的值时只调用一次 `get_batches`，然后将其对应的值存储在 `batches` 变量中。然后可以在推导式的其他部分引用该变量来构建字典的内容，而不需要再次调用 `get_batches`。消除对 `get` 和 `get_batches` 的冗余调用还可以通过避免对 `order` 中的每个项目进行不必要的计算来提高性能。

It’s valid syntax to define an assignment expression in the value expression for a comprehension. But if you try to reference the variable it defines ( `tenth` ) in other parts of the comprehension, you might get an exception at runtime because of the order in which comprehensions are evaluated:

在推导式的值表达式中定义赋值表达式是一种有效的语法。但是如果你尝试在推导式的其他部分引用它定义的变量 (`tenth`)，你可能会在运行时得到异常，因为推导式的求值顺序导致的问题：

```
result = {name: (tenth := count // 10)
          for name, count in stock.items() if tenth > 0}
>>>
Traceback ...
NameError: name 'tenth' is not defined
```

You can fix this example by moving the assignment expression into the condition and then referencing the variable name it defined ( `tenth` ) in the comprehension’s value expression:

你可以通过将赋值表达式移至条件中，然后在推导式的值表达式中引用它定义的变量名 (`tenth`) 来修复此问题：

```
result = {name: tenth for name, count in stock.items()
          if (tenth := count // 10) > 0}
print(result)
>>>
{'nails': 12, 'screws': 3, 'washers': 2}
```

When a comprehension uses walrus operators, any corresponding variable names will be leaked into the containing scope (see Item 33: “Know How Closures Interact with Variable Scope and nonlocal ” for background):

当推导式使用海象运算符时，任何相应的变量名都会泄露到包含作用域中（参见条目33：“了解闭包如何与变量作用域和 nonlocal 相互作用”了解背景信息）：

```
half = [(squared := last**2)
        for count in stock.values()
        if (last := count // 2) > 10]
print(f"Last item of {half} is {last} ** 2 = {squared}")
>>>
Last item of [3844, 289, 144] is 12 ** 2 = 144
```

The leakage of these variable names is similar to what happens with a normal `for` loop:

这些变量名的泄露行为类似于正常 `for` 循环的行为：

```
for count in stock.values():
    last = count // 2
    squared = last**2

print(f"{count} // 2 = {last}; {last} ** 2 = {squared}")
>>>
24 // 2 = 12; 12 ** 2 = 144
```

However, this leakage behavior can be surprising because when comprehensions don’t use assignment expressions the loop variable names won’t leak like that (see Item 20: “Never Use for Loop Variables After the Loop Ends” and Item 84: “Beware of Exception Variables Disappearing” for more background):

然而，这种泄露行为可能会令人惊讶，因为在不使用赋值表达式的情况下，循环变量名不会像这样泄露（参见条目20：“永远不要在循环结束后使用 for 循环变量”和条目84：“注意异常变量消失的问题”了解更多信息）：

```
half = [count // 2 for count in stock.values()]
print(half)   # Works
print(count)  # Exception because loop variable didn't leak
>>>
[62, 17, 4, 12]
Traceback ...
NameError: name 'count' is not defined
```

Using an assignment expression also works the same way in generator expressions (see Item 44: “Consider Generator Expressions for Large List Comprehensions”). Here, I create an iterator of pairs containing the item name and the current count in stock instead of a `dict` instance:

使用赋值表达式在生成器表达式中同样适用（参见条目44：“考虑为大型列表推导式使用生成器表达式”）。在这里，我创建了一个包含项名称和当前库存数量的对的迭代器，而不是一个 `dict` 实例：

```
found = ((name, batches) for name in order
         if (batches := get_batches(stock.get(name, 0), 8)))
print(next(found))
print(next(found))
>>>
('screws', 4)
('wingnuts', 1)
```

**Things to Remember**
- Assignment expressions make it possible for comprehensions and generator expressions to reuse the value from one condition elsewhere in the same comprehension, which can improve readability and performance.
- Although it’s possible to use an assignment expression outside of a comprehension or generator expression’s condition, you should avoid doing so because it doesn’t work reliably.
- In comprehensions, variables from assignment expressions will leak into the enclosing scope, which is unlike how comprehension loop variables won’t leak.

**注意事项**
- 赋值表达式使得推导式和生成器表达式能够在同一推导式的其他地方重用来自一个条件的值，这可以提高可读性和性能。
- 尽管可以在推导式或生成器表达式的条件之外使用赋值表达式，但你应该避免这样做，因为它不能可靠地工作。
- 在推导式中，来自赋值表达式的变量会泄露到封闭作用域中，这一点不同于推导式循环变量不会泄露的方式。