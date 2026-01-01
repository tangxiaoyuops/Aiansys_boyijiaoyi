"""
结构化数据 Agent
整理原始K线数据，输出结构化信息供LLM分析使用
"""
from core.models.state import AnalysisState
from core.tools.advanced_distribution_analyzer import (
    analyze_distribution_advanced,
    find_significant_highs,
)
from core.tools.technical_analyzer import (
    detect_capitulation,
    detect_base,
    detect_breakout,
    detect_box,
    compute_gains,
    compute_max_drawdown,
    compute_volatility,
    compute_days_from_high,
    calculate_washout_indicators,
    find_o_point,
    calculate_ma,
)
import pandas as pd
from typing import Dict, Any, List


def structured_data_node(state: AnalysisState) -> AnalysisState:
    """
    结构化数据节点：
    1. 整理分水岭事件列表
    2. 整理出货周期列表
    3. 识别阶段候选区间（O点、恐慌低点、箱体等）
    4. 生成最近180-300日的K线简表
    """
    stock_code = state.get('stock_code', '')
    stock_data = state.get('stock_data')
    if stock_data is None or stock_data.empty:
        raise ValueError("股票数据为空")
    
    df = stock_data.copy()
    # 只在非回测模式或首次分析时打印详细日志
    is_backtest = state.get('run_backtest', False)
    if not is_backtest:
        print(f"[结构化数据] 开始处理 {stock_code}...")
        print(f"[结构化数据] 数据量: {len(df)} 条")
        # 调试：打印原始K线价格示例，帮助排查异常开盘价/跌停标记
        try:
            print("[结构化数据] 原始K线价格（最近10条，进入结构化前）：")
            print(df[['日期', '开盘', '最高', '最低', '收盘']].tail(10))
        except Exception:
            pass
    # 确保数据类型正确
    for col in ['开盘', '收盘', '最高', '最低', '成交量', '涨跌幅']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    df['日期'] = pd.to_datetime(df['日期'], errors='coerce')
    df = df.dropna(subset=['日期', '收盘']).sort_values('日期').reset_index(drop=True)
    
    # 数据验证和清洗
    if not df.empty:
        # 确保最高 >= 最低
        invalid_high_low = df['最高'] < df['最低']
        if invalid_high_low.any():
            print(f"[结构化数据] 警告：发现 {invalid_high_low.sum()} 条数据最高 < 最低，正在修复...")
            # 交换最高和最低
            df.loc[invalid_high_low, ['最高', '最低']] = df.loc[invalid_high_low, ['最低', '最高']].values
        
        # 确保收盘在最高和最低之间
        invalid_close = (df['收盘'] > df['最高']) | (df['收盘'] < df['最低'])
        if invalid_close.any():
            print(f"[结构化数据] 警告：发现 {invalid_close.sum()} 条数据收盘不在最高最低之间，正在修复...")
            # 将收盘价限制在最高和最低之间
            df.loc[invalid_close, '收盘'] = df.loc[invalid_close, ['最高', '最低', '收盘']].apply(
                lambda x: max(min(x['收盘'], x['最高']), x['最低']), axis=1
            )
        
        # 确保开盘在最高和最低之间
        invalid_open = (df['开盘'] > df['最高']) | (df['开盘'] < df['最低'])
        if invalid_open.any():
            print(f"[结构化数据] 警告：发现 {invalid_open.sum()} 条数据开盘不在最高最低之间，正在修复...")
            # 将开盘价限制在最高和最低之间
            df.loc[invalid_open, '开盘'] = df.loc[invalid_open, ['最高', '最低', '开盘']].apply(
                lambda x: max(min(x['开盘'], x['最高']), x['最低']), axis=1
            )
        
        # 移除明显异常的数据（价格 <= 0）
        invalid_price = (df['收盘'] <= 0) | (df['开盘'] <= 0) | (df['最高'] <= 0) | (df['最低'] <= 0)
        if invalid_price.any():
            print(f"[结构化数据] 警告：发现 {invalid_price.sum()} 条数据价格 <= 0，正在移除...")
            df = df[~invalid_price].copy()
        
        df = df.reset_index(drop=True)
    
    if df.empty or len(df) < 60:
        state['structured_data'] = {
            'error': '数据不足，无法进行结构化分析',
            'watershed_events': [],
            'distribution_cycles': [],
            'stage_candidates': [],
            'recent_bars': []
        }
        return state
    
    structured_result: Dict[str, Any] = {
        'watershed_events': [],
        'distribution_cycles': [],
        'stage_candidates': [],
        'recent_bars': []
    }
    
    # 1. 获取分水岭事件和出货周期（使用高级分析器）
    is_backtest = state.get('run_backtest', False)
    if not is_backtest:
        print(f"[结构化数据] 开始分析分水岭事件和出货周期...")
    try:
        advanced_result = analyze_distribution_advanced(df)
        watershed_events = advanced_result.get('watershed_events', [])
        cycles = advanced_result.get('cycles', [])
        if not is_backtest:
            print(f"[结构化数据] 识别到 {len(watershed_events)} 个分水岭事件, {len(cycles)} 个出货周期")
        
        # 格式化分水岭事件
        for event in watershed_events:
            structured_result['watershed_events'].append({
                'date': event.date.strftime('%Y-%m-%d') if hasattr(event.date, 'strftime') else str(event.date),
                'price': event.price,
                'breakthrough_price': event.breakthrough_price,
                'volume_ratio': event.volume_ratio,
                'is_limit_up': event.is_limit_up,
                'post_max_gain': event.post_days_max_gain,
                'post_max_drop': event.post_days_max_drop
            })
        
        # 格式化出货周期
        for cycle in cycles:
            segments_info = []
            for seg in cycle.segments:
                segments_info.append({
                    'start_date': seg.start_date.strftime('%Y-%m-%d') if hasattr(seg.start_date, 'strftime') else str(seg.start_date),
                    'end_date': seg.end_date.strftime('%Y-%m-%d') if hasattr(seg.end_date, 'strftime') else str(seg.end_date),
                    'high_price': seg.high_price,
                    'low_price': seg.low_price,
                    'avg_price': seg.avg_price,
                    'volume_ratio': seg.volume_ratio,
                    'days': seg.days,
                    'post_drop_pct': seg.post_drop_pct,
                    'watershed_count': len(seg.watershed_events)
                })
            
            structured_result['distribution_cycles'].append({
                'start_date': cycle.start_date.strftime('%Y-%m-%d') if hasattr(cycle.start_date, 'strftime') else str(cycle.start_date),
                'end_date': cycle.end_date.strftime('%Y-%m-%d') if hasattr(cycle.end_date, 'strftime') else str(cycle.end_date),
                'scale': cycle.scale,  # small/medium/large
                'cycle_days': cycle.cycle_days,
                'max_price': cycle.max_price,
                'min_price_in_cycle': cycle.min_price_in_cycle,
                'total_watershed_count': cycle.total_watershed_count,
                'post_cycle_drop_pct': cycle.post_cycle_drop_pct,
                'post_cycle_drop_days': cycle.post_cycle_drop_days,
                'segments': segments_info
            })
    except Exception as e:
        print(f"[结构化数据] 高级分析失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 2. 识别阶段候选区间（O点、恐慌低点、箱体、突破点）
    is_backtest = state.get('run_backtest', False)
    if not is_backtest:
        print(f"[结构化数据] 开始识别阶段候选区间...")
    stage_candidates = []
    
    # 2.1 识别恐慌低点（4/5阶段末尾的急跌）
    try:
        cap = detect_capitulation(df, window=60, vol_ratio=1.5)
        if cap.get('has_capitulation'):
            cap_date = cap.get('cap_date')
            if cap_date:
                cap_date_str = cap_date.strftime('%Y-%m-%d') if hasattr(cap_date, 'strftime') else str(cap_date)
                stage_candidates.append({
                    'type': 'capitulation',
                    'name': '恐慌低点',
                    'date': cap_date_str,
                    'price': cap.get('cap_price'),
                    'description': f'恐慌性放量急跌，可能是4/5阶段末尾，后续可能进入一阶段'
                })
    except Exception as e:
        # 静默处理，不是所有股票都有恐慌低点
        pass
    
    # 2.2 识别底部（一阶段吸筹区间）
    base = None  # 初始化base变量
    try:
        cap_price = cap.get('cap_price') if cap.get('has_capitulation') else None
        if cap_price:
            base = detect_base(df, cap_price, tol=0.15, min_days=30)
            if base and base.get('has_base'):
                base_start = base.get('base_start')
                base_end = base.get('base_end')
                base_start_str = base_start.strftime('%Y-%m-%d') if hasattr(base_start, 'strftime') else str(base_start)
                base_end_str = base_end.strftime('%Y-%m-%d') if hasattr(base_end, 'strftime') else str(base_end)
                stage_candidates.append({
                    'type': 'base',
                    'name': '底部吸筹区间（一阶段候选）',
                    'start_date': base_start_str,
                    'end_date': base_end_str,
                    'low_price': base.get('base_low'),
                    'high_price': base.get('base_high'),
                    'description': f'底部横盘吸筹，可能是一阶段'
                })
    except Exception as e:
        # 静默处理，不是所有股票都有底部
        pass
    
    # 2.3 识别突破点（一阶段到二阶段的转折）
    try:
        if base and base.get('has_base'):
            base_high = base.get('base_high')
            breakout = detect_breakout(df, base_high, look_forward=10, gain_thresh=0.2, vol_ratio=1.3)
            if breakout and breakout.get('has_breakout'):
                breakout_date = breakout.get('breakout_date')
                if breakout_date:
                    breakout_date_str = breakout_date.strftime('%Y-%m-%d') if hasattr(breakout_date, 'strftime') else str(breakout_date)
                    stage_candidates.append({
                        'type': 'breakout',
                        'name': '突破点（一阶段到二阶段转折）',
                        'date': breakout_date_str,
                        'price': breakout.get('breakout_price'),
                        'description': f'突破底部高点，可能进入二阶段快速上涨'
                    })
    except Exception as e:
        print(f"[结构化数据] 识别突破点失败: {e}")
    
    # 2.4 识别箱体（二阶段高位震荡）
    try:
        box = detect_box(df, window=120, max_range_pct=40.0, min_days=20)
        if box.get('has_box'):
            box_start = box.get('box_start')
            box_end = box.get('box_end')
            box_start_str = box_start.strftime('%Y-%m-%d') if hasattr(box_start, 'strftime') else str(box_start)
            box_end_str = box_end.strftime('%Y-%m-%d') if hasattr(box_end, 'strftime') else str(box_end)
            stage_candidates.append({
                'type': 'box',
                'name': '高位箱体（二阶段候选）',
                'start_date': box_start_str,
                'end_date': box_end_str,
                'low_price': box.get('box_low'),
                'high_price': box.get('box_high'),
                'description': f'高位箱体震荡，可能是二阶段高位运行'
            })
    except Exception as e:
        print(f"[结构化数据] 识别箱体失败: {e}")
    
    structured_result['stage_candidates'] = stage_candidates
    
    # 2.5 计算技术指标（用于阶段分析辅助）
    technical_indicators = {}
    try:
        # 计算涨跌幅
        gains = compute_gains(df, (20, 60, 120, 180))
        technical_indicators.update(gains)
        
        # 计算最大回撤
        mdd60 = compute_max_drawdown(df, 60)
        mdd120 = compute_max_drawdown(df, 120)
        mdd180 = compute_max_drawdown(df, 180)
        technical_indicators['max_drawdown_60'] = mdd60
        technical_indicators['max_drawdown_120'] = mdd120
        technical_indicators['max_drawdown_180'] = mdd180
        
        # 计算波动率
        vol20 = compute_volatility(df, 20)
        vol60 = compute_volatility(df, 60)
        technical_indicators['volatility_20'] = vol20
        technical_indicators['volatility_60'] = vol60
        
        # 计算距离高点
        days_from_high, high_gap_pct = compute_days_from_high(df, 180)
        technical_indicators['days_from_high'] = days_from_high
        technical_indicators['high_gap_pct'] = high_gap_pct
        
        # 计算MA
        df_with_ma = calculate_ma(df)
        if len(df_with_ma) > 0:
            current_price = float(df_with_ma.iloc[-1]['收盘'])
            technical_indicators['current_price'] = current_price
            technical_indicators['ma5'] = float(df_with_ma.iloc[-1].get('MA5', current_price)) if 'MA5' in df_with_ma.columns else None
            technical_indicators['ma20'] = float(df_with_ma.iloc[-1].get('MA20', current_price)) if 'MA20' in df_with_ma.columns else None
            technical_indicators['ma60'] = float(df_with_ma.iloc[-1].get('MA60', current_price)) if 'MA60' in df_with_ma.columns else None
        
        # 计算洗盘指标
        washout_indicators = calculate_washout_indicators(df, lookback_days=30)
        technical_indicators['washout'] = washout_indicators
        
        # 识别O点
        o_point_info = find_o_point(df, lookback_days=250)
        if o_point_info:
            technical_indicators['o_point'] = o_point_info
        
    except Exception as e:
        print(f"[结构化数据] 计算技术指标失败: {e}")
        import traceback
        traceback.print_exc()
    
    structured_result['technical_indicators'] = technical_indicators
    
    # 3. 生成最近180-300日的K线简表（用于LLM分析）
    recent_days = min(300, len(df))
    recent_bars = df.tail(recent_days).copy()
    
    recent_bars_list = []
    for _, row in recent_bars.iterrows():
        date_str = row['日期'].strftime('%Y-%m-%d') if hasattr(row['日期'], 'strftime') else str(row['日期'])
        # 数据验证：确保字段存在且有效
        open_price = float(row.get('开盘', 0))
        high_price = float(row.get('最高', 0))
        low_price = float(row.get('最低', 0))
        close_price = float(row.get('收盘', 0))
        change_pct = float(row.get('涨跌幅', 0.0))
        volume = float(row.get('成交量', 0.0)) / 10000.0  # 转换为万手
        
        # 验证数据合理性
        if high_price < low_price:
            print(f"[结构化数据] 警告：日期 {date_str} 数据异常，最高({high_price}) < 最低({low_price})")
        if close_price > high_price or close_price < low_price:
            print(f"[结构化数据] 警告：日期 {date_str} 数据异常，收盘({close_price})不在最高({high_price})和最低({low_price})之间")
        
        recent_bars_list.append({
            'date': date_str,
            'open': open_price,
            'high': high_price,
            'low': low_price,
            'close': close_price,
            'change_pct': change_pct,
            'volume': volume
        })
    
    structured_result['recent_bars'] = recent_bars_list
    structured_result['stock_code'] = state.get('stock_code', '')
    structured_result['stock_name'] = state.get('stock_name', '')
    
    # 4. 识别出货起始信号（高调放量突破前高，连续2-3根放量大阳线）
    distribution_start_signals = []
    try:
        # 扫描最近的数据，寻找连续2-3根放量大阳线突破前高的信号
        if len(df) >= 100:
            # 计算前期均量（用于判断放量）
            vol_avg_baseline = df['成交量'].tail(60).mean()
            
            # 找出显著高点
            significant_highs = find_significant_highs(df, window=20, min_gain_from_low=0.15)
            
            # 扫描最近200天，寻找连续放量大阳线突破前高的信号
            scan_window = min(200, len(df) - 60)
            for i in range(60, len(df) - 2):  # 至少需要3根K线
                # 检查连续2-3根是否都是大阳线+放量+突破前高
                consecutive_big_yang = 0
                max_consecutive = 0
                start_idx = None
                
                for j in range(i, min(i + 5, len(df))):  # 最多检查5根
                    row = df.iloc[j]
                    close = row['收盘']
                    open_price = row['开盘']
                    volume = row['成交量']
                    
                    # 判断是否大阳线（涨幅>5%）
                    body_pct = (close - open_price) / open_price if open_price > 0 else 0
                    is_big_yang = body_pct > 0.05
                    
                    # 判断是否放量（>前期均量1.5倍）
                    vol_ratio = volume / vol_avg_baseline if vol_avg_baseline > 0 else 1.0
                    is_high_volume = vol_ratio >= 1.5
                    
                    # 检查是否突破前高（检查lookback_days内的前高）
                    lookback_days = 250
                    lookback_start = j - lookback_days if j >= lookback_days else 0
                    breakthrough = False
                    for h in significant_highs:
                        matches = df[df['日期'] == h['date']]
                        if matches.empty:
                            continue
                        high_idx = matches.index[0]
                        if lookback_start <= high_idx < j:
                            if close >= h['price'] * 1.01:  # 突破前高1%以上
                                breakthrough = True
                                break
                    
                    if is_big_yang and is_high_volume and breakthrough:
                        if start_idx is None:
                            start_idx = j
                        consecutive_big_yang += 1
                        max_consecutive = max(max_consecutive, consecutive_big_yang)
                    else:
                        # 如果已经有2根以上，就记录这个信号
                        if consecutive_big_yang >= 2:
                            break
                        consecutive_big_yang = 0
                        start_idx = None
                
                # 如果找到连续2-3根放量大阳线突破前高，记录为出货起始信号
                if max_consecutive >= 2 and start_idx is not None:
                    signal_row = df.iloc[start_idx]
                    signal_date = signal_row['日期']
                    signal_date_str = signal_date.strftime('%Y-%m-%d') if hasattr(signal_date, 'strftime') else str(signal_date)
                    
                    # 检查是否已经记录过（避免重复）
                    if not any(s['date'] == signal_date_str for s in distribution_start_signals):
                        distribution_start_signals.append({
                            'date': signal_date_str,
                            'price': float(signal_row['收盘']),
                            'consecutive_days': max_consecutive,
                            'description': f'连续{max_consecutive}根放量大阳线突破前高，出货起始信号'
                        })
                        # 只记录最近的几个信号，避免太多
                        if len(distribution_start_signals) >= 5:
                            break
    except Exception as e:
        print(f"[结构化数据] 识别出货起始信号失败: {e}")
        import traceback
        traceback.print_exc()
    
    structured_result['distribution_start_signals'] = distribution_start_signals
    
    # 更新状态
    state['structured_data'] = structured_result
    
    return state

