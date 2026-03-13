---
name: netnotes
description: |
  互联网笔记本（NetNotes）- 网页内容收集与管理系统。
  用于抓取网页文章、自动分类、保存为 Markdown 并建立索引数据库。

  触发场景：
  - "保存这篇文章" / "收藏这个网页"
  - "抓取 https://..."
  - "把这篇文章存到笔记本"
  - "NetNotes" / "网络笔记本"
  - "帮我整理这篇文章到 AI/运营商/管理 等分类"
  - "给这篇文章打标签"
  - "按标签搜索"
  - "查询文章" / "搜索笔记" / "查找文章"

  功能：
  - 支持普通 HTTP 抓取和 Playwright 动态渲染（反爬）
  - 自动分类到 6 个专题笔记本：AI、运营商、管理、社会生活、技术其他、其他
  - 标签系统：多标签管理、按标签检索
  - 组合查询：分类+标签+关键词+日期范围自由组合
  - 生成 100 字内文章摘要
  - SQLite 数据库记录入库信息
---

# NetNotes 互联网笔记本

一个本地网页内容收集和管理系统。

## 目录结构

```
netnotes/
├── notes/                    # 笔记本存储目录
│   ├── AI/                   # AI/人工智能相关
│   ├── 运营商/               # 电信运营商/通信行业
│   ├── 管理/                 # 管理/商业/领导力
│   ├── 社会生活/             # 生活/健康/旅行/理财
│   ├── 技术其他/             # 编程/技术（非AI）
│   └── 其他/                 # 未分类内容
├── scripts/
│   ├── fetch_article.py      # 网页抓取
│   ├── classify_article.py   # 自动分类
│   ├── save_article.py       # 保存和入库
│   ├── tag_manager.py        # 标签管理
│   └── search.py             # 组合查询（NEW）
└── articles.db               # SQLite 数据库
```

## 使用流程

### 1. 抓取文章

```bash
# 普通抓取
python scripts/fetch_article.py "https://example.com/article" -o /tmp/article.md

# 使用 Playwright（用于反爬/动态页面）
python scripts/fetch_article.py "https://example.com/article" -p -o /tmp/article.md
```

### 2. 分类文章

```bash
python scripts/classify_article.py -t "文章标题" -c "文章内容" -u "https://..."
```

输出示例：
```
建议分类: AI
置信度: 85.00%
理由: 匹配关键词: 人工智能, 深度学习, 大模型, GPT
```

### 3. 保存文章（支持标签）

```bash
# 初始化数据库（首次使用）
python scripts/save_article.py init
python scripts/tag_manager.py init

# 保存文章（不带标签）
python scripts/save_article.py save \
  -t "文章标题" \
  -c "文章内容或文件路径" \
  -u "https://..." \
  -cat "AI"

# 保存文章（带标签）
python scripts/save_article.py save \
  -t "文章标题" \
  -c "文章内容" \
  -u "https://..." \
  -cat "AI" \
  --tags "GPT,教程,深度学习"
```

## 标签管理

### 为已有文章添加标签

```bash
python scripts/tag_manager.py tag <文章ID> "标签1,标签2,标签3"
```

### 查看所有标签

```bash
python scripts/tag_manager.py list
```

输出示例：
```json
[
  {"id": 1, "name": "OpenClaw", "article_count": 2},
  {"id": 2, "name": "教程", "article_count": 5}
]
```

### 查看文章的标签

```bash
python scripts/tag_manager.py article-tags <文章ID>
```

### 按标签搜索文章

```bash
# 搜索单个标签
python scripts/tag_manager.py search "教程"

# 搜索多个标签（匹配任一）
python scripts/tag_manager.py search "AI,深度学习"

# 搜索多个标签（匹配全部）
python scripts/tag_manager.py search "AI,教程" --all
```

### 移除标签

```bash
python scripts/tag_manager.py untag <文章ID> "标签名"
```

## 组合查询（NEW）

使用 `search.py` 进行多条件组合查询，支持分类、标签、关键词、日期范围自由组合。

### 基础查询

```bash
# 按分类查询
python scripts/search.py --category AI

# 按标签查询
python scripts/search.py --tags OpenClaw

# 按关键词查询（标题/摘要/URL）
python scripts/search.py --keyword "原理"

# 按日期范围查询
python scripts/search.py --from 2026-03-01 --to 2026-03-14

# 最近7天的文章
python scripts/search.py --days 7
```

### 组合查询

```bash
# AI分类 + OpenClaw标签
python scripts/search.py -c AI --tags OpenClaw

# AI分类 + 教程标签 + 关键词"底层"
python scripts/search.py -c AI --tags 教程 -k 底层

# 最近30天 + 管理分类 + 关键词"领导力"
python scripts/search.py --days 30 -c 管理 -k 领导力
```

### 输出选项

```bash
# 显示详细信息（URL、摘要）
python scripts/search.py -c AI -d

# 输出JSON格式
python scripts/search.py --tags OpenClaw --json

# 限制结果数量
python scripts/search.py -c AI -n 10
```

### 交互模式（查看文章）

```bash
# 查询后进入交互模式，可输入编号查看文章
python scripts/search.py -c AI -i

# 输出示例：
# ====================================================================================================
# 找到 2 篇文章
# ====================================================================================================
#
# [1] OpenClaw让我看到：从指令控制到意图交互...
#     分类: AI | 日期: 2026-03-13 16:19:23
#     标签: OpenClaw, 认知隐形
#
# [2] 【深度解剖】OpenClaw 底层原理全解析...
#     分类: AI | 日期: 2026-03-13 15:54:57
#     标签: 架构, 教程, AI工具
#
# ----------------------------------------------------------------------------------------------------
# 输入编号查看文章（如: 1,2,3），或输入 'q' 退出
#
# > 1,2
# （将依次打开选中的文章）
```

## 完整工作流示例

```python
import subprocess
import json

url = "https://example.com/article"

# 1. 抓取
fetch_result = subprocess.run(
    ['python', 'scripts/fetch_article.py', url, '-o', '/tmp/article.md'],
    capture_output=True, text=True
)

# 2. 读取内容
with open('/tmp/article.md', 'r') as f:
    content = f.read()

# 3. 提取标题（从文件第一行）
title = content.split('\n')[0].replace('# ', '').strip()

# 4. 自动分类
classify_result = subprocess.run(
    ['python', 'scripts/classify_article.py', '-t', title, '-c', content, '--json'],
    capture_output=True, text=True
)
category = json.loads(classify_result.stdout)['category']

# 5. 询问用户确认分类和标签
# ... 用户交互 ...
user_tags = "GPT,教程,AI工具"  # 用户指定的标签

# 6. 保存（带标签）
save_result = subprocess.run(
    ['python', 'scripts/save_article.py', 'save',
     '-t', title, '-c', content, '-u', url, '-cat', category,
     '--tags', user_tags],
    capture_output=True, text=True
)

result = json.loads(save_result.stdout)
print(f"文章已保存，ID: {result['id']}, 标签: {result.get('tags', [])}")
```

## 数据库查询

```bash
# 列出最近20篇文章（包含标签）
python scripts/save_article.py list

# 按分类列出
python scripts/save_article.py list -c "AI"

# 搜索
python scripts/save_article.py search "关键词"
```

## 依赖安装

```bash
# 基础依赖
pip install requests beautifulsoup4

# 完整依赖（含 Playwright）
pip install requests beautifulsoup4 playwright
playwright install chromium
```

## 分类规则

| 分类 | 关键词示例 |
|------|-----------|
| AI | 人工智能、机器学习、GPT、大模型、OpenAI |
| 运营商 | 中国移动、5G、通信、基站、华为、数字化转型 |
| 管理 | 领导力、OKR、产品经理、项目管理、商业分析 |
| 社会生活 | 健康、旅行、理财、心理学、电影、美食 |
| 技术其他 | 编程、Python、云计算、数据库、Kubernetes |
| 其他 | 未匹配以上内容的文章 |

## 标签系统特点

- **多对多关系**：一篇文章可有多个标签，一个标签可关联多篇文章
- **自动创建**：保存时指定的标签不存在会自动创建
- **标签去重**：同一文章的重复标签自动去重
- **文章计数**：`tag_manager.py list` 显示每个标签关联的文章数

## 数据库表结构

### articles 表
| 字段 | 说明 |
|------|------|
| id | 文章ID |
| title | 标题 |
| url | 来源URL |
| category | 分类目录 |
| summary | 摘要 |
| file_path | 文件路径 |
| fetched_at | 抓取时间 |
| file_size | 文件大小 |

### tags 表
| 字段 | 说明 |
|------|------|
| id | 标签ID |
| name | 标签名称（唯一） |
| description | 标签描述 |
| created_at | 创建时间 |

### article_tags 表
| 字段 | 说明 |
|------|------|
| article_id | 文章ID |
| tag_id | 标签ID |
| created_at | 关联时间 |

详见 `references/database_schema.md`

## 文件命名规则

- 使用文章标题作为文件名
- 自动清理不安全字符（< > : " / \ \| ? *）
- 长度限制 100 字符
- 重名时自动添加序号后缀
