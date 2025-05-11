# Chapter 2: Strings and Slicing (字符串和切片操作)

## Item 10: Know the Differences Between bytes and str (了解 bytes 和 str 的区别)

In Python, there are two types that represent sequences of character data: bytes and str . 

在 Python 中，有两种类型可以表示字符数据序列：bytes 和 str。

Instances of bytes contain raw, unsigned 8-bit values (often displayed in the ASCII encoding):

bytes 的实例包含原始的、无符号的 8 位值（通常以 ASCII 编码显示）：

```
a = b"h\x65llo"
print(type(a))
print(list(a))
print(a)
>>>
<class 'bytes'>
[104, 101, 108, 108, 111]
b'hello'
```

Instances of str contain Unicode code points that represent textual characters from human languages:

str 的实例包含代表人类语言中字符的 Unicode 码点：

```
a = "a\u0300 propos"
print(type(a))
print(list(a))
print(a)
>>>
<class 'str'>
['a', '̀', ' ', 'p', 'r', 'o', 'p', 'o', 's']
à propos
```

Importantly, str instances do not have an associated binary encoding, and bytes instances do not have an associated text encoding. To convert Unicode data to binary data, you must call the encode method of str . To convert binary data to Unicode data, you must call the decode method of bytes . You can explicitly specify the encoding you want to use for these methods, or accept the system default, which is commonly UTF-8 (but not always—see more on that below).

重要的是，str 实例没有关联的二进制编码，而 bytes 实例也没有关联的文本编码。要将 Unicode 数据转换为二进制数据，必须调用 str.encode() 方法；要将二进制数据转换为 Unicode 数据，则必须调用 bytes.decode() 方法。你可以显式指定这些方法使用的编码，或者使用系统默认编码（通常是 UTF-8，但不总是如此）。

When you’re writing Python programs, it’s important to do encoding and decoding of Unicode data at the furthest boundary of your interfaces; this approach is often called the Unicode sandwich. The core of your program should use the str type containing Unicode data and should not assume anything about character encodings. This setup allows you to be very accepting of alternative text encodings (such as Latin-1, Shift JIS, and Big5) while being strict about your output text encoding (ideally, UTF-8).

当你编写 Python 程序时，应该在接口边界处进行 Unicode 的编码和解码操作。这种方法被称为 Unicode sandwich（Unicode 三明治）。程序的核心应使用包含 Unicode 数据的 str 类型，并且不应假设任何字符编码。这种方式使你的程序能够接受多种替代文本编码（如 Latin-1、Shift JIS 和 Big5），同时对输出文本编码保持严格要求（理想情况下是 UTF-8）。

The split between character data types leads to two common situations in Python code:

str 和 bytes 的区分会导致 Python 代码中出现两种常见情况：

- You want to operate on raw 8-bit sequences that contain UTF-8-encoded strings (or some other encoding).
- You want to operate on Unicode strings that have no specific encoding.

- 你想操作包含 UTF-8 编码字符串（或其他编码）的原始 8 位字节序列；
- 你想操作没有特定编码的 Unicode 字符串。

You’ll often need two helper functions to convert between these cases and to ensure that the type of input values matches your code’s expectations.

你经常需要两个辅助函数来在这两种情况之间转换，并确保输入值的类型符合代码预期。

The first function takes a bytes or str instance and always returns a str :

第一个函数接收 bytes 或 str 实例，并始终返回 str：

```
def to_str(bytes_or_str):
 if isinstance(bytes_or_str, bytes):
 value = bytes_or_str.decode("utf-8")
 else:
 value = bytes_or_str
 return value # Instance of str
print(repr(to_str(b"foo")))
print(repr(to_str("bar")))
>>>
'foo'
'bar'
```

The second function takes a bytes or str instance and always returns a bytes :

第二个函数接收 bytes 或 str 实例，并始终返回 bytes：

```
def to_bytes(bytes_or_str):
 if isinstance(bytes_or_str, str):
 value = bytes_or_str.encode("utf-8")
 else:
 value = bytes_or_str
 return value # Instance of bytes
print(repr(to_bytes(b"foo")))
print(repr(to_bytes("bar")))
```

There are two big gotchas when dealing with raw 8-bit values and Unicode strings in Python.

在处理原始 8 位值和 Unicode 字符串时，有两个常见的陷阱需要注意。

The first issue is that bytes and str seem to work the same way, but their instances are not compatible with each other, so you must be deliberate about the types of character sequences that you’re passing around.By using the + operator, you can add bytes to bytes and str to str , respectively:

第一个问题是，虽然 bytes 和 str 在某些方面表现相似，但它们的实例并不兼容。因此你必须明确地处理字符序列的类型。例如，使用 + 操作符时，只能拼接 bytes 和 bytes，或 str 和 str：

```
print(b"one" + b"two")
print("one" + "two")
>>>
b'onetwo'
onetwo
```

But you can’t add str instances to bytes instances:

但不能将 bytes 实例与 str 实例拼接：

```
b"one" + "two"
>>>
Traceback ...
TypeError: can't concat str to bytes
```

Nor can you add bytes instances to str instances:

也不能将 str 实例与 bytes 实例拼接：

```
"one" + b"two"
>>>
Traceback ...
TypeError: can only concatenate str (not "bytes")
```

By using binary operators, you can compare bytes to bytes and str to str , respectively:

通过使用比较运算符，你可以分别对 `bytes` 与 `bytes`、`str` 与 `str` 进行比较：

```
assert b"red" > b"blue"
assert "red" > "blue"
```

But you can’t compare a str instance to a bytes instance:

但你不能将 `str` 实例与 `bytes` 实例进行比较：

```
assert "red" > b"blue"
>>>
Traceback ...
TypeError: '>' not supported between instances of 'str' and 'bytes'
```

Nor can you compare a bytes instance to a str instance.

同样，你也不能将 `bytes` 实例与 `str` 实例进行比较：

```
assert b"blue" < "red"
>>>
Traceback ...
TypeError: '<' not supported between instances of 'bytes' and 'str'
```

Comparing bytes and str instances for equality will always evaluate to False , even when they contain exactly the same characters (in this case, ASCII-encoded “foo”):

比较 `bytes` 和 `str` 实例是否相等时，结果总是 `False`，即使它们包含完全相同的字符（例如此处为 ASCII 编码的 "foo"）：

```
print(b"foo" == "foo")
>>>
False
```

The % operator works with format strings for each type, respectively (see Item 11: “Prefer Interpolated F-Strings Over C-style Format Strings and str.format ” for background):

`%` 运算符可以分别对每种类型使用对应的格式化字符串进行操作：

```
blue_bytes = b"blue"
blue_str = "blue"
print(b"red %s" % blue_bytes)
print("red %s" % blue_str)
>>>
b'red blue'
red blue
```

But you can’t pass a str instance to a bytes format string because Python doesn’t know what binary text encoding to use:

但你不能将 `str` 实例传递给 `bytes` 的格式化字符串，因为 Python 不知道应该使用哪种二进制文本编码：

```
print(b"red %s" % blue_str)
>>>
Traceback ...
TypeError: %b requires a bytes-like object, or an object that implements __bytes__, not 'str'
```

However, you can pass a bytes instance to a str format string using the % operator, or use a bytes instance in an interpolated format string, but it doesn’t do what you’d expect:

虽然，你可以通过 `%` 运算符将 `bytes` 实例传递给 `str` 的格式化字符串，但它的行为并不如你所预期：

```
print("red %s" % blue_bytes)
print(f"red {blue_bytes}")
>>>
red b'blue'
red b'blue'
```

In these cases, the code actually invokes the __repr__ special method (see Item 12: “Understand the Difference Between repr and str When Printing Objects”) on the bytes instance and substitutes that in place of %s or {blue_bytes} , which is why the b'blue' literal appears in the output.

这段代码实际上在 `bytes` 实例上调用了 `__repr__` 方法（参见第 12 条），并用该方法的返回值替换 `%s`，这就是为什么输出中会保留 `b'blue'` 的转义形式。

The second gotcha is that operations involving file handles (returned by the open built-in function) default to requiring Unicode strings instead of raw bytes . This can cause surprising failures, especially for programmers accustomed to Python 2. For example, say that I want to write some binary data to a file. This seemingly simple code breaks:

第二个问题是：涉及文件句柄（由内置函数 `open` 返回）的操作默认要求使用 Unicode 字符串而非原始字节。尤其是对于习惯使用 Python 2 的程序员而言，这可能会导致一些令人意外的失败。例如，假设我想要向文件中写入一些二进制数据，这段看似简单的代码却会出错：

```
with open("data.bin", "w") as f:
  f.write(b"\xf1\xf2\xf3\xf4\xf5")
>>>
Traceback ...
TypeError: write() argument must be str, not byte
```

The cause of the exception is that the file was opened in write text mode ( "w" ) instead of write binary mode ( "wb" ). When a file is in text mode, write operations expect str instances containing Unicode data instead of bytes instances containing binary data. Here, I fix this by changing the open mode to "wb" :

原因是文件是以文本模式（"w"）打开的，而非二进制模式（"wb"）。当文件处于文本模式时，write() 操作期望的是包含 Unicode 数据的 str，而不是包含二进制数据的 bytes。解决办法是改为使用 "wb" 模式：

```
with open("data.bin", "wb") as f:
  f.write(b"\xf1\xf2\xf3\xf4\xf5")
```

A similar problem also exists for reading data from files. For example, here I try to read the binary file that was written above:

读取文件时也会遇到类似问题。例如，这里我尝试读取前面写入的二进制文件：

```
with open("data.bin", "r") as f:
  data = f.read()
>>>
Traceback ...
UnicodeDecodeError: 'gbk' codec can't decode byte 0xf5 in position 4: incomplete multibyte sequence
```

This fails because the file was opened in read text mode ( "r" ) instead of read binary mode ( "rb" ). When a handle is in text mode, it uses the system’s default text encoding to interpret binary data using the bytes.decode (for reading) and str.encode (for writing) methods. On most systems, the default encoding is UTF-8, which can’t accept the binary data b"\xf1\xf2\xf3\xf4\xf5" , thus causing the error above. Here, I solve this problem by changing the open mode to "rb" :

这个错误的原因是文件以读文本模式（`'r'`）打开，而不是读二进制模式（`'rb'`）。当文件句柄处于文本模式时，它会使用系统默认的文本编码来解释二进制数据，通过 `bytes.encode`（用于写入）和 `str.decode`（用于读取）方法。在大多数系统上，默认的编码方式是 UTF-8，它无法解析这段二进制数据 `b'\xf1\xf2\xf3\xf4\xf5'`，从而导致了上述错误。在这里，我通过将打开文件的模式改为 `'rb'` 来解决这个问题：

```
with open("data.bin", "rb") as f:
  data = f.read()
assert data == b"\xf1\xf2\xf3\xf4\xf5"
```

Alternatively, I can explicitly specify the encoding parameter to the open function to make sure that I’m not surprised by any platform￾specific behavior. For example, here I assume that the binary data in the file was actually meant to be a string encoded as 'cp1252' (a legacy Windows encoding):

或者，也可以显式地向 `open` 函数传入 `encoding` 参数，以确保不会因平台相关的特性而产生意外行为。例如，这里我假设文件中的二进制数据实际上是采用 `'cp1252'` 编码的字符串（一种遗留的 Windows 编码方式）：

```
with open("data.bin", "r", encoding="cp1252") as
  data = f.read()
assert data == "ñòóôõ"
```

The exception is gone, and the string interpretation of the file’s contents is very different from what was returned when reading raw bytes. The lesson here is that you should check the default encoding on your system (using python3 -c 'import locale; print(locale.getpreferredencoding())' ) to understand how it differs from your expectations. When in doubt, you should explicitly pass the encoding parameter to open .

异常消失了，文件内容的字符串解释与读取原始字节时返回的结果大相径。这里的经验是：你应该检查系统默认的编码方式（通过命令 `python3 -c 'import locale; print(locale.getpreferredencoding())'`），以理解它与你的预期有何不同。当你不确定时，应显式向 `open` 函数传递 `encoding` 参数。

**Things to Remember**

- bytes contains sequences of 8-bit values, and str contains sequences of Unicode code points.
- Use helper functions to ensure that the inputs you operate on are the type of character sequence that you expect (8-bit values, UTF-8-encoded strings,
Unicode code points, etc).
- bytes and str instances can’t be used together with operators (like > , == , + , and % ).
- If you want to read or write binary data to/from a file, always open the file using a binary mode (like "rb" or "wb" ).
- If you want to read or write Unicode data to/from a file, be careful about your system’s default text encoding. Explicitly pass the encoding parameter to open to avoid surprises.

**注意事项**
- `bytes` 包含 8 位值的序列，而 `str` 包含 Unicode 码点的序列。
- 使用辅助函数来确保你操作的输入是你所期望的字符序列类型（如 8 位值、UTF-8 编码的字符串、Unicode 码点等）。
- `bytes` 和 `str` 实例不能混合使用运算符（如 `>`, `==`, `+`, `%`）。
- 如果你想从文件中读写二进制数据，请始终使用二进制模式打开文件（如 `'rb'` 或 `'wb'`）。
- 如果你想从文件中读写 Unicode 数据，请注意系统的默认文本编码。如果你希望避免意外行为，建议显式传递 encoding 参数给 open() 函数以避免意外行为。