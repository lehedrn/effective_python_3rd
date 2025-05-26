# Chapter 13: Testing and Debugging (测试与调试)

## Item 113: Use `assertAlmostEqual` to Control Precision in Floating Point Tests (使用 `assertAlmostEqual` 控制浮点数测试中的精度)

Python's `float` type is a double-precision floating point number (following the IEEE 754 standard). This scheme has limitations (see Item 106: “Use `decimal` When Precision Is Paramount”), but floating point numbers are useful for many purposes and are well supported in Python.

Python 的 `float` 类型是双精度浮点数（遵循 IEEE 754 标准）。这种方案有其局限性（详见第 106 条：“在精度至关重要的情况下使用 `decimal`”），但浮点数在许多用途中都非常有用，并且在 Python 中得到了良好的支持。

Often, it’s important to test mathematical code for boundary conditions and other potential sources of error (see Item 109: “Prefer Integration Tests Over Unit Tests” for details). Unfortunately, writing automated tests involving floating point numbers can be tricky. For example, here I use the `unittest` built-in module to define a test that tries (and fails) to verify the result of the expression `5 / 3` :

通常，在数学代码的测试中，边界条件和其他潜在错误源是非常重要的测试点（详见第 109 条：“优先集成测试而非单元测试”）。然而，编写涉及浮点数的自动化测试可能会很棘手。例如，下面我使用内置的 `unittest` 模块定义了一个试图验证表达式 `5 / 3` 结果的测试，结果失败了：

```
import unittest
    
class MyTestCase(unittest.TestCase):
    def test_equal(self):
        n = 5
        d = 3
        self.assertEqual(1.667, n / d)  # Raises

>>>
Traceback ...
AssertionError: 1.667 != 1.6666666666666667
```

The issue is that in Python the expression `5 / 3` results in a number that can't be represented exactly as a `float` value (which is evidenced by the repeating `6` after the decimal point). The expected value passed to `assertEqual` , `1.667` , isn’t sufficiently precise to exactly match the calculated result (they're different by 0.000333...). Thus, the `assertEqual` method call fails. I could solve this problem by making the expected result more precise, such as the literal `1.6666666666666667`. But in practice, using this level of precision makes numerical tests hard to maintain. The order of operations can produce different results due to rounding behavior. It’s also possible for architectural differences (such as x86 vs. AArch64) to affect the results.

问题是 Python 中的表达式 `5 / 3` 会产生一个无法精确表示为 `float` 值的数字（这可以通过小数点后重复的 `6` 看出）。传递给 `assertEqual` 的预期值 `1.667` 并不足以精确匹配计算结果（它们之间相差约 0.000333...）。因此，`assertEqual` 方法调用失败。我可以通过使预期结果更加精确来解决这个问题，比如使用字面量 `1.6666666666666667`。但在实践中，使用这种级别的精度会使数值测试难以维护。运算顺序的不同可能会由于舍入行为产生不同的结果。此外，架构差异（如 x86 与 AArch64）也可能影响结果。

Here, I show this rounding problem by reordering a calculation in a way that doesn’t look like it should affect the results, but it does (note the last digit):

这里，我通过重新排序一个看起来不应该影响结果的计算来展示这个舍入问题（注意最后一位数字）：

```
print(5 / 3 * 0.1)
print(0.1 * 5 / 3)
>>>
0.16666666666666669
0.16666666666666666
```

To deal with this in automated tests, the `assertAlmostEqual` helper method in the `TestCase` class can be used to do approximate comparisons between floating point numbers. It properly deals with infinity and NaN conditions, and minimizes the introduction of error from rounding. Here, I use this method to verify that the numbers are equal when rounded to two decimal places after the decimal point:

为了在自动化测试中处理这种情况，`TestCase` 类中的 `assertAlmostEqual` 辅助方法可以用于在浮点数之间进行近似比较。它能够正确处理无穷大和 NaN 条件，并最小化由舍入引入的误差。在这里，我使用这种方法验证小数点后两位的数字相等：

```
class MyTestCase2(unittest.TestCase):
    def test_equal(self):
        n = 5
        d = 3
        self.assertAlmostEqual(1.667, n / d, places=2)  # Changed

>>>
.
-------------------------------------------------
Ran 1 test in 0.000s
OK        
```

The `places` parameter for `assertAlmostEqual` works well in verifying numbers with a fractional portion between zero and one. But floating point behavior and repeating decimals might affect larger numbers as well. For example, consider the large difference, in absolute terms, between these two calculations, even though the only change is the addition of `0.001` to one coefficient:

对于 `assertAlmostEqual` 的 `places` 参数，在验证介于零和一之间的分数部分时效果很好。但浮点行为和重复小数可能也会影响较大的数字。例如，请考虑这两个计算之间的巨大差异，尽管唯一的改变是在其中一个系数上增加了 `0.001`：

```
print(1e24 / 1.1e16)
print(1e24 / 1.101e16)
>>>
90909090.9090909
90826521.34423251
```

The difference between these values is approximately 82,569. Depending on the use case, that margin might matter, or it might not. To enable you to express your tolerance for imprecision, you can provide a `delta` argument to the `assertAlmostEqual` helper method. This parameter causes the method to consider the absolute difference between the numbers and only raise an `AssertionError` exception if it’s larger than the `delta` provided.

这些值之间的差大约是 82,569。根据使用场景，这个差异可能重要，也可能不重要。为了让你能表达对不精确性的容忍度，你可以向 `assertAlmostEqual` 辅助方法提供一个 `delta` 参数。此参数会导致方法仅在绝对差值大于提供的 `delta` 时才引发 `AssertionError` 异常。

Here, I use this option to specify a tolerance of 100,000, which is more than the 82,569 difference, allowing both assertions to pass:

在这里，我使用此选项指定了 100,000 的容差，这比 82,569 的差值更大，允许两个断言都通过：

```
class MyTestCase3(unittest.TestCase):
    def test_equal(self):
        a = 1e24 / 1.1e16
        b = 1e24 / 1.101e16
        self.assertAlmostEqual(90.9e6, a, delta=0.1e6)
        self.assertAlmostEqual(90.9e6, b, delta=0.1e6)
```

In some situations, you might need to assert the opposite: that two numbers are not close to each other given a tolerance or number of decimal places. The `TestCase` class also provides the `assertNotAlmostEqual` method to make this easy. To handle more complex use cases when comparing numbers in test code or outside of tests, the math built-in module provides the `isclose` function, which has similar functionality, and more.

在某些情况下，你可能需要断言相反的情况：在给定容差或小数位数的情况下，两个数字彼此并不接近。`TestCase` 类还提供了 `assertNotAlmostEqual` 方法来简化这一操作。要处理在测试代码中或测试之外比较数字的更复杂用例，内置的 `math` 模块提供了 `isclose` 函数，它具有类似的功能，而且更多样化。

**Things to Remember**
- Floating point numbers, especially their fractional part, might change as a result of the order of operations applied due to rounding behavior.
- Testing floating point values with `assertEqual` can lead to flaky tests because it considers the full precision of the numbers being compared.
- The `assertAlmostEqual` and `assertNotAlmostEqual` methods allow you to specify `places` or `delta` parameters to indicate your tolerance for differences when comparing floating point numbers.

**注意事项**

- 浮点数，尤其是其小数部分，可能会因为运算顺序的不同而因舍入行为发生变化。
- 使用 `assertEqual` 测试浮点数值可能导致不可靠的测试，因为它会考虑被比较数字的全部精度。
- `assertAlmostEqual` 和 `assertNotAlmostEqual` 方法允许你指定 `places` 或 `delta` 参数，以表明你在比较浮点数时对差异的容忍度。