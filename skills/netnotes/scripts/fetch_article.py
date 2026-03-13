#!/usr/bin/env python3
"""
NetNotes 文章抓取模块
支持普通 requests 和 playwright 两种模式
"""

import argparse
import sys
import re
from urllib.parse import urlparse
from pathlib import Path

try:
    import requests
    from bs4 import BeautifulSoup
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


def clean_filename(title: str) -> str:
    """清理标题，生成安全的文件名"""
    # 移除或替换不安全的字符
    title = re.sub(r'[<>:"/\\|?*]', '', title)
    title = title.strip()
    # 限制长度
    if len(title) > 100:
        title = title[:100]
    return title


def extract_with_requests(url: str) -> dict:
    """使用 requests + BeautifulSoup 提取文章"""
    if not REQUESTS_AVAILABLE:
        raise ImportError("requests 和 beautifulsoup4 未安装")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    }
    
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    response.encoding = response.apparent_encoding or 'utf-8'
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 提取标题
    title = soup.title.string if soup.title else 'Untitled'
    
    # 尝试提取正文内容（常见的文章容器选择器）
    content_selectors = [
        'article',
        '.article-content',
        '.post-content',
        '.entry-content',
        '.content',
        'main',
        '[role="main"]',
        '.article-body',
        '.post-body',
    ]
    
    content = None
    for selector in content_selectors:
        element = soup.select_one(selector)
        if element:
            content = element.get_text(separator='\n', strip=True)
            break
    
    # 如果找不到，使用 body
    if not content:
        content = soup.body.get_text(separator='\n', strip=True) if soup.body else ''
    
    return {
        'title': clean_filename(title),
        'content': content,
        'url': url,
        'method': 'requests'
    }


def extract_with_playwright(url: str) -> dict:
    """使用 playwright 提取文章（用于动态页面/反爬）"""
    if not PLAYWRIGHT_AVAILABLE:
        raise ImportError("playwright 未安装，请先运行: pip install playwright && playwright install chromium")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = context.new_page()
        
        try:
            page.goto(url, wait_until='networkidle', timeout=30000)
            page.wait_for_load_state('domcontentloaded')
            
            # 提取标题
            title = page.title()
            
            # 尝试提取正文内容
            content_selectors = [
                'article',
                '.article-content',
                '.post-content',
                '.entry-content',
                '.content',
                'main',
                '[role="main"]',
                '.article-body',
                '.post-body',
            ]
            
            content = None
            for selector in content_selectors:
                element = page.query_selector(selector)
                if element:
                    content = element.inner_text()
                    break
            
            # 如果找不到，使用 body
            if not content:
                body = page.query_selector('body')
                content = body.inner_text() if body else ''
            
            return {
                'title': clean_filename(title),
                'content': content,
                'url': url,
                'method': 'playwright'
            }
            
        finally:
            context.close()
            browser.close()


def extract_article(url: str, use_playwright: bool = False) -> dict:
    """
    提取文章内容
    
    Args:
        url: 文章 URL
        use_playwright: 是否使用 playwright（用于反爬/动态页面）
    
    Returns:
        dict: 包含 title, content, url, method
    """
    if use_playwright:
        return extract_with_playwright(url)
    else:
        try:
            return extract_with_requests(url)
        except Exception as e:
            print(f"普通模式失败: {e}", file=sys.stderr)
            if PLAYWRIGHT_AVAILABLE:
                print("尝试使用 playwright 模式...", file=sys.stderr)
                return extract_with_playwright(url)
            raise


def main():
    parser = argparse.ArgumentParser(description='抓取网页文章')
    parser.add_argument('url', help='文章 URL')
    parser.add_argument('--playwright', '-p', action='store_true', help='使用 playwright 模式（用于反爬）')
    parser.add_argument('--output', '-o', help='输出文件路径（默认输出到 stdout）')
    
    args = parser.parse_args()
    
    try:
        result = extract_article(args.url, args.playwright)
        
        md_content = f"""# {result['title']}

**来源**: {result['url']}  
**抓取方式**: {result['method']}  
**抓取时间**: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

{result['content']}
"""
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(md_content)
            print(f"已保存到: {args.output}")
        else:
            print(md_content)
            
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
