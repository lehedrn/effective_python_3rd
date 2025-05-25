# Chapter 12: Data Structures and Algorithms (数据结构与算法)

## Item 107: Make `pickle` Serialization Maintainable with `copyreg` (使用 `copyreg` 维护 `pickle` 序列化的可维护性)

The `pickle` built-in module can serialize Python objects into a stream of bytes and deserialize bytes back into objects (see Item 10: “Know the Differences Between `bytes` and `str` ” for background). Pickled byte streams shouldn’t be used to communicate between untrusted parties. The purpose of `pickle` is to let you pass Python objects between programs that you control over binary channels.

`pickle` 内置模块可以将 Python 对象序列化为字节流，并能将字节流反序列化回对象（背景信息请参见条目 10：“了解 `bytes` 和 `str` 的区别”）。不应使用 Pickled 字节流在不受信任的各方之间通信。`pickle` 的目的是让您通过您控制的二进制通道传递 Python 对象。

---

>Note
The `pickle` module’s serialization format is unsafe by design. The serialized data contains what is essentially a program that describes how to reconstruct the original Python objects. This means a malicious `pickle` payload could be used to compromise any part of the Python program that attempts to deserialize it. 
In contrast, the `json` module is safe by design. Serialized JSON data contains a simple description of an object hierarchy. Deserializing JSON data does not expose a Python program to any additional risk beyond out of memory errors. Formats like JSON should be used for communication between programs or people that don’t trust each other.

> 注意
`pickle` 模块的序列化格式设计上是不安全的。序列化的数据本质上包含了一个程序，描述了如何重建原始的 Python 对象。这意味着恶意的 `pickle` 负载可能被用来破坏任何尝试反序列化它的 Python 程序的任何部分。
相比之下，`json` 模块设计上是安全的。序列化的 JSON 数据仅包含一个对象层次结构的简单描述。反序列化 JSON 数据不会给 Python 程序带来除内存不足错误之外的任何额外风险。对于互不信任的程序或人之间的通信应使用像 JSON 这样的格式。
---

For example, say that I want to use a Python object to represent the state of a player’s progress in a game. The game state includes the level the player is on and the number of lives they have remaining:

例如，假设我想使用一个 Python 对象来表示玩家在游戏中进度的状态。游戏状态包括玩家所处的关卡和剩余的生命次数：

```
class GameState:
    def __init__(self):
        self.level = 0
        self.lives = 4
```

The program modifies this object as the game runs:

程序在游戏运行时修改此对象：

```
state = GameState()
state.level += 1  # Player beat a level
state.lives -= 1  # Player had to try again

print(state.__dict__)

>>>
{'level': 1, 'lives': 3}
```

When the user quits playing, the program can save the state of the game to a file so it can be resumed at a later time. The `pickle` module makes it easy to do this. Here, I `dump` the `GameState` object directly to a file:

当用户退出游戏时，程序可以将游戏的状态保存到文件中以便以后恢复。`pickle` 模块使这变得容易。在这里，我直接将 `GameState` 对象 `dump` 到一个文件中：

```
import pickle

state_path = "game_state.bin"
with open(state_path, "wb") as f:
    pickle.dump(state, f)
```

Later, I can `load` the file and get back the `GameState` object as if it had never been serialized:

之后，我可以从文件中 `load` 并获取原来的 `GameState` 对象，就像它从未被序列化一样：

```
with open(state_path, "rb") as f:
    state_after = pickle.load(f)
print(state_after.__dict__)
>>>
{'level': 1, 'lives': 3}
```

The problem with this approach is what happens as the game’s features expand over time. Imagine that I want the player to earn points towards a high score. To track the player’s points, I can add a new field to the `GameState` class:

这种方法的问题在于随着游戏功能的扩展会发生什么。想象一下，我希望玩家能够获得积分以取得高分。为了跟踪玩家的分数，我可以向 `GameState` 类添加一个新的字段：

```
class GameState:
    def __init__(self):
        self.level = 0
        self.lives = 4
        self.points = 0  # New field
```

Serializing the new version of the `GameState` class using `pickle` will work exactly as before. Here, I simulate the round-trip through a file by serializing to a string with `dumps` and back to a `GameState` object with `loads` :

使用 `pickle` 序列化新的 `GameState` 类将完全如前所述工作。在这里，我通过使用 `dumps` 序列化到字符串并通过 `loads` 反序列化回来模拟文件往返过程：

```
state = GameState()
serialized = pickle.dumps(state)
state_after = pickle.loads(serialized)
print(state_after.__dict__)
>>>
{'level': 0, 'lives': 4, 'points': 0}
```

But what happens to older saved `GameState` objects that the user may want to resume? Here, I unpickle an old game file using a program with the new definition of the `GameState` class:

但旧的已保存的 `GameState` 对象会发生什么呢？这里，我使用新定义的 `GameState` 类反解析一个旧的游戏文件：

```
with open(state_path, "rb") as f:
    state_after = pickle.load(f)
print(state_after.__dict__)
>>>
{'level': 1, 'lives': 3}
```

The `points` attribute is missing! This is especially confusing because the returned `object` is an instance of the new `GameState` class:

`points` 属性不见了！这尤其令人困惑，因为返回的对象是新 `GameState` 类的一个实例：

```
assert isinstance(state_after, GameState)
```

This behavior is a byproduct of the way the `pickle` module works. Its primary use case is making it easy to serialize objects. As soon as your use of `pickle` expands beyond trivial usage, the module’s functionality starts to break down in surprising ways.

这种行为是 `pickle` 模块工作方式的一个副作用。其主要用例是让对象序列化变得简单。一旦您的 `pickle` 使用超出了简单的用途，模块的功能开始以令人惊讶的方式失效。

Fixing these problems is straightforward using the `copyreg` built-in module. The `copyreg` module lets you register the functions responsible for serializing and deserializing Python objects, allowing you to control the behavior of `pickle` and make it more reliable and adaptable.

使用 `copyreg` 内置模块修复这些问题非常直接。`copyreg` 模块允许您注册负责序列化和反序列化 Python 对象的函数，从而允许您控制 `pickle` 的行为，使其更加可靠和适应性强。

### Default Attribute Values (默认属性值)

In the simplest case, you can use a constructor with default arguments (see Item 35: “Provide Optional Behavior with Keyword Arguments” for background) to ensure that `GameState` objects will always have all attributes after unpickling. Here, I redefine the constructor this way:

在最简单的情况下，您可以使用带有默认参数的构造函数（背景信息请参见条目 35：“使用关键字参数提供可选行为”）来确保 `GameState` 对象在反序列化后始终拥有所有属性。这里，我这样重新定义构造函数：

```
class GameState:
    def __init__(self, level=0, lives=4, points=0):
        self.level = level
        self.lives = lives
        self.points = points
```

To use this constructor for pickling, I define a helper function that takes a `GameState` object and turns it into a `tuple` of parameters for the `copyreg` module. The returned `tuple` contains the function to use for unpickling and the parameters to pass to the unpickling function:

为了使用这个构造函数进行 pickling，我定义了一个辅助函数，该函数接受一个 `GameState` 对象并将其转换为 `copyreg` 模块所需的参数元组。返回的元组包含用于 unpickling 的函数和要传递给 unpickling 函数的参数：

```
def pickle_game_state(game_state):
    kwargs = game_state.__dict__
    return unpickle_game_state, (kwargs,)
```

Now, I need to define the `unpickle_game_state` helper. This function takes serialized data and parameters from `pickle_game_state` and returns the corresponding `GameState`
object. It’s a tiny wrapper around the constructor:

现在，我需要定义 `unpickle_game_state` 辅助函数。这个函数接收序列化的数据和来自 `pickle_game_state` 的参数，并返回相应的 `GameState` 对象。它是构造函数的一个小包装器：

```
def unpickle_game_state(kwargs):
    return GameState(**kwargs)
```

Now, I register these functions with the `copyreg` built-in module:

现在，我将这些函数注册到 `copyreg` 内置模块中：

```
import copyreg
copyreg.pickle(GameState, pickle_game_state)
```

After registration, serializing and deserializing works as before:

注册后，序列化和反序列化的工作一如往常：

```
state = GameState()
state.points += 1000
serialized = pickle.dumps(state)
state_after = pickle.loads(serialized)
print(state_after.__dict__)
>>>
{'level': 0, 'lives': 4, 'points': 1000}
```

With this registration done, now I’ll change the definition of `GameState` again to give the player a count of magic spells to use. This change is similar to when I added the `points` field to `GameState` :

完成此注册后，我现在将再次更改 `GameState` 的定义，以给玩家计数魔法咒语的使用次数。这次更改类似于我在 `GameState` 中添加 `points` 字段时所做的更改：

```
class GameState:
    def __init__(self, level=0, lives=4, points=0, magic=5):
        self.level = level
        self.lives = lives
        self.points = points
        self.magic = magic  # New field
```

But unlike before, deserializing an old `GameState` object will result in valid game data instead of missing attributes. This works because `unpickle_game_state` calls the `GameState` constructor directly, instead of using the `pickle` module’s default behavior of saving and restoring only the attributes that belong to an `object` . The `GameState` constructor’s keyword arguments have default values that will be used for any parameters that are missing. This causes old game state files to receive the default value for the new `magic` field when they are deserialized:

但与之前不同的是，反序列化一个旧的 `GameState` 对象将导致有效的游戏数据而不是缺失属性。这是因为 `unpickle_game_state` 直接调用了 `GameState` 构造函数，而不是使用 `pickle` 模块的默认行为，即只保存和恢复属于对象的属性。`GameState` 构造函数的关键字参数具有默认值，将用于缺少的任何参数。这使得旧的游戏状态文件在反序列化时收到新 `magic` 字段的默认值：

```
print("Before:", state.__dict__)
state_after = pickle.loads(serialized)
print("After: ", state_after.__dict__)
>>>
Before: {'level': 0, 'lives': 4, 'points': 1000}
After: {'level': 0, 'lives': 4, 'points': 1000, magic:  5}
```

### Versioning Classes (版本化类)

Sometimes you need to make backward-incompatible changes to your Python objects by removing fields. Doing so prevents the default argument approach to migrating serializations from working.

有时，您需要通过对删除字段来进行向后不兼容的更改。这样做会阻止使用默认参数的方法迁移序列化。

For example, say I realize that a limited number of lives is a bad idea, and I want to remove the concept of lives from the game. Here, I redefine the `GameState` class to no longer have a lives field:

例如，假设我意识到有限数量的生命是个坏主意，我想从游戏中移除生命的概念。这里，我重新定义 `GameState` 类，不再有 lives 字段：

```
class GameState:
    def __init__(self, level=0, points=0, magic=5):
        self.level = level
        self.points = points
        self.magic = magic
```

The problem is that this breaks deserialization of old game data. All fields from the old data, even ones removed from the class, will be passed to the `GameState` constructor by the `unpickle_game_state` function:

问题是这会破坏旧游戏数据的反序列化。所有来自旧数据的字段，即使从类中删除了，也会由 `unpickle_game_state` 函数传递给 `GameState` 构造函数：

```
pickle.loads(serialized)
>>>
Traceback ...
TypeError: GameState.__init__() got an unexpected
argument 'lives'. Did you mean 'level'?
```

I can fix this by adding a version parameter to the functions supplied to `copyreg` . New serialized data will have a version of `2` specified when pickling a new `GameState` object:

我可以通过向提供给 `copyreg` 的函数添加版本参数来解决这个问题。新的序列化数据将在对新 `GameState` 对象进行 pickling 时指定版本为 `2`：

```
def pickle_game_state(game_state):
    kwargs = game_state.__dict__
    kwargs["version"] = 2
    return unpickle_game_state, (kwargs,)
```

Old versions of the data will not have a `version` argument present, which means I can manipulate the arguments passed to the `GameState` constructor accordingly:

旧版本的数据不会有 `version` 参数存在，这意味着我可以相应地操作传递给 `GameState` 构造函数的参数：

```
def unpickle_game_state(kwargs):
    version = kwargs.pop("version", 1)
    if version == 1:
        del kwargs["lives"]
    return GameState(**kwargs)
```

Now, deserializing an old object works properly:

现在，反序列化一个旧对象正常工作：

```
copyreg.pickle(GameState, pickle_game_state)
print("Before:", state.__dict__)
state_after = pickle.loads(serialized)
print("After: ", state_after.__dict__)
>>>
Before: {'level': 0, 'lives': 4, 'points': 1000}
After: {'level': 0, 'points': 1000, 'magic': 5}
```

I can continue using this approach to handle changes between future versions of the same class. Any logic I need to adapt an old version of the class to a new version of the class can go in the `unpickle_game_state` function.

我可以继续使用这种方法处理同一类未来版本之间的变化。任何需要将旧版本类适配到新版本类的逻辑都可以放在 `unpickle_game_state` 函数中。

### Stable Import Paths (稳定的导入路径)

One other issue you may encounter with `pickle` is breakage from renaming a class. Often over the life cycle of a program, you’ll refactor your code by renaming classes and moving them to other modules. Unfortunately, doing so breaks the `pickle` module unless you’re careful.

另一个您可能会遇到的与 `pickle` 相关的问题是从重命名一个类引起的 breakage。通常在一个程序的生命周期内，您会通过重命名类并将它们移动到其他模块来进行代码重构。不幸的是，除非您小心，否则这样做会破坏 `pickle` 模块。

Here, I rename the `GameState` class to `BetterGameState` and remove the old class from the program entirely:

在此，我将 `GameState` 类重命名为 `BetterGameState` 并从程序中完全删除旧类：

```
copyreg.dispatch_table.clear()
state = GameState()
serialized = pickle.dumps(state)
del GameState

class BetterGameState:
    def __init__(self, level=0, points=0, magic=5):
        self.level = level
        self.points = points
        self.magic = magic

```

Attempting to deserialize an old `GameState` object now fails because the class can’t be found:

尝试反序列化一个旧的 `GameState` 对象现在失败了，因为找不到类：

```
pickle.loads(serialized)
>>>
Traceback ...
AttributeError: Can't get attribute 'GameState' o
'__main__' from 'my_code.py'>
```

The cause of this exception is that the import path of the serialized object’s class is encoded in the pickled data.

此异常的原因是序列化对象的类的导入路径编码在了 pickled 数据中。

```
print(serialized)
>>>
b'\x80\x04\x95A\x00\x00\x00\x00\x00\x00\x00\x8c\x
8c\tGameState\x94\x93\x94)\x81\x94}\x94(\x8c\x05l
c\x06points\x94K\x00\x8c\x05magic\x94K\x05ub.'
```

The solution is to use `copyreg` again. I can specify a stable identifier for the function to use for unpickling an object. This allows me to transition pickled data to different classes with different names when it’s deserialized. It gives me a level of indirection:

解决方案是再次使用 `copyreg`。我可以指定一个稳定的标识符用于反序列化对象的函数。这允许我在反序列化时将 pickled 数据过渡到具有不同名称的不同类。这给了我一层间接：

```
copyreg.pickle(BetterGameState, pickle_game_state)
```

After I use `copyreg` , it’s evident that the import path to `unpickle_game_state` is encoded in the serialized data instead of `BetterGameState` :

在我使用 `copyreg` 后，很明显 `unpickle_game_state` 的导入路径代替 `BetterGameState` 编码在了序列化的数据中：

```
state = BetterGameState()
serialized = pickle.dumps(state)
print(serialized)
>>>
b'\x80\x04\x95W\x00\x00\x00\x00\x00\x00\x00\x8c\x
8c\x13unpickle_game_state\x94\x93\x94}\x94(\x8c\x
\x8c\x06points\x94K\x00\x8c\x05magic\x94K\x05\x8c
\x02u\x85\x94R\x94.'
```

The only gotcha is that I can’t change the path of the module in which the `unpickle_game_state` function is present. Once I serialize data with a function, it must remain available on that import path for deserialization in the future.

唯一的注意事项是我不能改变 `unpickle_game_state` 函数所在模块的路径。一旦我使用某个函数序列化数据，必须保持该函数在未来反序列化时可用在相同的导入路径上。

**Things to Remember**
- The `pickle` built-in module is useful only for serializing and deserializing objects between trusted programs.
- Deserializing previously pickled objects may break if the classes involved have changed over time (e.g., attributes have been added or removed).
- Use the `copyreg` built-in module with `pickle` to ensure backward compatibility for serialized objects.

**注意事项**
- `pickle` 内建模块仅在可信程序之间序列化和反序列化对象时有用。
- 如果涉及的类随时间发生了变化（例如，添加或删除了属性），反序列化先前的 pickled 对象可能会中断。
- 使用 `copyreg` 内建模块与 `pickle` 一起确保序列化对象的向后兼容性。