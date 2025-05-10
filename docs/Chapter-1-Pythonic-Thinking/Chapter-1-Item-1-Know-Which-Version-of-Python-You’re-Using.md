# Chapter 1: Pythonic Thinking (第一章 用Pythonic方式来思考)

## Item 1: Know Which Version of Python You’re Using (第一条：确认自己所用的Python版本)

Throughout this book, the majority of example code is for Python 3.12 (released in October, 2023). This book also provides some examples relying on features from Python 3.13 (released in October, 2024) to highlight new capabilities that will be more widely available soon. This book does not cover Python 2. Older versions of Python 3 are sometimes mentioned, but only to provide background information.

在本书中，大部分示例代码是针对 Python 3.12（2023年10月发布）编写的。本书还提供了一些依赖于 Python 3.13（2024年10月发布）新特性的示例，以突出展示即将更广泛可用的新功能。本书不涉及 Python 2。旧版的 Python 3 有时会被提及，但仅用于提供背景信息。

Many computer operating systems ship with multiple versions of the standard CPython interpreter preinstalled. However, the default meaning of python on the command line may not be clear. python is usually an alias for python2.7 , but it can sometimes be an alias for even older versions, like python2.6 or python2.5 . To find out exactly which version of Python you’re using, you can use the --version flag:

许多操作系统预装了多个版本的标准 CPython 解释器。然而，在命令行中 python 命令的默认含义可能并不明确。python 通常是指向 python2.7 的别名，但有时也可能是更旧的版本，比如 python2.6 或 python2.5。要确切知道你使用的 Python 版本，可以使用 --version 标志：

```bash
$ python --version
Python 2.7.0
```

On many systems, Python 2 is no longer installed, so the python command will cause an error:

在许多系统上，Python 2 已不再安装，因此 python 命令会导致错误：

```bash
$ python --version
-bash: python: command not found
```

Python 3 is usually available under the name python3:

Python 3 通常可以通过 python3 命令访问：

```bash
$ python3 --version
```
```
>>>
Python 3.8.0
```

To use alternative Python runtimes, such as PyPy (https://www.pypy.org/), to run Python programs, you’ll need to use their specific commands:

如果想使用其他 Python 运行器（如 PyPy (https://www.pypy.org/)）来运行 Python 程序，则需要使用它们的特定命令：

```bash
$ pypy3 --version

```

You can also figure out the version of Python you’re using at runtime by inspecting values in the sys built-in module:

还可以通过检查内置模块 sys 中的值来确定当前使用的 Python 版本：

```python
import sys

print(sys.platform)
print(sys.implementation.name)
print(sys.version_info)
print(sys.version)
```
```
>>>
win32
cpython
sys.version_info(major=3, minor=12, micro=9, releaselevel='final', serial=0)
3.12.9 | packaged by Anaconda, Inc. | (main, Feb  6 2025, 18:49:16) [MSC v.1929 64 bit (AMD64)]
```

For a long time, the Python core developers and community were actively maintaining support for both Python 2 and Python 3. The versions are different in significant ways and have incompatibilities that made porting difficult. The migration from 2 to 3 was an extremely long and painful period that finally came to an end on April 20th, 2020, when Python version 2.7.18 was published. This was the final official release of Python 2. For anyone who still needs security patches and bug fixes for Python 2, the only remaining options are to pay a commercial software vendor for support or do it yourself.

长期以来，Python 核心开发人员和社区一直在积极维护 Python 2 和 Python 3 的支持。这两个版本存在重大差异，并且存在一些兼容性问题，使得迁移变得困难。从 Python 2 向 Python 3 的迁移经历了一个漫长而痛苦的过程，最终于 2020 年 4 月 20 日发布了 Python 2.7.18，这是 Python 2 的最后一个官方版本。对于仍需对 Python 2 进行安全补丁和错误修复的用户来说，唯一剩下的选择是付费购买商业软件供应商的支持或自行处理。

Since then and continuing now, the Python core developers and community are focused on Python version 3. The functionality of the core language, the standard library, and the ecosystem of packages and tools are constantly being improved. Keeping up with all of the changes and innovations happening can be overwhelming. One good way to find out about what’s new is to read the release notes (https://docs.python.org/3/whatsnew/index.html), which highlight additions and changes for each version. There are other websites out there that will also notify you when the community packages you rely on are updated (see Item 116: “Know Where to Find Community-Built Modules”).

自那以后，Python 核心开发人员和社区将精力集中在 Python 3 上。核心语言的功能、标准库以及包和工具的生态系统正在不断改进。跟上所有变化和创新可能会让人感到不知所措。一个了解新增功能的好方法是阅读发行说明 (https://docs.python.org/3/whatsnew/index.html)，这些说明会突出显示每个版本的新增内容和更改内容。此外还有其他网站会在你依赖的社区包更新时通知你（参见第 116 条：“知道在哪里找到社区构建的模块”）。

**Things to Remember**

- Python 3 is the most up-to-date and well-supported version of Python, and you should use it for your projects.
- Be sure that the command-line executable for running Python on your system is the version you expect it to be.
- Python 2 is no longer officially maintained by the core developers.

**注意事项**
- Python 3 是最新且得到良好支持的 Python 版本，你应该在项目中使用它。
- 确保系统上用于运行 Python 的命令行可执行文件是你期望的版本。
- Python 2 不再由核心开发人员进行官方维护