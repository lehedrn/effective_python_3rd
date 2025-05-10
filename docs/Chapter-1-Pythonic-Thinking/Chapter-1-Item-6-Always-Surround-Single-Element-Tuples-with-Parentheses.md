# Chapter 1: Pythonic Thinking (第一章 用Pythonic方式来思考)

## Item 6: Always Surround Single-Element Tuples with Parentheses(始终使用括号包裹单元素元组)

In Python there are four kinds of tuple literal values. The first kind is a comma-separated list of items inside open and close parentheses:

在 Python 中，有四种元组字面量的写法。第一种是一个由逗号分隔的元素列表，并被小括号包裹：

```bash
first = (1, 2, 3)
```

The second kind is the just like the first, but with an optional trailing comma included, which allows for consistency when going across multiple lines and eases editing:

第二种与第一种类似，但允许在最后添加一个可选的逗号，这有助于跨多行书写时保持一致性，并简化编辑操作：

```bash
second = (1, 2, 3,)
second_wrapped = (
    1,
    2,
    3, # Optional comma
)
```

The third kind is a comma-separated list of items without any surrounding parentheses:

第三种是不带任何括号、仅由逗号分隔的元素列表：

```bash
third = 1, 2, 3
```

And finally, the fourth kind is just like the third, but with an optional trailing comma:

第四种与第三种类似，也允许最后有一个逗号：

```bash
fourth = 1, 2, 3,
```

Python treats all of these constructions as the same value:

在 Python 中，以上这些写法都会被视为相同的值：

```bash
assert first == second == third == fourth
```

However, there are also three special cases in creating tuples that need to be considered. The first case is the empty tuple, which is merely open and close parentheses:

然而，在创建元组时还有三种特殊情况需要注意。 第一个特殊情况是空元组，只需一对空的小括号即可：

```bash
empty = ()
```

The second special case is the form of single-element tuples: you must include a trailing comma. If you leave out the trailing comma, then what you have is a parenthesized expression instead of a tuple:

第二个特殊情况是单元素元组：你必须在该元素后加上一个逗号。如果你省略了这个逗号，那么它就只是一个被括号包裹的表达式，而不是一个元组：

```bash
single_with = (1,)
single_without = (1)
assert single_with != single_without
assert single_with[0] == single_without
```

And the third special case is similar to the second one except without the parentheses:

第三个特殊情况与第二个类似，只是没有括号：

```bash
single_parens = (1,)
single_no_parens = 1,
assert single_parens == single_no_parens
```

This third special case—a trailing comma with no parentheses—can cause unexpected problems that are hard to diagnose. Consider the following function call from an E-commerce website. Can you spot the bug?

第三种情况——即没有括号但有结尾逗号的形式——可能会导致难以察觉的错误。考虑下面来自一个电子商务网站的函数调用。你能发现其中的 bug 吗？

```bash
to_refund = calculate_refund(
 get_order_value(user, order.id),
 get_tax(user.address, order.dest),
 adjust_discount(user) + 0.1),
```

You might expect that the return type is an integer, float, or decimal number containing the amount of money to be refunded to a customer. But in fact, it’s a tuple!

你可能期望返回的是一个整数、浮点数或十进制数字，表示应退还给客户的金额。但实际上，它却是一个元组！

```bash
print(type(to_refund))
>>>
<class 'tuple'>
```

The problem is the extraneous comma at the end of the final line. Removing the comma fixes the code:

问题出在最后一行多余的逗号上。删除这个逗号即可修复代码：

```bash
to_refund2 = calculate_refund(
 get_order_value(user, order.id),
 get_tax(user.address, order.dest),
 adjust_discount(user) + 0.1,
) # No trailing comma
print(type(to_refund2))
>>>
<class 'int'>
```

A comma character like this could be inserted into your code by accident, causing a change in behavior that’s hard to track down even upon close inspection. The errant separator could also be left over from editing the items in a tuple , list , set , or function call and forgetting to remove a leftover comma. It happens more often than you might expect!

这样的逗号可能是不小心插入的，从而导致程序行为发生微妙变化，即使仔细检查也可能难以发现。这种多余的逗号也可能是在编辑元组、列表、集合或函数调用的参数列表时忘记删除而遗留下来的。这种情况比你想象的更常见！

Another problem with single-element tuples without surrounding parentheses is that they can’t be easily moved from assignments into expressions. For example, if I want to copy the 1, single-element tuple below into a list, I have to surround it with parentheses. If I forget to do that, I end up passing more items or arguments to the surrounding form instead of a tuple:

另一个问题是，没有括号的单元素元组不容易从赋值语句中直接移到表达式中。例如，如果你想将下面这个 1, 单元素元组复制到一个列表中，就必须为它加上括号。如果忘了加括号，就会向列表中传入多个项或参数，而不是一个元组：

```bash
value_a = 1, # No parentheses, right
list_b = [1,] # No parentheses, wrong
list_c = [(1,)] # Parentheses, right
print('A:', value_a)
print('B:', list_b)
print('C:', list_c)

>>>
A: (1,)
B: [1]
C: [(1,)]
```

Single-element tuples may also be on the left side of an assignment as part of the unpacking syntax (see Item 5: “Prefer Multiple Assignment Unpacking Over Indexing”, Item 31: “Return Dedicated Result Objects Instead of Requiring Function Callers to Unpack More Than Three Variables”, and Item 16: “Prefer Catch-All Unpacking Over Slicing”). Surprisingly, all of these assignments are allowed, depending on the value returned, but they produce three different results:

单元素元组也可能出现在赋值语句的左侧，作为解包语法的一部分（参见其他相关条目）。令人惊讶的是，所有这些写法都根据返回值的不同而被允许，但它们会产生三种完全不同的结果：

```bash
def get_coupon_codes(user):
 ...
 return [['DEAL20']]
 ...
(a1,), = get_coupon_codes(user)
(a2,) = get_coupon_codes(user)
(a3), = get_coupon_codes(user)
(a4) = get_coupon_codes(user)
a5, = get_coupon_codes(user)
a6 = get_coupon_codes(user)
assert a1 not in (a2, a3, a4, a5, a6)
assert a2 == a3 == a5
assert a4 == a6
```

Sometimes automatic source code formatting tools (see Item 2: “Follow the PEP 8 Style Guide”) and static analysis tools (see Item 3: “Never Expect Python to Detect Errors at Compile Time”) can make the trailing comma problem more visible. But often it goes unnoticed until a program or test suite starts acting strange. The best way to avoid this situation is to always write single-element tuples with surrounding parentheses whether they’re on the left or the right of an assignment.

有时，自动格式化工具（参见条目 2）和静态分析工具（参见条目 3）可以让这种多余逗号的问题变得明显一些。但更多时候，这些问题直到程序或测试套件出现异常之前都不会被发现。要避免这种情况的最佳做法是：无论是在赋值语句的左边还是右边，始终使用括号显式地写出单元素元组。

**Things to Remember**

- Tuple literal values in Python may have optional surrounding parentheses and optional trailing commas, except for a few special cases.
- Single-element tuples require a trailing comma after the one value, and may have optional surrounding parentheses.
- It’s all too easy to have an extraneous trailing comma at the end of an expression, changing its meaning into a single-element tuple that breaks a program.

**注意事项**

- Python 中的元组字面量可以带有可选的括号和可选的结尾逗号，但有一些特殊情况。
- 单元素元组必须在其唯一一个元素后面加上逗号，也可以选择是否使用括号。
- 在表达式的末尾很容易意外地多打一个逗号，从而使其变成一个破坏程序的单元素元组。