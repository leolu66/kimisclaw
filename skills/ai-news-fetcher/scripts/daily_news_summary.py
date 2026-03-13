#!/usr/bin/env python3
"""
AI新闻精简版 - 用于定时任务推送
生成简洁的文本格式，适合飞书消息
"""
import asyncio
import sys
from datetime import datetime
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from spider.config_loader import ConfigLoader
from spider.engine import SpiderEngine


async def fetch_news_summary(max_items_per_site: int = 3):
    """获取AI新闻精简版"""
    loader = ConfigLoader()
    configs = loader.load_all(enabled_only=True)
    
    if not configs:
        return "暂无可用新闻源"
    
    all_items = []
    async with SpiderEngine(default_delay=2) as engine:
        for config in configs:
            site_name = config["site"]["name"]
            try:
                async for item in engine.crawl_site(config, max_items_per_site):
                    all_items.append(item)
            except Exception as e:
                print(f"采集 {site_name} 失败: {e}", file=sys.stderr)
                continue
    
    return format_summary(all_items)


def format_summary(items):
    """格式化为精简文本"""
    if not items:
        return "📭 今日暂无AI新闻"
    
    lines = [
        f"📰 今日AI新闻 ({datetime.now().strftime('%m月%d日')})",
        f"共 {len(items)} 条",
        ""
    ]
    
    # 按来源分组
    from collections import defaultdict
    source_groups = defaultdict(list)
    for item in items:
        source_groups[item.source].append(item)
    
    for source, source_items in sorted(source_groups.items()):
        lines.append(f"\n【{source}】")
        for i, item in enumerate(source_items, 1):
            # 精简格式：标题 + 时间 + 链接
            time_str = item.publish_time_raw or ""
            if time_str:
                lines.append(f"{i}. {item.title} ({time_str})")
            else:
                lines.append(f"{i}. {item.title}")
            lines.append(f"   {item.url}")
            lines.append("")
    
    return "\n".join(lines)


async def main():
    summary = await fetch_news_summary(max_items_per_site=2)
    print(summary)
    return summary


if __name__ == "__main__":
    asyncio.run(main())
