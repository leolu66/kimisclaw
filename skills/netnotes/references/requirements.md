# NetNotes 依赖

## 必需依赖

```
requests>=2.28.0
beautifulsoup4>=4.11.0
```

## 可选依赖（用于反爬/动态页面）

```
playwright>=1.40.0
```

安装 playwright 后还需要下载浏览器：
```bash
playwright install chromium
```

## 完整安装

```bash
# 基础功能
pip install requests beautifulsoup4

# 完整功能（包含 playwright）
pip install requests beautifulsoup4 playwright
playwright install chromium
```
