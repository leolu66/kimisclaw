#!/usr/bin/env python3
"""
NetNotes 文章分类模块
基于内容自动判断文章类别
"""

import argparse
import sys
from pathlib import Path

# 分类定义（与目录结构对应）
CATEGORIES = {
    'AI': {
        'keywords': [
            '人工智能', 'AI', '机器学习', '深度学习', '神经网络', '大模型', 'LLM',
            'GPT', 'ChatGPT', 'Claude', 'Gemini', 'Kimi', '文心一言', '通义千问',
            '自然语言处理', 'NLP', '计算机视觉', 'CV', '生成式AI', 'AIGC',
            'OpenAI', 'Anthropic', 'Google AI', '百度AI', '阿里AI', '腾讯AI',
            '算法', '模型训练', 'Transformer', 'Diffusion', '多模态'
        ],
        'domains': ['openai.com', 'anthropic.com', 'huggingface.co', 'arxiv.org', 'medium.com']
    },
    '运营商': {
        'keywords': [
            '运营商', '电信', '移动', '联通', '广电', '5G', '6G', '通信', '网络',
            '基站', '光纤', '宽带', '移动通信', '蜂窝网络', '物联网', 'NB-IoT',
            '中国移动', '中国电信', '中国联通', '中国广电', '华为', '中兴', '爱立信', '诺基亚',
            '套餐', '流量', '话费', '漫游', '携号转网', '增值业务',
            'ICT', '云网融合', '数字化转型', '智慧城市'
        ],
        'domains': ['chinamobile.com', 'chinatelecom.com', 'chinaunicom.com', '10086.cn', '189.cn']
    },
    '管理': {
        'keywords': [
            '管理', '领导力', '团队', '项目管理', '敏捷', 'Scrum', 'OKR', 'KPI',
            '组织架构', '企业文化', '人力资源', '招聘', '绩效', '晋升',
            '产品管理', '产品经理', '运营', '增长', '用户运营', '数据分析',
            '战略规划', '商业模式', '商业分析', '市场营销', '品牌',
            '时间管理', '效率', '生产力', '工作方法', '会议', '决策',
            '麦肯锡', '波士顿', '贝恩', '埃森哲', '德勤'
        ],
        'domains': ['hbr.org', 'mckinsey.com', 'bain.com', 'bcg.com']
    },
    '社会生活': {
        'keywords': [
            '社会', '生活', '健康', '医疗', '教育', '养老', '育儿', '家庭',
            '旅行', '旅游', '美食', '餐厅', '菜谱', '健身', '运动', '瑜伽',
            '心理', '情感', '人际关系', '沟通', '心理学', '冥想', ' mindfulness',
            '理财', '投资', '房产', '保险', '基金', '股票', '加密货币',
            '时尚', '穿搭', '护肤', '美妆', '家居', '装修',
            '电影', '音乐', '书籍', '读书', '艺术', '展览'
        ],
        'domains': ['douban.com', 'xiaohongshu.com', 'zhihu.com', 'jianshu.com']
    },
    '技术其他': {
        'keywords': [
            '编程', '开发', '代码', '软件工程', '架构', '设计模式', '算法',
            '前端', '后端', '全栈', 'Web开发', '移动开发', 'iOS', 'Android',
            '数据库', 'SQL', 'NoSQL', 'Redis', 'MongoDB', 'MySQL', 'PostgreSQL',
            '云计算', 'AWS', 'Azure', '阿里云', '腾讯云', '华为云', 'Kubernetes', 'Docker',
            'DevOps', 'CI/CD', 'Git', 'GitHub', 'GitLab',
            '安全', '网络安全', '黑客', '加密', '漏洞', '渗透测试',
            'Python', 'JavaScript', 'TypeScript', 'Java', 'Go', 'Rust', 'C++', 'Rust'
        ],
        'domains': ['github.com', 'stackoverflow.com', 'dev.to', 'infoq.cn', 'oschina.net']
    }
}

DEFAULT_CATEGORY = '其他'


def classify_article(title: str, content: str, url: str = '') -> dict:
    """
    基于标题、内容和 URL 自动分类文章
    
    Returns:
        dict: {
            'category': '分类名',
            'confidence': 置信度分数(0-1),
            'reason': '分类理由'
        }
    """
    text = f"{title} {content}".lower()
    url_lower = url.lower()
    
    scores = {}
    
    for category, data in CATEGORIES.items():
        score = 0
        matched_keywords = []
        
        # 关键词匹配
        for keyword in data['keywords']:
            keyword_lower = keyword.lower()
            count = text.count(keyword_lower)
            if count > 0:
                score += count * 10
                matched_keywords.append(keyword)
        
        # 域名匹配
        for domain in data.get('domains', []):
            if domain in url_lower:
                score += 50  # 域名匹配权重较高
        
        # 标题关键词权重加倍
        title_lower = title.lower()
        for keyword in data['keywords']:
            if keyword.lower() in title_lower:
                score += 20
        
        scores[category] = {
            'score': score,
            'keywords': matched_keywords
        }
    
    # 找出最高分
    if scores:
        best_category = max(scores.keys(), key=lambda k: scores[k]['score'])
        best_score = scores[best_category]['score']
        
        # 计算置信度
        total_score = sum(s['score'] for s in scores.values())
        confidence = best_score / total_score if total_score > 0 else 0
        
        # 如果最高分太低，归类到"其他"
        if best_score < 30:
            return {
                'category': DEFAULT_CATEGORY,
                'confidence': 0.1,
                'reason': '未找到明显匹配的分类特征'
            }
        
        reason = f"匹配关键词: {', '.join(scores[best_category]['keywords'][:5])}"
        
        return {
            'category': best_category,
            'confidence': confidence,
            'reason': reason
        }
    
    return {
        'category': DEFAULT_CATEGORY,
        'confidence': 0,
        'reason': '无法确定分类'
    }


def main():
    parser = argparse.ArgumentParser(description='自动分类文章')
    parser.add_argument('--title', '-t', required=True, help='文章标题')
    parser.add_argument('--content', '-c', help='文章内容')
    parser.add_argument('--url', '-u', help='文章URL')
    parser.add_argument('--json', action='store_true', help='输出JSON格式')
    
    args = parser.parse_args()
    
    result = classify_article(args.title, args.content or '', args.url or '')
    
    if args.json:
        import json
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"建议分类: {result['category']}")
        print(f"置信度: {result['confidence']:.2%}")
        print(f"理由: {result['reason']}")


if __name__ == '__main__':
    main()
