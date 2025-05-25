# Chapter 13: Testing and Debugging (测试与调试)

The dynamic behavior of Python and its lack of static type checking by default is both a blessing and a curse (see Item 3: “Never Expect Python to Detect Errors at Compile Time” for details). However, the large numbers of Python programmers out there say it’s worth using because of the productivity gained from the resulting brevity and simplicity. But most people using Python have at least one horror story about about a program encountering a boneheaded error at runtime. One of the worst examples I’ve heard of involved a `SyntaxError` being raised in production as a side effect of a dynamic import (see Item 98: “Lazy-load Modules with Dynamic Imports to Reduce Startup Time” for an example), resulting in a crashed server process. The programmer I know who was hit by this surprising occurrence has since ruled out using Python ever again.

Python的动态行为及其默认缺乏静态类型检查的特性是一把双刃剑（详情请参见第3条：“不要期望Python在编译时检测错误”）。然而，大量的Python程序员表示，由于由此带来的简洁性和简单性，使用Python是值得的。但大多数使用Python的人都至少有一个关于程序在运行时遇到低级错误的恐怖故事。我听过的一个最糟糕的例子涉及到一个`SyntaxError`作为动态导入的副作用（请参见第98条：“使用动态导入延迟加载模块以减少启动时间”）导致服务器进程崩溃。那位遭遇这一意外情况的程序员从此决定不再使用Python。

But I have to wonder, why wasn’t the code more well tested before the program was deployed to production? Compile-time static type safety isn’t everything. You should always test your code, regardless of what language it’s written in. However, I’ll admit that in Python it may be more important to write tests to verify correctness than in other languages. Luckily, the same dynamic features that create these risks also make it extremely easy to write tests for your code and to debug malfunctioning programs. You can use Python’s dynamic nature and easily overridable behaviors to implement tests and ensure that your programs work as expected.

但我不得不问，为什么在程序部署到生产环境之前没有更充分地进行测试？编译时的静态类型安全性并不是万能的。无论使用哪种语言编写代码，都应该始终对其进行测试。不过，我承认，在Python中编写测试可能比其他语言更重要。幸运的是，创造这些风险的相同动态特性也使得为代码编写测试和调试出现故障的程序变得极其容易。您可以利用Python的动态特性和易于覆盖的行为来实现测试，并确保您的程序按预期工作。

1. [Item 108: Verify Related Behaviors in TestCase Subclasses](Chapter-13-Item-108.md) 在TestCase子类中验证相关行为
2. [Item 109: Prefer Integration Tests over Unit Tests](Chapter-13-Item-109.md) 偏好集成测试而非单元测试
3. [Item 110: Isolate Tests From Each Other with setUp, tearDown, setUpModule, and tearDownModule](Chapter-13-Item-110.md) 使用setUp、tearDown、setUpModule和tearDownModule隔离测试
4. [Item 111: Use Mocks to Test Code with Complex Dependencies](Chapter-13-Item-111.md) 使用Mock测试具有复杂依赖的代码
5. [Item 112: Encapsulate Dependencies to Facilitate Mocking and Testing](Chapter-13-Item-112.md) 封装依赖以方便Mock和测试
6. [Item 113: Use assertAlmostEqual to Control Precision in Floating Point Tests](Chapter-13-Item-113.md) 在浮点数测试中使用assertAlmostEqual控制精度
7. [Item 114: Consider Interactive Debugging with pdb](Chapter-13-Item-114.md) 考虑使用pdb进行交互式调试
8. [Item 115: Use tracemalloc to Understand Memory Usage and Leaks](Chapter-13-Item-115.md) 使用tracemalloc了解内存使用和泄漏