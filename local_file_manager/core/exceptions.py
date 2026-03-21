"""异常类定义"""

class FileManagerError(Exception):
    """文件管理器基础异常"""
    pass

class FileNotFoundError(FileManagerError):
    """文件不存在异常"""
    pass

class FileAccessError(FileManagerError):
    """文件访问异常"""
    pass

class FileOperationError(FileManagerError):
    """文件操作异常"""
    pass

class PathValidationError(FileManagerError):
    """路径验证异常"""
    pass

class StorageError(FileManagerError):
    """存储异常"""
    pass

class BackupError(FileManagerError):
    """备份异常"""
    pass

class SearchError(Exception):
    """搜索异常"""
    pass

class ValidationError(Exception):
    """验证异常"""
    pass
