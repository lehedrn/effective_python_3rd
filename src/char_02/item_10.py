"""
本模块演示了 Python 中 bytes 和 str 的区别，包括常见陷阱和正确使用方式。
每个示例都封装在一个函数中，并在 main 函数中统一调用。
特别增加了关于 locale.getpreferredencoding() 的示例以说明系统默认编码问题。
"""

import locale
import os


# -------------------------------
# 示例 1: bytes 和 str 的基本区别
# -------------------------------

def example_1():
    """
    展示 bytes 和 str 的基本区别：
    - bytes 是原始的 8 位字节序列。
    - str 是 Unicode 码点的序列。
    """
    # 创建一个 bytes 实例
    byte_data = b"h\x65llo"
    print("Type of byte_data:", type(byte_data))  # <class 'bytes'>
    print("List of byte values:", list(byte_data))  # [104, 101, 108, 108, 111]
    print("Decoded string:", byte_data)  # b'hello'

    # 创建一个 str 实例
    str_data = "a\u0300 propos"
    print("\nType of str_data:", type(str_data))  # <class 'str'>
    print("List of characters:", list(str_data))  # ['a', '̀', ' ', 'p', 'r', 'o', 'p', 'o', 's']
    print("Unicode string:", str_data)  # à propos


# -------------------------------------
# 示例 2: bytes 和 str 拼接错误与正确方式
# -------------------------------------

def example_2_wrong():
    """
    错误示例：尝试拼接 str 和 bytes 会引发 TypeError。
    """
    try:
        result = b"one" + "two"
    except TypeError as e:
        print("Caught error:", e)

def example_2_correct():
    """
    正确示例：确保类型一致后再进行拼接。
    """
    result1 = b"one" + b"two"
    result2 = "one" + "two"
    print("Bytes concatenation:", result1)  # b'onetwo'
    print("Str concatenation:", result2)  # onetwo


# -------------------------------------
# 示例 3: bytes 和 str 比较错误与正确方式
# -------------------------------------

def example_3_wrong():
    """
    错误示例：比较 str 和 bytes 会引发 TypeError。
    """
    try:
        assert "red" > b"blue"
    except TypeError as e:
        print("Caught error:", e)

def example_3_correct():
    """
    正确示例：将 bytes 解码为 str 后再比较。
    """
    str_data = "red"
    byte_data = b"blue"

    decoded_str = byte_data.decode("utf-8")
    result = str_data > decoded_str
    print("Comparison after decoding:", result)  # True


# -------------------------------------
# 示例 4: 使用 % 格式化字符串时的陷阱
# -------------------------------------

def example_4_wrong():
    """
    错误示例：在 bytes 格式字符串中使用 str 参数会出错。
    """
    blue_str = "blue"
    try:
        print(b"red %s" % blue_str)
    except TypeError as e:
        print("Caught error:", e)

def example_4_correct():
    """
    正确示例：确保格式化参数与格式字符串类型一致。
    """
    blue_bytes = b"blue"
    blue_str = "blue"

    print(b"red %s" % blue_bytes)  # b'red blue'
    print("red %s" % blue_str)  # red blue


# -----------------------------------------
# 示例 5: 文件读写时 bytes 与 str 的处理错误与正确方式
# -----------------------------------------

def example_5_wrong():
    """
    错误示例：以文本模式写入 bytes 数据会出错。
    """
    try:
        with open("data.bin", "w") as f:
            f.write(b"\xf1\xf2\xf3\xf4\xf5")
    except TypeError as e:
        print("Caught error:", e)

def example_5_correct_write():
    """
    正确示例：以二进制模式写入 bytes 数据。
    """
    with open("data.bin", "wb") as f:
        f.write(b"\xf1\xf2\xf3\xf4\xf5")
    print("Binary data written successfully.")

def example_5_correct_read():
    """
    正确示例：以二进制模式读取 bytes 数据。
    """
    with open("data.bin", "rb") as f:
        data = f.read()
    print("Binary data read:", data)  # b'\xf1\xf2\xf3\xf4\xf5'


# -----------------------------------------
# 示例 6: 获取系统默认编码（locale.getpreferredencoding）
# -----------------------------------------

def example_6_get_system_encoding():
    """
    示例展示如何获取系统默认编码。
    这对理解文件读写时默认使用的编码很有帮助。
    """
    encoding = locale.getpreferredencoding()
    print(f"System's preferred encoding is: {encoding}")

def delete_file():
    """删除示例中用到的data.bin文件"""
    try:
        os.remove("data.bin")
        print("File data.bin deleted successfully.")
    except FileNotFoundError as e:
        print(f"File data.bin is  not found. Skipping deletion. {e}")

# -------------------------------
# 主函数：运行所有示例
# -------------------------------

def main():
    print("=== Example 1 ===")
    example_1()

    print("\n=== Example 2 (Wrong) ===")
    example_2_wrong()
    print("\n=== Example 2 (Correct) ===")
    example_2_correct()

    print("\n=== Example 3 (Wrong) ===")
    example_3_wrong()
    print("\n=== Example 3 (Correct) ===")
    example_3_correct()

    print("\n=== Example 4 (Wrong) ===")
    example_4_wrong()
    print("\n=== Example 4 (Correct) ===")
    example_4_correct()

    print("\n=== Example 5 (Wrong) ===")
    example_5_wrong()
    print("\n=== Example 5 (Correct Write) ===")
    example_5_correct_write()
    print("\n=== Example 5 (Correct Read) ===")
    example_5_correct_read()

    print("\n=== Example 6 (Get System Encoding) ===")
    example_6_get_system_encoding()

    print("\n=== delete demo file [data.bin] ===")
    delete_file()


if __name__ == "__main__":
    main()
