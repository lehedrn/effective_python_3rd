# Chapter 5: Functions (函数)

## Item 34: Reduce Visual Noise with Variable Positional Arguments (使用变量位置参数减少视觉噪声)


Accepting a variable number of positional arguments can make a function call clearer and reduce visual noise. These positional arguments are often called varargs for short, or star args, in reference to the conventional name for the parameter `*args` . For example, say that I want to log some debugging information. With a fixed number of arguments, I would need a function that takes a message and a `list` of values:

接受可变数量的位置参数可以使函数调用更加清晰并减少视觉噪声。这些位置参数通常简称为varargs，或 `*args`，是指以常规参数名`*args`来表示的参数。例如，假设我想记录一些调试信息。使用固定数量的参数时，我需要一个接收消息和一个值`list`的函数：

```
def log(message, values):
    if not values:
        print(message)
    else:
        values_str = ", ".join(str(x) for x in values)
        print(f"{message}: {values_str}")

log("My numbers are", [1, 2])
log("Hi there", [])
>>>
My numbers are: 1, 2
Hi there
```

Having to pass an empty `list` when I have no values to log is cumbersome and noisy. It’d be better to leave out the second argument entirely. I can do this in Python by prefixing the last positional parameter name with `*` . The first parameter for the log message is required, whereas any number of subsequent positional arguments are optional. The function body doesn’t need to change; only the callers do:

不得不在没有值要记录时传递一个空的`list`是繁琐且嘈杂的。最好能够完全省略第二个参数。在Python中，我可以通过在最后一个位置参数名前加上`*`来实现这一点。第一个用于日志消息的参数是必需的，而任何后续的位置参数都是可选的。函数体不需要改变；只有调用者需要改变：

```
def log(message, *values):   # Changed
    if not values:
        print(message)
    else:
        values_str = ", ".join(str(x) for x in values)
        print(f"{message}: {values_str}")

log("My numbers are", 1, 2)
log("Hi there")              # Changed

>>>
My numbers are: 1, 2
Hi there
```

This syntax works very similarly to the starred expressions used in unpacking assignment statements (see Item 16: “Prefer Catch-All Unpacking Over Slicing” and Item 9: “Consider match for Destructuring in Flow Control, Avoid When if Statements Are Sufficient” for more examples).

这种语法的工作方式与解包赋值语句中使用的星号表达式非常相似（参见第16条：“优先选择全打包而非切片” 和 第9条：“考虑在流程控制中使用match进行解构，在if语句足够时避免使用”了解更多示例）。

If I already have a sequence (like a `list` ) and I want to call a variadic function like `log` , I can do this by using the `*` operator. This instructs Python to pass items from the sequence as positional arguments to the function:

如果我已经有一个序列（如一个`list`），并且想要调用像`log`这样的可变参数函数，我可以使用`*`操作符来做到这一点。这会指示Python将序列中的项作为位置参数传递给函数：

```
favorites = [7, 33, 99]
log("Favorite colors",  *favorites)
>>>
Favorite colors: 7, 33, 99
```

There are two problems with accepting a variable number of positional arguments.

接受可变数量的位置参数存在两个问题。

The first issue is that these optional positional arguments are always turned into a `tuple` before they are passed to your function. This means that if the caller of your function uses the `*` operator on a generator, it will be iterated until it’s exhausted (see Item 43: “Consider Generators Instead of Returning Lists” for background). The resulting `tuple` includes every value from the generator, which could consume a lot of memory and cause the program to crash:

第一个问题是，这些可选的位置参数在传递给你的函数之前总是被转换成一个`tuple`。这意味着如果你的函数调用者在一个生成器上使用了`*`操作符，它将被迭代直到耗尽（参见第43条：“考虑使用生成器替代返回列表”了解背景）。生成的`tuple`包含生成器中的每个值，这可能会消耗大量内存并导致程序崩溃：

```
def my_generator():
    for i in range(10):
        yield i

def my_func(*args):
    print(args)

it = my_generator()
my_func(*it)

>>>
(0, 1, 2, 3, 4, 5, 6, 7, 8, 9)
```

Functions that accept `*args` are best for situations where you know the number of inputs in the argument list will be reasonably small. `*args` is ideal for function calls that pass many literals or variable names together. It’s primarily for the convenience of the programmer who calls the function and the readability of the calling code.

`*args`最适用于你确定参数列表中的输入数量将合理小的情况。`*args`非常适合于传递许多字面量或变量名一起的函数调用。它的主要目的是为了调用函数的程序员的便利性和调用代码的可读性。

The second issue with `*args` is that you can’t add new positional arguments to a function in the future without migrating every caller. If you try to add a positional argument in the front of the argument list, existing callers will subtly break if they aren’t updated. For example, here I add `sequence` as the first argument of the function and use it to render the log messages:

`*args`的第二个问题是，你不能在不迁移每个调用者的情况下将来向函数添加新的位置参数。如果你尝试在参数列表的前面添加一个位置参数，现有调用者如果不更新就会悄然中断。例如，这里我在函数中添加了`sequence`作为第一个参数，并使用它来渲染日志消息：

```
def log_seq(sequence, message, *values):
    if not values:
        print(f"{sequence} - {message}")
    else:
        values_str = ", ".join(str(x) for x in values)
        print(f"{sequence} - {message}: {values_str}")

log_seq(1, "Favorites", 7, 33)      # New with *args OK
log_seq(1, "Hi there")              # New message only OK
log_seq("Favorite numbers", 7, 33)  # Old usage breaks

>>>
1 - Favorites: 7, 33
1 - Hi there
Favorite numbers - 7: 33
```

The problem with the code above is that the third call to `log` used `7` as the `message` parameter because a `sequence` argument wasn’t provided. Bugs like this are hard to track down because the code still runs without raising any exceptions. To avoid this possibility entirely, you should use keyword-only arguments when you want to extend functions that accept `*args` (see Item 37: “Enforce Clarity with Keyword-Only and Positional￾Only Arguments”). To be even more defensive, you could also consider using type annotations (see Item 124: “Consider Static Analysis via typing to Obviate Bugs”).

上面代码的问题在于第三次对`log`的调用因为没有提供`sequence`参数，所以将`7`用作了`message`参数。这类错误很难追踪，因为代码仍然不会抛出任何异常地运行。为了避免这种可能性，当您想扩展接受`*args`的函数时，应使用关键字限定参数（参见第37条：“通过关键字限定和位置限定参数强制清晰度”）。为了更加谨慎，您还可以考虑使用类型注释（参见第124条：“考虑通过typing进行静态分析以消除错误”）。

**Things to Remember**
- Functions can accept a variable number of positional arguments by using `*args` in the `def` statement.
- You can use the items from a sequence as the positional arguments for a function with the `*` operator.
- Using the `*` operator with a generator may cause a program to run out of memory and crash.
- Adding new positional arguments to functions that accept `*args` can introduce hard-to-detect bugs.

**注意事项**
- 函数可以通过在`def`语句中使用`*args`接受可变数量的位置参数。
- 您可以使用`*`操作符将一个序列中的项作为函数的位置参数。
- 将`*`操作符与生成器一起使用可能会导致程序内存不足并崩溃。
- 向接受`*args`的函数添加新的位置参数可能会引入难以发现的错误。