#!/usr/bin/env python3
"""
Workspace Git Sync - 工作空间 GitHub 同步工具
一键将工作空间内容提交到 GitHub
"""

import os
import sys
import subprocess
import json
from datetime import datetime
from pathlib import Path

# GitHub 仓库配置
GITHUB_REPO = "https://github.com/leolu66/kimisclaw.git"
DEFAULT_BRANCH = "main"


def run_command(cmd, cwd=None, check=True):
    """运行 shell 命令"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        if check and result.returncode != 0:
            print(f"[ERROR] 命令执行失败: {cmd}")
            print(f"[ERROR] {result.stderr}")
            return None
        return result.stdout.strip()
    except Exception as e:
        print(f"[ERROR] 执行命令时出错: {e}")
        return None


def get_workspace_dir():
    """获取工作空间目录"""
    # 脚本位于 skills/workspace-git-sync/scripts/
    # 工作空间是 skills 的父目录
    script_dir = Path(__file__).parent.resolve()
    skills_dir = script_dir.parent.parent
    workspace_dir = skills_dir.parent
    return workspace_dir


def check_git_config(workspace_dir):
    """检查 Git 配置"""
    git_dir = workspace_dir / ".git"
    if not git_dir.exists():
        print("[INFO] 工作空间未初始化 Git 仓库")
        return False
    return True


def init_git_repo(workspace_dir):
    """初始化 Git 仓库"""
    print("[INFO] 初始化 Git 仓库...")
    result = run_command("git init", cwd=workspace_dir)
    if result is not None:
        print("[OK] Git 仓库初始化成功")
        return True
    return False


def setup_remote(workspace_dir, repo_url=GITHUB_REPO):
    """设置远程仓库"""
    print(f"[INFO] 设置远程仓库: {repo_url}")
    
    # 检查是否已有远程仓库
    result = run_command("git remote get-url origin", cwd=workspace_dir, check=False)
    
    if result and repo_url in result:
        print("[OK] 远程仓库已配置")
        return True
    
    # 移除旧的 origin（如果存在）
    run_command("git remote remove origin", cwd=workspace_dir, check=False)
    
    # 添加新的远程仓库
    result = run_command(f"git remote add origin {repo_url}", cwd=workspace_dir)
    if result is not None:
        print("[OK] 远程仓库设置成功")
        return True
    
    return False


def get_git_status(workspace_dir):
    """获取 Git 状态"""
    result = run_command("git status --porcelain", cwd=workspace_dir, check=False)
    if result is None:
        return []
    
    changes = []
    for line in result.split('\n'):
        if line.strip():
            status = line[:2]
            filename = line[3:].strip()
            changes.append({
                'status': status,
                'filename': filename
            })
    return changes


def sync_to_github(workspace_dir, commit_message=None, branch=DEFAULT_BRANCH):
    """同步工作空间到 GitHub"""
    print("=" * 50)
    print("Workspace Git Sync - 开始同步")
    print("=" * 50)
    print()
    
    # 1. 检查/初始化 Git 仓库
    if not check_git_config(workspace_dir):
        if not init_git_repo(workspace_dir):
            print("[FAILED] Git 仓库初始化失败")
            return False
    
    # 2. 设置远程仓库
    if not setup_remote(workspace_dir):
        print("[FAILED] 远程仓库设置失败")
        return False
    
    # 3. 获取当前分支
    current_branch = run_command("git branch --show-current", cwd=workspace_dir)
    if current_branch:
        print(f"[INFO] 当前分支: {current_branch}")
    
    # 4. 获取 Git 状态
    print("[INFO] 检查文件变更...")
    changes = get_git_status(workspace_dir)
    
    if not changes:
        print("[INFO] 没有需要提交的变更")
        
        # 检查是否有提交需要推送
        ahead = run_command(
            f"git rev-list --count {branch}..origin/{branch} 2>/dev/null || echo '0'",
            cwd=workspace_dir,
            check=False
        )
        if ahead and ahead != '0':
            print(f"[INFO] 本地有 {ahead} 个提交需要推送")
        else:
            print("[OK] 工作空间已是最新状态")
            return True
    else:
        print(f"[INFO] 发现 {len(changes)} 个文件变更:")
        for change in changes[:10]:  # 只显示前10个
            status_map = {
                'M ': '修改',
                ' M': '修改',
                'A ': '新增',
                '??': '未跟踪'
            }
            status_desc = status_map.get(change['status'], change['status'])
            print(f"  [{status_desc}] {change['filename']}")
        
        if len(changes) > 10:
            print(f"  ... 还有 {len(changes) - 10} 个文件")
        print()
    
    # 5. 添加所有变更
    print("[INFO] 添加文件到暂存区...")
    result = run_command("git add -A", cwd=workspace_dir)
    if result is None:
        print("[FAILED] 添加文件失败")
        return False
    print("[OK] 文件已添加")
    
    # 6. 生成提交信息
    if not commit_message:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        change_count = len(changes) if changes else 0
        commit_message = f"Sync workspace - {timestamp} ({change_count} changes)"
    
    print(f"[INFO] 提交信息: {commit_message}")
    
    # 7. 提交
    result = run_command(f'git commit -m "{commit_message}"', cwd=workspace_dir, check=False)
    if result is None:
        print("[INFO] 没有需要提交的变更，或提交失败")
    else:
        print("[OK] 提交成功")
    
    # 8. 推送到 GitHub
    print(f"[INFO] 推送到 GitHub ({branch} 分支)...")
    result = run_command(f"git push -u origin {branch}", cwd=workspace_dir, check=False)
    
    if result is not None:
        print("[OK] 推送成功!")
        print()
        print("=" * 50)
        print("✅ 工作空间已成功同步到 GitHub")
        print(f"📁 仓库地址: {GITHUB_REPO}")
        print("=" * 50)
        return True
    else:
        print("[FAILED] 推送失败，请检查网络连接和权限")
        return False


def show_status(workspace_dir):
    """显示同步状态"""
    print("=" * 50)
    print("Workspace Git Sync - 状态检查")
    print("=" * 50)
    print()
    
    # 检查 Git 仓库
    if not check_git_config(workspace_dir):
        print("[INFO] Git 仓库: 未初始化")
        return
    
    print("[OK] Git 仓库: 已初始化")
    
    # 检查远程仓库
    remote = run_command("git remote get-url origin", cwd=workspace_dir, check=False)
    if remote:
        print(f"[OK] 远程仓库: {remote}")
    else:
        print("[WARN] 远程仓库: 未配置")
    
    # 检查分支
    branch = run_command("git branch --show-current", cwd=workspace_dir, check=False)
    if branch:
        print(f"[OK] 当前分支: {branch}")
    
    # 检查变更
    changes = get_git_status(workspace_dir)
    if changes:
        print(f"[INFO] 未提交变更: {len(changes)} 个文件")
        for change in changes[:5]:
            print(f"  - {change['filename']}")
        if len(changes) > 5:
            print(f"  ... 还有 {len(changes) - 5} 个文件")
    else:
        print("[OK] 工作目录: 干净（无未提交变更）")
    
    # 检查提交历史
    commit_count = run_command(
        "git rev-list --count HEAD 2>/dev/null || echo '0'",
        cwd=workspace_dir,
        check=False
    )
    if commit_count and commit_count != '0':
        print(f"[INFO] 本地提交数: {commit_count}")
    
    print()


def main():
    """主函数"""
    # 获取工作空间目录
    workspace_dir = get_workspace_dir()
    print(f"[INFO] 工作空间: {workspace_dir}")
    
    # 解析命令
    if len(sys.argv) < 2:
        # 默认执行同步
        sync_to_github(workspace_dir)
        return
    
    command = sys.argv[1].lower()
    
    if command in ["sync", "push", "提交"]:
        # 支持自定义提交信息
        commit_msg = sys.argv[2] if len(sys.argv) > 2 else None
        sync_to_github(workspace_dir, commit_msg)
    
    elif command in ["status", "状态"]:
        show_status(workspace_dir)
    
    elif command in ["init", "初始化"]:
        if not check_git_config(workspace_dir):
            init_git_repo(workspace_dir)
        setup_remote(workspace_dir)
    
    else:
        print("用法: python workspace_git_sync.py [命令]")
        print()
        print("命令:")
        print("  sync, push, 提交    - 同步工作空间到 GitHub")
        print("  status, 状态        - 查看同步状态")
        print("  init, 初始化        - 初始化 Git 仓库和远程")
        print()
        print("示例:")
        print('  python workspace_git_sync.py sync')
        print('  python workspace_git_sync.py sync "自定义提交信息"')
        print('  python workspace_git_sync.py status')


if __name__ == "__main__":
    main()
