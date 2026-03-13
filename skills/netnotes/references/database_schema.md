# NetNotes 数据库结构

## 数据库文件
- 位置: `articles.db` (SQLite)
- 创建: 首次使用时自动初始化

## 表结构

### articles 表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PRIMARY KEY AUTOINCREMENT | 自增主键 |
| title | TEXT NOT NULL | 文章标题 |
| url | TEXT NOT NULL | 文章来源URL |
| category | TEXT NOT NULL | 分类目录 |
| summary | TEXT | 文章摘要（不超过100字） |
| file_path | TEXT | 保存的Markdown文件相对路径 |
| fetched_at | TIMESTAMP DEFAULT CURRENT_TIMESTAMP | 抓取时间 |
| file_size | INTEGER | 文件大小（字节） |

### tags 表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PRIMARY KEY AUTOINCREMENT | 自增主键 |
| name | TEXT UNIQUE NOT NULL | 标签名称（唯一） |
| description | TEXT | 标签描述 |
| created_at | TIMESTAMP DEFAULT CURRENT_TIMESTAMP | 创建时间 |

### article_tags 表

| 字段 | 类型 | 说明 |
|------|------|------|
| article_id | INTEGER NOT NULL | 文章ID（外键） |
| tag_id | INTEGER NOT NULL | 标签ID（外键） |
| created_at | TIMESTAMP DEFAULT CURRENT_TIMESTAMP | 关联时间 |
| PRIMARY KEY | (article_id, tag_id) | 联合主键 |

## 索引

- `idx_category`: articles.category 索引
- `idx_url`: articles.url 索引
- `idx_fetched_at`: articles.fetched_at 索引
- `idx_article_tags_article`: article_tags.article_id 索引
- `idx_article_tags_tag`: article_tags.tag_id 索引

## 使用示例

### 查询某分类的所有文章
```sql
SELECT * FROM articles WHERE category = 'AI' ORDER BY fetched_at DESC;
```

### 搜索文章
```sql
SELECT * FROM articles WHERE title LIKE '%关键词%' OR summary LIKE '%关键词%';
```

### 统计各分类文章数
```sql
SELECT category, COUNT(*) as count FROM articles GROUP BY category;
```

### 查询文章的所有标签
```sql
SELECT t.name FROM tags t
JOIN article_tags at ON t.id = at.tag_id
WHERE at.article_id = 1;
```

### 按标签搜索文章
```sql
SELECT a.* FROM articles a
JOIN article_tags at ON a.id = at.article_id
JOIN tags t ON at.tag_id = t.id
WHERE t.name = '教程'
ORDER BY a.fetched_at DESC;
```

### 统计标签使用次数
```sql
SELECT t.name, COUNT(at.article_id) as count
FROM tags t
LEFT JOIN article_tags at ON t.id = at.tag_id
GROUP BY t.id
ORDER BY count DESC;
```
