---
name: workspace-git-sync
description: |
  将 OpenClaw 工作空间内容同步到 GitHub 仓库。
  
  触发命令：
  - "提交到github" / "同步到github" / "git push"
  - "提交工作空间"
  - "查看git状态" / "git status"
  
  用于备份工作空间、同步技能文件、保存记忆和日志到云端仓库。
---

# Workspace Git Sync - 工作空间 GitHub 同步

一键将 OpenClaw 工作空间内容提交到 GitHub 仓库进行备份和同步。

## GitHub 仓库

**目标仓库**: https://github.com/leolu66/kimisclaw

## 使用方法

### 1. 同步工作空间到 GitHub（默认）

```bash
python skills/workspace-git-sync/scripts/workspace_git_sync.py
```

或触发词：
- "提交到github"
- "同步到github"
- "git push"

### 2. 带自定义提交信息

```bash
python skills/workspace-git-sync/scripts/workspace_git_sync.py sync "更新技能文件"
```

### 3. 查看同步状态

```bash
python skills/workspace-git-sync/scripts/workspace_git_sync.py status
```

或触发词：
- "查看git状态"
- "git status"

### 4. 初始化 Git 仓库

```bash
python skills/workspace-git-sync/scripts/workspace_git_sync.py init
```

或触发词：
- "初始化git"
- "git init"

## 功能特性

- ✅ **自动检测** - 自动检测 Git 仓库状态，未初始化时自动初始化
- ✅ **远程配置** - 自动配置 GitHub 远程仓库
- ✅ **状态检查** - 显示文件变更、提交状态
- ✅ **一键提交** - 添加所有变更、提交并推送到 GitHub
- ✅ **智能提交信息** - 自动生成包含时间和变更数的提交信息
- ✅ **分支管理** - 支持 main 分支推送

## 同步内容

工作空间同步包含以下内容：

```
workspace/
├── AGENTS.md              # 代理配置
├── MEMORY.md              # 长期记忆
├── SOUL.md                # 人格设定
├── USER.md                # 用户信息
├── IDENTITY.md            # 身份配置
├── TOOLS.md               # 工具配置
├── skills/                # 技能目录
│   ├── weather-skill/
│   ├── todo-manager/
│   └── ...
├── memory/                # 每日记忆
│   └── 2026-03-*.md
└── logs/daily/            # 工作日志
    └── 2026-03-*.md
```

## 工作流程

1. **检查 Git 仓库** - 检查工作空间是否已初始化 Git
2. **配置远程** - 设置 GitHub 远程仓库地址
3. **获取状态** - 检查文件变更情况
4. **添加文件** - 将所有变更添加到暂存区
5. **提交** - 创建提交（自动生成提交信息）
6. **推送** - 推送到 GitHub main 分支

## 输出示例

### 同步成功

```
==================================================
Workspace Git Sync - 开始同步
==================================================

[INFO] 工作空间: /root/.openclaw/workspace
[INFO] 当前分支: main
[INFO] 检查文件变更...
[INFO] 发现 15 个文件变更:
  [新增] skills/workspace-git-sync/SKILL.md
  [新增] skills/workspace-git-sync/scripts/workspace_git_sync.py
  [修改] MEMORY.md
  ...

[INFO] 添加文件到暂存区...
[OK] 文件已添加
[INFO] 提交信息: Sync workspace - 2026-03-09 00:45 (15 changes)
[OK] 提交成功
[INFO] 推送到 GitHub (main 分支)...
[OK] 推送成功!

==================================================
✅ 工作空间已成功同步到 GitHub
📁 仓库地址: https://github.com/leolu66/kimisclaw
==================================================
```

### 状态检查

```
==================================================
Workspace Git Sync - 状态检查
==================================================

[OK] Git 仓库: 已初始化
[OK] 远程仓库: https://github.com/leolu66/kimisclaw.git
[OK] 当前分支: main
[INFO] 未提交变更: 5 个文件
  - skills/workspace-git-sync/SKILL.md
  - skills/workspace-git-sync/scripts/workspace_git_sync.py
  ...
[INFO] 本地提交数: 42
```

## 依赖

- Python 3.x
- Git
- GitHub 访问权限（已配置 SSH Key 或 Token）

## 注意事项

1. **首次使用** - 需要配置 Git 用户名和邮箱：
   ```bash
   git config --global user.name "Your Name"
   git config --global user.email "your@email.com"
   ```

2. **认证方式** - 支持以下认证方式：
   - SSH Key（推荐）
   - Personal Access Token
   - Git 凭证管理器

3. **大文件** - 避免提交大文件（>100MB），GitHub 有文件大小限制

4. **敏感信息** - 技能会自动过滤敏感信息，但仍需注意：
   - API Key 建议存储在 vault 密码箱中
   - 密码等敏感信息不要明文写入文件

## 相关技能

- **skill-creator-local** - 创建新技能
- **vault** - 密码箱（安全存储 API Key）
- **one-click-commit** - 一键提交（本地日志记录）

## 更新记录

- **v1.0** (2026-03-09) - 初始版本，支持基本的同步功能
