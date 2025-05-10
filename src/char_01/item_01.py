"""
获取当前 Python 解释器的运行环境信息。

该脚本输出以下内容：
- 当前运行的操作系统平台（如 win32、linux、darwin 等）
- Python 解释器的实现名称（如 cpython、pypy 等）
- Python 版本信息的命名元组（包含主版本号、次版本号等）
- 完整的 Python 版本字符串

用途：用于调试或确认当前运行的 Python 环境。
"""

import sys

print(sys.platform)
print(sys.implementation.name)
print(sys.version_info)
print(sys.version)
