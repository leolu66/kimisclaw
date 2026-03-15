#!/usr/bin/env python3
"""
IMAP 邮箱客户端封装类
"""

import os
import imaplib
import email
from email.header import decode_header
from email.utils import parsedate_to_datetime
from typing import List, Dict, Optional, Tuple
import re


class ImapEmailClient:
    """IMAP 邮箱客户端"""
    
    def __init__(self, server: str = None, port: int = None, 
                 username: str = None, password: str = None):
        """
        初始化客户端
        
        参数可以从环境变量或参数传入，优先级：参数 > 环境变量
        """
        self.server = server or os.environ.get("EMAIL_IMAP_SERVER", "imap.qq.com")
        self.port = port or int(os.environ.get("EMAIL_IMAP_PORT", "993"))
        self.username = username or os.environ.get("EMAIL_USERNAME", "")
        self.password = password or os.environ.get("EMAIL_PASSWORD", "")
        
        self.conn = None
        self.connected = False
    
    def connect(self) -> bool:
        """连接邮箱服务器"""
        try:
            self.conn = imaplib.IMAP4_SSL(self.server, self.port)
            self.conn.login(self.username, self.password)
            self.connected = True
            return True
        except Exception as e:
            print(f"连接失败: {e}")
            return False
    
    def disconnect(self):
        """断开连接"""
        if self.conn:
            try:
                self.conn.logout()
            except:
                pass
        self.connected = False
    
    def __enter__(self):
        """上下文管理器入口"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.disconnect()
        return False
    
    def _decode_str(self, s: str) -> str:
        """解码邮件头中的编码字符串"""
        if not s:
            return ""
        try:
            decoded_parts = decode_header(s)
            result = []
            for part, charset in decoded_parts:
                if isinstance(part, bytes):
                    if charset:
                        result.append(part.decode(charset))
                    else:
                        try:
                            result.append(part.decode('utf-8'))
                        except:
                            result.append(part.decode('gbk', errors='ignore'))
                else:
                    result.append(part)
            return "".join(result)
        except Exception as e:
            return s
    
    def _get_email_body(self, msg) -> Tuple[str, str]:
        """
        获取邮件正文内容
        返回: (纯文本内容, HTML内容)
        """
        text_content = ""
        html_content = ""
        
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = part.get("Content-Disposition", "")
                
                # 跳过附件
                if "attachment" in content_disposition:
                    continue
                
                try:
                    payload = part.get_payload(decode=True)
                    if payload:
                        charset = part.get_content_charset()
                        if charset:
                            content = payload.decode(charset, errors='ignore')
                        else:
                            try:
                                content = payload.decode('utf-8')
                            except:
                                content = payload.decode('gbk', errors='ignore')
                        
                        if content_type == "text/plain":
                            text_content += content
                        elif content_type == "text/html":
                            html_content += content
                except Exception:
                    pass
        else:
            try:
                payload = msg.get_payload(decode=True)
                charset = msg.get_content_charset()
                if payload:
                    if charset:
                        content = payload.decode(charset, errors='ignore')
                    else:
                        try:
                            content = payload.decode('utf-8')
                        except:
                            content = payload.decode('gbk', errors='ignore')
                    
                    if msg.get_content_type() == "text/html":
                        html_content = content
                    else:
                        text_content = content
            except Exception:
                pass
        
        return text_content, html_content
    
    def get_latest_emails(self, count: int = 5, unread_only: bool = False) -> List[Dict]:
        """
        获取最新邮件
        
        Args:
            count: 获取数量
            unread_only: 是否只获取未读邮件
            
        Returns:
            邮件列表，每封邮件包含：number, subject, from_name, from_email, date, is_read, snippet
        """
        emails = []
        
        if not self.connected:
            if not self.connect():
                return emails
        
        try:
            # 选择收件箱
            self.conn.select("INBOX")
            
            # 搜索条件
            if unread_only:
                _, search_data = self.conn.search(None, "UNSEEN")
            else:
                _, search_data = self.conn.search(None, "ALL")
            
            email_ids = search_data[0].split()
            
            # 取最新的 count 封
            email_ids = email_ids[-count:]
            email_ids.reverse()  # 最新的在前
            
            for i, email_id in enumerate(email_ids, 1):
                try:
                    _, msg_data = self.conn.fetch(email_id, "(RFC822 FLAGS)")
                    
                    # 解析 flags 判断是否已读
                    is_read = True
                    raw_msg = None
                    
                    for response_part in msg_data:
                        if isinstance(response_part, tuple):
                            raw_msg = response_part[1]
                        elif isinstance(response_part, bytes):
                            # 可能是 flags 信息
                            if b'\\Seen' not in response_part:
                                pass  # 未读
                    
                    if raw_msg:
                        msg = email.message_from_bytes(raw_msg)
                        
                        # 解析邮件头
                        subject = self._decode_str(msg.get("Subject", ""))
                        from_header = msg.get("From", "")
                        date_str = msg.get("Date", "")
                        
                        # 解析发件人
                        from_match = re.match(r'"?([^"<]+)"?\s*<?([^>]*)>?', from_header)
                        if from_match:
                            from_name = from_match.group(1).strip()
                            from_email = from_match.group(2).strip()
                        else:
                            from_name = from_header
                            from_email = from_header
                        
                        from_name = self._decode_str(from_name)
                        
                        # 解析日期
                        try:
                            date_obj = parsedate_to_datetime(date_str)
                            date_formatted = date_obj.strftime("%Y-%m-%d %H:%M:%S")
                        except:
                            date_formatted = date_str
                        
                        # 获取邮件正文摘要
                        text_body, html_body = self._get_email_body(msg)
                        snippet = text_body[:100].replace('\n', ' ').strip() if text_body else ""
                        if len(text_body) > 100:
                            snippet += "..."
                        
                        # 检查是否已读（通过 flags）
                        try:
                            _, flags_data = self.conn.fetch(email_id, "(FLAGS)")
                            flags_str = str(flags_data[0])
                            is_read = '\\Seen' in flags_str
                        except:
                            is_read = True
                        
                        emails.append({
                            "number": i,
                            "email_id": email_id.decode() if isinstance(email_id, bytes) else email_id,
                            "subject": subject or "(无主题)",
                            "from_name": from_name,
                            "from_email": from_email,
                            "date": date_formatted,
                            "is_read": is_read,
                            "snippet": snippet,
                            "text_body": text_body,
                            "html_body": html_body
                        })
                except Exception as e:
                    print(f"解析邮件 {email_id} 失败: {e}")
                    continue
                    
        except Exception as e:
            print(f"获取邮件失败: {e}")
        
        return emails
    
    def get_email_detail(self, email_id: str) -> Optional[Dict]:
        """获取单封邮件的完整内容"""
        if not self.connected:
            if not self.connect():
                return None
        
        try:
            self.conn.select("INBOX")
            
            # 获取邮件
            email_id_bytes = email_id.encode() if isinstance(email_id, str) else email_id
            _, msg_data = self.conn.fetch(email_id_bytes, "(RFC822)")
            
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    
                    subject = self._decode_str(msg.get("Subject", ""))
                    from_header = msg.get("From", "")
                    date_str = msg.get("Date", "")
                    to_header = msg.get("To", "")
                    
                    # 解析发件人
                    from_match = re.match(r'"?([^"<]+)"?\s*<?([^>]*)>?', from_header)
                    if from_match:
                        from_name = from_match.group(1).strip()
                        from_email = from_match.group(2).strip()
                    else:
                        from_name = from_header
                        from_email = from_header
                    
                    from_name = self._decode_str(from_name)
                    
                    # 解析日期
                    try:
                        date_obj = parsedate_to_datetime(date_str)
                        date_formatted = date_obj.strftime("%Y-%m-%d %H:%M:%S")
                    except:
                        date_formatted = date_str
                    
                    text_body, html_body = self._get_email_body(msg)
                    
                    return {
                        "email_id": email_id,
                        "subject": subject or "(无主题)",
                        "from_name": from_name,
                        "from_email": from_email,
                        "to": self._decode_str(to_header),
                        "date": date_formatted,
                        "text_body": text_body,
                        "html_body": html_body
                    }
            
            return None
            
        except Exception as e:
            print(f"获取邮件详情失败: {e}")
            return None
    
    def search_emails(self, keyword: str = None, from_email: str = None, 
                      since: str = None, before: str = None, 
                      count: int = 10) -> List[Dict]:
        """
        搜索邮件
        
        Args:
            keyword: 主题或正文关键词
            from_email: 发件人邮箱
            since: 开始日期 (YYYY-MM-DD)
            before: 结束日期 (YYYY-MM-DD)
            count: 最大返回数量
        """
        emails = []
        
        if not self.connected:
            if not self.connect():
                return emails
        
        try:
            self.conn.select("INBOX")
            
            # 构建搜索条件
            search_criteria = []
            
            if keyword:
                search_criteria.append(f'SUBJECT "{keyword}"')
            
            if from_email:
                search_criteria.append(f'FROM "{from_email}"')
            
            if since:
                # IMAP 日期格式: DD-Mon-YYYY
                search_criteria.append(f'SINCE "{since}"')
            
            if before:
                search_criteria.append(f'BEFORE "{before}"')
            
            if not search_criteria:
                search_criteria.append("ALL")
            
            # 执行搜索
            search_str = " ".join(search_criteria)
            _, search_data = self.conn.search(None, search_str)
            
            email_ids = search_data[0].split()
            email_ids = email_ids[-count:]  # 取最新的
            email_ids.reverse()
            
            for i, email_id in enumerate(email_ids, 1):
                try:
                    _, msg_data = self.conn.fetch(email_id, "(RFC822)")
                    
                    for response_part in msg_data:
                        if isinstance(response_part, tuple):
                            msg = email.message_from_bytes(response_part[1])
                            
                            subject = self._decode_str(msg.get("Subject", ""))
                            from_header = msg.get("From", "")
                            date_str = msg.get("Date", "")
                            
                            # 解析发件人
                            from_match = re.match(r'"?([^"<]+)"?\s*<?([^>]*)>?', from_header)
                            if from_match:
                                from_name = from_match.group(1).strip()
                                from_email_parsed = from_match.group(2).strip()
                            else:
                                from_name = from_header
                                from_email_parsed = from_header
                            
                            from_name = self._decode_str(from_name)
                            
                            try:
                                date_obj = parsedate_to_datetime(date_str)
                                date_formatted = date_obj.strftime("%Y-%m-%d %H:%M:%S")
                            except:
                                date_formatted = date_str
                            
                            text_body, _ = self._get_email_body(msg)
                            snippet = text_body[:100].replace('\n', ' ').strip() if text_body else ""
                            if len(text_body) > 100:
                                snippet += "..."
                            
                            emails.append({
                                "number": i,
                                "email_id": email_id.decode() if isinstance(email_id, bytes) else email_id,
                                "subject": subject or "(无主题)",
                                "from_name": from_name,
                                "from_email": from_email_parsed,
                                "date": date_formatted,
                                "snippet": snippet
                            })
                except Exception as e:
                    continue
                    
        except Exception as e:
            print(f"搜索邮件失败: {e}")
        
        return emails


if __name__ == "__main__":
    # 测试代码
    with ImapEmailClient() as client:
        emails = client.get_latest_emails(count=3)
        for email in emails:
            print(f"[{email['number']}] {email['subject']}")
            print(f"    From: {email['from_name']} <{email['from_email']}>")
            print(f"    Date: {email['date']}")
            print(f"    Snippet: {email['snippet'][:50]}...")
            print()
