#!/usr/bin/env python3
"""
搜索邮件
"""

import argparse
import sys
import os

# 添加脚本目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from email_client import ImapEmailClient


def main():
    parser = argparse.ArgumentParser(description="搜索邮箱邮件")
    parser.add_argument("keyword", nargs="?", default=None,
                       help="搜索关键词（主题）")
    parser.add_argument("-f", "--from", dest="from_email", metavar="EMAIL",
                       help="按发件人搜索")
    parser.add_argument("-s", "--since", metavar="DATE",
                       help="开始日期 (YYYY-MM-DD)")
    parser.add_argument("-b", "--before", metavar="DATE",
                       help="结束日期 (YYYY-MM-DD)")
    parser.add_argument("-n", "--count", type=int, default=10,
                       help="最大返回数量 (默认: 10)")
    
    args = parser.parse_args()
    
    # 检查环境变量
    if not os.environ.get("EMAIL_USERNAME"):
        print("""错误: 未配置邮箱信息

请设置以下环境变量:

export EMAIL_IMAP_SERVER="imap.qq.com"
export EMAIL_IMAP_PORT="993"
export EMAIL_USERNAME="lu.zhen9@qq.com"
export EMAIL_PASSWORD="jownkbygnemccaha"
""")
        return
    
    # 至少需要一个搜索条件
    if not args.keyword and not args.from_email and not args.since:
        print("请提供至少一个搜索条件: 关键词、发件人、或日期范围")
        parser.print_help()
        return
    
    with ImapEmailClient() as client:
        emails = client.search_emails(
            keyword=args.keyword,
            from_email=args.from_email,
            since=args.since,
            before=args.before,
            count=args.count
        )
        
        if not emails:
            print("📭 没有找到匹配的邮件")
            return
        
        print(f"\n🔍 找到 {len(emails)} 封匹配邮件\n")
        
        for email in emails:
            print(f"[{email['number']}] {email['subject']}")
            print(f"    发件人: {email['from_name']} <{email['from_email']}>")
            print(f"    时间: {email['date']}")
            if email['snippet']:
                print(f"    摘要: {email['snippet']}")
            print()
        
        print(f"提示: 使用 read_email.py -d <邮件ID> 查看完整内容")


if __name__ == "__main__":
    main()
