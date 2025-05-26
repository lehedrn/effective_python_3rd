# Chapter 14: Collaboration (协作)

## Item 119: Use Packages to Organize Modules and Provide Stable APIs (使用包来组织模块并提供稳定的API)

As the size of a program’s codebase grows, it’s natural for you to reorganize its structure. You’ll split larger functions into smaller functions. You’ll refactor data structures into helper classes (see Item 29: “Compose Classes Instead of Deeply Nesting Dictionaries, Lists, and Tuples” for an example). You’ll separate functionality into various modules that depend on each other.

随着程序代码库的增大，自然需要对其结构进行重新组织。你会将较大的函数拆分为较小的函数，重构数据结构为辅助类（例如参见条目29：“用组合类代替深层嵌套的字典、列表和元组”）。你还会将功能分离到相互依赖的不同模块中。

At some point, you’ll find yourself with so many modules that you need another layer in your program to make it understandable. For this purpose, Python provides packages. Packages are modules that contain other modules.

在某个时刻，你会发现模块太多以至于需要另一个层次的结构来使其易于理解。为此，Python提供了包。包是包含其他模块的模块。

In most cases, packages are defined by putting an empty file named `__init__.py` into a directory. Once `__init__.py` is present, any other Python files in that directory will be available for import, using a path relative to the directory. For example, imagine that I have the following directory structure in a program:

大多数情况下，包是通过在一个目录中放置一个名为`__init__.py`的空文件来定义的。一旦存在`__init__.py`，该目录中的任何其他Python文件都可以使用相对于该目录的路径进行导入。例如，假设我在一个程序中有以下目录结构：

```
main.py
mypackage/__init__.py
mypackage/models.py
mypackage/utils.py
```

To import the `utils` module, I can use the absolute module name that includes the package directory’s name:

要导入`utils`模块，可以使用包含包目录名称的绝对模块名：

```
# main.py
import mypackage.utils
```

I can also import a child module name relative to its containing package using the `from` clause:

也可以使用`from`子句从包含它的包中相对导入子模块：

```
# main2.py
from mypackage import utils
```

This dotted path pattern for the `import` statement continues when I have package directories nested within other packages (like `import mypackage.foo.bar` and `from mypackage.foo import bar` ).

当你有嵌套在其他包内的包时（如`import mypackage.foo.bar`和`from mypackage.foo import bar`），这种带点路径模式的`import`语句同样适用。

The functionality provided by packages has two primary purposes in Python programs.

Python程序中包的功能主要有两个用途。

### Namespaces (命名空间)

The first use of packages is to help divide your modules into separate namespaces. They enable you to have many modules with the same filename but different absolute paths that are unique. For example, here’s a program that imports attributes from two modules with the same filename, `utils.py` :

包的第一个用途是帮助将你的模块划分为单独的命名空间。它们使你可以拥有许多具有相同文件名但不同绝对路径且唯一的模块。例如，以下是一个从两个同名`utils.py`模块中导入属性的程序：

```
# main.py
from analysis.utils import log_base2_bucket
from frontend.utils import stringify

bucket = stringify(log_base2_bucket(33))
```

This approach breaks when the functions, classes, or submodules defined in packages have the same names. For example, say that I want to use the `inspect` function from both the `analysis.utils` and the `frontend.utils` modules. Importing the attributes directly won’t work because the second import statement will overwrite the value of inspect in the current scope.

当包中定义的函数、类或子模块具有相同名称时，这种方法会失效。例如，假设我想从`analysis.utils`和`frontend.utils`模块中都使用`inspect`函数。直接导入属性将不起作用，因为第二个导入语句会覆盖当前作用域中`inspect`的值。

```
# main2.py
from analysis.utils import inspect
from frontend.utils import inspect # Overwrites
```

The solution is to use the `as` clause of the `import` statement to rename whatever I’ve imported for the current scope:

解决方案是使用`import`语句的`as`子句重命名导入的内容以供当前作用域使用：

```
# main3.py
from analysis.utils import inspect as analysis_inspect
from frontend.utils import inspect as frontend_inspect

value = 33
if analysis_inspect(value) == frontend_inspect(value):
    print("Inspection equal!")
```

The `as` clause can be used to rename anything retrieved with the `import` statement, including entire modules. This facilitates accessing namespaced code and makes its identity clear when you use it.

`as`子句可用于重命名通过`import`语句检索的任何内容，包括整个模块。这有助于访问命名空间代码并在使用时明确其身份。

Another approach for avoiding imported name conflicts is to always access names by their highest unique module name. For the example above, this means I’d use basic `import` statements instead of the `from` clause:

另一种避免导入名称冲突的方法是始终按其最高唯一模块名称访问名称。对于上面的例子，这意味着我将使用基本的`import`语句而不是`from`子句：

```
# main4.py
import analysis.utils
import frontend.utils

value = 33
if analysis.utils.inspect(value) == frontend.utils.inspect(value):
    print("Inspection equal!")
```

This approach allows you to avoid the `as` clause altogether. It also makes it abundantly clear to new readers of the code where each of the similarly named functions is defined.

这种方法完全避免了`as`子句。同时也使得新读者清楚地知道每个相似名称的函数是在哪里定义的。

### Stable APIs (稳定的API)

The second use of packages in Python is to provide strict, stable APIs for external consumers.

Python中包的第二个用途是为外部消费者提供严格的、稳定的API。

When you’re writing an API for wider consumption, such as an open source package (see Item 116: “Know Where to Find Community-Built Modules” for examples), you’ll want to provide stable functionality that doesn’t change between releases. To ensure that happens, it’s important to hide your internal code organization from external users. This way, you can refactor and improve your package’s internal modules without breaking existing users.

当你为更广泛的消费编写API时，比如开源包（例如参见条目116：“知道在哪里找到社区构建的模块”），你需要提供稳定的功能，这些功能在发布之间不会发生变化。为了确保这一点，重要的是隐藏内部代码组织对最终用户的影响。这样，你可以重构和改进包的内部模块而不破坏现有用户。

Python can limit the surface area exposed to API consumers by using the `__all__` special attribute of a module or package. The value of `__all__` is a `list` of every name to export from the module as part of its public API. When consuming code executes from `foo import *`——details on this below——only the attributes in `foo.__all__` will be imported from foo . If `__all__` isn’t present in `foo` , then only public attributes——those without a leading underscore——are imported (see Item 55: “Prefer Public Attributes Over Private Ones” for details about that convention).

Python可以通过使用模块或包的特殊属性`__all__`来限制暴露给API消费者的表面区域。`__all__`的值是一个包含要作为模块公共API一部分导出的所有名称的列表。当消费代码执行`from foo import *`（详情如下）时，只有`foo.__all__`中的属性才会从`foo`中导入。如果`foo`中没有`__all__`，则只会导入公共属性——那些没有前导下划线的属性（有关此约定的详细信息，请参见条目55：“偏好公共属性而非私有属性”）。

For example, say that I want to provide a package for calculating collisions between moving projectiles. Here, I define the `models` module of `mypackage` to contain the representation of projectiles:

例如，假设我想提供一个用于计算移动抛射体碰撞的包。在这里，我定义`mypackage`的`models`模块来包含抛射体的表示：

```
# models.py
__all__ = ["Projectile"]

class Projectile:
    def __init__(self, mass, velocity):
        self.mass = mass
        self.velocity = velocity
```

I also define a `utils` module in `mypackage` to perform operations on the `Projectile` instances, such as simulating collisions between them:

我还定义了一个`mypackage`中的`utils`模块来对`Projectile`实例执行操作，例如模拟它们之间的碰撞：

```
# utils.py
from .models import Projectile

__all__ = ["simulate_collision"]

def _dot_product(a, b):
    pass

def simulate_collision(a, b):
    after_a = Projectile(-a.mass, -a.velocity)
    after_b = Projectile(-b.mass, -b.velocity)
    return after_a, after_b
```

Now, I’d like to provide all of the public parts of this API as a set of attributes that are available on the `mypackage` module. This will allow downstream consumers to always import directly from `mypackage` instead of importing from `mypackage.models` or `mypackage.utils` . This ensures that the API consumer’s code will continue to work even if the internal organization of `mypackage` changes (e.g., `models.py` is deleted).

现在，我希望将这个API的所有公开部分作为一组属性提供，以便可以在`mypackage`模块上访问它们。这将允许下游消费者始终直接从`mypackage`导入，而不是从`mypackage.models`或`mypackage.utils`导入。这确保了即使`mypackage`的内部组织发生变化（例如删除了`models.py`），API消费者的代码仍将继续工作。

To do this with Python packages, you need to modify the `__init__.py` file in the `mypackage` directory. This file is what actually becomes the contents of the `mypackage` module when it’s imported. Thus, you can specify an explicit API for `mypackage` by limiting what you import into `__init__.py` . Since all of my internal modules already specify `__all__` , I can expose the public interface of `mypackage` by simply importing everything from the internal modules and updating `__all__` accordingly:

要在Python包中实现这一点，你需要修改`mypackage`目录中的`__init__.py`文件。这个文件实际上是导入时成为`mypackage`模块内容的文件。因此，你可以通过限制导入到`__init__.py`中的内容来指定`mypackage`的显式API。由于我的所有内部模块都已经指定了`__all__`，我可以简单地通过从内部模块导入一切并相应地更新`__all__`来暴露`mypackage`的公共接口：

```
# __init__.py

__all__ = []
from .models import *

__all__ += models.__all__
from .utils import *

__all__ += utils.__all__
```

Here’s a consumer of the API that directly imports from `mypackage` instead of accessing the inner modules:

这是一个直接从`mypackage`导入而不是访问内部模块的API消费者示例：

```
# api_consumer.py
from mypackage import *
a = Projectile(1.5, 3)
b = Projectile(4, 1.7)
after_a, after_b = simulate_collision(a, b)
```

Notably, internal-only functions like `mypackage.utils._dot_product` will not be available to the API consumer on `mypackage` because they weren’t present in `__all__` . Being omitted from `__all__` also means that they weren’t imported by the `from mypackage import *` statement. The internal-only names are effectively hidden.

值得注意的是，像`mypackage.utils._dot_product`这样的仅内部函数将不会对`mypackage`上的API消费者可用，因为它们未出现在`__all__`中。未包含在`__all__`中也意味着它们未被`from mypackage import *`语句导入。这些仅内部名称实际上被隐藏了。

This whole approach works great when it’s important to provide an explicit, stable API. However, if you’re building an API for use between your own modules, the functionality of `__all__` is probably unnecessary and should be avoided. The namespacing provided by packages is usually enough for a team of programmers to collaborate on large amounts of code they control while maintaining reasonable interface boundaries.

当需要提供一个明确且稳定的API时，这种方法非常有效。然而，如果你正在为自己的模块之间构建API，则`__all__`的功能可能没有必要，应该避免使用。对于程序员团队来说，包提供的命名空间通常足以在维护合理接口边界的同时合作处理大量代码。

---

**Beware of `import *` (注意 `import *`)**

Import statements like `from x import y` are clear because the source of `y` is explicitly the `x` package or module. Wildcard imports like `from foo import *` can also be useful, especially in interactive Python sessions. However, wildcards make code more difficult to understand:

- `from foo import *` hides the source of names from new readers of the code. If a module has multiple `import *` statements, the reader needs to check all of the referenced modules to figure out where a name was defined.
- Names from `import *` statements will overwrite any conflicting names within the containing module. This can lead to strange bugs caused by accidental interactions between your code and names reassigned by successive `import *` statements.

The safest approach is to avoid `import *` in your code and explicitly import names with the `from x import y` style.

像`from x import y`这样的导入语句很清晰，因为`y`的来源明确是`x`包或模块。像`from foo import *`这样的通配符导入也可以很有用，尤其是在交互式Python会话中。但是，通配符会使代码更难理解：

- `from foo import *`隐藏了名称来源的新读者。如果一个模块有多个`import *`语句，读者需要检查所有引用的模块才能弄清楚名称在哪里定义。
- 通配符导入的名称会覆盖包含模块中的任何冲突名称。这可能导致由代码与连续`import *`语句重新分配的名称之间的意外交互引起的奇怪错误。

最安全的方法是在代码中避免使用`import *`，而是使用`from x import y`风格显式导入名称。

---

**Things to Remember**

- Packages in Python are modules that contain other modules. Packages allow you to organize your code into separate, non-conflicting namespaces with unique absolute module names.
- Simple packages are defined by adding an `__init__.py` file to a directory that contains other source files. These files become the child modules of the directory’s package. Package directories may also contain other packages.
- You can provide an explicit API for a module by listing its publicly visible names in its `__all__` special attribute.
- You can hide a package’s internal implementation by only importing public names in the package’s `__init__.py` file or by naming internal￾only members with a leading underscore.
- When collaborating within a single team or on a single codebase, using `__all__` for explicit APIs is probably unnecessary.

**注意事项**

- Python中的包是包含其他模块的模块。包允许你将代码组织成独立、无冲突的命名空间，具有唯一的绝对模块名称。
- 简单的包通过在包含其他源文件的目录中添加一个`__init__.py`文件来定义。这些文件成为目录包的子模块。包目录还可以包含其他包。
- 可以通过在其`__all__`特殊属性中列出模块的公开可见名称来为其提供显式API。
- 可以通过仅在包的`__init__.py`文件中导入公开名称或将仅内部成员命名为带有前导下划线来隐藏包的内部实现。
- 在单个团队或单一代码库内协作时，使用`__all__`进行显式API可能是不必要的。