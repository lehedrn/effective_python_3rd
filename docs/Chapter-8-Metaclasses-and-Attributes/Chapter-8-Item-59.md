# Chapter 8: Metaclasses and Attributes (元类和属性)

## Item 59: Consider `@property` Instead of Refactoring Attributes (考虑使用 `@property` 而不是重构属性)

The built-in `@property` decorator makes it easy for simple accesses of an instance’s attributes to act more intelligently (see Item 58: “Use Plain Attributes Instead of Setter and Getter Methods”). One advanced but common use of `@property` is transitioning what was once a simple numerical attribute into an on-the-fly calculation. This is extremely helpful because it lets you migrate all existing usage of a class to have new behaviors without requiring any of the call sites to be rewritten (which is especially important if there’s calling code that you don’t control). `@property` also provides an important stopgap for improving interfaces over time.

内置的 `@property` 装饰器使得实例属性的简单访问能够更加智能（参见条目58：“使用普通属性而不是Setter和Getter方法”）。`@property` 的一个高级但常见的用途是将原本简单的数值属性转换为即时计算。这非常有帮助，因为它允许你迁移类的所有现有用法以具有新的行为，而无需重写任何调用点（如果存在你无法控制的调用代码，则尤其重要）。`@property` 还提供了一个重要的过渡期来随时间改善接口。

For example, say that I want to implement a "leaky bucket", rate-limiting quota system using plain Python objects. Here, the `Bucket` class represents how much quota remains and the duration for which the quota will be available:

例如，假设我想使用普通的Python对象实现一个“漏水桶”限流配额系统。在这里，`Bucket` 类表示剩余的配额以及配额可用的时间长度：

```
from datetime import datetime, timedelta

class Bucket:
    def __init__(self, period):
        self.period_delta = timedelta(seconds=period)
        self.reset_time = datetime.now()
        self.quota = 0

    def __repr__(self):
        return f"Bucket(quota={self.quota})"
```

The leaky bucket algorithm works by ensuring that, whenever the bucket is filled, the amount of quota does not carry over from one period to the next:

漏水桶算法的工作原理是确保每当水桶被填满时，配额不会从一个时间段延续到下一个时间段：

```
def fill(bucket, amount):
    now = datetime.now()
    if (now - bucket.reset_time) > bucket.period_delta:
        bucket.quota = 0
        bucket.reset_time = now
    bucket.quota += amount
```

Each time a quota consumer wants to do something, it must first ensure that it can deduct the amount of quota it needs to use:

每次配额消费者想要做某事时，它必须首先确保可以扣除所需的配额量：

```
def deduct(bucket, amount):
    now = datetime.now()
    if (now - bucket.reset_time) > bucket.period_delta:
        return False  # Bucket hasn't been filled this period
    if bucket.quota - amount < 0:
        return False  # Bucket was filled, but not enough
    bucket.quota -= amount
    return True       # Bucket had enough, quota consumed
```

To use this class, first I fill the bucket up:

要使用此类，首先我需要填充桶：

```
bucket = Bucket(60)
fill(bucket, 100)
print(bucket)
>>>
Bucket(quota=100)
```

Then, I deduct the quota that I need:

然后，我扣除所需的配额：

```
if deduct(bucket, 99):
    print("Had 99 quota")
else:
    print("Not enough for 99 quota")
print(bucket)
>>>
Had 99 quota
Bucket(quota=1)
```

Eventually, I’m prevented from making progress because I try to deduct more quota than is available. In this case, the bucket’s quota level remains unchanged:

最终，由于尝试扣除的配额超过可用配额，我被阻止进行操作。在这种情况下，桶的配额水平保持不变：

```
if deduct(bucket, 3):
    print("Had 3 quota")
else:
    print("Not enough for 3 quota")
print(bucket)
>>>
Not enough for 3 quota
Bucket(quota=1)
```

The problem with this implementation is that I never know what quota level the bucket started with. The quota is deducted over the course of the period until it reaches zero. At that point, `deduct` will always return `False` until the bucket is refilled. When that happens, it would be useful to know whether callers to `deduct` are being blocked because the `Bucket` ran out of quota or because the `Bucket` never had quota during this period in the first place.

此实现的问题在于我永远不知道桶开始时的配额级别。在时间段内配额逐渐减少直到为零。此时，`deduct` 将始终返回 `False`，直到桶重新装满。发生这种情况时，知道对 `deduct` 的调用是否因为 `Bucket` 没有足够的配额或者是因为 `Bucket` 在本周期内根本没有配额会很有用。

To fix this, I can change the class to keep track of the `max_quota` issued in the period and the `quota_consumed` in the same period:

为了解决这个问题，我可以更改类以跟踪期间内发放的最大配额 `max_quota` 和在此期间消耗的配额 `quota_consumed`：

```
class NewBucket:
    def __init__(self, period):
        self.period_delta = timedelta(seconds=period)
        self.reset_time = datetime.now()
        self.max_quota = 0
        self.quota_consumed = 0

    def __repr__(self):
        return (
            f"NewBucket(max_quota={self.max_quota}, "
            f"quota_consumed={self.quota_consumed})"
        )
```

To match the previous interface of the original `Bucket` class, I use a `@property` method to compute the current level of quota on-the-fly using these new attributes:

为了匹配原始 `Bucket` 类的先前接口，我使用 `@property` 方法即时计算当前配额级别：

```
@property
def quota(self):
    return self.max_quota - self.quota_consumed
```

When the `quota` attribute is assigned, I take special action to be compatible with the current usage of the class by the `fill` and `deduct` functions:

当分配 `quota` 属性时，我采取特殊操作以与当前类由 `fill` 和 `deduct` 函数使用的兼容性：

```
@quota.setter
def quota(self, amount):
    delta = self.max_quota - amount
    if amount == 0:
        # Quota being reset for a new period
        self.quota_consumed = 0
        self.max_quota = 0
    elif delta < 0:
        # Quota being filled during the period
        self.max_quota = amount + self.quota_consumed
    else:
        # Quota being consumed during the period
        self.quota_consumed = delta
```

Rerunning the demo code from above produces the same results:

重新运行上面的演示代码会产生相同的结果：

```
bucket = NewBucket(60)
print("Initial", bucket)
fill(bucket, 100)
print("Filled", bucket)
if deduct(bucket, 99):
    print("Had 99 quota")
else:
    print("Not enough for 99 quota")
print("Now", bucket)
if deduct(bucket, 3):
    print("Had 3 quota")
else:
    print("Not enough for 3 quota")
print("Still", bucket)
>>>
Initial NewBucket(max_quota=0, quota_consumed=0)
Filled NewBucket(max_quota=100, quota_consumed=0)
Had 99 quota
Now NewBucket(max_quota=100, quota_consumed=99)
Not enough for 3 quota
Still NewBucket(max_quota=100, quota_consumed=99)
```

The best part is that the code using `Bucket.quota` doesn’t have to change or know that the class has changed. New usage of `Bucket` can do the right thing and access `max_quota` and `quota_consumed` directly.

最好的部分是使用 `Bucket.quota` 的代码不需要改变或知道该类已经改变。新使用 `Bucket` 可以正确地直接访问 `max_quota` 和 `quota_consumed`。

I especially like `@property` because it lets you make incremental progress toward a better data model over time. Reading the `Bucket` example above, you might have thought that `fill` and `deduct` should have been implemented as instance methods in the first place. Although you’re probably right, in practice there are many situations in which objects start with poorly defined interfaces or act as dumb data containers (see Item 51: “Prefer dataclasses For Defining Light-Weight Classes” for examples). This happens when code grows over time, scope increases, multiple authors contribute without anyone considering long-term hygiene, and so on.

我特别喜欢 `@property`，因为它让你随着时间推移逐步改进数据模型。阅读上面的 `Bucket` 示例，你可能会认为 `fill` 和 `deduct` 最初就应该作为实例方法实现。虽然你是正确的，但在实践中有很多情况对象的接口定义不明确或充当了笨拙的数据容器（参见条目51：“优先使用 dataclasses 定义轻量级类”以获取示例）。这通常发生在代码随着时间增长、范围扩大、多个作者贡献而没有人考虑长期维护的情况下。

`@property` is a tool to help you address problems you’ll come across in real-world code. Don’t overuse it. When you find yourself repeatedly extending `@property` methods, it’s probably time to refactor your class instead of further paving over your code’s poor design.

`@property` 是一种工具，可以帮助你解决在现实世界代码中遇到的问题。不要过度使用它。当你发现自己反复扩展 `@property` 方法时，可能是时候重构你的类，而不是继续掩盖代码设计不佳的问题。

**Things to Remember**
- Use `@property` to give existing instance attributes new functionality.
- Make incremental progress toward better data models by using `@property` .
- Consider refactoring a class and all call sites when you find yourself using `@property` too heavily.

**注意事项**
- 使用 `@property` 给现有的实例属性添加新功能。
- 通过使用 `@property` 逐步推进更好的数据模型。
- 当发现频繁使用 `@property` 时，应考虑重构类及其所有调用站点。