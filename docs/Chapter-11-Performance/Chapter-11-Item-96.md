# Chapter 11: Performance (性能)

## Item 96: Consider Extension Modules to Maximize Performance and Ergonomics (考虑使用扩展模块以最大化性能和可用性)

The CPython implementation of the Python language (see Item 1: “Know Which Version of Python You’re Using”) supports extension modules that are written in C. These modules can directly use the Python API to take advantage of object-oriented features (see Chapter 7), duck typing protocols (see Item 25: “Be Cautious When Relying on Dictionary Insertion Ordering”), reference counting garbage collection, and nearly every other feature that makes Python great. The previous item (see Item 95: “Consider `ctypes` to Rapidly Integrate with Native Libraries”) presented the upsides and downsides of the `ctypes` built-in module——the gist: If you’re looking to provide a Pythonic development experience without compromising on performance or platform-specific capabilities, extension modules are the way to go.

Python语言的CPython实现（参见条目1：“了解你使用的Python版本”）支持用C编写的扩展模块。这些模块可以直接使用Python API，从而利用面向对象特性（参见第7章）、鸭子类型协议（参见条目25：“依赖字典插入顺序时要小心”）、引用计数垃圾回收机制，以及几乎所有让Python变得强大的其他功能。上一条（参见条目95：“快速集成本地库可考虑`ctypes`”）介绍了`ctypes`内置模块的优缺点——简而言之：如果你希望在不牺牲性能或平台特定功能的前提下提供Python风格的开发体验，扩展模块是正确的选择。

Although creating an extension module is much more complicated than using `ctypes` , the Python C API helps make it pretty straightforward. To demonstrate, I’ll implement the same `dot_product` function from before (see Item 94: “Know When and How to Replace Python with Another Programming Language”) but as an extension module. First, I’ll declare the C function that I want the extension to provide:

尽管创建扩展模块比使用`ctypes`复杂得多，但Python C API有助于使其相对简单明了。为了演示，我将重新实现之前的`dot_product`函数（参见条目94：“知道何时以及如何用另一种编程语言替换Python”），但这次作为扩展模块。首先，我将声明该扩展希望提供的C函数：

```
/* my_extension.h */

#define PY_SSIZE_T_CLEAN
#include <Python.h>

PyObject *dot_product(PyObject *self, PyObject *args);
```

Then I’ll implement the function using C. The Python API I use to interface with inputs and outputs (e.g., `PyList_Size` , `PyFloat_FromDouble` ) is extensive, constantly evolving, and——luckily——well-documented (see `https://docs.python.org/3/extending`). This version of the function expects to receive two equally-sized lists of floating point numbers and return a single floating point number:

然后我将使用C实现该函数。用于与输入输出进行交互的Python API（例如`PyList_Size`、`PyFloat_FromDouble`）非常广泛，不断演进，并且幸运的是文档齐全（参见`https://docs.python.org/3/extending`）。此版本的函数期望接收两个等长的浮点数列表并返回一个浮点数：

```
/* dot_product.c */

#include "my_extension.h"

PyObject *dot_product(PyObject *self, PyObject *args)
{
    PyObject *left, *right;
    if (!PyArg_ParseTuple(args, "OO", &left, &right)) {
        return NULL;
    }
    if (!PyList_Check(left) || !PyList_Check(right)) {
        PyErr_SetString(PyExc_TypeError, "Both arguments must be lists");
        return NULL;
    }

    Py_ssize_t left_length = PyList_Size(left);
    Py_ssize_t right_length = PyList_Size(right);
    if (left_length == -1 || right_length == -1) {
        return NULL;
    }
    if (left_length != right_length) {
        PyErr_SetString(PyExc_ValueError, "Lists must be the same length");
        return NULL;
    }

    double result = 0;

    for (Py_ssize_t i = 0; i < left_length; i++) {
        PyObject *left_item = PyList_GET_ITEM(left, i);
        PyObject *right_item = PyList_GET_ITEM(right, i);

        double left_double = PyFloat_AsDouble(left_item);
        double right_double = PyFloat_AsDouble(right_item);
        if (PyErr_Occurred()) {
            return NULL;
        }

        result += left_double * right_double;
    }

    return PyFloat_FromDouble(result);
}
```

The function is about 40 lines of code, which is 4 times longer than a simple C implementation that can be called using the `ctypes` module. There’s also some additional boilerplate code required to configure the extension module and initialize it:

这个函数大约有40行代码，是使用`ctypes`调用的简单C实现长度的四倍。还需要一些额外的样板代码来配置扩展模块并初始化它：

```
/* init.c */

#include "my_extension.h"

static PyMethodDef my_extension_methods[] = {
    {
        "dot_product",
        dot_product,
        METH_VARARGS,
        "Compute dot product",
    },
    {
        NULL,
        NULL,
        0,
        NULL,
    },
};

static struct PyModuleDef my_extension = {
    PyModuleDef_HEAD_INIT,
    "my_extension",
    "My C-extension module",
    -1,
    my_extension_methods,
};

PyMODINIT_FUNC
PyInit_my_extension(void)
{
    return PyModule_Create(&my_extension);
}
```


Now, I need to compile the C code into a native library that can be dynamically loaded by the CPython interpreter. The simplest way to do this is to define a minimal `setup.py` configuration file:

现在，我需要将C代码编译成可以被CPython解释器动态加载的本机库。最简单的方法是定义一个最小的`setup.py`配置文件：

```
# setup.py

from setuptools import Extension, setup

setup(
    name="my_extension",
    ext_modules=[
        Extension(
            name="my_extension",
            sources=["init.c", "dot_product.c"],
        ),
    ],
)
```

I can use this configuration file, a virtual environment (see Item 117: “Use Virtual Environments for Isolated and Reproducible Dependencies”), and the `setuptools` package (see Item 116: “Know Where to Find Community-Built Modules”) to properly drive my system’s compiler with the right paths and flags; at the end, I’ll get a native library file that can be imported by Python:

我可以使用这个配置文件、虚拟环境（参见条目117：“使用虚拟环境实现隔离和可重现的依赖”）以及`setuptools`包（参见条目116：“知道在哪里找到社区构建的模块”）来正确驱动系统的编译器，并在最后得到一个可以被Python导入的本机库文件：

```
$ python3 -m venv .
$ source bin/activate
$ pip install setuptools
...
$ python3 setup.py develop
...
```

There are many ways to build Python extension modules and package them up for distribution. Unfortunately, the tools for this are constantly changing. In this example, I’m only focused on getting an extension module working in my local development environment. If you encounter problems or have other use-cases, be sure to check the latest documentation from the official Python Packaging Authority (`https://www.pypa.io`).

有许多方法可以构建Python扩展模块并将其打包分发。不幸的是，相关工具一直在变化。在此示例中，我只关注在我的本地开发环境中运行扩展模块。如果遇到问题或有其他使用场景，请务必查阅Python Packaging Authority的最新文档（`https://www.pypa.io`）。

After compilation, I can use tests written in Python (see Item 108: “Verify Related Behaviors in `TestCase` Subclasses”) to verify that the extension module works as expected:

编译后，我可以使用Python编写的测试（参见条目108：“在`TestCase`子类中验证相关行为”）来验证扩展模块是否按预期工作：

```
# my_extension_test.py

import unittest
import my_extension

class MyExtensionTest(unittest.TestCase):

    def test_empty(self):
        result = my_extension.dot_product([], [])
        self.assertAlmostEqual(0, result)

    def test_positive_result(self):
        result = my_extension.dot_product(
            [3, 4, 5],
            [-1, 9, -2.5],
        )
        self.assertAlmostEqual(20.5, result)

    def test_zero_result(self):
        result = my_extension.dot_product(
            [0, 0, 0],
            [1, 1, 1],
        )
        self.assertAlmostEqual(0, result)

    def test_negative_result(self):
        result = my_extension.dot_product(
            [-1, -1, -1],
            [1, 1, 1],
        )
        self.assertAlmostEqual(-3, result)

    def test_not_lists(self):
        with self.assertRaises(TypeError) as context:
            my_extension.dot_product((1, 2), [3, 4])
        self.assertEqual(
            "Both arguments must be lists", str(context.exception)
        )

        with self.assertRaises(TypeError) as context:
            my_extension.dot_product([1, 2], (3, 4))
        self.assertEqual(
            "Both arguments must be lists", str(context.exception)
        )

    def test_mismatched_size(self):
        with self.assertRaises(ValueError) as context:
            my_extension.dot_product([1], [2, 3])
        self.assertEqual(
            "Lists must be the same length", str(context.exception)
        )

        with self.assertRaises(ValueError) as context:
            my_extension.dot_product([1, 2], [3])
        self.assertEqual(
            "Lists must be the same length", str(context.exception)
        )

    def test_not_floatable(self):
        with self.assertRaises(TypeError) as context:
            my_extension.dot_product(["bad"], [1])
        self.assertEqual(
            "must be real number, not str", str(context.exception)
        )


if __name__ == "__main__":
    unittest.main()
```

This was a lot of effort compared to the basic C implementation. And the ergonomics of the interface are about the same as if I used the `ctypes` module: both arguments to `dot_product` need to be lists that contain floats. If this is as far as you’re going to go with the C extension API, then it’s not worth it. You’d not be taking advantage of its most valuable features.

与基本的C实现相比，这是一次相当大的努力。而且接口的可用性几乎与使用`ctypes`模块一样：`dot_product`的两个参数都需要是包含浮点数的列表。如果这就是你对C扩展API所能做的全部，那么这样做并不值得。你并没有充分利用其最有价值的功能。

Now, I’m going to create another version of this extension module that uses the iterator and number protocols that are provided by the Python API. This is 60 lines of code——50% more than the simpler `dot_product` function and 6 times more than the basic C version——but it enables the full set of features that make Python so powerful. By using the `PyObject_GetIter` and `PyIter_Next` APIs, the input types can be any kind of iterable container, such as tuples, lists, generators, etc (see Item 21: “Be Defensive When Iterating Over Arguments”). By using the `PyNumber_Multiply` and `PyNumber_Add` APIs, the values from the iterators can be any object that properly implements the number special methods (see Item 57: “Inherit from `collections.abc` Classes for Custom Container Types”):

现在，我将创建另一个版本的这个扩展模块，它使用Python API提供的迭代器和数字协议。这是60行代码——比简单的`dot_product`函数多了50%，是基本C版本的六倍——但它启用了使Python如此强大的一整套功能。通过使用`PyObject_GetIter`和`PyIter_Next` API，输入类型可以是任何类型的可迭代容器，比如元组、列表、生成器等（参见条目21：“迭代参数时要保持防御性”）。通过使用`PyNumber_Multiply`和`PyNumber_Add` API，迭代器中的值可以是任何正确实现了数字特殊方法的对象（参见条目57：“自定义容器类型应继承`collections.abc`类”）：

```
#include "my_extension2.h"

PyObject *dot_product(PyObject *self, PyObject *args)
{
    PyObject *left, *right;
    if (!PyArg_ParseTuple(args, "OO", &left, &right)) {
        return NULL;
    }
    PyObject *left_iter = PyObject_GetIter(left);
    if (left_iter == NULL) {
        return NULL;
    }
    PyObject *right_iter = PyObject_GetIter(right);
    if (right_iter == NULL) {
        Py_DECREF(left_iter);
        return NULL;
    }

    PyObject *left_item = NULL;
    PyObject *right_item = NULL;
    PyObject *multiplied = NULL;
    PyObject *result = PyLong_FromLong(0);

    while (1) {
        Py_CLEAR(left_item);
        Py_CLEAR(right_item);
        Py_CLEAR(multiplied);
        left_item = PyIter_Next(left_iter);
        right_item = PyIter_Next(right_iter);

        if (left_item == NULL && right_item == NULL) {
            break;
        } else if (left_item == NULL || right_item == NULL) {
            PyErr_SetString(PyExc_ValueError, "Arguments had unequal length");
            break;
        }

        multiplied = PyNumber_Multiply(left_item, right_item);
        if (multiplied == NULL) {
            break;
        }
        PyObject *added = PyNumber_Add(result, multiplied);
        if (added == NULL) {
            break;
        }
        Py_CLEAR(result);
        result = added;
    }

    Py_CLEAR(left_item);
    Py_CLEAR(right_item);
    Py_CLEAR(multiplied);
    Py_DECREF(left_iter);
    Py_DECREF(right_iter);

    if (PyErr_Occurred()) {
        Py_CLEAR(result);
        return NULL;
    }

    return result;
}
```

The implementation is further complicated by the need to properly manage object reference counts and the peculiarities of error propagation and reference borrowing. But the result is, perhaps, Python’s holy grail: a module that is both fast and easy to use. Here, I show that it works for multiple types of iterables and the `Decimal` numerical class (see Item 106: “Use `decimal` When Precision is Paramount”):

由于需要正确管理对象引用计数以及错误传播和引用借用的特性，实现变得更加复杂。但结果可能是Python的圣杯：一个既快速又易于使用的模块。在这里，我展示了它可以处理多种类型的可迭代对象和`Decimal`数值类（参见条目106：“精度至关重要时使用`decimal`”）：

```
# my_extension2_test.py

import unittest
import my_extension2

class MyExtension2Test(unittest.TestCase):

    def test_decimals(self):
        import decimal

        a = [decimal.Decimal(1), decimal.Decimal(2)]
        b = [decimal.Decimal(3), decimal.Decimal(4)]
        result = my_extension2.dot_product(a, b)
        self.assertEqual(11, result)

    def test_not_lists(self):
        result1 = my_extension2.dot_product(
            (1, 2),
            [3, 4],
        )
        result2 = my_extension2.dot_product(
            [1, 2],
            (3, 4),
        )
        result3 = my_extension2.dot_product(
            range(1, 3),
            range(3, 5),
        )
        self.assertAlmostEqual(11, result1)
        self.assertAlmostEqual(11, result2)
        self.assertAlmostEqual(11, result3)

    def test_empty(self):
        result = my_extension2.dot_product([], [])
        self.assertAlmostEqual(0, result)

    def test_positive_result(self):
        result = my_extension2.dot_product(
            [3, 4, 5],
            [-1, 9, -2.5],
        )
        self.assertAlmostEqual(20.5, result)

    def test_zero_result(self):
        result = my_extension2.dot_product(
            [0, 0, 0],
            [1, 1, 1],
        )
        self.assertAlmostEqual(0, result)

    def test_negative_result(self):
        result = my_extension2.dot_product(
            [-1, -1, -1],
            [1, 1, 1],
        )
        self.assertAlmostEqual(-3, result)

    def test_mismatched_size(self):
        with self.assertRaises(ValueError) as context:
            my_extension2.dot_product([1], [2, 3])
        self.assertEqual(
            "Arguments had unequal length", str(context.exception)
        )

        with self.assertRaises(ValueError) as context:
            my_extension2.dot_product([1, 2], [3])
        self.assertEqual(
            "Arguments had unequal length", str(context.exception)
        )

    def test_not_floatable(self):
        with self.assertRaises(TypeError) as context:
            my_extension2.dot_product(["bad"], [1])
        self.assertEqual(
            "unsupported operand type(s) for +: 'int' and 'str'",
            str(context.exception),
        )


if __name__ == "__main__":
    unittest.main()
```

This level of extensibility and flexibility in an API is what good ergonomics look like. Achieving the same behaviors with basic C code would require essentially reimplementing the core of the Python interpreter and API. Knowing that, the larger line count of these extension modules seems reasonable given how much functionality and performance you get in return.

这种级别的可扩展性和灵活性正是良好可用性的体现。使用基本的C代码实现相同的行为实际上需要重新实现Python解释器和API的核心部分。考虑到这一点，这些扩展模块的更大代码量似乎是合理的，因为它们提供了大量的功能和性能提升。

**Things to Remember**

- Extension modules are written in C, executing at native speed, and can use the Python API to access nearly all of Python’s powerful features.
- The peculiarities of the Python API, including memory management and error propagation, can be hard to learn and difficult to get right.
- The biggest value of a C extension comes from using the Python API’s protocols and built-in data types, which are difficult to replicate in simple C code.

**注意事项**

- 扩展模块使用C编写，执行速度接近原生速度，并且可以使用Python API访问几乎所有Python的强大功能。
- Python API的特性，包括内存管理和错误传播，学习起来较为困难，也很难正确实现。
- C扩展的最大价值在于使用Python API的协议和内置数据类型，这些在简单的C代码中难以复制。