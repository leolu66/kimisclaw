#!/usr/bin/env python3
"""
NetNotes 标签管理模块
"""

import argparse
import sqlite3
import json
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
DB_PATH = SKILL_DIR / 'articles.db'

# 数据库连接超时（秒）
DB_TIMEOUT = 30


def init_tags_tables():
    """初始化标签相关表"""
    conn = sqlite3.connect(DB_PATH, timeout=DB_TIMEOUT)
    cursor = conn.cursor()
    
    # 标签定义表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 文章-标签关联表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS article_tags (
            article_id INTEGER NOT NULL,
            tag_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (article_id, tag_id),
            FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE,
            FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
        )
    ''')
    
    # 创建索引
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_article_tags_article ON article_tags(article_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_article_tags_tag ON article_tags(tag_id)')
    
    conn.commit()
    conn.close()


def add_tag(name: str, description: str = None) -> dict:
    """添加新标签"""
    conn = sqlite3.connect(DB_PATH, timeout=DB_TIMEOUT)
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            'INSERT INTO tags (name, description) VALUES (?, ?)',
            (name, description)
        )
        tag_id = cursor.lastrowid
        conn.commit()
        return {'success': True, 'id': tag_id, 'name': name}
    except sqlite3.IntegrityError:
        # 标签已存在，获取ID
        cursor.execute('SELECT id FROM tags WHERE name = ?', (name,))
        tag_id = cursor.fetchone()[0]
        return {'success': True, 'id': tag_id, 'name': name, 'exists': True}
    finally:
        conn.close()


def get_or_create_tag(name: str) -> int:
    """获取标签ID，不存在则创建"""
    conn = sqlite3.connect(DB_PATH, timeout=DB_TIMEOUT)
    cursor = conn.cursor()
    
    cursor.execute('SELECT id FROM tags WHERE name = ?', (name,))
    result = cursor.fetchone()
    
    if result:
        tag_id = result[0]
    else:
        cursor.execute('INSERT INTO tags (name) VALUES (?)', (name,))
        tag_id = cursor.lastrowid
        conn.commit()
    
    conn.close()
    return tag_id


def add_tags_to_article(article_id: int, tag_names: list) -> dict:
    """为文章添加标签"""
    conn = sqlite3.connect(DB_PATH, timeout=DB_TIMEOUT)
    cursor = conn.cursor()
    
    added_tags = []
    
    for tag_name in tag_names:
        tag_name = tag_name.strip()
        if not tag_name:
            continue
        
        # 获取或创建标签（内联实现避免嵌套连接）
        cursor.execute('SELECT id FROM tags WHERE name = ?', (tag_name,))
        result = cursor.fetchone()
        
        if result:
            tag_id = result[0]
        else:
            cursor.execute('INSERT INTO tags (name) VALUES (?)', (tag_name,))
            tag_id = cursor.lastrowid
        
        # 建立关联
        try:
            cursor.execute(
                'INSERT INTO article_tags (article_id, tag_id) VALUES (?, ?)',
                (article_id, tag_id)
            )
            added_tags.append(tag_name)
        except sqlite3.IntegrityError:
            # 已有关联，跳过
            pass
    
    conn.commit()
    conn.close()
    
    return {
        'success': True,
        'article_id': article_id,
        'added_tags': added_tags
    }


def list_tags() -> list:
    """列出所有标签及文章数量"""
    conn = sqlite3.connect(DB_PATH, timeout=DB_TIMEOUT)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT t.id, t.name, t.description, COUNT(at.article_id) as article_count
        FROM tags t
        LEFT JOIN article_tags at ON t.id = at.tag_id
        GROUP BY t.id
        ORDER BY article_count DESC, t.name
    ''')
    
    results = cursor.fetchall()
    conn.close()
    
    return [
        {
            'id': row[0],
            'name': row[1],
            'description': row[2],
            'article_count': row[3]
        }
        for row in results
    ]


def get_article_tags(article_id: int) -> list:
    """获取文章的所有标签"""
    conn = sqlite3.connect(DB_PATH, timeout=DB_TIMEOUT)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT t.id, t.name
        FROM tags t
        JOIN article_tags at ON t.id = at.tag_id
        WHERE at.article_id = ?
        ORDER BY t.name
    ''', (article_id,))
    
    results = cursor.fetchall()
    conn.close()
    
    return [{'id': row[0], 'name': row[1]} for row in results]


def search_by_tag(tag_name: str) -> list:
    """通过标签搜索文章"""
    conn = sqlite3.connect(DB_PATH, timeout=DB_TIMEOUT)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT a.id, a.title, a.url, a.category, a.summary, a.fetched_at,
               GROUP_CONCAT(t2.name) as all_tags
        FROM articles a
        JOIN article_tags at ON a.id = at.article_id
        JOIN tags t ON at.tag_id = t.id
        LEFT JOIN article_tags at2 ON a.id = at2.article_id
        LEFT JOIN tags t2 ON at2.tag_id = t2.id
        WHERE t.name = ?
        GROUP BY a.id
        ORDER BY a.fetched_at DESC
    ''', (tag_name,))
    
    results = cursor.fetchall()
    conn.close()
    
    return [
        {
            'id': row[0],
            'title': row[1],
            'url': row[2],
            'category': row[3],
            'summary': row[4],
            'fetched_at': row[5],
            'tags': row[6].split(',') if row[6] else []
        }
        for row in results
    ]


def search_by_tags(tag_names: list, match_all: bool = False) -> list:
    """
    通过多个标签搜索文章
    
    Args:
        tag_names: 标签名列表
        match_all: True=必须包含所有标签, False=包含任一标签
    """
    conn = sqlite3.connect(DB_PATH, timeout=DB_TIMEOUT)
    cursor = conn.cursor()
    
    if match_all:
        # 必须包含所有标签
        placeholders = ','.join(['?'] * len(tag_names))
        cursor.execute(f'''
            SELECT a.id, a.title, a.url, a.category, a.summary, a.fetched_at
            FROM articles a
            JOIN article_tags at ON a.id = at.article_id
            JOIN tags t ON at.tag_id = t.id
            WHERE t.name IN ({placeholders})
            GROUP BY a.id
            HAVING COUNT(DISTINCT t.name) = ?
            ORDER BY a.fetched_at DESC
        ''', tag_names + [len(tag_names)])
    else:
        # 包含任一标签
        placeholders = ','.join(['?'] * len(tag_names))
        cursor.execute(f'''
            SELECT DISTINCT a.id, a.title, a.url, a.category, a.summary, a.fetched_at
            FROM articles a
            JOIN article_tags at ON a.id = at.article_id
            JOIN tags t ON at.tag_id = t.id
            WHERE t.name IN ({placeholders})
            ORDER BY a.fetched_at DESC
        ''', tag_names)
    
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


def remove_tag_from_article(article_id: int, tag_name: str) -> dict:
    """从文章移除标签"""
    conn = sqlite3.connect(DB_PATH, timeout=DB_TIMEOUT)
    cursor = conn.cursor()
    
    cursor.execute('''
        DELETE FROM article_tags 
        WHERE article_id = ? AND tag_id = (SELECT id FROM tags WHERE name = ?)
    ''', (article_id, tag_name))
    
    conn.commit()
    conn.close()
    
    return {'success': True, 'article_id': article_id, 'removed_tag': tag_name}


def main():
    parser = argparse.ArgumentParser(description='NetNotes 标签管理')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # init 命令
    subparsers.add_parser('init', help='初始化标签表')
    
    # add 命令 - 添加标签
    add_parser = subparsers.add_parser('add', help='添加标签')
    add_parser.add_argument('name', help='标签名称')
    add_parser.add_argument('--desc', '-d', help='标签描述')
    
    # tag 命令 - 为文章添加标签
    tag_parser = subparsers.add_parser('tag', help='为文章添加标签')
    tag_parser.add_argument('article_id', type=int, help='文章ID')
    tag_parser.add_argument('tags', help='标签名称，多个用逗号分隔')
    
    # list 命令
    subparsers.add_parser('list', help='列出所有标签')
    
    # article-tags 命令 - 查看文章的标签
    article_tags_parser = subparsers.add_parser('article-tags', help='查看文章的标签')
    article_tags_parser.add_argument('article_id', type=int, help='文章ID')
    
    # search 命令 - 按标签搜索
    search_parser = subparsers.add_parser('search', help='按标签搜索文章')
    search_parser.add_argument('tags', help='标签名称，多个用逗号分隔')
    search_parser.add_argument('--all', '-a', action='store_true', help='匹配所有标签（默认匹配任一）')
    
    # untag 命令 - 移除标签
    untag_parser = subparsers.add_parser('untag', help='从文章移除标签')
    untag_parser.add_argument('article_id', type=int, help='文章ID')
    untag_parser.add_argument('tag', help='要移除的标签名称')
    
    args = parser.parse_args()
    
    if args.command == 'init':
        init_tags_tables()
        print(f"标签表已初始化")
        
    elif args.command == 'add':
        result = add_tag(args.name, args.desc)
        if result.get('exists'):
            print(f"标签 '{args.name}' 已存在 (ID: {result['id']})")
        else:
            print(f"标签添加成功: {result['name']} (ID: {result['id']})")
            
    elif args.command == 'tag':
        tag_names = [t.strip() for t in args.tags.split(',')]
        result = add_tags_to_article(args.article_id, tag_names)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    elif args.command == 'list':
        tags = list_tags()
        print(json.dumps(tags, ensure_ascii=False, indent=2))
        
    elif args.command == 'article-tags':
        tags = get_article_tags(args.article_id)
        print(json.dumps(tags, ensure_ascii=False, indent=2))
        
    elif args.command == 'search':
        tag_names = [t.strip() for t in args.tags.split(',')]
        if len(tag_names) == 1:
            results = search_by_tag(tag_names[0])
        else:
            results = search_by_tags(tag_names, args.all)
        print(json.dumps(results, ensure_ascii=False, indent=2))
        
    elif args.command == 'untag':
        result = remove_tag_from_article(args.article_id, args.tag)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
