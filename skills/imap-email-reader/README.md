# IMAP 邮箱读取技能

## 安装依赖

无需额外依赖，使用 Python 标准库 (imaplib, email)

## 快速开始

### 1. 配置环境变量

```bash
export EMAIL_IMAP_SERVER="imap.qq.com"
export EMAIL_IMAP_PORT="993"
export EMAIL_USERNAME="lu.zhen9@qq.com"
export EMAIL_PASSWORD="jownkbygnemccaha"
```

### 2. 读取最新邮件

```bash
python scripts/read_email.py

# 读取 10 封
python scripts/read_email.py -n 10

# 只显示未读
python scripts/read_email.py -u

# 查看邮件详情
python scripts/read_email.py -d <邮件ID>
```

### 3. 搜索邮件

```bash
# 按主题搜索
python scripts/search_email.py "会议"

# 按发件人搜索
python scripts/search_email.py -f "noreply@github.com"

# 按日期搜索
python scripts/search_email.py -s "2026-03-01" -b "2026-03-15"
```
