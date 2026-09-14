"""
数据采集模块

负责从Tushare、Akshare等数据源采集股票数据
"""

import tushare as ts
import akshare as ak
import pandas as pd
from typing import List, Dict, Optional
import logging
from datetime import datetime, timedelta
import asyncio

logger = logging.getLogger(__name__)


class StockDataCollector:
    """
    股票数据采集器
    
    支持多个数据源：Tushare、Akshare
    """
    
    def __init__(self, tushare_token: Optional[str] = None):
        """
        初始化数据采集器
        
        Args:
            tushare_token: Tushare API Token
        """
        if tushare_token:
            ts.set_token(tushare_token)
            self.pro = ts.pro_api()
        else:
            self.pro = None
        
        self.logger = logger
    
    async def get_stock_list(self) -> List[Dict]:
        """
        获取A股股票列表
        
        Returns:
            股票列表，包含代码、名称、行业等
        """
        try:
            # 使用Tushare获取股票列表
            if self.pro:
                df = self.pro.stock_basic(
                    exchange='',
                    list_status='L',
                    fields='ts_code,symbol,name,area,industry,market,list_date'
                )
                
                stocks = []
                for _, row in df.iterrows():
                    stocks.append({
                        'stock_code': row['ts_code'],
                        'stock_name': row['name'],
                        'industry': row['industry'],
                        'market': row['market'],
                        'list_date': row['list_date']
                    })
                
                self.logger.info(f"获取到 {len(stocks)} 只股票")
                return stocks
            else:
                # 使用Akshare作为备用
                df = ak.stock_zh_a_spot_em()
                stocks = []
                for _, row in df.iterrows():
                    stocks.append({
                        'stock_code': row['代码'],
                        'stock_name': row['名称']
                    })
                return stocks
                
        except Exception as e:
            self.logger.error(f"获取股票列表失败: {e}")
            return []
    
    async def get_daily_data(
        self,
        stock_code: str,
        start_date: str,
        end_date: str
    ) -> List[Dict]:
        """
        获取日线数据
        
        Args:
            stock_code: 股票代码 (格式：000001.SZ)
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
        
        Returns:
            日线数据列表
        """
        try:
            if self.pro:
                # Tushare格式
                df = self.pro.daily(
                    ts_code=stock_code,
                    start_date=start_date,
                    end_date=end_date
                )
                
                if df.empty:
                    return []
                
                data = []
                for _, row in df.iterrows():
                    data.append({
                        'time': pd.to_datetime(row['trade_date']),
                        'stock_code': row['ts_code'],
                        'open': float(row['open']),
                        'high': float(row['high']),
                        'low': float(row['low']),
                        'close': float(row['close']),
                        'volume': int(row['vol']),
                        'amount': float(row['amount'])
                    })
                
                return data
            else:
                # Akshare格式
                symbol = stock_code.split('.')[0]
                df = ak.stock_zh_a_hist(
                    symbol=symbol,
                    period="daily",
                    start_date=start_date,
                    end_date=end_date,
                    adjust=""
                )
                
                if df.empty:
                    return []
                
                data = []
                for _, row in df.iterrows():
                    data.append({
                        'time': pd.to_datetime(row['日期']),
                        'stock_code': stock_code,
                        'open': float(row['开盘']),
                        'high': float(row['最高']),
                        'low': float(row['最低']),
                        'close': float(row['收盘']),
                        'volume': int(row['成交量']),
                        'amount': float(row['成交额'])
                    })
                
                return data
                
        except Exception as e:
            self.logger.error(f"获取日线数据失败 {stock_code}: {e}")
            return []
    
    async def get_realtime_quote(self, stock_code: str) -> Optional[Dict]:
        """
        获取实时行情
        
        Args:
            stock_code: 股票代码
        
        Returns:
            实时行情数据
        """
        try:
            symbol = stock_code.split('.')[0]
            df = ak.stock_zh_a_spot_em()
            stock_data = df[df['代码'] == symbol]
            
            if stock_data.empty:
                return None
            
            row = stock_data.iloc[0]
            
            return {
                'stock_code': stock_code,
                'stock_name': row['名称'],
                'price': float(row['最新价']),
                'open': float(row['今开']),
                'high': float(row['最高']),
                'low': float(row['最低']),
                'volume': int(row['成交量']),
                'amount': float(row['成交额']),
                'change_percent': float(row['涨跌幅']),
                'change': float(row['涨跌额']),
                'turnover_rate': float(row['换手率']) if '换手率' in row else 0,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            self.logger.error(f"获取实时行情失败 {stock_code}: {e}")
            return None
    
    async def get_limit_up_stocks(self) -> List[Dict]:
        """
        获取涨停股票列表
        
        Returns:
            涨停股票列表
        """
        try:
            df = ak.stock_zh_a_spot_em()
            
            # 涨幅接近10%的股票
            limit_ups = df[df['涨跌幅'] >= 9.9]
            
            stocks = []
            for _, row in limit_ups.iterrows():
                stocks.append({
                    'stock_code': row['代码'],
                    'stock_name': row['名称'],
                    'price': float(row['最新价']),
                    'change_percent': float(row['涨跌幅']),
                    'volume': int(row['成交量']),
                    'amount': float(row['成交额']),
                    'limit_up_times': 1,  # 需要额外计算连板次数
                    'timestamp': datetime.now()
                })
            
            self.logger.info(f"发现 {len(stocks)} 只涨停股票")
            return stocks
            
        except Exception as e:
            self.logger.error(f"获取涨停股票失败: {e}")
            return []
    
    async def get_market_indices(self) -> List[Dict]:
        """
        获取大盘指数
        
        Returns:
            大盘指数列表
        """
        try:
            # 上证指数
            sh_index = ak.stock_zh_index_daily(symbol="sh000001")
            sh_latest = sh_index.iloc[-1]
            
            # 深证成指
            sz_index = ak.stock_zh_index_daily(symbol="sz399001")
            sz_latest = sz_index.iloc[-1]
            
            # 创业板指
            cy_index = ak.stock_zh_index_daily(symbol="sz399006")
            cy_latest = cy_index.iloc[-1]
            
            return [
                {
                    'index_code': '000001.SH',
                    'index_name': '上证指数',
                    'price': float(sh_latest['close']),
                    'change': float(sh_latest['close'] - sh_latest['open']),
                    'change_percent': float(
                        (sh_latest['close'] - sh_latest['open']) / sh_latest['open'] * 100
                    )
                },
                {
                    'index_code': '399001.SZ',
                    'index_name': '深证成指',
                    'price': float(sz_latest['close']),
                    'change': float(sz_latest['close'] - sz_latest['open']),
                    'change_percent': float(
                        (sz_latest['close'] - sz_latest['open']) / sz_latest['open'] * 100
                    )
                },
                {
                    'index_code': '399006.SZ',
                    'index_name': '创业板指',
                    'price': float(cy_latest['close']),
                    'change': float(cy_latest['close'] - cy_latest['open']),
                    'change_percent': float(
                        (cy_latest['close'] - cy_latest['open']) / cy_latest['open'] * 100
                    )
                }
            ]
            
        except Exception as e:
            self.logger.error(f"获取大盘指数失败: {e}")
            return []
    
    async def collect_all_stocks_daily_data(
        self,
        start_date: str,
        end_date: str,
        batch_size: int = 50
    ) -> Dict[str, int]:
        """
        批量采集全市场日线数据
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            batch_size: 批次大小
        
        Returns:
            统计信息 {'total': 总数, 'success': 成功数, 'failed': 失败数}
        """
        self.logger.info(f"开始批量采集日线数据: {start_date} - {end_date}")
        
        # 获取股票列表
        stock_list = await self.get_stock_list()
        total = len(stock_list)
        success_count = 0
        failed_count = 0
        
        # 分批处理
        for i in range(0, total, batch_size):
            batch = stock_list[i:i + batch_size]
            
            tasks = []
            for stock in batch:
                task = self.get_daily_data(
                    stock['stock_code'],
                    start_date,
                    end_date
                )
                tasks.append(task)
            
            # 并发采集
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, Exception):
                    failed_count += 1
                elif result:
                    success_count += 1
                    # TODO: 保存到数据库
                else:
                    failed_count += 1
            
            self.logger.info(
                f"进度: {i + len(batch)}/{total}, "
                f"成功: {success_count}, 失败: {failed_count}"
            )
            
            # 避免请求过快
            await asyncio.sleep(0.5)
        
        return {
            'total': total,
            'success': success_count,
            'failed': failed_count
        }


# 创建全局数据采集器实例
_collector: Optional[StockDataCollector] = None


def get_collector() -> StockDataCollector:
    """获取数据采集器实例（单例）"""
    global _collector
    
    if _collector is None:
        from core.intelligent_system.config import settings
        _collector = StockDataCollector(tushare_token=settings.TUSHARE_TOKEN)
    
    return _collector
