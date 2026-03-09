---
name: ai-news-fetcher
description: |
  AI新闻采集框架 - 支持多站点的可配置新闻爬虫。
  
  触发命令：
  - "获取AI新闻"
  - "采集新闻"
  - "运行ai-news-fetcher"
  
  支持7个AI科技媒体站点：36氪、AiBase、InfoQ、机器之心、AI科技评论、量子位、智东西
version: 2.0
---

# AI新闻采集框架

基于 YAML 配置的通用新闻采集框架，支持 XPath/CSS/JSON SSR 多种提取方式。

## 支持的站点

| 站点 | 技术模式 | 字段覆盖 |
|------|---------|---------|
| **36氪AI** | 列表页 HTML | 标题、摘要、作者、相对时间 |
| **AiBase新闻** | JSON SSR | 标题、摘要、作者、秒级时间戳 |
| **InfoQ AI简报** | JSON SSR | 标题、摘要、外链、作者、时间戳 |
| **机器之心** | 列表页 HTML | 标题、摘要、作者、时间 |
| **AI科技评论** | 列表页 HTML | 标题、摘要、作者、相对时间 |
| **量子位** | 列表页 HTML | 标题、摘要、作者、相对时间 |
| **智东西** | 列表页 HTML | 标题、摘要、作者、时间 |

## 使用方法

### 1. 采集所有站点

```bash
cd /root/.openclaw/workspace/skills/ai-news-fetcher
python3 main.py
```

### 2. 采集指定站点

```bash
python3 spider_cli.py crawl qbitai --max-items 10 --output output/news.json
```

### 3. 测试配置

```bash
python3 spider_cli.py test 36kr
```

### 4. 列出所有站点

```bash
python3 spider_cli.py list-sites
```

## 添加新站点

1. 复制模板：
```bash
cp site-configs/_template.yaml site-configs/yoursite.yaml
```

2. 编辑配置，填写选择器

3. 测试验证：
```bash
python3 spider_cli.py test yoursite
```

## 项目结构

```
ai-news-fetcher/
├── spider/                 # 核心代码
│   ├── config_loader.py    # 配置加载
│   ├── engine.py           # 采集引擎
│   ├── extractors.py       # 字段提取器
│   ├── storage.py          # 存储模块
│   └── monitor.py          # 监控告警
├── site-configs/           # 站点配置
│   ├── _template.yaml      # 配置模板
│   ├── 36kr.yaml
│   ├── aibase.yaml
│   ├── infoq.yaml
│   ├── jiqizhixin.yaml
│   ├── leiphone.yaml
│   ├── qbitai.yaml
│   └── zhidx.yaml
├── main.py                 # 主入口
└── spider_cli.py           # 命令行工具
```

## 配置示例

```yaml
site:
  name: "站点名称"
  base_url: "https://example.com"
  enabled: true

list_page:
  url: "https://example.com/news"
  item_selector:
    type: "css"  # 或 "xpath"
    value: ".news-item"
  
  fields:
    title:
      type: "xpath"
      value: ".//h2/a/text()"
      required: true
    
    link:
      type: "xpath"
      value: ".//h2/a/@href"
      transform: "absolute_url"
```

## 输出格式

支持 JSON、CSV、Markdown 三种格式：

```bash
python3 main.py --format json --output news.json
python3 main.py --format csv --output news.csv
python3 main.py --format md --output news.md
```

## 依赖安装

```bash
pip3 install lxml aiohttp pyyaml click python-dateutil cssselect
```

## 注意事项

- 部分站点有反爬机制，请设置合理的 delay（建议 2-3 秒）
- 36氪、智东西等站点分页可能触发反爬，建议只采集首页
- 输出文件默认保存在 `output/` 目录

## 更新记录

- **v2.0** (2026-03-09) - 完全重写，支持7个站点，配置驱动架构
- **v1.0** (旧版) - 基础版本，已停用（见 ai-news-fetcher-old）
