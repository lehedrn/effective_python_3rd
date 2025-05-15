# Chapter 4: Dictionaries (字典)

## Item 28: Know How to Construct Key-Dependent Default Values with `__missing__` (了解如何使用 `__missing__` 构造依赖键的默认值)

The built-in `dict` type’s `setdefault` method results in shorter code when handling missing keys in some specific circumstances (see Item 26: “Prefer `get` Over `in` and `KeyError` to Handle Missing Dictionary Keys”). For many of those situations, the better tool for the job is the `defaultdict` type from the `collections` built-in module (see Item 27: “Prefer `defaultdict` Over `setdefault` to Handle Missing Items in Internal State” for why). However, there are times when neither `setdefault` nor `defaultdict` is the right fit.

内置的 `dict` 类型的 `setdefault` 方法在某些特定情况下处理缺失键时会使代码更简洁（参见条目26）。在这些情况中的许多场景下，更好的选择是使用来自 `collections` 内置模块的 `defaultdict` 类型（参见条目27）。然而，有时 `setdefault` 和 `defaultdict` 都不适合。

For example, say that I’m writing a program to manage social network profile pictures on the filesystem. I need a dictionary to map profile picture pathnames to open file handles so I can read and write those images as needed. Here, I do this by using a normal `dict` instance and checking for the presence of keys using the `get` method and an assignment expression (see Item 8: “Prevent Repetition with Assignment Expressions”):

例如，假设我正在编写一个程序来管理文件系统上的社交网络头像图片。我需要一个字典将头像路径名映射到打开的文件句柄，以便按需读写这些图像。这里，我通过使用普通的 `dict` 实例并通过 `get` 方法和赋值表达式检查键的存在性来实现这一点（参见条目8）：

```
pictures = {}
path = "profile_1234.png"

with open(path, "wb") as f:
    f.write(b"image data here 1234")

if (handle := pictures.get(path)) is None:
    try:
        handle = open(path, "a+b")
    except OSError:
        print(f"Failed to open path {path}")
        raise
    else:
        pictures[path] = handle

handle.seek(0)
image_data = handle.read()
```

When the file handle already exists in the dictionary, this code makes only a single dictionary access. In the case that the file handle doesn’t exist, the dictionary is accessed once by `get` , and then it is assigned in the `else` clause of the `try / except` statement (see Item 80: “Take Advantage of Each Block in `try / except / else / finally` ”). The call to the `read` method stands clearly separate from the code that calls `open` and handles exceptions.

当文件句柄已经存在于字典中时，此代码仅进行一次字典访问。如果该文件句柄不存在，则字典由 `get` 访问一次，并在 `try / except` 语句的 `else` 子句中分配（参见条目80）。调用 `read` 方法显然与调用 `open` 并处理异常的代码分离开了。

Although it’s possible to use the `in` operator or `KeyError` approaches to implement this same logic, those options require more dictionary accesses and levels of nesting. Given that these other options work, you might also assume that the `setdefault` method would work, too:

虽然可以使用 `in` 运算符或 `KeyError` 方法实现相同的逻辑，但这些选项需要更多的字典访问和嵌套层次。鉴于其他选项有效，您可能也认为 `setdefault` 方法也可以工作：

```
try:
    handle = pictures.setdefault(path, open(path,  open(path, "a+b"))
except OSError:
     print(f"Failed to open path {path}")
     raise
else:
     handle.seek(0)
     image_data = handle.read()
```

This code has many problems. The `open` built-in function to create the file handle is always called, even when the path is already present in the dictionary. This results in an additional file handle that might conflict with existing open handles in the same program. Exceptions might be raised by the `open` call and need to be handled, but it may not be possible to differentiate them from exceptions that could be raised by the `setdefault` call on the same line (which is possible for other dictionary-like implementations; see Item 57: “Inherit from collections.abc for Custom Container Types”).

这段代码有很多问题。创建文件句柄的 `open` 内建函数总是被调用，即使路径已经存在于字典中。这会导致额外的文件句柄，可能与程序中已有的打开句柄冲突。`open` 调用可能会引发异常需要处理，但可能无法将其与同一行上对 `setdefault` 的调用可能引发的异常区分开来（对于其他类似字典的实现来说这是可能的；参见条目57）。

If you’re trying to manage internal state, another assumption you might make is that a `defaultdict` could be used for keeping track of these profile pictures. Here, I attempt to implement the same logic as before but now using a helper function and the `defaultdict` class:

如果您尝试管理内部状态，另一个您可能做出的假设是，可以使用 `defaultdict` 来跟踪这些头像图片。在这里，我尝试实现同样的逻辑，但现在使用了一个辅助函数和 `defaultdict` 类：

```
from collections import defaultdict
def open_picture(profile_path):
    try:
        return open(profile_path, "a+b")
    except OSError:
        print(f"Failed to open path {profile_path}")
        raise
    
pictures = defaultdict(open_picture)
handle = pictures[path]
handle.seek(0)
image_data = handle.read()
>>>
Traceback ...
TypeError: open_picture() missing 1 required posi
'profile_path'
```

The problem is that `defaultdict` expects that the function passed to its constructor doesn’t require any arguments. This means that the helper function `defaultdict` calls doesn’t know the specific `key` that’s being accessed, which hinders my ability to call open . In this situation, both `setdefault` and `defaultdict` fall short of what I need.

问题是 `defaultdict` 期望传递给其构造函数的函数不带任何参数。这意味着 `defaultdict` 调用的辅助函数不知道具体正在访问哪个键，这就阻碍了我调用 `open` 的能力。在这种情况下，`setdefault` 和 `defaultdict` 都达不到我的需求。

Fortunately, this situation is common enough that Python has another built-in solution. You can subclass the `dict` type and implement the `__missing__` special method to add custom logic for handling missing keys. Here, I do this by defining a new class that takes advantage of the same `open_picture` helper method defined above:

幸运的是，这种情况足够常见，Python 提供了另一种内置解决方案。您可以子类化 `dict` 类型并实现 `__missing__` 特殊方法，以添加用于处理缺失键的自定义逻辑。在这里，我通过定义一个新类来利用上面定义的相同 `open_picture` 辅助方法来实现这一点：

```
class Pictures(dict):
    def __missing__(self, key):
        value = open_picture(key)
        self[key] = value
        return value
pictures = Pictures()
handle = pictures[path]
handle.seek(0)
image_data = handle.read()
```

When the `pictures[path]` dictionary access finds that the `path` key isn’t present in the dictionary, the `__missing__` method is called. This method must create the new default value for the key, insert it into the dictionary, and return it to the caller. Subsequent accesses of the same path will not call `__missing__` since the corresponding item is already present (similar to the behavior of `__getattr__` ; see Item 61: “Use` __getattr__` , `__getattribute__` , and `__setattr__` for Lazy Attributes”).

当 `pictures[path]` 字典访问发现 `path` 键不在字典中时，会调用 `__missing__` 方法。此方法必须为该键创建新的默认值，将其插入字典中，并将其返回给调用者。之后对该路径的相同访问不会调用 `__missing__`，因为相应的项已经存在（类似于 `__getattr__` 的行为；参见条目61）。

**Things to Remember**
- The `setdefault` method of `dict` is a bad fit when creating the default value has high computational cost or might raise exceptions.
- The function passed to `defaultdict` must not require any arguments, which makes it impossible to have the default value depend on the key being accessed.
- You can define your own `dict` subclass with a `__missing__` method in order to construct default values that must know which key was being accessed.

**注意事项**
- 当创建默认值具有高计算成本或可能引发异常时，`dict` 的 `setdefault` 方法并不适合。
- 传递给 `defaultdict` 的函数不能有任何参数，这使得默认值不可能依赖于被访问的键。
- 您可以定义自己的 `dict` 子类并带有 `__missing__` 方法，以便构建必须知道被访问键的默认值。