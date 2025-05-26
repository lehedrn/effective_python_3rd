# Chapter 14: Collaboration (协作)

## Item 118: Write Docstrings for Every Function, Class, and Module (为每个函数、类和模块编写文档字符串)

Documentation in Python is extremely important because of the dynamic nature of the language. Python provides built-in support for attaching documentation to blocks of code. Unlike with many other languages, the documentation from a program’s source code is directly accessible as the program runs.

Python中的文档非常重要，因为该语言具有动态特性。Python提供了对代码块附加文档的内置支持。与许多其他语言不同，Python程序的源代码中的文档在程序运行时可以直接访问。

For example, you can add documentation by providing a docstring immediately after the `def` statement of a function:

例如，您可以通过在函数的`def`语句之后立即提供一个文档字符串来添加文档：

```
def palindrome(word):
    """Return True if the given word is a palindrome."""
    return word == word[::-1]

assert palindrome("tacocat")
assert not palindrome("banana")
```

You can retrieve the docstring from within the Python program itself by accessing the function’s `__doc__` special attribute:

您可以通过访问函数的`__doc__`特殊属性从Python程序内部检索文档字符串：

```
print(palindrome.__doc__)
>>>
Return True if the given word is a palindrome.
```

You can also use the built-in `pydoc` module from the command line to run a local web server on your computer that hosts all of the Python documentation that’s accessible to your interpreter, including modules that you’ve written:

您还可以使用内置的`pydoc`模块从命令行运行本地Web服务器，托管所有可被解释器访问的Python文档，包括您自己编写的模块：

```
$ python3 -m pydoc -p 1234
Server ready at http://localhost:1234/
Server commands: [b]rowser, [q]uit
server> b
```

Docstrings can be attached to functions, classes, and modules. This connection is part of the process of compiling and running a Python program. Support for docstrings and the `__doc__` attribute has three consequences:

- The accessibility of documentation makes interactive development easier. You can inspect functions, classes, and modules to see their documentation by using the `help` built-in function. This makes the Python interactive interpreter and tools like Jupyter (`https://jupyter.org`) a joy to use while you’re developing algorithms, testing APIs, and writing code snippets.
- A standard way of defining documentation makes it easy to build tools that convert the text into more appealing formats (like HTML). This has led to excellent documentation generation tools for the Python community, such as Sphinx (`https://www.sphinx-doc.org`). It has also enabled services like Read the Docs (`https://readthedocs.org`) that provide free hosting of beautiful-looking documentation for open source Python projects.
- Python’s first-class, accessible, and good-looking documentation encourages people to write more documentation. The members of the Python community have a strong belief in the importance of documentation. There’s an assumption that "good code" also means well-documented code. This means that you can expect most open source Python libraries to have decent documentation.


文档字符串可以附加到函数、类和模块上。这种连接是编译和运行Python程序过程的一部分。对文档字符串和`__doc__`属性的支持有三个后果：

- 文档的可访问性使交互式开发更容易。您可以检查函数、类和模块，通过使用内置的`help`函数查看它们的文档。这使得Python交互式解释器和像Jupyter（`https://jupyter.org`）这样的工具在开发算法、测试API和编写代码片段时非常愉快。
- 定义文档的标准方式使其易于构建将文本转换为更吸引人格式（如HTML）的工具。这导致了Python社区出现优秀的文档生成工具，例如Sphinx (`https://www.sphinx-doc.org`)。这也使得Read the Docs (https://readthedocs.org)等服务能够为开源Python项目提供免费的美观文档托管。
- Python的一流、可访问且美观的文档鼓励人们编写更多文档。Python社区的成员非常重视文档的重要性。有一种观念认为“好代码”也意味着文档良好的代码。这意味着您可以期望大多数开源Python库都有不错的文档。

To participate in this excellent culture of documentation, you need to follow a few guidelines when you write docstrings. The full details are discussed online in PEP 257 (`https://www.python.org/dev/peps/pep-0257/`). There are a few best-practices you should be sure to follow.

为了参与这一优秀的文档文化，您需要在编写文档字符串时遵循一些指南。完整的细节可以在PEP 257中找到（`https://www.python.org/dev/peps/pep-0257/`）。有几个最佳实践您应该确保遵循。

### Documenting Modules (记录模块)

Each module should have a top-level docstring—a string literal that is the first statement in a source file. It should use three double quotes ( `"""` ). The goal of this docstring is to introduce the module and its contents.

每个模块都应该有一个顶层文档字符串——这是源文件中的第一个语句，它应该使用三个双引号 (`"""`)。该文档字符串的目标是介绍模块及其内容。

The first line of the docstring should be a single sentence describing the module’s purpose. The paragraphs that follow should contain the details that all users of the module should know about its operation. The module docstring is also a jumping-off point where you can highlight important classes and functions found in the module.

文档字符串的第一行应该是单句话，描述模块的目的。随后的段落应包含关于其操作的所有用户应知道的重要信息。模块文档字符串也是一个出发点，您可以在其中突出显示模块中的重要类和函数。

Here’s an example of a module docstring:

以下是一个模块文档字符串的示例：

```
# words.py
#!/usr/bin/env python3
"""Library for finding linguistic patterns in words.

Testing how words relate to each other can be tricky sometimes!
This module provides easy ways to determine when words you've
found have special properties.

Available functions:
- palindrome: Determine if a word is a palindrome.
- check_anagram: Determine if two words are anagrams.
...
"""
...
```

If the module is a command-line utility, the module docstring is also a great place to put usage information for running the tool.

如果模块是一个命令行实用程序，模块文档字符串也是放置运行该工具用法信息的好地方。

### Documenting Classes (记录类)

Each class should have a class-level docstring. This largely follows the same pattern as the module-level docstring. The first line is the single-sentence purpose of the class. Paragraphs that follow discuss important details of the class’s operation.

每个类都应该有一个类级文档字符串。这基本上遵循与模块级文档字符串相同的模式。第一行是该类目的的单句话。随后的段落讨论类操作的重要细节。

Important public attributes and methods of the class should be highlighted in the class-level docstring. It should also provide guidance to subclasses on how to properly interact with protected attributes (see Item 55: “Prefer Public Attributes Over Private Ones”) and the superclass’s methods (see Item 53: “Initialize Parent Classes with super ”).

类级文档字符串中应突出显示类的重要公共属性和方法。还应向子类提供如何正确处理受保护属性（参见条目55：“优先选择公共属性而非私有属性”）和超类方法（参见条目53：“使用super初始化父类”）的指导。

Here’s an example of a class docstring:

以下是一个类文档字符串的示例：

```
class Player:
    """Represents a player of the game.

    Subclasses may override the 'tick' method to provide
    custom animations for the player's movement depending
    on their power level, etc.

    Public attributes:
    - power: Unused power-ups (float between 0 and 1).
    - coins: Coins found during the level (integer).
    """
 ...
```

### Documenting Functions (记录函数)

Each public function and method should have a docstring. This follows the same pattern as the docstrings for modules and classes. The first line is a single-sentence description of what the function does. The paragraphs that follow should describe any specific behaviors and the arguments for the function. Any return values should be mentioned. Any exceptions that callers must handle as part of the function’s interface should be explained (see Item 32: “Prefer Raising Exceptions to Returning `None` ” for an example).

每个公共函数和方法都应有文档字符串。这遵循与模块和类的文档字符串相同的模式。第一行是对函数功能的单句话描述。随后的段落应描述任何特定行为和函数参数。应提及任何返回值。应解释调用者必须处理的作为函数接口一部分的异常（参见条目32：“优先引发异常而不是返回None”以获取示例）。

Here’s an example of a function docstring:

以下是一个函数文档字符串的示例：

```
import itertools

def find_anagrams(word, dictionary):
    """Find all anagrams for a word.

    This function only runs as fast as the test for
    membership in the 'dictionary' container.

    Args:
        word: String of the target word.
        dictionary: collections.abc.Container with all
            strings that are known to be actual words.

    Returns:
        List of anagrams that were found. Empty if
        none were found.
    """
    permutations = itertools.permutations(word, len(word))
    possible = ("".join(x) for x in permutations)
    found = {word for word in possible if word in dictionary}
    return list(found)


assert find_anagrams("pancakes", ["scanpeak"]) == ["scanpeak"]
```

There are also some special cases in writing docstrings for functions that are important to know:

- If a function has no arguments and a simple return value, a single sentence description is probably good enough.
- If a function doesn’t return anything, it’s better to leave out any mention of the return value instead of saying "returns None".
- If a function’s interface includes raising exceptions, then your docstring should describe each exception that’s raised and when it’s raised.
- If you don’t expect a function to raise an exception during normal operation, don’t mention that fact.
- If a function accepts a variable number of arguments (see Item 34: “Reduce Visual Noise with Variable Positional Arguments”) or keyword￾arguments (see Item 35: “Provide Optional Behavior with Keyword Arguments”), use `*args` and `**kwargs` in the documented list of arguments to describe their purpose.
- If a function has arguments with default values, those defaults should be mentioned (see Item 36: “Use `None` and Docstrings to Specify Dynamic Default Arguments”).
- If a function is a generator (see Item 43: “Consider Generators Instead of Returning Lists”), its docstring should describe what the generator yields when it’s iterated.
- If a function is an asynchronous coroutine (see Item 75: “Achieve Highly Concurrent I/O with Coroutines”), its docstring should explain when it will stop execution.

在编写函数文档字符串时也有一些特殊情况需要注意：

- 如果一个函数没有参数且返回值简单，则一句描述可能就足够了。
- 如果一个函数不返回任何内容，最好省略对返回值的提及，而不是说"returns None"。
- 如果函数的接口包括引发异常，则您的文档字符串应描述每次异常及其引发时机。
- 如果函数在正常操作期间不预期引发异常，则不要提及该事实。
- 如果函数接受可变数量的参数（参见条目34：“使用变量位置参数减少视觉噪声”）或关键字参数（参见条目35：“使用关键字参数提供可选行为”），请在记录的参数列表中使用`*args`和`**kwargs`来描述其用途。
- 如果函数的参数具有默认值，这些默认值应被提及（参见条目36：“使用`None`和文档字符串指定动态默认参数”）。
- 如果函数是一个生成器（参见条目43：“考虑使用生成器代替返回列表”），其文档字符串应描述迭代时生成器产生什么。
- 如果函数是一个异步协程（参见条目75：“通过协程实现高度并发的I/O”），其文档字符串应解释它何时停止执行。

### Using Docstrings and Type Annotations (使用文档字符串和类型注解)

Python now supports type annotations for a variety of purposes (see Item 124: “Consider Static Analysis via `typing` to Obviate Bugs” for how to use them). The information they contain may be redundant with typical docstrings. For example, here is the function signature for `find_anagrams` with type annotations applied:

Python现在支持多种用途的类型注解（有关如何使用它们，请参见条目124：“考虑通过`typing`进行静态分析以消除错误”）。它们包含的信息可能与典型的文档字符串重复。例如，以下是应用了类型注解的`find_anagrams`函数签名：

```
from collections.abc import Container

def find_anagrams(word: str, dictionary: Container[str]) -> list[str]:
    return []
```

There is no longer a need to specify in the docstring that the `word` argument is a string, since the type annotation has that information. The same goes for the `dictionary` argument being a `collections.abc.Container` . There’s no reason to mention that the return type will be a `list` , since this fact is clearly annotated as such. And when no anagrams are found, the return value still must be a `list` , so it’s implied that it will be empty; that doesn’t need to be noted in the docstring. Here, I write the same function signature from above along with the docstring that has been shortened accordingly:

不再需要在文档字符串中指定`word`参数是字符串，因为类型注解已包含该信息。同样，`dictionary`参数是`collections.abc.Container`这一点也不需要再提。没有必要提到返回类型将是`list`，因为这个事实显然已被注解。当未找到回文时，返回值仍然是`list`，因此暗示它是空的；不需要在文档字符串中注明。在这里，我编写了上面的相同函数签名以及相应缩短后的文档字符串：

```
from collections.abc import Container

def find_anagrams(word: str, dictionary: Container[str]) -> list[str]:
    """Find all anagrams for a word.

    This function only runs as fast as the test for
    membership in the 'dictionary' container.

    Args:
        word: Target word.
        dictionary: All known actual words.

    Returns:
        Anagrams that were found.
    """
    return []
```

The redundancy between type annotations and docstrings should be similarly avoided for instance fields, class attributes, and methods. It’s best to have type information in only one place so there’s less risk that it will skew from the actual implementation.

类型注解和文档字符串之间的冗余也应该避免出现在实例字段、类属性和方法中。最好只在一个地方拥有类型信息，这样就不会有与实际实现偏离的风险。

**Things to Remember**

- Write documentation for every module, class, method, and function using docstrings. Keep them up-to-date as your code changes.
- For modules: Introduce the contents of the module and any important classes or functions that all users should know about.
- For classes: Document behavior, important attributes, and subclass behavior in the docstring following the `class` statement.
- For functions and methods: Document every argument, returned value, raised exception, and other behaviors in the docstring following the `def` statement.
- If you’re using type annotations, omit the information that’s already present in type annotations from docstrings since it would be redundant to have it in both places.

**注意事项**

- 使用文档字符串为每个模块、类、方法和函数编写文档。随着代码的变化，保持文档的更新。
- 对于模块：介绍模块的内容以及所有用户应了解的重要类或函数。
- 对于类：在`class`语句后面的文档字符串中记录行为、重要属性和子类行为。
- 对于函数和方法：在`def`语句后面的文档字符串中记录每个参数、返回值、引发的异常和其他行为。
- 如果您使用类型注解，请省略文档字符串中已经存在于类型注解中的信息，因为在两个地方存在这些信息是多余的。