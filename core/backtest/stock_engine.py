"""
股票回测引擎核心模块
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import pandas as pd
import numpy as np

from .stock_broker import StockBroker, StockBrokerConfig
from .portfolio import Portfolio
from .risk_manager import RiskManager, RiskConfig
from .metrics.performance import PerformanceMetrics
from .metrics.risk import RiskMetrics
from .metrics.trade_stats import TradeStatistics
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..strategy.base import Strategy


@dataclass
class StockBacktestConfig:
    """股票回测配置"""
    initial_capital: float = 100000.0  # 初始资金
    commission_rate: float = 0.0003  # 手续费率（万3）
    slippage: float = 0.0002  # 滑点（万2）
    stamp_tax_rate: float = 0.001  # 印花税（卖出时，0.1%）
    min_commission: float = 5.0  # 最小手续费（元）
    max_position: int = 10000  # 最大持仓（股数）
    stop_loss_ratio: float = 0.05  # 止损比例
    take_profit_ratio: float = 0.10  # 止盈比例


class StockBacktestEngine:
    """股票回测引擎"""
    
    def __init__(self, config: StockBacktestConfig):
        """
        初始化回测引擎
        
        Args:
            config: 回测配置
        """
        self.config = config
        
        # 创建股票券商
        broker_config = StockBrokerConfig(
            commission_rate=config.commission_rate,
            slippage=config.slippage,
            stamp_tax_rate=config.stamp_tax_rate,
            min_commission=config.min_commission
        )
        self.broker = StockBroker(broker_config)
        
        # 创建风险管理器（股票不使用保证金，max_margin_rate设为1.0表示无限制）
        risk_config = RiskConfig(
            max_margin_rate=1.0,  # 股票不使用保证金，设为1.0表示无限制
            max_position_size=config.max_position,
            stop_loss_ratio=config.stop_loss_ratio,
            take_profit_ratio=config.take_profit_ratio
        )
        self.risk_manager = RiskManager(risk_config)
        
        # 创建组合
        self.portfolio = Portfolio(config.initial_capital)
    
    def run_backtest(
        self,
        data: pd.DataFrame,
        strategy: Any,  # Strategy类型，避免循环导入
        strategy_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        运行回测
        
        Args:
            data: OHLCV数据，必须包含列：'open', 'high', 'low', 'close', 'volume' 或中文列名
            strategy: 策略实例（需要实现generate_signal方法）
            strategy_params: 策略参数
            
        Returns:
            回测结果字典
        """
        # 初始化策略
        if hasattr(strategy, 'initialize'):
            strategy.initialize(strategy_params or {})
        
        # 标准化数据列名
        print(f"[股票回测引擎] 标准化数据，原始列名: {list(data.columns)}")
        data = self._normalize_data(data)
        print(f"[股票回测引擎] 标准化后列名: {list(data.columns)}, 数据行数: {len(data)}")
        
        if len(data) == 0:
            return {
                'success': False,
                'error': '数据为空'
            }
        
        # 保存原始数据用于返回K线数据
        self.data = data
        
        # 重置组合
        self.portfolio = Portfolio(self.config.initial_capital)
        print(f"[股票回测引擎] 初始化组合，初始资金: {self.config.initial_capital}")
        
        # 逐日回测
        print(f"[股票回测引擎] 开始逐日回测，共 {len(data)} 个交易日")
        for i in range(len(data)):
            try:
                current_bar = data.iloc[i].to_dict()
                # 获取日期（优先使用索引，其次使用date列）
                if isinstance(data.index, pd.DatetimeIndex):
                    current_date = data.index[i]
                elif 'date' in current_bar:
                    current_date = pd.to_datetime(current_bar['date'])
                else:
                    current_date = i
                
                # 将日期添加到current_bar中，确保broker可以获取到正确的交易时间
                # 处理日期格式，确保是datetime对象
                if isinstance(current_date, pd.Timestamp):
                    current_bar['date'] = current_date.to_pydatetime()
                elif isinstance(current_date, datetime):
                    current_bar['date'] = current_date
                elif isinstance(current_date, (int, float)):
                    # 如果是数字索引，尝试从数据中获取日期
                    if 'date' in data.columns:
                        date_val = data.iloc[i]['date']
                        if pd.notna(date_val):
                            current_bar['date'] = pd.to_datetime(date_val).to_pydatetime()
                        else:
                            # 如果date列为空，尝试从索引获取
                            if isinstance(data.index, pd.DatetimeIndex):
                                current_bar['date'] = data.index[i].to_pydatetime()
                            else:
                                # 最后备选：使用一个基于索引的日期（从今天往前推）
                                days_ago = len(data) - i - 1
                                current_bar['date'] = (datetime.now() - pd.Timedelta(days=days_ago)).replace(hour=0, minute=0, second=0, microsecond=0)
                    else:
                        # 如果数据中没有date列，尝试从索引获取
                        if isinstance(data.index, pd.DatetimeIndex):
                            current_bar['date'] = data.index[i].to_pydatetime()
                        else:
                            # 最后备选：使用一个基于索引的日期
                            days_ago = len(data) - i - 1
                            current_bar['date'] = (datetime.now() - pd.Timedelta(days=days_ago)).replace(hour=0, minute=0, second=0, microsecond=0)
                else:
                    # 尝试转换其他格式的日期
                    try:
                        parsed_date = pd.to_datetime(current_date)
                        if pd.notna(parsed_date):
                            current_bar['date'] = parsed_date.to_pydatetime() if isinstance(parsed_date, pd.Timestamp) else datetime.now()
                        else:
                            current_bar['date'] = datetime.now()
                    except:
                        current_bar['date'] = datetime.now()
                
                # 更新持仓价格
                current_price = current_bar.get('close', 0)
                if pd.isna(current_price) or current_price <= 0:
                    print(f"[股票回测引擎] 第 {i} 天价格无效: {current_price}，跳过")
                    continue
                
                current_price = float(current_price)
                
                self.portfolio.update_position_price(current_price)
                
                # 风险检查（股票不使用保证金，但需要检查资金充足）
                # 股票的风险检查主要是止损止盈，而不是保证金
                
                # 止损止盈检查
                if self.risk_manager.should_stop_loss(self.portfolio):
                    signal = {
                        'action': 'CLOSE_ALL',
                        'size': abs(self.portfolio.position.size),
                        'reason': '止损'
                    }
                    self.broker.execute_order(signal, current_bar, self.portfolio)
                    continue
                
                if self.risk_manager.should_take_profit(self.portfolio):
                    signal = {
                        'action': 'CLOSE_ALL',
                        'size': abs(self.portfolio.position.size),
                        'reason': '止盈'
                    }
                    self.broker.execute_order(signal, current_bar, self.portfolio)
                    continue
                
                # 获取历史数据（到当前bar为止）
                historical_data = data.iloc[:i+1].copy()
                
                # 生成交易信号
                signal = strategy.generate_signal(historical_data, self.portfolio)
                
                # 执行交易
                if signal:
                    self.broker.execute_order(signal, current_bar, self.portfolio)
                
                # 记录每日状态
                self.portfolio.record_daily_stat(current_date, current_price)
            except Exception as e:
                print(f"[股票回测引擎] 第 {i} 天处理异常: {e}")
                import traceback
                print(traceback.format_exc())
                continue
        
        print(f"[股票回测引擎] 回测循环完成，交易次数: {len(self.portfolio.trade_log)}")
        
        # 计算绩效指标
        try:
            metrics = self._calculate_metrics()
            print(f"[股票回测引擎] 指标计算完成")
        except Exception as e:
            print(f"[股票回测引擎] 指标计算异常: {e}")
            import traceback
            print(traceback.format_exc())
            metrics = {}
        
        # 转换交易日志为可序列化格式，添加更易读的字段
        trade_log_serializable = []
        open_trade_map = {}  # 用于跟踪开仓交易，key为direction
        for trade in self.portfolio.trade_log:
            # 基础字段
            trade_dict = {
                'time': trade.time.isoformat() if hasattr(trade.time, 'isoformat') else str(trade.time),
                'action': trade.action,
                'direction': trade.direction,
                'size': trade.size,
                'price': trade.price,
                'commission': trade.commission,
                'slippage': trade.slippage,
                'reason': trade.reason,
                'equity_before': trade.equity_before,
                'equity_after': trade.equity_after
            }
            
            # 添加易读字段
            if trade.action in ['OPEN_LONG', 'OPEN_SHORT']:
                # 开仓交易
                trade_amount = trade.size * trade.price  # 交易金额（不含手续费）
                trade_dict['operation_type'] = '开仓'
                trade_dict['shares'] = trade.size  # 买入股数
                trade_dict['trade_price'] = round(trade.price, 2)  # 成交价格
                trade_dict['trade_amount'] = round(trade_amount, 2)  # 交易金额
                trade_dict['total_cost'] = round(trade_amount + trade.commission + trade.slippage, 2)  # 总成本（含手续费）
                # 保存开仓信息，用于后续平仓时计算盈亏
                if trade.direction not in open_trade_map:
                    open_trade_map[trade.direction] = []
                open_trade_map[trade.direction].append({
                    'size': trade.size,
                    'price': trade.price,
                    'time': trade.time,
                    'total_cost': trade_amount + trade.commission + trade.slippage
                })
            elif trade.action in ['CLOSE_LONG', 'CLOSE_SHORT', 'CLOSE_ALL']:
                # 平仓交易
                close_direction = -trade.direction if trade.action == 'CLOSE_ALL' else -trade.direction
                trade_amount = trade.size * trade.price  # 卖出金额（不含手续费）
                trade_dict['operation_type'] = '平仓'
                trade_dict['shares'] = trade.size  # 卖出股数
                trade_dict['trade_price'] = round(trade.price, 2)  # 卖出价格
                trade_dict['trade_amount'] = round(trade_amount, 2)  # 卖出金额
                trade_dict['net_proceeds'] = round(trade_amount - trade.commission - trade.slippage, 2)  # 净收入（扣除手续费）
                
                # 计算盈亏：查找对应的开仓交易
                pnl = 0.0
                pnl_pct = 0.0
                if close_direction in open_trade_map and open_trade_map[close_direction]:
                    open_trade = open_trade_map[close_direction].pop(0) if open_trade_map[close_direction] else None
                    if open_trade:
                        # 计算盈亏：卖出净收入 - 开仓总成本
                        pnl = (trade_amount - trade.commission - trade.slippage) - open_trade['total_cost']
                        # 计算盈亏比例
                        if open_trade['total_cost'] > 0:
                            pnl_pct = (pnl / open_trade['total_cost']) * 100
                        
                        trade_dict['open_price'] = round(open_trade['price'], 2)  # 开仓价格
                        trade_dict['open_shares'] = open_trade['size']  # 开仓股数
                        trade_dict['open_total_cost'] = round(open_trade['total_cost'], 2)  # 开仓总成本
                
                trade_dict['pnl'] = round(pnl, 2)  # 盈亏金额
                trade_dict['pnl_pct'] = round(pnl_pct, 2)  # 盈亏比例（%）
                # 判断是止盈还是止损
                if pnl > 0:
                    trade_dict['pnl_type'] = '止盈'
                elif pnl < 0:
                    trade_dict['pnl_type'] = '止损'
                else:
                    trade_dict['pnl_type'] = '平本'
            
            trade_log_serializable.append(trade_dict)
        
        # 转换每日统计为可序列化格式
        daily_stats_serializable = []
        for stat in self.portfolio.daily_stats:
            stat_dict = stat.copy()
            if 'date' in stat_dict and hasattr(stat_dict['date'], 'isoformat'):
                stat_dict['date'] = stat_dict['date'].isoformat()
            else:
                stat_dict['date'] = str(stat_dict['date']) if 'date' in stat_dict else None
            daily_stats_serializable.append(stat_dict)
        
        # 转换K线数据为可序列化格式
        kline_data_serializable = []
        if hasattr(self, 'data') and self.data is not None:
            for idx, row in self.data.iterrows():
                # 优先使用date列，如果没有则从索引获取
                date_val = None
                if 'date' in row and pd.notna(row['date']):
                    date_val = row['date']
                elif isinstance(self.data.index, pd.DatetimeIndex):
                    date_val = self.data.index[self.data.index.get_loc(idx)]
                elif hasattr(idx, 'isoformat'):
                    date_val = idx
                elif hasattr(idx, 'strftime'):
                    date_val = idx
                else:
                    # 如果都没有，尝试从索引转换为日期
                    try:
                        date_val = pd.to_datetime(idx)
                    except:
                        date_val = None
                
                # 统一转换为ISO格式字符串
                if date_val is not None:
                    if isinstance(date_val, pd.Timestamp):
                        date_str = date_val.strftime('%Y-%m-%d')
                    elif hasattr(date_val, 'isoformat'):
                        date_str = date_val.isoformat()[:10]  # 只取日期部分
                    elif hasattr(date_val, 'strftime'):
                        date_str = date_val.strftime('%Y-%m-%d')
                    else:
                        try:
                            date_str = pd.to_datetime(date_val).strftime('%Y-%m-%d')
                        except:
                            date_str = str(date_val)
                else:
                    date_str = str(idx)
                
                kline_dict = {
                    'date': date_str,
                    'open': float(row.get('open', 0) or 0),
                    'high': float(row.get('high', 0) or 0),
                    'low': float(row.get('low', 0) or 0),
                    'close': float(row.get('close', 0) or 0),
                    'volume': float(row.get('volume', 0) or 0),
                    'open_interest': 0  # 股票没有持仓量
                }
                kline_data_serializable.append(kline_dict)
        
        return {
            'success': True,
            'equity_curve': self.portfolio.equity_history,
            'trade_log': trade_log_serializable,
            'daily_stats': daily_stats_serializable,
            'kline_data': kline_data_serializable,
            'metrics': metrics,
            'config': self.config.__dict__
        }
    
    def _normalize_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """标准化数据列名"""
        data = data.copy()
        
        # 列名映射（中文/英文 -> 标准英文列名）
        column_mapping = {
            # 中文列名
            '开盘': 'open',
            '最高': 'high',
            '最低': 'low',
            '收盘': 'close',
            '成交量': 'volume',
            '日期': 'date',
            # 英文列名（akshare可能返回的）
            'settle': 'close',  # 结算价，如果没有close可以用这个
        }
        
        # 重命名列
        for old_name, new_name in column_mapping.items():
            if old_name in data.columns:
                if new_name not in data.columns:
                    data[new_name] = data[old_name]
                elif old_name != new_name:
                    # 如果新列名已存在，但旧列名不同，则用旧列名的值更新（如果新列名为空）
                    data[new_name] = data[new_name].fillna(data[old_name])
        
        # 确保必要的列存在
        required_cols = ['open', 'high', 'low', 'close']
        for col in required_cols:
            if col not in data.columns:
                raise ValueError(f"数据缺少必要列: {col}，当前列名: {list(data.columns)}")
        
        # 如果没有volume，添加默认值
        if 'volume' not in data.columns:
            data['volume'] = 0
        
        # 确保数据类型正确
        numeric_cols = ['open', 'high', 'low', 'close', 'volume']
        for col in numeric_cols:
            if col in data.columns:
                data[col] = pd.to_numeric(data[col], errors='coerce')
        
        # 确保日期列存在（用于索引）
        if 'date' in data.columns:
            data['date'] = pd.to_datetime(data['date'], errors='coerce')
            # 如果date列存在，设置为索引
            if data.index.name != 'date' and 'date' in data.columns:
                data = data.set_index('date')
        
        return data
    
    def _calculate_metrics(self) -> Dict[str, Any]:
        """计算绩效指标"""
        if len(self.portfolio.equity_history) < 2:
            return {}
        
        equity_curve = np.array(self.portfolio.equity_history)
        trade_log = self.portfolio.trade_log
        
        # 绩效指标
        perf_metrics = PerformanceMetrics(equity_curve, self.config.initial_capital)
        
        # 风险指标
        risk_metrics = RiskMetrics(equity_curve)
        
        # 交易统计
        trade_stats = TradeStatistics(trade_log)
        
        # 获取风险指标
        max_dd_result = risk_metrics.max_drawdown()
        volatility_value = risk_metrics.volatility()
        downside_dev_value = risk_metrics.downside_deviation()
        
        # 提取最大回撤数值
        max_dd_value = max_dd_result.get('max_drawdown', 0.0) if isinstance(max_dd_result, dict) else max_dd_result
        
        # 辅助函数：清理inf和nan值，确保JSON兼容
        def clean_value(value):
            """将inf和nan转换为可序列化的值"""
            if value is None:
                return 0.0
            if isinstance(value, (int, float)):
                if np.isinf(value):
                    # 正无穷用999.99表示，负无穷用-999.99表示
                    return 999.99 if value > 0 else -999.99
                if np.isnan(value):
                    return 0.0
            return value
        
        # 计算指标
        metrics_dict = {
            # 收益指标
            'total_return': perf_metrics.total_return(),
            'annual_return': perf_metrics.annual_return(),
            'monthly_returns': perf_metrics.monthly_returns(),
            
            # 风险指标
            'max_drawdown': max_dd_value,
            'max_drawdown_duration': max_dd_result.get('max_drawdown_duration', 0) if isinstance(max_dd_result, dict) else 0,
            'current_drawdown': max_dd_result.get('current_drawdown', 0.0) if isinstance(max_dd_result, dict) else 0.0,
            'drawdown_series': max_dd_result.get('drawdown_series', []) if isinstance(max_dd_result, dict) else [],
            'volatility': volatility_value,
            'var_95': risk_metrics.value_at_risk(0.95),
            'cvar_95': risk_metrics.conditional_var(0.95),
            
            # 风险调整收益
            'sharpe_ratio': perf_metrics.sharpe_ratio(volatility_value),
            'sortino_ratio': perf_metrics.sortino_ratio(downside_dev_value),
            'calmar_ratio': perf_metrics.calmar_ratio(max_dd_value),
            
            # 交易统计
            'win_rate': trade_stats.win_rate(),
            'profit_factor': trade_stats.profit_factor(),
            'avg_trade': trade_stats.average_trade(),
            'total_trades': trade_stats.total_trades(),
            'avg_holding_period': trade_stats.average_holding_period(),
            
            # 股票特有
            'final_equity': float(equity_curve[-1]),
            'total_profit': float(equity_curve[-1] - self.config.initial_capital),
        }
        
        # 清理所有指标值中的inf和nan
        cleaned_metrics = {}
        for key, value in metrics_dict.items():
            if isinstance(value, (list, tuple)):
                # 处理列表（如monthly_returns, drawdown_series）
                cleaned_list = []
                for item in value:
                    if isinstance(item, dict):
                        cleaned_item = {k: clean_value(v) for k, v in item.items()}
                        cleaned_list.append(cleaned_item)
                    else:
                        cleaned_list.append(clean_value(item))
                cleaned_metrics[key] = cleaned_list
            else:
                cleaned_metrics[key] = clean_value(value)
        
        return cleaned_metrics

