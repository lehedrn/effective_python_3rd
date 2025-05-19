# Chapter 6: Comprehensions and Generators (推导式与生成器)

## Item 45: Compose Multiple Generators with `yield from` (使用 `yield from` 组合多个生成器)

Generators provide a variety of benefits (see Item 43: “Consider Generators Instead of Returning Lists”) and solutions to common problems (see Item 21: “Be Defensive When Iterating Over Arguments”). Generators are so useful that many programs start to look like layers of generators strung together.

生成器提供了各种好处（参见条目43：“考虑使用生成器代替返回列表”）以及解决常见问题的方法（参见条目21：“在迭代参数时保持防御性”）。生成器非常有用，以至于许多程序开始看起来像是一层接一层的生成器串联在一起。

For example, say that I have a graphical program that’s using generators to animate the movement of images onscreen. To get the visual effect I’m looking for, I need the images to move quickly at first, pause temporarily, and then continue moving at a slower pace. Here, I define two generators that yield the expected onscreen deltas for each part of this animation:

例如，假设我有一个图形程序，它使用生成器来实现图像在屏幕上的动画移动。为了达到我想要的视觉效果，我需要图像一开始快速移动，然后暂时暂停，再以较慢的速度继续移动。在这里，我定义了两个生成器，它们会为动画每个部分产生预期的屏幕增量：

```
def move(period, speed):
    for _ in range(period):
        yield speed

def pause(delay):
    for _ in range(delay):
        yield 0
```

To create the final animation, I need to combine `move` and `pause` together to produce a single sequence of onscreen deltas. Here, I do this by calling a generator for each step of the animation, iterating over each generator in turn, and then yielding the deltas from all of them in sequence:

为了创建最终的动画，我需要将 `move` 和 `pause` 结合起来，生成一个单一的、连续的屏幕增量序列。在这里，我通过分别为每个动画步骤调用一个生成器，依次迭代每个生成器，然后按顺序产生所有增量来实现这一点：

```
def animate():
    for delta in move(4, 5.0):
        yield delta
    for delta in pause(3):
        yield delta
    for delta in move(2, 3.0):
        yield delta
```

Now, I can render those deltas onscreen as they’re produced by the single `animation` generator:

现在，我可以将这些增量渲染到屏幕上，因为它们是由单个 `animation` 生成器产生的：

```
def render(delta):
    print(f"Delta: {delta:.1f}")
    # Move the images onscreen

def run(func):
    for delta in func():
        render(delta)

run(animate)
>>>
Delta: 5.0
Delta: 5.0
Delta: 5.0
Delta: 5.0
Delta: 0.0
Delta: 0.0
Delta: 0.0
Delta: 3.0
Delta: 3.0
```

The problem with this code is the repetitive nature of the `animate` function. The redundancy of the `for` statements and `yield` expressions for each generator adds noise and reduces readability. This example includes only three nested generators and it’s already hurting clarity; a complex animation with a dozen phases or more would be extremely difficult to follow.

这段代码的问题在于 `animate` 函数的重复性质。对于每个生成器，`for` 语句和 `yield` 表达式的冗余增加了噪音并降低了可读性。这个例子只包含了三个嵌套生成器，就已经影响了清晰度；具有十几个阶段的复杂动画将极其难以跟踪。

The solution to this problem is to use the `yield from` expression. This advanced generator feature allows you to yield all values from a nested generator before returning control to the parent generator. Here, I reimplement the `animation` function by using `yield from` :

这个问题的解决方案是使用 `yield from` 表达式。这个高级生成器特性允许你在返回控制权给父生成器之前，从嵌套生成器中产出所有的值。在这里，我通过使用 `yield from` 重新实现了 `animation` 函数：

```
def animate_composed():
    yield from move(4, 5.0)
    yield from pause(3)
    yield from move(2, 3.0)

run(animate_composed)
>>>
Delta: 5.0
Delta: 5.0
Delta: 5.0
Delta: 5.0
Delta: 0.0
Delta: 0.0
Delta: 0.0
Delta: 3.0
Delta: 3.0
```

The result is the same as before, but now the code is clearer and more intuitive. `yield from` essentially instructs the Python interpreter to do the nested `for` loop and `yield` expressions for you, resulting in slightly faster execution as well. If you find yourself composing generators, I strongly encourage you to use `yield from` when possible.

结果和以前一样，但现在代码更清晰直观了。`yield from` 实际上指示 Python 解释器为你执行嵌套的 `for` 循环和 `yield` 表达式，从而导致略微更快的执行速度。如果你发现自己在组合生成器，我强烈建议你在可能的情况下使用 `yield from`。

**Things to Remember**
- The `yield from `expression allows you to compose multiple nested generators together into a single combined generator.
- `yield from` eliminates the boilerplate required for manually iterating nested generators and yielding their outputs.

**注意事项**
- `yield from` 表达式允许你将多个嵌套生成器组合成一个单一的综合生成器。
- `yield from` 消除了手动迭代嵌套生成器并产生其输出所需的样板代码。