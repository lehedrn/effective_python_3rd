# Chapter 6: Comprehensions and Generators (推导式与生成器)

## Item 46: Pass Iterators into Generators as Arguments Instead of Calling the send Method (将迭代器作为参数传递给生成器，而不是调用send方法)

`yield` expressions provide generator functions with a simple way to produce an iterable series of output values (see Item 43: “Consider Generators Instead of Returning Lists”). However, this channel appears to be unidirectional: There’s no immediately obvious way to simultaneously stream data in and out of a generator as it runs. Having such bidirectional communication could be valuable in a variety of situations. For example, say that I’m writing a program to transmit signals using a software-defined radio. Here, I use a function to generate an approximation of a sine wave with a given number of points:

`yield` 表达式为生成器函数提供了一种简单的方式来产生一系列可迭代的输出值（参见条目43：“考虑使用生成器代替返回列表”）。然而，这个通道看起来是单向的：在运行时没有明显的方法可以同时从生成器中流式传输数据进和出。这样的双向通信可以在各种情况下很有价值。例如，假设我正在编写一个使用软件定义无线电发送信号的程序。在这里，我使用一个函数来生成具有指定点数的正弦波近似值：

```
import math

def wave(amplitude, steps):
    step_size = 2 * math.pi / steps
    for step in range(steps):
        radians = step * step_size
        fraction = math.sin(radians)
        output = amplitude * fraction
        yield output

```

Now, I can transmit the wave signal at a single specified amplitude by iterating over the `wave` generator:

现在，我可以传输在单个指定幅度下的波形信号，通过迭代 `wave` 生成器：

```
def transmit(output):
    if output is None:
        print(f"Output is None")
    else:
        print(f"Output: {output:>5.1f}")

def run(it):
    for output in it:
        transmit(output)

run(wave(3.0, 8))

>>>
Output: 0.0
Output: 2.1
Output: 3.0
Output: 2.1
Output: 0.0
Output: -2.1
Output: -3.0
Output: -2.1
```

This works fine for producing basic waveforms, but it can’t be used to constantly vary the amplitude of the wave based on a separate input (i.e., as required to broadcast AM radio signals). I need a way to modulate the amplitude on each iteration of the generator.

这对于生成基本波形来说工作得很好，但无法用于根据单独的输入不断变化波的幅度（即广播AM无线电信号所需）。我需要一种方法在生成器每次迭代时调节幅度。

Python generators support the `send` method, which upgrades `yield` expressions into a two-way channel. The `send` method can be used to provide streaming inputs to a generator at the same time it’s yielding outputs. Normally, when iterating a generator, the value of the `yield` expression is `None` :

Python生成器支持`send`方法，它将`yield`表达式升级为双向通道。`send`方法可以用来在生成器产生输出的同时提供流式输入。通常情况下，当迭代生成器时，`yield`表达式的值是`None`：

```
def my_generator():
    received = yield 1
    print(f"{received=}")

it = my_generator()
output = next(it)  # Get first generator output
print(f"{output=}")

try:
    next(it)       # Run generator until it exits
except StopIteration:
    pass
else:
    assert False
    
>>>
output=1
received=None
```

When I call the `send` method instead of iterating the generator with a `for` loop or the `next` built-in function, the supplied parameter becomes the value of the `yield` expression when the generator is resumed. However, when the generator first starts, a `yield` expression has not been encountered yet, so the only valid value for calling send initially is `None` (any other argument would raise an exception at runtime). Here, I run the same generators as above but using `send` instead of `next` to progress them forward:

当我调用`send`方法而不是使用`for`循环或内置的`next`函数来迭代生成器时，提供的参数将成为生成器恢复执行时`yield`表达式的值。但是，当生成器首次启动时，还没有遇到`yield`表达式，因此最初调用`send`时唯一有效的值是`None`（任何其他参数都会在运行时引发异常）。这里，我运行上面相同的生成器，但使用`send`而不是`next`来向前推进它们：

```
it = my_generator()
output = it.send(None)  # Get first generator output
print(f"{output=}")

try:
    it.send("hello!")   # Send value into the generator
except StopIteration:
    pass
else:
    assert False
>>>
output=1
received='hello!'
```

I can take advantage of this behavior in order to modulate the amplitude of the sine wave based on an input signal. First, I need to change the `wave` generator to save the `amplitude` returned by the `yield` expression and use it to calculate the next generated output:

我可以利用这种行为，以基于输入信号调节正弦波的幅度。首先，我需要更改`wave`生成器，保存由`yield`表达式返回的`amplitude`并用它来计算下一个生成的输出：

```
def wave_modulating(steps):
    step_size = 2 * math.pi / steps
    amplitude = yield              # Receive initial amplitude
    for step in range(steps):
        radians = step * step_size
        fraction = math.sin(radians)
        output = amplitude * fraction
        amplitude = yield output   # Receive next amplitude
```

Then, I need to update the `run` function to stream the modulating amplitude into the `wave_modulating` generator on each iteration. The first input to `send` must be `None` , since a `yield` expression would not have occurred within the generator yet:

然后，我需要更新 `run` 函数，在每次迭代时将调节幅度流式传入 `wave_modulating` 生成器。第一次调用`send`必须为`None`，因为在生成器内尚未发生`yield`表达式：
```
def run_modulating(it):
    amplitudes = [None, 7, 7, 7, 2, 2, 2, 2, 10, 10, 10, 10, 10]
    for amplitude in amplitudes:
        output = it.send(amplitude)
        transmit(output)

run_modulating(wave_modulating(12))

>>>
Output is None
Output: 0.0
Output: 3.5
Output: 6.1
Output: 2.0
Output: 1.7
Output: 1.0
Output: 0.0
Output: -5.0
Output: -8.7
Output: -10.0
Output: -8.7
Output: -5.0
```

This works; it properly varies the output amplitude based on the input signal. The first output is `None` , as expected, because a value for the `amplitude` wasn’t received by the generator until after the initial `yield` expression.

这有效；它能正确地根据输入信号改变输出幅度。由于生成器在初始`yield`表达式之后才接收到幅度值，所以第一个输出是`None`。

One problem with this code is that it’s difficult for new readers to understand: Using `yield` on the right side of an assignment statement isn’t intuitive, and it’s hard to see the connection between `yield` and `send` without already knowing the details of this advanced generator feature.

这个问题的一个缺点是代码难以让新读者理解：在赋值语句的右侧使用`yield`并不直观，并且在不了解这个高级生成器功能的情况下很难看到`yield`和`send`之间的联系。

Now, imagine that the program’s requirements get more complicated. Instead of using a simple sine wave as my carrier, I need to use a complex waveform consisting of multiple signals in sequence. One way to implement this behavior is by composing multiple generators together with the yield from expression (see Item 45: “Compose Multiple Generators with yield from ”). Here, I confirm that this works as expected in the simpler case where the amplitude is fixed:

现在，想象一下程序的需求变得更加复杂。不再使用简单的正弦波作为载波，而是需要用多个信号顺序组成的复杂波形。实现此行为的一种方法是使用`yield from`表达式组合多个生成器（参见条目45：“使用yield from组合多个生成器”）。在这里，我确认在幅度固定的情况下按预期工作：

```
def complex_wave():
    yield from wave(7.0, 3)
    yield from wave(2.0, 4)
    yield from wave(10.0, 5)

run(complex_wave())

>>>
Output: 0.0
Output: 6.1
Output: -6.1
Output: 0.0
Output: 2.0
Output: 0.0
Output: -2.0
Output: 0.0
Output: 9.5
Output: 5.9
Output: -5.9
Output: -9.5
```

Given that the `yield from` expression handles the simpler case, you may expect it to also work properly along with the generator `send` method. Here, I try to use `yield from` to compose multiple calls to the `wave_modulating` generator (that uses `send` ):

鉴于`yield from`表达式处理了更简单的情况，您可能期望它在结合生成器`send`方法时也能正常工作。在这里，我尝试使用`yield from`来组合对使用`send`的`wave_modulating`生成器的多次调用：

```
def complex_wave_modulating():
    yield from wave_modulating(3)
    yield from wave_modulating(4)
    yield from wave_modulating(5)
    
run_modulating(complex_wave_modulating())
>>>
Output is None
Output: 0.0
Output: 6.1
Output: -6.1
Output is None
Output: 0.0
Output: 2.0
Output: 0.0
Output: -10.0
Output is None
Output: 0.0
Output: 9.5
Output: 5.9
```

This works to some extent, but the result contains a big surprise: There are many `None` values in the output! Why does this happen? When each `yield from` expression finishes iterating over a nested generator, it moves on to the next one. Each nested generator starts with a bare `yield` expression—one without a value—in order to receive the initial amplitude from a generator `send` method call. This causes the parent generator to output a `None` value when it transitions between child generators.

这在一定程度上是有效的，但结果包含了一个大惊喜：输出中有许多`None`值！为什么会这样？每当每个`yield from`表达式完成对嵌套生成器的迭代后，它会继续下一个。每个嵌套的生成器都以裸露的`yield`表达式开始——没有值，以便从生成器的`send`方法调用接收初始幅度。这导致父生成器在子生成器之间转换时输出一个`None`值。

This means that your assumptions about how the `yield from` and `send` features behave individually will be broken if you try to use them together. Although it’s possible to work around this `None` problem by increasing the complexity of the `run_modulating` function, it’s not worth the trouble. It’s already difficult for new readers of the code to understand how `send` works. This surprising gotcha with `yield from` makes it even worse. My advice is to avoid the `send` method entirely and go with a simpler approach.

这意味着如果您尝试一起使用它们，则关于`yield from`和`send`功能如何单独行为的假设将被打破。尽管可以通过增加`run_modulating`函数的复杂性来解决这个`None`问题，但这不值得。对于新阅读代码的人来说，已经很难理解`send`的工作方式。这个带有`yield from`的意外陷阱使情况更加糟糕。我的建议是完全避免使用`send`方法，选择更简单的方法。

The easiest solution is to pass an iterator into the `wave` function. The iterator should return an input amplitude each time the `next` built-in function is called on it. This arrangement ensures that each generator is progressed in a cascade as inputs and outputs are processed (see Item 44: “Consider Generator Expressions for Large List Comprehensions” and Item 23: “Pass Iterators to any and all for Efficient Short-Circuiting Logic” for other examples):

最简单的解决方案是将一个迭代器传递给`wave`函数。该迭代器应在对其调用内置的`next`函数时返回一个输入幅度。这种安排确保了在处理输入和输出时，每个生成器依次进行（参见条目44：“对于大型列表推导式，请考虑使用生成器表达式”以及条目23：“将迭代器传递给any和all以实现高效的短路逻辑”中的其他示例）：

```
def wave_cascading(amplitude_it, steps):
    step_size = 2 * math.pi / steps
    for step in range(steps):
        radians = step * step_size
        fraction = math.sin(radians)
        amplitude = next(amplitude_it)  # Get next input
        output = amplitude * fraction
        yield output
```

I can pass the same iterator into each of the generator functions that I’m trying to compose together with `yield from` . Iterators are stateful, and thus each of the nested generators picks up where the previous generator left off (see Item 21: “Be Defensive When Iterating Over Arguments” for background):

我可以将相同的迭代器传递给我试图使用`yield from`组合在一起的每个生成器函数。迭代器是有状态的，因此每个嵌套的生成器都会从上一个生成器离开的地方继续（参见条目21：“在迭代参数时要保持防御性”以获取背景信息）：

```
def complex_wave_cascading(amplitude_it):
    yield from wave_cascading(amplitude_it, 3)
    yield from wave_cascading(amplitude_it, 4)
    yield from wave_cascading(amplitude_it, 5)
```

Now, I can run the composed generator by simply passing in an iterator from the `amplitudes list` :

现在，我只需传递来自`amplitudes list`的迭代器即可运行组合生成器：

```
def run_cascading():
    amplitudes = [7, 7, 7, 2, 2, 2, 2, 10, 10, 10, 10, 10]
    it = complex_wave_cascading(iter(amplitudes))  # Supplies iterator
    for amplitude in amplitudes:
        output = next(it)
        transmit(output)

run_cascading()

>>>
Output: 0.0
Output: 6.1
Output: -6.1
Output: 0.0
Output: 2.0
Output: 0.0
Output: -2.0
Output: 0.0
Output: 9.5
Output: 5.9
Output: -5.9
Output: -9.5
```

The best part about this approach is that the input iterator can come from anywhere and could be completely dynamic (e.g., implemented using a generator function or composed; see Item 24: “Consider itertools for Working with Iterators and Generators”). The only downside is that this code assumes that the input generator is thread safe, which may not be the case. If you need to cross thread boundaries, async functions may be a better fit (see Item 77: “Mix Threads and Coroutines to Ease the Transition to asyncio ”).

这种方法最好的部分是输入迭代器可以来自任何地方，并且可以是完全动态的（例如，使用生成器函数实现或组合；参见条目24：“考虑使用itertools来处理迭代器和生成器”）。唯一的缺点是这段代码假定输入生成器是线程安全的，这可能不是事实。如果需要跨越线程边界，异步函数可能是更好的选择（参见条目77：“混合线程和协程以轻松过渡到asyncio”）。

**Things to Remember**
- The `send` method can be used to inject data into a generator by giving the `yield` expression a value that can be assigned to a variable.
- Using `send` with `yield from` expressions may cause surprising behavior, such as None values appearing at unexpected times in the
generator output.
- Providing an input iterator to a set of composed generators is a better approach than using the `send` method, which should be avoided.

**注意事项**
- `send` 方法可用于通过给 `yield` 表达式赋值来向生成器注入数据。
- 将 `send` 和 `yield from` 表达式一起使用可能会导致意外的行为，比如在生成器输出中的意外时刻出现 `None` 值。
- 向一组组合的生成器提供输入迭代器是一种比使用 `send` 方法更好的方法，应避免使用 `send` 方法。