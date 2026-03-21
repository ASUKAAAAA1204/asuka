import argparse
import json
import os
from document_analyzer import DocumentAnalyzer


def main():
    """命令行工具主函数"""
    parser = argparse.ArgumentParser(description='文档内容概括与关键词提取工具')
    
    # 位置参数
    parser.add_argument('file', nargs='*', help='要分析的文件路径')
    
    # 选项参数
    parser.add_argument('--format', choices=['text', 'json'], default='text', help='输出格式')
    parser.add_argument('--keywords', type=int, default=10, help='关键词数量')
    parser.add_argument('--summary', type=int, help='摘要句子数')
    parser.add_argument('--batch', action='store_true', help='批量处理模式')
    
    args = parser.parse_args()
    
    # 检查文件参数
    if not args.file:
        parser.print_help()
        return
    
    analyzer = DocumentAnalyzer()
    
    # 处理文件
    for file_path in args.file:
        if not os.path.exists(file_path):
            print(f"错误: 文件不存在: {file_path}")
            continue
        
        try:
            # 分析文档
            result = analyzer.analyze(file_path)
            
            # 输出结果
            if args.format == 'json':
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                # 文本格式输出
                print(f"\n=== 文档分析结果: {result['metadata']['filename']} ===")
                print(f"文件大小: {result['metadata']['file_size']} 字节")
                print(f"字数: {result['metadata']['word_count']}")
                if 'pages' in result['metadata']:
                    print(f"页数: {result['metadata']['pages']}")
                print(f"\n=== 摘要 ===")
                print(result['summary'])
                print(f"\n=== 关键词 ===")
                for keyword in result['keywords'][:args.keywords]:
                    print(f"{keyword['keyword']} (权重: {keyword['weight']:.4f})")
                print(f"\n=== 统计信息 ===")
                print(f"总句子数: {result['statistics']['total_sentences']}")
                print(f"摘要句子数: {result['statistics']['summary_sentences']}")
                print(f"关键词数: {result['statistics']['keyword_count']}")
                print("=" * 50)
                
        except Exception as e:
            print(f"分析文件 {file_path} 时出错: {str(e)}")


if __name__ == '__main__':
    main()
