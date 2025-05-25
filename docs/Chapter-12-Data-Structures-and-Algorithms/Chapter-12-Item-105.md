# Chapter 12: Data Structures and Algorithms (数据结构与算法)

## Item 105: Use `datetime` Instead of `time` for Local Clocks (应该使用 `datetime` 而不是 `time` 来处理本地时钟)

Coordinated Universal Time (UTC) is the standard, time-zone-independent representation of time. UTC works great for computers that represent time as seconds since the UNIX epoch. But UTC isn’t ideal for humans. Humans reference time relative to where they’re currently located. People say “noon” or “8 am” instead of “UTC 15:00 minus 7 hours.” If your program handles time, you’ll probably find yourself converting time between UTC and local clocks for the sake of human understanding.

协调世界时（UTC）是一种与时间区无关的时间标准表示形式。UTC 对于计算机来说非常合适，因为计算机将时间表示为自 UNIX 纪元以来的秒数。但 UTC 并不理想于人类。人类通常根据他们当前所在的位置来引用时间。人们会说“中午”或“早上8点”，而不是“UTC 15:00 减去7小时”。如果你的程序需要处理时间，你可能发现自己需要在 UTC 和本地时钟之间进行转换，以方便人类理解。

Python provides two ways of accomplishing time zone conversions. The old way, using the `time` built-in module, is terribly error prone. The new way, using the `datetime` , works great with some help from the other built-in package named `zoneinfo` .

Python 提供了两种方式来进行时区转换。旧的方式是使用 `time` 内置模块，这种方法非常容易出错。新的方式是使用 `datetime` 模块，在配合名为 `zoneinfo` 的其他内置包时效果很好。

You should be acquainted with both `time` and `datetime` to thoroughly understand why `datetime` is the best choice and `time` should be avoided.

你应该熟悉 `time` 和 `datetime`，以便彻底了解为什么 `datetime` 是最佳选择，而 `time` 应该避免使用。

### The `time` Module ( `time` 模块)

The `localtime` function from the `time` built-in module lets you convert a UNIX timestamp (seconds since the UNIX epoch in UTC) to a local time that matches the host computer’s time zone (Pacific Daylight Time in my case). This local time can be printed in human-readable format using the `strftime` function:

`time` 内置模块中的 `localtime` 函数可以让你将一个 UNIX 时间戳（自 UTC 下的 UNIX 纪元开始的秒数）转换为主机计算机时区（在我的情况下是太平洋夏令时间）的本地时间。这种本地时间可以使用 `strftime` 函数以人类可读的格式打印：

```
import time

now = 1710047865.0
local_tuple = time.localtime(now)
time_format = "%Y-%m-%d %H:%M:%S"
time_str = time.strftime(time_format, local_tuple)
print(time_str)
>>>
2024-03-09 21:17:45
```

You’ll often need to go the other way as well, starting with user input in human-readable local time and converting it to UTC time. You can do this by using the `strptime` function to parse the time string, and then calling `mktime` to convert local time to a UNIX timestamp:

你通常还需要反向操作，即从用户输入的人类可读的本地时间开始，并将其转换为 UTC 时间。你可以通过使用 `strptime` 函数解析时间字符串，然后调用 `mktime` 将本地时间转换为 UNIX 时间戳来实现这一点：

```
time_tuple = time.strptime(time_str, time_format)
utc_now = time.mktime(time_tuple)
print(utc_now)
>>>
1710047865.0
```

How do you convert local time in one time zone to local time in another time zone? For example, say that I’m taking a flight between San Francisco and New York, and I want to know what time it will be in San Francisco when I’ve arrived in New York.

如何将一个时区的本地时间转换为另一个时区的本地时间？例如，假设我要在旧金山和纽约之间乘坐航班，并想知道到达纽约时旧金山的时间。

I might initially assume that I can directly manipulate the return values from the `time` , `localtime` , and `strptime` functions to do time zone conversions. But this is a very bad idea. Time zones change all the time due to local laws. It’s too complicated to manage yourself, especially if you want to handle every global city for flight departures and arrivals.

我可能会最初假设可以直接操作 `time`、`localtime` 和 `strptime` 函数的返回值来执行时区转换。但这其实是一个非常糟糕的想法。由于地方法律的变化，时区一直在变化。自己管理这些变化太复杂了，特别是如果你想处理全球每个城市航班的起飞和到达时间的话。

Many operating systems have configuration files that keep up with the time zone changes automatically. Python lets you use these time zones through the `time` module if your platform supports it. On other platforms, such as Windows, some time zone functionality isn’t available from `time` at all. For example, here I parse a departure time from the San Francisco time zone, Pacific Standard Time (PST):

许多操作系统都有配置文件来自动跟踪时区变化。如果平台支持，Python 允许你通过 `time` 模块使用这些时区。而在其他平台上，比如 Windows，则根本无法通过 `time` 使用某些时区功能。例如，这里我解析了来自太平洋标准时间 (PST) 的旧金山出发时间：

```
parse_format = "%Y-%m-%d %H:%M:%S %Z"
depart_sfo = "2024-03-09 21:17:45 PST"
time_tuple = time.strptime(depart_sfo, parse_format)
time_str = time.strftime(time_format, time_tuple)
print(time_str)
>>>
2024-03-09 21:17:45
```

After seeing that `"PST"` works with the `strptime` function, I might also assume that other time zones known to my computer will work. Unfortunately, this isn’t the case. Instead, `strptime` raises an exception when it sees Eastern Daylight Time (EDT), which is the time zone for New York:

看到 `"PST"` 在 `strptime` 中有效后，我也可能假设我的计算机上已知的其他时区也会有效。不幸的是，情况并非如此。相反，当 `strptime` 看到美国东部夏令时间 (EDT)，即纽约的时区时，会引发异常：

```
arrival_nyc = "2024-03-10 03:31:18 EDT"
time_tuple = time.strptime(arrival_nyc, parse_format)
>>>
Traceback ...
ValueError: time data '2024-03-10 03:31:18 EDT' does not match format '%Y-%m-%d %H:%M:%S %Z'
```

The problem here is the platform-dependent nature of the `time` module. Its actual behavior is determined by how the underlying C functions work with the host operating system. This makes the functionality of the `time` module unreliable in Python. The `time` module fails to consistently work properly for multiple local times. Thus, you should avoid using the `time` module for this purpose. If you must use `time` , use it only to convert between UTC and the host computer’s local time. For all other types of conversions, use the `datetime` module.

这里的问题在于 `time` 模块的平台依赖性。它的实际行为取决于底层 C 函数与主机操作系统的工作方式。这使得 Python 中 `time` 模块的功能不可靠。`time` 模块不能一致地正常工作于多个本地时间。因此，你应该避免为此目的使用 `time` 模块。如果你必须使用 `time`，请仅将其用于在 UTC 和主机计算机的本地时间之间进行转换。对于所有其他类型的转换，请使用 `datetime` 模块。

### The `datetime` Module (`datetime` 模块)

The second option for representing times in Python is the `datetime` class from the `datetime` built-in module. Like the time module, `datetime` can be used to convert from the current time in UTC to local time.

Python 中表示时间的第二个选项是使用 `datetime` 模块中的 `datetime` 类。像 `time` 模块一样，`datetime` 可以用来将当前的 UTC 时间转换为本地时间。

Here, I convert the present time in UTC to my computer’s local time, PDT:

在这里，我将当前 UTC 时间转换为我的计算机的本地时间 PDT：

```
from datetime import datetime, timezone

now = datetime(2024, 3, 10, 5, 17, 45)
now_utc = now.replace(tzinfo=timezone.utc)
now_local = now_utc.astimezone()
print(now_local)
>>>
2024-03-09 21:17:45-08:00
```

The `datetime` module can also easily convert a local time back to a UNIX timestamp in UTC (matching the value above):

`datetime` 模块还可以轻松地将本地时间转换回 UTC 的 UNIX 时间戳（与上面的值匹配）：

```
time_str = "2024-03-09 21:17:45"
now = datetime.strptime(time_str, time_format)
time_tuple = now.timetuple()
utc_now = time.mktime(time_tuple)
print(utc_now)
>>>
1710047865.0
```

Unlike the `time` module, the `datetime` module has facilities for reliably converting from one local time to another local time. However, `datetime` only provides the machinery for time zone operations with its `tzinfo` class and related methods.

与 `time` 模块不同，`datetime` 模块具备可靠地在一个本地时间与另一个本地时间之间转换的设施。然而，`datetime` 仅为时区操作提供了工具，其核心是 `tzinfo` 类及其相关方法。

Fortunately, since Python version 3.9, on many systems the `zoneinfo` built-in module contains a full database of every time zone definition you might need. On other systems, such as Windows, the officially endorsed `tzdata` community package might need to be installed to provide the timezone database that the `zoneinfo` module needs to function properly (see Item 116: “Know Where to Find Community-Built Modules” for details).

幸运的是，自 Python 3.9 版本起，在许多系统上，`zoneinfo` 内建模块包含了你可能需要的所有时区定义的完整数据库。在其他系统上，例如 Windows，可能需要安装官方推荐的 `tzdata` 社区包，以提供 `zoneinfo` 模块正常运行所需的时区数据库（详情请参见第 116 项：“知道在哪里寻找社区构建的模块”）。

To use `zoneinfo` effectively, you should always convert local times to UTC first. Perform any `datetime` operations you need on the UTC values (such as offsetting). Then, convert to local times as a final step.

为了有效地使用 `zoneinfo`，你应该始终首先将本地时间转换为 UTC。对 UTC 值执行任何你需要的 `datetime` 操作（如偏移）。然后，最后一步再将其转换为本地时间。

For example, here I convert a New York City flight arrival time to a UTC `datetime` :

例如，这里我将纽约市航班到达时间转换为一个 UTC `datetime`：

```
from zoneinfo import ZoneInfo

arrival_nyc = "2024-03-10 03:31:18"
nyc_dt_naive = datetime.strptime(arrival_nyc, time_format)
eastern = ZoneInfo("US/Eastern")
nyc_dt = nyc_dt_naive.replace(tzinfo=eastern)
utc_dt = nyc_dt.astimezone(timezone.utc)
print("EDT:", nyc_dt)
print("UTC:", utc_dt)
>>>
EDT: 2024-03-10 03:31:18-04:00
UTC: 2024-03-10 07:31:18+00:00
```

Once I have a UTC `datetime` , I can convert it to San Francisco local time:

一旦我有了一个 UTC `datetime`，我可以将其转换为旧金山的本地时间：

```
pacific = ZoneInfo("US/Pacific")
sf_dt = utc_dt.astimezone(pacific)
print("PST:", sf_dt)
>>>
PST: 2024-03-09 23:31:18-08:00
```

Just as easily, I can convert it to the local time in Nepal:

同样地，我也可以轻松地将其转换为尼泊尔的当地时间：

```
nepal = ZoneInfo("Asia/Katmandu")
nepal_dt = utc_dt.astimezone(nepal)
print("NPT", nepal_dt)
>>>
NPT 2024-03-10 13:16:18+05:45
```

With `datetime` and `zoneinfo` , these conversions are consistent across all environments, regardless of what operating system the host computer is running.

借助 `datetime` 和 `zoneinfo`，无论主机运行何种操作系统，这些转换在所有环境中都是一致的。

**Things to Remember**
- Avoid using the `time` module for translating between different time zones.
- Use the `datetime` and `zoneinfo` built-in modules to reliably convert between times and dates in different time zones.
- Always represent time in UTC and do conversions to local time as the very final step before presentation.

**注意事项**
- 避免使用 `time` 模块在不同时区之间进行转换。
- 使用 `datetime` 和 `zoneinfo` 内建模块，以可靠地在不同时区的日期和时间之间进行转换。
- 始终以 UTC 表示时间，并在最终步骤进行转换为本地时间以便展示。