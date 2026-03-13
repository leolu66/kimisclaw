#!/usr/bin/env python3
"""
NetNotes 组合查询模块 - 支持多条件检索 + 交互式查看
"""

import argparse
import sqlite3
import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime, timedelta

SKILL_DIR = Path(__file__).parent.parent
DB_PATH = SKILL_DIR / 'articles.db'
DB_TIMEOUT = 30


def build_query(
    category: str = None,
    tags: list = None,
    keyword: str = None,
    date_from: str = None,
    date_to: str = None
) -> tuple:
    """
    构建组合查询SQL
    
    Returns:
        (sql, params)
    """
    # 基础查询
    if tags:
        # 需要关联标签表
        sql = '''
            SELECT DISTINCT a.id, a.title, a.url, a.category, a.summary, 
                           a.fetched_at, a.file_path
            FROM articles a
            JOIN article_tags at ON a.id = at.article_id
            JOIN tags t ON at.tag_id = t.id
            WHERE 1=1
        '''
    else:
        sql = '''
            SELECT a.id, a.title, a.url, a.category, a.summary, 
                   a.fetched_at, a.file_path
            FROM articles a
            WHERE 1=1
        '''
    
    params = []
    
    # 分类筛选
    if category:
        sql += ' AND a.category = ?'
        params.append(category)
    
    # 标签筛选
    if tags:
        placeholders = ','.join(['?'] * len(tags))
        sql += f' AND t.name IN ({placeholders})'
        params.extend(tags)
        # 如果要匹配所有标签，需要GROUP BY + HAVING
        if len(tags) > 1:
            sql += '''
                GROUP BY a.id
                HAVING COUNT(DISTINCT t.name) = ?
            '''
            params.append(len(tags))
    
    # 关键词搜索（标题、摘要、URL）
    if keyword:
        sql += ' AND (a.title LIKE ? OR a.summary LIKE ? OR a.url LIKE ?)'
        like_pattern = f'%{keyword}%'
        params.extend([like_pattern, like_pattern, like_pattern])
    
    # 日期范围
    if date_from:
        sql += ' AND a.fetched_at >= ?'
        params.append(date_from)
    if date_to:
        sql += ' AND a.fetched_at <= ?'
        params.append(date_to + ' 23:59:59')  # 包含当天
    
    # 排序
    sql += ' ORDER BY a.fetched_at DESC'
    
    return sql, params


def search_articles(
    category: str = None,
    tags: list = None,
    keyword: str = None,
    date_from: str = None,
    date_to: str = None,
    limit: int = 50
) -> list:
    """执行组合查询"""
    conn = sqlite3.connect(DB_PATH, timeout=DB_TIMEOUT)
    cursor = conn.cursor()
    
    sql, params = build_query(category, tags, keyword, date_from, date_to)
    
    if limit:
        sql += ' LIMIT ?'
        params.append(limit)
    
    cursor.execute(sql, params)
    results = cursor.fetchall()
    
    articles = []
    for row in results:
        article = {
            'id': row[0],
            'title': row[1],
            'url': row[2],
            'category': row[3],
            'summary': row[4][:150] + '...' if row[4] and len(row[4]) > 150 else row[4],
            'fetched_at': row[5],
            'file_path': row[6]
        }
        
        # 获取标签
        cursor.execute('''
            SELECT t.name FROM tags t
            JOIN article_tags at ON t.id = at.tag_id
            WHERE at.article_id = ?
        ''', (row[0],))
        article['tags'] = [t[0] for t in cursor.fetchall()]
        
        articles.append(article)
    
    conn.close()
    return articles


def format_results(articles: list, show_details: bool = False) -> str:
    """格式化查询结果为表格"""
    if not articles:
        return "未找到匹配的文章。"
    
    lines = []
    lines.append("=" * 100)
    lines.append(f"找到 {len(articles)} 篇文章")
    lines.append("=" * 100)
    lines.append("")
    
    for i, article in enumerate(articles, 1):
        lines.append(f"[{i}] {article['title']}")
        lines.append(f"    分类: {article['category']} | 日期: {article['fetched_at']}")
        if article['tags']:
            lines.append(f"    标签: {', '.join(article['tags'])}")
        if show_details:
            lines.append(f"    URL: {article['url']}")
            if article['summary']:
                lines.append(f"    摘要: {article['summary']}")
        lines.append("")
    
    lines.append("-" * 100)
    lines.append("输入编号查看文章（如: 1,2,3），或输入 'q' 退出")
    
    return '\n'.join(lines)


def open_article(file_path: str):
    """打开文章文件"""
    full_path = SKILL_DIR / file_path
    if not full_path.exists():
        print(f"文件不存在: {full_path}")
        return False
    
    # 使用系统默认编辑器打开
    try:
        if sys.platform == 'darwin':  # macOS
            subprocess.run(['open', str(full_path)], check=True)
        elif sys.platform == 'win32':  # Windows
            subprocess.run(['start', str(full_path)], shell=True, check=True)
        else:  # Linux
            subprocess.run(['cat', str(full_path)], check=True)
        return True
    except Exception as e:
        print(f"打开文件失败: {e}")
        # 尝试直接打印内容
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                print("\n" + "=" * 80)
                print(f"文件内容: {file_path}")
                print("=" * 80)
                print(f.read())
                print("=" * 80 + "\n")
            return True
        except Exception as e2:
            print(f"读取文件失败: {e2}")
            return False


def interactive_mode(articles: list):
    """交互模式 - 选择文章查看"""
    if not articles:
        print("没有文章可查看。")
        return
    
    while True:
        print("\n请输入要查看的文章编号（多个用逗号分隔，如: 1,2,3），或输入 'q' 退出:")
        try:
            user_input = input("> ").strip()
        except EOFError:
            break
        
        if user_input.lower() in ('q', 'quit', 'exit', ''):
            break
        
        # 解析编号
        try:
            indices = [int(x.strip()) for x in user_input.split(',')]
        except ValueError:
            print("输入无效，请输入数字编号。")
            continue
        
        # 验证并打开
        for idx in indices:
            if idx < 1 or idx > len(articles):
                print(f"编号 {idx} 超出范围（1-{len(articles)}）")
                continue
            
            article = articles[idx - 1]
            print(f"\n正在打开: [{idx}] {article['title']}")
            open_article(article['file_path'])


def main():
    parser = argparse.ArgumentParser(
        description='NetNotes 组合查询 - 支持分类、标签、关键词、日期范围组合检索',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  # 查询 AI 分类的所有文章
  python search.py --category AI
  
  # 查询带有"教程"标签的文章
  python search.py --tags 教程
  
  # 组合查询：AI分类 + OpenClaw标签 + 关键词"原理"
  python search.py -c AI --tags OpenClaw -k 原理
  
  # 查询最近7天的文章
  python search.py --days 7
  
  # 查询指定日期范围
  python search.py --from 2026-03-01 --to 2026-03-14
  
  # 交互模式（查询后可选择查看文章）
  python search.py -c AI -i
        '''
    )
    
    # 查询条件
    parser.add_argument('-c', '--category', help='按分类筛选（如: AI, 运营商, 管理）')
    parser.add_argument('-t', '--tags', help='按标签筛选，多个用逗号分隔（如: OpenClaw,教程）')
    parser.add_argument('-k', '--keyword', help='关键词搜索（标题/摘要/URL）')
    parser.add_argument('--from', dest='date_from', help='起始日期（YYYY-MM-DD）')
    parser.add_argument('--to', dest='date_to', help='结束日期（YYYY-MM-DD）')
    parser.add_argument('--days', type=int, help='最近N天（如: 7, 30）')
    
    # 输出选项
    parser.add_argument('-i', '--interactive', action='store_true', 
                        help='交互模式：查询后可选择查看文章')
    parser.add_argument('-d', '--details', action='store_true',
                        help='显示详细信息（URL、摘要）')
    parser.add_argument('--json', action='store_true',
                        help='输出JSON格式')
    parser.add_argument('-n', '--limit', type=int, default=50,
                        help='限制结果数量（默认50）')
    
    args = parser.parse_args()
    
    # 处理日期参数
    date_from = args.date_from
    date_to = args.date_to
    
    if args.days and not (date_from or date_to):
        # 最近N天
        end = datetime.now()
        start = end - timedelta(days=args.days)
        date_to = end.strftime('%Y-%m-%d')
        date_from = start.strftime('%Y-%m-%d')
    
    # 解析标签
    tags = None
    if args.tags:
        tags = [t.strip() for t in args.tags.split(',') if t.strip()]
    
    # 执行查询
    articles = search_articles(
        category=args.category,
        tags=tags,
        keyword=args.keyword,
        date_from=date_from,
        date_to=date_to,
        limit=args.limit
    )
    
    # 输出结果
    if args.json:
        print(json.dumps(articles, ensure_ascii=False, indent=2))
    else:
        print(format_results(articles, args.details))
    
    # 交互模式
    if args.interactive and articles:
        interactive_mode(articles)
    
    return len(articles)


if __name__ == '__main__':
    sys.exit(main() or 0)
