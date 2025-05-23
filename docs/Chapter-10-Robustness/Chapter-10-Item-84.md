# Chapter 10: Robustness (健壮性)

## Item 84: Beware of Exception Variables Disappearing (警惕异常变量消失的问题)

Unlike `for` loop variables (see Item 20: “Never Use `for` Loop Variables After the Loop Ends”), exception variables are not accessible on the line following an `except` block:

与`for`循环变量不同（参见条目20：“永远不要在`for`循环结束后使用循环变量”），异常变量在`except`块之后的下一行是不可访问的：

```
try:
    raise MyError(123)
except MyError as e:
    print(f"Inside {e=}")
print(f"Outside {e=}") # Raises

>>>
Inside e=MyError(123)
Traceback ...
NameError: name 'e' is not defined
```

You might assume that the exception variable will still exist within scope of the `finally` block that is part of the exception handling machinery (see Item 80: “Take Advantage of Each Block in `try` / `except` / `else` / `finally` ”). Unfortunately, it will not:

你可能会认为异常变量仍然存在于异常处理机制的`finally`块中（参见条目80：“充分利用`try` / `except` / `else` / `finally`中的每个块”）。不幸的是，事实并非如此：

```
try:
    raise MyError(123)
except MyError as e:
    print(f"Inside {e=}")
finally:
    print(f"Finally {e=}") # Raises
    
>>>
Inside e=MyError(123)
Traceback ...
NameError: name 'e' is not defined
```

Sometimes it’s useful to save the result of each potential outcome of a `try` statement. For example, say that I want to log the result of each branch for debugging purposes. In order to accomplish this, I need to create a new variable and assign a value to it in each branch:

有时候保存`try`语句每个可能结果是有用的。例如，假设我想记录每个分支的结果以供调试。为了实现这一点，我需要创建一个新变量并在每个分支中为其赋值：

```
result = "Unexpected exception"
try:
    raise MyError(123)
except MyError as e:
    result = e
except OtherError as e:
    result = e
else:
    result = "Success"
finally:
    print(f"Log {result=}")

>>>
Log result=MyError(123)
```

It’s important to note that the `result` variable is assigned in the example above even before the `try` block. This is necessary to address the situation where an exception is raised that is not covered by one of the `except` clauses. If you don’t assign `result` up front, a runtime error will be raised instead your original error:

需要注意的是，在上面的例子中，`result` 变量在`try`块之前就被赋值了。这是为了解决未被任何`except`子句处理的异常情况。如果不提前分配`result`，将会引发运行时错误而不是你的原始错误：

```
try:
    raise OtherError(123) # Not handled
except MyError as e:
    result = e
else:
    result = "Success"
finally:
    print(f"{result=}") # Raises

>>>
Traceback ...
OtherError: 123
The above exception was the direct cause of the ...
Traceback ...
NameError: name 'result' is not defined
```


This illustrates another way in which Python does not consistently scope variables to functions. The lifetime of a variable in an `except` block, generator expression, list comprehension, or `for` loop might be different than what you expect (see Item 42: “Reduce Repetition in Comprehensions with Assignment Expressions” for an example).

这说明了Python在变量作用域方面不一致的另一种方式。`except`块、生成器表达式、列表推导式或`for`循环中的变量生命周期可能与你的预期不同（参见条目42：“使用赋值表达式减少推导式中的重复”）。

**Things to Remember**
- `Exception` variables assigned by `except` statements are only accessible within their associated `except` blocks.
- In order to access a caught `Exception` instance in the surrounding scope or subsequent `finally` block, you must assign it to another variable name.

**注意事项**
- 由`except`语句分配的异常变量只能在其关联的`except`块内访问。
- 要想在周围的作用域或后续的`finally`块中访问捕获的异常实例，必须将其分配给另一个变量名。