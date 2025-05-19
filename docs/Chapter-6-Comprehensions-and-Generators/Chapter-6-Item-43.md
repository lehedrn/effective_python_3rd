# Chapter 6: Comprehensions and Generators (推导式与生成器)

## Item 43: Consider Generators Instead of Returning Lists (考虑使用生成器而不是返回列表)

The simplest choice for a function that produces a sequence of results is to return a `list` of items. For example, say that I want to find the index of every word in a string. Here, I accumulate results in a `list` using the `append` method and return it at the end of the function:

对于产生一系列结果的函数来说，最简单的选择是返回一个包含所有项目的`list`。例如，我想找到字符串中每个单词的索引。这里我使用`append`方法在一个`list`中累积结果，并在函数结束时返回它：

```
def index_words(text):
    result = []
    if text:
        result.append(0)
    for index, letter in enumerate(text):
        if letter == " ":
            result.append(index + 1)
    return result
```

This works as expected for some sample input:

这在某些示例输入下可以正常工作：

```
address = "Four score and seven years ago..."
address = "Four score and seven years ago our fathers brought forth on this continent a new nation, conceived in liberty, and dedicated to the proposition that all men are created equal."
result = index_words(address)
print(result[:10])
>>>
[0, 5, 11, 15, 21, 27, 31, 35, 43, 51]
```

There are two problems with the `index_words` function above.

上述`index_words`函数有两个问题。

The first problem is that the code is a bit dense and noisy. Each time a new result is found, I call the `append` method. The method call’s bulk ( `result.append` ) deemphasizes the value being added to the `list` ( `index + 1` ). There is one line for creating the result `list` and another for returning it. While the function body contains ~130 characters (without whitespace), only ~75 characters are important.

第一个问题是代码有些密集和杂乱。每次发现新结果时，我都要调用`append`方法。由于方法调用的冗长（`result.append`）淡化了添加到`list`中的值（`index + 1`）。有一行用于创建结果`list`，另一行用于返回它。虽然函数体包含大约130个字符（不包括空格），但只有大约75个字符是重要的。

A better way to write this function is by using a generator. Generators are functions that use `yield` expressions to incrementally produce outputs. Here, I define a generator version of the function that achieves the same result as before:

编写这个函数更好的方式是使用生成器。生成器是一种使用`yield`表达式逐步产生输出的函数。在这里，我定义了一个生成器版本的函数，实现了相同的结果：

```
def index_words_iter(text):
    if text:
        yield 0
    for index, letter in enumerate(text):
        if letter == " ":
            yield index + 1
```

When called, a generator function does not actually run but instead immediately returns an iterator. With each call to the `next` built-in function, the iterator advances the generator to its next `yield` expression. Each value passed to yield by the generator is returned by the iterator to the caller of next :

调用生成器函数实际上不会运行，而是立即返回一个迭代器。每次调用内置函数`next`，迭代器都会将生成器推进到下一个`yield`表达式。传递给`yield`的每个值都会由迭代器返回给`next`的调用者：

```
it = index_words_iter(address)
print(next(it))
print(next(it))
>>>
0
5
```

The `index_words_iter` function is significantly easier to read because all interactions with the result `list` have been eliminated. Results are passed to `yield` expressions instead. I can easily convert the iterator returned by the generator to a `list` by passing it to the `list` built-in function if necessary (see Item 44: “Consider Generator Expressions for Large List Comprehensions” for how this works):

`index_words_iter`函数明显更易于阅读，因为它消除了对结果`list`的所有交互操作。结果被传递给`yield`表达式。如果需要的话，我可以轻松地通过将其传递给内置函数`list`来将生成器返回的迭代器转换为`list`（参见条目44：“考虑为大型列表推导式使用生成器表达式”了解其工作原理）：

```
result = list(index_words_iter(address))
print(result[:10])
>>>
[0, 5, 11, 15, 21, 27, 31, 35, 43, 51]
```

The second problem with `index_words` is that it requires all results to be stored in the `list` before being returned. For huge inputs, this can cause a program to run out of memory and crash.

第二个问题是`index_words`要求在返回之前将所有结果存储在`list`中。对于巨大的输入，这可能导致程序耗尽内存并崩溃。

In contrast, a generator version of this function can easily be adapted to take inputs of arbitrary length due to its bounded memory requirements. For example, here I define a generator that streams input from a file one line at a time and yields outputs one word at a time:

相比之下，由于内存需求有限，此函数的生成器版本可以轻松适应任意长度的输入。例如，这里我定义了一个生成器，它一次从文件中读取一行输入，并逐词生成输出：

```
def index_file(handle):
    offset = 0
    for line in handle:
        if line:
            yield offset
        for letter in line:
            offset += 1
            if letter == " ":
                yield offset
```

The working memory for this function is limited to the maximum length of one line of input instead of the entire input file’s contents. Here, I show that running the generator on a file input produces the same results (see Item 24: “Consider itertools for Working with Iterators and Generators” for more about the `islice` function):

此函数的工作内存仅限于最长输入行的长度，而不是整个输入文件的内容。这里我展示了在文件输入上运行该生成器会产生相同的结果（有关`islice`函数的更多信息，请参见条目24：“考虑使用itertools处理迭代器和生成器”）：

```
address_lines = """Four score and seven years
ago our fathers brought forth on this
continent a new nation, conceived in liberty,
and dedicated to the proposition that all men
are created equal."""

with open("address.txt", "w") as f:
    f.write(address_lines)

import itertools

with open("address.txt", "r") as f:
    it = index_file(f)
    results = itertools.islice(it, 0, 10)
    print(list(results))

>>>
[0, 5, 11, 15, 21, 27, 31, 35, 43, 51]
```

The only gotcha with defining generators like this is that the callers must be aware that the iterators returned are stateful and can’t be reused (see Item 21: “Be Defensive When Iterating Over Arguments”).

像这样定义生成器唯一的注意事项是调用者必须意识到返回的迭代器是有状态的，不能重复使用（参见条目21：“在迭代参数时要保持防御性”）。

**Things to Remember**
- Using generators can be clearer than the alternative of having a function return a `list` of accumulated results.
- The iterator returned by a generator produces the set of values passed to `yield` expressions within the generator function’s body.
- Generators can produce a sequence of outputs for arbitrarily large inputs because their working memory doesn’t include a materialization of all prior inputs and outputs.

**注意事项**
- 使用生成器比让函数返回累积结果的`list`更清晰。
- 生成器函数体内`yield`表达式传递的值集合由生成器返回的迭代器产生。
- 生成器可以为任意大的输入生成一连串输出，因为其工作内存不包含所有先前输入和输出的具体化表示。