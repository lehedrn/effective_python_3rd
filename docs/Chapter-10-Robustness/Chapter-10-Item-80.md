# Chapter 10: Robustness (健壮性)

## Item 80: Take Advantage of Each Block in `try`/ `except`/ `else`/ `finally` (利用 `try`/`except`/`else`/`finally` 中的每个代码块)

There are four distinct times when you might want to take action during exception handling in Python. These are captured in the functionality of `try` , `except` , `else` , and `finally` blocks. Each block serves a unique purpose in the compound statement, and their various combinations are useful (see Item 121: “Define a Root Exception to Insulate Callers from APIs” for another example).

在 Python 的异常处理中，你可能希望在四个不同的时刻采取行动。这些情况通过 `try`、`except`、`else` 和 `finally` 块的功能来捕获。每个块在复合语句中都有独特的用途，并且它们的各种组合都很有用（另一个例子请参见条目 121：“定义一个根异常以隔离调用者与 API”）。

### `finally` Blocks (`finally` 块)

Use `try` / `finally` when you want exceptions to propagate up, but you also want to run cleanup code even when exceptions occur. One common usage of `try` / `finally` is for reliably closing file handles (see Item 82: “Consider `contextlib` and `with` Statements for Reusable `try` / `finally` Behavior” for another—likely better—approach):

当你希望异常能够向上抛出，但同时也想运行清理代码时，请使用 `try` / `finally`。一个常见的 `try` / `finally` 用法是可靠地关闭文件句柄（有关另一种（可能是更好的）方法，请参见条目 82：“考虑使用 `contextlib` 和 `with` 语句以实现可重用的 `try` / `finally` 行为”）：

```
def try_finally_example(filename):
    print("* Opening file")
    handle = open(filename, encoding="utf-8")  # May raise OSError
    try:
        print("* Reading data")
        return handle.read()                   # May raise UnicodeDecodeError
    finally:
        print("* Calling close()")
        handle.close()                         # Always runs after try block
```

Any exception raised by the `read` method will always propagate up to the calling code, but the `close` method of `handle` in the `finally` block will run first:

`read` 方法引发的任何异常都将始终传播到调用代码，但在 `finally` 块中的 `handle` 的 `close` 方法将首先运行：

```
filename = "random_data.txt"
with open(filename, "wb") as f:
    f.write(b"\xf1\xf2\xf3\xf4\xf5")  # Invalid utf-8

data = try_finally_example(filename)

>>>
* Opening file
* Reading data
* Calling close()
Traceback (most recent call last):
  ...
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xf1 in position 0: invalid continuation byte
```

You must call `open` before the `try` block because exceptions that occur when opening the file (like `OSError` if the file does not exist) should skip the `finally` block entirely:

你必须在 `try` 块之前调用 `open`，因为打开文件时发生的错误（如文件不存在导致的 `OSError`）应该完全跳过 `finally` 块：

```
try_finally_example("does_not_exist.txt")

>>>
* Opening file
Traceback (most recent call last):
  ...
FileNotFoundError: [Errno 2] No such file or directory: 'does_not_exist.txt'
```

### `else` Blocks (`else` 块)

Use `try` / `except` / `else` to make it clear which exceptions will be handled by your code and which exceptions will propagate up. When the `try` block doesn’t raise an exception, the `else` block runs. The else block helps you minimize the amount of code in the `try` block, which is good for isolating potential exception causes and improves readability (see Item 83: “Always Make `try` Blocks as Short as Possible”). For example, say that I want to load JSON dictionary data from a string and return the value of a key it contains:

使用 `try` / `except` / `else` 可以明确你的代码将处理哪些异常以及哪些异常将被传播上去。当 `try` 块不引发异常时，将运行 `else` 块。`else` 块可以帮助你最小化 `try` 块中的代码量，这对于隔离潜在的异常原因和提高可读性是有益的（另请参见条目 83：“总是使 `try` 块尽可能短”）。例如，假设我想从字符串中加载 JSON 字典数据并返回其包含的某个键的值：

```
import json
def load_json_key(data, key):
    try:
        print("* Loading JSON data")
        result_dict = json.loads(data)  # May raise ValueError
    except ValueError:
        print("* Handling ValueError")
        raise KeyError(key)
    else:
        print("* Looking up key")
        return result_dict[key]         # May raise KeyError
```

In the successful case, the JSON data is decoded in the `try` block, and then the key lookup occurs in the `else` block:

在成功的情况下，JSON 数据将在 `try` 块中解码，然后在 `else` 块中进行键查找：

```
assert load_json_key('{"foo": "bar"}', "foo") == "bar"

>>>
* Loading JSON data
* Looking up key
```

If the input data isn’t valid JSON, then decoding with `json.loads` raises a `ValueError` . The exception is caught by the except block and handled:

如果输入的数据不是有效的 JSON，则使用 `json.loads` 解码会引发 `ValueError`。该异常将由 except 块捕获并处理：

```
load_json_key('{"foo": bad payload', "foo")

>>>
* Loading JSON data
* Handling ValueError
Traceback (most recent call last):
  ...
json.decoder.JSONDecodeError: Expecting value: line 1 column 9 (char 8)
During handling of the above exception, another exception occurred:
Traceback (most recent call last):
  ...
KeyError: 'foo'
```

If the key lookup raises any exceptions, they will propagate up to the caller because they are outside the `try` block. The `else` clause ensures that what follows the `try` / `except` is visually distinguished from the `except` block. This makes the exception propagation behavior clear:

如果键查找引发了任何异常，它们将传播到调用方，因为它们位于 `try` 块之外。`else` 子句确保紧跟 `try` / `except` 后的内容在视觉上区别于 `except` 块。这使得异常传播行为清晰可见：

```
load_json_key('{"foo": "bar"}', "does not exist")
>>>
* Loading JSON data
* Looking up key
Traceback ...
KeyError: 'does not exist'
```

### Everything Together (综合应用)

Use `try` / `except` / `else` / `finally` when you want to do it all in one compound statement. For example, say that I want to read a description of work to do from a file, process it, and then update the file in-place. Here, the `try` block is used to read the file and process it; the `except` block is used to handle exceptions from the `try` block that are expected; the `else` block is used to update the file in place and allow related exceptions to propagate up; and the `finally` block cleans up the file handle:

当你想在一个复合语句中完成所有操作时，请使用 `try` / `except` / `else` / `finally`。例如，假设我想要从文件中读取要做的工作的描述，处理它，然后就地更新文件。在这里，`try` 块用于读取文件并处理它；`except` 块用于处理来自 `try` 块的预期异常；`else` 块用于就地更新文件并允许相关异常传播；而 `finally` 块则用于清理文件句柄：

```
UNDEFINED = object()
DIE_IN_ELSE_BLOCK = False

def divide_json(path):
    print("* Opening file")
    handle = open(path, "r+")                        # May raise OSError
    try:
        print("* Reading data")
        data = handle.read()                         # May raise UnicodeDecodeError
        print("* Loading JSON data")
        op = json.loads(data)                        # May raise ValueError
        print("* Performing calculation")
        value = op["numerator"] / op["denominator"]  # May raise ZeroDivisionError
    except ZeroDivisionError:
        print("* Handling ZeroDivisionError")
        return UNDEFINED
    else:
        print("* Writing calculation")
        op["result"] = value
        result = json.dumps(op)
        handle.seek(0)                               # May raise OSError
        if DIE_IN_ELSE_BLOCK:
            import errno
            import os

            raise OSError(errno.ENOSPC, os.strerror(errno.ENOSPC))
        handle.write(result)                         # May raise OSError
        return value
    finally:
        print("* Calling close()")
        handle.close()                               # Always runs
```

In the successful case, the `try` , `else` , and `finally` blocks run.

在成功的情况下，将运行 `try`、`else` 和 `finally` 块。

```
temp_path = "random_data.json"
with open(temp_path, "w") as f:
    f.write('{"numerator": 1, "denominator": 10}')
assert divide_json(temp_path) == 0.1

>>>
>>>
* Opening file
* Reading data
* Loading JSON data
* Performing calculation
* Writing calculation
* Calling close()
```

If the calculation is invalid, then the `try` , `except` , and `finally` blocks run, but the `else` block does not:

如果计算无效，则将运行 `try`、`except` 和 `finally` 块，但不会运行 `else` 块：

```
with open(temp_path, "w") as f:
    f.write('{"numerator": 1, "denominator": 0}')
assert divide_json(temp_path) is UNDEFINED
>>>
* Opening file
* Reading data
* Loading JSON data
* Performing calculation
* Handling ZeroDivisionError
* Calling close()
```

If the JSON data was invalid, the `try` block runs and raises an exception, the `finally` block runs, and then the exception is propagated up to the caller. The `except` and `else` blocks do not run:

如果 JSON 数据无效，则 `try` 块将运行并引发异常，`finally` 块将运行，然后异常将传播到调用方。`except` 和 `else` 块不会运行：

```
with open(temp_path, "w") as f:
    f.write('{"numerator": 1 bad data')

divide_json(temp_path)

>>>
* Opening file
* Reading data
* Loading JSON data
* Calling close()
Traceback ...
JSONDecodeError: Expecting ',' delimiter: line 1 ...
```

This layout is especially useful because all of the blocks work together in intuitive ways. For example, here I simulate this by running the `divide_json` function at the same time that my hard drive runs out of disk space:

这种布局特别有用，因为所有的块都以直观的方式协同工作。例如，这里我通过在重新写入结果数据时模拟硬盘空间不足的情况来演示这一点：

```
with open(temp_path, "w") as f:
    f.write('{"numerator": 1, "denominator": 10}')
DIE_IN_ELSE_BLOCK = True
divide_json(temp_path)

>>>
* Opening file
* Reading data
* Loading JSON data
* Performing calculation
* Writing calculation
* Calling close()
Traceback ...
OSError: [Errno 28] No space left on device
```

When the exception was raised in the `else` block while rewriting the result data, the `finally` block still ran and closed the file handle as expected.

当在 `else` 块中重新编写结果数据时引发异常，仍然运行了 `finally` 块并按预期关闭了文件句柄。

**Things to Remember**

- The `try` / `finally` compound statement lets you run cleanup code regardless of whether exceptions were raised in the `try` block.
- The `else` block helps you minimize the amount of code in `try` blocks and visually distinguish the success case from the `try` / `except` blocks.
- An `else` block can be used to perform additional actions after a successful `try` block but before common cleanup in a `finally` block.

**注意事项**

- 使用 `try` / `finally` 复合语句可以不管是否在 `try` 块中引发异常都可以执行清理代码。
- `else` 块有助于减少 `try` 块中的代码量，并在视觉上区分成功情况与 `try` / `except` 块。
- `else` 块可用于在成功的 `try` 块之后但在通用清理的 `finally` 块之前执行额外的操作。