---
name: imap-email-reader
description: 使用 IMAP 协议读取邮箱邮件，支持 QQ 邮箱、163 邮箱等主流邮箱服务。可读取收件箱最新邮件、搜索邮件、查看邮件详情。
---

# IMAP 邮箱读取技能

使用 IMAP 协议直接连接邮箱服务器读取邮件，支持多种主流邮箱服务。

## 支持的邮箱

| 邮箱服务 | IMAP 服务器 | 端口 | SSL |
|---------|------------|------|-----|
| QQ 邮箱 | imap.qq.com | 993 | 是 |
| 163 邮箱 | imap.163.com | 993 | 是 |
| Gmail | imap.gmail.com | 993 | 是 |
| Outlook | outlook.office365.com | 993 | 是 |

## 配置方法

### 环境变量配置（推荐）

```bash
# QQ 邮箱
export EMAIL_IMAP_SERVER="imap.qq.com"
export EMAIL_IMAP_PORT="993"
export EMAIL_USERNAME="lu.zhen9@qq.com"
export EMAIL_PASSWORD="jownkbygnemccaha"  # QQ邮箱授权码

# 添加到永久配置
echo 'export EMAIL_IMAP_SERVER="imap.qq.com"' >> ~/.bashrc
echo 'export EMAIL_IMAP_PORT="993"' >> ~/.bashrc
echo 'export EMAIL_USERNAME="lu.zhen9@qq.com"' >> ~/.bashrc
echo 'export EMAIL_PASSWORD="jownkbygnemccaha"' >> ~/.bashrc
```

### OpenClaw 配置

在 `~/.openclaw/config.json` 中添加：

```json
{
  "env": {
    "EMAIL_IMAP_SERVER": "imap.qq.com",
    "EMAIL_IMAP_PORT": "993",
    "EMAIL_USERNAME": "lu.zhen9@qq.com",
    "EMAIL_PASSWORD": "jownkbygnemccaha"
  }
}
```

## 快速使用

### 查看最新邮件

```bash
# 读取最新 5 封邮件
python scripts/read_email.py

# 读取最新 10 封邮件
python scripts/read_email.py -n 10

# 只显示未读邮件
python scripts/read_email.py --unread
```

### 搜索邮件

```bash
# 按主题搜索
python scripts/search_email.py "会议"

# 按发件人搜索
python scripts/search_email.py -f "noreply@github.com"

# 按日期范围搜索
python scripts/search_email.py -d "2026-03-01" "2026-03-15"
```

### 查看邮件详情

```bash
# 查看指定序号邮件的完整内容
python scripts/read_email.py -d 1
```

## Python 调用

```python
import subprocess
import os

script_path = os.path.join(os.path.dirname(__file__), 'scripts', 'read_email.py')
result = subprocess.run(
    ["python3", script_path, "-n", "5"],
    capture_output=True, text=True
)
print(result.stdout)
```

## 输出格式

邮件列表输出示例：

```
📧 最新 5 封邮件

[1] GitHub Actions workflow failed
    发件人: GitHub <noreply@github.com>
    时间: 2026-03-15 14:32:18
    已读: ✓

[2] 您的验证码是 123456
    发件人: 腾讯 <noreply@tencent.com>
    时间: 2026-03-15 12:10:05
    已读: ✗

共 5 封邮件，1 封未读
```

## 注意事项

1. **授权码**：QQ/163 等邮箱需要使用授权码（在邮箱设置中生成），不是邮箱登录密码
2. **安全**：授权码建议通过环境变量或配置文件管理，不要硬编码在代码中
3. **SSL**：默认使用 SSL 加密连接，端口 993
4. **频率**：频繁连接可能会被邮箱服务器限制，建议合理使用

## 获取 QQ 邮箱授权码

1. 登录 QQ 邮箱网页版
2. 点击「设置」→「账户」
3. 找到「POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务」
4. 开启「IMAP/SMTP服务」
5. 按提示生成授权码（16位字符串）

## 文件说明

- `scripts/read_email.py` - 读取最新邮件
- `scripts/search_email.py` - 搜索邮件
- `scripts/email_client.py` - IMAP 客户端封装类
