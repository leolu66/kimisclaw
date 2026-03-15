#!/usr/bin/env python3
"""
读取最新邮件
"""

import argparse
import sys
import os

# 添加脚本目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from email_client import ImapEmailClient


def main():
    parser = argparse.ArgumentParser(description="读取邮箱最新邮件")
    parser.add_argument("-n", "--count", type=int, default=5, 
                       help="读取邮件数量 (默认: 5)")
    parser.add_argument("-u", "--unread", action="store_true",
                       help="只显示未读邮件")
    parser.add_argument("-d", "--detail", type=str, metavar="EMAIL_ID",
                       help="查看指定邮件的完整内容")
    
    args = parser.parse_args()
    
    # 检查环境变量
    if not os.environ.get("EMAIL_USERNAME"):
        print("""错误: 未配置邮箱信息

请设置以下环境变量:

export EMAIL_IMAP_SERVER="imap.qq.com"
export EMAIL_IMAP_PORT="993"
export EMAIL_USERNAME="lu.zhen9@qq.com"
export EMAIL_PASSWORD="jownkbygnemccaha"

获取 QQ 邮箱授权码:
1. 登录 QQ 邮箱网页版
2. 设置 → 账户 → POP3/IMAP/SMTP服务
3. 开启 IMAP/SMTP 服务，获取授权码
""")
        return
    
    with ImapEmailClient() as client:
        if args.detail:
            # 查看邮件详情
            email = client.get_email_detail(args.detail)
            if email:
                print(f"\n{'='*60}")
                print(f"📧 {email['subject']}")
                print(f"{'='*60}")
                print(f"发件人: {email['from_name']} <{email['from_email']}>")
                print(f"收件人: {email['to']}")
                print(f"时间: {email['date']}")
                print(f"{'='*60}\n")
                
                if email['text_body']:
                    print(email['text_body'])
                elif email['html_body']:
                    # 简单去除 HTML 标签显示
                    import re
                    text = re.sub(r'<[^>]+>', '', email['html_body'])
                    text = re.sub(r'\n+', '\n', text)
                    print(text)
                else:
                    print("(邮件无正文内容)")
                print()
            else:
                print(f"未找到邮件 ID: {args.detail}")
        else:
            # 获取邮件列表
            emails = client.get_latest_emails(count=args.count, unread_only=args.unread)
            
            if not emails:
                print("📭 没有找到邮件")
                return
            
            unread_count = sum(1 for e in emails if not e['is_read'])
            total_count = len(emails)
            
            if args.unread:
                print(f"\n📧 未读邮件 ({total_count} 封)\n")
            else:
                print(f"\n📧 最新 {total_count} 封邮件")
                if unread_count > 0:
                    print(f"   (其中 {unread_count} 封未读)\n")
                else:
                    print()
            
            for email in emails:
                read_mark = "✓" if email['is_read'] else "✗"
                print(f"[{email['number']}] {email['subject']}")
                print(f"    发件人: {email['from_name']} <{email['from_email']}>")
                print(f"    时间: {email['date']}")
                print(f"    已读: {read_mark}")
                if email['snippet']:
                    print(f"    摘要: {email['snippet']}")
                print()
            
            print(f"提示: 使用 -d <邮件ID> 查看完整内容")


if __name__ == "__main__":
    main()
