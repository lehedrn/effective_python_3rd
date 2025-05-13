"""
本模块演示了 Python 中处理自定义类数据的完整示例，涵盖了以下内容：
1. 自定义类中 `__repr__` 和 `__str__` 的正确实现方式。
2. 使用 `bytes` 和 `str` 处理原始字节和文本字符串之间的转换。
3. 列表切片与步长操作在实际数据解析中的应用。
4. 星号解包（*）用于动态数据结构的灵活处理。
5. 文件读写时使用二进制模式与文本模式的区别及注意事项。

该示例模拟了一个简单的数据处理流程：从文件中读取原始二进制数据、解析为文本格式、提取关键信息并生成可调试输出。
"""

import locale


# -------------------------------
# 1. 定义自定义类以支持调试和用户展示
# -------------------------------

class SensorData:
    """
    表示传感器采集的数据条目，包含时间戳、温度和湿度字段。
    - 实现 __repr__以便于调试，返回可重建对象的字符串表示。
    - 实现 __str__以提供对终端用户友好的格式化输出。
    """

    def __init__(self, timestamp: str, temperature: float, humidity: float):
        self.timestamp = timestamp
        self.temperature = temperature
        self.humidity = humidity

    def __repr__(self):
        return f"SensorData(timestamp={self.timestamp!r}, temperature={self.temperature!r}, humidity={self.humidity!r})"

    def __str__(self):
        return f"[{self.timestamp}] 温度: {self.temperature}°C, 湿度: {self.humidity}%"


# -------------------------------
# 2. 原始数据处理函数
# -------------------------------

def parse_binary_sensor_data(raw_data: bytes) -> list[SensorData]:
    """
    解析原始二进制传感器数据流，将其转换为结构化的 SensorData 对象列表。

    参数:
        raw_data (bytes): 包含传感器记录的原始字节数据，每行由逗号分隔，
                          格式为 "timestamp,temp,humid\n"

    返回:
        list[SensorData]: 解析后的传感器数据对象列表。
    """
    # 将原始字节数据解码为 UTF-8 字符串
    decoded_data = raw_data.decode("utf-8")

    # 按换行符分割成每一行数据
    lines = decoded_data.strip().split("\n")

    parsed_records = []

    for line in lines:
        try:
            timestamp, temp_str, humid_str = line.split(",")
            temperature = float(temp_str)
            humidity = float(humid_str)

            # 创建 SensorData 对象并加入列表
            record = SensorData(timestamp.strip(), temperature, humidity)
            parsed_records.append(record)
        except ValueError as e:
            print(f"解析错误：无法处理行 '{line}'，原因：{e}")

    return parsed_records


# -------------------------------
# 3. 数据分析与提取函数
# -------------------------------

def extract_temperature_trend(data_list: list[SensorData], start_index: int, end_index: int, step: int):
    """
    提取温度变化趋势子集，使用切片与步长操作获取间隔采样数据。

    参数:
        data_list (list[SensorData]): 完整的传感器数据列表。
        start_index (int): 起始索引。
        end_index (int): 结束索引（不包含）。
        step (int): 步长值。

    返回:
        list[SensorData]: 提取后的样本数据。
    """
    if not data_list:
        raise ValueError("输入数据为空，请确保已成功解析传感器数据。")

    # 使用切片提取指定范围并按步长取样
    sampled_data = data_list[start_index:end_index:step]
    return sampled_data


# -------------------------------
# 4. 主程序逻辑
# -------------------------------

def main():
    """
    主函数：执行整个数据处理流程：
    1. 准备原始二进制数据。
    2. 解析为结构化 SensorData 对象列表。
    3. 使用切片提取特定区间内的温度趋势数据。
    4. 打印调试信息和用户友好信息。
    """
    print("=== 系统默认编码 ===")
    encoding = locale.getpreferredencoding()
    print(f"系统首选编码为: {encoding}\n")

    print("=== 模拟原始二进制数据准备 ===")
    raw_binary_data = (
        b"2023-10-01 12:00:00,22.5,60\n"
        b"2023-10-01 12:05:00,22.7,61\n"
        b"2023-10-01 12:10:00,23.0,62\n"
        b"2023-10-01 12:15:00,23.3,63\n"
        b"2023-10-01 12:20:00,23.5,64\n"
        b"2023-10-01 12:25:00,23.7,65\n"
        b"2023-10-01 12:30:00,23.9,66\n"
    )
    print("原始二进制数据:", raw_binary_data)

    print("\n=== 解析原始数据为结构化 SensorData ===")
    sensor_records = parse_binary_sensor_data(raw_binary_data)
    print("解析结果:")
    for record in sensor_records:
        print(repr(record))  # 调用 __repr__ 输出调试信息
        print(str(record))   # 调用 __str__ 输出用户友好信息

    print("\n=== 提取温度变化趋势（每隔两行采样） ===")
    try:
        trend_samples = extract_temperature_trend(sensor_records, start_index=0, end_index=5, step=2)
        print("温度趋势采样结果:")
        for sample in trend_samples:
            print(str(sample))
    except ValueError as e:
        print("提取失败:", e)

    print("\n=== 保存解析后数据到文件 ===")
    output_file = "sensor_output.txt"
    with open(output_file, "w", encoding="utf-8") as file:
        for record in sensor_records:
            file.write(str(record) + "\n")  # 写入用户友好格式

    print(f"数据已写入文件 {output_file}")

    print("\n=== 读取并验证文件内容 ===")
    with open(output_file, "r", encoding="utf-8") as file:
        content = file.read()
    print("文件内容:")
    print(content)


if __name__ == "__main__":
    main()
