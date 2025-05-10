"""
Python 运行时错误示例

该文件演示了以下内容：
- 编译时无法检测到的运行时错误
- 正确使用变量和控制流避免错误
- 通过 main() 函数统一执行所有测试用例
"""

# 错误示例 1：未定义变量引用
def bad_reference():
    print(my_var)  # my_var 尚未定义
    my_var = 123

# 错误示例 2：条件语句中变量可能未定义
def sometimes_ok(x):
    if x:
        my_var = 123
    print(my_var)  # 当 x 为 False 时，my_var 未定义

# 错误示例 3：除零错误（数学错误）
def bad_math():
    return 1 / 0  # 除以零会在运行时报错

# 正确示例 1：确保变量在所有路径下都被定义
def sometimes_ok_fixed(x):
    if x:
        my_var = 123
    else:
        my_var = 0  # 明确赋值以避免 UnboundLocalError
    print(my_var)

# 正确示例 2：处理除法错误
def safe_divide(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        return "除法错误：除数不能为零"

# 主函数统一运行所有示例
def main():
    print("=== 错误示例 ===")
    try:
        bad_reference()
    except Exception as e:
        print(f"bad_reference 异常: {e}")

    try:
        sometimes_ok(False)
    except Exception as e:
        print(f"sometimes_ok(False) 异常: {e}")

    try:
        bad_math()
    except Exception as e:
        print(f"bad_math 异常: {e}")

    print("\n=== 正确示例 ===")
    sometimes_ok_fixed(True)   # 应输出 123
    sometimes_ok_fixed(False)  # 应输出 0

    result1 = safe_divide(1, 0)
    result2 = safe_divide(10, 2)
    print(f"safe_divide(1, 0) 结果: {result1}")
    print(f"safe_divide(10, 2) 结果: {result2}")

# 执行主函数
if __name__ == "__main__":
    main()
