# Chapter 5: Functions (函数)

## Item 38: Define Function Decorators with `functools.wraps` (使用 `functools.wraps` 定义函数装饰器)

Python has special syntax for decorators that can be applied to functions. A decorator has the ability to run additional code before and after each call to a function it wraps. This means decorators can access and modify input arguments, return values, and raised exceptions. These capabilities can be useful for enforcing semantics, debugging, registering functions, and more.

Python 有特殊的语法用于应用于函数的装饰器。装饰器有能力在它包装的函数调用之前和之后运行额外的代码。这意味着装饰器可以访问和修改输入参数、返回值和抛出的异常。这些功能对于执行语义检查、调试、注册函数等非常有用。

For example, say that I want to print the arguments and return value of a function call. This can be especially helpful when debugging the stack of nested function calls from a recursive function (logging exceptions could be useful too; see Item 86: “Understand the Difference Between Exception and BaseException ”). Here, I define such a decorator by using `*args` and `**kwargs` (see Item 34: “Reduce Visual Noise with Variable Positional Arguments” and Item 35: “Provide Optional Behavior with Keyword Arguments”) to pass through all parameters to the wrapped function:

例如，假设我想打印一个函数调用的参数和返回值。这在调试递归函数调用栈时尤其有帮助（记录异常信息也可能很有用；参见条目86：“理解 Exception 和 BaseException 的区别”）。这里，我定义了这样一个装饰器，通过使用 `*args` 和 `**kwargs` （参见条目34：“使用变量位置参数减少视觉噪音”和条目35：“使用关键字参数提供可选行为”）来传递所有参数到被包装的函数：

```
def trace(func):
    def wrapper(*args, **kwargs):
        args_repr = repr(args)
        kwargs_repr = repr(kwargs)
        result = func(*args, **kwargs)
        print(f"{func.__name__}"
              f"({args_repr}, {kwargs_repr}) "
              f"-> {result!r}")
        return result
    return wrapper
```

I can apply this decorator to a function by using the `@` symbol:

我可以通过使用 `@` 符号将此装饰器应用到函数上：

```
@trace
def fibonacci(n):
    """Return the n-th Fibonacci number"""
    if n in (0, 1):
        return n
    return fibonacci(n - 2) + fibonacci(n - 1)
```

Using the `@` symbol is equivalent to calling the decorator on the function it wraps and assigning the return value to the original name in the same scope:

使用 `@` 符号等同于使用装饰器调用它所包装的函数，并将返回值分配给相同作用域中的原始名称：

```
fibonacci = trace(fibonacci)
```

The decorated function runs the `wrapper` code before and after `fibonacci` runs. It prints the arguments and return value at each level in the recursive stack:

装饰后的函数在 `fibonacci` 运行前和运行后都会运行 `wrapper` 代码。它会在递归栈的每一层打印参数和返回值：

```
fibonacci(4)
>>>
fibonacci((0,), {}) -> 0
fibonacci((1,), {}) -> 1
fibonacci((2,), {}) -> 1
fibonacci((1,), {}) -> 1
fibonacci((0,), {}) -> 0
fibonacci((1,), {}) -> 1
fibonacci((2,), {}) -> 1
fibonacci((3,), {}) -> 2
fibonacci((4,), {}) -> 3
```

This works well, but it has an unintended side effect. The value returned by the decorator—the function that’s called above—doesn’t think it’s named `fibonacci` :

这工作得很好，但它有一个意外的副作用。由装饰器返回的值——即上面调用的函数——并不认为它的名字是 `fibonacci`：

```
print(fibonacci)
>>>
<function trace.<locals>.wrapper at 0x104a179c0>
```

The cause of this isn’t hard to see. The `trace` function returns the `wrapper` defined within its body. The `wrapper` function is what’s assigned to the `fibonacci` name in the containing module because of the decorator. This behavior is problematic because it undermines tools that do introspection, such as debuggers (see Item 115: “Consider Interactive Debugging with pdb ”).

这个问题的原因不难发现。`trace` 函数返回其体内定义的 `wrapper`。由于装饰器的关系，`wrapper` 函数就是被赋值给模块中 `fibonacci` 名称的那个函数。这种行为是有问题的，因为它破坏了诸如调试器之类的进行内省的工具的功能（参见条目115：“考虑使用 pdb 进行交互式调试”）。

For example, the `help` built-in function is useless when called on the decorated `fibonacci` function. It should print out the docstring defined above ( `'Return the n-th Fibonacci number'` ), but it doesn’t:

例如，当在装饰过的 `fibonacci` 函数上调用内置的 `help` 函数时，它就变得无用。它应该打印出上面定义的文档字符串（'Return the n-th Fibonacci number'），但实际却不是这样：

```
help(fibonacci)
>>>
Help on function wrapper in module __main__:
wrapper(*args, **kwargs)
```

Another problem is that object serializers (see Item 106: “Make pickle Reliable with copyreg ”) break because they can’t determine the location of the original function that was decorated:

另一个问题是对象序列化器（参见条目106：“使用 copyreg 让 pickle 更可靠”）会失效，因为它们无法确定被装饰的原始函数的位置：

```
import pickle
pickle.dumps(fibonacci)
>>>
Traceback ...
AttributeError: Can't pickle local object 'trace.<locals>.wrapper'
```

The solution is to use the `wraps` helper function from the `functools` built-in module. This is a decorator that helps you write decorators. When you apply it to the `wrapper` function, it copies all of the important metadata about the inner function to the outer function. Here, I redefine the `trace` decorator using `wraps` :

解决方案是使用来自 `functools` 内置模块的 `wraps` 辅助函数。这是一个能帮助你编写装饰器的装饰器。当你将其应用到 `wrapper` 函数时，它会将内部函数的所有重要元数据复制到外部函数。在这里，我重新定义了使用 `wraps` 的 `trace` 装饰器：

```
from functools import wraps

def trace(func):
    @wraps(func)  # Changed
    def wrapper(*args, **kwargs):
        args_repr = repr(args)
        kwargs_repr = repr(kwargs)
        result = func(*args, **kwargs)
        print(f"{func.__name__}" f"({args_repr}, {kwargs_repr}) " f"-> {result!r}")
        return result

    return wrapper

@trace
def fibonacci(n):
    """Return the n-th Fibonacci number"""
    if n in (0, 1):
        return n
    return fibonacci(n - 2) + fibonacci(n - 1)
```

Now, running the `help` function produces the expected result, even though the function is decorated:

现在，即使该函数已被装饰，运行 `help` 函数也能产生预期的结果：

```
help(fibonacci)
>>>
Help on function fibonacci in module __main__:
fibonacci(n)
 Return the n-th Fibonacci number
```

The pickle object serializer also works:

`Pickle` 对象序列化器也起作用：

```
print(pickle.dumps(fibonacci))
>>>
b'\x80\x04\x95\x1a\x00\x00\x00\x00\x00\x00\x00\x8
4\x8c\tfibonacci\x94\x93\x94.'
```

Beyond these examples, Python functions have many other standard attributes (e.g., `__name__` , `__module__` , `__annotations__` ) that must be preserved to maintain the interface of functions in the language. Using `wraps` ensures that you’ll always get the correct behavior.

除了这些例子之外，Python 函数还有许多其他标准属性（如 `__name__`、`__module__`、`__annotations__`）必须保留，以保持语言中函数接口的行为。使用 wraps 可以确保您始终获得正确的行为。

**Things to Remember**
- Decorators in Python are syntax to allow one function to modify another function at runtime. 
- Using decorators can cause strange behaviors in tools that do introspection, such as debuggers.
- Use the `wraps` decorator from the `functools` built-in module when you define your own decorators to avoid any issues.

**注意事项**
- Python 中的装饰器是一种语法，允许一个函数在运行时修改另一个函数。
- 使用装饰器可能会导致某些做内省的工具（如调试器）出现奇怪的行为。
- 在定义自己的装饰器时，使用来自 `functools` 内建模块的 `wraps` 装饰器，以避免任何问题。