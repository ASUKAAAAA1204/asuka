#!/usr/bin/env python3
"""
本地化智能文件管理系统 - 主程序入口
"""

from local_file_manager.config.config_manager import ConfigManager
from local_file_manager.core.data_store import DataStore
from local_file_manager.modules.file_import.file_importer import FileImporter
from local_file_manager.modules.file_management.file_manager import FileManager
from local_file_manager.modules.search.search_engine import SearchEngine
from local_file_manager.modules.tagging.tag_manager import TagManager
from local_file_manager.modules.knowledge_graph.graph_viewer import GraphViewer
import os
import time
import argparse

def clear_screen():
    """清屏"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_menu():
    """打印主菜单"""
    print("=====================================")
    print("     本地化智能文件管理系统")
    print("=====================================")
    print("1. 文件管理")
    print("2. 智能搜索")
    print("3. 标签管理")
    print("4. 知识图谱")
    print("5. 系统设置")
    print("6. 退出系统")
    print("=====================================")

def file_management_menu(file_manager, file_importer):
    """文件管理菜单"""
    while True:
        clear_screen()
        print("=====================================")
        print("          文件管理")
        print("=====================================")
        print("1. 导入文件")
        print("2. 查看文件列表")
        print("3. 查看文件信息")
        print("4. 复制文件")
        print("5. 重命名文件")
        print("6. 删除文件")
        print("7. 导出文件")
        print("8. 返回主菜单")
        print("=====================================")
        
        choice = input("请输入选项: ")
        
        if choice == '1':
            # 导入文件
            print("请输入要导入的文件路径（或直接按回车使用默认测试文件）:")
            file_path = input().strip()
            if not file_path:
                file_path = 'test_document.txt'
                print(f"使用默认测试文件: {file_path}")
            
            if os.path.exists(file_path):
                print("正在导入文件...")
                result = file_importer.import_file(file_path)
                if result['success']:
                    print("✓ 文件导入成功")
                    print(f"  文件ID: {result['file_id']}")
                    print(f"  分类: {result['category']}")
                else:
                    print(f"✗ 文件导入失败: {result['message']}")
            else:
                print(f"错误: 文件 {file_path} 不存在")
            input("按回车键继续...")
            
        elif choice == '2':
            # 查看文件列表
            files = file_manager.get_files()
            if files:
                print(f"当前文件数量: {len(files)}")
                print("文件列表:")
                for i, file in enumerate(files):
                    print(f"{i+1}. {file['filename']} (ID: {file['id']}, 分类: {file['category']})")
            else:
                print("没有文件")
            input("按回车键继续...")
            
        elif choice == '3':
            # 查看文件信息
            files = file_manager.get_files()
            if files:
                print("选择文件:")
                for i, file in enumerate(files):
                    print(f"{i+1}. {file['filename']} (ID: {file['id']})")
                try:
                    file_index = int(input()) - 1
                    if 0 <= file_index < len(files):
                        file_id = files[file_index]['id']
                        file_info = file_manager.get_file_info(file_id)
                        if file_info:
                            print("文件信息:")
                            print(f"  文件名: {file_info['filename']}")
                            print(f"  分类: {file_info['category']}")
                            print(f"  文件类型: {file_info['file_type']}")
                            print(f"  大小: {file_info['size']} bytes")
                            print(f"  创建时间: {file_info['created_at']}")
                            print(f"  修改时间: {file_info['modified_at']}")
                            print(f"  存储路径: {file_info['file_path']}")
                        else:
                            print("获取文件信息失败")
                    else:
                        print("无效的文件序号")
                except ValueError:
                    print("请输入有效的数字")
            else:
                print("没有文件")
            input("按回车键继续...")
            
        elif choice == '4':
            # 复制文件
            files = file_manager.get_files()
            if files:
                print("选择要复制的文件:")
                for i, file in enumerate(files):
                    print(f"{i+1}. {file['filename']} (ID: {file['id']})")
                try:
                    file_index = int(input()) - 1
                    if 0 <= file_index < len(files):
                        file_id = files[file_index]['id']
                        print("请输入目标分类:")
                        category = input().strip()
                        result = file_manager.copy_file(file_id, category)
                        if result['success']:
                            print(f"✓ 文件复制成功，新文件ID: {result['file_id']}")
                        else:
                            print(f"✗ 文件复制失败: {result['message']}")
                    else:
                        print("无效的文件序号")
                except ValueError:
                    print("请输入有效的数字")
            else:
                print("没有文件")
            input("按回车键继续...")
            
        elif choice == '5':
            # 重命名文件
            files = file_manager.get_files()
            if files:
                print("选择要重命名的文件:")
                for i, file in enumerate(files):
                    print(f"{i+1}. {file['filename']} (ID: {file['id']})")
                try:
                    file_index = int(input()) - 1
                    if 0 <= file_index < len(files):
                        file_id = files[file_index]['id']
                        print("请输入新文件名:")
                        new_filename = input().strip()
                        result = file_manager.rename_file(file_id, new_filename)
                        if result['success']:
                            print(f"✓ 文件重命名成功")
                        else:
                            print(f"✗ 文件重命名失败: {result['message']}")
                    else:
                        print("无效的文件序号")
                except ValueError:
                    print("请输入有效的数字")
            else:
                print("没有文件")
            input("按回车键继续...")
            
        elif choice == '6':
            # 删除文件
            files = file_manager.get_files()
            if files:
                print("选择要删除的文件:")
                for i, file in enumerate(files):
                    print(f"{i+1}. {file['filename']} (ID: {file['id']})")
                try:
                    file_index = int(input()) - 1
                    if 0 <= file_index < len(files):
                        file_id = files[file_index]['id']
                        result = file_manager.delete_file(file_id)
                        if result['success']:
                            print(f"✓ 文件删除成功")
                        else:
                            print(f"✗ 文件删除失败: {result['message']}")
                    else:
                        print("无效的文件序号")
                except ValueError:
                    print("请输入有效的数字")
            else:
                print("没有文件")
            input("按回车键继续...")
            
        elif choice == '7':
            # 导出文件
            files = file_manager.get_files()
            if files:
                print("选择要导出的文件:")
                for i, file in enumerate(files):
                    print(f"{i+1}. {file['filename']} (ID: {file['id']})")
                try:
                    file_index = int(input()) - 1
                    if 0 <= file_index < len(files):
                        file_id = files[file_index]['id']
                        print("请输入导出目录:")
                        export_dir = input().strip()
                        if not export_dir:
                            export_dir = os.getcwd()
                        result = file_manager.export_file(file_id, export_dir)
                        if result['success']:
                            print(f"✓ 文件导出成功: {result['export_path']}")
                        else:
                            print(f"✗ 文件导出失败: {result['message']}")
                    else:
                        print("无效的文件序号")
                except ValueError:
                    print("请输入有效的数字")
            else:
                print("没有文件")
            input("按回车键继续...")
            
        elif choice == '8':
            # 返回主菜单
            break
        else:
            print("无效选项，请重新输入")
            time.sleep(1)

def search_menu(search_engine):
    """智能搜索菜单"""
    while True:
        clear_screen()
        print("=====================================")
        print("          智能搜索")
        print("=====================================")
        print("1. 关键词搜索")
        print("2. 语义搜索")
        print("3. 关联搜索")
        print("4. 查看搜索历史")
        print("5. 清空搜索历史")
        print("6. 返回主菜单")
        print("=====================================")
        
        choice = input("请输入选项: ")
        
        if choice == '1':
            # 关键词搜索
            print("请输入搜索关键词:")
            query = input().strip()
            if query:
                print("正在搜索...")
                results = search_engine.search(query, search_type='keyword')
                print(f"找到 {len(results)} 个结果:")
                for i, result in enumerate(results[:10]):
                    score = result.get('score', 0)
                    print(f"{i+1}. {result['filename']} (分数: {score:.2f}, 分类: {result['category']})")
            else:
                print("请输入搜索关键词")
            input("按回车键继续...")
            
        elif choice == '2':
            # 语义搜索
            print("请输入搜索关键词:")
            query = input().strip()
            if query:
                print("正在搜索...")
                results = search_engine.search(query, search_type='semantic')
                print(f"找到 {len(results)} 个结果:")
                for i, result in enumerate(results[:10]):
                    score = result.get('score', 0)
                    print(f"{i+1}. {result['filename']} (分数: {score:.2f}, 分类: {result['category']})")
            else:
                print("请输入搜索关键词")
            input("按回车键继续...")
            
        elif choice == '3':
            # 关联搜索
            print("请输入搜索关键词:")
            query = input().strip()
            if query:
                print("正在搜索...")
                results = search_engine.search(query, search_type='related')
                print(f"找到 {len(results)} 个结果:")
                for i, result in enumerate(results[:10]):
                    score = result.get('score', 0)
                    print(f"{i+1}. {result['filename']} (分数: {score:.2f}, 分类: {result['category']})")
            else:
                print("请输入搜索关键词")
            input("按回车键继续...")
            
        elif choice == '4':
            # 查看搜索历史
            history = search_engine.get_search_history()
            if history:
                print("搜索历史:")
                for i, item in enumerate(history):
                    print(f"{i+1}. {item}")
            else:
                print("搜索历史为空")
            input("按回车键继续...")
            
        elif choice == '5':
            # 清空搜索历史
            search_engine.clear_search_history()
            print("搜索历史已清空")
            input("按回车键继续...")
            
        elif choice == '6':
            # 返回主菜单
            break
        else:
            print("无效选项，请重新输入")
            time.sleep(1)

def tag_menu(tag_manager, file_manager):
    """标签管理菜单"""
    while True:
        clear_screen()
        print("=====================================")
        print("          标签管理")
        print("=====================================")
        print("1. 查看所有标签")
        print("2. 添加标签")
        print("3. 删除标签")
        print("4. 为文件添加标签")
        print("5. 从文件移除标签")
        print("6. 查看文件标签")
        print("7. 返回主菜单")
        print("=====================================")
        
        choice = input("请输入选项: ")
        
        if choice == '1':
            # 查看所有标签
            tags = tag_manager.get_all_tags()
            if tags:
                print("所有标签:")
                for tag in tags:
                    tag_info = tag_manager.get_tag_info(tag)
                    print(f"  - {tag} (分组: {tag_info.get('group', '默认')}, 颜色: {tag_info.get('color', '#4A90E2')}")
            else:
                print("没有标签")
            input("按回车键继续...")
            
        elif choice == '2':
            # 添加标签
            print("请输入标签名称:")
            tag_name = input().strip()
            print("请输入标签分组（按回车使用默认分组）:")
            tag_group = input().strip() or '默认'
            print("请输入标签颜色（按回车使用默认颜色）:")
            color = input().strip() or '#4A90E2'
            result = tag_manager.add_tag(tag_name, tag_group, color)
            if result['success']:
                print("✓ 标签添加成功")
            else:
                print(f"✗ 标签添加失败: {result['message']}")
            input("按回车键继续...")
            
        elif choice == '3':
            # 删除标签
            tags = tag_manager.get_all_tags()
            if tags:
                print("选择要删除的标签:")
                for i, tag in enumerate(tags):
                    print(f"{i+1}. {tag}")
                try:
                    tag_index = int(input()) - 1
                    if 0 <= tag_index < len(tags):
                        tag_name = tags[tag_index]
                        result = tag_manager.remove_tag(tag_name)
                        if result['success']:
                            print("✓ 标签删除成功")
                        else:
                            print(f"✗ 标签删除失败: {result['message']}")
                    else:
                        print("无效的标签序号")
                except ValueError:
                    print("请输入有效的数字")
            else:
                print("没有标签")
            input("按回车键继续...")
            
        elif choice == '4':
            # 为文件添加标签
            files = file_manager.get_files()
            if files:
                print("选择文件:")
                for i, file in enumerate(files):
                    print(f"{i+1}. {file['filename']} (ID: {file['id']})")
                try:
                    file_index = int(input()) - 1
                    if 0 <= file_index < len(files):
                        file_id = files[file_index]['id']
                        print("请输入要添加的标签（用逗号分隔）:")
                        tags_input = input().strip()
                        tags = [tag.strip() for tag in tags_input.split(',') if tag.strip()]
                        if tags:
                            result = tag_manager.add_tags_to_file(file_id, tags)
                            if result['success']:
                                print("✓ 标签添加成功")
                            else:
                                print(f"✗ 标签添加失败: {result['message']}")
                        else:
                            print("请输入至少一个标签")
                    else:
                        print("无效的文件序号")
                except ValueError:
                    print("请输入有效的数字")
            else:
                print("没有文件")
            input("按回车键继续...")
            
        elif choice == '5':
            # 从文件移除标签
            files = file_manager.get_files()
            if files:
                print("选择文件:")
                for i, file in enumerate(files):
                    print(f"{i+1}. {file['filename']} (ID: {file['id']})")
                try:
                    file_index = int(input()) - 1
                    if 0 <= file_index < len(files):
                        file_id = files[file_index]['id']
                        tags = tag_manager.get_file_tags(file_id)
                        if tags:
                            print("选择要移除的标签:")
                            for i, tag in enumerate(tags):
                                print(f"{i+1}. {tag}")
                            try:
                                tag_index = int(input()) - 1
                                if 0 <= tag_index < len(tags):
                                    tag_name = tags[tag_index]
                                    result = tag_manager.remove_tags_from_file(file_id, [tag_name])
                                    if result['success']:
                                        print("✓ 标签移除成功")
                                    else:
                                        print(f"✗ 标签移除失败: {result['message']}")
                                else:
                                    print("无效的标签序号")
                            except ValueError:
                                print("请输入有效的数字")
                        else:
                            print("该文件没有标签")
                    else:
                        print("无效的文件序号")
                except ValueError:
                    print("请输入有效的数字")
            else:
                print("没有文件")
            input("按回车键继续...")
            
        elif choice == '6':
            # 查看文件标签
            files = file_manager.get_files()
            if files:
                print("选择文件:")
                for i, file in enumerate(files):
                    print(f"{i+1}. {file['filename']} (ID: {file['id']})")
                try:
                    file_index = int(input()) - 1
                    if 0 <= file_index < len(files):
                        file_id = files[file_index]['id']
                        tags = tag_manager.get_file_tags(file_id)
                        if tags:
                            print(f"文件 {files[file_index]['filename']} 的标签:")
                            for tag in tags:
                                print(f"  - {tag}")
                        else:
                            print("该文件没有标签")
                    else:
                        print("无效的文件序号")
                except ValueError:
                    print("请输入有效的数字")
            else:
                print("没有文件")
            input("按回车键继续...")
            
        elif choice == '7':
            # 返回主菜单
            break
        else:
            print("无效选项，请重新输入")
            time.sleep(1)

def graph_menu(graph_viewer, file_manager):
    """知识图谱菜单"""
    while True:
        clear_screen()
        print("=====================================")
        print("          知识图谱")
        print("=====================================")
        print("1. 生成最近文件的图谱")
        print("2. 生成整个图谱")
        print("3. 生成以指定文件为中心的子图")
        print("4. 查看图谱统计信息")
        print("5. 返回主菜单")
        print("=====================================")
        
        choice = input("请输入选项: ")
        
        if choice == '1':
            # 生成最近文件的图谱
            print("正在生成最近文件的图谱...")
            graph_data = graph_viewer.generate_graph()
            print(f"✓ 生成成功")
            print(f"  节点数量: {len(graph_data['nodes'])}")
            print(f"  边数量: {len(graph_data['edges'])}")
            
            # 显示节点信息
            print("\n节点信息:")
            for node in graph_data['nodes']:
                print(f"  - {node['label']} (类型: {node['file_type']}, 分类: {node['category']})")
            input("按回车键继续...")
            
        elif choice == '2':
            # 生成整个图谱
            print("正在生成整个图谱...")
            graph_data = graph_viewer.generate_graph(include_all=True)
            print(f"✓ 生成成功")
            print(f"  节点数量: {len(graph_data['nodes'])}")
            print(f"  边数量: {len(graph_data['edges'])}")
            input("按回车键继续...")
            
        elif choice == '3':
            # 生成以指定文件为中心的子图
            files = file_manager.get_files()
            if files:
                print("选择中心文件:")
                for i, file in enumerate(files):
                    print(f"{i+1}. {file['filename']} (ID: {file['id']})")
                try:
                    file_index = int(input()) - 1
                    if 0 <= file_index < len(files):
                        file_id = files[file_index]['id']
                        print(f"正在生成以 {files[file_index]['filename']} 为中心的子图...")
                        graph_data = graph_viewer.generate_graph(file_id=file_id)
                        print(f"✓ 生成成功")
                        print(f"  节点数量: {len(graph_data['nodes'])}")
                        print(f"  边数量: {len(graph_data['edges'])}")
                    else:
                        print("无效的文件序号")
                except ValueError:
                    print("请输入有效的数字")
            else:
                print("没有文件")
            input("按回车键继续...")
            
        elif choice == '4':
            # 查看图谱统计信息
            print("正在获取图谱统计信息...")
            stats = graph_viewer.get_graph_stats()
            print(f"✓ 获取成功")
            print(f"  文件数量: {stats['node_count']}")
            print(f"  关联数量: {stats['edge_count']}")
            print(f"  文件类型分布: {stats['file_type_distribution']}")
            print(f"  分类分布: {stats['category_distribution']}")
            input("按回车键继续...")
            
        elif choice == '5':
            # 返回主菜单
            break
        else:
            print("无效选项，请重新输入")
            time.sleep(1)

def settings_menu(config_manager):
    """系统设置菜单"""
    while True:
        clear_screen()
        print("=====================================")
        print("          系统设置")
        print("=====================================")
        print("1. 查看当前配置")
        print("2. 修改存储目录")
        print("3. 修改搜索设置")
        print("4. 重置配置到默认值")
        print("5. 返回主菜单")
        print("=====================================")
        
        choice = input("请输入选项: ")
        
        if choice == '1':
            # 查看当前配置
            print("当前配置:")
            print(f"  存储目录: {config_manager.get('storage.base_dir')}")
            print(f"  索引目录: {config_manager.get('storage.index_dir')}")
            print(f"  备份目录: {config_manager.get('storage.backup_dir')}")
            print(f"  搜索结果限制: {config_manager.get('search.max_results')}")
            print(f"  搜索最小分数: {config_manager.get('search.min_score')}")
            print(f"  主题: {config_manager.get('interface.theme')}")
            print(f"  视图: {config_manager.get('interface.view')}")
            print(f"  语言: {config_manager.get('interface.language')}")
            input("按回车键继续...")
            
        elif choice == '2':
            # 修改存储目录
            print("请输入新的存储目录:")
            new_dir = input().strip()
            if new_dir:
                config_manager.set('storage.base_dir', new_dir)
                print("存储目录已更新")
            else:
                print("请输入有效的目录路径")
            input("按回车键继续...")
            
        elif choice == '3':
            # 修改搜索设置
            print("请输入搜索结果限制（默认: 100）:")
            max_results = input().strip()
            if max_results:
                try:
                    max_results = int(max_results)
                    config_manager.set('search.max_results', max_results)
                except ValueError:
                    print("请输入有效的数字")
            
            print("请输入搜索最小分数（默认: 0.3）:")
            min_score = input().strip()
            if min_score:
                try:
                    min_score = float(min_score)
                    config_manager.set('search.min_score', min_score)
                except ValueError:
                    print("请输入有效的数字")
            
            print("搜索设置已更新")
            input("按回车键继续...")
            
        elif choice == '4':
            # 重置配置到默认值
            config_manager.reset_to_default()
            print("配置已重置到默认值")
            input("按回车键继续...")
            
        elif choice == '5':
            # 返回主菜单
            break
        else:
            print("无效选项，请重新输入")
            time.sleep(1)

def main():
    """主函数"""
    # 初始化系统
    config_manager = ConfigManager()
    index_dir = config_manager.get_index_dir()
    data_store = DataStore(index_dir)
    file_importer = FileImporter(config_manager, data_store)
    file_manager = FileManager(config_manager, data_store)
    search_engine = SearchEngine(config_manager, data_store)
    tag_manager = TagManager(config_manager, data_store)
    graph_viewer = GraphViewer(config_manager, data_store)
    
    while True:
        clear_screen()
        print_menu()
        choice = input("请输入选项: ")
        
        if choice == '1':
            # 文件管理
            file_management_menu(file_manager, file_importer)
        elif choice == '2':
            # 智能搜索
            search_menu(search_engine)
        elif choice == '3':
            # 标签管理
            tag_menu(tag_manager, file_manager)
        elif choice == '4':
            # 知识图谱
            graph_menu(graph_viewer, file_manager)
        elif choice == '5':
            # 系统设置
            settings_menu(config_manager)
        elif choice == '6':
            # 退出系统
            print("退出系统...")
            break
        else:
            print("无效选项，请重新输入")
            time.sleep(1)

if __name__ == "__main__":
    main()
