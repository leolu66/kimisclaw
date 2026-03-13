# 扩展指南 - 如何添加新路线

本文档说明如何为"几点出发"技能添加新的路线。

## 快速步骤

添加一条新路线只需要 **3个步骤**：

### 第1步：添加地点（config/locations.yaml）

如果地点已存在，跳过此步骤。

```yaml
# 在文件末尾添加新地点
guangzhou_home:
  name: "广州住处"
  city: "广州"
  address: "具体地址"
  type: "residence"  # 类型：residence, office, airport, train_station, bus_station

guangzhou_baiyun_airport:
  name: "白云机场"
  city: "广州"
  address: "广州白云国际机场T2航站楼"
  type: "airport"
```

### 第2步：添加路线（config/routes.yaml）

```yaml
# 在 routes: 下添加新路线
guangzhou_home_to_baiyun_airport:
  name: "广州住处 → 白云机场"
  from: "guangzhou_home"
  to: "guangzhou_baiyun_airport"
  transport_type: "flight"  # flight=飞机, train=高铁
  segments:
    - from: "广州住处"
      to: "白云机场"
      mode: "地铁3号线北延段"
      idle: 50    # 闲时分钟
      busy: 65    # 忙时分钟
      wait: 10    # 等待分钟
  buffer:
    flight: 45
    train: 15
```

### 第3步：添加关键词映射（scripts/calculate_departure.py）

找到 `fuzzy_match_route` 函数中的 `location_map`，添加：

```python
location_map = {
    # ... 已有地点 ...
    
    # ===== 广州地点 =====
    '广州': 'guangzhou_home',
    '广州住处': 'guangzhou_home',
    '白云机场': 'guangzhou_baiyun_airport',
}
```

## 完整示例：添加广州→南京路线

### 场景1：从广州住处去白云机场坐飞机

**1. 添加地点：**
```yaml
guangzhou_home:
  name: "广州住处"
  city: "广州"
  address: "广州天河区"
  type: "residence"

guangzhou_baiyun_airport:
  name: "白云机场"
  city: "广州"
  address: "广州白云国际机场"
  type: "airport"
```

**2. 添加路线：**
```yaml
guangzhou_home_to_baiyun_airport:
  name: "广州住处 → 白云机场"
  from: "guangzhou_home"
  to: "guangzhou_baiyun_airport"
  transport_type: "flight"
  segments:
    - from: "广州住处"
      to: "白云机场"
      mode: "地铁3号线北延段"
      idle: 50
      busy: 65
      wait: 10
  buffer:
    flight: 45
    train: 15
```

**3. 添加关键词：**
```python
'广州': 'guangzhou_home',
'广州住处': 'guangzhou_home',
'白云': 'guangzhou_baiyun_airport',
'白云机场': 'guangzhou_baiyun_airport',
```

### 场景2：广州住处 → 南京家（跨城路线）

对于这种路线，建议拆分为两段：
1. 广州住处 → 白云机场（本地路线，已添加）
2. 南京禄口机场 → 南京家（本地路线，已存在）

跨城行程需要分别计算两端的出发时间。

## 高级配置

### 机场大巴时刻表

如果路线涉及固定时刻表的交通（如机场大巴），添加时刻表：

```yaml
nanjing_home_to_lukou_airport:
  name: "家 → 禄口机场"
  from: "nanjing_home"
  to: "lukou_airport"
  transport_type: "flight"
  note: "河西万达机场大巴每小时40分发车"
  bus_schedule: ["05:40", "06:40", "07:40", "08:40", "09:40", ...]
  segments:
    ...
```

### 多段行程

支持多段行程，例如：打车 → 地铁 → 机场线

```yaml
segments:
  - from: "北京宿舍"
    to: "草桥地铁口"
    mode: "打车"
    idle: 25
    busy: 35
    wait: 10
  - from: "草桥地铁口"
    to: "大兴机场"
    mode: "地铁机场线（从G口进入）"
    idle: 20
    busy: 20
    wait: 5
```

## 测试新路线

添加完成后，测试：

```bash
cd /root/.openclaw/workspace/skills/departure-time-calculator
python3 scripts/calculate_departure.py "从广州住处去白云机场，15:00的飞机"
```

## 模板文件

参考 `config/route_template.yaml` 获取完整模板。
