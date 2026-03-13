#!/usr/bin/env python3
"""
NetNotes 文章保存和入库模块
"""

import argparse
import sqlite3
import json
import sys
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse

# 技能根目录
SKILL_DIR = Path(__file__).parent.parent
NOTES_DIR = SKILL_DIR / 'notes'
DB_PATH = SKILL_DIR / 'articles.db'
DB_TIMEOUT = 30


def init_database():
    """初始化 SQLite 数据库"""
    conn = sqlite3.connect(DB_PATH, timeout=DB_TIMEOUT)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            url TEXT NOT NULL,
            category TEXT NOT NULL,
            summary TEXT,
            file_path TEXT,
            fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            file_size INTEGER
        )
    ''')
    
    # 创建索引
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_category ON articles(category)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_url ON articles(url)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_fetched_at ON articles(fetched_at)')
    
    conn.commit()
    conn.close()


def generate_summary(content: str, max_length: int = 100) -> str:
    """
    生成文章摘要（简单实现）
    实际使用中，可以让大模型生成更准确的摘要
    """
    # 清理内容
    lines = [line.strip() for line in content.split('\n') if line.strip()]
    text = ' '.join(lines)
    
    # 去除多余空格
    text = ' '.join(text.split())
    
    # 截取前 max_length 个字符
    if len(text) <= max_length:
        return text
    
    # 尝试在句子边界截断
    truncated = text[:max_length]
    last_period = max(truncated.rfind('。'), truncated.rfind('.'), truncated.rfind('!'), truncated.rfind('?'))
    
    if last_period > max_length * 0.7:  # 如果找到句子边界且在合理位置
        return truncated[:last_period + 1]
    
    return truncated + '...'


def save_article(title: str, content: str, url: str, category: str, summary: str = None, tags: list = None) -> dict:
    """
    保存文章到文件并记录到数据库
    
    Args:
        tags: 标签列表，如 ['OpenClaw', '教程']
    
    Returns:
        dict: 包含保存结果信息
    """
    # 确保目录存在
    category_dir = NOTES_DIR / category
    category_dir.mkdir(parents=True, exist_ok=True)
    
    # 生成文件名（处理重名）
    safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
    if len(safe_title) > 80:
        safe_title = safe_title[:80]
    
    filename = f"{safe_title}.md"
    file_path = category_dir / filename
    
    # 处理重名文件
    counter = 1
    original_file_path = file_path
    while file_path.exists():
        filename = f"{safe_title}_{counter}.md"
        file_path = category_dir / filename
        counter += 1
    
    # 生成摘要（如果没有提供）
    if summary is None:
        summary = generate_summary(content)
    
    # 准备 Markdown 内容
    md_content = f"""# {title}

**来源**: {url}  
**分类**: {category}  
**保存时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 概要

{summary}

---

## 正文

{content}
"""
    
    # 写入文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    file_size = file_path.stat().st_size
    
    # 记录到数据库
    conn = sqlite3.connect(DB_PATH, timeout=DB_TIMEOUT)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO articles (title, url, category, summary, file_path, file_size)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (title, url, category, summary, str(file_path.relative_to(SKILL_DIR)), file_size))
    
    article_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    # 处理标签
    tag_result = None
    if tags:
        # 动态导入避免循环依赖
        import importlib.util
        spec = importlib.util.spec_from_file_location("tag_manager", Path(__file__).parent / "tag_manager.py")
        tag_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(tag_module)
        tag_result = tag_module.add_tags_to_article(article_id, tags)
    
    result = {
        'success': True,
        'id': article_id,
        'title': title,
        'category': category,
        'file_path': str(file_path),
        'summary': summary,
        'file_size': file_size
    }
    
    if tag_result:
        result['tags'] = tag_result['added_tags']
    
    return result


def list_articles(category: str = None, limit: int = 20, with_tags: bool = True) -> list:
    """列出已保存的文章"""
    conn = sqlite3.connect(DB_PATH, timeout=DB_TIMEOUT)
    cursor = conn.cursor()
    
    if category:
        cursor.execute('''
            SELECT id, title, url, category, summary, fetched_at 
            FROM articles 
            WHERE category = ?
            ORDER BY fetched_at DESC
            LIMIT ?
        ''', (category, limit))
    else:
        cursor.execute('''
            SELECT id, title, url, category, summary, fetched_at 
            FROM articles 
            ORDER BY fetched_at DESC
            LIMIT ?
        ''', (limit,))
    
    results = cursor.fetchall()
    
    articles = []
    for row in results:
        article = {
            'id': row[0],
            'title': row[1],
            'url': row[2],
            'category': row[3],
            'summary': row[4],
            'fetched_at': row[5]
        }
        
        # 获取标签
        if with_tags:
            cursor.execute('''
                SELECT t.name 
                FROM tags t
                JOIN article_tags at ON t.id = at.tag_id
                WHERE at.article_id = ?
                ORDER BY t.name
            ''', (row[0],))
            tags = [t[0] for t in cursor.fetchall()]
            article['tags'] = tags
        
        articles.append(article)
    
    conn.close()
    return articles


def search_articles(query: str) -> list:
    """搜索文章"""
    conn = sqlite3.connect(DB_PATH, timeout=DB_TIMEOUT)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, title, url, category, summary, fetched_at 
        FROM articles 
        WHERE title LIKE ? OR summary LIKE ? OR url LIKE ?
        ORDER BY fetched_at DESC
    ''', (f'%{query}%', f'%{query}%', f'%{query}%'))
    
    results = cursor.fetchall()
    conn.close()
    
    return [
        {
            'id': row[0],
            'title': row[1],
            'url': row[2],
            'category': row[3],
            'summary': row[4],
            'fetched_at': row[5]
        }
        for row in results
    ]


def main():
    parser = argparse.ArgumentParser(description='保存和管理文章')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # init 命令
    subparsers.add_parser('init', help='初始化数据库')
    
    # save 命令
    save_parser = subparsers.add_parser('save', help='保存文章')
    save_parser.add_argument('--title', '-t', required=True, help='文章标题')
    save_parser.add_argument('--content', '-c', required=True, help='文章内容（文件路径或直接文本）')
    save_parser.add_argument('--url', '-u', required=True, help='文章URL')
    save_parser.add_argument('--category', '-cat', required=True, help='分类目录')
    save_parser.add_argument('--summary', '-s', help='文章摘要（可选）')
    save_parser.add_argument('--tags', help='标签，多个用逗号分隔（如：OpenClaw,教程）')
    save_parser.add_argument('--content-file', '-f', action='store_true', help='表示content参数是文件路径')
    
    # list 命令
    list_parser = subparsers.add_parser('list', help='列出文章')
    list_parser.add_argument('--category', '-c', help='按分类筛选')
    list_parser.add_argument('--limit', '-n', type=int, default=20, help='限制数量')
    
    # search 命令
    search_parser = subparsers.add_parser('search', help='搜索文章')
    search_parser.add_argument('query', help='搜索关键词')
    
    args = parser.parse_args()
    
    if args.command == 'init':
        init_database()
        print(f"数据库已初始化: {DB_PATH}")
        
    elif args.command == 'save':
        # 读取内容
        if args.content_file:
            with open(args.content, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            content = args.content
        
        # 解析标签
        tags = None
        if args.tags:
            tags = [t.strip() for t in args.tags.split(',') if t.strip()]
        
        result = save_article(args.title, content, args.url, args.category, args.summary, tags)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    elif args.command == 'list':
        results = list_articles(args.category, args.limit)
        print(json.dumps(results, ensure_ascii=False, indent=2))
        
    elif args.command == 'search':
        results = search_articles(args.query)
        print(json.dumps(results, ensure_ascii=False, indent=2))
        
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
