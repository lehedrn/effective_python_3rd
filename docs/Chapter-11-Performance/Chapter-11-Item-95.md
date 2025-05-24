# Chapter 11: Performance (性能)

## Item 95: Consider `ctypes` to Rapidly Integrate with Native Libraries (考虑使用 `ctypes` 快速集成原生库)

The `ctypes` built-in module enables Python to call functions that are defined in native libraries. Those libraries can be implemented in any other programming language that can export functions following the C calling convention (e.g., C, C++, Rust). The module provides two key benefits to Python developers:

`ctypes` 是一个内建模块，使 Python 能够调用定义在原生库中的函数。这些库可以用任何能够按照 C 调用约定导出函数的编程语言实现（例如 C、C++、Rust）。该模块为 Python 开发人员提供了两个关键优势：

- `ctypes` makes it easy to connect systems together using Python. If there’s an existing native library with functionality you need, you will be able to use it without much effort.
- `ctypes` provides a straightforward path to optimizing slow parts of your program. If you find a hotspot you can’t speedup otherwise, you can reimplement it in another language and then call the faster version using `ctypes` .

- `ctypes` 使得使用 Python 连接系统变得容易。如果存在一个你需要其功能的现有原生库，你将能够轻松地使用它。
- `ctypes` 提供了一条优化程序缓慢部分的直接路径。如果你发现一个无法通过其他方式加速的热点，你可以用另一种语言重新实现它，然后使用 `ctypes` 调用更快的版本。

For example, consider the `dot_product` function from the previous item (see Item 94: “Know When and How to Replace Python with Another Programming Language”):

例如，考虑前一条目中的 `dot_product` 函数（见条目94：“知道何时以及如何用另一种编程语言替换 Python”）:

```
def dot_product(a, b):
    result = 0
    for i, j in zip(a, b):
        result += i * j
    return result
```

I can implement similar functionality using a simple C function that operates on arrays. Here, I define the interface:

我可以使用一个简单的 C 函数来实现类似的功能，该函数操作数组。在这里，我定义了接口：

```
/* my_library.h */
extern double dot_product(int length, double* a, double* b);
```

The implementation is simple and will be automatically vectorized by most C compilers to maximize performance using advanced processor features like SIMD (single instruction, multiple data) operations:

其实现很简单，并且大多数 C 编译器会自动向量化以利用诸如 SIMD（单指令多数据）这样的高级处理器特性来最大化性能：

```
/* my_library.c */
#include <stdio.h>
#include "my_library.h"

double dot_product(int length, double* a, double* b) {
    double result = 0;
    for (int i = 0; i < length; i++) {
        result += a[i] * b[i];
    }
    return result;
}
```

Now I need to compile this code into a library file. Doing so is out of the scope of this book, but the command on my machine is:

现在我需要将这段代码编译成一个库文件。这超出了本书的范围，但我机器上的命令是：

```
$ cc -shared -o my_library.lib my_library.c
```

I can load this library file in Python simply by providing its path to the `ctypes.cdll.LoadLibrary` constructor:

我可以在 Python 中简单地通过提供其路径给 `ctypes.cdll.LoadLibrary` 构造函数来加载这个库文件：

```
import ctypes

library_path = ...

import pathlib

run_py = pathlib.Path(__file__)
library_path = run_py.parent / "item_095" / "my_library" / "my_library.lib"

my_library = ctypes.cdll.LoadLibrary(library_path)
```

The `dot_product` function that was implemented in C is now available as an attribute of `my_library` :

在 C 中实现的 `dot_product` 函数现在作为 `my_library` 的属性可用：

```
print(my_library.dot_product)

>>>
<_FuncPtr object at 0x10544cc50>
```

If you wrap the imported function pointer with a `ctypes.CFUNCTYPE` object, you might observe broken behavior due to implicit type conversions. Instead, it’s best to directly assign the `restype` and `argtypes` attributes of an imported function to the `ctypes` types that match the signature of the function’s native implementation:

如果您用 `ctypes.CFUNCTYPE` 对象包装导入的函数指针，由于隐式类型转换可能会观察到损坏的行为。因此，最好直接为导入的函数分配与函数本机实现签名匹配的 `ctypes` 类型的 `restype` 和 `argtypes` 属性：

```
my_library.dot_product.restype = ctypes.c_double

vector_ptr = ctypes.POINTER(ctypes.c_double)
my_library.dot_product.argtypes = (
    ctypes.c_int,
    vector_ptr,
    vector_ptr,
)
```

Calling the imported function is relatively easy. First, I define an array data type that contains three double values. Then, I allocate two instances of that type to pass as arguments:

调用导入的函数相对容易。首先，我定义了一个包含三个双精度值的数组数据类型。然后，我分配两个这种类型的实例作为参数传递：

```
size = 3
vector3 = ctypes.c_double * size
a = vector3(1.0, 2.5, 3.5)
b = vector3(-7, 4, -12.1)
```

And finally, I call the `dot_product` imported function with these two arrays. I need to use the `ctypes.cast` helper function to ensure that the address of the first item in the array is supplied——matching C convention——instead of the address of the `vector3` Python object. I don’t need to do any casting of the return value because `ctypes` automatically converts it to a Python value:

最后，我使用这两个数组调用 `dot_product` 导入的函数。我需要使用 `ctypes.cast` 辅助函数确保提供的是数组中第一个元素的地址——符合 C 的惯例——而不是 `vector3` Python 对象的地址。我们不需要对返回值做任何转换，因为 `ctypes` 会自动将其转换为 Python 值：

```
result = my_library.dot_product(
    3,
    ctypes.cast(a, vector_ptr),
    ctypes.cast(b, vector_ptr),
)
print(result)

>>>
-39.35
```

It should be obvious by now that the ergonomics of the `ctypes` API are quite poor and not Pythonic. But it’s impressive how quickly everything comes together and starts working. To make it feel more natural, here I wrap the imported native function with a Python function to do the datatype mapping and verify assumptions (see Item 81: “ `assert` Internal Assumptions, `raise` Missed Expectations” for background):

到现在为止，很明显 `ctypes` API 的易用性相当差，不够 Pythonic。但令人印象深刻的是，一切是如何快速地整合在一起并开始工作。为了让它感觉更自然，我在此处用一个 Python 函数包装导入的本地函数，以进行数据类型映射并验证假设（有关背景信息，请参见条目81：“断言内部假设，未满足期望则抛出异常”）：

```
def dot_product(a, b):
    size = len(a)
    assert len(b) == size
    a_vector = vector3(*a)
    b_vector = vector3(*b)
    result = my_library.dot_product(size, a_vector, b_vector)
    return result

result = dot_product([1.0, 2.5, 3.5], [-7, 4, -12.1])
print(result)

>>>
-39.35
```

Alternatively, I can use Python’s C extension API (see Item 96: “Consider Extension Modules to Maximize Performance and Ergonomics”) to provide a more Pythonic interface with native performance. However, `ctypes` has some advantages over C extensions that are worthwhile:

- Pointer values that you hold with `ctypes` will be freed automatically when the Python object reference count goes to zero. C extensions must do manual memory management for C pointers and manual reference counting for Python objects.
- When you call a function with `ctypes` it automatically releases the GIL while the call is executing, allowing other Python threads to progress in parallel (see Item 68: “Use Threads for Blocking I/O, Avoid for Parallelism”. With a C extension module the GIL must be managed explicitly, and functionality is limited while not holding the lock.
- With `ctypes` , you simply provide a path to a shared object or dynamic library on disk and it can be loaded. Compilation can be done separately with a build system that you already have in place. With Python C extensions you need to leverage the Python build system to include the right paths, set linker flags, etc——it’s a lot of complexity and potentially duplicative.

或者，我可以使用 Python 的 C 扩展 API（见条目96：“考虑扩展模块以最大化性能和用户体验”）来提供具有原生性能的更 Pythonic 接口。然而，与 C 扩展相比，`ctypes` 具有一些值得考虑的优势：

- 使用 `ctypes` 持有的指针值将在 Python 对象引用计数归零时自动释放。C 扩展必须手动管理 C 指针的内存和 Python 对象的手动引用计数。
- 当您使用 `ctypes` 调用函数时，它会在执行调用期间自动释放 GIL，允许其他 Python 线程并行进展（见条目68：“在线程用于阻塞 I/O 时使用，避免用于并行化”）。对于 C 扩展模块，GIL 必须显式管理，在不持有锁的情况下功能受限。
- 使用 `ctypes` ，只需提供磁盘上共享对象或动态库的路径即可加载。可以使用现有的构建系统单独进行编译。而 Python C 扩展需要利用 Python 构建系统来包含正确的路径、设置链接器标志等——这带来了大量复杂性和潜在的重复。

But there are also important downsides to using the `ctypes` module instead of building a C extension:
- `ctypes` restricts you to the data types that C can describe. You lose most of the expressive power of Python, including extremely common functionality like iterators (see Item 21: “Be Defensive When Iterating Over Arguments”) and duck typing (see Item 25: “Be Cautious When Relying on Dictionary Insertion Ordering”). Even with wrappers, native functions imported using `ctypes` can feel strange to Python programmers and hamper productivity.
- Calling `ctypes` with the right data types often requires you to make copies or transformations of function inputs and outputs. The cost of this overhead might undermine the performance benefit of using a native library, rendering the whole optimization exercise worthless. C extensions allow you to bypass copies—the only speed limit is the inherent performance of the underlying data types.
- If you use `ctypes` slightly the wrong way, that might cause your program to corrupt its own memory and behave strangely. For example, if you accidentally provide a `ctypes.c_double` where you should have specified a `ctypes.c_int` for function arguments or return values, you might see unpredictable crashes with cryptic error messages. The `faulthandler` built-in module can help track these problems down, but they’re still difficult to debug.

但是，使用 `ctypes` 模块而非构建 C 扩展也存在重要缺点：

- `ctypes` 将您限制在 C 可以描述的数据类型中。您会失去 Python 大量的表达能力，包括极其常见的功能，如迭代器（见条目21：“在迭代参数时要谨慎”）和鸭子类型（见条目25：“依赖字典插入顺序时要小心”）。即使有封装器，使用 `ctypes` 导入的本地函数对 Python 程序员来说可能感觉奇怪，从而影响生产力。
- 使用正确的数据类型调用 `ctypes` 经常要求您复制或转换函数输入和输出。这种开销的成本可能会削弱使用原生库带来的性能优势，使整个优化练习变得毫无价值。C 扩展允许绕过复制——唯一的速度限制是底层数据类型的固有性能。
- 如果您稍微错误地使用 `ctypes`，那可能会导致程序破坏自己的内存并表现出奇怪的行为。例如，如果您意外地在应指定 `ctypes.c_int` 的函数参数或返回值中使用了 `ctypes.c_double`，您可能会看到不可预测的崩溃并伴有晦涩的错误消息。`faulthandler` 内置模块可以帮助追踪这些问题，但它们仍然难以调试。

The best practice when using `ctypes` is to always write corresponding unit tests before putting it to work in more complex code (see Item 109: “Prefer Integration Tests Over Unit Tests”). The goal of these tests is to exercise the basic surface area of a library that you’re calling in order to confirm that it works as expected for simple usage. This can help you detect situations like when a function in a shared library has its argument types modified, but your `ctypes` usage hasn’t been updated to match. Here, I test the `my_library.dot_product` symbol from the imported library:

使用 `ctypes` 的最佳实践是在将其应用于更复杂的代码之前编写相应的单元测试（见条目109：“优先选择集成测试而非单元测试”）。这些测试的目标是对您正在调用的库的基本功能区域进行测试，以确认其按预期工作。这可以帮助您检测到诸如共享库中的函数参数类型被修改，但您的 `ctypes` 使用尚未更新以匹配的情况。以下是我测试导入库中的 `my_library.dot_product` 符号：

```
from unittest import TestCase
class MyLibraryTest(TestCase):
    def test_dot_product(self):
        vector3 = ctypes.c_double * size
        a = vector3(1.0, 2.5, 3.5)
        b = vector3(-7, 4, -12.1)
        vector_ptr = ctypes.POINTER(ctypes.c_double)
        result = my_library.dot_product(
            3,
            ctypes.cast(a, vector_ptr),
            ctypes.cast(b, vector_ptr),
        )
        self.assertAlmostEqual(-39.35, result)

import unittest
suite = unittest.defaultTestLoader.loadTestsFromTestCase(
    MyLibraryTest
)
# suite.debug()
unittest.TextTestRunner(stream=STDOUT).run(suite)

>>>
.
-------------------------------------------------
-----
Ran 1 test in 0.000s
OK
```

The `ctypes` module includes additional functionality for mapping Python objects to C structs, copying memory, error checking, and a whole lot more (see the full manual `https://docs.python.org/3/library/ctypes.html` for details). Ultimately, you’ll need to decide if the ease and speed of development you get from using `ctypes` is worth its inferior ergonomics and overhead.

`ctypes` 模块还包括额外的功能，用于将 Python 对象映射到 C 结构体、复制内存、错误检查等等（详细信息请参阅完整手册 `https://docs.python.org/3/library/ctypes.html`）。最终，您需要决定从使用 `ctypes` 获得的开发便捷性和速度是否值得其较差的易用性和开销。

**Things to Remember**

- The `ctypes` built-in module makes it easy to integrate the functionality and performance of native libraries written in other languages into Python programs.
- In comparison to the Python C extension API, `ctypes` enables rapid development without additional build complexity.
- It’s difficult to write Pythonic APIs using `ctypes` because the data types and protocols available are limited to what’s expressible in C.

**注意事项**

- `ctypes` 内建模块使得将用其他语言编写的原生库的功能和性能集成到 Python 程序中变得容易。
- 与 Python C 扩展 API 相比，`ctypes` 可以在没有额外构建复杂性的情况下实现快速开发。
- 使用 `ctypes` 编写 Pythonic API 很困难，因为可用的数据类型和协议仅限于 C 可以表达的内容。