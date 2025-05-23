# Chapter 10: Robustness (健壮性)

## Item 83: Always Make `try` Blocks as Short as Possible (始终使 `try` 块尽可能短)

When handling an expected exception, there’s quite a bit of overhead in getting all of the various statement blocks set up properly (see Item 80: “Take Advantage of Each Block in `try` / `except` / `else` / `finally` ”). For example, say that I want to make a remote procedure call (RPC) via a connection, which might encounter an error:

在处理预期的异常时，正确设置各种语句块会带来相当大的开销（参见条目80：“充分利用 `try` / `except` / `else` / `finally` 中的每个代码块”）。例如，我想要通过连接执行一个远程过程调用（RPC），这可能会遇到错误：

```
connection = ...
class RpcError(Exception):
    pass
def lookup_request(connection):
    raise RpcError("From lookup_request")
def close_connection(connection):
    print("Connection closed")
try:
    request = lookup_request(connection)
except RpcError:
    print("Encountered error!")
    close_connection(connection)

>>>
Error!
Connection closed
```

Later, imagine that I want to do more processing with the data gathered inside the `try` block, or handle special cases. The simplest and most natural way to do this is to add code right where it’s needed. Here, I change the example above to have a fast path that checks for cached responses in order to avoid extra processing:

之后，假设我想要在 `try` 块内部进行更多的数据处理，或者处理特殊情况。最简单和最自然的方法就是在需要的地方添加代码。在这里，我把上面的例子改写为快速路径检查缓存响应以避免额外的处理：

```
def lookup_request(connection):
    # No error raised
    return object()
def is_cached(connection, request):
    raise RpcError("From is_cached")
try:
    request = lookup_request(connection)
    if is_cached(connection, request):
        request = None
except RpcError:
    print("Encountered error!")
    close_connection(connection)

>>>
Connection closed
```

The problem is that the `is_cached` function might also raise an `RpcError` exception. By calling `lookup_request` and `is_cached` in the same `try` / `except` statement, later on in the code I can’t tell which of these functions actually raised the error and caused the connection to be closed:

问题在于 `is_cached` 函数也可能引发一个 `RpcError` 异常。通过将 `lookup_request` 和 `is_cached` 放在同一个 `try` / `except` 语句中，在以后的代码中我就无法分辨到底是哪一个函数引发了导致连接关闭的错误：

```
def is_closed(_):
    pass
if is_closed(connection):
    # Was the connection closed because of an error
    # in lookup_request or is_cached?
    pass
```

Instead, what you should do is put only one source of expected in errors in each `try` block. Everything else should either be in an associated `else` block or a separate subsequent `try` statement:

相反，你应该在一个 `try` 块中只包含一个预期的错误来源。其他一切内容应该放在关联的 `else` 块中，或者放在后续的另一个 `try` 语句中：

```
try:
    request = lookup_request(connection)
except RpcError:
    close_connection(connection)
else:
    if is_cached(connection, request):  # Moved
        request = None

>>>
Traceback ...
RpcError: From is_cached
```

This approach ensures that exceptions you did not expect, such as those potentially raised by `is_cached` , will bubble up through your call stack and produce an error message that you can find, debug, and fix later.

这种方法可以确保你未预料到的异常，如可能由 `is_cached` 抛出的异常，会通过你的调用栈向上冒泡，并生成你可以查找、调试和修复的错误消息。

**Things to Remember**

- Putting too much code inside of a `try` block can cause your program to catch exceptions you didn’t intend to handle.
- Instead expanding a `try` block, put additional code into the `else` block following the associated `except` block, or in a totally separate `try` statement.

**注意事项**

- 在 `try` 块中放入太多代码可能导致程序捕获到你不打算处理的异常。
- 不要扩展 `try` 块，而是将额外的代码放入关联的 `except` 块后面的 `else` 块中，或者完全放入另一个 `try` 语句中。