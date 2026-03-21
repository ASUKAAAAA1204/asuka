from setuptools import setup, find_packages

setup(
    name="document-analyzer",
    version="1.0.0",
    description="文档内容概括与关键词提取系统",
    long_description="一个本地化的文档处理系统，能够从各类文档中提取文本内容，自动生成摘要并提取关键词。",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "jieba>=0.42.1",
        "scikit-learn>=1.0.0",
        "numpy>=1.21.0",
        "networkx>=2.6.0",
        "pdfplumber>=0.7.0",
        "python-docx>=0.8.11",
        "openpyxl>=3.0.9"
    ],
    extras_require={
        "optional": [
            "pandas>=1.3.0",
            "nltk>=3.7"
        ]
    },
    entry_points={
        "console_scripts": [
            "document-analyzer=document_analyzer.cli:main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8'
)
