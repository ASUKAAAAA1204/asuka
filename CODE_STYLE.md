# 代码风格指南

本项目遵循以下代码风格规范，确保代码的一致性和可维护性。

## 1. 命名规范

### 1.1 类名
- 使用驼峰命名法（CamelCase）
- 首字母大写
- 示例：`FileManager`、`SearchEngine`

### 1.2 函数名和方法名
- 使用小驼峰命名法（camelCase）
- 首字母小写
- 示例：`get_file_info`、`search_files`

### 1.3 变量名
- 使用小写字母加下划线（snake_case）
- 示例：`file_path`、`storage_dir`

### 1.4 常量
- 使用全大写字母加下划线
- 示例：`MAX_RESULTS`、`DEFAULT_CACHE_SIZE`

## 2. 代码格式

### 2.1 缩进
- 使用4个空格进行缩进
- 不要使用制表符（tab）

### 2.2 空行
- 类定义和函数定义之间使用2个空行
- 函数内部逻辑块之间使用1个空行
- 导入语句和代码主体之间使用1个空行

### 2.3 行长度
- 每行代码长度不超过80个字符
- 长行应适当换行，保持代码可读性

### 2.4 括号和空格
- 函数参数列表中，逗号后加空格
- 括号内不使用空格
- 运算符两侧加空格
- 示例：`def function_name(param1, param2):`

## 3. 文档字符串

### 3.1 类文档字符串
- 使用三引号（"""）
- 包含类的简要描述
- 示例：
  ```python
  class FileManager:
      """本地文件管理模块"""
  ```

### 3.2 函数文档字符串
- 使用三引号（"""）
- 包含函数的简要描述
- 使用`Args:`部分描述参数
- 使用`Returns:`部分描述返回值
- 示例：
  ```python
  def get_file_info(self, file_id: int) -> Optional[Dict[str, Any]]:
      """获取文件信息
      
      Args:
          file_id: 文件ID
          
      Returns:
          文件信息字典
      """
  ```

## 4. 导入语句

### 4.1 导入顺序
1. 标准库导入
2. 第三方库导入
3. 本地模块导入

### 4.2 导入格式
- 每个导入语句占一行
- 从同一模块导入多个项时，使用括号
- 示例：
  ```python
  import os
  import shutil
  from typing import Dict, List, Any, Optional
  from local_file_manager.core.data_store import DataStore
  from local_file_manager.core.exceptions import (
      FileNotFoundError,
      FileAccessError,
      FileOperationError
  )
  ```

## 5. 错误处理

- 使用具体的异常类型
- 提供详细的错误信息
- 使用try-except块捕获异常
- 示例：
  ```python
  try:
      # 代码
  except FileNotFoundError as e:
      return {'success': False, 'message': f'文件错误: {str(e)}'}
  except Exception as e:
      return {'success': False, 'message': f'未知错误: {str(e)}'}
  ```

## 6. 注释

- 注释应简洁明了
- 解释复杂的逻辑或算法
- 避免冗余注释
- 使用中文注释

## 7. 代码组织

- 每个文件应具有单一职责
- 类和函数应保持合理的大小
- 避免过长的函数（一般不超过50行）
- 提取重复代码为公共函数

## 8. 类型提示

- 使用Python类型提示
- 导入必要的类型
- 示例：
  ```python
  def add_file(self, file_info: Dict[str, Any]) -> int:
      """添加文件到数据库"""
  ```

## 9. 版本控制

- 提交消息应清晰明了
- 每个提交应专注于一个功能或修复
- 避免提交无关的更改

## 10. 工具和检查

- 使用静态类型检查工具（如mypy）
- 使用代码风格检查工具（如flake8）
- 运行测试确保代码质量

---

遵循以上代码风格规范，将有助于提高代码的可读性、可维护性和一致性。