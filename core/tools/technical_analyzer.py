"""
技术分析工具
提供各种技术指标计算和形态识别
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, Tuple, List


def compute_gains(df: pd.DataFrame, windows: Tuple[int, ...] = (20, 60, 120, 180)) -> Dict[str, float]:
    """计算多窗口涨跌幅（%）"""
    res = {}
    for w in windows:
        if len(df) >= w + 1:
            start = df.iloc[-(w + 1)]['收盘']
            end = df.iloc[-1]['收盘']
            if start and not pd.isna(start):
                res[f'gain{w}'] = float((end - start) / start * 100)
            else:
                res[f'gain{w}'] = 0.0
        else:
            res[f'gain{w}'] = None
    return res


def compute_max_drawdown(df: pd.DataFrame, window: int = 180) -> float:
    """计算近 window 日最大回撤（%）"""
    if df.empty:
        return None
    recent = df.tail(window) if len(df) > window else df
    highs = recent['收盘'].cummax()
    drawdown = (recent['收盘'] - highs) / highs
    return float(drawdown.min() * 100)


def compute_volatility(df: pd.DataFrame, window: int = 20) -> float:
    """计算近 window 日波动率（收盘收益率标准差，%）"""
    if len(df) < window + 1:
        return None
    recent = df.tail(window + 1)['收盘'].pct_change().dropna()
    return float(recent.std() * 100)


def compute_days_from_high(df: pd.DataFrame, window: int = 180) -> Tuple[int, float]:
    """距离近 window 日高点的天数与当前价/高点比"""
    recent = df.tail(window) if len(df) > window else df
    idx_max = recent['收盘'].idxmax()
    high_price = recent.loc[idx_max, '收盘']
    days_from_high = len(recent) - (recent.index.get_loc(idx_max) + 1)
    current = recent.iloc[-1]['收盘']
    high_gap = float((high_price - current) / high_price * 100) if high_price else 0.0
    return int(days_from_high), high_gap


def detect_capitulation(df: pd.DataFrame, window: int = 40, vol_ratio: float = 1.8) -> Dict[str, Any]:
    """
    识别恐慌性放量长阴/长下影（4/5阶段末尾的急跌）
    返回:
        {
            'has_capitulation': bool,
            'cap_price': float,
            'cap_date': datetime,
            'cap_vol_ratio': float,
            'cap_tail_ratio': float,
        }
    """
    res = {
        'has_capitulation': False,
        'cap_price': None,
        'cap_date': None,
        'cap_vol_ratio': None,
        'cap_tail_ratio': None
    }
    recent = df.tail(window) if len(df) > window else df
    if recent.empty:
        return res

    vol_avg = recent['成交量'].mean()
    if vol_avg is None or vol_avg == 0 or pd.isna(vol_avg):
        vol_avg = np.nan
    # 定义下影线比例：下影长度 / 收盘价
    lower_shadow = (recent['开盘'].combine(recent['收盘'], max) - recent['最低']) / recent['收盘']
    vol_ratio_series = recent['成交量'] / vol_avg

    # 条件：放量且长下影或长阴
    mask = (vol_ratio_series > vol_ratio) & ((lower_shadow > 0.05) | (recent['收盘'] < recent['开盘'] * 0.97))
    if mask.any():
        idx = mask.idxmax()
        row = recent.loc[idx]
        res.update({
            'has_capitulation': True,
            'cap_price': float(row['收盘']),
            'cap_date': row['日期'] if '日期' in recent.columns else idx,
            'cap_vol_ratio': float(vol_ratio_series.loc[idx]),
            'cap_tail_ratio': float(lower_shadow.loc[idx])
        })
    return res


def detect_base(df: pd.DataFrame, cap_price: float, tol: float = 0.15, min_days: int = 60) -> Dict[str, Any]:
    """
    识别恐慌低点附近的长期横盘（一阶段吸筹）
    返回:
        {
            'has_base': bool,
            'base_low': float,
            'base_high': float,
            'base_days': int
        }
    """
    res = {'has_base': False, 'base_low': None, 'base_high': None, 'base_days': 0}
    if cap_price is None or cap_price <= 0:
        return res
    low_band = cap_price * (1 - tol)
    high_band = cap_price * (1 + tol)
    in_band = (df['收盘'] >= low_band) & (df['收盘'] <= high_band)
    # 统计连续在区间内的最长段
    max_run = run = 0
    for v in in_band.values:
        if v:
            run += 1
            max_run = max(max_run, run)
        else:
            run = 0
    if max_run >= min_days:
        res.update({
            'has_base': True,
            'base_low': float(low_band),
            'base_high': float(high_band),
            'base_days': int(max_run)
        })
    return res


def detect_breakout(df: pd.DataFrame, base_high: Optional[float], look_forward: int = 10, gain_thresh: float = 0.3, vol_ratio: float = 1.5) -> Dict[str, Any]:
    """
    识别从底部箱体上沿的快速突破，判定进入二阶段
    返回:
        {
            'has_breakout': bool,
            'breakout_price': float,
            'breakout_return_pct': float,
            'breakout_days': int
        }
    """
    res = {
        'has_breakout': False,
        'breakout_price': None,
        'breakout_return_pct': None,
        'breakout_days': None
    }
    if base_high is None or base_high <= 0 or len(df) < look_forward + 1:
        return res

    recent = df.tail(look_forward + 1).reset_index(drop=True)
    vol_avg = recent['成交量'].mean()
    for i in range(len(recent)):
        price = recent.loc[i, '收盘']
        if price > base_high:
            ret = (price - base_high) / base_high
            vol_r = recent.loc[i, '成交量'] / vol_avg if vol_avg else 0
            if ret >= gain_thresh and vol_r >= vol_ratio:
                res.update({
                    'has_breakout': True,
                    'breakout_price': float(price),
                    'breakout_return_pct': float(ret * 100),
                    'breakout_days': int(i + 1)
                })
                break
    return res


def detect_box(df: pd.DataFrame, window: int = 120, max_range_pct: float = 40.0, min_days: int = 30) -> Dict[str, Any]:
    """
    识别高位箱体震荡（用于判定二阶段后半程）
    返回:
        {
            'has_box': bool,
            'box_low': float,
            'box_high': float,
            'box_range_pct': float,
            'box_days': int
        }
    """
    res = {
        'has_box': False,
        'box_low': None,
        'box_high': None,
        'box_range_pct': None,
        'box_days': 0
    }
    recent = df.tail(window) if len(df) > window else df
    if len(recent) < min_days:
        return res

    low = recent['收盘'].min()
    high = recent['收盘'].max()
    if low <= 0:
        return res
    range_pct = (high - low) / low * 100
    if range_pct <= max_range_pct:
        res.update({
            'has_box': True,
            'box_low': float(low),
            'box_high': float(high),
            'box_range_pct': float(range_pct),
            'box_days': int(len(recent))
        })
    return res


def compute_three_stage_features(df: pd.DataFrame, window: int = 40) -> Dict[str, Any]:
    """
    为三阶段判定提供的形态与量能特征：
    - upper_shadow_ratio: 近 window 日上影线偏长的K线比例
    - mild_pullback_runs: 连续4天以上小跌（-3%<日收益<0）的段数
    - big_bull_count: 高位大阳数量（涨幅>3%且放量）
    - vol_ratio_recent: 近10日均量 / 近60日均量
    - bull_vs_bear: 近20日日线阳线数 / 阴线数
    """
    res: Dict[str, Any] = {
        'upper_shadow_ratio': None,
        'mild_pullback_runs': None,
        'big_bull_count': None,
        'vol_ratio_recent': None,
        'bull_vs_bear': None,
    }

    recent = df.tail(window) if len(df) > window else df.copy()
    if len(recent) < 10:
        return res

    # 上影线比例
    upper_shadow = (recent['最高'] - recent[['开盘', '收盘']].max(axis=1)) / recent['收盘']
    long_upper = upper_shadow > 0.03
    res['upper_shadow_ratio'] = float(long_upper.mean())

    # 小跌段统计：-3% < 日收益 < 0，连续 >=4 天算一段
    ret = recent['收盘'].pct_change().fillna(0.0)
    mild_down = (ret < 0) & (ret > -0.03)
    runs = 0
    count_runs = 0
    for v in mild_down.values:
        if v:
            runs += 1
        else:
            if runs >= 4:
                count_runs += 1
            runs = 0
    if runs >= 4:
        count_runs += 1
    res['mild_pullback_runs'] = int(count_runs)

    # 大阳线数量：涨幅>3%，且放量>1.5倍近20日均量
    body = (recent['收盘'] - recent['开盘']) / recent['开盘']
    vol20 = recent['成交量'].tail(20).mean()
    if vol20 and not pd.isna(vol20):
        big_bull = (body > 0.03) & (recent['成交量'] > vol20 * 1.5)
        res['big_bull_count'] = int(big_bull.sum())
    else:
        res['big_bull_count'] = 0

    # 量能比：近10日均量 / 近60日均量
    vol10 = recent['成交量'].tail(10).mean()
    vol60_series = df['成交量'].tail(60)
    vol60 = vol60_series.mean() if not vol60_series.empty else None
    if vol10 and vol60 and not (pd.isna(vol10) or pd.isna(vol60)) and vol60 > 0:
        res['vol_ratio_recent'] = float(vol10 / vol60)

    # 阳线 / 阴线 比例（近20日）
    sub = recent.tail(20)
    bulls = (sub['收盘'] > sub['开盘']).sum()
    bears = (sub['收盘'] < sub['开盘']).sum()
    if bears > 0:
        res['bull_vs_bear'] = float(bulls / bears)
    elif bulls > 0:
        res['bull_vs_bear'] = float('inf')
    else:
        res['bull_vs_bear'] = None

    return res


def detect_watershed_top(df: pd.DataFrame, indicators: Dict[str, Any]) -> Dict[str, Any]:
    """
    高位分水岭风险形态检测：
    - 前提：已处于高位（涨幅大，距离高点不远，并存在高位箱体）
    - 特征：高位箱体附近出现两次以上大阳/涨停放量突破尝试
    """
    res = {
        "has_watershed_top": False,
        "watershed_strength": 0.0,
        "watershed_date": None,
        "watershed_price": None,
        "description": "",
    }
    if len(df) < 40:
        return res
    # 分水岭作为一个“形态标签”，不再强制依赖涨幅/阶段，只看最近一段是否出现
    # “多次高位放量突破前高的大阳/涨停”，这样一阶段末尾的换赛道出货也能被识别出来。
    events = indicators.get("events", {}) or {}
    has_box = events.get("has_box", False)

    # 扫描最近 80 根K线，覆盖一阶段末尾 / 二阶段中后段 / 三阶段末端的典型分水岭形态
    recent = df.tail(80).reset_index(drop=True)

    # 取前一段的前高（排除最后几天）
    pre_segment = recent.iloc[:-5] if len(recent) > 5 else recent
    prev_high = pre_segment['收盘'].max()

    # 大阳 + 放量定义
    body = (recent['收盘'] - recent['开盘']) / recent['开盘']
    vol = recent['成交量']
    vol_avg20 = vol.tail(20).mean()
    # 分水岭出货往往明显放量，这里以近20日均量的 1.5 倍作为门槛，稍微放宽
    vol_thresh = vol_avg20 * 1.5 if vol_avg20 and not pd.isna(vol_avg20) else None

    big_bull_mask = body > 0.05  # 涨幅 > 5%
    if vol_thresh:
        big_bull_mask &= (vol > vol_thresh)

    high_bulls_idx = [
        i for i, is_bull in enumerate(big_bull_mask)
        if is_bull and recent.loc[i, '收盘'] >= prev_high * 0.97
    ]

    if len(high_bulls_idx) >= 2:
        last_idx = high_bulls_idx[-1]
        res["has_watershed_top"] = True
        # 若本身处于箱体高位，则强度更高
        base_strength = len(high_bulls_idx) / 3.0
        if has_box:
            base_strength += 0.2
        res["watershed_strength"] = float(min(1.0, base_strength))
        res["watershed_date"] = recent.loc[last_idx, '日期'] if '日期' in recent.columns else None
        res["watershed_price"] = float(recent.loc[last_idx, '收盘'])
        res["description"] = (
            "高位箱体附近出现多次大阳/涨停放量突破前高，"
            "说明散户在高位集中涌入，主力疑似边拉边出货，"
            "存在分水岭式顶部风险，建议分批减仓或清仓。"
        )

    return res


def calculate_ma(data: pd.DataFrame, periods: list = [5, 10, 20, 60]) -> pd.DataFrame:
    """计算移动平均线"""
    df = data.copy()
    for period in periods:
        df[f'MA{period}'] = df['收盘'].rolling(window=period).mean()
    return df


def calculate_macd(data: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    """计算MACD指标"""
    df = data.copy()
    exp1 = df['收盘'].ewm(span=fast, adjust=False).mean()
    exp2 = df['收盘'].ewm(span=slow, adjust=False).mean()
    df['MACD'] = exp1 - exp2
    df['MACD_Signal'] = df['MACD'].ewm(span=signal, adjust=False).mean()
    df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']
    return df


def calculate_rsi(data: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    """计算RSI指标"""
    df = data.copy()
    delta = df['收盘'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    return df


def find_o_point(data: pd.DataFrame, lookback_days: int = 250) -> Optional[Dict[str, Any]]:
    """
    识别O点（原始低点）
    
    Args:
        data: 股票数据
        lookback_days: 向前查找的天数
    
    Returns:
        O点信息：价格、日期、相对涨幅
    """
    if len(data) < 60:
        return None
    
    # 查找最近lookback_days天内的最低点
    recent_data = data.tail(lookback_days) if len(data) > lookback_days else data
    min_idx = recent_data['最低'].idxmin()
    o_point_price = recent_data.loc[min_idx, '最低']
    o_point_date = recent_data.loc[min_idx, '日期']
    
    # 计算当前相对O点的涨幅
    current_price = data.iloc[-1]['收盘']
    relative_gain = ((current_price - o_point_price) / o_point_price) * 100
    
    return {
        'o_point_price': float(o_point_price),
        'o_point_date': o_point_date.strftime('%Y-%m-%d') if hasattr(o_point_date, 'strftime') else str(o_point_date),
        'current_price': float(current_price),
        'relative_gain': float(relative_gain),
        'days_from_o': len(data) - min_idx
    }


def identify_stage_indicators(data: pd.DataFrame) -> Dict[str, Any]:
    """
    识别阶段的技术指标
    
    Returns:
        包含各种阶段判断指标
    """
    if len(data) < 60:
        return {}
    
    df = calculate_ma(data)
    df = calculate_macd(df)
    df = calculate_rsi(df)
    
    current_price = df.iloc[-1]['收盘']
    ma5 = df.iloc[-1].get('MA5', current_price)
    ma10 = df.iloc[-1].get('MA10', current_price)
    ma20 = df.iloc[-1].get('MA20', current_price)
    ma60 = df.iloc[-1].get('MA60', current_price)
    
    # 计算趋势方向
    price_above_ma20 = current_price > ma20
    price_above_ma60 = current_price > ma60
    ma5_above_ma20 = ma5 > ma20
    ma10_above_ma20 = ma10 > ma20
    
    # 计算涨跌幅
    recent_gain = ((current_price - df.iloc[-20]['收盘']) / df.iloc[-20]['收盘']) * 100 if len(df) >= 20 else 0
    
    # MACD状态
    macd_positive = df.iloc[-1].get('MACD', 0) > 0
    macd_hist_positive = df.iloc[-1].get('MACD_Hist', 0) > 0
    
    # RSI状态
    rsi = df.iloc[-1].get('RSI', 50)
    
    return {
        'price_above_ma20': bool(price_above_ma20),
        'price_above_ma60': bool(price_above_ma60),
        'ma5_above_ma20': bool(ma5_above_ma20),
        'ma10_above_ma20': bool(ma10_above_ma20),
        'recent_gain_20d': float(recent_gain),
        'macd_positive': bool(macd_positive),
        'macd_hist_positive': bool(macd_hist_positive),
        'rsi': float(rsi),
        'current_price': float(current_price),
        'ma5': float(ma5),
        'ma10': float(ma10),
        'ma20': float(ma20),
        'ma60': float(ma60) if not pd.isna(ma60) else None
    }


def calculate_washout_indicators(data: pd.DataFrame, lookback_days: int = 30) -> Dict[str, Any]:
    """
    计算洗盘相关指标
    
    Args:
        data: 股票数据
        lookback_days: 回看天数
    
    Returns:
        洗盘指标
    """
    if len(data) < lookback_days:
        return {}
    
    recent_data = data.tail(lookback_days)
    
    # 计算波动率（恐惧程度）
    volatility = recent_data['涨跌幅'].std()
    
    # 计算下跌天数（焦虑程度）
    down_days = (recent_data['涨跌幅'] < 0).sum()
    down_ratio = down_days / len(recent_data)
    
    # 计算成交量变化
    avg_volume = recent_data['成交量'].mean()
    recent_volume = recent_data.tail(5)['成交量'].mean()
    volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 1
    
    # 计算最大回撤
    high_price = recent_data['最高'].max()
    low_price = recent_data['最低'].min()
    max_drawdown = ((high_price - low_price) / high_price) * 100
    
    return {
        'volatility': float(volatility),
        'down_days': int(down_days),
        'down_ratio': float(down_ratio),
        'volume_ratio': float(volume_ratio),
        'max_drawdown': float(max_drawdown),
        'recent_high': float(high_price),
        'recent_low': float(low_price)
    }


def detect_panic_points(df: pd.DataFrame, window: int = 60, vol_ratio: float = 1.5) -> List[Dict[str, Any]]:
    """
    识别恐慌点（买入信号）
    
    核心原则：持仓的跌了怕继续跌，外面的不敢进
    
    恐慌点特征：
    1. 5阶段长期阴跌后，突然急剧下跌且放量
    2. 一阶段O点之前的急剧下跌，反弹一小段后又往下跌，出现小短期放量
    3. 1/2阶段，具有上涨趋势，前面有明显洗盘、长时间横盘，突然出现1-2根大大的放巨量的阴线
    4. 小碎步上涨过程中突然的大跌放量阴线
    5. **连续下跌，跟随的大阴线跌破前低点、重要均线，导致恐慌盘放量，散户被洗出去**
       - 这是最重要的恐慌点类型：持仓的跌了怕继续跌，外面的不敢进
       - 特征：前面有连续下跌（至少3-5天），大阴线跌破前低或重要均线（如20日、30日、60日均线）
       - 放量下跌，但后续继续下跌或横盘，让外面的人不敢进
    
    返回:
        List[Dict]: 恐慌点列表，每个包含：
        {
            'date': datetime,
            'price': float,
            'type': str,  # 'stage5_panic', 'stage1_panic', 'washout_panic', 'uptrend_panic', 'breakdown_panic'
            'vol_ratio': float,
            'drop_pct': float,
            'description': str
        }
    """
    if len(df) < window:
        return []
    
    panic_points = []
    recent = df.tail(window).reset_index(drop=True)
    
    # 计算均量
    vol_avg = recent['成交量'].mean()
    if vol_avg is None or vol_avg == 0 or pd.isna(vol_avg):
        return []
    
    # 计算涨跌幅
    recent['change_pct'] = recent['收盘'].pct_change() * 100
    
    for i in range(1, len(recent)):
        row = recent.iloc[i]
        prev_row = recent.iloc[i-1]
        
        # 基本条件：放量
        vol_ratio_current = row['成交量'] / vol_avg if vol_avg > 0 else 1.0
        if vol_ratio_current < vol_ratio:
            continue
        
        # 判断是否阴线
        is_bearish = row['收盘'] < row['开盘']
        # 判断是否大跌
        drop_pct = (row['收盘'] - prev_row['收盘']) / prev_row['收盘'] * 100 if prev_row['收盘'] > 0 else 0
        
        # 排除涨停后的调整：如果前一天是涨停，且今天跌幅不大（<5%），不算恐慌点
        # 涨停后的正常调整不应该被视为恐慌点
        if i >= 1:
            prev_open = prev_row['开盘']
            prev_close = prev_row['收盘']
            prev_body_pct = (prev_close - prev_open) / prev_open if prev_open > 0 else 0
            prev_is_limit_up = prev_body_pct > 0.095  # 前一天是涨停
            
            if prev_is_limit_up:
                # 涨停后1-3天的调整，如果跌幅<5%，不算恐慌点（这是正常的技术性调整）
                if drop_pct > -5.0:
                    continue
                # 即使跌幅>=5%，也要检查是否是连续涨停后的调整（不算恐慌点）
                if i >= 2:
                    prev_2_row = recent.iloc[i-2]
                    prev_2_open = prev_2_row['开盘']
                    prev_2_close = prev_2_row['收盘']
                    prev_2_body_pct = (prev_2_close - prev_2_open) / prev_2_open if prev_2_open > 0 else 0
                    # 如果前两天也是涨停，说明是连续涨停后的调整，不算恐慌点
                    if prev_2_body_pct > 0.095:
                        continue
        
        # 1. 5阶段长期阴跌后的急剧下跌（跌幅>3%，放量）
        if drop_pct < -3.0 and vol_ratio_current >= vol_ratio:
            # 检查前面是否长期阴跌（近20日整体下跌）
            if i >= 20:
                prev_20 = recent.iloc[i-20:i]
                prev_20_change = (prev_20.iloc[-1]['收盘'] - prev_20.iloc[0]['收盘']) / prev_20.iloc[0]['收盘'] * 100
                if prev_20_change < -10:  # 前面20日累计跌幅>10%
                    panic_points.append({
                        'date': row['日期'] if '日期' in row else None,
                        'price': float(row['收盘']),
                        'type': 'stage5_panic',
                        'vol_ratio': float(vol_ratio_current),
                        'drop_pct': float(drop_pct),
                        'description': f'5阶段长期阴跌后的急剧下跌，跌幅{drop_pct:.2f}%，放量{vol_ratio_current:.2f}倍'
                    })
        
        # 2. 一阶段O点之前的急剧下跌（跌幅>3%，反弹后又下跌）
        # 提高阈值到-3%，避免将涨停后的小幅调整误判为恐慌点
        if drop_pct < -3.0 and vol_ratio_current >= vol_ratio:
            # 检查前面是否有反弹
            if i >= 5:
                prev_5 = recent.iloc[i-5:i]
                prev_5_max = prev_5['收盘'].max()
                prev_5_min = prev_5['收盘'].min()
                # 前面有反弹（涨幅>5%），且不是涨停后的调整
                if prev_5_max > prev_5_min * 1.05:  # 前面有反弹（涨幅>5%）
                    # 进一步检查：如果前一天是涨停，且跌幅<5%，不算恐慌点
                    prev_open = prev_row['开盘']
                    prev_close = prev_row['收盘']
                    prev_body_pct = (prev_close - prev_open) / prev_open if prev_open > 0 else 0
                    prev_is_limit_up = prev_body_pct > 0.095
                    
                    # 如果是涨停后的调整，且跌幅不大，不算恐慌点
                    if prev_is_limit_up and drop_pct > -5.0:
                        continue
                    
                    panic_points.append({
                        'date': row['日期'] if '日期' in row else None,
                        'price': float(row['收盘']),
                        'type': 'stage1_panic',
                        'vol_ratio': float(vol_ratio_current),
                        'drop_pct': float(drop_pct),
                        'description': f'一阶段O点前的急剧下跌，反弹后又下跌，跌幅{drop_pct:.2f}%，放量{vol_ratio_current:.2f}倍'
                    })
        
        # 3. 1/2阶段上涨趋势中，洗盘横盘后的放量阴线
        if is_bearish and vol_ratio_current >= vol_ratio * 1.5:  # 放巨量
            # 检查前面是否有横盘（波动小）
            if i >= 10:
                prev_10 = recent.iloc[i-10:i]
                prev_10_volatility = prev_10['收盘'].std() / prev_10['收盘'].mean() if prev_10['收盘'].mean() > 0 else 0
                # 检查整体趋势（近30日）
                if i >= 30:
                    prev_30 = recent.iloc[i-30:i]
                    prev_30_change = (prev_30.iloc[-1]['收盘'] - prev_30.iloc[0]['收盘']) / prev_30.iloc[0]['收盘'] * 100
                    # 前面有上涨趋势（涨幅>5%）且横盘（波动率<3%）
                    if prev_30_change > 5 and prev_10_volatility < 0.03:
                        panic_points.append({
                            'date': row['日期'] if '日期' in row else None,
                            'price': float(row['收盘']),
                            'type': 'washout_panic',
                            'vol_ratio': float(vol_ratio_current),
                            'drop_pct': float(drop_pct),
                            'description': f'1/2阶段洗盘横盘后的放量阴线，跌幅{drop_pct:.2f}%，放量{vol_ratio_current:.2f}倍'
                        })
        
        # 4. 小碎步上涨过程中的大跌放量阴线
        # 提高阈值到-3%，避免将涨停后的小幅调整误判为恐慌点
        if drop_pct < -3.0 and vol_ratio_current >= vol_ratio:
            # 检查前面是否小碎步上涨（近10日累计涨幅>3%但单日涨幅都不大）
            if i >= 10:
                prev_10 = recent.iloc[i-10:i]
                prev_10_change = (prev_10.iloc[-1]['收盘'] - prev_10.iloc[0]['收盘']) / prev_10.iloc[0]['收盘'] * 100
                prev_10_max_single = prev_10['change_pct'].max()
                # 累计涨幅>3%，但单日最大涨幅<3%（小碎步）
                # 注意：如果前一天是涨停，说明不是小碎步上涨，应该排除
                prev_open = prev_row['开盘']
                prev_close = prev_row['收盘']
                prev_body_pct = (prev_close - prev_open) / prev_open if prev_open > 0 else 0
                prev_is_limit_up = prev_body_pct > 0.095
                
                # 如果前一天是涨停，不算小碎步上涨，排除
                if prev_is_limit_up:
                    continue
                
                if prev_10_change > 3 and prev_10_max_single < 3:
                    panic_points.append({
                        'date': row['日期'] if '日期' in row else None,
                        'price': float(row['收盘']),
                        'type': 'uptrend_panic',
                        'vol_ratio': float(vol_ratio_current),
                        'drop_pct': float(drop_pct),
                        'description': f'小碎步上涨过程中的大跌放量阴线，跌幅{drop_pct:.2f}%，放量{vol_ratio_current:.2f}倍'
                    })
        
        # 5. 连续下跌，跟随的大阴线跌破前低点、重要均线，导致恐慌盘放量（最重要的恐慌点类型）
        # 核心：持仓的跌了怕继续跌，外面的不敢进
        if drop_pct < -4.0 and vol_ratio_current >= vol_ratio and is_bearish:
            # 检查前面是否有连续下跌（至少3-5天）
            if i >= 5:
                # 计算连续下跌天数
                consecutive_down_days = 0
                for j in range(i-1, max(0, i-5), -1):
                    if j > 0:
                        check_row = recent.iloc[j]
                        check_prev = recent.iloc[j-1]
                        check_drop = (check_row['收盘'] - check_prev['收盘']) / check_prev['收盘'] * 100 if check_prev['收盘'] > 0 else 0
                        if check_drop < 0:
                            consecutive_down_days += 1
                        else:
                            break
                
                # 至少连续3天下跌
                if consecutive_down_days >= 3:
                    # 计算重要均线（20日、30日、60日）
                    ma20 = None
                    ma30 = None
                    ma60 = None
                    if i >= 20:
                        ma20 = recent.iloc[max(0, i-20):i]['收盘'].mean()
                    if i >= 30:
                        ma30 = recent.iloc[max(0, i-30):i]['收盘'].mean()
                    if i >= 60:
                        ma60 = recent.iloc[max(0, i-60):i]['收盘'].mean()
                    
                    # 查找前低点（最近60天内的最低点）
                    lookback_days = min(60, i)
                    prev_lows = recent.iloc[max(0, i-lookback_days):i]['最低']
                    if len(prev_lows) > 0:
                        prev_low = prev_lows.min()
                        current_close = row['收盘']
                        
                        # 检查是否跌破前低或重要均线
                        broke_prev_low = current_close < prev_low * 0.98  # 收盘价跌破前低2%以上
                        broke_ma20 = ma20 is not None and current_close < ma20 * 0.98
                        broke_ma30 = ma30 is not None and current_close < ma30 * 0.98
                        broke_ma60 = ma60 is not None and current_close < ma60 * 0.98
                        
                        # 检查后续走势：是否继续下跌或横盘（让外面的人不敢进）
                        # 如果后续3-5天继续下跌或横盘，说明外面的人不敢进
                        future_continues_down = False
                        if i < len(recent) - 3:
                            future_3 = recent.iloc[i+1:min(len(recent), i+4)]
                            if len(future_3) > 0:
                                future_max = future_3['收盘'].max()
                                # 后续3天内最高价不超过当前收盘价的3%，说明继续下跌或横盘
                                if future_max < current_close * 1.03:
                                    future_continues_down = True
                        
                        # 如果跌破前低或重要均线，且后续继续下跌/横盘，符合"持仓的跌了怕继续跌，外面的不敢进"
                        if (broke_prev_low or broke_ma20 or broke_ma30 or broke_ma60) and future_continues_down:
                            # 排除涨停后的调整
                            prev_open = prev_row['开盘']
                            prev_close = prev_row['收盘']
                            prev_body_pct = (prev_close - prev_open) / prev_open if prev_open > 0 else 0
                            prev_is_limit_up = prev_body_pct > 0.095
                            
                            if not prev_is_limit_up:  # 不是涨停后的调整
                                breakdown_desc = []
                                if broke_prev_low:
                                    breakdown_desc.append(f"跌破前低({prev_low:.2f})")
                                if broke_ma20:
                                    breakdown_desc.append("跌破20日均线")
                                if broke_ma30:
                                    breakdown_desc.append("跌破30日均线")
                                if broke_ma60:
                                    breakdown_desc.append("跌破60日均线")
                                
                                panic_points.append({
                                    'date': row['日期'] if '日期' in row else None,
                                    'price': float(row['收盘']),
                                    'type': 'breakdown_panic',
                                    'vol_ratio': float(vol_ratio_current),
                                    'drop_pct': float(drop_pct),
                                    'description': f'连续下跌后大阴线跌破{",".join(breakdown_desc)}，恐慌盘放量，跌幅{drop_pct:.2f}%，放量{vol_ratio_current:.2f}倍（持仓的跌了怕继续跌，外面的不敢进）'
                                })
    
    return panic_points


def detect_sell_signals(df: pd.DataFrame, window: int = 60, stage: int = 0) -> List[Dict[str, Any]]:
    """
    识别卖点信号（适用于一二阶段，手里有底仓的情况）
    
    卖点信号类型：
    1. 大阳线放量，形态特别好看（一二阶段）
    2. 放量突破前高，形态特别好看
    3. 涨停第二天还是大阳线
    4. 多方锚定形态 + 放量大涨
    
    返回:
        List[Dict]: 卖点信号列表，每个包含：
        {
            'date': datetime,
            'price': float,
            'type': str,  # 'beautiful_big_yang', 'breakthrough_high', 'limit_up_next_day', 'bullish_anchor'
            'vol_ratio': float,
            'gain_pct': float,
            'description': str
        }
    """
    if len(df) < window:
        return []
    
    sell_signals = []
    recent = df.tail(window).reset_index(drop=True)
    
    # 计算均量
    vol_avg = recent['成交量'].mean()
    if vol_avg is None or vol_avg == 0 or pd.isna(vol_avg):
        return []
    
    # 只在一二阶段检测卖点
    if stage not in [1, 2]:
        return []
    
    for i in range(1, len(recent)):
        row = recent.iloc[i]
        prev_row = recent.iloc[i-1]
        
        date = row['日期'] if '日期' in row else None
        open_price = row['开盘']
        close = row['收盘']
        high = row['最高']
        low = row['最低']
        volume = row['成交量']
        
        # 计算涨跌幅和放量倍数
        body_pct = (close - open_price) / open_price if open_price > 0 else 0
        gain_pct = (close - prev_row['收盘']) / prev_row['收盘'] * 100 if prev_row['收盘'] > 0 else 0
        vol_ratio = volume / vol_avg if vol_avg > 0 else 1.0
        
        # 判断是否大阳线（涨幅>5%）- 必须是收盘价>开盘价
        is_big_yang = body_pct > 0.05 and close > open_price
        # 判断是否大阴线（跌幅>5%）
        is_big_yin = body_pct < -0.05 and close < open_price
        # 判断是否涨停
        is_limit_up = body_pct > 0.095 and close > open_price
        
        # 如果是大阴线，直接跳过（卖点信号只针对大阳线）
        if is_big_yin:
            continue
        
        # 额外验证：如果收盘价 <= 开盘价，绝对不是阳线，直接跳过
        if close <= open_price:
            continue
        
        # 1. 大阳线放量，形态特别好看（一二阶段）
        # 特征：大阳线（涨幅>5%），放量（>1.5倍），上影线短（形态好看），下影线短或没有
        if is_big_yang and vol_ratio >= 1.5:
            upper_shadow = (high - max(open_price, close)) / close if close > 0 else 0
            lower_shadow = (min(open_price, close) - low) / close if close > 0 else 0
            # 形态好看：上影线短（<2%），下影线短（<1%）
            if upper_shadow < 0.02 and lower_shadow < 0.01:
                # 再次验证：确保是阳线
                if close > open_price:
                    sell_signals.append({
                        'date': date,
                        'price': float(close),
                        'type': 'beautiful_big_yang',
                        'vol_ratio': float(vol_ratio),
                        'gain_pct': float(gain_pct),
                        'body_pct': float(body_pct * 100),  # 添加body_pct用于调试
                        'open': float(open_price),  # 添加开盘价用于调试
                        'close': float(close),  # 添加收盘价用于调试
                        'description': f'大阳线放量，形态特别好看，当日涨幅{body_pct*100:.2f}%（收盘{close:.2f}>开盘{open_price:.2f}），相对前日涨幅{gain_pct:.2f}%，放量{vol_ratio:.2f}倍'
                    })
        
        # 2. 放量突破前高，形态特别好看
        # 检查是否突破前高（近60日内的前高）
        # 注意：必须是阳线（收盘价>开盘价）才能算突破
        if i >= 20 and close > open_price and is_big_yang:
            prev_60 = recent.iloc[max(0, i-60):i]
            prev_high = prev_60['最高'].max()
            
            if close >= prev_high * 1.01 and vol_ratio >= 1.5:
                upper_shadow = (high - max(open_price, close)) / close if close > 0 else 0
                lower_shadow = (min(open_price, close) - low) / close if close > 0 else 0
                # 形态好看：上影线短（<2%），下影线短（<1%）
                if upper_shadow < 0.02 and lower_shadow < 0.01:
                    # 再次验证：确保是阳线
                    if close > open_price:
                        sell_signals.append({
                            'date': date,
                            'price': float(close),
                            'type': 'breakthrough_high',
                            'vol_ratio': float(vol_ratio),
                            'gain_pct': float(gain_pct),
                            'body_pct': float(body_pct * 100),  # 添加body_pct用于调试
                            'open': float(open_price),  # 添加开盘价用于调试
                            'close': float(close),  # 添加收盘价用于调试
                            'description': f'放量突破前高，形态特别好看，当日涨幅{body_pct*100:.2f}%（收盘{close:.2f}>开盘{open_price:.2f}），相对前日涨幅{gain_pct:.2f}%，放量{vol_ratio:.2f}倍'
                        })
        
        # 3. 涨停第二天还是大阳线
        # 检查前一天是否涨停
        if i >= 1:
            prev_day = recent.iloc[i-1]
            prev_open = prev_day['开盘']
            prev_close = prev_day['收盘']
            prev_body_pct = (prev_close - prev_open) / prev_open if prev_open > 0 else 0
            prev_is_limit_up = prev_body_pct > 0.095
            
            if prev_is_limit_up:
                # 今天是大阳线（涨幅>5%）且必须是阳线
                if is_big_yang and close > open_price:
                    # 涨停第二天还是大阳线，主力可能在出货
                    sell_signals.append({
                        'date': date,
                        'price': float(close),
                        'type': 'limit_up_next_day',
                        'vol_ratio': float(vol_ratio),
                        'gain_pct': float(gain_pct),
                        'body_pct': float(body_pct * 100),  # 添加body_pct用于调试
                        'open': float(open_price),  # 添加开盘价用于调试
                        'close': float(close),  # 添加收盘价用于调试
                        'description': f'涨停第二天还是大阳线，当日涨幅{body_pct*100:.2f}%（收盘{close:.2f}>开盘{open_price:.2f}），相对前日涨幅{gain_pct:.2f}%，放量{vol_ratio:.2f}倍，主力可能出货'
                    })
                # 注意：如果第二天是涨停（散户买不到）或大阴线（散户不敢买），不算卖点
    
    return sell_signals


def detect_bullish_anchor_pattern(df: pd.DataFrame, window: int = 120) -> List[Dict[str, Any]]:
    """
    检测多方锚定形态
    
    多方锚定特征：
    - 形态上和前面近期几个月（3-6个月）的形态很相似
    - 有重复再次上涨的感觉
    - 这是主力操控形态，形成多方锚定
    - 当识别到这种形态，且出现放量的大涨时，考虑大幅度减仓或离场
    
    返回:
        List[Dict]: 多方锚定信号列表
    """
    if len(df) < window:
        return []
    
    anchor_signals = []
    recent = df.tail(window).reset_index(drop=True)
    
    # 计算均量
    vol_avg = recent['成交量'].mean()
    if vol_avg is None or vol_avg == 0 or pd.isna(vol_avg):
        return []
    
    # 需要至少60天的数据来比较形态
    if len(recent) < 60:
        return []
    
    # 将数据分成两段：前半段（3-6个月前）和后半段（最近）
    mid_point = len(recent) // 2
    first_half = recent.iloc[:mid_point]
    second_half = recent.iloc[mid_point:]
    
    # 计算两段的特征（简化版：使用涨跌幅、波动率、成交量等）
    first_half_change = (first_half.iloc[-1]['收盘'] - first_half.iloc[0]['收盘']) / first_half.iloc[0]['收盘'] * 100 if len(first_half) > 0 and first_half.iloc[0]['收盘'] > 0 else 0
    second_half_change = (second_half.iloc[-1]['收盘'] - second_half.iloc[0]['收盘']) / second_half.iloc[0]['收盘'] * 100 if len(second_half) > 0 and second_half.iloc[0]['收盘'] > 0 else 0
    
    first_half_volatility = first_half['收盘'].std() / first_half['收盘'].mean() if first_half['收盘'].mean() > 0 else 0
    second_half_volatility = second_half['收盘'].std() / second_half['收盘'].mean() if second_half['收盘'].mean() > 0 else 0
    
    # 判断形态相似度（简化版：涨跌幅方向相同，波动率相近）
    similar_pattern = (
        (first_half_change > 0 and second_half_change > 0) or  # 都是上涨
        (first_half_change < 0 and second_half_change < 0)    # 都是下跌
    ) and abs(first_half_volatility - second_half_volatility) < 0.05  # 波动率相近
    
    if similar_pattern:
        # 检查最近是否有放量大涨
        for i in range(len(second_half) - 5, len(second_half)):
            if i < 1:
                continue
            row = second_half.iloc[i]
            prev_row = second_half.iloc[i-1] if i > 0 else recent.iloc[mid_point + i - 1]
            
            open_price = row['开盘']
            close = row['收盘']
            volume = row['成交量']
            
            body_pct = (close - open_price) / open_price if open_price > 0 else 0
            gain_pct = (close - prev_row['收盘']) / prev_row['收盘'] * 100 if prev_row['收盘'] > 0 else 0
            vol_ratio = volume / vol_avg if vol_avg > 0 else 1.0
            
            # 放量大涨：涨幅>5%，放量>1.5倍
            if body_pct > 0.05 and vol_ratio >= 1.5:
                anchor_signals.append({
                    'date': row['日期'] if '日期' in row else None,
                    'price': float(close),
                    'type': 'bullish_anchor',
                    'vol_ratio': float(vol_ratio),
                    'gain_pct': float(gain_pct),
                    'description': f'多方锚定形态，放量大涨，涨幅{gain_pct:.2f}%，放量{vol_ratio:.2f}倍，考虑大幅度减仓或离场'
                })
                break  # 只记录最近的一个
    
    return anchor_signals


