# Chapter 14: Collaboration (协作)

## Item 120: Consider Module-Scoped Code to Configure Deployment Environments (考虑使用模块作用域代码来配置部署环境)

A deployment environment is a configuration in which a program runs. Every program has at least one deployment environment: the production environment. The goal of writing a program in the first place is to put it to work in the production environment and achieve some kind of outcome.

部署环境是指程序运行时所处的配置。每个程序至少有一个部署环境：生产环境。编写程序的首要目标就是将其部署在生产环境中并实现某种结果。

Writing or modifying a program requires being able to run it on the computer you use for developing. The configuration of your development environment might be very different from that of your production environment. For example, you might be using a tiny single-board computer to develop a program that’s meant to run on enormous supercomputers.

编写或修改程序时，需要能够在开发用计算机上运行它。开发环境的配置可能与生产环境有很大不同。例如，您可能正在使用一个微型单板计算机来开发一个旨在运行在巨型超级计算机上的程序。

Tools like `venv` (see Item 117: “Use Virtual Environments for Isolated and Reproducible Dependencies”) make it easy to ensure that all environments have the same Python packages installed. The trouble is that production environments often require many external assumptions that are hard to reproduce in development environments.

像`venv`这样的工具（参见条目117：“使用虚拟环境实现依赖的隔离和可重现性”）使得确保所有环境都安装相同的Python包变得容易。问题在于，生产环境通常需要许多外部假设，这些假设在开发环境中很难复现。

For example, say that I want to run a program in a web server container and give it access to a database. Every time I want to modify my program’s code, I need to run a server container, the database schema must be set up properly, and my program needs the password for access. This is a very high cost if all I’m trying to do is verify that a one-line change to my program works correctly.

例如，假设我想在一个Web服务器容器中运行一个程序，并让它访问数据库。每次我要修改程序的代码时，都需要运行一个服务器容器，正确设置数据库模式，并且我的程序需要密码才能访问。如果我所做的只是一行代码的修改，这种代价是非常高的。

The best way to work around such issues is to override parts of a program at startup time to provide different functionality depending on the deployment environment. For example, I could have two different `__main__` files——one for production and one for development:

解决此类问题的最佳方法是在程序启动时覆盖部分程序，以根据不同的部署环境提供不同的功能。例如，我可以有两个不同的`__main__`文件——一个用于生产环境，另一个用于开发：

```
# dev_main.py
TESTING = True
import db_connection
db = db_connection.Database()
# prod_main.py
TESTING = False
import db_connection
db = db_connection.Database()
```

The only difference between the two files is the value of the `TESTING` constant. Other modules in my program can then import the `__main__` module and use the value of `TESTING` to decide how they define their own attributes.

这两个文件唯一的区别是`TESTING`常量的值。程序中的其他模块可以导入`__main__`模块，并使用`TESTING`的值来决定如何定义自己的属性。

```
# db_connection.py
import __main__

class TestingDatabase:
    pass

class RealDatabase:
    pass

if __main__.TESTING:
    Database = TestingDatabase
else:
    Database = RealDatabase
```

The key behavior to notice here is that code running in module scope—not inside a function or method—is just normal Python code (see Item 98: “Lazy-load Modules with Dynamic Imports to Reduce Startup Time” for details). You can use an `if` statement at the module level to decide how the module will define names. This makes it easy to tailor modules to your various deployment environments. You can avoid having to reproduce costly assumptions like database configurations when they aren’t needed. You can inject local or fake implementations that ease interactive development, or you can use mocks for writing tests (see Item 111: “Use Mocks to Test Code with Complex Dependencies”).

需要注意的关键行为是，在模块作用域中运行的代码——而不是在函数或方法内部的代码——只是普通的Python代码（详见条目98：“使用动态导入延迟加载模块以减少启动时间”）。您可以使用模块级别的`if`语句来决定模块将如何定义名称。这使得针对各种部署环境定制模块变得容易。当不需要某些昂贵的假设时（如数据库配置），可以避免复现它们；可以注入本地或假实现以方便交互式开发；或者可以使用mock进行测试（详见条目111：“使用Mock测试具有复杂依赖性的代码”）。

---

>Note(注意)  
When your deployment environment configuration gets really complicated, you should consider moving it out of Python constants (like `TESTING` ) and into dedicated configuration files. Tools like the `configparser` built-in module let you maintain production configurations separately from code, a distinction that’s crucial for collaborating with an operations team.

当您的部署环境配置变得非常复杂时，应考虑将其从Python常量（如`TESTING`）移出到专用的配置文件中。像`configparser`这样的内置模块可以让您将生产配置与代码分开维护，这对于与运维团队协作至关重要。

---

Module-scoped code can be used for more than dealing with external configurations. For example, if I know that my program must work differently depending on its host platform, I can inspect the `sys` module before defining top-level constructs in a module:

模块作用域代码的用途不仅仅是处理外部配置。例如，如果我知道我的程序必须根据其宿主平台的不同而工作，可以在模块中检查`sys`模块后再定义顶层结构：

```
# db_connection.py
import sys

class Win32Database:
    pass

class PosixDatabase:
    pass

if sys.platform.startswith("win32"):
    Database = Win32Database
else:
    Database = PosixDatabase
```

Similarly, I could use environment variables from `os.environ` to guide my module definitions to match other constraints and requirements of the system.

同样，我可以使用来自`os.environ`的环境变量来指导模块定义，以满足系统的其他约束和要求。

**Things to Remember**

- Programs often need to run in multiple deployment environments that each have unique assumptions and configurations.
- You can tailor a module’s contents to different deployment environments by using normal Python statements in module scope.
- Module contents can be the product of any external condition, including host introspection through the `sys` and `os` modules.

**注意事项**

- 程序通常需要在多个部署环境中运行，每个环境都有其独特的假设和配置。
- 您可以通过在模块作用域中使用普通Python语句来调整模块内容，以适应不同的部署环境。
- 模块内容可以基于任何外部条件生成，包括通过`sys`和`os`模块对宿主系统的自省。