---
name: departure-time-calculator
description: |
  计算出差时从出发地到机场/高铁站的最迟出发时间。
  支持两种查询方式：1) 提供路线和起飞时间；2) 提供航班号/车次号自动匹配路线。
  支持历史记录保存和复用。易于扩展，支持添加新城市和新路线。
  
  触发场景：
  - "从北京宿舍去大兴机场，17:30的飞机"（标准查询）
  - "从北京宿舍坐CZ3122"（航班号查询）
  - "查高铁G1234从南京家出发"（车次号查询）
  - "历史" / "历史 1，18:00的飞机"（历史复用）
  - 添加新路线（参见 EXTENSION_GUIDE.md）
---

# 几点出发 - 出差出发时间计算器

根据预设的路线方案，计算从出发地到机场/高铁站的最迟出发时间。

## 使用方法

### 模式1：标准查询（提供路线和时间）

```
从北京宿舍去大兴机场，17:30的飞机
查南京总部到禄口机场的高铁，14:00发车
```

### 模式2：航班号/车次号查询

```
从北京宿舍坐CZ3122
查高铁G1234从南京家出发
```

### 历史记录功能

```
历史                    # 查看历史
历史 1，18:00的飞机      # 复用历史路线
```

## 已配置路线（8条）

**北京：**
- 北京宿舍 → 大兴机场（飞机，经草桥G口）
- 北京宿舍 → 北京南站（高铁）
- 北京公司 → 大兴机场（飞机，经草桥G口）
- 北京公司 → 北京南站（高铁）

**南京：**
- 家 → 禄口机场（飞机，机场大巴路线）
- 南京总部 → 禄口机场（飞机，地铁S1）
- 家 → 南京南站（高铁）
- 南京总部 → 南京南站（高铁）

**机场大巴时刻（河西万达）：**
05:40, 06:40, 07:40, 08:40, 09:40, 10:40, 11:40, 12:40, 13:40, 14:40, 15:40, 16:40, 17:40, 18:40, 19:40
（每小时40分发车，乘车地点：江东万达广场公交站台）

详见 `references/routes.md`

## 扩展性

### 添加新路线

3步添加新路线，详见 `EXTENSION_GUIDE.md`：

1. **添加地点** → `config/locations.yaml`
2. **添加路线** → `config/routes.yaml`
3. **添加关键词** → `scripts/calculate_departure.py`

### 模板文件

- `config/route_template.yaml` - 路线配置模板
- `EXTENSION_GUIDE.md` - 完整扩展指南

## 脚本使用

```bash
# 标准查询
python scripts/calculate_departure.py "从北京宿舍去大兴机场，17:30的飞机"

# 航班号查询
python scripts/calculate_departure.py "从北京宿舍坐CZ3122"

# 查看历史
python scripts/calculate_departure.py "历史"

# 复用历史
python scripts/calculate_departure.py "历史 1，18:00的飞机"
```

## 配置说明

- `config/locations.yaml` - 地点配置
- `config/routes.yaml` - 路线方案
- `config/history.yaml` - 查询历史
- `references/routes.md` - 路线详情文档

## 开发规范

参见：
- `skills/SKILL_DO.md` - 开发规范
- `skills/SKILL_TEMPLATE.md` - 技能模板
