"""
日志收集与分析全流程中的 Python 字符串与切片最佳实践示例

本文件系统性演示了《Effective Python》第三版第2章“Strings and Slicing”的主要实践，
结合“日志文件读取→解析→格式化输出→告警分析→数据抽样”完整工程场景，涵盖如下要点：

- `bytes` 与 `str` 区分与安全转换
- 日志文本与二进制数据的正确读取与写入
- f-string 格式化字符串的极致用法
- repr 与 str 的调试/友好展示分工
- 显式字符串拼接减少隐藏Bug
- 切片的安全、高效与副作用
- 步长切片与 itertools 的工程安全用法
- 星号解包在日志数据拆分/结构变动场景的优越性

本代码通过模拟日志数据与多元流程，帮助你在工程实践中掌握字符串与切片的底层功夫。
"""

import os
import csv
import random
from itertools import islice
from pathlib import Path


# =======================
# 1. bytes 与 str 的边界
# =======================
def to_str(bytes_or_str):
    """将 bytes（假设 utf-8 编码）转换为 str，否则原样返回"""
    if isinstance(bytes_or_str, bytes):
        return bytes_or_str.decode("utf-8")
    return bytes_or_str


def to_bytes(bytes_or_str):
    """将 str 转 bytes（utf-8），否则原样返回"""
    if isinstance(bytes_or_str, str):
        return bytes_or_str.encode("utf-8")
    return bytes_or_str


def demo_bytes_str_io():
    """模拟日志的文本和二进制读取与写入"""
    # 生成模拟日志
    LOG_TXT = "demo_log_utf8.txt"
    LOG_BIN = "demo_snap.bin"
    text_line = "2023-10-01 12:00:01 INFO 用户alice登录系统\n"
    bin_data = b'\xf0\xf1\xf2 DEMO\xff\xee'

    # 写文本型日志
    with open(LOG_TXT, "w", encoding="utf-8") as f:
        f.write(text_line)
    # 读文本型日志
    with open(LOG_TXT, "r", encoding="utf-8") as f:
        tmp = f.read()
        print(f"读文本日志: {tmp.strip()}，类型: {type(tmp)}")

    # 写二进制快照
    with open(LOG_BIN, "wb") as f:
        f.write(bin_data)
    # 读二进制快照
    with open(LOG_BIN, "rb") as f:
        data = f.read()
        print(f"读快照数据: {data}，类型: {type(data)}")
        # 转回字符串（仅演示，实际需知具体编码）
        # recover_str = to_str(data[:10])  # 假定前10字节可正确decode
        # print(f"二进制转str（部分）: {recover_str}")
        try:
            recover_str = to_str(data[:10])
            print(f"二进制转str（部分）: {recover_str}")
        except UnicodeDecodeError as e:
            print(f"无法decode，可能非utf-8编码 {e}")



# =======================
# 2. 生成模拟日志 CSV
# =======================
def generate_fake_log_csv(filename, n=20):
    """生成模拟日志数据 CSV 文件：字段 = 时间戳, 用户, 事件, ...可变字段"""
    users = ["alice", "bob", "张三", "root"]
    events = ["login", "logout", "buy", "error"]
    extra_fields = [["IP:192.168.1.1"], ["ret:ok", "cost:120ms"], [], ["warn:none"], ["code:404"]]
    with open(filename, "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        # 写header
        writer.writerow(["timestamp", "user", "event", "detail1", "detail2"])
        for i in range(n):
            ts = f"2023-10-01 12:{str(i % 60).zfill(2)}:{str(random.randint(0, 59)).zfill(2)}"
            user = random.choice(users)
            event = random.choice(events)
            extras = random.choice(extra_fields)
            detail1 = extras[0] if len(extras) > 0 else ""
            detail2 = extras[1] if len(extras) > 1 else ""
            writer.writerow([ts, user, event, detail1, detail2])


# =======================
# 3. 日志格式化输出与告警分析
# =======================
def log_analysis_pipeline(logfile):
    """演示日志的分步骤处理，包括解包、格式化、告警与统计"""
    # ============ 步骤1：读取文件，首行为header，剩余为记录 ============
    with open(logfile, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header, *rows = reader  # 星号解包分离header与全部日志行
        print(f"日志字段: {header}\n日志总条数: {len(rows)}")

        # ========== 步骤2：格式化输出（f-string展示），拼接多余字段 ==========
        print("\n【格式化日志输出】")
        for row in rows[:5]:  # 仅展示前5条
            ts, user, event, *extra = row
            # extra有时为空、有时有“IP:xxx”等
            extra_info = '；'.join(e for e in extra if e)
            msg = f"[{ts}] 用户 {user!r} 发生事件: {event:<8s} {extra_info}"
            print(msg)

        # ========== 步骤3：异常用户名告警 & repr 调试 ==========
        print("\n【告警分析：非法用户名出现时使用repr输出】")
        for line in rows:
            ts, user, event, *_ = line
            if not user.isascii():  # 检查是否包含非ascii（如中文名）
                print(f"⚠️ 非法用户名: {repr(user)} -> 日志时间: {ts}, 事件: {event}")

        # ========== 步骤4：切片操作与采样 ==========
        print("\n【日志抽样/切片】")
        first_3 = rows[:3]
        print(f"前三条样本（总共{len(first_3)}条）：")
        for r in first_3:
            print(f"[{r[0]}] {r[1]} - {r[2]}")
        # 超界切片不会报错
        last_10 = rows[-10:]
        print(f"\n最后10条样本实际拿到 {len(last_10)} 条。")

        # ========== 步骤5：步长采样，复杂步长分步实现 ==========
        print("\n【步长采样，每隔3条输出一条（itertools.islice）】")
        for r in islice(rows, 0, len(rows), 3):
            ts, user, event, *_ = r
            print(f"[{ts}] {user}-{event}")

        # ========== 步骤6：星号解包用于自适应结构 ==========
        print("\n【结构变动时解包更健壮】")
        for r in rows[:5]:
            head, *body, last = r
            print(f"首字段: {head}, 结尾字段: {last}, 中间: {body}")

        # ========== 步骤7：字符串拼接必须显式，避免隐式BUG ==========
        multi_fields = [
            "header:" + header[0],  # 显式 +
            "fields:" + ",".join(header[1:]),
        ]
        print("\n【多字段拼接，全部用 + 连接】")
        for f in multi_fields:
            print(f)


# =======================
# 4. 对象的 repr 与 str 的分工演示
# =======================
class LogRecord:
    """演示日志结构对象在调试和用户展示不同场合下 repr 与 str 的定制"""

    def __init__(self, ts, user, event, *det):
        self.ts = ts
        self.user = user
        self.event = event
        self.det = det

    def __repr__(self):
        # 适合日志调试、还原对象
        return (f"LogRecord({self.ts!r}, {self.user!r}, "
                f"{self.event!r}, {self.det!r})")

    def __str__(self):
        # 适合向用户/终端展示
        dets = ", ".join(d for d in self.det if d)
        return f"[{self.ts}] <{self.user}> 事件: {self.event} {dets}"


def demo_repr_str():
    obj = LogRecord("2023-10-01 13:00", "alice", "login", "IP:10.0.0.1")
    print(f"repr(obj)：{repr(obj)}")  # 调试用
    print(f"str(obj)：{str(obj)}")  # 展示用


# =======================
# 5. 一键运行主流程
# =======================
def main():
    print("【DEMO 1：bytes/str边界与I/O】")
    demo_bytes_str_io()
    print("\n【DEMO 2：生成并分析模拟日志文件】")

    # 准备模拟CSV日志文件
    demo_csv = "demo_logs.csv"
    generate_fake_log_csv(demo_csv, n=20)

    # 分步演示整个日志管道分析和字符串、切片高级用法
    log_analysis_pipeline(demo_csv)

    print("\n【DEMO 3：repr 与 str 的对象输出分层】")
    demo_repr_str()

    # 清理示例文件
    Path("demo_log_utf8.txt").unlink(missing_ok=True)
    Path("demo_snap.bin").unlink(missing_ok=True)
    Path("demo_logs.csv").unlink(missing_ok=True)


if __name__ == "__main__":
    main()