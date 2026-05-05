"""
股票池管理模块
支持多种股票池来源：沪深300、自定义池、动态池
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
import json
from pathlib import Path


@dataclass
class StockPoolConfig:
    """股票池配置"""
    pool_id: str
    pool_name: str
    pool_type: str  # "hs300" | "custom" | "dynamic"
    codes: List[str] = field(default_factory=list)
    enabled: bool = True
    scan_time: str = "15:30"  # 每日扫描时间
    scan_days: int = 5  # 检测最近N天的买卖点
    created_at: str = ""
    updated_at: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if not self.updated_at:
            self.updated_at = self.created_at
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StockPoolConfig":
        return cls(**data)


class StockPoolManager:
    """股票池管理器"""
    
    def __init__(self, config_path: str = "config/stock_pools.json"):
        self.config_path = Path(config_path)
        self.pools: Dict[str, StockPoolConfig] = {}
        self._load_config()
    
    def _load_config(self) -> None:
        """加载配置文件"""
        if not self.config_path.exists():
            # 创建默认配置
            self._create_default_config()
            return
        
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            pools_data = data.get("pools", [])
            for pool_data in pools_data:
                pool = StockPoolConfig.from_dict(pool_data)
                self.pools[pool.pool_id] = pool
                
        except Exception as e:
            print(f"[StockPoolManager] 加载配置失败: {e}")
            self._create_default_config()
    
    def _create_default_config(self) -> None:
        """创建默认配置"""
        default_pools = [
            StockPoolConfig(
                pool_id="hs300",
                pool_name="沪深300",
                pool_type="hs300",
                codes=[],  # 动态获取
                enabled=True
            ),
            StockPoolConfig(
                pool_id="custom",
                pool_name="自选股",
                pool_type="custom",
                codes=["600519", "000001", "600036"],
                enabled=True
            )
        ]
        
        for pool in default_pools:
            self.pools[pool.pool_id] = pool
        
        self._save_config()
    
    def _save_config(self) -> None:
        """保存配置文件"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "pools": [pool.to_dict() for pool in self.pools.values()],
            "schedule": {
                "cron": "30 15 * * 1-5",
                "enabled": True
            },
            "notification": {
                "email": {
                    "enabled": False,
                    "recipients": []
                },
                "webhook": {
                    "enabled": False,
                    "url": ""
                }
            }
        }
        
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def get_active_pool_codes(self) -> List[str]:
        """获取所有启用的股票池代码（去重）"""
        all_codes = set()
        for pool in self.pools.values():
            if pool.enabled:
                # 如果是沪深300，动态获取
                if pool.pool_type == "hs300":
                    hs300_codes = self._get_hs300_codes()
                    all_codes.update(hs300_codes)
                else:
                    all_codes.update(pool.codes)
        return sorted(all_codes)
    
    def _get_hs300_codes(self) -> List[str]:
        """获取沪深300成分股代码"""
        try:
            import akshare as ak
            df = ak.index_stock_cons(symbol="000300")
            if df is None or df.empty:
                return []
            
            code_col = None
            for col in df.columns:
                col_str = str(col)
                if col_str in ("品种代码", "代码", "index_code", "股票代码", "证券代码"):
                    code_col = col_str
                    break
            
            if code_col is None:
                return []
            
            return df[code_col].astype(str).str.zfill(6).tolist()
        except Exception as e:
            print(f"[StockPoolManager] 获取沪深300成分股失败: {e}")
            return []
    
    def add_pool(self, pool: StockPoolConfig) -> None:
        """添加股票池"""
        pool.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        pool.updated_at = pool.created_at
        self.pools[pool.pool_id] = pool
        self._save_config()
    
    def update_pool(self, pool_id: str, codes: List[str], **kwargs) -> bool:
        """更新股票池"""
        if pool_id not in self.pools:
            return False
        
        pool = self.pools[pool_id]
        pool.codes = codes
        pool.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 更新其他属性
        for key, value in kwargs.items():
            if hasattr(pool, key):
                setattr(pool, key, value)
        
        self._save_config()
        return True
    
    def delete_pool(self, pool_id: str) -> bool:
        """删除股票池"""
        if pool_id in self.pools:
            del self.pools[pool_id]
            self._save_config()
            return True
        return False
    
    def get_pool(self, pool_id: str) -> Optional[StockPoolConfig]:
        """获取指定股票池"""
        return self.pools.get(pool_id)
    
    def list_pools(self) -> List[StockPoolConfig]:
        """列出所有股票池"""
        return list(self.pools.values())
    
    def toggle_pool(self, pool_id: str, enabled: bool) -> bool:
        """启用/禁用股票池"""
        if pool_id not in self.pools:
            return False
        self.pools[pool_id].enabled = enabled
        self.pools[pool_id].updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._save_config()
        return True
