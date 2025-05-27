# effective_python_3rd
effective python 第三版 学习笔记

## 目录结构说明

- **src/**: 所有源码文件按照章节划分，每个章节对应一本章的学习内容。
  - 如：`char_01/` 包含第1章相关的 Python 文件（如 `item_01.py`, `item_02.py` 等）
- **docs/**: Markdown 文档，包含每章和每项的详细解释
  - 如：`Chapter-1-Pythonic-Thinking` 放置了第1章相关学习内容


## 依赖环境

`miniconda`、`pycharm`/`vscode`、`python3`

## 使用方法

1. 克隆仓库到本地：

```sh
bash git clone https://github.com/yourname/effective_python_3rd.git
```
2. 安装所需虚拟环境:

```sh
cd effective_python_3rd

conda create -n python313 python=3.13

conda activate python313

conda install -y conda-forge::requests
conda install -y conda-forge::black
conda install -y conda-forge::mypy
conda install -y conda-forge::aiofiles
conda install -y conda-forge::numba
conda install -y conda-forge::numpy
```   
3. 查看文档：
   - 每个 `docs/` 下的子目录对应一个章节，可以打开 Markdown 文件阅读详细内容。


