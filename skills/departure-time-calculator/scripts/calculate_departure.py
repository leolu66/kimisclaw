#!/usr/bin/env python3
"""
出发时间计算器 - 根据航班/高铁时间计算最迟出发时间
支持：手动输入时间、航班号/车次号自动匹配路线
"""
import yaml
import re
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# 忙时定义
RUSH_HOURS = [
    (7, 0, 9, 30),    # 早高峰 7:00-9:30
    (17, 0, 19, 30),  # 晚高峰 17:00-19:30
]

def is_rush_hour(dt: datetime) -> bool:
    """判断给定时间是否处于忙时"""
    for start_h, start_m, end_h, end_m in RUSH_HOURS:
        start = dt.replace(hour=start_h, minute=start_m, second=0)
        end = dt.replace(hour=end_h, minute=end_m, second=0)
        if start <= dt <= end:
            return True
    return False

def load_yaml(filepath):
    """加载 YAML 配置文件"""
    if not os.path.exists(filepath):
        return {}
    with open(filepath, 'r', encoding='utf-8') as f:
        result = yaml.safe_load(f)
        return result if result is not None else {}

def save_yaml(filepath, data):
    """保存 YAML 配置文件"""
    with open(filepath, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False, default_flow_style=False)

def parse_time(time_str):
    """解析时间字符串，如 '17:30' 或 '17点30分'"""
    patterns = [
        (r'(\d{1,2}):(\d{2})', lambda m: (int(m.group(1)), int(m.group(2)))),
        (r'(\d{1,2})点(\d{1,2})分', lambda m: (int(m.group(1)), int(m.group(2)))),
        (r'(\d{1,2})点', lambda m: (int(m.group(1)), 0)),
    ]
    
    for pattern, extractor in patterns:
        match = re.search(pattern, time_str)
        if match:
            hour, minute = extractor(match)
            now = datetime.now()
            return now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    
    raise ValueError(f"无法解析时间: {time_str}")

def parse_transport_type(query):
    """从查询中识别交通类型"""
    if re.search(r'飞机|航班|起飞|机场|航站楼|flight', query, re.I):
        return 'flight'
    elif re.search(r'高铁|动车|火车|发车|检票|train|车次', query, re.I):
        return 'train'
    return None

def extract_flight_number(query):
    """提取航班号，如 CZ3122, CA1234"""
    match = re.search(r'([A-Z]{2}\d{3,4})', query.upper())
    return match.group(1) if match else None

def extract_train_number(query):
    """提取高铁/火车车次，如 G123, D4567, K88"""
    match = re.search(r'\b([GCDKZT]\d{1,4})\b', query.upper())
    return match.group(1) if match else None

def fuzzy_match_route(query, routes_data, locations_data):
    """根据查询模糊匹配路线
    
    扩展说明：添加新地点时，在此处添加关键词映射
    格式：'查询关键词': 'locations.yaml中的地点ID',
    """
    location_map = {
        # ===== 北京地点 =====
        '宿舍': 'beijing_dorm',
        '北京宿舍': 'beijing_dorm',
        '一品亦庄': 'beijing_dorm',
        '北京公司': 'beijing_office',
        '丽泽天地': 'beijing_office',
        '公司': 'beijing_office',
        '大兴': 'daxing_airport',
        '大兴机场': 'daxing_airport',
        '首都': 'capital_airport',
        '首都机场': 'capital_airport',
        '草桥': 'caoqiao_station',
        '草桥地铁': 'caoqiao_station',
        '北京南站': 'beijing_south_station',
        
        # ===== 南京地点 =====
        '家': 'nanjing_home',
        '南京家': 'nanjing_home',
        '长阳花园': 'nanjing_home',
        '南京总部': 'nanjing_hq',
        '雨花大道': 'nanjing_hq',
        '总部': 'nanjing_hq',
        '禄口': 'lukou_airport',
        '禄口机场': 'lukou_airport',
        '河西万达': 'nanjing_airport_bus_station',
        '河西万达大巴': 'nanjing_airport_bus_station',
        '机场大巴站': 'nanjing_airport_bus_station',
        '南京南站': 'nanjing_south_station',
        
        # ===== 广州地点 =====
        '潮漫酒店': 'guangzhou_cu_hotel',
        '广州联通软院': 'guangzhou_cu_hotel',
        '广州住处': 'guangzhou_home',
        # '白云机场': 'guangzhou_baiyun_airport',
        # '广州南站': 'guangzhou_south_station',
    }
    
    from_loc = None
    to_loc = None
    
    # 收集所有匹配的关键词及其位置
    matches = []
    for keyword, loc_id in location_map.items():
        pos = query.find(keyword)
        if pos != -1:
            matches.append((pos, keyword, loc_id))
    
    # 按位置排序
    matches.sort(key=lambda x: x[0])
    
    # 第一个匹配是出发地，最后一个匹配是目的地
    if matches:
        from_loc = matches[0][2]
        # 找不同的地点作为目的地
        for pos, keyword, loc_id in matches[1:]:
            if loc_id != from_loc:
                to_loc = loc_id
                break
    
    return from_loc, to_loc

def find_route(routes, from_loc, to_loc, transport_type=None):
    """查找匹配的路由"""
    matches = []
    
    for route_id, route in routes.items():
        route_from = route.get('from', '')
        route_to = route.get('to', '')
        route_transport = route.get('transport_type', '')
        
        from_match = (from_loc in route_id or 
                      from_loc == route_from or
                      from_loc in route.get('name', ''))
        
        to_match = (to_loc in route_id or 
                    to_loc == route_to or
                    to_loc in route.get('name', ''))
        
        if from_match and to_match:
            if transport_type and route_transport != transport_type:
                continue
            matches.append((route_id, route))
    
    if not matches:
        return None, None
    
    if len(matches) == 1:
        return matches[0]
    
    if transport_type:
        for route_id, route in matches:
            if route.get('transport_type') == transport_type:
                return route_id, route
    
    return matches[0]

def calculate_departure_time(route, arrival_time, is_rush):
    """计算出发时间"""
    segments = route.get('segments', [])
    transport_type = route.get('transport_type', 'flight')
    buffer = route.get('buffer', {'flight': 45, 'train': 15})
    route_note = route.get('note', '')
    
    buffer_minutes = buffer.get(transport_type, 45 if transport_type == 'flight' else 15)
    latest_arrival = arrival_time - timedelta(minutes=buffer_minutes)
    
    total_time = 0
    segment_details = []
    
    for seg in segments:
        mode = seg.get('mode', '未知')
        time_key = 'busy' if is_rush else 'idle'
        travel_time = seg.get(time_key, 30)
        wait_time = seg.get('wait', 0)
        seg_total = travel_time + wait_time
        
        segment_details.append({
            'from': seg.get('from'),
            'to': seg.get('to'),
            'mode': mode,
            'travel_time': travel_time,
            'wait_time': wait_time,
            'total': seg_total,
            'is_rush': is_rush,
            'price': seg.get('price'),
            'price_options': seg.get('price_options')
        })
        
        total_time += seg_total
    
    latest_departure = latest_arrival - timedelta(minutes=total_time)
    
    # 特殊处理：机场大巴按时刻表发车
    recommended_bus_time = None
    bus_schedule = route.get('bus_schedule')
    if bus_schedule or any('大巴' in seg.get('mode', '') for seg in segments):
        recommended_bus_time = calculate_bus_departure(arrival_time, buffer_minutes, 
                                                        segments[-1].get('busy' if is_rush else 'idle', 45),
                                                        bus_schedule)
    
    return {
        'route_name': route.get('name', '未知路线'),
        'transport_type': '飞机' if transport_type == 'flight' else '高铁',
        'arrival_time': arrival_time,
        'buffer_minutes': buffer_minutes,
        'latest_arrival_station': latest_arrival,
        'total_travel_time': total_time,
        'segments': segment_details,
        'latest_departure': latest_departure,
        'is_rush': is_rush,
        'route_note': route_note,
        'recommended_bus_time': recommended_bus_time,
        'price': route.get('price'),
        'price_options': route.get('price_options')
    }

def calculate_bus_departure(flight_time, buffer_minutes, bus_travel_time, bus_schedule=None):
    """根据飞机时间计算推荐的大巴发车时间"""
    # 最迟到达机场时间
    latest_arrival_airport = flight_time - timedelta(minutes=buffer_minutes)
    
    # 最迟大巴发车时间（假设大巴走最长时间）
    latest_bus_departure = latest_arrival_airport - timedelta(minutes=bus_travel_time)
    
    # 使用实际时刻表或默认每小时40分
    if bus_schedule:
        bus_times = bus_schedule
    else:
        bus_times = [f"{h:02d}:40" for h in range(5, 20)]  # 05:40-19:40
    
    # 从晚往早找，找到 <= latest_bus_departure 的最晚一班
    recommended = None
    for bt in reversed(bus_times):
        hour, minute = map(int, bt.split(':'))
        bt_time = flight_time.replace(hour=hour, minute=minute, second=0)
        if bt_time <= latest_bus_departure:
            recommended = bt
            break
    
    return recommended

def save_query_history(history_path, query, route_id, route, result, query_type='normal'):
    """保存查询历史"""
    history = load_yaml(history_path)
    
    if not history:
        history = {}
    if 'history' not in history or history['history'] is None:
        history['history'] = []
    
    timestamp = datetime.now()
    record_id = timestamp.strftime('%Y%m%d_%H%M%S')
    
    segments = route.get('segments', [])
    from_name = segments[0].get('from', '未知') if segments else '未知'
    to_name = segments[-1].get('to', '未知') if segments else '未知'
    
    # 检查是否已存在相同的路线查询
    existing = None
    for h in history['history']:
        if h.get('route_id') == route_id:
            existing = h
            break
    
    if existing:
        existing['used_count'] = existing.get('used_count', 1) + 1
        existing['last_used'] = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        existing['query'] = query
        if 'latest_departure' in result:
            existing['departure_time'] = result['latest_departure'].strftime('%H:%M')
        if 'arrival_time' in result:
            existing['arrival_time'] = result['arrival_time'].strftime('%H:%M')
    else:
        new_record = {
            'id': record_id,
            'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'query': query,
            'route_id': route_id,
            'from_name': from_name,
            'to_name': to_name,
            'used_count': 1,
            'last_used': timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }
        if 'latest_departure' in result:
            new_record['departure_time'] = result['latest_departure'].strftime('%H:%M')
        if 'arrival_time' in result:
            new_record['arrival_time'] = result['arrival_time'].strftime('%H:%M')
        history['history'].insert(0, new_record)
    
    save_yaml(history_path, history)
    return record_id

def list_history(history_path, limit=10):
    """列出历史查询记录"""
    history = load_yaml(history_path)
    records = history.get('history', [])
    
    if not records:
        print("暂无历史查询记录")
        return
    
    print(f"📜 最近 {min(len(records), limit)} 条查询历史：\n")
    print(f"{'序号':<4} {'时间':<20} {'路线':<30} {'复用次数':<8}")
    print("-" * 70)
    
    for i, record in enumerate(records[:limit], 1):
        route_desc = f"{record.get('from_name', '未知')} → {record.get('to_name', '未知')}"
        used = record.get('used_count', 1)
        last_used = record.get('last_used', record.get('timestamp', ''))[:16]
        
        print(f"{i:<4} {last_used:<20} {route_desc:<30} {used:<8}")
    
    print(f'\n💡 提示：使用历史序号快速查询，如 "历史 1，18:00的飞机"')

def use_history(history_path, history_index, new_time_str):
    """使用历史记录进行新查询"""
    history = load_yaml(history_path)
    records = history.get('history', [])
    
    if not records:
        print("暂无历史查询记录")
        return None
    
    try:
        idx = int(history_index) - 1
        if idx < 0 or idx >= len(records):
            print(f"无效的历史序号，有效范围：1-{len(records)}")
            return None
    except ValueError:
        print(f"无效的历史序号：{history_index}")
        return None
    
    record = records[idx]
    
    try:
        arrival_time = parse_time(new_time_str)
    except ValueError as e:
        print(f"错误：无法解析时间 '{new_time_str}'，请使用格式如 '17:30' 或 '17点30分'")
        return None
    
    return {
        'route_id': record.get('route_id'),
        'from_name': record.get('from_name'),
        'to_name': record.get('to_name'),
        'arrival_time': arrival_time,
        'original_query': record.get('query', '')
    }

def format_result(result):
    """格式化输出结果"""
    lines = []
    
    lines.append(f"📍 路线：{result['route_name']}")
    lines.append("")
    
    lines.append("🚗 行程详情：")
    for i, seg in enumerate(result['segments'], 1):
        rush_tag = "【忙时】" if seg['is_rush'] else "【闲时】"
        lines.append(f"  {i}. {seg['from']} → {seg['to']}")
        lines.append(f"     方式：{seg['mode']} {rush_tag}")
        lines.append(f"     耗时：{seg['travel_time']}分钟 + 等待{seg['wait_time']}分钟 = {seg['total']}分钟")
        
        # 显示每段价格
        if seg.get('price_options'):
            for opt in seg['price_options']:
                lines.append(f"     💰 {opt['name']}：{opt['price']}元 - {opt.get('note', '')}")
        elif seg.get('price'):
            lines.append(f"     💰 约{seg['price']}元")
    
    lines.append("")
    
    # 显示总价
    if result.get('price_options'):
        lines.append("💰 费用估算（多方案）：")
        for opt in result['price_options']:
            lines.append(f"  • {opt['name']}：{opt['total']}元")
            if opt.get('note'):
                lines.append(f"    {opt['note']}")
    elif result.get('price'):
        price_info = result['price']
        lines.append(f"💰 费用估算：{price_info['total']}元")
        if price_info.get('note'):
            lines.append(f"   {price_info['note']}")
    
    lines.append("")
    
    transport = result['transport_type']
    lines.append("⏱️ 时间计算：")
    lines.append(f"  {transport}时间：{result['arrival_time'].strftime('%H:%M')}")
    lines.append(f"  需提前{result['buffer_minutes']}分钟到达（截止{'登机' if transport == '飞机' else '检票'}）")
    lines.append(f"  最迟到达{('机场' if transport == '飞机' else '车站')}：{result['latest_arrival_station'].strftime('%H:%M')}")
    lines.append(f"  行程总耗时：{result['total_travel_time']}分钟")
    
    lines.append("")
    
    # 显示路线备注（如机场大巴时刻表说明）
    if result.get('route_note'):
        lines.append(f"💡 提示：{result['route_note']}")
        lines.append("")
    
    now = datetime.now()
    departure = result['latest_departure']
    time_diff = departure - now
    hours = time_diff.seconds // 3600
    minutes = (time_diff.seconds % 3600) // 60
    
    lines.append("=" * 40)
    
    # 如果有推荐的大巴时间，特别显示
    if result.get('recommended_bus_time'):
        lines.append(f"🚌 建议乘坐机场大巴：{result['recommended_bus_time']} 班次")
        lines.append("")
    
    lines.append(f"🚨 你最迟从家出发时间：{departure.strftime('%H:%M')}")
    
    if time_diff.total_seconds() > 0:
        lines.append(f"   距离现在还有：{hours}小时{minutes}分钟")
    else:
        lines.append(f"   ⚠️ 已经晚了！建议立即出发！")
    lines.append("=" * 40)
    
    return "\n".join(lines)

def main():
    if len(sys.argv) < 2:
        print("用法: python calculate_departure.py '<查询>'")
        print("")
        print("查询方式：")
        print("  1. 标准查询 - 提供路线和起飞时间")
        print("     python calculate_departure.py '从北京宿舍去大兴机场，17:30的飞机'")
        print("")
        print("  2. 航班号/车次号查询 - 提供航班号自动匹配路线")
        print("     python calculate_departure.py '从北京宿舍坐CZ3122'")
        print("     python calculate_departure.py '查高铁G1234从南京家出发'")
        print("")
        print("  3. 查看历史")
        print("     python calculate_departure.py '历史'")
        print("")
        print("  4. 复用历史")
        print("     python calculate_departure.py '历史 1，18:00的飞机'")
        sys.exit(1)
    
    query = sys.argv[1]
    
    # 加载配置
    script_dir = Path(__file__).parent.parent
    config_dir = script_dir / 'config'
    locations = load_yaml(config_dir / 'locations.yaml')
    routes = load_yaml(config_dir / 'routes.yaml')
    history_path = config_dir / 'history.yaml'
    
    # 处理历史查询
    if query in ['历史', 'history', '列出历史']:
        list_history(history_path)
        sys.exit(0)
    
    # 处理复用历史
    history_match = re.match(r'历史\s*(\d+)[，,]\s*(.+)', query)
    if history_match:
        history_idx = history_match.group(1)
        new_time = history_match.group(2)
        
        history_data = use_history(history_path, history_idx, new_time)
        if not history_data:
            sys.exit(1)
        
        route_id = history_data['route_id']
        routes_data = routes.get('routes', {})
        
        if route_id not in routes_data:
            print(f"错误：历史记录中的路线 '{route_id}' 已不存在")
            sys.exit(1)
        
        route = routes_data[route_id]
        now = datetime.now()
        is_rush = is_rush_hour(now)
        
        result = calculate_departure_time(route, history_data['arrival_time'], is_rush)
        print(format_result(result))
        
        new_query = f"从{history_data['from_name']}去{history_data['to_name']}，{new_time}"
        save_query_history(history_path, new_query, route_id, route, result)
        print(f"\n💾 已保存到历史记录")
        sys.exit(0)
    
    # 识别查询类型
    flight_number = extract_flight_number(query)
    train_number = extract_train_number(query)
    transport_type = parse_transport_type(query)
    
    # 尝试匹配地点
    routes_data = routes.get('routes', {})
    from_loc, to_loc = fuzzy_match_route(query, routes_data, locations.get('locations', {}))
    
    now = datetime.now()
    is_rush = is_rush_hour(now)
    
    # 模式B：航班号/车次号查询
    if flight_number or train_number:
        number = flight_number or train_number
        print(f"🔍 检测到{'航班号' if flight_number else '车次号'}：{number}")
        
        # 尝试查找路线
        if not from_loc:
            if '北京' in query:
                from_loc = 'beijing_dorm'
            elif '南京' in query:
                from_loc = 'nanjing_home'
        
        # 航班号默认目的地是机场
        if flight_number and not to_loc:
            if '北京' in query:
                to_loc = 'daxing_airport'
            elif '南京' in query:
                to_loc = 'lukou_airport'
        
        # 高铁车次默认目的地是高铁站
        if train_number and not to_loc:
            if '北京' in query:
                to_loc = 'beijing_south_station'
            elif '南京' in query:
                to_loc = 'nanjing_south_station'
        
        if from_loc and to_loc:
            route_id, route = find_route(routes_data, from_loc, to_loc, transport_type)
            if route:
                print(f"✅ 已匹配路线：{route['name']}")
                print("⚠️ 自动查询功能需要接入API")
                print("请提供起飞时间继续计算，格式如：17:30")
                print(f"\n示例：python calculate_departure.py '从北京宿舍去大兴机场，17:30的飞机'")
                sys.exit(0)
        
        print("未能自动匹配路线，请使用标准格式查询：")
        print("  从北京宿舍去大兴机场，17:30的飞机")
        sys.exit(0)
    
    # 标准模式：已知起飞/发车时间
    try:
        arrival_time = parse_time(query)
    except ValueError as e:
        print(f"错误：无法解析时间，请使用格式如 '17:30' 或 '17点30分'")
        print("支持的查询方式：")
        print("  1. '从北京宿舍去大兴机场，17:30的飞机'（标准查询）")
        print("  2. '从北京宿舍坐CZ3122'（航班号查询）")
        print("  3. '历史'（查看历史记录）")
        sys.exit(1)
    
    # 查找路线
    if not from_loc or not to_loc:
        print("未能识别出发地和目的地，请明确说明，例如：")
        print("  '从北京宿舍去大兴机场，17:30的飞机'")
        sys.exit(1)
    
    route_id, route = find_route(routes_data, from_loc, to_loc, transport_type)
    
    if not route:
        print(f"未找到匹配的路线")
        print(f"已配置的路线：")
        for rid, r in routes_data.items():
            print(f"  - {r.get('name', rid)}")
        sys.exit(1)
    
    # 计算出发时间
    result = calculate_departure_time(route, arrival_time, is_rush)
    print(format_result(result))
    
    # 保存查询历史
    save_query_history(history_path, query, route_id, route, result)
    print(f"\n💾 已保存到历史记录（使用 '历史' 命令查看）")

if __name__ == '__main__':
    main()
