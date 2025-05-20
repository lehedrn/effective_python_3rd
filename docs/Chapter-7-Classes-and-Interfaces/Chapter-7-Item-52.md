# Chapter 7: Classes and Interfaces (类与接口)

## Item 52: Use `@classmethod` Polymorphism to Construct Objects Generically (使用 `@classmethod` 多态来通用地构造对象)

In Python, not only do objects support polymorphism, but classes do as well. What does that mean, and what is it good for?

在 Python 中，不仅对象支持多态，类也是如此。这意味着什么，又有什么用呢？

Polymorphism enables multiple classes in a hierarchy to implement their own unique versions of a method. This means that many classes can fulfill the same interface or abstract base class while providing different functionality (see Item 49: “Prefer Object-Oriented Polymorphism Over Functions with `isinstance` Checks” and Item 57: “Inherit from `collections.abc` Classes for Custom Container Types” for background).

多态使层次结构中的多个类可以实现自己独特版本的方法。这意味着许多类可以在提供不同功能的同时满足相同的接口或抽象基类（请参见条目49：“优先使用面向对象的多态而不是带有 `isinstance` 检查的函数” 和 条目57：“为自定义容器类型继承 `collections.abc` 类” 以了解背景）。

For example, say that I’m writing a map-reduce implementation, and I want a common class to represent the input data. Here, I define such a class with a `read` method that must be defined by subclasses:

例如，假设我在编写一个 map-reduce 实现，并且我想要一个通用的类来表示输入数据。在这里，我定义了一个这样的类，其中包含一个必须由子类定义的 `read` 方法：

```
class InputData:
    def read(self):
        raise NotImplementedError
```

I also have a concrete subclass of `InputData` that reads data from a file on disk:

我还拥有一个 `InputData` 的具体子类，用于从磁盘上的文件读取数据：

```
class PathInputData(InputData):
    def __init__(self, path):
        super().__init__()
        self.path = path

    def read(self):
        with open(self.path) as f:
            return f.read()
```

I could have any number of `InputData` subclasses, like `PathInputData` , and each of them could implement the standard interface for `read` to return the data to process. Other `InputData` subclasses could read from the network, decompress data transparently, and so on.

我可以有多个 `InputData` 子类，如 `PathInputData`，每个子类都可以实现标准的 `read` 接口以返回要处理的数据。其他 `InputData` 子类可以从网络读取、透明地解压数据等等。

I’d want a similar abstract interface for the map-reduce worker that consumes the input data in a standard way:

我也希望有一个类似的抽象接口用于消费输入数据的标准方式的 map-reduce 工作者：

```
class Worker:
    def __init__(self, input_data):
        self.input_data = input_data
        self.result = None

    def map(self):
        raise NotImplementedError

    def reduce(self, other):
        raise NotImplementedError
```

Here, I define a concrete subclass of `Worker` to implement the specific map-reduce function I want to apply—a simple newline counter:

在这里，我定义了一个 `Worker` 的具体子类以实现我想要应用的特定 map-reduce 函数——一个简单的换行计数器：

```
class LineCountWorker(Worker):
    def map(self):
        data = self.input_data.read()
        self.result = data.count("\n")

    def reduce(self, other):
        self.result += other.result
```

It might look like this implementation is going great, but I’ve reached the biggest hurdle in all of this: What connects all of these pieces? I have a nice set of classes with reasonable interfaces and abstractions, but that’s only useful once the objects are constructed. What component is responsible for building the objects and orchestrating the map-reduce?

看起来这个实现进行得很顺利，但我遇到了最大的障碍：什么连接了所有这些部分？我有一组具有合理接口和抽象的类，但这只有在对象被构建之后才有用。哪个组件负责构建对象并协调 map-reduce？

The simplest approach is to manually build and connect the objects with some helper functions. Here, I list the contents of a directory and construct a `PathInputData` instance for each file it contains:

最简单的方法是使用一些辅助函数手动构建并连接对象。在这里，我列出目录的内容并为其中的每个文件构建一个 `PathInputData` 实例：

```
import os

def generate_inputs(data_dir):
    for name in os.listdir(data_dir):
        yield PathInputData(os.path.join(data_dir, name))
```

Next, I create the `LineCountWorker` instances by using the `InputData` instances returned by `generate_inputs` :

接下来，我使用 `generate_inputs` 返回的 `InputData` 实例创建 `LineCountWorker` 实例：

```
def create_workers(input_list):
    workers = []
    for input_data in input_list:
        workers.append(LineCountWorker(input_data))
    return workers
```

I execute these `Worker` instances by fanning out the `map` step to multiple threads (see Item 68: “Use Threads for Blocking I/O, Avoid for Parallelism” for background). Then, I call `reduce` repeatedly to combine the results into one final value:

通过将 `map` 步骤分散到多个线程中执行这些 `Worker` 实例（有关背景信息，请参见条目68：“对阻塞 I/O 使用线程，避免用于并行”）。然后，我反复调用 `reduce` 将结果合并成一个最终值：

```
from threading import Thread

def execute(workers):
    threads = [Thread(target=w.map) for w in workers]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    first, *rest = workers
    for worker in rest:
        first.reduce(worker)
    return first.result
```

Finally, I connect all of the pieces together in a function that runs each step:

最后，我在一个运行每个步骤的函数中连接所有部分：

```
def mapreduce(data_dir):
    inputs = generate_inputs(data_dir)
    workers = create_workers(inputs)
    return execute(workers)
```

Calling this function with a set of test input files works great:

使用一组测试输入文件调用此函数效果很好：

```
import os
import random

def write_test_files(tmpdir):
    os.makedirs(tmpdir)
    for i in range(100):
        with open(os.path.join(tmpdir, str(i)), "w") as f:
            f.write("\n" * random.randint(0, 100))

tmpdir = "test_inputs"
write_test_files(tmpdir)

result = mapreduce(tmpdir)
print(f"There are {result} lines")

>>>
There are 4360 lines
```

What’s the problem? The huge issue is that the `mapreduce` function is not generic at all. If I wanted to write another `InputData` or `Worker` subclass, I would also have to rewrite the `generate_inputs` , `create_workers` , and `mapreduce` functions to match.

问题是什么？巨大的问题是 `mapreduce` 函数一点也不通用。如果我想编写另一个 `InputData` 或 `Worker` 子类，我还必须重写 `generate_inputs`、`create_workers` 和 `mapreduce` 函数以匹配。

This problem boils down to needing a generic way to construct objects. In other languages, you’d solve this problem with constructor polymorphism, requiring that each `InputData` subclass provides a special constructor that can be used generically by the helper methods that orchestrate the map￾reduce (similar to the factory pattern). The trouble is that Python only allows for the single constructor method ( `__init__` ). It’s unreasonable to require every `InputData` subclass to have a compatible constructor.

这个问题归结为需要一种通用的方式来构造对象。在其他语言中，您可以通过构造函数多态解决这个问题，要求每个 `InputData` 子类提供一个可以被协调 map-reduce 的帮助方法通用使用的特殊构造函数（类似于工厂模式）。问题是 Python 只允许单一的构造方法 `__init__`。要求每个 `InputData` 子类都有兼容的构造函数是不合理的。

The best way to solve this problem is with class method polymorphism. This is exactly like the instance method polymorphism I used for `InputData.read` , except that it’s for whole classes instead of their constructed objects.

解决这个问题的最佳方法是使用类方法多态。这与我用于 `InputData.read` 的实例方法多态完全一样，只是它适用于整个类而不是它们构造的对象。

Let me apply this idea to the map-reduce classes. Here, I extend the `InputData` class with a generic `@classmethod` that’s responsible for creating new `InputData` instances using a common interface:

让我将这个想法应用于 map-reduce 类。在这里，我扩展了 `InputData` 类，添加了一个通用的 `@classmethod`，该方法负责使用公共接口创建新的 `InputData` 实例：

```
class GenericInputData:
    def read(self):
        raise NotImplementedError

    @classmethod
    def generate_inputs(cls, config):
        raise NotImplementedError
```

I have `generate_inputs` take a dictionary with a set of configuration parameters that the `GenericInputData` concrete subclass needs to interpret. Here, I use the `config` to find the directory to list for input files:

我让 `generate_inputs` 接受一个字典，其中包含 `GenericInputData` 具体子类需要解释的一组配置参数。在这里，我使用 `config` 查找要列出输入文件的目录：

```
class PathInputData(GenericInputData):
    def __init__(self, path):
        super().__init__()
        self.path = path

    def read(self):
        with open(self.path) as f:
            return f.read()


    @classmethod
    def generate_inputs(cls, config):
        data_dir = config["data_dir"]
        for name in os.listdir(data_dir):
            yield cls(os.path.join(data_dir, name))
```

Similarly, I can make the `create_workers` helper part of the `GenericWorker` class. Here, I use the `input_class` parameter, which must be a subclass of `GenericInputData` , to generate the necessary inputs:

同样，我可以将 `create_workers` 辅助函数作为 `GenericWorker` 类的一部分。在这里，我使用 `input_class` 参数，它必须是 `GenericInputData` 的子类，以生成必要的输入：

```
class GenericWorker:
    def __init__(self, input_data):
        self.input_data = input_data
        self.result = None

    def map(self):
        raise NotImplementedError

    def reduce(self, other):
        raise NotImplementedError

    @classmethod
    def create_workers(cls, input_class, config):
        workers = []
        for input_data in input_class.generate_inputs(config):
            workers.append(cls(input_data))
        return workers
```

Note that the call to `input_class.generate_inputs` above is the class polymorphism that I’m trying to show. You can also see how `create_workers` calling `cls` provides an alternative way to construct GenericWorker objects besides using the `__init__` method directly.

请注意上面调用的 `input_class.generate_inputs` 是我试图展示的类多态。您还可以看到 `create_workers` 调用 `cls` 提供了一种除了直接使用 `__init__` 方法之外的构造 `GenericWorker` 对象的替代方法。

The effect on my concrete `GenericWorker` subclass is nothing more than changing its parent class:

这对我的具体 `GenericWorker` 子类的影响不过是更改其父类：

```
class LineCountWorker(GenericWorker):  # Changed
    def map(self):
        data = self.input_data.read()
        self.result = data.count("\n")

    def reduce(self, other):
        self.result += other.result
```

Finally, I can rewrite the `mapreduce` function to be completely generic by calling the `create_workers` class method:

最后，我可以通过调用 `create_workers` 类方法重写 `mapreduce` 函数，使其完全通用：

```
def mapreduce(worker_class, input_class, config):
    workers = worker_class.create_workers(input_class, config)
    return execute(workers)
```

Running the new worker on a set of test files produces the same result as the old implementation. The difference is that the `mapreduce` function requires more parameters so that it can operate generically:

在一组测试文件上运行新工作者会产生与旧实现相同的结果。区别在于 `mapreduce` 函数需要更多参数以便能够通用地操作：

```
config = {"data_dir": tmpdir}
result = mapreduce(LineCountWorker, PathInputData
print(f"There are {result} lines")
>>>
There are 4360 lines
```

Now, I can write other `GenericInputData` and `GenericWorker` subclasses as I wish, without having to rewrite any of the glue code.

现在，我可以随意编写其他 `GenericInputData` 和 `GenericWorker` 子类，而无需重写任何粘合代码。

**Things to Remember**
- Python only supports a single constructor per class: the `__init__` method.
- Use `@classmethod` to define alternative constructors for your classes.
- Use class method polymorphism to provide generic ways to build and connect many concrete subclasses.

**注意事项**
- Python 仅支持每个类一个构造函数：`__init__` 方法。
- 使用 `@classmethod` 定义类的替代构造函数。
- 使用类方法多态为构建和连接多个具体子类提供通用的方式。