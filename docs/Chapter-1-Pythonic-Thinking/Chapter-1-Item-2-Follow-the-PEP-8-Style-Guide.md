# Chapter 1: Pythonic Thinking (第一章 用Pythonic方式来思考)

## Item 2: Follow the PEP 8 Style Guide (遵循 PEP 8 风格指南)

Python Enhancement Proposal #8, otherwise known as PEP 8, is the style guide for how to format Python code. You are welcome to write Python code any way you want, as long as it has valid syntax. However, using a consistent style makes your code more approachable and easier to read. Sharing a common style with other Python programmers in the larger community facilitates collaboration on projects. But even if you are the only one who will ever read your code, following the style guide will make it easier for you to change things later, and can help you avoid many common errors.

Python 增强提案第 8 号（PEP 8）是关于如何格式化 Python 代码的风格指南。只要你编写的代码语法正确，你可以以任何你喜欢的方式编写 Python 代码。然而，使用一致的编码风格可以使你的代码更易接近和阅读。与更大的 Python 社区中的其他 Python 程序员共享一种通用的风格可以促进项目上的协作。即使将来只有你一个人会阅读你的代码，遵循风格指南将使你在以后更容易修改内容，并且可以帮助你避免许多常见的错误。

PEP 8 provides a wealth of details about how to write clear Python code. It continues to be updated as the Python language evolves. It’s worth reading the whole guide online (https://www.python.org/dev/peps/pep-0008/). Here are a few rules you should be sure to follow.

PEP 8 提供了大量有关如何编写清晰 Python 代码的细节。随着 Python 语言的发展，它也在不断更新。值得在线阅读整个[指南](https://www.python.org/dev/peps/pep-0008/)。以下是几个你应该遵守的基本规则。

**Whitespace**

In Python, whitespace is syntactically significant. Python programmers are especially sensitive to the effects of whitespace on code clarity. Follow these guidelines related to whitespace:

- Use spaces instead of tabs for indentation.
- Use four spaces for each level of syntactically significant indenting.
- Lines should be 79 characters in length or less.
- Continuations of long expressions onto additional lines should be indented by four extra spaces from their normal indentation level.
- In a file, functions and classes should be separated by two blank lines.
- In a class, methods should be separated by one blank line.
- In a dictionary, put no whitespace between each key and colon, and put a single space before the corresponding value if it fits on the same line.
- Put one—and only one—space before and after the = operator in a variable assignment.
- For type annotations, ensure that there is no separation between the variable name and the colon, and use a space before the type information.

**空白字符**

在 Python 中，空白字符在语法上是有意义的。Python 程序员尤其关注空白字符对代码清晰度的影响。请遵循以下与空白字符相关的准则：

- 使用空格而不是制表符进行缩进。
- 每一级语法缩进使用四个空格。
- 每行长度应为 79 个字符或更少。
- 对于长表达式延续到下一行的情况，应该比其正常缩进级别多四个空格。
- 在文件中，函数和类之间应有两个空行。
- 在类中，方法之间应有一个空行。
- 在字典中，每个键与冒号之间不要有空格；如果值在同一行，则在其前面放一个空格。
- 在变量赋值时，在 = 运算符前后各保留一个（只有一个）空格。
- 对于类型注解，在变量名和冒号之间不要有空格，在类型信息前使用一个空格。

**Naming**

PEP 8 suggests unique styles of naming for different parts in the language. These conventions make it easy to distinguish which type corresponds to each name when reading code. Follow these guidelines related to naming:

- Functions, variables, and attributes should be in `lowercase_underscore` format.
- Protected instance attributes should be in `_leading_underscore` format.
- Private instance attributes should be in `__double_leading_underscore` format.
- Classes (including exceptions) should be in `CapitalizedWord` format.
- Module-level constants should be in `ALL_CAPS` format.
- Instance methods in classes should use `self` , which refers to the object, as the name of the first parameter.
- Class methods should use `cls` , which refers to the class, as the name of the first parameter.

**命名**

PEP 8 对不同部分的命名提出了独特的命名风格。这些约定使得在阅读代码时很容易区分每个名称对应的类型。请遵循以下与命名相关的准则：
- 函数、变量和属性应该使用 `lowercase_underscore` 格式。
- 受保护的实例属性应该使用 `_leading_underscore` 格式。
- 私有的实例属性应该使用 `__double_leading_underscore` 格式。
- 类（包括异常）应该使用 `CapitalizedWord` 格式。
- 模块级常量应该使用 `ALL_CAPS` 格式。
- 类中的实例方法应使用 `self`（表示对象）作为第一个参数的名称。
- 类方法应使用 `cls`（表示类）作为第一个参数的名称。

**Expressions and Statements**

The Zen of Python states: "There should be one—and preferably only one-obvious way to do it." PEP 8 attempts to codify this style in its guidance for expressions and statements:

- Use inline negation ( `if a is not b`) instead of negation of positive expressions ( `if not a is b` ).
- Don’t check for empty containers or sequences (like `[]` or `""` ) by comparing the length to zero ( `if len(somelist) == 0` ). Use `if not somelist` and assume that empty values will implicitly evaluate to `False` .
- The same thing goes for non-empty containers or sequences (like `[1]` or `"hi"` ). The statement `if somelist` is implicitly `True` for nonempty values.
- Avoid single-line `if` statements, `for` and `while` loops, and `except` compound statements. Spread these over multiple lines for clarity.
- If you can’t fit an expression on one line, surround it with parentheses and add line breaks and indentation to make it easier to read.
- Prefer surrounding multiline expressions with parentheses over using the `\` line continuation character.

**表达式和语句**

Python编程之禅中提到：“应该有一种——最好是只有一种——明显的方式来完成它。” `PEP8` 力图在其对表达式和语句的指导中体现这一风格：

- 使用内联否定（`if a is not b`），而不是对正向表达式进行否定（`if not a is b`）。
- 不要通过比较容器或序列（如 `[]` 或 `""`）的长度是否为零来检查它们是否为空（如 `if len(somelist) == 0`）。使用 `if not somelist` 并假设空值将隐式地评估为 `False`。
- 对于非空容器或序列也是如此（例如 `[1]` 或 `"hi"`）。语句 `if somelist` 对于非空值来说隐式地为 `True`。
- 避免单行的 `if` 语句、`for` 和 `while` 循环以及 `except` 复合语句。为了清晰起见，请将这些分布在多行上。
- 如果不能在一个行内容纳某个表达式，请将其用括号包围，并添加换行和缩进以使其更易于阅读。
- 相对于使用 `\` 继续字符，优先使用括号包裹多行表达式。

**Imports**

PEP 8 suggests some guidelines for how to import modules and use them in your code:

- Always put `import` statements (including `from x import y`) at the top of a file.
- Always use absolute names for modules when importing them, not names relative to the current module’s own path. For example, to import the `foo` module from within the `bar` package, you should use `from bar import foo` , not just `import foo` .
- If you must do relative imports, use the explicit syntax `from . import foo` .
- Imports should be in sections in the following order: standard library modules, third-party modules, your own modules. Each subsection should have imports in alphabetical order.

**导入**

PEP 8 对如何导入模块并在代码中使用它们提出了一些准则：

- 总是将 `import` 语句（包括 `from x import y`）放在文件顶部。
- 导入模块时始终使用绝对名称，而不是相对于当前模块路径的名称。例如，从 `bar` 包内导入 `foo` 模块时，应使用 `from bar import foo`，而不仅仅是 `import foo`。
- 如果必须做相对导入，请使用显式语法 `from . import foo`。
- 导入应该分为以下顺序的部分：标准库模块、第三方模块、你自己的模块。每个子部分中的导入应按字母顺序排列。

**Automation(自动化)**

If that all seems like a lot to remember, I have good news: The Python community is coalescing around a common tool for automatic PEP 8 formatting: it's called black (https://github.com/psf/black) and it's an official Python Software Foundation project. black provides very few configuration options, which makes it easy for developers working on the same code base to agree on the style of code. Installing and using black is straightforward:

如果以上所有看起来很难记住，我有个好消息：Python 社区正在围绕一个通用的 PEP 8 自动格式化工具达成共识：称为 [black](https://github.com/psf/black) ，它是 Python 软件基金会的官方项目。black 提供了非常少的配置选项，这使得在同一个代码库上工作的开发人员更容易就代码风格达成一致。安装和使用 black 是非常直接的：

```
$ pip install black
$ python -m black example.py
reformatted example.py
All done! 
1 file reformatted.
```

Besides `black` , there are many other community tools to help you improve your source code automatically. Many IDEs and editors include style-checking tools, auto-formatters, and similar plug-ins. One popular code analyzer is `pylint` (https://github.com/pylint-dev/pylint); it helps enforce the PEP 8 style guide and detects many other types of common errors in Python programs (see Item 3: “Never Expect Python to Detect Errors at Compile Time” for more examples).

除了 `black` 之外，还有许多其他社区工具可以帮助你自动改进源代码。许多 IDE 和编辑器包括了样式检查工具、自动格式化工具和类似的插件。一个流行的代码分析器是 [pylint](https://github.com/pylint-dev/pylint)；它帮助执行 `PEP8` 风格指南并检测 `Python` 程序中的许多其他常见错误（更多示例参见条目 3：“永远不要期望 Python 在编译时检测错误”）。


**Things to Remember**

- Always follow the Python Enhancement Proposal #8 (PEP 8) style guide when writing Python code.
- Sharing a common style with the larger Python community facilitates collaboration with others.
- Using a consistent style makes it easier to modify your own code later.
- Community tools like black and pylint can automate compliance with PEP 8, making it easy to keep your source code in good style

**注意事项**
- 编写 `Python` 代码时，始终遵循 `Python` 增强提案第 8 号（`PEP 8`）风格指南。
- 与更强大的 `Python` 社区共享一种共同的风格有助于与其他人的协作。
- 使用一致的风格可以使以后修改自己的代码更容易。
- 社区工具如 `black` 和 `pylint` 可以自动化符合 `PEP 8` 的过程，从而轻松保持良好的源代码风格。