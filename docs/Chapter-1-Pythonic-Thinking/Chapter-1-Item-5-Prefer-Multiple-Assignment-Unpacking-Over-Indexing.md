# Chapter 1: Pythonic Thinking (第一章 用Pythonic方式来思考)

## Item 5: Prefer Multiple Assignment Unpacking Over Indexing(使用多重赋值解包代替索引访问)

Python has a built-in tuple type that can be used to create immutable, ordered sequences of values (see Item 56: “Prefer dataclasses for Creating Immutable Objects” for similar data structures). Tuples can be empty or contain a single item:

Python 有一个内置的元组 (tuple) 类型，可以用于创建不可变、有序的值序列（有关类似的数据结构，请参见条目 56：“优先使用 dataclasses 创建不可变对象”）。元组可以为空，也可以只包含一个元素：

```bash
no_snack = ()
snack = ("chips",)
```

Tuples can also include multiple items, such as in these key-value pairs from a dictionary:

元组也可以包含多个元素，例如字典中的键值对：

```bash
snack_calories = {
 "chips": 140,
 "popcorn": 80,
 "nuts": 190,
}
items = list(snack_calories.items())
print(items)
>>>
[('chips', 140), ('popcorn', 80), ('nuts', 190)]
```

The members in tuples can be accessed through numerical indexes and slices, just like a list :

元组中的成员可以通过数字索引和切片访问，就像列表一样：

```bash
item = ("Peanut butter", "Jelly")
first_item = item[0] # Index
first_half = item[:1] # Slice
print(first_item)
print(first_half)
>>>
Peanut butter
('Peanut butter',)
```

Once a tuple is created, you can’t modify it by assigning a new value to an index:

```bash
pair = ("Chocolate", "Peanut butter")
pair[0] = "Honey"
>>>
Traceback ...
TypeError: 'tuple' object does not support item a
```

一旦元组被创建，你就不能通过为某个索引赋新值的方式来修改它：

Python also has syntax for unpacking, which allows for assigning multiple values in a single statement. The patterns that you specify in unpacking assignments look a lot like trying to mutate tuples—which isn’t allowed—but they actually work quite differently. For example, if you know that a tuple is a pair, instead of using indexes to access its values, you can assign it to a tuple of two variable names:

Python 还提供了一种叫做“解包”(unpacking) 的语法，允许你在一条语句中为多个变量赋值。你所指定的解包模式看起来像是在尝试修改元组——这是不允许的——但实际上它们的工作方式完全不同。例如，如果你知道一个元组是一个二元组，你可以将其直接赋值给两个变量名，而无需使用索引来访问它的值：

```bash
item = ("Peanut butter", "Jelly")
first, second = item # Unpacking
print(first, "and", second)
>>>
Peanut butter and Jelly
```

Unpacking has less visual noise than accessing the tuple’s indexes, and it often requires fewer lines of code. The same pattern matching syntax of unpacking works when assigning to lists, sequences, and multiple levels of arbitrary iterables within iterables. I don’t recommend doing the following in your code, but it’s important to know that it’s possible and how it works:

相比使用索引访问元组元素，解包更简洁直观，通常也能减少代码行数。这种模式匹配的解包语法也适用于列表、任意嵌套的可迭代对象等。虽然不建议你在实际代码中这么做，但了解它是可能的以及其工作原理仍然很重要：

```bash
favorite_snacks = {
 "salty": ("pretzels", 100),
 "sweet": ("cookies", 180),
 "veggie": ("carrots", 20),
}
((type1, (name1, cals1)),
 (type2, (name2, cals2)),
 (type3, (name3, cals3))) = favorite_snacks.items
print(f'Favorite {type1} is {name1} with {cals1} 
print(f'Favorite {type2} is {name2} with {cals2} 
print(f'Favorite {type3} is {name3} with {cals3} 
>>>
Favorite salty is pretzels with 100 calories
Favorite sweet is cookies with 180 calories
Favorite veggie is carrots with 20 calories
```

Newcomers to Python may be surprised to learn that unpacking can even be used to swap values in place without the need to create temporary variables. Here, I use typical syntax with indexes to swap the values between two positions in a list as part of an ascending order sorting algorithm:

Python 初学者可能会惊讶地发现，解包甚至可以在不创建临时变量的情况下就地交换值。下面的例子中，我使用传统的索引方法在一个排序算法中交换列表中两个位置的值：

```bash
def bubble_sort(a):
    for _ in range(len(a)):
        for i in range(1, len(a)):
            if a[i] < a[i - 1]:
                temp = a[i]
                a[i] = a[i - 1]
                a[i - 1] = temp

names = ["pretzels", "carrots", "arugula", "bacon"]
bubble_sort(names)
print(names)

>>>
['arugula', 'bacon', 'carrots', 'pretzels']
```

However, with unpacking syntax, it’s possible to swap indexes in a single line:

然而，使用解包语法，我们可以将交换操作写成一行：

```bash
def bubble_sort(a):
    for _ in range(len(a)):
        for i in range(1, len(a)):
            if a[i] < a[i - 1]:
                a[i - 1], a[i] = a[i], a[i - 1] 
names = ["pretzels", "carrots", "arugula", "bacon"]
bubble_sort(names)
print(names)

>>>
['arugula', 'bacon', 'carrots', 'pretzels']
```

The way this swap works is that the right side of the assignment ( a[i], a[i-1] ) is evaluated first, and its values are put into a new temporary, unnamed tuple (such as ("carrots", "pretzels") on the first iteration of the loops). Then, the unpacking pattern from the left side of the assignment ( a[i-1], a[i] ) is used to receive that tuple value and assign it to the variable names a[i-1] and a[i] , respectively. This replaces "pretzels" with "carrots" at index 0 and "carrots" with "pretzels" at index 1 . Finally, the temporary unnamed tuple silently goes away.

这个交换操作之所以有效，是因为赋值表达式的右侧（a[i], a[i-1]）会先被求值，并放入一个新的临时匿名元组（比如第一次循环时是 ("carrots", "pretzels")），然后左侧的解包模式（a[i-1], a[i]）会接收该元组并分别赋值给 a[i-1] 和 a[i]，从而完成值的交换。

Another valuable application of unpacking is in the target list of for loops and similar constructs, such as comprehensions and generator expressions (see Item 40: “Use Comprehensions Instead of map and filter ” and Item 44: “Consider Generator Expressions for Large List Comprehensions”). For example, here I iterate over a list of snacks without using unpacking:

解包的另一个重要应用场景是在 for 循环的目标列表中，包括列表推导式和生成器表达式等场景（详见 Item 40 和 Item 44）。例如，下面的代码在没有使用解包的情况下遍历零食列表：

```bash
snacks = [("bacon", 350), ("donut", 240), ("muffin", 190)]
for i in range(len(snacks)):
    item = snacks[i]
    name = item[0]
    calories = item[1]
    print(f"#{i+1}: {name} has {calories} calorie")
    
>>>
#1: bacon has 350 calories
#2: donut has 240 calories
#3: muffin has 190 calories
```

This works, but it’s noisy. There are a lot of extra characters required in order to index into the various levels of the snacks structure. Now, I achieve the same output by using unpacking along with the enumerate built-in function (see Item 17: “Prefer enumerate Over range ”):

这段代码是可行的，但略显冗长。为了访问每个元素，我们需要编写很多额外的索引代码。现在我们使用 enumerate 和解包实现同样的输出效果：

```bash
for rank, (name, calories) in enumerate(snacks, 1):
    print(f"#{rank}: {name} has {calories} calori
>>>
#1: bacon has 350 calories
#2: donut has 240 calories
#3: muffin has 190 calories
```

This is the Pythonic way to write this type of loop; it’s short and easy to understand. There’s usually no need to access anything using indexes.

这才是 Pythonic 的写法，简洁明了。通常不需要再通过索引去访问数据。


Python provides additional unpacking functionality for list construction (see Item 16: “Prefer Catch-All Unpacking Over Slicing”), function arguments (see Item 34: “Reduce Visual Noise with Variable Positional Arguments”), keyword arguments (see Item 35: “Provide Optional Behavior with Keyword Arguments”), multiple return values (see Item 31: “Return Dedicated Result Objects Instead of Requiring Function Callers to Unpack More Than Three Variables”), and structural pattern matching (see Item 9: “Consider match for Destructuring in Flow Control, Avoid When if Statements Are Sufficient”), and more.

Python 提供了更多关于解包的功能，包括列表构造（详见 Item 16）、函数参数（详见 Item 34）、关键字参数（详见 Item 35）、多返回值（详见 Item 31）、结构化模式匹配（详见 Item 9）等等。

Using unpacking wisely will enable you to avoid indexing when possible, resulting in clearer and more Pythonic code. However, these features are not without pitfalls to consider (see Item 6: “Always Surround Single-Element Tuples with Parentheses”). Unpacking also doesn’t work in assignment expressions (see Item 8: “Prevent Repetition with Assignment Expressions”).

合理使用解包可以帮助你避免显式索引，写出更清晰、更具 Pythonic 风格的代码。当然，这些特性也有一些需要注意的地方（详见 Item 6）。此外，在赋值表达式中无法使用解包（详见 Item 8）。

**Things to Remember**

- Python has special syntax called unpacking for assigning multiple values in a single statement.
- Unpacking is generalized in Python and can be applied to any iterable, including many levels of iterables within iterables.
- You can reduce visual noise and increase code clarity by using unpacking to avoid explicitly indexing into sequences.

**注意事项**

- Python 提供了一种特殊的语法叫“解包”，用于在单个语句中为多个变量赋值。
- 解包机制非常通用，可以应用于任何可迭代对象，包括多层次嵌套的可迭代结构。
- 使用解包可以减少代码视觉噪音，提高代码的可读性和清晰度。