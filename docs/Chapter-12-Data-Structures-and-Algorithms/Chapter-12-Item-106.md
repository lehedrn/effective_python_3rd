# Chapter 12: Data Structures and Algorithms (数据结构与算法)

## Item 106: Use `decimal` When Precision Is Paramount (当精度至关重要时使用 `decimal`)

Python is an excellent language for writing code that interacts with numerical data. Python’s integer type can represent values of any practical size. Its double-precision floating point type complies with the IEEE 754 standard. The language also provides a standard complex number type for imaginary values. However, these aren’t enough for every situation.

Python 是一种非常适合编写处理数值数据代码的语言。Python 的整数类型可以表示任何实际大小的值。其双精度浮点类型符合 IEEE 754 标准。该语言还提供了一个标准复数类型用于虚数值。然而，这些在某些情况下并不足够。

For example, say that I want to compute the amount to charge a customer for an international phone call via a portable satellite phone. I know the time in minutes and seconds that the customer was on the phone (say, 3 minutes 42 seconds). I also have a set rate for the cost of calling Antarctica from the United States (say, $1.45/minute). What should the charge be?

例如，假设我想计算客户通过便携式卫星电话拨打国际长途到南极洲的费用（通话时间为3分42秒）。我知道美国拨打南极洲的固定费率（比如每分钟$1.45）。应该向客户收取多少费用？

With floating point math, the computed charge seems reasonable:

使用浮点数学运算，计算出的费用看似合理：

```
rate = 1.45
seconds = 3 * 60 + 42
cost = rate * seconds / 60
print(cost)
>>>
5.364999999999999
```

The result is `0.0001` short of the correct value ( `5.365` ) due to how IEEE 754 floating point numbers are represented. I might want to round up this value to `5.37` to properly cover all costs incurred by the customer. However, due to floating point error, rounding to the nearest whole cent actually reduces the final charge (from `5.364` to `5.36` ) instead of increasing it (from `5.365` to `5.37` ):

由于 IEEE 754 浮点数的表示方式，结果比正确值（`5.365`）少了 `0.0001`。我可能希望将此值向上舍入到 `5.37` 以覆盖客户产生的所有成本。但是，由于浮点误差，四舍五入到最接近的美分实际上会减少最终费用（从 `5.364` 变为 `5.36`）而不是增加它（从 `5.365` 变为 `5.37`）：

```
print(round(cost, 2))
>>>
5.36
```

The solution is to use the `Decimal` class from the `decimal` built-in module. The `Decimal` class provides fixed point math of 28 decimal places by default. It can go even higher, if required. This works around the precision issues in IEEE 754 floating point numbers. The class also gives you more control over rounding behaviors.

解决方案是使用 `decimal` 内置模块中的 `Decimal` 类。默认情况下，`Decimal` 类提供了 28 位小数的定点数学运算。如果需要，它可以更高。这解决了 IEEE 754 浮点数中的精度问题。此类还允许您对舍入行为进行更多控制。

For example, redoing the Antarctica calculation with `Decimal` results in the exact expected charge instead of an approximation:

例如，用 `Decimal` 重新计算南极费用，得到的是精确的预期费用而不是近似值：

```
from decimal import Decimal
rate = Decimal("1.45")
seconds = Decimal(3 * 60 + 42)
cost = rate * seconds / Decimal(60)
print(cost)
>>>
5.365
```

`Decimal` instances can be given starting values in two different ways. The first way is by passing a `str` containing the number to the `Decimal` constructor. This ensures that there is no loss of precision due to the inherent nature of Python floating point values and number constants. The second way is by directly passing a `float` or an `int` instance to the constructor. Here, you can see that the two construction methods result in different behavior:

`Decimal` 实例可以通过两种不同的方法提供起始值。第一种方法是通过将包含数字的 `str` 传递给 `Decimal` 构造函数。这样可以确保不会因为 Python 浮点数值和数字常量的固有特性而丢失精度。第二种方法是直接将 `float` 或 `int` 实例传递给构造函数。在这里，您可以看到这两种构造方法会导致不同的行为：

```
print(Decimal("1.45"))
print(Decimal(1.45))
>>>
1.45
1.44999999999999995559107901499373838305473327636
```

The same problem doesn’t happen if I supply integers to the `Decimal` constructor:

```
print("456")
print(456)
>>>
456
456
```

If you care about exact answers, err on the side of caution and always use the `str` constructor for the `Decimal` type.

如果您关心确切答案，请谨慎行事，并始终为 `Decimal` 类使用 `str` 构造函数。

Getting back to the phone call example, say that I also want to support very short phone calls between places (like Toledo and Detroit) that are much cheaper to connect via an auxiliary cellular connection. Here, I compute the charge for a phone call that was 5 seconds long with a rate of $0.05/minute:

回到电话示例，假设我还想支持非常短的电话呼叫（如托莱多和底特律之间），这些呼叫可以通过辅助蜂窝连接更便宜地连接。这里，我计算一个持续了5秒钟且费率是 $0.05/分钟 的电话呼叫费用：

```
rate = Decimal("0.05")
seconds = Decimal("5")
small_cost = rate * seconds / Decimal(60)
print(small_cost)
>>>
0.004166666666666666666666666667
```

The result is so low that it is decreased to zero when I try to round it to the nearest whole cent. This won’t do!

结果非常低，当我尝试将其舍入到最接近的美分时，它被减到了零。这不行！

```
print(round(small_cost, 2))
>>>
0.00
```

Luckily, the `Decimal` class has a built-in function for rounding to exactly the decimal place needed with the desired rounding behavior. This works for the higher cost case from earlier:

幸运的是，`Decimal` 类有一个内置函数，可以按照所需的小数位和期望的舍入行为进行舍入。这对于前面提到的较高成本案例有效：

```
from decimal import ROUND_UP

rounded = cost.quantize(Decimal("0.01"), rounding=ROUND_UP)
print(f"Rounded {cost} to {rounded}")

>>>
Rounded 5.365 to 5.37
```

Using the `quantize` method this way also properly handles the small usage case for short, cheap phone calls:

以这种方式使用 `quantize` 方法也能正确处理短而便宜的通话情况：

```
rounded = small_cost.quantize(Decimal("0.01"), rounding=ROUND_UP)
print(f"Rounded {small_cost} to {rounded}")
>>>
Rounded 0.004166666666666666666666666667 to 0.01
```

While `Decimal` works great for fixed point numbers, it still has limitations in its precision (e.g., `1/3` will be an approximation). For representing rational numbers with no limit to precision, consider using the `Fraction` class from the `fractions` built-in module.

虽然 `Decimal` 在定点数方面表现很好，但它仍然存在精度限制（例如，`1/3` 将是一个近似值）。为了表示没有精度限制的有理数，请考虑使用 `fractions` 内置模块中的 `Fraction` 类。

**Things to Remember**

- Python has built-in types and classes in modules that can represent practically every type of numerical value.
- The `Decimal` class is ideal for situations that require high precision and control over rounding behavior, such as computations of monetary values.
- Pass `str` instances to the `Decimal` constructor instead of `float` instances if it’s important to compute exact answers and not floating point approximations.

**注意事项**
- Python 拥有内建类型和模块中的类，几乎可以表示所有类型的数值。
- `Decimal` 类适用于需要高精度和对舍入行为进行控制的情况，例如货币值的计算。
- 如果需要计算准确的答案而不是浮点近似值，请将 `str` 实例传递给 `Decimal` 构造函数，而不是 `float` 实例。