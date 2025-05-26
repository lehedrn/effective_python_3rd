# Chapter 14: Collaboration (协作)

## Item 116: Know Where to Find Community-Built Modules (了解诶在哪里找到社区构建的模块)

Python has a central repository of modules (`https://pypi.org`) that you can install and use in your programs. These modules are built and maintained by people like you: the Python community. When you find yourself facing an unfamiliar challenge, the Python Package Index (PyPI) is a great place to look for code that will get you closer to your goal.

Python 有一个中央模块仓库（`https://pypi.org`），你可以安装并在程序中使用这些模块。这些模块是由像你一样的人——Python 社区成员构建和维护的。当你面对一个不熟悉的挑战时，Python 包索引 (PyPI) 是寻找代码以帮助你更接近目标的好地方。

To use the Package Index, you need to use the command-line tool named pip (a recursive acronym for "pip installs packages"). `pip` can be run with `python3 -m pip` to ensure that packages are installed for the correct version of Python on your system (see Item 1: “Know Which Version of Python You’re Using”). Using `pip` to install a new module is simple. For example, here I install the `numpy` module (see Item 94: “Know When and How to Replace Python with Another Programming Language” for related info):

要使用这个包索引，你需要使用名为 `pip` 的命令行工具（这是一个递归缩写，代表“pip installs packages”）。使用 `python3 -m pip` 可以确保为系统上正确版本的 Python 安装包（参见条目1：“了解你正在使用的 Python 版本”）。使用 pip 安装新模块非常简单。例如，这里我安装了 `numpy` 模块（参见条目94：“了解何时以及如何用其他编程语言替换 Python” 以获取相关信息）：

```
$ python3 -m pip install numpy
Collecting numpy
 Downloading ...
Installing collected packages: numpy
Successfully installed numpy-2.0.0
```

`pip` is best used together with the built-in module `venv` to consistently track sets of packages to install for your projects (see Item 117: “Use Virtual Environments for Isolated and Reproducible Dependencies”). You can also create your own PyPI packages to share with the Python community, or host your own private package repositories for use with `pip` .

`pip` 最好与内置模块 `venv` 一起使用，以便为项目一致地跟踪需要安装的一组包（参见条目117：“使用虚拟环境实现隔离且可重复的依赖项”）。你也可以创建自己的 PyPI 包与 Python 社区共享，或者托管自己的私有包仓库供 `pip` 使用。

Each module in the PyPI has its own software license. Most of the packages, especially the popular ones, have free or open source licenses (see `https://opensource.org` for details). In most cases, these licenses allow you to include a copy of the module with your program (including for end￾user distribution; see Item 125: “Prefer Open Source Projects for Bundling Python Programs Over `zipimport` and `zipapp` ”); when in doubt, talk to a lawyer.

每个在 PyPI 上的模块都有自己的软件许可协议。大多数包，尤其是流行的那些，都采用免费或开源许可协议（详情请参阅 `https://opensource.org`）。在大多数情况下，这些许可允许你在程序中包含模块的一个副本（包括向最终用户分发；参见条目125：“对于打包 Python 程序，优先选择开源项目而非 `zipimport` 和 `zipapp`”)；如有疑问，请咨询律师。

**Things to Remember**
- The Python Package Index (PyPI) contains a wealth of common packages that are built and maintained by the Python community.
- `pip` is the command-line tool you can use to install packages from PyPI.
- The majority of PyPI modules are free and open source software.

**注意事项**
- Python 包索引 (PyPI) 包含大量由 Python 社区构建和维护的常用包。
- `pip` 是你可以用来从 PyPI 安装包的命令行工具。
- 大多数 PyPI 模块都是免费的开源软件。
