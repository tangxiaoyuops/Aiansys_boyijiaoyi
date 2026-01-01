"""
高级出货分析器
基于时间轴和价位记忆的出货识别框架

核心思路：
1. 按时间轴扫描，识别分水岭事件（涨停/大阳突破前高）
2. 以分水岭为中心，聚合出货片段（高位放量震荡区间）
3. 将相邻片段合并为出货周期（基于价位和回落深度）
4. 基于周期时长、分水岭次数、后续跌幅，判断规模（small/medium/large）
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class WatershedEvent:
    """分水岭事件"""
    date: pd.Timestamp
    price: float
    breakthrough_price: float  # 突破的前高价位
    breakthrough_high_id: int  # 被突破的前高ID
    volume_ratio: float  # 当日成交量/前期均量
    is_limit_up: bool  # 是否涨停
    post_days_max_gain: float  # 后续N天最大涨幅
    post_days_max_drop: float  # 后续N天最大跌幅


@dataclass
class DistributionSegment:
    """出货片段"""
    start_date: pd.Timestamp
    end_date: pd.Timestamp
    high_price: float
    low_price: float
    avg_price: float
    volume_ratio: float  # 片段均量/前期均量
    watershed_events: List[WatershedEvent]  # 片段内的分水岭事件
    days: int
    post_drop_pct: float  # 片段结束后最大跌幅


@dataclass
class DistributionCycle:
    """出货周期"""
    start_date: pd.Timestamp
    end_date: pd.Timestamp
    segments: List[DistributionSegment]
    total_watershed_count: int
    cycle_days: int
    max_price: float
    min_price_in_cycle: float
    post_cycle_drop_pct: float  # 周期结束后最大跌幅
    post_cycle_drop_days: int  # 周期结束后下跌持续天数
    scale: str  # small/medium/large


def find_significant_highs(df: pd.DataFrame, window: int = 20, min_gain_from_low: float = 0.15) -> List[Dict[str, Any]]:
    """
    找出所有显著高点（用于判断"突破前高"）（性能优化版本）
    
    Args:
        df: 股票数据（按日期排序）
        window: 局部高点窗口（前后N天）
        min_gain_from_low: 从局部低点的最小涨幅（过滤噪音）
    
    Returns:
        List of {date, price, high_id, post_drop_pct, post_drop_days}
    """
    if len(df) < window * 2:
        return []
    
    # 性能优化：预先提取需要的列，避免重复访问
    highs_col = df['最高'].values
    lows_col = df['最低'].values
    dates_col = df['日期'].values
    
    highs = []
    high_id = 0
    
    # 性能优化：使用滑动窗口，减少重复计算
    # 使用numpy的rolling window会更高效，但这里用简单方法
    total_points = len(df) - window * 2
    check_interval = max(10, total_points // 20)  # 每5%打印一次进度
    
    for i in range(window, len(df) - window):
        # 进度日志（每5%打印一次）
        if (i - window) % check_interval == 0:
            progress = (i - window) / total_points * 100 if total_points > 0 else 0
            print(f"[出货分析] 查找显著高点进度: {progress:.1f}% ({i-window}/{total_points})")
        
        current_high = highs_col[i]
        
        # 性能优化：使用numpy数组切片，比DataFrame操作快
        local_window = highs_col[i-window:i+window+1]
        local_max = local_window.max()
        if current_high < local_max * 0.99:  # 不是最高点
            continue
        
        # 找局部低点（前window天）
        local_low = lows_col[i-window:i].min()
        gain_from_low = (current_high - local_low) / local_low if local_low > 0 else 0
        
        if gain_from_low < min_gain_from_low:
            continue
        
        # 计算后续最大跌幅（用于判断是否出货高点）
        post_end = min(i+120, len(df))
        if i+1 < post_end:
            post_lows = lows_col[i+1:post_end]
            post_low = post_lows.min()
            post_drop = (current_high - post_low) / current_high * 100 if current_high > 0 else 0
            # 简化计算：用后续天数作为下跌持续天数
            post_drop_days = post_end - i - 1
        else:
            post_drop = 0
            post_drop_days = 0
        
        highs.append({
            'date': dates_col[i],
            'price': float(current_high),
            'high_id': high_id,
            'post_drop_pct': float(post_drop),
            'post_drop_days': int(post_drop_days)
        })
        high_id += 1
    
    return highs


def detect_watershed_events(df: pd.DataFrame, significant_highs: List[Dict[str, Any]], 
                            lookback_days: int = 250) -> List[WatershedEvent]:
    """
    按时间轴扫描，检测分水岭事件（性能优化版本）
    
    分水岭特征：
    - 涨停或大阳（涨幅>5%）
    - 放量（>前期均量1.5倍）
    - 突破某个历史高点价位（收盘价 > 前高 * 1.01）
    """
    if len(df) < 60:
        return []
    
    events = []
    
    # 性能优化：预先建立日期到索引的映射（只创建一次）
    date_to_index = {}
    for idx, row in df.iterrows():
        date = row['日期']
        if date not in date_to_index:
            date_to_index[date] = idx
    
    # 性能优化：预先计算每个significant_high的索引，并排序
    high_indexes = []
    for h in significant_highs:
        high_idx = date_to_index.get(h['date'])
        if high_idx is not None:
            high_indexes.append((high_idx, h))
    high_indexes.sort(key=lambda x: x[0])  # 按索引排序
    
    # 计算前期均量（用于判断放量）
    vol_avg_baseline = df['成交量'].tail(60).mean()
    
    # 进度日志
    total_points = len(df) - 60
    check_interval = max(1, total_points // 20)  # 每5%打印一次进度
    
    for i in range(60, len(df)):
        # 进度日志
        if (i - 60) % check_interval == 0:
            progress = (i - 60) / total_points * 100 if total_points > 0 else 0
            if progress > 0:
                print(f"[出货分析] 检测分水岭事件进度: {progress:.1f}% ({i-60}/{total_points})")
        row = df.iloc[i]
        date = row['日期']
        close = row['收盘']
        open_price = row['开盘']
        high = row['最高']
        volume = row['成交量']
        
        # 判断是否大阳/涨停
        body_pct = (close - open_price) / open_price if open_price > 0 else 0
        is_big_yang = body_pct > 0.05  # 涨幅>5%
        is_limit_up = body_pct > 0.095  # 接近涨停
        
        if not is_big_yang:
            continue
        
        # 判断是否放量
        vol_ratio = volume / vol_avg_baseline if vol_avg_baseline > 0 else 1.0
        if vol_ratio < 1.5:
            continue
        
        # 性能优化：只检查lookback_days内的前高（使用预排序的列表）
        lookback_start = i - lookback_days if i >= lookback_days else 0
        breakthrough_high = None
        breakthrough_high_id = None
        
        # 从后往前查找（因为已经排序，可以提前退出）
        for high_idx, high_info in reversed(high_indexes):
            if high_idx < lookback_start:
                break  # 已经超出范围，可以提前退出
            if high_idx >= i:
                continue  # 不能是未来的高点
            if close >= high_info['price'] * 1.01:  # 突破前高1%以上
                breakthrough_high = high_info['price']
                breakthrough_high_id = high_info['high_id']
                break
        
        if breakthrough_high is None:
            continue
        
        # 计算后续N天表现（用于判断是否真出货）
        post_segment = df.iloc[i+1:i+10] if i+10 < len(df) else df.iloc[i+1:]
        if not post_segment.empty:
            post_max = post_segment['最高'].max()
            post_min = post_segment['最低'].min()
            post_max_gain = (post_max - close) / close * 100 if close > 0 else 0
            post_max_drop = (close - post_min) / close * 100 if close > 0 else 0
        else:
            post_max_gain = 0
            post_max_drop = 0
        
        events.append(WatershedEvent(
            date=date,
            price=float(close),
            breakthrough_price=breakthrough_high,
            breakthrough_high_id=breakthrough_high_id,
            volume_ratio=float(vol_ratio),
            is_limit_up=is_limit_up,
            post_days_max_gain=float(post_max_gain),
            post_days_max_drop=float(post_max_drop)
        ))
    
    return events


def aggregate_distribution_segments(df: pd.DataFrame, watershed_events: List[WatershedEvent],
                                   price_tolerance: float = 0.15) -> List[DistributionSegment]:
    """
    以分水岭事件为中心，聚合出货片段（性能优化版本）
    
    策略：
    - 每个分水岭前后扩展，找到高位放量震荡区间
    - 如果两个分水岭时间接近且价位重叠，合并为同一片段
    """
    if not watershed_events:
        return []
    
    segments = []
    
    # 性能优化：预先建立日期到索引的映射
    date_to_index = {}
    for idx, row in df.iterrows():
        date = row['日期']
        if date not in date_to_index:
            date_to_index[date] = idx
    
    # 性能优化：预先提取需要的列为numpy数组，避免循环中重复访问DataFrame
    closes_col = df['收盘'].values
    highs_col = df['最高'].values
    lows_col = df['最低'].values
    volumes_col = df['成交量'].values
    dates_col = df['日期'].values
    
    # 按日期排序
    events_sorted = sorted(watershed_events, key=lambda e: e.date)
    
    print(f"[出货分析] 聚合出货片段: 处理 {len(events_sorted)} 个分水岭事件...")
    
    i = 0
    while i < len(events_sorted):
        if i % 1 == 0:  # 每个事件都打印进度
            print(f"[出货分析] 处理第 {i+1}/{len(events_sorted)} 个分水岭事件...")
        event = events_sorted[i]
        segment_events = [event]
        
        # 向前扩展：找片段起点（价格开始进入高位区间）
        start_idx = date_to_index.get(event.date)
        if start_idx is None:
            i += 1
            continue
        
        # 向前找：价格进入 event.price * (1 - price_tolerance) 以上
        price_lower = event.price * (1 - price_tolerance)
        # 性能优化：使用numpy数组而不是df.iloc
        for j in range(start_idx - 1, max(0, start_idx - 60), -1):
            if closes_col[j] < price_lower:
                start_idx = j + 1
                break
        
        # 向后扩展：找片段终点
        # 检查后续是否有其他分水岭事件（时间接近且价位重叠）
        end_idx = start_idx + 30  # 默认30天
        merged = False  # 标记是否合并了其他事件
        
        for k in range(i + 1, len(events_sorted)):
            next_event = events_sorted[k]
            next_idx = date_to_index.get(next_event.date)
            if next_idx is None:
                continue
            
            # 如果下一个分水岭在30天内，且价位接近，合并
            if (next_idx - start_idx <= 30 and 
                abs(next_event.price - event.price) / event.price < price_tolerance):
                segment_events.append(next_event)
                end_idx = min(len(df) - 1, next_idx + 20)
                merged = True
                i = k + 1  # 跳过已合并的事件
                break
            elif next_idx - start_idx > 30:
                break
        
        # 如果没合并，向后找价格明显回落的位置
        if not merged:
            # 性能优化：使用numpy数组而不是df.iloc
            for j in range(start_idx + 10, min(len(df), start_idx + 60)):
                if closes_col[j] < price_lower:
                    end_idx = j
                    break
        
        # 检查边界
        if end_idx + 1 > len(df) or end_idx < start_idx:
            if not merged:
                i += 1
            continue
        
        # 检查片段长度
        if end_idx - start_idx + 1 < 3:
            if not merged:
                i += 1
            continue
        
        # 性能优化：使用numpy数组切片计算统计值
        segment_high = float(highs_col[start_idx:end_idx+1].max())
        segment_low = float(closes_col[start_idx:end_idx+1].min())
        segment_avg = float(closes_col[start_idx:end_idx+1].mean())
        
        # 计算放量倍数（对比片段前60天）
        pre_start = max(0, start_idx - 60)
        if start_idx > pre_start:
            pre_vol_avg = volumes_col[pre_start:start_idx].mean()
        else:
            pre_vol_avg = volumes_col[start_idx:end_idx+1].mean()
        segment_vol_avg = volumes_col[start_idx:end_idx+1].mean()
        vol_ratio = segment_vol_avg / pre_vol_avg if pre_vol_avg > 0 else 1.0
        
        # 计算后续最大跌幅
        post_end = min(len(df), end_idx + 120)
        if end_idx + 1 < post_end:
            post_low = float(lows_col[end_idx+1:post_end].min())
            post_drop = (segment_high - post_low) / segment_high * 100 if segment_high > 0 else 0
        else:
            post_drop = 0
        
        # 确保日期是 pandas Timestamp 类型（numpy.datetime64 没有 strftime 方法）
        start_date = pd.Timestamp(dates_col[start_idx]) if isinstance(dates_col[start_idx], np.datetime64) else dates_col[start_idx]
        end_date = pd.Timestamp(dates_col[end_idx]) if isinstance(dates_col[end_idx], np.datetime64) else dates_col[end_idx]
        
        segments.append(DistributionSegment(
            start_date=start_date,
            end_date=end_date,
            high_price=segment_high,
            low_price=segment_low,
            avg_price=segment_avg,
            volume_ratio=float(vol_ratio),
            watershed_events=segment_events,
            days=end_idx - start_idx + 1,
            post_drop_pct=float(post_drop)
        ))
        
        # 如果没合并其他事件，递增i
        if not merged:
            i += 1
    
    print(f"[出货分析] 聚合完成: 生成 {len(segments)} 个出货片段")
    return segments


def merge_segments_to_cycles(segments: List[DistributionSegment], df: pd.DataFrame,
                            price_tolerance: float = 0.25, min_drop_for_break: float = 0.30) -> List[DistributionCycle]:
    """
    将相邻片段合并为出货周期（性能优化版本）
    
    合并条件：
    - 相邻片段之间的最低价仍在整体高位附近（没走完整4/5阶段）
    - 一旦出现深跌（>30%）且持续，说明周期结束
    """
    if not segments:
        return []
    
    # 性能优化：预先建立日期到索引的映射
    date_to_index = {}
    for idx, row in df.iterrows():
        date = row['日期']
        if date not in date_to_index:
            date_to_index[date] = idx
    
    # 性能优化：预先提取最低价列为numpy数组
    lows_col = df['最低'].values
    
    cycles = []
    current_cycle_segments = [segments[0]]
    
    for i in range(1, len(segments)):
        prev_segment = segments[i-1]
        curr_segment = segments[i]
        
        # 计算两个片段之间的最低价
        prev_end_idx = date_to_index.get(prev_segment.end_date)
        curr_start_idx = date_to_index.get(curr_segment.start_date)
        
        if prev_end_idx is None or curr_start_idx is None:
            current_cycle_segments.append(curr_segment)
            continue
        
        # 性能优化：使用numpy数组切片而不是DataFrame切片
        if prev_end_idx + 1 < curr_start_idx:
            gap_low = float(lows_col[prev_end_idx+1:curr_start_idx].min())
            gap_drop_from_prev_high = (prev_segment.high_price - gap_low) / prev_segment.high_price if prev_segment.high_price > 0 else 0
            
            # 如果回落深度>30%，且持续时间>60天，说明周期结束
            gap_days = curr_start_idx - prev_end_idx - 1
            if gap_drop_from_prev_high > min_drop_for_break and gap_days > 60:
                # 结束当前周期
                cycle = _create_cycle_from_segments(current_cycle_segments, df)
                cycles.append(cycle)
                current_cycle_segments = [curr_segment]
            else:
                # 合并到当前周期
                current_cycle_segments.append(curr_segment)
        else:
            current_cycle_segments.append(curr_segment)
    
    # 处理最后一个周期
    if current_cycle_segments:
        cycle = _create_cycle_from_segments(current_cycle_segments, df)
        cycles.append(cycle)
    
    return cycles


def _create_cycle_from_segments(segments: List[DistributionSegment], df: pd.DataFrame) -> DistributionCycle:
    """从片段列表创建出货周期（性能优化版本）"""
    if not segments:
        return None
    
    start_date = min(s.start_date for s in segments)
    end_date = max(s.end_date for s in segments)
    
    total_watershed = sum(len(s.watershed_events) for s in segments)
    max_price = max(s.high_price for s in segments)
    min_price_in_cycle = min(s.low_price for s in segments)
    
    # 性能优化：使用日期索引映射
    date_to_index = {row['日期']: idx for idx, row in df.iterrows()}
    
    # 性能优化：预先提取最低价列为numpy数组
    lows_col = df['最低'].values
    
    # 计算周期结束后的最大跌幅和持续天数
    end_idx = date_to_index.get(end_date)
    if end_idx is not None:
        if end_idx + 1 < len(df):
            post_end = min(len(df), end_idx + 500)
            if end_idx + 1 < post_end:
                # 性能优化：使用numpy数组切片而不是DataFrame切片
                post_low = float(lows_col[end_idx+1:post_end].min())
                post_drop = (max_price - post_low) / max_price * 100 if max_price > 0 else 0
                post_drop_days = post_end - end_idx - 1
            else:
                post_drop = 0
                post_drop_days = 0
        else:
            post_drop = 0
            post_drop_days = 0
    else:
        post_drop = 0
        post_drop_days = 0
    
    # 判断规模
    if isinstance(start_date, pd.Timestamp) and isinstance(end_date, pd.Timestamp):
        cycle_days = (end_date - start_date).days
    else:
        cycle_days = 0
    scale = _classify_cycle_scale(cycle_days, total_watershed, post_drop, post_drop_days)
    
    return DistributionCycle(
        start_date=start_date,
        end_date=end_date,
        segments=segments,
        total_watershed_count=total_watershed,
        cycle_days=cycle_days,
        max_price=max_price,
        min_price_in_cycle=min_price_in_cycle,
        post_cycle_drop_pct=float(post_drop),
        post_cycle_drop_days=int(post_drop_days),
        scale=scale
    )


def _classify_cycle_scale(cycle_days: int, watershed_count: int, post_drop: float, post_drop_days: int) -> str:
    """
    判断出货周期规模
    
    规则（基于用户600536案例）：
    - 大规模：周期>200天，或分水岭>=3次，或后续跌幅>50%且持续>1年
    - 中等规模：周期60-200天，分水岭2次，或后续跌幅30-50%且持续3-12个月
    - 小规模：周期<60天，分水岭1-2次，后续跌幅<30%或持续时间短
    """
    if cycle_days > 200 or watershed_count >= 3 or (post_drop > 50 and post_drop_days > 250):
        return 'large'
    elif cycle_days >= 60 or watershed_count >= 2 or (post_drop > 30 and post_drop_days > 90):
        return 'medium'
    else:
        return 'small'


def analyze_distribution_advanced(df: pd.DataFrame) -> Dict[str, Any]:
    """
    高级出货分析主函数
    
    Returns:
        {
            'cycles': List[DistributionCycle],
            'latest_cycle': DistributionCycle,
            'latest_scale': str,
            'watershed_events': List[WatershedEvent],
            'summary': str
        }
    """
    if len(df) < 100:
        return {
            'cycles': [],
            'latest_cycle': None,
            'latest_scale': 'unknown',
            'watershed_events': [],
            'summary': '数据不足，无法分析'
        }
    
    # 1. 找出显著高点（覆盖3年数据，约750个交易日）
    print(f"[出货分析] 步骤1/4: 查找显著高点（数据量: {len(df)}）...")
    significant_highs = find_significant_highs(df, window=20, min_gain_from_low=0.15)
    print(f"[出货分析] 找到 {len(significant_highs)} 个显著高点")
    
    # 2. 检测分水岭事件（回溯3年，约750个交易日）
    # 使用750天作为lookback_days，确保覆盖往前3年的所有出货情况
    print(f"[出货分析] 步骤2/4: 检测分水岭事件（回溯750天）...")
    watershed_events = detect_watershed_events(df, significant_highs, lookback_days=750)
    print(f"[出货分析] 检测到 {len(watershed_events)} 个分水岭事件")
    
    # 3. 聚合出货片段
    print(f"[出货分析] 步骤3/4: 聚合出货片段...")
    segments = aggregate_distribution_segments(df, watershed_events, price_tolerance=0.15)
    print(f"[出货分析] 聚合为 {len(segments)} 个出货片段")
    
    # 4. 合并为出货周期
    print(f"[出货分析] 步骤4/4: 合并为出货周期...")
    cycles = merge_segments_to_cycles(segments, df, price_tolerance=0.25, min_drop_for_break=0.30)
    print(f"[出货分析] 合并为 {len(cycles)} 个出货周期")
    
    # 5. 取最近一个周期
    latest_cycle = cycles[-1] if cycles else None
    
    # 6. 生成总结
    summary_parts = []
    if latest_cycle:
        scale_map = {'small': '小规模', 'medium': '中等规模', 'large': '大规模'}
        summary_parts.append(
            f"最近一轮出货周期：{scale_map.get(latest_cycle.scale, latest_cycle.scale)}出货"
        )
        # 确保日期是 Timestamp 类型，支持 strftime
        start_date_str = pd.Timestamp(latest_cycle.start_date).strftime('%Y-%m-%d') if not isinstance(latest_cycle.start_date, pd.Timestamp) else latest_cycle.start_date.strftime('%Y-%m-%d')
        end_date_str = pd.Timestamp(latest_cycle.end_date).strftime('%Y-%m-%d') if not isinstance(latest_cycle.end_date, pd.Timestamp) else latest_cycle.end_date.strftime('%Y-%m-%d')
        summary_parts.append(
            f"周期时间：{start_date_str} ~ {end_date_str}"
        )
        summary_parts.append(f"分水岭次数：{latest_cycle.total_watershed_count}")
        summary_parts.append(f"周期后最大跌幅：{latest_cycle.post_cycle_drop_pct:.1f}%")
        if latest_cycle.post_cycle_drop_days > 0:
            summary_parts.append(f"下跌持续天数：{latest_cycle.post_cycle_drop_days}天")
    
    return {
        'cycles': cycles,
        'latest_cycle': latest_cycle,
        'latest_scale': latest_cycle.scale if latest_cycle else 'none',
        'watershed_events': watershed_events,
        'segments': segments,
        'summary': '\n'.join(summary_parts) if summary_parts else '未检测到明显出货周期'
    }

