# Chapter 3: Loops and Iterators (循环和迭代器)

## Item 22: Never Modify Containers While Iterating over Them; Use Copies or Caches Instead (永远不要在迭代容器的同时修改它们；使用副本或缓存代替)

There are many gotchas in Python caused by surprising iteration behaviors (see Item 21: “Be Defensive When Iterating Over Arguments” for another common situation). For example, if you add a new item to a dictionary while iterating over it, Python will raise a runtime exception:

Python中有许多令人惊讶的迭代行为导致的问题（参见条目21）。例如，如果你在迭代字典时向其中添加一个新项，Python将引发运行时异常：

```
search_key = "red"
my_dict = {"red": 1, "blue": 2, "green": 3}

for key in my_dict:
    if key == "blue":
        my_dict["yellow"] = 4  # Causes error
>>>
Traceback ...
RuntimeError: dictionary changed size during iteration
```

A similar error occurs if you delete an item from a dictionary while iterating over it:

如果你在迭代字典时删除一个项，也会发生类似的错误：

```
my_dict = {"red": 1, "blue": 2, "green": 3}
for key in my_dict:
    if key == "blue":
        del my_dict["green"]  # Causes error
>>>
Traceback ...
RuntimeError: dictionary changed size during iteration
```

An error won’t occur if, instead of adding or deleting keys from a dictionary, you only change their associated values—surprisingly inconsistent with the behaviors above:

如果你在迭代字典时仅更改其关联值而不是添加或删除键，则不会发生错误——与上述行为相比显得出奇地不一致：

```
my_dict = {"red": 1, "blue": 2, "green": 3}
for key in my_dict:
    if key == "blue":
        my_dict["green"] = 4  # Okay
print(my_dict)

>>>
{'red': 1, 'blue': 2, 'green': 4}
```

Sets work similarly to dictionaries and will raise a exception at runtime if you change their size by adding or removing items during iteration:

集合的工作方式类似于字典，如果在迭代期间通过添加或删除项来改变其大小，将在运行时引发异常：

```
my_set = {"red", "blue", "green"}
    
for color in my_set:
    if color == "blue":
        my_set.add("yellow")  # Causes error
>>>
Traceback ...
RuntimeError: Set changed size during iteration
```

However, the behavior of set also seems inconsistent because trying to add an item that already exists in a set won’t cause any problems while you’re iterating over it—re-adding is allowed because the set’s size didn’t change:

然而，集合的行为也似乎不一致，因为在迭代期间重新添加已存在的项不会引起任何问题——允许重复添加，因为集合的大小没有改变：

```
my_set = {"red", "blue", "green"}
for color in my_set:
    if color == "blue":
        my_set.add("green")  # Okay
>>>
{'green', 'blue', 'red'}
```

Similar to dictionaries, and also surprisingly inconsistent, lists can have any existing index overwritten during iteration with no problems:

类似于字典，列表在迭代过程中可以覆盖任何现有索引的值而不会出现问题，这同样显得出奇地不一致：

```
my_list = [1, 2, 3]

for number in my_list:
    print(number)
    if number == 2:
        my_list[0] = -1  # Okay

print(my_list)
>>>
1
2
3
[-1, 2, 3]
```

But if you try to insert an element into a list before the current iterator position, your code will get stuck in an infinite loop:

但如果你尝试在当前迭代位置之前插入元素到列表中，代码将会陷入无限循环：

```
my_list = [1, 2, 3]
for number in my_list:
    print(number)
    if number == 2:
        my_list.insert(0, 4) # Causes error
>>>
1
2
2
2
2
2
...
```

However, appending to a list after the current iterator position is not a problem—the index-based iterator hasn’t gotten that far yet—which is again, surprisingly inconsistent behavior:

但是，在当前迭代位置之后追加元素到列表中则没有问题——索引迭代器尚未到达那么远的位置——这再次表现出令人惊讶的不一致行为：

```
my_list = [1, 2, 3]
for number in my_list:
    print(number)
    if number == 2:
        my_list.append(4)  # Okay this time
print(my_list)
>>>
1
2
3
4
[1, 2, 3, 4]
```

Looking at each of the examples above, it can be hard to guess whether the code will work in all cases or not. Modifying containers during iteration can be especially error-prone in situations where the modification point changes based on input to the algorithm—in some cases it’ll work and in others there will be an error. Thus, my advice is to never modify containers while you iterate over them.

查看上述每个示例，很难猜测代码在所有情况下是否都能正常工作。在迭代容器时修改容器可能会特别容易出错，尤其是在算法的修改点根据输入变化的情况下——有时能正常运行，有时则会出错。因此，我的建议是永远不要在迭代容器的同时修改它们。

If you still need to make modifications during iteration due to the nature of your algorithm, you should simply make a copy of the container you want to iterate and apply modifications to the original (see Item 30: “Know That Function Arguments Can Be Mutated”). For example, with dictionaries I can copy the keys:

如果你由于算法性质仍需要在迭代期间进行修改，你应该简单地创建你要迭代的容器的副本，并对原始容器应用修改（参见条目30）。例如，对于字典，我可以复制键：

```
my_dict = {"red": 1, "blue": 2, "green": 3}

keys_copy = list(my_dict.keys())  # Copy
for key in keys_copy:             # Iterate over copy
    if key == "blue":
        my_dict["green"] = 4      # Modify original dict

print(my_dict)
>>>
{'red': 1, 'blue': 2, 'green': 4}
```

For lists I can copy the whole container:

对于列表，我可以复制整个容器：

```
my_list = [1, 2, 3]

list_copy = list(my_list)     # Copy
for number in list_copy:      # Iterate over copy
    print(number)
    if number == 2:
        my_list.insert(0, 4)  # Inserts in original list

print(my_list)
>>>
1
2
3
[4, 1, 2, 3]
```

And the same approach works for sets:

同样的方法适用于集合：

```
my_set = {"red", "blue", "green"}

set_copy = set(my_set)        # Copy
for color in set_copy:        # Iterate over copy
    if color == "blue":
        my_set.add("yellow")  # Add to original set

print(my_set)
>>>
{'yellow', 'green', 'blue', 'red'}
```

For some extremely large containers, copying might be too slow (see Item 92: “Profile Before Optimizing” to verify your assumptions). One way to deal with poor performance is to stage modifications in a separate container and then merge the changes into the main data structure after iteration. For example, here I modify a separate dictionary and then use the `update` method to bring the changes into the original dictionary:

对于一些非常大的容器，复制可能太慢（参见条目92）。一种解决性能问题的方法是在单独的容器中暂存修改，然后在迭代后将这些更改合并到主数据结构中。例如，这里我在修改一个单独的字典后使用`update`方法将更改带入原始字典：

```
my_dict = {"red": 1, "blue": 2, "green": 3}
modifications = {}

for key in my_dict:
    if key == "blue":
        modifications["green"] = 4  # Add to staging

my_dict.update(modifications)       # Merge modifications
print(my_dict)
>>>
{'red': 1, 'blue': 2, 'green': 4}
```

The problem with staging modifications is that they won’t be immediately visible in the original container during iteration. If the logic in the loop relies on modifications to be immediately visible, the code won’t work as expected. For example, here the programmer’s intent might have been to cause `"yellow"` to be in the resulting dictionary, but it won’t be there because the modifications aren’t visible during iteration:

暂存修改的问题在于，在迭代期间这些修改不会立即在原始容器中可见。如果循环中的逻辑依赖于立即可见的修改，则代码将无法按预期工作。例如，程序员的意图可能是使 "yellow" 出现在最终的字典中，但由于在迭代期间修改不可见，它不会出现在那里：

```
my_dict = {"red": 1, "blue": 2, "green": 3}
modifications = {}

for key in my_dict:
    if key == "blue":
        modifications["green"] = 4
    value = my_dict[key]
    if value == 4:                   # This condition is never true
        modifications["yellow"] = 5

my_dict.update(modifications)        # Merge modifications
print(my_dict)
>>>
{'red': 1, 'blue': 2, 'green': 4}
```

This code can be fixed by looking in both the original container ( `my_dict` ) and the modifications container ( `modifications` ) for the latest value during iteration, essentially treating the staging dictionary like an intermediate cache:

这个问题可以通过在迭代期间同时查找原始容器 (`my_dict`) 和修改容器 (`modifications`) 中的最新值来解决，本质上是将暂存字典视为中间缓存：

```
my_dict = {"red": 1, "blue": 2, "green": 3}
modifications = {}

for key in my_dict:
    if key == "blue":
        modifications["green"] = 4
    value = my_dict[key]
    other_value = modifications.get(key)  # Check cache
    if value == 4 or other_value == 4:
        modifications["yellow"] = 5

my_dict.update(modifications)             # Merge modifications
print(my_dict)
>>>
{'red': 1, 'blue': 2, 'green': 4, 'yellow': 5}
```

This type of reconciliation works, but it’s hard to generalize to all situations. When developing an algorithm like this, you’ll need to take your specific constraints into account. This can be quite difficult to get right, especially with all of the edge-cases, so I’d recommend writing automated tests Item 109: “Prefer Integration Tests Over Unit Tests”) to verify correctness. Similarly, you can use microbenchmarks to measure the performance of various approaches to pick the best one (see Item 93: “Optimize Performance-Critical Code Using timeit Microbenchmarks”).

这种类型的协调是可以工作的，但很难推广到所有情况。在开发这样的算法时，你需要考虑你的具体约束条件。这可能会相当困难，尤其是考虑到所有的边界情况，所以我建议编写自动化测试（参见条目109）来验证正确性。同样，你可以使用微基准测试来测量各种方法的性能，从而选择最佳方法（参见条目93）。

**Things to Remember**
- Adding or removing elements from lists, dictionaries, and sets while you’re iterating over them can cause errors at runtime that are often hard to predict.
- You can iterate over a copy of a container to avoid runtime errors that might be caused by mutation during iteration.
- If you need to avoid copying for better performance, you can stage modifications in a second container cache that you later merge into the original.

**注意事项**
- 在迭代列表、字典和集合时添加或删除元素可能导致运行时错误，这些错误通常难以预测。
- 为了避免在迭代期间因修改容器而导致的运行时错误，可以遍历容器的副本。
- 如果为了更好的性能需要避免复制，可以在第二个容器缓存中暂存修改，然后再将其合并到原始容器中。