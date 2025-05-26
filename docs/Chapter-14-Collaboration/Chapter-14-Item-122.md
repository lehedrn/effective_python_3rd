# Chapter 14: Collaboration (协作)

## Item 122: Know How to Break Circular Dependencies (了解如何打破循环依赖)

Inevitably, while you’re collaborating with others, you’ll find a mutual interdependence between modules. It can even happen while you work by yourself on the various parts of a single program.

在与他人协作的过程中，你不可避免地会遇到模块之间的相互依赖。即使你在独立开发一个程序的不同部分时，这种情况也可能发生。

For example, say that I want my GUI application to show a dialog box for choosing where to save a document. The data displayed by the dialog could be specified through arguments to my event handlers. But the dialog also needs to read global state, such as user preferences, to know how to render properly.

例如，假设我想要我的GUI应用程序显示一个用于选择文档保存位置的对话框。对话框中显示的数据可以通过事件处理函数的参数来指定。但是，对话框还需要读取全局状态，例如用户偏好设置，以确定如何正确渲染。

Here, I define a dialog that retrieves the default document save location from global preferences:

这里，我定义了一个从全局偏好设置中获取默认文档保存位置的对话框：

```
# dialog.py
import app

class Dialog:
    def __init__(self, save_dir):
        self.save_dir = save_dir


save_dialog = Dialog(app.prefs.get("save_dir"))

def show():
    print("Showing the dialog!")
```

The problem is that the `app` module that contains the `prefs` object also imports the `dialog` class in order to show the same dialog on program start:

问题是包含 `prefs` 对象的 `app` 模块也需要导入 `dialog` 类以便在程序启动时显示相同的对话框：

```
# app.py
import dialog

class Prefs:
    def get(self, name):
        pass

prefs = Prefs()
dialog.show()
```

It’s a circular dependency. If I try to import the `app` module from my main program like this:

这是一个循环依赖。如果我尝试像这样从主程序导入 `app` 模块：

```
# main.py
import app
```

I get an exception:

我会得到一个异常：

```
$ python3 main.py
Traceback (most recent call last):
 File ".../main.py", line 4, in <module>
 import app
 File ".../app.py", line 4, in <module>
 import dialog
 File ".../dialog.py", line 15, in <module>
 save_dialog = Dialog(app.prefs.get("save_dir"
 ^^^^^^^^^
AttributeError: partially initialized module 'app
attribute 'prefs' (most likely due to a circular 
```

To understand what’s happening here, you need to know how Python’s import machinery works in general (see `https://docs.python.org/3/library/importlib.html` for the full details). When a module is imported, here’s what Python actually does, in depth-first order:

1. Searches for the module in locations from `sys.path`
2. Loads the code from the module and ensures that it compiles
3. Creates a corresponding empty module object
4. Inserts the module into `sys.modules`
5. Runs the code in the module object to define its contents

要理解发生了什么，你需要了解Python的导入机制是如何工作的（完整的细节请参见[https://docs.python.org/3/library/importlib.html](https://docs.python.org/3/library/importlib.html)）。当一个模块被导入时，Python实际上按以下深度优先顺序进行：

1. 在 `sys.path` 中的路径里搜索这个模块
2. 加载模块代码并确保其可以编译
3. 创建相应的空模块对象
4. 将模块插入到 `sys.modules` 中
5. 运行模块中的代码以定义其内容

The problem with a circular dependency is that the attributes of a module aren’t defined until the code for those attributes has executed (after step #5). But the module can be loaded with the `import` statement immediately after it’s inserted into `sys.modules` (after step #4).

循环依赖的问题在于模块的属性直到定义这些属性的代码执行后才会存在（在步骤 #5 后）。 但该模块可以在它被插入到 `sys.modules` 后立即通过 `import` 语句加载（在步骤 #4 后）。

In the example above, the `app` module imports `dialog` before defining anything. Then, the `dialog` module imports `app` . Since `app` still hasn’t finished running——it’s currently importing `dialog`——the `app` module is empty (from step #4). The `AttributeError` is raised (during step #5 for `dialog` ) because the code that defines `prefs` hasn’t run yet (step #5 for `app` isn’t complete).

在上面的例子中，`app` 模块在定义任何东西之前就导入了 `dialog` 。然后，`dialog` 模块又导入了 `app` 。由于 `app` 还未完成运行——它当前正在导入 `dialog` ——所以 `app` 模块是空的（来自步骤 #4）。在 `dialog` 的步骤 #5 中引发 `AttributeError` 是因为定义 `prefs` 的代码还未运行（步骤 #5 对于 `app` 还未完成）。

The best solution to this problem is to refactor the code so that the `prefs` data structure is at the bottom of the dependency tree. Then, both app and `dialog` can import the same utility module and avoid any circular dependencies. But such a clear division isn’t always possible or could require too much refactoring to be worth the effort.

解决这个问题的最佳方案是重构代码，使 `prefs` 数据结构位于依赖树的底部。这样，`app` 和 `dialog` 都可以导入同一个工具模块，从而避免任何循环依赖。不过，这样的明确划分并不总是可行的，或者可能需要大量的重构工作，以至于不值得这样做。

There are three other ways to break circular dependencies.

还有三种其他方法可以打破循环依赖。

### Reordering Imports (重新排序导入)

The first approach is to change the order of imports. For example, if I import the `dialog` module toward the bottom of the `app` module, after the `app` module’s other contents have run, the `AttributeError` goes away:

第一种方法是改变导入的顺序。例如，如果我在 `app` 模块的底部导入 `dialog` 模块，在 `app` 模块的其他内容运行之后，`AttributeError` 就会消失：

```
# app.py
class Prefs:
    def get(self, name):
        pass


prefs = Prefs()

import dialog  # Moved

dialog.show()
```

This works because, when the `dialog` module is loaded late, its recursive import of `app` finds that `app.prefs` has already been defined (step #5 is mostly done for `app` ).

这之所以有效，是因为当 `dialog` 模块被晚些时候加载时，它的递归导入 `app` 发现 `app.prefs` 已经被定义了（步骤 #5 对于 `app` 几乎已经完成）。

Although this avoids the `AttributeError` , it goes against the PEP 8 style guide (see Item 2: “Follow the PEP 8 Style Guide”). The style guide suggests that you always put imports at the top of your Python files. This makes your module’s dependencies clear to new readers of the code. It also ensures that any module you depend on is in scope and available to all the code in your module.

虽然这种方法避免了 `AttributeError` ，但它违反了PEP 8风格指南（参见条目2：“遵循PEP 8风格指南”）。该风格指南建议你始终将导入放在Python文件的顶部。这使得你的模块的依赖关系对代码的新读者来说清晰明了。它还确保了你所依赖的任何模块都在作用域内，并且对你的模块中的所有代码都可用。

Having imports later in a file can be brittle and can cause small changes in the ordering of your code to break the module entirely. I suggest not using import reordering to solve your circular dependency issues.

将导入放在文件后面可能会很脆弱，并可能导致代码顺序的小变化完全破坏模块的功能。我不建议使用导入重排序来解决你的循环依赖问题。

### Import, Configure, Run (导入、配置、运行)

A second solution to the circular imports problem is to have modules minimize side effects at import time. For example, I can have my modules only define functions, classes, and constants. I specifically avoid running any functions at import time. Then, I have each module provide a `configure` function that I can call once all other modules have finished importing. The purpose of `configure` is to prepare each module’s state by accessing the attributes of other modules. I run `configure` after all modules have been imported (step #5 is complete), so all attributes must be defined.

解决循环导入问题的第二个解决方案是让模块在导入时尽量减少副作用。例如，我可以让我模块只定义函数、类和常量。我特别避免在导入时运行任何函数。然后，每个模块提供一个 `configure` 函数，我可以在所有其他模块导入后调用它。`configure` 的目的是通过访问其他模块的属性来准备每个模块的状态。我在所有模块都已导入后（步骤 #5 完成）运行 `configure` ，因此所有的属性必须已经被定义。

Here, I redefine the `dialog` module to only access the `prefs` object when `configure` is called:

在这里，我重新定义了 `dialog` 模块，只有在调用 `configure` 时才访问 `prefs` 对象：

```
# dialog.py
import app

class Dialog:
    def __init__(self):
        pass


save_dialog = Dialog()

def show():
    print("Showing the dialog!")

def configure():
    save_dialog.save_dir = app.prefs.get("save_dir")
```

I also redefine the `app` module to not run any activities on import:

我也重新定义了 `app` 模块，使其在导入时不运行任何活动：

```
import dialog

class Prefs:
    def get(self, name):
        pass


prefs = Prefs()

def configure():
    pass
```

Finally, the `main` module has three distinct phases of execution: import everything, `configure` everything, and run the first activity:

最后，`main` 模块有三个不同的执行阶段：导入所有内容、`configure` 所有内容，以及运行第一个活动：

```
# main.py
import app
import dialog

app.configure()
dialog.configure()

dialog.show()
```

This works well in many situations and enables patterns like dependency injection (see Item 112: “Encapsulate Dependencies to Facilitate Mocking and Testing” for a similar example). But sometimes it can be difficult to structure your code so that an explicit `configure` step is possible. Having two distinct phases within a module can also make your code harder to read because it separates the definition of objects from their configuration.

这在许多情况下效果良好，并且能够支持依赖注入模式（参见条目112：“封装依赖以方便模拟和测试”，其中有一个类似的例子）。但有时很难构建你的代码，以便显式的 `configure` 步骤成为可能。具有两个不同阶段也会使你的代码更难阅读，因为它将对象的定义与其配置分离开来。

### Dynamic Import (动态导入)

The third——and often simplest——solution to the circular imports problem is to use an `import` statement within a function or method. This is called a dynamic import because the module import happens while the program is running, not while the program is first starting up and initializing its modules.

第三种——而且通常最简单——解决循环导入问题的方法是在函数或方法内部使用 `import` 语句。这被称为动态导入，因为模块的导入发生在程序运行期间，而不是程序首次启动并初始化其模块时。

Here, I redefine the `dialog` module to use a dynamic import. The `dialog.show` function imports the `app` module at runtime instead of the `dialog` module importing `app` at initialization time:

在这里，我重新定义了 `dialog` 模块以使用动态导入。`dialog.show` 函数在运行时导入 `app` 模块，而不是在初始化时导入 `app` ：

```
# dialog.py
class Dialog:
    def __init__(self):
        pass


# Using this instead will break things
# save_dialog = Dialog(app.prefs.get('save_dir'))
save_dialog = Dialog()

def show():
    import app  # Dynamic import

    save_dialog.save_dir = app.prefs.get("save_dir")
    print("Showing the dialog!")
```

The `app` module can now be the same as it was in the original example. It imports `dialog` at the top and calls `dialog.show` at the bottom:

现在，`app` 模块可以与原始示例中的相同。它在顶部导入 `dialog` 并在底部调用 `dialog.show` ：

```
# app.py
import dialog

class Prefs:
    def get(self, name):
        pass


prefs = Prefs()
dialog.show()
```

This approach has a similar effect to the import, configure, and run steps from before. The difference is that it requires no structural changes to the way the modules are defined and imported. I’m simply delaying the circular import until the moment you must access the other module. At that point, I can be pretty sure that all other modules have already been initialized (step #5 is complete for everything).

这种方法与之前的导入、配置和运行步骤有类似的效果。区别在于它不需要对模块的定义和导入方式进行结构性更改。我只是将循环导入延迟到了必须访问另一个模块的那一刻。在这一点上，我可以相当确定所有其他模块都已经初始化了（步骤 #5 对所有模块都已完成）。

In general, it’s good to avoid dynamic imports like this. The cost of the `import` statement is not negligible and can be especially bad in tight loops (see Item 98: “Lazy-load Modules with Dynamic Imports to Reduce Startup Time” for an example). By delaying execution, dynamic imports also set you up for surprising failures at runtime, such as `SyntaxError` exceptions long after your program has started running (see Item 108: “Verify Related Behaviors in `TestCase` Subclasses” for how to avoid that). However, these downsides are often better than the alternative of restructuring your entire program.

一般来说，最好避免像这样的动态导入。`import` 语句的成本不容忽视，特别是在紧密循环中可能特别糟糕（参见条目98：“使用动态导入延迟加载模块以减少启动时间”中的示例）。通过延迟执行，动态导入也导致程序在运行时出现令人惊讶的失败，比如在程序开始运行很久之后出现 `SyntaxError` 异常（参见条目108：“在 `TestCase` 子类中验证相关行为”了解如何避免这种情况）。然而，这些缺点往往比重构整个程序的替代方案更好。

**Things to Remember**
- Circular dependencies happen when two modules must call into each other at import time. They can cause your program to crash at startup.
- The best way to break a circular dependency is to refactor mutual dependencies into a separate module at the bottom of the dependency tree.
- Dynamic imports are the simplest solution for breaking a circular dependency between modules while minimizing refactoring and complexity.

**注意事项**
- 循环依赖发生在两个模块在导入时必须互相调用时。它们可能导致你的程序在启动时崩溃。
- 打破循环依赖的最佳方式是将相互依赖重构为位于依赖树底部的单独模块。
- 动态导入是最简单的解决方案，可在最小化重构和复杂性的同时打破模块之间的循环依赖。