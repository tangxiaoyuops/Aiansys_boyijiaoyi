"""
数据库管理模块

提供PostgreSQL和TimescaleDB的连接和操作管理
"""

import asyncpg
from typing import Optional, Dict, List, Any
import logging
from contextlib import asynccontextmanager
import json

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    数据库管理器
    
    管理PostgreSQL和TimescaleDB的连接和操作
    """
    
    def __init__(self, database_url: str, timescaledb_url: str):
        self.database_url = database_url
        self.timescaledb_url = timescaledb_url
        self.pg_pool: Optional[asyncpg.Pool] = None
        self.ts_pool: Optional[asyncpg.Pool] = None
    
    async def connect(self):
        """建立数据库连接池"""
        try:
            # PostgreSQL连接池
            self.pg_pool = await asyncpg.create_pool(
                self.database_url,
                min_size=5,
                max_size=20,
                command_timeout=60
            )
            logger.info("PostgreSQL连接池创建成功")
            
            # TimescaleDB连接池
            self.ts_pool = await asyncpg.create_pool(
                self.timescaledb_url,
                min_size=5,
                max_size=20,
                command_timeout=60
            )
            logger.info("TimescaleDB连接池创建成功")
            
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            raise
    
    async def disconnect(self):
        """关闭数据库连接池"""
        if self.pg_pool:
            await self.pg_pool.close()
            logger.info("PostgreSQL连接池已关闭")
        
        if self.ts_pool:
            await self.ts_pool.close()
            logger.info("TimescaleDB连接池已关闭")
    
    @asynccontextmanager
    async def get_pg_connection(self):
        """获取PostgreSQL连接"""
        if not self.pg_pool:
            await self.connect()
        
        async with self.pg_pool.acquire() as connection:
            try:
                yield connection
            except Exception as e:
                logger.error(f"PostgreSQL操作异常: {e}")
                await connection.execute('ROLLBACK')
                raise
    
    @asynccontextmanager
    async def get_ts_connection(self):
        """获取TimescaleDB连接"""
        if not self.ts_pool:
            await self.connect()
        
        async with self.ts_pool.acquire() as connection:
            try:
                yield connection
            except Exception as e:
                logger.error(f"TimescaleDB操作异常: {e}")
                await connection.execute('ROLLBACK')
                raise
    
    # ========== TimescaleDB时序数据操作 ==========
    
    async def save_stock_daily_data(self, data: List[Dict]) -> None:
        """
        保存股票日线数据到TimescaleDB
        
        Args:
            data: 日线数据列表，每个元素包含:
                - time: 时间戳
                - stock_code: 股票代码
                - open, high, low, close: 价格
                - volume, amount: 成交量和成交额
        """
        query = """
            INSERT INTO stock_daily (
                time, stock_code, open, high, low, close, 
                volume, amount, turnover
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            ON CONFLICT (time, stock_code) 
            DO UPDATE SET
                open = EXCLUDED.open,
                high = EXCLUDED.high,
                low = EXCLUDED.low,
                close = EXCLUDED.close,
                volume = EXCLUDED.volume,
                amount = EXCLUDED.amount
        """
        
        async with self.get_ts_connection() as conn:
            await conn.executemany(query, [
                (
                    d['time'], d['stock_code'], d['open'], d['high'],
                    d['low'], d['close'], d['volume'], d['amount'],
                    d.get('turnover', 0)
                )
                for d in data
            ])
        
        logger.info(f"保存了 {len(data)} 条日线数据")
    
    async def get_stock_daily_data(
        self,
        stock_code: str,
        start_date: str,
        end_date: str,
        limit: int = 500
    ) -> List[Dict]:
        """
        获取股票日线数据
        
        Args:
            stock_code: 股票代码
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            limit: 返回数据条数限制
        
        Returns:
            日线数据列表
        """
        query = """
            SELECT * FROM stock_daily 
            WHERE stock_code = $1 
            AND time >= $2 
            AND time <= $3
            ORDER BY time DESC
            LIMIT $4
        """
        
        async with self.get_ts_connection() as conn:
            rows = await conn.fetch(query, stock_code, start_date, end_date, limit)
            return [dict(row) for row in rows]
    
    async def save_agent_analysis_result(
        self,
        stock_code: str,
        analysis_type: str,
        result: Dict,
        confidence: float
    ) -> None:
        """
        保存Agent分析结果
        
        Args:
            stock_code: 股票代码
            analysis_type: 分析类型 (phase/washing/distribution)
            result: 分析结果
            confidence: 置信度
        """
        query = """
            INSERT INTO agent_analysis_results (
                time, stock_code, analysis_type, result, confidence
            ) VALUES (NOW(), $1, $2, $3, $4)
            ON CONFLICT (time, stock_code, analysis_type)
            DO UPDATE SET
                result = EXCLUDED.result,
                confidence = EXCLUDED.confidence
        """
        
        async with self.get_ts_connection() as conn:
            await conn.execute(
                query,
                stock_code,
                analysis_type,
                json.dumps(result, ensure_ascii=False),
                confidence
            )
        
        logger.info(f"保存Agent分析结果: {stock_code} - {analysis_type}")
    
    # ========== PostgreSQL关系数据操作 ==========
    
    async def get_stock_info(self, stock_code: str) -> Optional[Dict]:
        """获取股票基本信息"""
        query = "SELECT * FROM stock_info WHERE stock_code = $1"
        
        async with self.get_pg_connection() as conn:
            row = await conn.fetchrow(query, stock_code)
            return dict(row) if row else None
    
    async def save_stock_info(self, info: Dict) -> None:
        """保存股票基本信息"""
        query = """
            INSERT INTO stock_info (
                stock_code, stock_name, industry, sector, 
                list_date, total_shares, float_shares
            ) VALUES ($1, $2, $3, $4, $5, $6, $7)
            ON CONFLICT (stock_code)
            DO UPDATE SET
                stock_name = EXCLUDED.stock_name,
                industry = EXCLUDED.industry,
                sector = EXCLUDED.sector,
                total_shares = EXCLUDED.total_shares,
                float_shares = EXCLUDED.float_shares
        """
        
        async with self.get_pg_connection() as conn:
            await conn.execute(
                query,
                info['stock_code'],
                info['stock_name'],
                info.get('industry'),
                info.get('sector'),
                info.get('list_date'),
                info.get('total_shares'),
                info.get('float_shares')
            )
    
    async def save_trading_signal(self, signal: Dict) -> int:
        """
        保存交易信号
        
        Returns:
            信号ID
        """
        query = """
            INSERT INTO trading_signals (
                signal_type, stock_code, stock_name, price, 
                position_ratio, reason, confidence, agent_decision
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            RETURNING id
        """
        
        async with self.get_pg_connection() as conn:
            signal_id = await conn.fetchval(
                query,
                signal['signal_type'],
                signal['stock_code'],
                signal.get('stock_name'),
                signal.get('price'),
                signal.get('position_ratio'),
                signal.get('reason'),
                signal.get('confidence'),
                json.dumps(signal.get('agent_decision', {}), ensure_ascii=False)
            )
        
        logger.info(f"保存交易信号: {signal['signal_type']} - {signal['stock_code']}")
        return signal_id
    
    async def save_alert(self, alert: Dict) -> int:
        """
        保存预警
        
        Returns:
            预警ID
        """
        query = """
            INSERT INTO alerts (
                user_id, alert_type, stock_code, title, 
                message, priority, agent_analysis
            ) VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING id
        """
        
        async with self.get_pg_connection() as conn:
            alert_id = await conn.fetchval(
                query,
                alert.get('user_id', 1),  # 默认用户ID为1
                alert['alert_type'],
                alert.get('stock_code'),
                alert['title'],
                alert.get('message'),
                alert.get('priority', 5),
                json.dumps(alert.get('agent_analysis', {}), ensure_ascii=False)
            )
        
        logger.info(f"保存预警: {alert['alert_type']} - {alert.get('stock_code', 'N/A')}")
        return alert_id
    
    async def get_unread_alerts(self, user_id: int, limit: int = 50) -> List[Dict]:
        """获取未读预警"""
        query = """
            SELECT * FROM alerts 
            WHERE user_id = $1 AND status = 'UNREAD'
            ORDER BY create_time DESC
            LIMIT $2
        """
        
        async with self.get_pg_connection() as conn:
            rows = await conn.fetch(query, user_id, limit)
            return [dict(row) for row in rows]


# 创建全局数据库管理器实例（延迟初始化）
_db_manager: Optional[DatabaseManager] = None


async def get_db_manager() -> DatabaseManager:
    """获取数据库管理器实例（单例）"""
    global _db_manager
    
    if _db_manager is None:
        from core.intelligent_system.config import settings
        _db_manager = DatabaseManager(
            database_url=settings.DATABASE_URL,
            timescaledb_url=settings.TIMESCALEDB_URL
        )
        await _db_manager.connect()
    
    return _db_manager
