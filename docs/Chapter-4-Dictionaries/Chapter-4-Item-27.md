# Chapter 4: Dictionaries (字典)

## Item 27: Prefer defaultdict over setdefault to Handle Missing Items in Internal State (对于内部状态中的缺失项，优先使用defaultdict而非setdefault)

When working with a dictionary that you didn’t create, there are a variety of ways to handle missing keys (see Item 26: “Prefer `get` Over in and `KeyError` to Handle Missing Dictionary Keys”). Although using the `get` method is a better approach than using `in` operators and
`KeyError` exceptions, for some use cases `setdefault` appears to be the shortest option.

当你使用一个你没有创建的字典时，有各种方式来处理丢失的键（参见条目26）。尽管使用`get`方法比使用`in`运算符和`KeyError`异常更好，但在某些用例中，`setdefault`似乎是最短的选项。

For example, say that I want to keep track of the cities I’ve visited in countries around the world. Here, I do this by using a dictionary that maps country names to a `set` instance containing corresponding city names:

例如，假设我想跟踪我在世界各地访问过的城市。在这里，我通过使用将国家名称映射到包含相应城市名称的`set`实例的字典来实现：

```
visits = {
  "Mexico": {"Tulum", "Puerto Vallarta"},
  "Japan": {"Hakone"},
}
```

I can use the `setdefault` method to add new cities to the sets, whether the country name is already present in the dictionary or not. The code is much shorter than achieving the same behavior with the `get` method and an assignment expression:

我可以使用`setdefault`方法将新城市添加到这些集合中，无论该国家名称是否已经存在于字典中。这段代码比使用`get`方法和赋值表达式实现的相同行为要短得多：

```
# Short
visits.setdefault("France", set()).add("Arles")
# Long
if (japan := visits.get("Japan")) is None:
    visits["Japan"] = japan = set()
japan.add("Kyoto")
print(visits)
>>>
{'Mexico': {'Puerto Vallarta', 'Tulum'}, 'Japan': {'Kyoto', 'Hakone'}, 'France': {'Arles'}}
```

What about the situation when you do control creation of the dictionary being accessed? This is generally the case when you’re using a dictionary instance to keep track of the internal state of an object, for example. Here, I wrap the example above in a class with helper methods to access its dynamic inner state that’s stored in a dictionary:

那么当你确实控制了被访问字典的创建时会怎样呢？通常情况下，当你使用字典实例来跟踪对象的内部状态时，就是这种情况。在这里，我将上面的例子封装在一个类中，并提供了辅助方法来访问其存储在字典中的动态内部状态：

```
class Visits:
    def __init__(self):
        self.data = {}
    def add(self, country, city):
        city_set = self.data.setdefault(country, set())
        city_set.add(city)
```

This new class hides the complexity of calling `setdefault` with the correct arguments, and it provides a nicer interface for the programmer:

这个新类隐藏了调用`setdefault`方法的复杂性，并为程序员提供了一个更友好的接口：

```
visits = Visits()
visits.add("Russia", "Yekaterinburg")
visits.add("Tanzania", "Zanzibar")
print(visits.data)
>>>
{'Russia': {'Yekaterinburg'}, 'Tanzania': {'Zanzibar'}}
```

However, the implementation of the `Visits.add` method isn’t ideal. The `setdefault` method is still confusingly named, which makes it more difficult for a new reader of the code to immediately understand what’s happening. And the implementation isn’t efficient because it constructs a new `set` instance on every call, regardless of whether the given country was already present in the `data` dictionary.

然而，`Visits.add`方法的实现并不理想。`setdefault`方法的命名仍然令人困惑，这使得新读者理解代码发生的事情更加困难。而且实现效率不高，因为它在每次调用时都会构造一个新的`set`实例，不管给定的国家是否已经存在于数据字典中。

Luckily, the defaultdict class from the collections built-in module simplifies this common use case by automatically storing a default
value when a key doesn’t exist. All you have to do is provide a function that will return the default value to use each time a key is missing (an example of Item 48: “Accept Functions Instead of Classes for Simple Interfaces”). Here, I rewrite the Visits class to use defaultdict :

幸运的是，`collections`内置模块中的`defaultdict`类通过在键不存在时自动存储默认值来简化这种常见用例。你要做的就是提供一个函数，该函数将在每次缺少键时返回默认值（参见条目48）。在这里，我重写了使用`defaultdict`的`Visits`类：

```
from collections import defaultdict
class Visits:
    def __init__(self):
        self.data = defaultdict(set)
    def add(self, country, city):
        self.data[country].add(city)
visits = Visits()
visits.add("England", "Bath")
visits.add("England", "London")
print(visits.data)
>>>
defaultdict(<class 'set'>, {'England': {'Bath', 'London'}})
``` 

Now, the implementation of `add` is short and simple. The code can assume that accessing any key in the `data` dictionary will always result in an existing `set` instance. No superfluous `set` instances will be allocated, which could be costly if the `add` method is called a large number of times.

现在，`add`的实现很简短且简单。代码可以假定访问data字典中的任何键都将始终导致现有的`set`实例。不会分配多余的`set`实例，如果调用大量次`add`方法，这可能会很昂贵。

Using `defaultdict` is much better than using `setdefault` for this type of situation (see Item 29: “Compose Classes Instead of Deeply Nesting Dictionaries, Lists, and Tuples” for another example). There are still cases in which `defaultdict` will fall short of solving your problems, but there are even more tools available in Python to work around those limitations (see Item 28: “Know How to Construct Key-Dependent Default Values with `__missing__` ”, Item 57: “Inherit from `collections.abc` for Custom Container Types”, and the `collections.Counter` built-in class).

在这种类型的情况下，使用`defaultdict`比使用`setdefault`要好得多（参见条目29）。仍有某些情况下`defaultdict`无法解决你的问题，但Python中有更多工具可以绕过这些限制（参见条目28，条目57）。

**Things to Remember**

- If you’re creating a dictionary to manage an arbitrary set of potential keys, then you should prefer using a `defaultdict` instance from the
`collections` built-in module if it suits your problem.
- If a dictionary of arbitrary keys is passed to you, and you don’t control its creation, then you should prefer the `get` method to access its items. However, it’s worth considering using the `setdefault` method for the few situations in which it leads to shorter code and the default object allocation cost is low.

**注意事项**

- 如果你在创建一个字典来管理一组任意的潜在键，那么如果你的问题适合，应该优先使用来自`collections`内置模块的`defaultdict`实例。
- 如果有一个任意键的字典传递给了你，而你不能控制它的创建，那么你应该优先使用get方法来访问其项目。但是，在少数几种情况下，使用setdefault方法会导致较短的代码且默认对象分配成本较低，这时值得考虑使用它。