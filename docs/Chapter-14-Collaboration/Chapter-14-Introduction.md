# Chapter 14: Collaboration (协作)

Python has language features that help you construct well-defined APIs with clear interface boundaries. The Python community has established best practices to maximize the maintainability of code over time. In addition, some standard tools that ship with Python that enable large teams to work together across disparate environments.

Python 拥有帮助你构建定义良好的 API 和清晰接口边界的语言特性。Python 社区已经建立了最佳实践，以最大化代码的可维护性。此外，Python 自带了一些标准工具，使大型团队能够在不同的环境中协同工作。

Collaborating with others on Python programs requires being deliberate in how you write your code. Even if you’re working on your own, chances are you’ll be using code written by someone else via the standard library or open source packages. It’s important to understand the mechanisms that make it easy to collaborate with other Python programmers.

与其他人在 Python 程序上进行协作需要你在编写代码时格外用心。即使你是一个人工作，也可能需要使用其他人通过标准库或开源包编写的代码。理解那些使得与其他 Python 程序员协作变得容易的机制是非常重要的。

1. [Item 116: Know Where to Find Community-Built Modules](Chapter-14-Item-116.md) 了解在哪里找到社区构建的模块
2. [Item 117: Use Virtual Environments for Isolated and Reproducible Dependencies](Chapter-14-Item-117.md) 使用虚拟环境来隔离和重复使用依赖
3. [Item 118: Write Docstrings for Every Function, Class, and Module](Chapter-14-Item-118.md) 为每个函数、类和模块编写 Docstrings
4. [Item 119: Use Packages to Organize Modules and Provide Stable APIs](Chapter-14-Item-119.md) 使用包来组织模块并提供稳定 API
5. [Item 120: Consider Module-Scoped Code to Configure Deployment Environments](Chapter-14-Item-120.md) 考虑模块作用域的代码以配置部署环境
6. [Item 121: Define a Root Exception to Insulate Callers from APIs](Chapter-14-Item-121.md) 定义根异常以隔离调用者
7. [Item 122: Know How to Break Circular Dependencies](Chapter-14-Item-122.md) 了解如何解决循环依赖
8. [Item 123: Consider warnings to Refactor and Migrate Usage](Chapter-14-Item-123.md) 考虑警告以重构和迁移使用
9. [Item 124: Consider Static Analysis via typing to Obviate Bugs](Chapter-14-Item-124.md) 考虑使用 typing 进行静态分析以避免错误
10. [Item 125: Prefer Open Source Projects for Bundling Python Programs over zipimport and zipapp](Chapter-14-Item-125.md) 优先使用开源项目来打包 Python 程序而不是 `zipimport` 和 `zipapp`