# Chapter 1: Pythonic Thinking (第一章 用Pythonic方式来思考)

## Item 8: Prevent Repetition with Assignment Expressions

An assignment expression—also known as the walrus operator—is a new syntax feature introduced in Python 3.8 to solve a long-standing problem with the language that can cause code duplication. Whereas normal assignment statements are written a = b and pronounced "a equals b", these assignments are written a := b and pronounced "a walrus b" (because := looks like a pair of eyeballs and tusks).

赋值表达式（也称为海象运算符）是 Python 3.8 中引入的一种新语法特性，用于解决语言中长期存在的一个问题——它可能导致代码重复。普通赋值语句写为 a = b，读作“a 等于 b”，而赋值表达式则写为 a := b，读作“a 海象 b”（因为 := 看起来像一对眼睛和长牙）。

Assignment expressions are useful because they enable you to assign variables in places where assignment statements are disallowed, such as in the test expression of an if statement. An assignment expression’s value evaluates to whatever was assigned to the identifier on the left side of the walrus operator.

赋值表达式之所以有用，是因为它们允许你在原本不允许赋值语句的地方进行变量赋值，例如 if 语句的条件表达式中。赋值表达式的值就是被赋给左边标识符的那个值。

For example, say that I have a basket of fresh fruit that I’m trying to manage for a juice bar. Here, I define the contents of the basket:

举个例子，假设我有一个装满新鲜水果的篮子，我要管理这些水果，以便制作果汁。这里定义了篮子里的内容：

```
fresh_fruit = {
 "apple": 10,
 "banana": 8,
 "lemon": 5,
}
```

When a customer comes to the counter to order some lemonade, I need to make sure there is at least one lemon in the basket to squeeze. Here, I do this by retrieving the count of lemons and then using an if statement to check for a non-zero value:

当有顾客来柜台点柠檬水时，我需要确保篮子里至少有一个柠檬可以榨汁。以下是通过获取柠檬数量并使用 if 语句检查其是否为非零值来实现的：

```
def make_lemonade(count):
 ...
def out_of_stock():
 ...
count = fresh_fruit.get("lemon", 0)
if count:
 make_lemonade(count)
else:
 out_of_stock()
>>>
Making 5 lemons into lemonade
```

The problem with this seemingly simple code is that it’s noisier than it needs to be. The count variable is used only within the first block of the if statement. Defining count above the if statement causes it to appear to be more important than it really is, as if all code that follows, including the else block, will need to access the count variable, when in fact that is not the case.

这段看似简单的代码的问题在于它比必要的情况更冗杂。变量 count 只在 if 语句块内使用，但在 if 语句之前定义它会让它看起来更重要。这给人一种错觉，即所有后续代码，包括 else 块，都会访问 count 变量，而实际上并非如此。

This pattern of fetching a value, checking to see if it’s truthy, and then using it is extremely common in Python. Many programmers try to work around the multiple references to count with a variety of tricks that hurt readability (see Item 4: “Write Helper Functions Instead of Complex Expressions” and Item 7: “Consider Conditional Expressions for Simple Inline if Statements”). Luckily, assignment expressions were added to the language to streamline this type of code. Here, I rewrite the example above using the walrus operator:

这种模式在 Python 中非常常见：获取一个值，检查它是否为真值，然后使用它。许多程序员尝试用各种技巧来避免多次引用 count，但这往往会损害代码可读性（参见条目 4 和 条目 7）。幸运的是，Python 引入了赋值表达式来简化这类代码。下面使用海象运算符重写了上面的例子：

```
if count := fresh_fruit.get("lemon", 0):
 make_lemonade(count)
else:
 out_of_stock()
```

Although this is only one line shorter, it’s a lot more readable because it’s now clear that count is only relevant to the first block of the if statement. The assignment expression first assigns a value to the count variable, and then evaluates that value in the context of the if statement to determine how to proceed with flow control. This two-step behavior—assign and then evaluate—is the fundamental nature of the walrus operator.

虽然只少了一行，但可读性有了很大提升，因为现在清楚地表明 count 仅与 if 语句的第一个代码块相关。赋值表达式首先将值赋给 count 变量，然后在 if 语句的上下文中评估该值，以决定程序流程如何继续。这种两步行为——赋值然后评估——是海象运算符的基本特性。

Lemons are quite potent, so only one is needed for my lemonade recipe, which means a non-zero, truthy check is good enough. If a customer orders a cider, though, I need to make sure that I have at least four apples. Here, I do this by fetching the count from the fresh_fruit dictionary, and then using a comparison in the if statement test expression:

柠檬的效力很强，所以我的柠檬水配方只需要一个，这意味着只要判断 count 是否为真值即可。如果顾客点了苹果酒，则需要确保至少有四个苹果。以下是通过从 fresh_fruit 字典中获取 count 并在 if 语句的条件表达式中进行比较实现的：

```
def make_cider(count):
 ...
count = fresh_fruit.get("apple", 0)
if count >= 4:
 make_cider(count)
else:
 out_of_stock()
>>>
Making cider with 10 apples
```

This has the same problem as the lemonade example, where the assignment of count puts distracting emphasis on that variable. Here, I improve the clarity of this code by also using the walrus operator:

这也与柠檬水示例有同样的问题，其中 count 的赋值增加了不必要的干扰。下面是通过使用海象运算符来提高代码清晰度的改进版本：

```
if (count := fresh_fruit.get("apple", 0)) >= 4:
 make_cider(count)
else:
 out_of_stock()
```

This works as expected and makes the code one line shorter. It’s important to note how I needed to surround the assignment expression with parentheses to compare it with 4 in the if statement. In the lemonade example, no surrounding parentheses were required because the assignment expression stood on its own as a non-zero, truthy check; it wasn’t a subexpression of a larger expression. As with other expressions, you should avoid surrounding assignment expressions with parentheses when possible to reduce visual noise.

这样也能按预期工作，并使代码减少一行。请注意我在 if 语句中将赋值表达式括在括号中。在柠檬水示例中不需要括号，因为赋值表达式本身作为一个非零真值检查；而在苹果酒示例中，它是较大表达式的一部分。与其他表达式一样，在可能的情况下应避免为赋值表达式加括号，以减少视觉噪声。

Another common variation of this repetitive pattern occurs when I need to assign a variable in the enclosing scope depending on some condition, and then reference that variable shortly afterward in a function call. For example, say that a customer orders some banana smoothies. In order to make them, I need to have at least two bananas’ worth of slices, or else an OutOfBananas exception is raised. Here, I implement this logic in a typical way:

另一个常见的重复模式是当你需要根据某些条件在外层作用域中分配变量，然后在函数调用中立即引用该变量时。例如，当顾客订购香蕉奶昔时，为了制作它们，我需要至少两个香蕉切片，否则会引发 OutOfBananas 异常。以下是典型的实现方式：

```
def slice_bananas(count):
 ...
class OutOfBananas(Exception):
 pass
def make_smoothies(count):
 ...
pieces = 0
count = fresh_fruit.get("banana", 0)
if count >= 2:
 pieces = slice_bananas(count)
try:
 smoothies = make_smoothies(pieces)
except OutOfBananas:
 out_of_stock()
>>>
Slicing 8 bananas
Making a smoothies with 32 banana slices
```

The other common way to do this is to put the pieces = 0 assignment in the else block:

另一种常见做法是将 pieces = 0 赋值移到 else 块中：

```
count = fresh_fruit.get("banana", 0)
if count >= 2:
 pieces = slice_bananas(count)
else:
 pieces = 0 # Moved
try:
 smoothies = make_smoothies(pieces)
except OutOfBananas:
 out_of_stock()
```

This second approach can feel odd because it means that the pieces variable has two different locations—in each block of the if statement—where it can be initially defined. This split definition technically works because of Python’s scoping rules (see Item 33: “Know How Closures Interact with Variable Scope and nonlocal ”), but it isn’t easy to read or discover, which is why many people prefer the construct above, where the pieces = 0 assignment is first.

第二种方法可能会让人感觉有些奇怪，因为它意味着 pieces 变量可以在 if 语句的每个块中被定义。这种分拆定义从技术上讲是可行的（因为 Python 的作用域规则），但它不容易阅读或发现，这就是为什么许多人更喜欢前面的方式——先定义 pieces = 0。

The walrus operator can again be used to shorten this example by one line of code. This small change removes any emphasis on the count variable. Now, it’s clearer that pieces will be important beyond the if statement:

海象运算符再次被用来缩短这个例子一行代码。这个小改动消除了对 count 变量的关注。现在更容易看出 pieces 在 if 语句之外的重要性：

```
pieces = 0
if (count := fresh_fruit.get("banana", 0)) >= 2: 
 pieces = slice_bananas(count)
try:
 smoothies = make_smoothies(pieces)
except OutOfBananas:
 out_of_stock()
```

Using the walrus operator also improves the readability of splitting the definition of pieces across both parts of the if statement. It’s easier to trace the pieces variable when the count definition no longer precedes the if statement:

使用海象运算符还可以提高将 pieces 定义分布在 if 语句两部分中的可读性。当 count 的定义不再位于 if 语句之前时，追踪 pieces 变量更容易：

```
if (count := fresh_fruit.get("banana", 0)) >= 2:
 pieces = slice_bananas(count)
else:
 pieces = 0 # Moved
try:
 smoothies = make_smoothies(pieces)
except OutOfBananas:
 out_of_stock()
```

One frustration that programmers who are new to Python often have is the lack of a flexible switch / case statement. The general style for approximating this type of functionality is to have a deep nesting of multiple if , elif , and else blocks.

Python 新手程序员经常遇到的一个烦恼是缺乏灵活的 switch/case 语句。通常采用深度嵌套的多个 if、elif 和 else 块来近似实现此功能。

For example, imagine that I want to implement a system of precedence so that each customer automatically gets the best juice available and doesn’t have to order. Here, I define logic to make it so banana smoothies are served first, followed by apple cider, and then finally lemonade:

例如，假设我想实现一个优先级系统，使每位顾客自动获得最好的果汁，而无需自己点单。以下是定义逻辑的方法，使得香蕉奶昔优先供应，其次是苹果酒，最后是柠檬水：

```
count = fresh_fruit.get("banana", 0)
if count >= 2:
    pieces = slice_bananas(count)
    to_enjoy = make_smoothies(pieces)
else:
     count = fresh_fruit.get("apple", 0)
     if count >= 4:
        to_enjoy = make_cider(count)
     else:
        count = fresh_fruit.get("lemon", 0)
         if count:
            to_enjoy = make_lemonade(count)
         else:
            to_enjoy = "Nothing"
```

Ugly constructs like this are surprisingly common in Python code. Luckily, the walrus operator provides an elegant solution that can feel nearly as versatile as dedicated syntax for switch / case statements:

像这样的丑陋结构在 Python 代码中出奇地常见。幸运的是，海象运算符提供了一个优雅的解决方案，几乎可以像专门的 switch/case 语句一样灵活：

```
if (count := fresh_fruit.get("banana", 0)) >= 2:
    pieces = slice_bananas(count)
    to_enjoy = make_smoothies(pieces)
elif (count := fresh_fruit.get("apple", 0)) >= 4
    to_enjoy = make_cider(count)
elif count := fresh_fruit.get("lemon", 0):
    to_enjoy = make_lemonade(count)
else:
    to_enjoy = "Nothing"
```

The version that uses assignment expressions is only five lines shorter than the original, but the improvement in readability is vast due to the reduction in nesting and indentation. If you ever see the previous ugly constructs emerge in your code, I suggest that you move them over to using the walrus operator if possible (see Item 9: “Consider match for Destructuring in Flow Control, Avoid When if Statements Are Sufficient” for another approach).

使用赋值表达式的版本比原始版本只少五行，但由于减少了嵌套和缩进，可读性得到了极大的改善。如果你在代码中看到上述丑陋的结构，请考虑在可能的情况下使用海象运算符（参见条目 9 了解另一种方法）。

Another common frustration of new Python programmers is the lack of a do / while loop construct. For example, say that I want to bottle juice as new fruit is delivered until there’s no fruit remaining. Here, I implement this logic with a while loop:

另一个新手 Python 程序员常见的烦恼是缺乏 do/while 循环结构。例如，假设我希望在新水果送达时持续制作果汁，直到没有水果为止。以下是使用 while 循环实现的逻辑：

```
def pick_fruit():
 ...
def make_juice(fruit, count):
 ...
bottles = []
fresh_fruit = pick_fruit()
while fresh_fruit:
    for fruit, count in fresh_fruit.items():
        batch = make_juice(fruit, count)
        bottles.extend(batch)
    fresh_fruit = pick_fruit()
```

This is repetitive because it requires two separate `fresh_fruit = pick_fruit()` calls: one before the loop to set initial conditions, and another at the end of the loop to replenish the list of delivered fruit.

这是重复的，因为它要求两次单独的 fresh_fruit = pick_fruit() 调用：一次在循环前设置初始条件，另一次在循环结束时补充送来的水果。

A strategy for improving code reuse in this situation is to use the loop-and￾a-half idiom. This eliminates the redundant lines, but it also undermines the while loop’s contribution by making it a dumb infinite loop. Now, all of the flow control of the loop depends on the conditional break statement:

一种改进这种情况代码重用的策略是使用“循环与半次循环”（loop-and-a-half）惯用法。这样可以消除冗余代码，但也削弱了 while 循环的作用，使其成为一个傻瓜式的无限循环。现在，循环的所有流程控制都依赖于条件 break 语句：

```
bottles = []
while True: # Loop
 fresh_fruit = pick_fruit()
 if not fresh_fruit: # And a half
    break
 for fruit, count in fresh_fruit.items():
     batch = make_juice(fruit, count)
     bottles.extend(batch)
```

The walrus operator obviates the need for the loop-and-a-half idiom by allowing the fresh_fruit variable to be reassigned and then conditionally evaluated each time through the while loop. This solution is short and easy to read, and it should be the preferred approach in your code:

海象运算符可以通过在每次循环中重新赋值和条件评估 fresh_fruit 来省去“循环与半次循环”惯用法的需要。这种方法简洁易读，应该是你的首选方法：

```
bottles = []
while fresh_fruit := pick_fruit(): # Changed
  for fruit, count in fresh_fruit.items():
    batch = make_juice(fruit, count)
    bottles.extend(batch)
```

There are many other situations where assignment expressions can be used to eliminate redundancy (see Item 42: “Reduce Repetition in Comprehensions with Assignment Expressions” for an example). In general, when you find yourself repeating the same expression or assignment multiple times within a grouping of lines, it’s time to consider using assignment expressions in order to improve readability.

还有许多其他情况可以使用赋值表达式来消除冗余（参见条目 42）。一般来说，当你发现自己在一个代码组内多次重复相同的表达式或赋值时，就该考虑使用赋值表达式来提高代码的可读性了。


**Things to Remember**

- Assignment expressions use the walrus operator ( := ) to both assign and evaluate variable names in a single expression, thus reducing repetition.
- When an assignment expression is a subexpression of a larger expression, it must be surrounded with parentheses.
- Although switch / case statements and do / while loops are not available in Python, their functionality can be emulated much more clearly by using assignment expressions.

**注意事项**
- 赋值表达式使用海象运算符 :=，可以在单个表达式中同时进行变量赋值和求值，从而减少重复。
- 当赋值表达式是更大表达式的一个子表达式时，必须用括号括起来。
- 尽管 Python 中没有 switch/case 语句和 do/while 循环，但可以通过使用赋值表达式更加清晰地模拟它们的功能。