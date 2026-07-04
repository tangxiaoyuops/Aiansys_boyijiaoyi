"""
选股报告生成器
生成选股结果报告、可视化图表等
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import logging

from .stock_selection_strategy import SelectionResult, StockCandidate
from .selection_backtester import SelectionBacktestResult

logger = logging.getLogger(__name__)


class SelectionReporter:
    """选股报告生成器"""
    
    def __init__(self):
        pass
    
    def generate_selection_report(
        self,
        result: SelectionResult,
        output_format: str = "markdown"  # markdown, json, html
    ) -> str:
        """
        生成选股报告
        
        Args:
            result: 选股结果
            output_format: 输出格式
        
        Returns:
            报告内容
        """
        if output_format == "markdown":
            return self._generate_markdown_report(result)
        elif output_format == "json":
            return self._generate_json_report(result)
        elif output_format == "html":
            return self._generate_html_report(result)
        else:
            return self._generate_markdown_report(result)
    
    def _generate_markdown_report(self, result: SelectionResult) -> str:
        """生成Markdown格式报告"""
        lines = []
        
        # 标题
        lines.append("# 博弈交易选股报告")
        lines.append("")
        lines.append(f"**扫描时间**: {result.scan_time}")
        lines.append(f"**扫描范围**: {result.total_candidates}只股票")
        lines.append(f"**合格候选**: {result.qualified_candidates}只")
        lines.append(f"**推荐股票**: {len(result.top_candidates)}只")
        lines.append("")
        
        # 顶级推荐
        lines.append("## 📊 顶级推荐股票")
        lines.append("")
        
        if not result.top_candidates:
            lines.append("暂无符合条件的股票")
        else:
            lines.append("| 排名 | 代码 | 名称 | 阶段 | 评分 | 买点类型 | 买入价 | 建议仓位 | 理由 |")
            lines.append("|------|------|------|------|------|----------|--------|----------|------|")
            
            for idx, candidate in enumerate(result.top_candidates, 1):
                bp = candidate.best_buy_point
                lines.append(
                    f"| {idx} | {candidate.code} | {candidate.name} | "
                    f"{candidate.stage} | {candidate.overall_score:.1f} | "
                    f"{bp.buy_type} | {bp.price:.2f} | "
                    f"{candidate.suggested_position_pct*100:.1f}% | {bp.reasoning[:30]}... |"
                )
        
        lines.append("")
        
        # 详细分析
        lines.append("## 📈 详细分析")
        lines.append("")
        
        for idx, candidate in enumerate(result.top_candidates[:5], 1):
            lines.append(f"### {idx}. {candidate.name} ({candidate.code})")
            lines.append("")
            lines.append(f"**阶段**: {candidate.stage_name}")
            lines.append(f"**综合评分**: {candidate.overall_score:.2f}")
            lines.append(f"**趋势强度**: {candidate.trend_strength:.2f}")
            lines.append(f"**情绪评分**: {candidate.emotion_score:.2f}")
            lines.append("")
            
            bp = candidate.best_buy_point
            lines.append(f"**最佳买点**: {bp.buy_type}")
            lines.append(f"- 买入价: {bp.price:.2f}")
            lines.append(f"- 信号日期: {bp.date}")
            lines.append(f"- 置信度: {bp.confidence:.2f}")
            lines.append(f"- 理由: {bp.reasoning}")
            
            if bp.drop_pct is not None:
                lines.append(f"- 跌幅: {bp.drop_pct:.2f}%")
            if bp.vol_ratio is not None:
                lines.append(f"- 放量倍数: {bp.vol_ratio:.2f}")
            
            lines.append("")
            lines.append(f"**仓位建议**:")
            lines.append(f"- 建议仓位: {candidate.suggested_position_pct*100:.1f}%")
            lines.append(f"- 建议股数: {candidate.suggested_shares}股")
            lines.append(f"- 建议金额: {candidate.suggested_amount:.2f}元")
            lines.append("")
            
            # 筛选条件
            lines.append("**筛选条件**:")
            for filter_name, filter_info in candidate.filter_details.items():
                status = "✅" if filter_info['passed'] else "❌"
                lines.append(f"- {status} {filter_name}: {filter_info['reason']}")
            
            lines.append("")
            lines.append("---")
            lines.append("")
        
        # 风险提示
        lines.append("## ⚠️ 风险提示")
        lines.append("")
        lines.append("1. 本报告基于博弈交易理论生成,仅供参考,不构成投资建议")
        lines.append("2. 股市有风险,投资需谨慎")
        lines.append("3. 请结合自身风险承受能力和投资目标做出决策")
        lines.append("4. 建议严格执行止损纪律,控制单只股票仓位")
        lines.append("5. 请关注大盘环境和板块热点,及时调整策略")
        lines.append("")
        
        # 筛选条件说明
        lines.append("## 📋 筛选条件说明")
        lines.append("")
        lines.append("- **阶段过滤**: 优先选择一、二阶段股票,五阶段可考虑")
        lines.append("- **趋势强度**: 至少有一定上涨趋势")
        lines.append("- **买点置信度**: 置信度≥60%")
        lines.append("- **情绪比例**: 难看洗盘+好看出货=看涨信号")
        lines.append("")
        
        # 错误信息
        if result.errors:
            lines.append("## ❌ 错误信息")
            lines.append("")
            for error in result.errors[:10]:
                lines.append(f"- {error['code']}: {error['error']}")
            lines.append("")
        
        return "\n".join(lines)
    
    def _generate_json_report(self, result: SelectionResult) -> str:
        """生成JSON格式报告"""
        return json.dumps(result.to_dict(), ensure_ascii=False, indent=2)
    
    def _generate_html_report(self, result: SelectionResult) -> str:
        """生成HTML格式报告"""
        # 简化版HTML报告
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>博弈交易选股报告</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #4CAF50; color: white; }}
                tr:nth-child(even) {{ background-color: #f2f2f2; }}
                .warning {{ background-color: #fff3cd; padding: 10px; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <h1>博弈交易选股报告</h1>
            <p>扫描时间: {result.scan_time}</p>
            <p>扫描范围: {result.total_candidates}只股票</p>
            <p>合格候选: {result.qualified_candidates}只</p>
            <p>推荐股票: {len(result.top_candidates)}只</p>
            
            <h2>顶级推荐股票</h2>
            <table>
                <tr>
                    <th>排名</th>
                    <th>代码</th>
                    <th>名称</th>
                    <th>阶段</th>
                    <th>评分</th>
                    <th>买点类型</th>
                    <th>买入价</th>
                    <th>建议仓位</th>
                </tr>
        """
        
        for idx, candidate in enumerate(result.top_candidates, 1):
            bp = candidate.best_buy_point
            html += f"""
                <tr>
                    <td>{idx}</td>
                    <td>{candidate.code}</td>
                    <td>{candidate.name}</td>
                    <td>{candidate.stage}</td>
                    <td>{candidate.overall_score:.1f}</td>
                    <td>{bp.buy_type}</td>
                    <td>{bp.price:.2f}</td>
                    <td>{candidate.suggested_position_pct*100:.1f}%</td>
                </tr>
            """
        
        html += """
            </table>
            
            <div class="warning">
                <h3>⚠️ 风险提示</h3>
                <p>本报告基于博弈交易理论生成,仅供参考,不构成投资建议。</p>
                <p>股市有风险,投资需谨慎。请严格执行止损纪律,控制仓位。</p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def generate_backtest_report(
        self,
        result: SelectionBacktestResult,
        output_format: str = "markdown"
    ) -> str:
        """
        生成回测报告
        
        Args:
            result: 回测结果
            output_format: 输出格式
        
        Returns:
            报告内容
        """
        if output_format == "markdown":
            return self._generate_backtest_markdown_report(result)
        elif output_format == "json":
            return json.dumps(result.to_dict(), ensure_ascii=False, indent=2)
        else:
            return self._generate_backtest_markdown_report(result)
    
    def _generate_backtest_markdown_report(self, result: SelectionBacktestResult) -> str:
        """生成回测Markdown报告"""
        lines = []
        
        # 标题
        lines.append("# 博弈交易选股策略回测报告")
        lines.append("")
        
        perf = result.performance
        
        # 概览
        lines.append("## 📊 回测概览")
        lines.append("")
        lines.append(f"- **回测区间**: {perf.start_date} 至 {perf.end_date}")
        lines.append(f"- **初始资金**: {perf.initial_capital:,.2f}元")
        lines.append(f"- **最终资金**: {perf.final_capital:,.2f}元")
        lines.append(f"- **总收益率**: {perf.total_return:.2f}%")
        lines.append(f"- **年化收益率**: {perf.annual_return:.2f}%")
        lines.append(f"- **最大回撤**: {perf.max_drawdown:.2f}%")
        lines.append(f"- **夏普比率**: {perf.sharpe_ratio:.2f}")
        lines.append("")
        
        # 交易统计
        lines.append("## 📈 交易统计")
        lines.append("")
        lines.append(f"- **总交易次数**: {perf.total_trades}")
        lines.append(f"- **盈利次数**: {perf.winning_trades}")
        lines.append(f"- **亏损次数**: {perf.losing_trades}")
        lines.append(f"- **胜率**: {perf.win_rate:.2f}%")
        lines.append(f"- **盈亏比**: {perf.profit_factor:.2f}")
        lines.append(f"- **平均持仓天数**: {perf.avg_holding_days:.1f}天")
        lines.append(f"- **平均盈利**: {perf.avg_profit:.2f}元")
        lines.append(f"- **平均亏损**: {perf.avg_loss:.2f}元")
        lines.append("")
        
        # 交易明细
        lines.append("## 📋 交易明细")
        lines.append("")
        
        if not result.trades:
            lines.append("无交易记录")
        else:
            lines.append("| 代码 | 名称 | 买入日期 | 买入价 | 卖出日期 | 卖出价 | 持仓天数 | 盈亏(元) | 盈亏(%) | 卖出原因 |")
            lines.append("|------|------|----------|--------|----------|--------|----------|----------|---------|----------|")
            
            for trade in result.trades:
                pnl_str = f"{trade.pnl:+.2f}"
                pnl_pct_str = f"{trade.pnl_pct:+.2f}"
                lines.append(
                    f"| {trade.code} | {trade.name} | {trade.buy_date} | {trade.buy_price:.2f} | "
                    f"{trade.sell_date} | {trade.sell_price:.2f} | {trade.holding_days} | "
                    f"{pnl_str} | {pnl_pct_str}% | {trade.sell_reason} |"
                )
        
        lines.append("")
        
        # 风险提示
        lines.append("## ⚠️ 风险提示")
        lines.append("")
        lines.append("1. 历史回测不代表未来表现")
        lines.append("2. 回测可能存在过拟合风险")
        lines.append("3. 实际交易会受到滑点、冲击成本等影响")
        lines.append("4. 请结合实际市场环境调整策略参数")
        lines.append("")
        
        return "\n".join(lines)
    
    def save_report(
        self,
        report: str,
        filepath: str
    ) -> bool:
        """
        保存报告到文件
        
        Args:
            report: 报告内容
            filepath: 文件路径
        
        Returns:
            是否成功
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(report)
            logger.info(f"[SelectionReporter] 报告已保存到 {filepath}")
            return True
        except Exception as e:
            logger.error(f"[SelectionReporter] 保存报告失败: {e}")
            return False
