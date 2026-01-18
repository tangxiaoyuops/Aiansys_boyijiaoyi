/**
 * 策略相关API
 */
import axios from 'axios';
import { API_BASE_URL } from './index';

/**
 * 获取策略模板列表
 */
export async function getStrategyTemplates(): Promise<string[]> {
  // 这里返回预定义的策略列表
  return ['dual_ma', 'triple_ma', 'bollinger_bands', 'rsi', 'game_theory'];
}

/**
 * 获取策略参数说明
 */
export async function getStrategyParams(strategy_name: string): Promise<Record<string, any>> {
  // 策略参数说明
  const paramsMap: Record<string, any> = {
    dual_ma: {
      fast_period: { type: 'number', default: 5, description: '快速均线周期' },
      slow_period: { type: 'number', default: 20, description: '慢速均线周期' },
      position_size: { type: 'number', default: 1, description: '每次开仓手数' }
    },
    triple_ma: {
      fast_period: { type: 'number', default: 5, description: '快速均线周期' },
      mid_period: { type: 'number', default: 20, description: '中期均线周期' },
      slow_period: { type: 'number', default: 60, description: '慢速均线周期' },
      position_size: { type: 'number', default: 1, description: '每次开仓手数' }
    },
    bollinger_bands: {
      period: { type: 'number', default: 20, description: '周期' },
      std_dev: { type: 'number', default: 2.0, description: '标准差倍数' },
      position_size: { type: 'number', default: 1, description: '每次开仓手数' }
    },
    rsi: {
      rsi_period: { type: 'number', default: 14, description: 'RSI周期' },
      rsi_overbought: { type: 'number', default: 70, description: '超买阈值' },
      rsi_oversold: { type: 'number', default: 30, description: '超卖阈值' },
      position_size: { type: 'number', default: 1, description: '每次开仓手数' }
    },
    game_theory: {
      panic_drop_threshold: { type: 'number', default: -3.0, description: '恐慌点跌幅阈值(%)', step: 0.1, min: -10, max: 0 },
      panic_vol_ratio: { type: 'number', default: 1.5, description: '恐慌点放量倍数', step: 0.1, min: 1.0, max: 5.0 },
      sell_gain_threshold: { type: 'number', default: 5.0, description: '好看点涨幅阈值(%)', step: 0.1, min: 0, max: 20 },
      sell_vol_ratio: { type: 'number', default: 1.5, description: '好看点放量倍数', step: 0.1, min: 1.0, max: 5.0 },
      position_size: { type: 'number', default: 100, description: '每次开仓股数(固定股数，0表示使用资金比例)', min: 0, step: 100 },
      position_capital_ratio: { type: 'number', default: 0.0, description: '每笔操作资金比例(0-1，0表示使用固定股数)', step: 0.01, min: 0, max: 1, precision: 2 },
      stage_window: { type: 'number', default: 60, description: '阶段判断窗口(天)', min: 20, max: 200 },
      panic_window: { type: 'number', default: 60, description: '恐慌点检测窗口(天)', min: 20, max: 200 },
      sell_window: { type: 'number', default: 60, description: '好看点检测窗口(天)', min: 20, max: 200 },
      big_yang_filter_ratio: { type: 'number', default: 1.2, description: '大阳线过滤比例(恐慌点阴线长度需>大阳线长度×此比例)', step: 0.1, min: 1.0, max: 3.0, precision: 1 },
      big_yang_filter_days: { type: 'number', default: 10, description: '大阳线过滤天数(检查前N天是否有大阳线)', min: 5, max: 30 },
      enable_short: { type: 'boolean', default: false, description: '是否允许开空' }
    }
  };
  
  return paramsMap[strategy_name] || {};
}

