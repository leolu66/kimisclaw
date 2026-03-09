---
name: ai-news-fetcher
description: |
  获取国内权威AI科技网站的最新新闻，并以带摘要的卡片形式展示。
  
  触发命令：
  - "获取AI新闻"
  - "最新AI资讯"
  - "科技新闻"
  - "AI动态"
  - "有什么AI新闻"
  
  支持从36氪、AiBase、InfoQ、AI科技评论、量子位、智东西等国内主流AI媒体获取新闻。
version: 2.0
---

# AI新闻获取器

用于获取国内权威AI科技网站的最新新闻，以带摘要的卡片形式展示。

## 支持的网站

| 网站 | 域名 | 技术模式 |
|------|------|---------|
| **36氪AI** | 36kr.com | 列表页HTML提取 |
| **AiBase新闻** | aibase.cn | JSON SSR模式 |
| **InfoQ AI简报** | infoq.cn | JSON SSR模式 |
| **AI科技评论** | leiphone.com | 列表页HTML提取 |
| **量子位** | qbitai.com | 列表页HTML提取 |
| **智东西** | zhidx.com | 列表页HTML提取 |

## 使用方法

### 直接运行获取所有新闻

```bash
cd /root/.openclaw/workspace/skills/ai-news-fetcher
python3 main.py
```

### 常用参数

- `--max-items N`: 每个网站获取N条新闻（默认10条）
- `--site 网站名`: 指定特定网站（如：qbitai, jiqizhixin）
- `--output 文件.md`: 保存到指定文件
- `--format md`: 指定输出格式（json/csv/md）

### 示例命令

```bash
# 获取每个网站5条新闻
cd /root/.openclaw/workspace/skills/ai-news-fetcher
python3 main.py --max-items 5

# 只获取量子位的新闻
python3 main.py --site qbitai --max-items 10

# 保存为Markdown文件
python3 main.py --max-items 5 --format md --output ai_news.md

# 采集所有站点并保存为多种格式
python3 main.py --max-items 5 --format auto
```

### 使用 CLI 工具

```bash
# 列出所有支持的站点
python3 spider_cli.py list-sites

# 测试特定站点配置
python3 spider_cli.py test qbitai

# 采集指定站点
python3 spider_cli.py crawl qbitai --max-items 5 --output output/news.json
```

## 输出格式

### Markdown 卡片格式（默认）

```markdown
# 新闻采集结果

生成时间: 2026-03-09 22:00:00
总条目数: 35

---

## 1. OpenClaw 3.8继续炸场，龙虾不睡觉...

**来源**: 36氪AI  
**作者**: 新智元  
**发布时间**: 2026-03-09 18:00  
**链接**: [https://36kr.com/p/...](https://36kr.com/p/...)

**摘要**:
> OpenClaw 3.7发布不到24小时，3.8稳定版就紧跟着上线了...

---

## 2. 从Sora惊恐到即梦反杀...

**来源**: 量子位  
**作者**: 脑极体  
...
```

### JSON 格式

```json
[
  {
    "title": "新闻标题",
    "summary": "内容摘要",
    "author": "作者",
    "publish_time": "2026-03-09T18:00:00",
    "url": "https://...",
    "source": "网站名称",
    "crawled_at": "2026-03-09T22:00:00"
  }
]
```

### CSV 格式

适合导入 Excel 进行数据分析。

## 添加新站点

1. 复制模板：
```bash
cp site-configs/_template.yaml site-configs/yoursite.yaml
```

2. 编辑配置，填写选择器（支持 XPath/CSS/JSON SSR）

3. 测试验证：
```bash
python3 spider_cli.py test yoursite
```

## 项目结构

```
ai-news-fetcher/
├── spider/                 # 核心采集引擎
│   ├── config_loader.py    # YAML配置加载
│   ├── engine.py           # 异步采集引擎
│   ├── extractors.py       # 字段提取器（XPath/CSS/JSON）
│   ├── storage.py          # 多格式存储（JSON/CSV/MD）
│   └── monitor.py          # 监控告警
├── site-configs/           # 站点配置目录
│   ├── _template.yaml      # 配置模板
│   ├── 36kr.yaml           # 36氪配置
│   ├── aibase.yaml         # AiBase配置
│   ├── infoq.yaml          # InfoQ配置
│   ├── leiphone.yaml       # AI科技评论配置
│   ├── qbitai.yaml         # 量子位配置
│   └── zhidx.yaml          # 智东西配置
│   ├── qbitai.yaml         # 量子位配置
│   └── zhidx.yaml          # 智东西配置
├── main.py                 # 主入口（支持命令行参数）
└── spider_cli.py           # CLI工具（测试/采集/列出）
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
    type: "css"  # 或 "xpath", "json_ssr"
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
    
    summary:
      type: "xpath"
      value: ".//p/text()"
      default: ""
```

## 依赖安装

```bash
pip3 install lxml aiohttp pyyaml click python-dateutil cssselect
```

## 注意事项

- **反爬机制**: 36氪、智东西等站点有反爬，建议设置 `--delay 2` 或只采集首页
- **请求频率**: 默认1秒间隔，可通过 `--delay` 调整
- **超时设置**: 默认30秒超时，网络慢时可调整
- **输出目录**: 默认保存到 `output/` 目录

## 更新记录

- **v2.0** (2026-03-09) - 完全重写
  - 配置驱动架构（YAML配置）
  - 支持7个站点（新增36氪、AiBase）
  - 多模式提取（XPath/CSS/JSON SSR）
  - 异步采集引擎
  - 多格式输出（JSON/CSV/Markdown）
  
- **v1.0** (旧版) - 基础版本，已停用
  - 见 `ai-news-fetcher-old` 目录
