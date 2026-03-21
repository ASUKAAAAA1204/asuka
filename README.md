# 文档内容概括与关键词提取系统

## 项目介绍

这是一个本地化的文档处理系统，能够从各类文档（PDF、Word、Excel、TXT）中提取文本内容，自动生成摘要并提取关键词。该系统作为个人知识库的核心功能模块，实现文件的智能分析和快速检索。

## 核心功能

- **文档内容提取**：支持多种文件格式的文本提取
- **智能摘要生成**：自动生成文档的核心内容摘要
- **关键词提取**：基于算法自动提取文档关键词
- **本地化运行**：所有处理在本地完成，无需联网

## 技术栈

- Python 3.8+
- jieba（中文分词）
- scikit-learn（TF-IDF、相似度计算）
- numpy（数值计算）
- networkx（图算法TextRank）
- pdfplumber（PDF解析）
- python-docx（Word解析）
- openpyxl（Excel解析）

## 安装方式

### 方法一：使用pip安装

```bash
pip install -r requirements.txt
```

### 方法二：本地安装

```bash
python setup.py install
```

## 使用示例

### 1. 作为Python库使用

```python
from document_analyzer import DocumentAnalyzer

# 初始化分析器
analyzer = DocumentAnalyzer()

# 完整分析文档
result = analyzer.analyze('example.pdf')
print("摘要:", result['summary'])
print("关键词:", [kw['keyword'] for kw in result['keywords']])

# 仅提取文本和元数据
text, metadata = analyzer.extract_only('example.docx')

# 仅生成摘要
summary = analyzer.summarize_only(text)

# 仅提取关键词
keywords = analyzer.extract_keywords_only(text, top_k=5)
```

### 2. 使用命令行工具

```bash
# 分析单个文档（文本格式输出）
document-analyzer example.pdf

# 分析单个文档（JSON格式输出）
document-analyzer --format json example.pdf

# 指定关键词数量
document-analyzer --keywords 5 example.pdf

# 批量处理多个文档
document-analyzer file1.pdf file2.docx file3.txt
```

## API文档

### DocumentAnalyzer类

#### `analyze(file_path)`

完整分析文档，返回包含元数据、摘要、关键词等的完整结果。

**参数**：

- `file_path`：文件路径

**返回值**：

- 字典，包含以下键：
  - `metadata`：元数据信息
  - `summary`：摘要文本
  - `summary_sentences`：摘要句子详情列表
  - `keywords`：关键词列表
  - `statistics`：统计信息

#### `extract_only(file_path)`

仅提取文本和元数据。

**参数**：

- `file_path`：文件路径

**返回值**：

- `(text, metadata)`：文本内容和元数据字典

#### `summarize_only(text, max_sentences=None, return_details=False)`

仅生成摘要。

**参数**：

- `text`：文本
- `max_sentences`：最大句子数，None表示自动调整
- `return_details`：是否返回句子详情

**返回值**：

- 如果`return_details`为True，返回`(summary, details)`
- 否则返回摘要文本

#### `extract_keywords_only(text, top_k=10, include_pos=False)`

仅提取关键词。

**参数**：

- `text`：文本
- `top_k`：提取的关键词数量
- `include_pos`：是否包含词性信息

**返回值**：

- 关键词列表

## 项目结构

```
document_analyzer/
├── core/                # 核心模块
│   ├── extractor.py     # 文件解析
│   ├── preprocessor.py  # 文本预处理
│   ├── summarizer.py    # 摘要生成
│   └── keyword.py       # 关键词提取
├── utils/               # 工具
│   ├── stopwords.txt    # 停用词表
│   └── text_utils.py    # 文本工具函数
├── models/              # 模型
│   └── algorithms.py    # 算法实现
├── api/                 # 接口
│   └── document_analyzer.py  # 主接口
├── tests/               # 测试
│   └── test_analyzer.py # 测试代码
├── cli.py               # 命令行工具
├── requirements.txt     # 依赖配置
├── setup.py             # 安装配置
└── README.md            # 项目文档
```

## 性能要求

- 普通文档处理时间 < 5秒
- 长文档处理时间 < 15秒
- 内存占用 < 1GB

## 注意事项

- 所有处理在本地完成，不依赖云端服务
- 支持的文件格式：PDF、Word (.docx, .doc)、Excel (.xlsx, .xls)、TXT
- 优先考虑中文文本处理优化
- 提供清晰的错误处理机制

  快捷运行：

## 测试

运行测试代码：

```bash
python -m pytest document_analyzer/tests/test_analyzer.py -v
```

## 版本

前版本：1.0.0
