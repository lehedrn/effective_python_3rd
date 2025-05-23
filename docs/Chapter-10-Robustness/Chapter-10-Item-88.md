# Chapter 10: Robustness (健壮性)

## Item 88: Consider Explicitly Chaining Exceptions to Clarify Tracebacks (考虑显式链接异常以澄清回溯)

Python programs raise exceptions when they encounter errors or certain conditions in code (see Item 32: “Prefer Raising Exceptions to Returning `None` ”). For example, here I try to access a non-existent key in a dictionary, which results in an exception being raised:

当Python程序在代码中遇到错误或某些条件时会引发异常（参见条目32：“优先引发异常而不是返回`None`”）。例如，这里我尝试访问字典中的一个不存在的键，这会导致引发异常：

```
my_dict = {}
my_dict["does_not_exist"]
>>>
Traceback ...
KeyError: 'does_not_exist'
```


I can catch this exception and handle it using the `try` statement (see Item 80: “Take Advantage of Each Block in `try` / `except` / `else` / `finally` ”):

我可以使用`try`语句捕获此异常并进行处理（参见条目80：“充分利用`try` / `except` / `else` / `finally`中的每个块”）：

```
my_dict = {}
try:
    my_dict["does_not_exist"]
except KeyError:
    print("Could not find key!")
    
>>>
Could not find key!
```

If another exception is raised while I’m already handling one, the output looks quite different. For example, here I raise a newly-defined `MissingError` exception while handling the `KeyError` :

如果在处理一个异常时又引发了另一个异常，输出看起来会大不相同。例如，这里我在处理`KeyError`时引发了一个新定义的`MissingError`异常：

```
class MissingError(Exception):
    pass

try:
    my_dict["does_not_exist"]    # Raises first exception
except KeyError:
    raise MissingError("Oops!")  # Raises second exception
    
>>>
Traceback (most recent call last):
  ...
KeyError: 'does_not_exist'
During handling of the above exception, another exception occurred:
Traceback (most recent call last):
  ...
MissingError: Oops!    
```

The `MissingError` exception that’s raised in the `except` `KeyError` block is the one propagated up to the caller. However, in the stack trace printed by Python, you can also see that it included information about the exception that caused the initial problem: the `KeyError` raised by the `my_dict["does_not_exist"]` expression. This extra data is available because Python will automatically assign an exception’s `__context__` attribute to the exception instance being handled by the surrounding except block. Here is the same code as above, but I catch the `MissingError` exception and print its `__context__` attribute to show how the exceptions are chained together:

在`except KeyError`块中引发的`MissingError`异常是传播到调用者的那个异常。然而，在Python打印的堆栈跟踪中，您还可以看到它包含了导致初始问题的异常信息：由`my_dict["does_not_exist"]`表达式引发的`KeyError`。这些额外的数据可用，因为Python会自动将异常的`__context__`属性分配给正在被周围except块处理的异常实例。以下是与上面相同的代码，但我捕获了`MissingError`异常并打印其`__context__`属性，以展示异常是如何链接在一起的：

```
try:
    try:
        my_dict["does_not_exist"]
    except KeyError:
        raise MissingError("Oops!")
except MissingError as e:
    print("Second:", repr(e))
    print("First: ", repr(e.__context__))

>>>
Second: MissingError('Oops!')
First: KeyError('does_not_exist')
```

In complex code with many layers of error handling, it can be useful to control these chains of exceptions to make the error messages more clear. To accomplish this, Python allows for explicitly chaining exceptions together by using the `from` clause in the `raise` statement.

在具有多层错误处理的复杂代码中，控制这些异常链可能会很有用，以便使错误消息更清晰。为了实现这一点，Python允许通过在`raise`语句中使用`from`子句来显式地将异常链接在一起。

For example, say that I want to define a helper function that implements the same dictionary lookup behavior as above:

例如，假设我想定义一个辅助函数，实现与上述相同的字典查找行为：

```
def lookup(my_key):
    try:
        return my_dict[my_key]
    except KeyError:
        raise MissingError
```

Looking up a key that is present retrieves the value without a problem:

查找存在的键可以毫无问题地检索值：

```
my_dict["my key 1"] = 123
print(lookup("my key 1"))

>>>
123
```

When the given key is missing, a `MissingError` exception is raised as expected:

当给定的键缺失时，会按预期引发`MissingError`异常：

```
print(lookup("my key 2"))

>>>
Traceback ...
KeyError: 'my key 2'
The above exception was the direct cause of the f
exception:
Traceback ...
MissingError
```

Now, imagine that I want to augment the `lookup` function with the ability to contact a remote database server and populate the `my_dict` dictionary in the event that a key is missing. Here, I implement this behavior, assuming `contact_server` will do the database communication:

现在，想象一下我希望增强`lookup`函数的功能，使其在键缺失时能够联系远程数据库服务器并填充`my_dict`字典。在这里，我实现了这种行为，假设`contact_server`将执行数据库通信：

```
def contact_server(my_key):
    print(f"Looking up {my_key!r} in server")
    return "my value 2"

def lookup(my_key):
    try:
        return my_dict[my_key]
    except KeyError:
        result = contact_server(my_key)
        my_dict[my_key] = result  # Fill the local cache
        return result
```

Calling this function repeatedly, I can see that the server is only contacted on the first call when the key is not yet present in the `my_dict` cache. The subsequent call avoids calling `contact_server` and returns the value already present in `my_dict` :

重复调用此函数，可以看到服务器仅在首次调用且键尚未存在于`my_dict`缓存中时才被联系。后续调用则避免调用`contact_server`，并返回`my_dict`中已有的值：

```
print("Call 1")
print("Result:", lookup("my key 2"))
print("Call 2")
print("Result:", lookup("my key 2"))
>>>
Call 1
Looking up 'my key 2' in server
Result: my value 2
Call 2
Result: my value 2
```

Imagine that it’s possible for the database server not to have a requested record. In this situation, perhaps the `contact_server` function raises a new type of exception to indicate the condition:

想象一下，有可能数据库服务器没有请求的记录。在这种情况下，也许`contact_server`函数会引发一种新的异常来表示这种情况：

```
class ServerMissingKeyError(Exception):
    pass

def contact_server(my_key):
    print(f"Looking up {my_key!r} in server")
    raise ServerMissingKeyError
```

Now, when I try to look up a record that’s missing, I see a traceback that includes the `ServerMissingKeyError` exception and the original `KeyError` for the `my_dict` cache miss:

现在，当我尝试查找一个缺失的记录时，我会看到包含`ServerMissingKeyError`异常和原始`KeyError`对于`my_dict`缓存未命中的追溯信息：

```
print(lookup("my key 3"))
>>>
Looking up 'my key 3' in server
Traceback ...
KeyError: 'my key 3'
The above exception was the direct cause of the f
exception:
Traceback ...
ServerMissingKeyError
```

The problem is that the `lookup` function no longer adheres to the same abstract the details of the exception from the caller, I want a cache miss to always result in a `MissingError` , not a `ServerMissingKeyError` which might be defined in a separate module that I don’t control (see Item 121: “Define a Root `Exception` to Insulate Callers from APIs” for exception classes in APIs).

问题是`lookup`函数不再遵守同样的抽象，从调用者那里隐藏异常的细节，我希望缓存未命中总是导致`MissingError`，而不是可能在我不控制的单独模块中定义的`ServerMissingKeyError`（参见条目121：“定义根`Exception`以保护调用者免受API的影响”，了解API中的异常类）。

To fix this, I can wrap the call to `contact_server` in another `try` statement, catch the `ServerMissingKeyError` exception, and raise a `MissingError` instead (matching my desired API for `lookup` ):

为了解决这个问题，我可以将对`contact_server`的调用包装在另一个`try`语句中，捕获`ServerMissingKeyError`异常，并改为引发`MissingError`（匹配我为`lookup`设计的API）：

```
def lookup(my_key):
    try:
        return my_dict[my_key]
    except KeyError:
        try:
            result = contact_server(my_key)
        except ServerMissingKeyError:
            raise MissingError        # Convert the server error
        else:
            my_dict[my_key] = result  # Fill the local cache
            return result
```

Trying the new implementation of `lookup` , I can verify that the `MissingError` exception is what’s propagated up to callers:

尝试新的`lookup`实现，我可以验证`MissingError`异常是传播给调用者的：

```
print(lookup("my key 4"))
>>>
Looking up 'my key 4' in server
Traceback ...
KeyError: 'my key 4'
The above exception was the direct cause of the f
exception:
Traceback ...
ServerMissingKeyError
The above exception was the direct cause of the f
exception:
Traceback ...
MissingError
```

This chain of exceptions shows three different errors because of how the `except` clauses are nested in the `lookup` function. First, the `KeyError` exception is raised. Then while handling it, the `contact_server` function raises a `ServerMissingKeyError` , which is implicitly chained from the `KeyError` using the `__context__` attribute. The `ServerMissingKeyError` is then caught, and the `MissingError` is raised with the `__context__` attribute implicitly assigned to the `ServerMissingKeyError` currently being handled.

这个异常链显示了三个不同的错误，这是由于`lookup`函数中嵌套的`except`子句的结构造成的。首先，引发了`KeyError`异常。然后在处理它时，`contact_server`函数引发了`ServerMissingKeyError`，它使用`__context__`属性隐式地从`KeyError`链接而来。接着，捕获了`ServerMissingKeyError`，并通过将当前处理的`ServerMissingKeyError`赋值给`__context__`属性，显式地引发了`MissingError`。

A lot of information was printed for this `MissingError`——so much that it seems like it could be confusing to programmers trying to debug a real problem. One way to reduce the output is to use the `from` clause in the `raise` statement to explicitly indicate the source of an exception. Here, I hide the `ServerMissingKeyError` source error by having the exception handler explicitly chain the `MissingError` from the `KeyError` :

对于这个`MissingError`打印了很多信息——以至于它似乎会让试图调试真实问题的程序员感到困惑。减少输出的一种方法是使用`raise`语句中的`from`子句，明确指示异常的来源。在这里，我通过让异常处理程序从`KeyError`显式链接`MissingError`来隐藏`ServerMissingKeyError`源错误：

```
def lookup_explicit(my_key):
    try:
        return my_dict[my_key]
    except KeyError as e:              # Changed
        try:
            result = contact_server(my_key)
        except ServerMissingKeyError:
            raise MissingError from e  # Changed
        else:
            my_dict[my_key] = result
            return result
```

Calling the function again, I can confirm the `ServerMissingKeyError` is no longer printed:

再次调用该函数，我可以确认`ServerMissingKeyError`不再打印：

```
print(lookup_explicit("my key 5"))
>>>
Looking up 'my key 5' in server
Traceback ...
KeyError: 'my key 5'
The above exception was the direct cause of the f
exception:
Traceback ...
MissingError
```

Although in the exception output it appears that the `ServerMissingKeyError` is no longer associated with the `MissingError` exception, it is in fact still there assigned to the `__context__` attribute as before. The reason it’s not printed is because using the `from` e clause in the raise statement assigns the `raised` exception’s `__cause__` attribute to the `KeyError` and the `__suppress_context__` attribute to `True` . Here, I show the value of these attributes to clarify what Python uses to control printing unhandled exceptions:

尽管在异常输出中似乎`ServerMissingKeyError`不再与`MissingError`异常相关联，但实际上它仍然存在，只是被分配给了`__context__`属性。它之所以没有被打印，是因为在raise语句中使用`from` e 子句将引发的异常的`__cause__`属性分配给了`KeyError`，并将`__suppress_context__`属性设置为`True`。以下我展示了这些属性的值，以澄清Python用于控制未处理异常打印的内容：

```
try:
    lookup_explicit("my key 6")
except Exception as e:
    print("Exception:", repr(e))
    print("Context:  ", repr(e.__context__))
    print("Cause:    ", repr(e.__cause__))
    print("Suppress: ", repr(e.__suppress_context__))
>>>
Looking up 'my key 6' in server
Exception: MissingError()
Context: ServerMissingKeyError()
Cause: KeyError('my key 6')
Suppress: True
```

The exception chain traversal behavior that inspects `__cause__` and `__suppress_context__` is only present for Python’s built-in exception printer. If you use the `traceback` module to process `Exception` stack traces yourself (see Item 87: “Use `traceback` for Enhanced Exception Reporting”), you might notice that chained exception data seems to be missing:

检查`__cause__`和`__suppress_context__`的异常链遍历行为只存在于Python的内置异常打印机中。如果您自己使用`traceback`模块处理异常堆栈跟踪（参见条目87：“使用`traceback`进行增强的异常报告”），您可能会注意到链式异常数据似乎丢失了：

```
try:
    lookup("my key 7")
except Exception as e:
    stack = traceback.extract_tb(e.__traceback__)
    for frame in stack:
        print(frame.line)

>>>
Looking up 'my key 7' in server
lookup('my key 7')
raise MissingError # Convert the server er
```

In order to extract the same chained exception information that Python prints for unhandled exceptions, you’ll need to properly consider each exception’s `__cause__` and `__context__` attributes:

为了提取Python为未处理异常打印的相同链式异常信息，您需要正确考虑每个异常的`__cause__`和`__context__`属性：

```
def get_cause(exc):
    if exc.__cause__ is not None:
        return exc.__cause__
    elif not exc.__suppress_context__:
        return exc.__context__
    else:
        return None
```

The `get_cause` function can be applied in a loop or recursively to construct the full stack of chained exceptions:

可以循环或递归应用`get_cause`函数来构建完整的链式异常堆栈：

```
try:
    lookup("my key 8")
except Exception as e:
    while e is not None:
        stack = traceback.extract_tb(e.__traceback__)
        for i, frame in enumerate(stack, 1):
            print(i, frame.line)
        e = get_cause(e)
        if e:
            print("Caused by")

>>>
Looking up 'my key 8' in server
1 lookup('my key 8')
2 raise MissingError # Convert the server 
Caused by
1 result = contact_server(my_key)
2 raise ServerMissingKeyError
Caused by
1 return my_dict[my_key]
```

Another alternative way to shorten the `MissingError` exception chain is to suppress the `KeyError` source for the `ServerMissingKeyError` raised in `contact_server` . Here, I do this by using the `from None` clause in the corresponding `raise` statement:

另一种缩短`MissingError`异常链的替代方法是抑制`contact_server`中引发的`ServerMissingKeyError`的`KeyError`源。在这里，我通过在相应的`raise`语句中使用`from None`子句来实现这一点：

```
def contact_server(key):
    raise ServerMissingKeyError from None  # Suppress
```

Calling the `lookup` function again, I can confirm that the `KeyError` is no longer in Python’s default exception handling output:

再次调用`lookup`函数，我可以确认`KeyError`不再出现在Python的默认异常处理输出中：

```
print(lookup("my key 9"))
>>>
Traceback ...
ServerMissingKeyError
The above exception was the direct cause of the f
exception:
Traceback ...
MissingError
```


**Things to Remember**
- When an exception is raised from inside an `except` clause, the original exception for that handler will always be saved to the newly raised `Exception` value’s `__context__` attribute.
- The `from` clause in the `raise` statement lets you explicitly indicate——by setting the `__cause__` attribute——that a previously raised exception is the cause of a newly raised one.
- Explicitly chaining one exception from another will cause Python to only print the supplied cause (or lack thereof) instead of the automatically chained exception.

**注意事项**

- 当在`except`子句内部引发异常时，该处理器的原始异常将始终保存到新引发的`Exception`值的`__context__`属性中。
- `raise`语句中的`from`子句允许您显式地指示——通过设置`__cause__`属性——先前引发的异常是新引发的一个异常的原因。
- 显式地从一个异常链接到另一个异常将导致Python仅打印提供的原因（或无原因）而不是自动链接的异常。