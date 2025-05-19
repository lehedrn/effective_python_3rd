"""
本文件演示了使用生成器替代返回列表的优势，包括：
1. 通过示例对比原始使用列表的函数与使用生成器的函数。
2. 展示如何将生成器应用于处理大文件等场景。
3. 提供了错误实现和正确实现，并进行说明。

目标是展示生成器在代码清晰度、内存效率以及处理大规模数据时的优势。
"""

import logging
import itertools

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# 错误示例：使用列表累积结果
def index_words(text):
    """
    错误示例：该函数通过列表存储所有结果，适用于小规模输入。
    但代码冗余且占用较多内存。
    """
    result = []
    if text:
        result.append(0)
    for index, letter in enumerate(text):
        if letter == " ":
            result.append(index + 1)
    return result


# 正确示例：使用生成器优化代码结构
def index_words_iter(text):
    """
    正确示例：使用生成器逐步产生输出，避免中间列表。
    更加简洁，适合各种规模的输入。
    """
    if text:
        yield 0
    for index, letter in enumerate(text):
        if letter == " ":
            yield index + 1


# 示例函数：处理大文件内容（按行读取）
def index_file(handle):
    """
    正确示例：逐行读取文件并生成单词索引。
    使用生成器处理任意长度的输入，减少内存消耗。
    """
    offset = 0
    for line in handle:
        if line.strip():
            yield offset
        for letter in line:
            offset += 1
            if letter == " ":
                yield offset


# 主函数：运行完整示例
def main():
    # 示例文本
    address = ("Four score and seven years ago our fathers brought forth on this "
               "continent a new nation, conceived in liberty, and dedicated to the proposition that all men are created equal.")

    # 错误示例：使用列表累积结果
    logging.info("错误示例：使用列表累积结果")
    list_result = index_words(address)
    logging.info(f"列表结果前10个索引: {list_result[:10]}")

    # 正确示例：使用生成器优化代码结构
    logging.info("正确示例：使用生成器优化代码结构")
    gen_result = list(index_words_iter(address))
    logging.info(f"生成器结果前10个索引: {gen_result[:10]}")

    # 正确示例：处理大文件内容
    logging.info("正确示例：处理大文件内容")

    # 写入测试文件
    file_path = "address.txt"
    address_lines = """Four score and seven years
ago our fathers brought forth on this
continent a new nation, conceived in liberty,
and dedicated to the proposition that all men
are created equal."""
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(address_lines)

    # 读取文件并处理
    with open(file_path, "r", encoding="utf-8") as f:
        file_gen = index_file(f)
        results = itertools.islice(file_gen, 0, 10)
        logging.info(f"文件处理结果前10个索引: {list(results)}")


if __name__ == "__main__":
    main()
