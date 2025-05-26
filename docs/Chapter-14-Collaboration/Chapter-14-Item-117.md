# Chapter 14: Collaboration (协作)

## Item 117: Use Virtual Environments for Isolated and Reproducible Dependencies (使用虚拟环境实现隔离和可重复的依赖)

Building larger and more complex programs often leads you to rely on various packages from the Python community (see Item 116: “Know Where to Find Community-Built Modules”). You’ll find yourself running the `python3 -m pip` command-line tool to install packages like `numpy` , `pandas` , and many others.

构建更大、更复杂的程序通常会让你依赖来自 Python 社区的各种包（参见条目 116：“知道在哪里找到社区构建的模块”）。你会发现你自己经常运行 `python3 -m pip` 命令行工具来安装像 `numpy`、`pandas` 等诸多其他包。

The problem is that, by default, `pip` installs new packages in a global location. That causes all Python programs on your system to be affected by these installed modules. In theory, this shouldn’t be an issue. If you install a package and never `import` it, how could it affect your programs?

问题在于，默认情况下，`pip` 将新包安装在一个全局位置。这导致系统上的所有 Python 程序都受到这些已安装模块的影响。理论上，这不应该是个问题。如果你安装了一个包但从未 `import` 它，它怎么会影响你的程序呢？

The trouble comes from transitive dependencies: the packages that the packages you install depend on. For example, you can see what the `Sphinx` package depends on after installing it by asking `pip` :

麻烦来自于传递依赖：即你安装的包所依赖的那些包。例如，你可以通过安装 `Sphinx` 包后询问 `pip` 来查看它的依赖：

```
$ python3 -m pip show Sphinx
Name: Sphinx
Version: 7.4.6
Summary: Python documentation generator
Location: /usr/local/lib/python3.13/site-packages
Requires: alabaster, babel, docutils, imagesize, 
packaging, Pygments, requests, snowballstemmer, s
applehelp, sphinxcontrib-devhelp, sphinxcontrib-h
sphinxcontrib-jsmath, sphinxcontrib-qthelp, sphin
serializinghtml
```

If you install another package like `flask` , you can see that it, too, depends on the `Jinja2` package:

如果你安装另一个像 `flask` 的包，你可以看到它也依赖于 `Jinja2` 包：

```
$ python3 -m pip show flask
Name: Flask
Version: 3.0.3
Summary: A simple framework for building complex 
applications.
Location: /usr/local/lib/python3.13/site-packages
Requires: blinker, click, itsdangerous, Jinja2, W
```

A dependency conflict can arise as `Sphinx` and `flask` diverge over time. Perhaps right now they both require the same version of `Jinja2` and everything is fine. But six months or a year from now, `Jinja2` may release a new version that makes breaking changes to users of the library. If you update your global version of `Jinja2` with `python3 -m pip install --upgrade Jinja2` , you may find that `Sphinx` breaks, while `flask` keeps working.

随着 `Sphinx` 和 `flask` 随着时间推移而发展，可能会出现依赖冲突。也许现在它们都需要相同的 `Jinja2` 版本，一切都没问题。但六个月或一年后，`Jinja2` 可能会发布一个对库用户做出重大更改的新版本。如果你用 `python3 -m pip install --upgrade Jinja2` 更新你的全局 `Jinja2` 版本，你可能会发现 `Sphinx` 崩溃了，而 `flask` 仍然正常工作。

The cause of such breakage is that Python can have only a single global version of a module installed at a time. If one of your installed packages must use the new version and another package must use the old version, your system isn’t going to work properly; this situation is often called dependency hell.

这种破坏的原因是 Python 在任何时候只能安装一个模块的一个全局版本。如果其中一个安装的包必须使用新版本，而另一个包必须使用旧版本，那么你的系统将无法正常工作；这种情况通常被称为依赖地狱。

Such breakage can even happen when package maintainers try their best to preserve API compatibility between releases (see Item 119: “Use Packages to Organize Modules and Provide Stable APIs”). New versions of a library can subtly change behaviors that API-consuming code relies on. Users on a system may upgrade one package to a new version but not others, which could break dependencies. If you’re not careful there’s a constant risk of the ground moving beneath your feet.

即使包维护者尽最大努力在发布之间保持 API 兼容性（参见条目 119：“使用包组织模块并提供稳定的 API”），这种破坏也可能发生。新版本的库可能会微妙地改变 API 使用代码所依赖的行为。用户可能会升级一个包到新版本，但不升级其他包，这可能会破坏依赖关系。如果不小心，脚下地面随时可能变动。

These difficulties are magnified when you collaborate with other developers who do their work on separate computers. It’s best to assume the worst: that the versions of Python and global packages that they have installed on their machines will be slightly different than your own. This can cause frustrating situations such as a codebase working perfectly on one programmer’s machine and being completely broken on another’s.

当你与其他在不同计算机上工作的开发人员协作时，这些困难会被放大。最好假设最坏的情况：他们在机器上安装的 Python 和全局包版本会与你自己的略有不同。这可能导致令人沮丧的情况，例如代码库在一个程序员的机器上完美运行，而在另一个人的机器上完全崩溃。

The solution to all of these problems is using a tool called `venv` , which provides virtual environments. Since Python 3.4, `pip` and the `venv` module have been available by default along with the Python installation (accessible with `python -m venv` ).

解决所有这些问题的方法是使用一个叫做 `venv` 的工具，它提供了虚拟环境。自 Python 3.4 起，`pip` 和 `venv` 模块已经默认随 Python 安装一起提供（可通过 `python -m venv` 访问）。

`venv` allows you to create isolated versions of the Python environment. Using `venv` , you can have many different versions of the same package installed on the same system at the same time without conflicts. This means you can work on many different projects and use many different tools on the same computer.

`venv` 允许你创建隔离的 Python 环境版本。使用 `venv`，你可以在同一台计算机上同时安装许多不同版本的相同包而不产生冲突。这意味着你可以在同一台计算机上处理许多不同的项目和使用许多不同的工具。

`venv` does this by installing explicit versions of packages and their dependencies into completely separate directory structures. This makes it possible to reproduce a Python environment that you know will work with your code. It’s a reliable way to avoid surprising breakages.

`venv` 通过将包及其依赖项的显式版本安装到完全独立的目录结构中来实现这一点。这使得可以重现你知道将与你的代码一起工作的 Python 环境。这是避免意外破坏的可靠方法。

### Using `venv` on the command line (在命令行中使用 `venv`)

Here’s a quick tutorial on how to use `venv` effectively. Before using the tool, it’s important to note the meaning of the `python3` command line on your system. On my computer, `python3` is located in the `/usr/local/bin` directory and evaluates to version 3.13 (see Item 1: “Know Which Version of Python You’re Using”):

以下是一个快速教程，介绍如何有效使用 `venv`。在使用该工具之前，重要的是了解 `python3` 命令行在你的系统中的含义。在我的电脑上，`python3` 位于 `/usr/local/bin` 目录下，并且评估为版本 3.13（参见条目 1：“知道你正在使用的 Python 版本”）：

```
$ which python3
/usr/local/bin/python3
$ python3 --version
Python 3.13.0
```

To demonstrate the setup of my environment, I can test that running a command to import the `numpy` module doesn’t cause an error. This works because I already have the `numpy` package installed as a global module:

为了演示我的环境设置，我可以测试运行一个导入 `numpy` 模块的命令不会导致错误。这是因为我已经将 `numpy` 包作为全局模块安装：

```
$ python3 -c 'import numpy'
$
```

Now, I use `venv` to create a new virtual environment called `myproject` . Each virtual environment must live in its own unique directory. The result of the command is a tree of directories and files that are used to manage the virtual environment:

现在，我使用 `venv` 创建一个名为 `myproject` 的新虚拟环境。每个虚拟环境必须存在于其自己的唯一目录中。该命令的结果是一个用于管理虚拟环境目录树：

```
$ python3 -m venv myproject
$ cd myproject
$ ls
bin include lib pyvenv.cfg
```

To start using the virtual environment, I use the `source` command from my shell on the `bin/activate` script. `activate` modifies all of my environment variables to match the virtual environment. It also updates my command-line prompt to include the virtual environment name (“myproject”) to make it extremely clear what I’m working on:

要开始使用虚拟环境，我在 shell 中对 `bin/activate` 脚本使用 `source` 命令。`activate` 修改我的所有环境变量以匹配虚拟环境。它还会更新我的命令行提示符以包含虚拟环境名称（“myproject”），以使其极其清楚我正在做什么：

```
$ source bin/activate
(myproject)$
```

On Windows the same script is available as:

在 Windows 上，同样的脚本可用作：

```
C:\> myproject\Scripts\activate.bat
(myproject) C:>
```

Or with PowerShell as:

或者使用 PowerShell：

```
PS C:\> myproject\Scripts\activate.ps1
(myproject) PS C:>
```

After activation, you can see that the path to the `python3` command-line tool has moved to within the virtual environment directory:

激活之后，你可以看到 `python3` 命令行工具的路径已经移动到了虚拟环境目录内：

```
(myproject)$ which python3
/tmp/myproject/bin/python3
(myproject)$ ls -l /tmp/myproject/bin/python3
... -> /usr/local/bin/python3
```

This ensures that changes to the outside system will not affect the virtual environment. Even if the outer system upgrades its default `python3` to version 3.14, my virtual environment will still explicitly point to version 3.13.

这确保了外部系统的更改不会影响虚拟环境。即使外部系统将其默认 `python3` 升级到 3.14 版本，我的虚拟环境仍将明确指向 3.13 版本。

The virtual environment I created with `venv` starts with no packages installed except for `pip` and `setuptools` . Trying to use the `numpy` package that was installed as a global module in the outside system will fail because it’s unknown to the virtual environment:

我使用 `venv` 创建的虚拟环境最初除了 `pip` 和 `setuptools` 外没有任何包安装。尝试使用作为全局模块在外部系统中安装的 `numpy` 包将会失败，因为虚拟环境中不知道它：

```
(myproject)$ python3 -c 'import numpy'
Traceback (most recent call last):
 File "<string>", line 1, in <module>
 import numpy
ModuleNotFoundError: No module named 'numpy'
```

I can use the `pip` command-line tool to install the `numpy` module into my virtual environment:

我可以使用 `pip` 命令行工具将 `numpy` 模块安装到我的虚拟环境中：

```
(myproject)$ python3 -m pip install numpy
Collecting numpy
 Downloading ...
Installing collected packages: numpy
Successfully installed numpy-2.0.0
```

Once it’s installed, I can verify that it’s working by using the same test import command:

一旦安装完成，我可以通过使用相同的测试导入命令来验证它是否正常工作：

```
(myproject)$ python3 -c 'import numpy'
(myproject)$
```

When I'm done with a virtual environment and want to go back to my default system, I use the `deactivate` command. This restores my environment to the system defaults, including the location of the `python3` command-line tool:

当我完成虚拟环境的工作并希望回到默认系统时，我使用 `deactivate` 命令。这将恢复我的环境到系统默认值，包括 `python3` 命令行工具的位置：

```
(myproject)$ which python3
/tmp/myproject/bin/python3
(myproject)$ deactivate
$ which python3
/usr/local/bin/python3
```

If I ever want to work in the `myproject` environment again, I can just run `source bin/activate` (or the similar command on Windows) in the directory like before.

如果我想再次在 `myproject` 环境中工作，只需像以前一样在目录中运行 `source bin/activate`（或 Windows 上的类似命令）即可。

### Reproducing Dependencies (重现依赖)

Once you are in a virtual environment, you can continue installing packages in it with `pip` as you need them. Eventually, you might want to copy your environment somewhere else. For example, say that I want to reproduce the development environment from my workstation on a server in a datacenter. Or maybe I want to clone someone else’s environment on my own machine so I can help debug their code.

一旦你进入虚拟环境，你可以继续按需使用 `pip` 安装包。最终，你可能想要复制你的环境到别处。例如，假设我想从我的工作站复制开发环境到数据中心的一台服务器上。或者，我可能想在我自己的机器上克隆别人的环境以便帮助调试他们的代码。

`venv` makes such tasks easy. I can use the `python3 -m pip freeze` command to save all of my explicit package dependencies into a file (which, by convention, is named `requirements.txt` ):

`venv` 使这样的任务变得简单。我可以使用 `python3 -m pip freeze` 命令将所有的显式包依赖保存到一个文件中（按照惯例，这个文件被命名为 `requirements.txt`）：

```
(myproject)$ python3 -m pip freeze > requirements.txt
(myproject)$ cat requirements.txt
certifi==2024.7.4
charset-normalizer==3.3.2
idna==3.7
numpy==2.0.0
requests==2.32.3
urllib3==2.2.2
```

Now, imagine that I'd like to have another virtual environment that matches the `myproject` environment. I can create a new directory as before by using `venv` and `activate` it:

现在，想象一下我希望有一个匹配 `myproject` 环境的另一个虚拟环境。我可以像以前一样通过使用 `venv` 创建一个新目录并激活它：

```
$ python3 -m venv otherproject
$ cd otherproject
$ source bin/activate
(otherproject)$
```

The new environment will have no extra packages installed:

新的环境将没有安装任何额外的包：

```
(otherproject)$ python3 -m pip list
Package Version
------- -------
pip 24.1.1
```

I can install all of the packages from the first environment by running `python3 -m pip install` on the `requirements.txt` that I generated with the `python3 -m pip freeze` command:

我可以通过在生成的 `requirements.txt` 文件上运行 `python3 -m pip install -r` 命令来安装第一个环境中的所有包：

```
(otherproject)$ python3 -m pip install -r
/tmp/myproject/requirements.txt
```

This command cranks along for a little while as it retrieves and installs all of the packages required to reproduce the first environment. When it’s done, I can list the set of installed packages in the second virtual environment and should see the same list of dependencies found in the first virtual environment:

这个命令会稍等片刻，因为它需要检索并安装重现第一个环境所需的所有包。完成后，我可以列出第二个虚拟环境中安装的包列表，并应该看到与第一个虚拟环境中找到的依赖列表相同的内容：

```
(otherproject)$ python3 -m pip list
Package Version
------------------ --------
certifi 2024.7.4
charset-normalizer 3.3.2
idna 3.7
pip 24.1.1
urllib3 2.2.2
```

Using a `requirements.txt` file is ideal for collaborating with others through a revision control system. You can commit changes to your code at the same time you update your list of package dependencies, ensuring that they move in lockstep. However, it’s important to note that the specific version of Python you’re using is not included in the `requirements.txt` file, so that must be managed separately.

通过版本控制系统与他人协作时，使用 `requirements.txt` 文件非常理想。你可以在更新包依赖列表的同时提交代码更改，确保它们同步进行。然而，需要注意的是，你使用的特定版本的 Python 不包含在 `requirements.txt` 文件中，因此必须单独管理。

The gotcha with virtual environments is that moving them breaks everything because all of the paths, like the `python3` command-line tool, are hard-coded to the environment’s install directory. But ultimately this limitation doesn’t matter. The whole purpose of virtual environments is to make it easy to reproduce a setup. Instead of moving a virtual environment directory, just use `python3 -m pip freeze` on the old one, create a new virtual environment somewhere else, and reinstall everything from the `requirements.txt` file.

使用虚拟环境的一个注意事项是，移动它们会使一切都失效，因为所有的路径，如 `python3` 命令行工具，都被硬编码到环境的安装目录中。但最终这一限制并不重要。虚拟环境的全部目的是使重新创建设置变得容易。与其移动虚拟环境目录，不如在旧环境中使用 `python3 -m pip freeze`，然后在别处创建一个新的虚拟环境，并从 `requirements.txt` 文件重新安装所有内容。

**Things to Remember**
- Virtual environments allow you to use `pip` to install many different versions of the same package on the same machine without conflicts.
- Virtual environments are created with `python -m venv` , enabled with `source bin/activate` , and disabled with `deactivate` .
- You can dump all of the requirements of an environment with `python3 -m pip freeze` . You can reproduce an environment by running `python3 -m pip install -r requirements.txt` .

**注意事项**

- 虚拟环境允许你使用 `pip` 在同一台机器上安装多个相同包的不同版本，而不会产生冲突。
- 虚拟环境通过 `python -m venv` 创建，通过 `source bin/activate` 启用，通过 `deactivate` 禁用。
- 你可以通过 `python3 -m pip freeze` 导出环境的所有需求。通过运行 `python3 -m pip install -r requirements.txt` 可以重现一个环境。