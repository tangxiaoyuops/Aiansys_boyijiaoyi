"""
技术指标计算模块
计算各类技术指标：MA、MACD、RSI、ATR、布林带等
"""
import numpy as np
from typing import List, Dict, Any, Optional
from core.models.strategy_models import TechnicalIndicators


class TechnicalIndicatorCalculator:
    """技术指标计算器"""
    
    @staticmethod
    def calculate_sma(data: List[float], period: int) -> List[float]:
        """
        计算简单移动平均线（SMA）
        
        Args:
            data: 价格数据
            period: 周期
        
        Returns:
            SMA值列表
        """
        if len(data) < period:
            return [None] * len(data)
        
        sma = []
        for i in range(len(data)):
            if i < period - 1:
                sma.append(None)
            else:
                window = data[i - period + 1:i + 1]
                sma.append(sum(window) / period)
        
        return sma
    
    @staticmethod
    def calculate_ema(data: List[float], period: int) -> List[float]:
        """
        计算指数移动平均线（EMA）
        
        Args:
            data: 价格数据
            period: 周期
        
        Returns:
            EMA值列表
        """
        if len(data) < period:
            return [None] * len(data)
        
        multiplier = 2 / (period + 1)
        ema = [None] * len(data)
        ema[period - 1] = sum(data[:period]) / period
        
        for i in range(period, len(data)):
            ema[i] = (data[i] - ema[i - 1]) * multiplier + ema[i - 1]
        
        return ema
    
    @staticmethod
    def calculate_macd(
        data: List[float],
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9
    ) -> Dict[str, List[float]]:
        """
        计算MACD指标
        
        Args:
            data: 价格数据
            fast_period: 快线周期
            slow_period: 慢线周期
            signal_period: 信号线周期
        
        Returns:
            {"dif": DIF, "dea": DEA, "macd": MACD柱}
        """
        ema_fast = TechnicalIndicatorCalculator.calculate_ema(data, fast_period)
        ema_slow = TechnicalIndicatorCalculator.calculate_ema(data, slow_period)
        
        dif = []
        for i in range(len(data)):
            if ema_fast[i] is None or ema_slow[i] is None:
                dif.append(None)
            else:
                dif.append(ema_fast[i] - ema_slow[i])
        
        dea = TechnicalIndicatorCalculator.calculate_ema([x or 0 for x in dif], signal_period)
        
        macd = []
        for i in range(len(data)):
            if dif[i] is None or dea[i] is None:
                macd.append(None)
            else:
                macd.append((dif[i] - dea[i]) * 2)
        
        return {"dif": dif, "dea": dea, "macd": macd}
    
    @staticmethod
    def calculate_rsi(data: List[float], period: int = 14) -> List[float]:
        """
        计算RSI指标
        
        Args:
            data: 价格数据
            period: 周期
        
        Returns:
            RSI值列表
        """
        if len(data) < period + 1:
            return [None] * len(data)
        
        deltas = [data[i] - data[i - 1] for i in range(1, len(data))]
        
        gains = [max(delta, 0) for delta in deltas]
        losses = [max(-delta, 0) for delta in deltas]
        
        avg_gains = []
        avg_losses = []
        
        avg_gains.append(sum(gains[:period]) / period)
        avg_losses.append(sum(losses[:period]) / period)
        
        for i in range(period, len(gains)):
            avg_gains.append((avg_gains[-1] * (period - 1) + gains[i]) / period)
            avg_losses.append((avg_losses[-1] * (period - 1) + losses[i]) / period)
        
        rsi = [None] * (period + 1)
        
        for i in range(len(avg_gains)):
            if avg_losses[i] == 0:
                rsi.append(100)
            else:
                rs = avg_gains[i] / avg_losses[i]
                rsi.append(100 - (100 / (1 + rs)))
        
        return rsi
    
    @staticmethod
    def calculate_bollinger_bands(
        data: List[float],
        period: int = 20,
        std_dev: float = 2.0
    ) -> Dict[str, List[float]]:
        """
        计算布林带
        
        Args:
            data: 价格数据
            period: 周期
            std_dev: 标准差倍数
        
        Returns:
            {"upper": 上轨, "middle": 中轨, "lower": 下轨}
        """
        sma = TechnicalIndicatorCalculator.calculate_sma(data, period)
        
        upper = []
        lower = []
        
        for i in range(len(data)):
            if i < period - 1:
                upper.append(None)
                lower.append(None)
            else:
                window = data[i - period + 1:i + 1]
                std = np.std(window)
                upper.append(sma[i] + std_dev * std)
                lower.append(sma[i] - std_dev * std)
        
        return {"upper": upper, "middle": sma, "lower": lower}
    
    @staticmethod
    def calculate_atr(
        high: List[float],
        low: List[float],
        close: List[float],
        period: int = 14
    ) -> List[float]:
        """
        计算ATR（平均真实波幅）
        
        Args:
            high: 最高价列表
            low: 最低价列表
            close: 收盘价列表
            period: 周期
        
        Returns:
            ATR值列表
        """
        if len(close) < period + 1:
            return [None] * len(close)
        
        tr = []
        for i in range(1, len(close)):
            tr1 = high[i] - low[i]
            tr2 = abs(high[i] - close[i - 1])
            tr3 = abs(low[i] - close[i - 1])
            tr.append(max(tr1, tr2, tr3))
        
        atr = [None] * (period + 1)
        atr[period] = sum(tr[:period]) / period
        
        for i in range(period, len(tr)):
            atr.append((atr[-1] * (period - 1) + tr[i]) / period)
        
        return atr
    
    @staticmethod
    def calculate_obv(close: List[float], volume: List[float]) -> List[float]:
        """
        计算OBV（能量潮）
        
        Args:
            close: 收盘价列表
            volume: 成交量列表
        
        Returns:
            OBV值列表
        """
        if len(close) != len(volume) or len(close) == 0:
            return [None] * len(close)
        
        obv = [0]
        
        for i in range(1, len(close)):
            if close[i] > close[i - 1]:
                obv.append(obv[-1] + volume[i])
            elif close[i] < close[i - 1]:
                obv.append(obv[-1] - volume[i])
            else:
                obv.append(obv[-1])
        
        return obv
    
    @staticmethod
    def calculate_kdj(
        high: List[float],
        low: List[float],
        close: List[float],
        n: int = 9,
        m1: int = 3,
        m2: int = 3
    ) -> Dict[str, List[float]]:
        """
        计算KDJ指标
        
        Args:
            high: 最高价列表
            low: 最低价列表
            close: 收盘价列表
            n: 周期
            m1: K值平滑周期
            m2: D值平滑周期
        
        Returns:
            {"k": K值, "d": D值, "j": J值}
        """
        if len(close) < n:
            return {"k": [None] * len(close), "d": [None] * len(close), "j": [None] * len(close)}
        
        rsv = []
        for i in range(n - 1, len(close)):
            high_n = max(high[i - n + 1:i + 1])
            low_n = min(low[i - n + 1:i + 1])
            if high_n == low_n:
                rsv.append(50)
            else:
                rsv.append((close[i] - low_n) / (high_n - low_n) * 100)
        
        k = [None] * (n - 1)
        k.append(sum(rsv[:m1]) / m1)
        
        for i in range(m1, len(rsv)):
            k.append((k[-1] * 2 + rsv[i]) / 3)
        
        d = [None] * (n - 1 + m1 - 1)
        d.append(sum(k[n - 1:n - 1 + m1]) / m1)
        
        for i in range(n - 1 + m1, len(k)):
            d.append((d[-1] * 2 + k[i]) / 3)
        
        j = []
        for i in range(len(d)):
            if d[i] is None:
                j.append(None)
            else:
                j.append(3 * k[i] - 2 * d[i])
        
        return {"k": k, "d": d, "j": j}
    
    @staticmethod
    def calculate_cci(
        high: List[float],
        low: List[float],
        close: List[float],
        period: int = 14
    ) -> List[float]:
        """
        计算CCI指标
        
        Args:
            high: 最高价列表
            low: 最低价列表
            close: 收盘价列表
            period: 周期
        
        Returns:
            CCI值列表
        """
        if len(close) < period:
            return [None] * len(close)
        
        tp = [(h + l + c) / 3 for h, l, c in zip(high, low, close)]
        
        cci = [None] * (period - 1)
        
        for i in range(period - 1, len(tp)):
            tp_window = tp[i - period + 1:i + 1]
            ma_tp = sum(tp_window) / period
            md = sum(abs(x - ma_tp) for x in tp_window) / period
            
            if md == 0:
                cci.append(0)
            else:
                cci.append((tp[i] - ma_tp) / (0.015 * md))
        
        return cci
    
    @staticmethod
    def calculate_all_indicators(
        high: List[float],
        low: List[float],
        close: List[float],
        volume: Optional[List[float]] = None
    ) -> TechnicalIndicators:
        """
        计算所有技术指标
        
        Args:
            high: 最高价列表
            low: 最低价列表
            close: 收盘价列表
            volume: 成交量列表（可选）
        
        Returns:
            TechnicalIndicators: 技术指标对象
        """
        ma_short = TechnicalIndicatorCalculator.calculate_sma(close, 5)
        ma_medium = TechnicalIndicatorCalculator.calculate_sma(close, 20)
        ma_long = TechnicalIndicatorCalculator.calculate_sma(close, 60)
        
        macd_result = TechnicalIndicatorCalculator.calculate_macd(close)
        rsi = TechnicalIndicatorCalculator.calculate_rsi(close)
        bollinger_result = TechnicalIndicatorCalculator.calculate_bollinger_bands(close)
        atr = TechnicalIndicatorCalculator.calculate_atr(high, low, close)
        
        kdj_result = TechnicalIndicatorCalculator.calculate_kdj(high, low, close)
        cci = TechnicalIndicatorCalculator.calculate_cci(high, low, close)
        
        obv = None
        if volume:
            obv = TechnicalIndicatorCalculator.calculate_obv(close, volume)
        
        return TechnicalIndicators(
            ma_short=ma_short[-1] if ma_short[-1] else None,
            ma_medium=ma_medium[-1] if ma_medium[-1] else None,
            ma_long=ma_long[-1] if ma_long[-1] else None,
            macd_dif=macd_result["dif"][-1] if macd_result["dif"][-1] else None,
            macd_dea=macd_result["dea"][-1] if macd_result["dea"][-1] else None,
            macd_bar=macd_result["macd"][-1] if macd_result["macd"][-1] else None,
            rsi=rsi[-1] if rsi[-1] else None,
            bollinger_upper=bollinger_result["upper"][-1] if bollinger_result["upper"][-1] else None,
            bollinger_middle=bollinger_result["middle"][-1] if bollinger_result["middle"][-1] else None,
            bollinger_lower=bollinger_result["lower"][-1] if bollinger_result["lower"][-1] else None,
            atr=atr[-1] if atr[-1] else None,
            obv=obv[-1] if obv and obv[-1] else None,
            adx=None,
            cci=cci[-1] if cci[-1] else None,
            kdj_k=kdj_result["k"][-1] if kdj_result["k"][-1] else None,
            kdj_d=kdj_result["d"][-1] if kdj_result["d"][-1] else None,
            kdj_j=kdj_result["j"][-1] if kdj_result["j"][-1] else None
        )


def create_technical_indicator_calculator() -> TechnicalIndicatorCalculator:
    """创建技术指标计算器实例"""
    return TechnicalIndicatorCalculator()
