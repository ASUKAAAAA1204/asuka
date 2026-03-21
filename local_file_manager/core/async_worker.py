"""异步文件操作模块"""

from PyQt6.QtCore import QThreadPool
from gui.utils.worker import Worker
from typing import Callable, Any, Dict

class AsyncFileWorker:
    """异步文件操作处理器"""
    
    def __init__(self):
        """初始化异步文件操作处理器"""
        self.thread_pool = QThreadPool.globalInstance()
    
    def execute_async(self, func: Callable, *args, **kwargs) -> Worker:
        """执行异步任务
        
        Args:
            func: 要执行的函数
            *args: 函数参数
            **kwargs: 函数关键字参数
            
        Returns:
            Worker: 工作线程实例
        """
        worker = Worker(func, *args, **kwargs)
        self.thread_pool.start(worker)
        return worker
    
    def delete_file_async(self, file_manager, file_id: int, 
                         on_success: Callable = None, 
                         on_error: Callable = None) -> Worker:
        """异步删除文件
        
        Args:
            file_manager: 文件管理器实例
            file_id: 文件ID
            on_success: 成功回调函数
            on_error: 错误回调函数
            
        Returns:
            Worker: 工作线程实例
        """
        def task():
            return file_manager.delete_file(file_id)
        
        worker = self.execute_async(task)
        
        if on_success:
            worker.signals.result.connect(lambda result: on_success(result) if result['success'] else on_error(result) if on_error else None)
        if on_error:
            worker.signals.error.connect(on_error)
        
        return worker
    
    def restore_file_async(self, file_manager, file_id: int, 
                          on_success: Callable = None, 
                          on_error: Callable = None) -> Worker:
        """异步恢复文件
        
        Args:
            file_manager: 文件管理器实例
            file_id: 文件ID
            on_success: 成功回调函数
            on_error: 错误回调函数
            
        Returns:
            Worker: 工作线程实例
        """
        def task():
            return file_manager.restore_file(file_id)
        
        worker = self.execute_async(task)
        
        if on_success:
            worker.signals.result.connect(lambda result: on_success(result) if result['success'] else on_error(result) if on_error else None)
        if on_error:
            worker.signals.error.connect(on_error)
        
        return worker
    
    def permanently_delete_file_async(self, file_manager, file_id: int, 
                                    on_success: Callable = None, 
                                    on_error: Callable = None) -> Worker:
        """异步永久删除文件
        
        Args:
            file_manager: 文件管理器实例
            file_id: 文件ID
            on_success: 成功回调函数
            on_error: 错误回调函数
            
        Returns:
            Worker: 工作线程实例
        """
        def task():
            return file_manager.permanently_delete_file(file_id)
        
        worker = self.execute_async(task)
        
        if on_success:
            worker.signals.result.connect(lambda result: on_success(result) if result['success'] else on_error(result) if on_error else None)
        if on_error:
            worker.signals.error.connect(on_error)
        
        return worker
    
    def move_file_async(self, file_manager, file_id: int, new_category: str, 
                       on_success: Callable = None, 
                       on_error: Callable = None) -> Worker:
        """异步移动文件
        
        Args:
            file_manager: 文件管理器实例
            file_id: 文件ID
            new_category: 新分类
            on_success: 成功回调函数
            on_error: 错误回调函数
            
        Returns:
            Worker: 工作线程实例
        """
        def task():
            return file_manager.move_file(file_id, new_category)
        
        worker = self.execute_async(task)
        
        if on_success:
            worker.signals.result.connect(lambda result: on_success(result) if result['success'] else on_error(result) if on_error else None)
        if on_error:
            worker.signals.error.connect(on_error)
        
        return worker
    
    def copy_file_async(self, file_manager, file_id: int, new_category: str, 
                       on_success: Callable = None, 
                       on_error: Callable = None) -> Worker:
        """异步复制文件
        
        Args:
            file_manager: 文件管理器实例
            file_id: 文件ID
            new_category: 新分类
            on_success: 成功回调函数
            on_error: 错误回调函数
            
        Returns:
            Worker: 工作线程实例
        """
        def task():
            return file_manager.copy_file(file_id, new_category)
        
        worker = self.execute_async(task)
        
        if on_success:
            worker.signals.result.connect(lambda result: on_success(result) if result['success'] else on_error(result) if on_error else None)
        if on_error:
            worker.signals.error.connect(on_error)
        
        return worker
    
    def rename_file_async(self, file_manager, file_id: int, new_filename: str, 
                         on_success: Callable = None, 
                         on_error: Callable = None) -> Worker:
        """异步重命名文件
        
        Args:
            file_manager: 文件管理器实例
            file_id: 文件ID
            new_filename: 新文件名
            on_success: 成功回调函数
            on_error: 错误回调函数
            
        Returns:
            Worker: 工作线程实例
        """
        def task():
            return file_manager.rename_file(file_id, new_filename)
        
        worker = self.execute_async(task)
        
        if on_success:
            worker.signals.result.connect(lambda result: on_success(result) if result['success'] else on_error(result) if on_error else None)
        if on_error:
            worker.signals.error.connect(on_error)
        
        return worker
    
    def export_file_async(self, file_manager, file_id: int, export_dir: str, 
                         on_success: Callable = None, 
                         on_error: Callable = None) -> Worker:
        """异步导出文件
        
        Args:
            file_manager: 文件管理器实例
            file_id: 文件ID
            export_dir: 导出目录
            on_success: 成功回调函数
            on_error: 错误回调函数
            
        Returns:
            Worker: 工作线程实例
        """
        def task():
            return file_manager.export_file(file_id, export_dir)
        
        worker = self.execute_async(task)
        
        if on_success:
            worker.signals.result.connect(lambda result: on_success(result) if result['success'] else on_error(result) if on_error else None)
        if on_error:
            worker.signals.error.connect(on_error)
        
        return worker
    
    def create_backup_async(self, file_manager, 
                           on_success: Callable = None, 
                           on_error: Callable = None) -> Worker:
        """异步创建备份
        
        Args:
            file_manager: 文件管理器实例
            on_success: 成功回调函数
            on_error: 错误回调函数
            
        Returns:
            Worker: 工作线程实例
        """
        def task():
            return file_manager.create_backup()
        
        worker = self.execute_async(task)
        
        if on_success:
            worker.signals.result.connect(lambda result: on_success(result) if result['success'] else on_error(result) if on_error else None)
        if on_error:
            worker.signals.error.connect(on_error)
        
        return worker
    
    def restore_backup_async(self, file_manager, backup_path: str, 
                           on_success: Callable = None, 
                           on_error: Callable = None) -> Worker:
        """异步恢复备份
        
        Args:
            file_manager: 文件管理器实例
            backup_path: 备份文件路径
            on_success: 成功回调函数
            on_error: 错误回调函数
            
        Returns:
            Worker: 工作线程实例
        """
        def task():
            return file_manager.restore_backup(backup_path)
        
        worker = self.execute_async(task)
        
        if on_success:
            worker.signals.result.connect(lambda result: on_success(result) if result['success'] else on_error(result) if on_error else None)
        if on_error:
            worker.signals.error.connect(on_error)
        
        return worker
    
    def empty_recycle_bin_async(self, file_manager, 
                               on_success: Callable = None, 
                               on_error: Callable = None) -> Worker:
        """异步清空回收站
        
        Args:
            file_manager: 文件管理器实例
            on_success: 成功回调函数
            on_error: 错误回调函数
            
        Returns:
            Worker: 工作线程实例
        """
        def task():
            return file_manager.empty_recycle_bin()
        
        worker = self.execute_async(task)
        
        if on_success:
            worker.signals.result.connect(lambda result: on_success(result) if result['success'] else on_error(result) if on_error else None)
        if on_error:
            worker.signals.error.connect(on_error)
        
        return worker
