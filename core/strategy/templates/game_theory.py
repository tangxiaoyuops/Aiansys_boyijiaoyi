"""
博弈分析策略
基于恐慌点和好看点的期货交易策略
"""
from typing import Dict, Any, Optional, TYPE_CHECKING
import pandas as pd
import numpy as np

from ..base import Strategy
from core.tools.technical_analyzer import (
    detect_panic_points,
    detect_sell_signals,
    detect_bullish_anchor_pattern
)
from core.tools.futures_analyzer import (
    compute_futures_technical_indicators,
    calculate_rsi_futures,
    analyze_open_interest_trend
)

if TYPE_CHECKING:
    from ...backtest.portfolio import Portfolio


class GameTheoryStrategy(Strategy):
    """博弈分析策略"""
    
    def __init__(self):
        super().__init__("博弈分析策略")
        # 默认参数
        self.panic_drop_threshold = -3.0  # 恐慌点跌幅阈值（%）
        self.panic_vol_ratio = 1.5  # 恐慌点放量倍数
        self.sell_gain_threshold = 5.0  # 好看点涨幅阈值（%）
        self.sell_vol_ratio = 1.5  # 好看点放量倍数
        self.position_size = 100  # 每次开仓股数（股票交易中1手=100股，这里直接使用股数）
        self.stage_window = 60  # 阶段判断窗口（天）
        self.enable_short = False  # 是否允许开空
        self.panic_window = 60  # 恐慌点检测窗口
        self.sell_window = 60  # 好看点检测窗口
        self.big_yang_filter_ratio = 1.2  # 恐慌点过滤大阳线的比例（如果前N天有大阳线，恐慌点阴线长度必须>大阳线长度*此比例）
        self.big_yang_filter_days = 10  # 恐慌点过滤大阳线的天数（检查前N天是否有大阳线）
        self.position_capital_ratio = 0.0  # 每笔操作使用资金的比例（0表示使用固定股数，>0表示按资金比例计算）
    
    def _on_initialize(self):
        """初始化参数"""
        # 获取参数（支持从self.parameters或默认值）
        self.panic_drop_threshold = self.get_parameter('panic_drop_threshold', -3.0)
        self.panic_vol_ratio = self.get_parameter('panic_vol_ratio', 1.5)
        self.sell_gain_threshold = self.get_parameter('sell_gain_threshold', 5.0)
        self.sell_vol_ratio = self.get_parameter('sell_vol_ratio', 1.5)
        # position_size参数：如果传入的是手数，需要转换为股数（乘以100）
        # 如果传入的值小于10，认为是手数，自动转换为股数；否则认为是股数
        position_size_param = self.get_parameter('position_size', 100)
        if position_size_param < 10:
            # 小于10，认为是手数，转换为股数
            self.position_size = position_size_param * 100
            print(f"[博弈策略] position_size参数{position_size_param}手已转换为{self.position_size}股")
        else:
            # 大于等于10，认为是股数
            self.position_size = position_size_param
        self.stage_window = self.get_parameter('stage_window', 60)
        self.enable_short = self.get_parameter('enable_short', False)
        self.panic_window = self.get_parameter('panic_window', 60)
        self.sell_window = self.get_parameter('sell_window', 60)
        self.big_yang_filter_ratio = self.get_parameter('big_yang_filter_ratio', 1.2)
        self.big_yang_filter_days = self.get_parameter('big_yang_filter_days', 10)
        self.position_capital_ratio = self.get_parameter('position_capital_ratio', 0.0)
        
        # 打印参数以便调试
        print(f"[博弈策略] 参数初始化完成:")
        print(f"  - panic_drop_threshold: {self.panic_drop_threshold}")
        print(f"  - panic_vol_ratio: {self.panic_vol_ratio}")
        print(f"  - sell_gain_threshold: {self.sell_gain_threshold}")
        print(f"  - sell_vol_ratio: {self.sell_vol_ratio}")
        print(f"  - position_size: {self.position_size}")
        print(f"  - stage_window: {self.stage_window}")
        print(f"  - panic_window: {self.panic_window}")
        print(f"  - sell_window: {self.sell_window}")
        print(f"  - enable_short: {self.enable_short}")
        print(f"  - big_yang_filter_ratio: {self.big_yang_filter_ratio}")
        print(f"  - big_yang_filter_days: {self.big_yang_filter_days}")
        print(f"  - position_capital_ratio: {self.position_capital_ratio}")
        print(f"[博弈策略] 传入的参数: {self.parameters}")
    
    def _normalize_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """标准化数据列名（中英文兼容）"""
        df = data.copy()
        
        # 列名映射
        column_mapping = {
            '开盘': 'open',
            '收盘': 'close',
            '最高': 'high',
            '最低': 'low',
            '成交量': 'volume',
            '持仓量': 'open_interest',
            '日期': 'date'
        }
        
        # 重命名列
        for old_name, new_name in column_mapping.items():
            if old_name in df.columns and new_name not in df.columns:
                df[new_name] = df[old_name]
        
        # 确保必要的列存在
        required_cols = ['open', 'high', 'low', 'close']
        for col in required_cols:
            if col not in df.columns:
                # 尝试从中文列名获取
                chinese_map = {
                    'open': '开盘',
                    'close': '收盘',
                    'high': '最高',
                    'low': '最低'
                }
                if chinese_map[col] in df.columns:
                    df[col] = df[chinese_map[col]]
                else:
                    raise ValueError(f"数据缺少必要列: {col}")
        
        # 如果没有volume，添加默认值
        if 'volume' not in df.columns:
            if '成交量' in df.columns:
                df['volume'] = df['成交量']
            else:
                df['volume'] = 0
        
        # 如果没有date列，使用索引
        if 'date' not in df.columns:
            if '日期' in df.columns:
                df['date'] = df['日期']
            elif isinstance(df.index, pd.DatetimeIndex):
                df['date'] = df.index
            else:
                df['date'] = pd.date_range(start='2020-01-01', periods=len(df), freq='D')
        
        # 确保数据类型正确
        numeric_cols = ['open', 'high', 'low', 'close', 'volume']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    
    def _detect_stage_simple(self, data: pd.DataFrame) -> int:
        """
        基于技术指标简化判断当前阶段
        
        Returns:
            阶段编号：1-5，0表示未知
        """
        if len(data) < self.stage_window:
            return 0
        
        # 标准化数据
        df = self._normalize_data(data)
        
        # 获取最近的数据
        recent = df.tail(self.stage_window).copy()
        
        # 计算技术指标
        try:
            indicators = compute_futures_technical_indicators(recent)
        except:
            # 如果计算失败，使用简化方法
            close = recent['close']
            gain_60 = (close.iloc[-1] - close.iloc[0]) / close.iloc[0] * 100 if len(close) > 0 and close.iloc[0] > 0 else 0
            gain_30 = (close.iloc[-1] - close.iloc[max(0, len(close)-30)]) / close.iloc[max(0, len(close)-30)] * 100 if len(close) > 30 and close.iloc[max(0, len(close)-30)] > 0 else 0
            gain_20 = (close.iloc[-1] - close.iloc[max(0, len(close)-20)]) / close.iloc[max(0, len(close)-20)] * 100 if len(close) > 20 and close.iloc[max(0, len(close)-20)] > 0 else 0
            
            # 计算RSI（简化版）
            try:
                rsi_series = calculate_rsi_futures(recent)
                rsi = rsi_series.iloc[-1] if not rsi_series.isna().iloc[-1] else 50
            except:
                rsi = 50
            
            indicators = {
                'gain60': gain_60,
                'gain30': gain_30,
                'gain20': gain_20,
                'rsi': rsi
            }
        
        # 获取涨跌幅（兼容不同的键名）
        # compute_futures_gains 返回的键名是 'gain20', 'gain60', 'gain120'
        gain_60 = indicators.get('gain60', indicators.get('gain_60', None))
        gain_30 = indicators.get('gain30', indicators.get('gain_30', None))
        gain_20 = indicators.get('gain20', indicators.get('gain_20', None))
        rsi = indicators.get('rsi', 50)
        
        # 如果还是没有，直接计算
        if gain_60 is None and len(recent) >= 60:
            close = recent['close']
            if close.iloc[0] > 0:
                gain_60 = (close.iloc[-1] - close.iloc[0]) / close.iloc[0] * 100
            else:
                gain_60 = 0
        elif gain_60 is None:
            gain_60 = 0
            
        if gain_30 is None and len(recent) >= 30:
            close = recent['close']
            idx_30 = max(0, len(close) - 30)
            if close.iloc[idx_30] > 0:
                gain_30 = (close.iloc[-1] - close.iloc[idx_30]) / close.iloc[idx_30] * 100
            else:
                gain_30 = 0
        elif gain_30 is None:
            gain_30 = 0
            
        if gain_20 is None and len(recent) >= 20:
            close = recent['close']
            idx_20 = max(0, len(close) - 20)
            if close.iloc[idx_20] > 0:
                gain_20 = (close.iloc[-1] - close.iloc[idx_20]) / close.iloc[idx_20] * 100
            else:
                gain_20 = 0
        elif gain_20 is None:
            gain_20 = 0
        
        # 阶段判断逻辑
        # 五阶段：长期阴跌，近60日跌幅<-15%，RSI<30
        if gain_60 < -15 and rsi < 30:
            return 5
        
        # 四阶段：猛烈下跌，近20日跌幅<-10%，RSI>50但价格下跌
        if gain_20 < -10:
            return 4
        
        # 三阶段：疯狂上涨，近20日涨幅>15%，RSI>70
        if gain_20 > 15 and rsi > 70:
            return 3
        
        # 二阶段：快速上涨，近30日涨幅>10%，RSI 40-70
        if gain_30 > 10 and 40 <= rsi <= 70:
            return 2
        
        # 一阶段：长期下跌后企稳，近60日涨幅<5%，RSI<40
        if gain_60 < 5 and rsi < 40:
            return 1
        
        # 默认返回0（未知）
        return 0
    
    def generate_signal(
        self,
        data: pd.DataFrame,
        portfolio: Any
    ) -> Optional[Dict[str, Any]]:
        """
        生成交易信号
        
        策略逻辑：
        1. 判断当前阶段
        2. 检测恐慌点（买入信号）
        3. 检测好看点（卖出信号）
        4. 根据阶段和信号生成交易指令
        """
        if len(data) < max(self.stage_window, self.panic_window, self.sell_window):
            return None
        
        # 标准化数据
        df = self._normalize_data(data)
        
        # 数据校验：验证OHLC数据的合理性
        try:
            # 检查必要的列是否存在
            required_cols = ['open', 'high', 'low', 'close']
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                print(f"[博弈策略] 数据缺少必要列: {missing_cols}")
                return None
            
            # 检查OHLC数据是否合理
            invalid_count = 0
            # 检查价格是否有效（>0）
            price_cols = ['open', 'high', 'low', 'close']
            for col in price_cols:
                invalid_prices = (df[col] <= 0).sum()
                if invalid_prices > 0:
                    print(f"[博弈策略] 警告: {col}列包含{invalid_prices}个无效价格（<=0）")
                    invalid_count += invalid_prices
            
            # 检查OHLC逻辑关系
            invalid_ohlc = (
                (df['high'] < df['low']) | 
                (df['high'] < df['open']) | 
                (df['high'] < df['close']) |
                (df['low'] > df['open']) | 
                (df['low'] > df['close'])
            ).sum()
            
            if invalid_ohlc > 0:
                print(f"[博弈策略] 警告: 检测到{invalid_ohlc}条OHLC逻辑关系错误的数据")
                invalid_count += invalid_ohlc
            
            # 如果无效数据过多（超过10%），返回None
            if invalid_count > len(df) * 0.1:
                print(f"[博弈策略] 数据质量差，无效数据过多（{invalid_count}/{len(df)}），跳过信号生成")
                return None
        except Exception as e:
            print(f"[博弈策略] 数据校验失败: {e}")
            import traceback
            traceback.print_exc()
            return None
        
        # 确保有必要的列（用于检测函数）
        # detect_panic_points 和 detect_sell_signals 需要中文列名
        if '开盘' not in df.columns:
            if 'open' in df.columns:
                df['开盘'] = df['open']
            else:
                raise ValueError("数据缺少开盘价列")
        if '收盘' not in df.columns:
            if 'close' in df.columns:
                df['收盘'] = df['close']
            else:
                raise ValueError("数据缺少收盘价列")
        if '最高' not in df.columns:
            if 'high' in df.columns:
                df['最高'] = df['high']
            else:
                df['最高'] = df['收盘']  # 使用收盘价作为默认值
        if '最低' not in df.columns:
            if 'low' in df.columns:
                df['最低'] = df['low']
            else:
                df['最低'] = df['收盘']  # 使用收盘价作为默认值
        if '成交量' not in df.columns:
            if 'volume' in df.columns:
                df['成交量'] = df['volume']
            else:
                df['成交量'] = 0  # 默认成交量为0
        if '日期' not in df.columns:
            if 'date' in df.columns:
                df['日期'] = df['date']
            elif isinstance(df.index, pd.DatetimeIndex):
                df['日期'] = df.index
            else:
                df['日期'] = pd.date_range(start='2020-01-01', periods=len(df), freq='D')
        
        # 1. 判断当前阶段
        current_stage = self._detect_stage_simple(df)
        
        # 2. 检测恐慌点（买入信号）
        try:
            panic_points = detect_panic_points(
                df, 
                window=self.panic_window, 
                vol_ratio=self.panic_vol_ratio,
                big_yang_filter_ratio=self.big_yang_filter_ratio,
                big_yang_filter_days=self.big_yang_filter_days
            )
        except Exception as e:
            print(f"[博弈策略] 检测恐慌点失败: {e}")
            panic_points = []
        
        # 检查当前K线是否是恐慌点，或是否接近最近恐慌点后的最低价
        current_panic = None
        near_lowest_after_panic = False
        
        if panic_points and len(df) > 0:
            current_date = df.iloc[-1]['date'] if 'date' in df.columns else df.index[-1]
            current_close = float(df.iloc[-1]['close'])
            current_low = float(df.iloc[-1]['low'])
            
            # 检查当前K线是否是恐慌点
            for point in panic_points:
                point_date = point.get('date')
                if point_date and str(point_date) == str(current_date):
                    current_panic = point
                    break
            
            # 如果没有当前恐慌点，检查当前是否是最近恐慌点后的最低价附近
            # 方法：检测当前是否是最近10-20天内的最低价，且最近有恐慌点记录
            if not current_panic and len(panic_points) > 0:
                # 找到最近的恐慌点
                latest_panic = panic_points[-1]
                panic_date = latest_panic.get('date')
                
                # 方法1：检查当前是否是恐慌点之后的最低价（恐慌点在最近30天内）
                if len(df) >= 30:
                    # 检查恐慌点是否在最近30天内
                    recent_30 = df.tail(30)
                    panic_in_recent = False
                    panic_idx_in_recent = None
                    
                    for idx, row in recent_30.iterrows():
                        row_date = row.get('date') if 'date' in row else idx
                        try:
                            # 尝试日期比较（考虑不同日期格式）
                            if str(row_date).split()[0] == str(panic_date).split()[0] if ' ' in str(row_date) and ' ' in str(panic_date) else str(row_date) == str(panic_date):
                                panic_in_recent = True
                                panic_idx_in_recent = list(recent_30.index).index(idx)
                                break
                        except:
                            continue
                    
                    # 如果恐慌点在最近30天内，检查恐慌点之后是否出现更低价格
                    if panic_in_recent and panic_idx_in_recent is not None:
                        # 恐慌点之后的数据
                        after_panic = recent_30.iloc[panic_idx_in_recent+1:] if panic_idx_in_recent < len(recent_30) - 1 else pd.DataFrame()
                        
                        if len(after_panic) > 0:
                            after_panic_low = float(after_panic['low'].min())
                            
                            # 当前价格接近或等于恐慌点后的最低价（允许0.5%误差）
                            if current_low <= after_panic_low * 1.005 and current_low >= after_panic_low * 0.995:
                                near_lowest_after_panic = True
                                # 日志移到实际买入时打印，避免重复打印
                
                # 方法2：如果方法1不适用，检查当前是否是最近15天内的最低价（且在恐慌点之后）
                if not near_lowest_after_panic and len(df) >= 15:
                    recent_15 = df.tail(15)
                    recent_15_low = float(recent_15['low'].min())
                    
                    # 当前价格是最近15天的最低价（允许0.3%误差）
                    if current_low <= recent_15_low * 1.003:
                        # 确认恐慌点在最近30天内（说明恐慌已经发生）
                        if len(df) >= 30:
                            recent_30_dates = [str(row.get('date') if 'date' in row else idx).split()[0] for idx, row in df.tail(30).iterrows()]
                            panic_date_str = str(panic_date).split()[0] if ' ' in str(panic_date) else str(panic_date)
                            if panic_date_str in recent_30_dates:
                                near_lowest_after_panic = True
                                # 日志移到实际买入时打印，避免重复打印
        
        # 3. 检测好看点（卖出信号，仅1-2阶段）
        sell_signals = []
        bullish_anchor_signals = []
        if current_stage in [1, 2]:
            try:
                sell_signals = detect_sell_signals(df, window=self.sell_window, stage=current_stage)
            except Exception as e:
                print(f"[博弈策略] 检测好看点失败: {e}")
                sell_signals = []
            
            try:
                bullish_anchor_signals = detect_bullish_anchor_pattern(df, window=120)
            except Exception as e:
                print(f"[博弈策略] 检测多方锚定失败: {e}")
                bullish_anchor_signals = []
        
        # 检查当前K线是否是好看点
        current_sell = None
        if len(df) > 0:
            current_date = df.iloc[-1]['date'] if 'date' in df.columns else df.index[-1]
            
            # 检查卖点信号
            for signal in sell_signals:
                signal_date = signal.get('date')
                if signal_date and str(signal_date) == str(current_date):
                    current_sell = signal
                    break
            
            # 检查多方锚定信号
            if not current_sell:
                for signal in bullish_anchor_signals:
                    signal_date = signal.get('date')
                    if signal_date and str(signal_date) == str(current_date):
                        current_sell = signal
                        break
        
        # 4. 生成交易信号
        
        # 卖出信号优先（如果有持仓），但要确认上涨趋势
        if current_sell and portfolio.position.size > 0:
            # 确认上涨趋势：检查最近几日的涨幅
            if len(df) >= 5:
                # 获取最近5日的价格变化
                recent_5 = df.tail(5)
                price_5_days_ago = float(recent_5.iloc[0]['close'])
                current_price = float(df.iloc[-1]['close'])
                gain_5_days = (current_price - price_5_days_ago) / price_5_days_ago * 100
                
                # 确认上涨：最近5日涨幅>3%，或者卖出信号类型是突破前高（突破本身已经确认了上涨）
                is_uptrend_confirmed = (
                    gain_5_days > 3.0 or 
                    current_sell.get('type') == 'breakthrough_high' or
                    current_sell.get('type') == 'limit_up_next_day'
                )
                
                # 如果上涨趋势确认，或者卖出信号是突破前高/涨停第二天（这些信号本身已经确认了上涨），则卖出
                if is_uptrend_confirmed:
                    return {
                        'action': 'CLOSE_ALL',
                        'size': portfolio.position.size,
                        'reason': f'好看点卖出（上涨确认）：{current_sell.get("type", "unknown")}，最近5日涨幅{gain_5_days:.2f}%，{current_sell.get("description", "")}'
                    }
                else:
                    print(f"[博弈策略] 检测到卖出信号，但上涨趋势未确认（最近5日涨幅{gain_5_days:.2f}%），暂不卖出")
            else:
                # 数据不足，但有卖出信号，也执行卖出（保守策略）
                return {
                    'action': 'CLOSE_ALL',
                    'size': portfolio.position.size,
                    'reason': f'好看点卖出：{current_sell.get("type", "unknown")}，{current_sell.get("description", "")}'
                }
        
        # 计算买入数量（支持固定股数或按资金比例）
        def calculate_buy_size(price: float) -> int:
            """计算买入数量"""
            if self.position_capital_ratio > 0:
                # 按资金比例计算
                available_cash = portfolio.cash
                target_capital = available_cash * self.position_capital_ratio
                # 计算能买多少股（考虑手续费和滑点，预留5%的缓冲）
                estimated_cost_per_share = price * 1.05  # 价格 + 手续费和滑点
                calculated_size = int(target_capital / estimated_cost_per_share)
                # 确保至少买100股（1手）
                calculated_size = max(100, (calculated_size // 100) * 100)
                return calculated_size
            else:
                # 使用固定股数
                return self.position_size
        
        # 买入信号（恐慌点或恐慌点后的最低价附近）
        if current_panic or near_lowest_after_panic:
            # 阶段过滤：优先1-2阶段，5阶段也可，避免3-4阶段
            if current_stage in [1, 2, 5]:
                # 检查是否已有持仓
                if portfolio.position.size <= 0:
                    buy_size = calculate_buy_size(current_close)
                    if current_panic:
                        return {
                            'action': 'OPEN_LONG',
                            'size': buy_size,
                            'reason': f'恐慌点买入：{current_panic.get("type", "unknown")}，阶段{current_stage}，{current_panic.get("description", "")}'
                        }
                    elif near_lowest_after_panic:
                        # 找到对应的恐慌点信息用于日志
                        latest_panic = panic_points[-1] if panic_points else None
                        panic_date = latest_panic.get('date') if latest_panic else None
                        print(f"[博弈策略] 恐慌点后的最低价买入：恐慌点{panic_date}，当前价格{current_close:.2f}，阶段{current_stage}，买入{buy_size}股")
                        return {
                            'action': 'OPEN_LONG',
                            'size': buy_size,
                            'reason': f'恐慌点后的最低价附近买入，阶段{current_stage}，价格{current_close:.2f}'
                        }
            elif current_stage == 0:
                # 阶段未知时，也允许买入（但风险较高）
                if portfolio.position.size <= 0:
                    buy_size = calculate_buy_size(current_close)
                    if current_panic:
                        return {
                            'action': 'OPEN_LONG',
                            'size': buy_size,
                            'reason': f'恐慌点买入（阶段未知）：{current_panic.get("type", "unknown")}，{current_panic.get("description", "")}'
                        }
                    elif near_lowest_after_panic:
                        # 找到对应的恐慌点信息用于日志
                        latest_panic = panic_points[-1] if panic_points else None
                        panic_date = latest_panic.get('date') if latest_panic else None
                        print(f"[博弈策略] 恐慌点后的最低价买入（阶段未知）：恐慌点{panic_date}，当前价格{current_close:.2f}，买入{buy_size}股")
                        return {
                            'action': 'OPEN_LONG',
                            'size': buy_size,
                            'reason': f'恐慌点后的最低价附近买入（阶段未知），价格{current_close:.2f}'
                        }
        
        return None

