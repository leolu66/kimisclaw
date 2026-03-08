#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess
import os

os.environ['PYTHONIOENCODING'] = 'utf-8'

def main():
    instruction = """在 D:\\projects\\workspace\\shared\\output\\task-test-006\\ 目录下创建一个测试报告文件 report.md，内容包含：
1. 测试标题：多智能体协作联调测试
2. 测试时间：2026-03-05 12:48
3. 执行节点：Claude
4. 测试结果：成功
5. 备注：这是通过 SDK 直接发送的测试任务

完成后请说明执行结果。"""
    
    print("[发送任务] 使用 --permission-mode acceptEdits...")
    print("=" * 50)
    
    try:
        result = subprocess.run(
            ["claude", "-p", instruction, "--permission-mode", "acceptEdits"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=300,
            cwd="D:\\projects\\workspace\\shared"
        )
        
        print(f"返回码: {result.returncode}")
        print()
        
        if result.stdout:
            print("【输出内容】")
            print(result.stdout[:2000])
        
        if result.stderr:
            print("\n【错误输出】")
            print(result.stderr[:500])
        
        print("=" * 50)
        
    except Exception as e:
        print(f"[错误] {e}")

if __name__ == "__main__":
    main()
