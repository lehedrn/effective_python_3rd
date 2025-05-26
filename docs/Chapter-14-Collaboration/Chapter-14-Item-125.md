# Chapter 14: Collaboration (协作)

## Item 125: Prefer Open Source Projects for Bundling Python Programs over `zipimport` and `zipapp` (在打包Python程序时，优先选择开源项目而不是`zipimport`和`zipapp`)

Imagine that you’ve finished building a web application in Python using the `flask` open source project and it’s time to ship it to production for real users (see Item 120: “Consider Module-Scoped Code to Configure Deployment Environments” for background). There are a variety of options for doing this with package managers (see Item 116: “Know Where to Find Community-Built Modules”). However, an often easier way is to simply copy the source code and dependencies to a server (or into a container image).

假设你已经使用`flask`这个开源项目构建了一个Web应用程序，现在需要将其部署到生产环境供真实用户使用（背景信息请参见条目120：“考虑使用模块级代码来配置部署环境”）。使用包管理器有很多种方式可以实现这一点（相关信息请参见条目116：“知道在哪里找到社区构建的模块”）。然而，一种更简单的方法是将源代码和依赖项复制到服务器上（或容器镜像中）。

To that end, I’ve pulled together my application and all of its related modules into a directory—similar to `site-packages` created by tools like `pip` (see Item 117: “Use Virtual Environments for Isolated and Reproducible Dependencies”):

为此，我将我的应用程序及其相关模块整理到了一个目录中——类似于`pip`等工具创建的`site-packages`：

```
$ ls flask_deps
Jinja2-3.1.3.dist-info
MarkupSafe-2.1.5.dist-info
blinker
blinker-1.7.0.dist-info
click
click-8.1.7.dist-info
flask
flask-3.0.2.dist-info
itsdangerous
itsdangerous-2.1.2.dist-info
jinja2
markupsafe
myapp.py
werkzeug
werkzeug-3.0.1.dist-info
```

These dependencies include over 330 files and 56,000 lines of source code, with an uncompressed size of 5.1MB. Copying this many relatively small files to another server can be annoyingly slow. Such transfers can also unexpectedly change important details like file permissions. In the past, a common way to work around these pitfalls was to archive a codebase into a zip file before deployment.

这些依赖项包括超过330个文件和56,000行源代码，未压缩大小为5.1MB。将如此多的小文件复制到另一台服务器可能会非常慢。这样的传输还可能意外更改重要的细节，如文件权限。在过去，常见的解决方法是在部署之前将代码库归档成zip文件。

To make archives like this easier to work with, Python has the `zipimport` built-in module. It enables programs to be decompressed and loaded on the fly from zip files that appear in the `PYTHONPATH` environment variable or `sys.path` list. Here, I create a zip archive of the `flask_deps` directory and then verify it’s working correctly when executed directly from a zip file:

为了使此类存档更容易使用，Python内置了`zipimport`模块。它允许从出现在`PYTHONPATH`环境变量或`sys.path`列表中的zip文件解压并即时加载程序。在这里，我创建了`flask_deps`目录的zip存档，并验证其是否可以从zip文件直接执行：

```
$ cd flask_deps
$ zip -r ../flask_deps.zip *
$ cd ..
$ PYTHONPATH=flask_deps.zip python3 -m flask --app
Endpoint Methods Rule
----------- ------- -----------------------
hello_world GET /
static GET /static/<path:filename>
```

You might expect that there’s a performance penalty in loading Python modules from a zip file due to the CPU overhead of decompression. Here, I measure the startup time loading from a zip archive:

您可能会期望由于解压缩的CPU开销，从zip文件加载Python模块会有性能惩罚。这里，我测量了从zip存档加载的启动时间：

```
$ time PYTHONPATH=flask_deps.zip python3 -m flask
...
real 0m0.123s
user 0m0.097s
sys 0m0.022s
```

And here, I measure startup time loading from plain files on disk:

然后，我测量了从磁盘上的普通文件加载的启动时间：

```
$ time PYTHONPATH=flask_deps python3 -m flask --app
Endpoint Methods Rule
----------- ------- -----------------------
hello_world GET /
static GET /static/<path:filename>
real 0m0.126s
user 0m0.098s
sys 0m0.023s
```

The performance is nearly identical. There are two main reasons for this. First, modern computers have a huge amount of processing power compared to their I/O capacity and memory bandwidth, so the slowdown from additional decompression is often negligible. Second, large file system caches and SSD (solid-state drive) performance can practically hide I/O delays for relatively small amounts of data (see Item 97: “Rely on Precompiled Bytecode and File System Caching to Improve Startup Time” for details). Although the `flask_deps.zip` file is 1.6MB compared to the uncompressed directory size of 5.1MB, the performance difference is effectively zero.

性能几乎相同。这有两个主要原因。首先，现代计算机的处理能力与其I/O容量和内存带宽相比要强大得多，因此额外解压缩带来的减缓通常可以忽略不计。其次，大型文件系统缓存和固态硬盘（SSD）的性能实际上可以隐藏相对小量数据的I/O延迟（详细信息请参见条目97：“依靠预编译字节码和文件系统缓存来提高启动时间”）。虽然`flask_deps.zip`文件的大小为1.6MB，而未压缩目录的大小为5.1MB，但性能差异实际上为零。

One conclusion might be that you should always compress your Python programs into zip files—it seems like there would be no downsides. Python even provides the `zipapp` built-in module for rapidly archiving whole applications because of this benefit. Here, I use this tool to create a compressed, single-file executable (with the `.pyz` suffix) for my web application that’s easy to copy around and interact with:

一个结论可能是你应该总是将你的Python程序压缩成zip文件——看起来这样做没有缺点。由于这种好处，Python甚至提供了`zipapp`内置模块来快速归档整个应用程序。在这里，我使用这个工具创建了一个压缩的单文件可执行文件（带有`.pyz`后缀），便于复制和交互：

```
$ python -m zipapp flask_deps -m "flask.__main__
$ ./flask_deps.pyz --app myapp routes
Endpoint Methods Rule
----------- ------- -----------------------
hello_world GET /
static GET /static/<path:filename>
```

Unfortunately, executing Python code from zip files causes real programs to break in two ways: data file accesses and extension modules.

不幸的是，从zip文件执行Python代码会导致实际程序以两种方式崩溃：数据文件访问和扩展模块。

As an example of the first issue, here I create a zip archive of the Django web framework and try to run a web application that depends on it:

作为第一个问题的例子，我创建了Django Web框架的zip存档，并尝试运行依赖于它的Web应用程序：

```
$ python3 -m compileall django
$ zip -r django.zip Django-5.0.3.dist-info django
$ rm -R Django-5.0.3.dist-info django
$ PYTHONPATH=django.zip python3 django_project/ma
Traceback (most recent call last):
...
OSError: No translation files found for default l
```

This didn’t work because Django is looking for the translations data file next to the source files. In the Django code excerpt below, the value of the `localedir` variable is `".../django.zip/django/conf/locale"` , which is not a directory on the filesystem. When that path is passed to the `gettext` module to load translations, the files can’t be found by the Django library code, causing the `OSError` above:

这并没有奏效，因为Django在其源文件旁边寻找翻译数据文件。在下面的Django代码片段中，`localedir`变量的值是`".../django.zip/django/conf/locale"`，这不是文件系统上的目录。当该路径传递给`gettext`模块以加载翻译时，Django库代码无法找到文件，导致上述`OSError`：

```
# trans_real.py
# Copyright (c) Django Software Foundation and
# individual contributors. All rights reserved.
class DjangoTranslation(gettext_module.GNUTranslations):

    def _init_translation_catalog(self):
        settingsfile = sys.modules[settings.__module__].__file__
        localedir = os.path.join(
            os.path.dirname(settingsfile),
            "locale",
        )
        translation = self._new_gnu_trans(localedir)
        self.merge(translation)
```

Python provides the `pkgutil` built-in module to work around this problem. It intelligently inspects modules to determine how to properly access their data resources even if they’re in zip archives or require a custom module loader. Here, I use `pkgutil` to load the translations file that Django couldn’t find due to the zip archive:

Python提供了`pkgutil`内置模块来解决这个问题。它可以智能地检查模块，以确定如何正确访问它们的数据资源，即使它们位于zip存档中或需要自定义模块加载器也是如此。在这里，我使用`pkgutil`来加载Django因zip存档而找不到的翻译文件：

```
# django_pkgutil.py
import pkgutil

data = pkgutil.get_data(
    "django.conf.locale",
    "en/LC_MESSAGES/django.po",
)
print(data.decode("utf-8"))

>>>
# This file is distributed under the same license
package.
#
msgid ""
msgstr ""
"Project-Id-Version: Django\n"
"Report-Msgid-Bugs-To: \n"
...
```

Few projects actually use `pkgutil`——even an extremely popular project like Django doesn’t. Python programs are most commonly executed as files on disk with their original directory structure. In contrast, other languages compile programs into an executable that is placed into a separate build artifacts directory far from the code. This causes programmers to assume they can’t access the source tree and need to handle data dependencies more explicitly. With Python code, however, the assumption is that the code is nearby, and thus the data files in the source tree must also be nearby. Don’t expect common packages to work when imported from zip archives.

很少有项目实际使用`pkgutil`——即使是像Django这样非常受欢迎的项目也没有。Python程序最常见的是以原始目录结构的形式作为文件在磁盘上执行。相比之下，其他语言会将程序编译成可执行文件，放入单独的构建产物目录中，远离代码。这使得程序员假设他们无法访问源树，因此需要更明确地处理数据依赖关系。然而，对于Python代码而言，假设代码就在附近，因此源树中的数据文件也必须在附近。不要期望从zip存档导入的通用包能够正常工作。

The second issue is that you can’t import native extension modules (see Item 96: “Consider Extension Modules to Maximize Performance and Ergonomics”) from zip archives due to operating system constraints. Here, I show how this breaks for the NumPy package:

第二个问题是由于操作系统限制，您不能从zip存档导入本地扩展模块（有关更多信息，请参见条目96：“考虑使用扩展模块以最大化性能和易用性”）。以下是一个关于NumPy包如何损坏的示例：

```
$ zip -r ./numpy.zip numpy numpy-1.26.4.dist-info
$ rm -R numpy numpy-1.26.4.dist-info
$ PYTHONPATH=numpy.zip python -c 'import numpy'
Traceback (most recent call last):
...
ModuleNotFoundError: No module named
'numpy.core._multiarray_umath'
During handling of the above exception, another e
occurred:
Traceback (most recent call last):
...
ImportError:
IMPORTANT: PLEASE READ THIS FOR ADVICE ON HOW TO 
ISSUE!
Importing the numpy C-extensions failed. This err
for
many reasons, often due to issues with your setup
was
installed.
...
```

Extension modules are extremely valuable and popular because they help Python go faster for CPU-intensive tasks (see Item 96: “Consider Extension Modules to Maximize Performance and Ergonomics”). This is ultimately the biggest deal-breaker for both `zipimport` and `zipapps` .

扩展模块极其有价值且广受欢迎，因为它可以帮助Python在CPU密集型任务中加速（有关更多信息，请参见条目96：“考虑使用扩展模块以最大化性能和易用性”）。最终，这是`zipimport`和`zipapps`的最大障碍。

Fortunately, the Python community has built a variety of open source solutions that are better at deploying Python applications. The Pex tool (`https://github.com/pex-tool/pex`) and a derivative project, Shiv (`https://github.com/linkedin/shiv`), provide similar functionality to `zipapp` but they automatically work around the problems with data files and native modules. For example, here I use Pex to create a single executable file for the same Django web application from earlier——this one actually works:

幸运的是，Python社区已经构建了许多更好的开源解决方案来部署Python应用程序。[Pex工具](https://github.com/pex-tool/pex) 及其衍生项目[Shiv](https://github.com/linkedin/shiv) 提供了与`zipapp`类似的功能，但它们自动绕过了数据文件和本机模块的问题。例如，这里我使用Pex为之前的Django Web应用程序创建了一个单一的可执行文件——这个确实有效：

```
$ pip install -e django_project
$ pex django_project -o myapp.pex
$ ./django_project.pex -m manage check
System check identified no issues (0 silenced).
```

Another alternative is PyInstaller (`https://pyinstaller.org`), which goes even further by bundling the Python executable itself so the user doesn’t need anything else installed on their system in order to run an application. Whatever route you decide to take, be sure to read the documentation carefully and experimentally verify that it’s compatible with the modules you need to use and the assumptions they make about their execution environment.

另一个替代方案是[PyInstaller](https://pyinstaller.org)，它走得更远，通过捆绑Python解释器本身，使用户无需在其系统上安装任何其他内容即可运行应用程序。无论您决定采取哪种路线，都务必仔细阅读文档，并通过实验验证其是否与您需要使用的模块以及它们对执行环境的假设兼容。

**Things to Remember**
- Python has the ability to load modules directly from zip archives, which makes it easier to deploy whole applications as a single file.
- Many common open source Python packages break when imported from a zip archive due to reliance on data files and extension modules.
- The community has built alternatives to Python’s built-in `zipapp` module, such as Pex, which provide the deployment benefits of zip archives without the downsides.

**注意事项**
- Python有能力直接从zip存档加载模块，这使得将整个应用程序作为一个单独的文件进行部署变得更加容易。
- 许多常见的开源Python包在从zip存档导入时会出错，这是因为它们依赖于数据文件和扩展模块。
- 社区已经构建了一些替代Python内置`zipapp`模块的开源项目，例如Pex，这些项目提供了zip存档的部署优势，同时避免了其缺点。