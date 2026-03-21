import os
import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from collections import OrderedDict

class DataStore:
    """数据存储模块"""
    
    def __init__(self, index_dir: str):
        """初始化数据存储
        
        Args:
            index_dir: 索引目录
        """
        self.db_path = os.path.join(index_dir, 'file_index.db')
        self._init_database()
        self._file_cache = OrderedDict()  # 文件缓存，使用LRU策略
        self._keyword_cache = OrderedDict()  # 关键词缓存，使用LRU策略
        self._tag_cache = OrderedDict()  # 标签缓存，使用LRU策略
        self._cache_size = 100  # 缓存大小限制
    
    def _init_database(self) -> None:
        """初始化数据库表结构"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 文件表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT UNIQUE NOT NULL,
                    filename TEXT NOT NULL,
                    file_type TEXT NOT NULL,
                    size INTEGER,
                    created_at TEXT,
                    modified_at TEXT,
                    category TEXT,
                    content_hash TEXT,
                    metadata TEXT,
                    added_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 文件内容表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS file_contents (
                    file_id INTEGER PRIMARY KEY,
                    content TEXT,
                    FOREIGN KEY (file_id) REFERENCES files (id) ON DELETE CASCADE
                )
            ''')
            
            # 关键词表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS keywords (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_id INTEGER,
                    keyword TEXT NOT NULL,
                    weight REAL,
                    FOREIGN KEY (file_id) REFERENCES files (id) ON DELETE CASCADE
                )
            ''')
            
            # 标签表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_id INTEGER,
                    tag TEXT NOT NULL,
                    FOREIGN KEY (file_id) REFERENCES files (id) ON DELETE CASCADE
                )
            ''')
            
            # 相似文件表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS similarities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_id1 INTEGER,
                    file_id2 INTEGER,
                    similarity REAL,
                    FOREIGN KEY (file_id1) REFERENCES files (id) ON DELETE CASCADE,
                    FOREIGN KEY (file_id2) REFERENCES files (id) ON DELETE CASCADE,
                    UNIQUE (file_id1, file_id2)
                )
            ''')
            
            # 索引
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_files_filepath ON files (file_path)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_files_category ON files (category)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_keywords_file_id ON keywords (file_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_keywords_keyword ON keywords (keyword)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_tags_file_id ON tags (file_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_tags_tag ON tags (tag)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_similarities_file1 ON similarities (file_id1)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_similarities_file2 ON similarities (file_id2)')
            
            conn.commit()
    
    def add_file(self, file_info: Dict[str, Any]) -> int:
        """添加文件到数据库
        
        Args:
            file_info: 文件信息字典，可包含 'content' 字段
            
        Returns:
            文件ID
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 检查文件是否已存在
            cursor.execute('SELECT id FROM files WHERE file_path = ?', (file_info['file_path'],))
            existing = cursor.fetchone()
            
            if existing:
                # 更新现有文件
                file_id = existing[0]
                cursor.execute('''
                    UPDATE files SET
                        filename = ?,
                        file_type = ?,
                        size = ?,
                        created_at = ?,
                        modified_at = ?,
                        category = ?,
                        content_hash = ?,
                        metadata = ?
                    WHERE id = ?
                ''', (
                    file_info['filename'],
                    file_info['file_type'],
                    file_info.get('size'),
                    file_info.get('created_at'),
                    file_info.get('modified_at'),
                    file_info.get('category'),
                    file_info.get('content_hash'),
                    json.dumps(file_info.get('metadata', {}), ensure_ascii=False),
                    file_id
                ))
            else:
                # 插入新文件
                cursor.execute('''
                    INSERT INTO files (
                        file_path, filename, file_type, size, created_at, modified_at, 
                        category, content_hash, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    file_info['file_path'],
                    file_info['filename'],
                    file_info['file_type'],
                    file_info.get('size'),
                    file_info.get('created_at'),
                    file_info.get('modified_at'),
                    file_info.get('category'),
                    file_info.get('content_hash'),
                    json.dumps(file_info.get('metadata', {}), ensure_ascii=False)
                ))
                file_id = cursor.lastrowid
            
            # 存储文件内容
            content = file_info.get('content')
            if content:
                # 检查内容是否已存在
                cursor.execute('SELECT file_id FROM file_contents WHERE file_id = ?', (file_id,))
                if cursor.fetchone():
                    # 更新内容
                    cursor.execute('UPDATE file_contents SET content = ? WHERE file_id = ?', (content, file_id))
                else:
                    # 插入内容
                    cursor.execute('INSERT INTO file_contents (file_id, content) VALUES (?, ?)', (file_id, content))
            
            conn.commit()
            return file_id
    
    def add_keywords(self, file_id: int, keywords: List[Dict[str, Any]]) -> None:
        """添加关键词到文件
        
        Args:
            file_id: 文件ID
            keywords: 关键词列表，每个元素包含 'keyword' 和 'weight'
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 删除现有关键词
            cursor.execute('DELETE FROM keywords WHERE file_id = ?', (file_id,))
            
            # 插入新关键词
            for kw in keywords:
                cursor.execute(
                    'INSERT INTO keywords (file_id, keyword, weight) VALUES (?, ?, ?)',
                    (file_id, kw['keyword'], kw.get('weight', 1.0))
                )
            
            conn.commit()
    
    def add_tags(self, file_id: int, tags: List[str]) -> None:
        """添加标签到文件
        
        Args:
            file_id: 文件ID
            tags: 标签列表
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 删除现有标签
            cursor.execute('DELETE FROM tags WHERE file_id = ?', (file_id,))
            
            # 插入新标签
            for tag in tags:
                cursor.execute(
                    'INSERT INTO tags (file_id, tag) VALUES (?, ?)',
                    (file_id, tag)
                )
            
            conn.commit()
    
    def add_similarity(self, file_id1: int, file_id2: int, similarity: float) -> None:
        """添加文件相似度
        
        Args:
            file_id1: 文件1 ID
            file_id2: 文件2 ID
            similarity: 相似度分数
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute(
                    'INSERT INTO similarities (file_id1, file_id2, similarity) VALUES (?, ?, ?)',
                    (file_id1, file_id2, similarity)
                )
                conn.commit()
            except sqlite3.IntegrityError:
                # 已存在的相似度记录，忽略
                pass
    
    def get_file(self, file_id: int) -> Optional[Dict[str, Any]]:
        """获取文件信息
        
        Args:
            file_id: 文件ID
            
        Returns:
            文件信息字典
        """
        # 检查缓存
        if file_id in self._file_cache:
            # 将访问的项移到字典末尾（LRU策略）
            self._file_cache.move_to_end(file_id)
            return self._file_cache[file_id]
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM files WHERE id = ?', (file_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            file_info = self._row_to_file_info(row)
            # 添加标签信息
            file_info['tags'] = self.get_file_tags(file_id)
            
            # 缓存结果
            self._file_cache[file_id] = file_info
            # 将新项移到字典末尾
            self._file_cache.move_to_end(file_id)
            # 限制缓存大小
            if len(self._file_cache) > self._cache_size:
                # 删除最旧的缓存项（字典开头）
                self._file_cache.popitem(last=False)
            
            return file_info
    
    def get_file_by_path(self, file_path: str) -> Optional[Dict[str, Any]]:
        """通过路径获取文件信息
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件信息字典
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM files WHERE file_path = ?', (file_path,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return self._row_to_file_info(row)
    
    def get_files(self, category: Optional[str] = None, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """获取文件列表
        
        Args:
            category: 分类，None表示所有分类
            limit: 限制数量
            offset: 偏移量
            
        Returns:
            文件信息列表
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if category:
                cursor.execute(
                    'SELECT * FROM files WHERE category = ? ORDER BY added_at DESC LIMIT ? OFFSET ?',
                    (category, limit, offset)
                )
            else:
                cursor.execute(
                    'SELECT * FROM files ORDER BY added_at DESC LIMIT ? OFFSET ?',
                    (limit, offset)
                )
            
            rows = cursor.fetchall()
            file_infos = []
            
            # 批量获取标签信息，减少数据库查询次数
            file_ids = [row[0] for row in rows]
            tags_map = {}
            if file_ids:
                cursor.execute('SELECT file_id, tag FROM tags WHERE file_id IN ({})'.format(','.join('?' for _ in file_ids)), file_ids)
                for file_id, tag in cursor.fetchall():
                    if file_id not in tags_map:
                        tags_map[file_id] = []
                    tags_map[file_id].append(tag)
            
            for row in rows:
                file_info = self._row_to_file_info(row)
                # 添加标签信息
                file_info['tags'] = tags_map.get(file_info['id'], [])
                file_infos.append(file_info)
            return file_infos
    
    def get_file_keywords(self, file_id: int) -> List[Dict[str, Any]]:
        """获取文件的关键词
        
        Args:
            file_id: 文件ID
            
        Returns:
            关键词列表
        """
        # 检查缓存
        if file_id in self._keyword_cache:
            # 将访问的项移到字典末尾（LRU策略）
            self._keyword_cache.move_to_end(file_id)
            return self._keyword_cache[file_id]
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT keyword, weight FROM keywords WHERE file_id = ? ORDER BY weight DESC', (file_id,))
            rows = cursor.fetchall()
            
            keywords = [{'keyword': row[0], 'weight': row[1]} for row in rows]
            
            # 缓存结果
            self._keyword_cache[file_id] = keywords
            # 将新项移到字典末尾
            self._keyword_cache.move_to_end(file_id)
            # 限制缓存大小
            if len(self._keyword_cache) > self._cache_size:
                # 删除最旧的缓存项（字典开头）
                self._keyword_cache.popitem(last=False)
            
            return keywords
    
    def get_file_tags(self, file_id: int) -> List[str]:
        """获取文件的标签
        
        Args:
            file_id: 文件ID
            
        Returns:
            标签列表
        """
        # 检查缓存
        if file_id in self._tag_cache:
            # 将访问的项移到字典末尾（LRU策略）
            self._tag_cache.move_to_end(file_id)
            return self._tag_cache[file_id]
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT tag FROM tags WHERE file_id = ?', (file_id,))
            rows = cursor.fetchall()
            
            tags = [row[0] for row in rows]
            
            # 缓存结果
            self._tag_cache[file_id] = tags
            # 将新项移到字典末尾
            self._tag_cache.move_to_end(file_id)
            # 限制缓存大小
            if len(self._tag_cache) > self._cache_size:
                # 删除最旧的缓存项（字典开头）
                self._tag_cache.popitem(last=False)
            
            return tags
    
    def get_similar_files(self, file_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """获取相似文件
        
        Args:
            file_id: 文件ID
            limit: 限制数量
            
        Returns:
            相似文件列表，包含相似度分数
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT f.*, s.similarity FROM files f
                JOIN similarities s ON f.id = s.file_id2
                WHERE s.file_id1 = ?
                ORDER BY s.similarity DESC
                LIMIT ?
            ''', (file_id, limit))
            
            rows = cursor.fetchall()
            result = []
            for row in rows:
                file_info = self._row_to_file_info(row[:-1])
                file_info['similarity'] = row[-1]
                result.append(file_info)
            
            return result
    
    def delete_file(self, file_id: int) -> None:
        """删除文件
        
        Args:
            file_id: 文件ID
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM files WHERE id = ?', (file_id,))
            conn.commit()
    
    def get_file_content(self, file_id: int) -> Optional[str]:
        """获取文件内容
        
        Args:
            file_id: 文件ID
            
        Returns:
            文件内容字符串，若不存在则返回None
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT content FROM file_contents WHERE file_id = ?', (file_id,))
            row = cursor.fetchone()
            
            return row[0] if row else None
    
    def update_file_content(self, file_id: int, content: str) -> None:
        """更新文件内容
        
        Args:
            file_id: 文件ID
            content: 文件内容
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 检查内容是否已存在
            cursor.execute('SELECT file_id FROM file_contents WHERE file_id = ?', (file_id,))
            if cursor.fetchone():
                # 更新内容
                cursor.execute('UPDATE file_contents SET content = ? WHERE file_id = ?', (content, file_id))
            else:
                # 插入内容
                cursor.execute('INSERT INTO file_contents (file_id, content) VALUES (?, ?)', (file_id, content))
            
            conn.commit()
    
    def search_content(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """搜索文件内容
        
        Args:
            query: 搜索关键词
            limit: 限制数量
            
        Returns:
            搜索结果列表
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 搜索文件内容
            cursor.execute('''
                SELECT f.* FROM files f
                JOIN file_contents fc ON f.id = fc.file_id
                WHERE fc.content LIKE ?
                ORDER BY f.added_at DESC
                LIMIT ?
            ''', (f'%{query}%', limit))
            
            rows = cursor.fetchall()
            return [self._row_to_file_info(row) for row in rows]
    
    def search_files(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """搜索文件
        
        Args:
            query: 搜索关键词
            limit: 限制数量
            
        Returns:
            搜索结果列表
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 优化搜索查询，使用UNION ALL替代LEFT JOIN，减少查询复杂度
            cursor.execute('''
                SELECT f.* FROM files f WHERE f.filename LIKE ?
                UNION ALL
                SELECT f.* FROM files f JOIN keywords k ON f.id = k.file_id WHERE k.keyword LIKE ?
                UNION ALL
                SELECT f.* FROM files f JOIN tags t ON f.id = t.file_id WHERE t.tag LIKE ?
                GROUP BY f.id
                ORDER BY MAX(f.added_at) DESC
                LIMIT ?
            ''', (f'%{query}%', f'%{query}%', f'%{query}%', limit))
            
            rows = cursor.fetchall()
            return [self._row_to_file_info(row) for row in rows]
    
    def _row_to_file_info(self, row: tuple) -> Dict[str, Any]:
        """将数据库行转换为文件信息字典
        
        Args:
            row: 数据库行
            
        Returns:
            文件信息字典
        """
        return {
            'id': row[0],
            'file_path': row[1],
            'filename': row[2],
            'file_type': row[3],
            'size': row[4],
            'created_at': row[5],
            'modified_at': row[6],
            'category': row[7],
            'content_hash': row[8],
            'metadata': json.loads(row[9]) if row[9] else {},
            'added_at': row[10]
        }
