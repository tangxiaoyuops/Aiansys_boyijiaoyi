"""
出货规模 LLM 调试脚本（独立运行，不影响主框架）

用途：
- 给定股票代码 + 数据区间，调用高级出货分析器
- 把分析得到的分水岭事件 / 出货片段 / 出货周期整理成一段「喂给大模型」的中文提示
- 不直接调用大模型，只打印出一份完整 prompt，方便你复制到 ChatGPT / 通义 / 其他大模型里调试回复效果

使用方式（命令行）：
    D:\tools\miniconda\envs\lianghuaansys\python.exe experiments/run_distribution_llm_debug.py 600536 1000

参数说明：
- 第一个参数：股票代码（如 600536）
- 第二个参数：回溯天数（默认 1000，尽量覆盖你要看的整轮出货）
"""

import sys
from datetime import datetime, timedelta
import os

import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv

from core.tools.data_fetcher import fetch_stock_data
from core.tools.advanced_distribution_analyzer import analyze_distribution_advanced


def format_cycle_for_prompt(cycle, idx: int) -> str:
    """把一个出货周期整理成可读文本"""
    if cycle is None:
        return ""

    scale_map = {"small": "小规模出货", "medium": "中等规模出货", "large": "大规模出货"}
    lines = []
    lines.append(f"【出货周期 {idx}】")
    lines.append(
        f"- 时间范围：{cycle.start_date.strftime('%Y-%m-%d')} ~ {cycle.end_date.strftime('%Y-%m-%d')}"
    )
    lines.append(f"- 模型初步判断规模：{scale_map.get(cycle.scale, cycle.scale)}")
    lines.append(f"- 周期内分水岭次数：{cycle.total_watershed_count}")
    lines.append(f"- 周期最高价：约 {cycle.max_price:.2f}")
    lines.append(f"- 周期内最低价：约 {cycle.min_price_in_cycle:.2f}")
    lines.append(
        f"- 周期结束后最大跌幅：约 {cycle.post_cycle_drop_pct:.1f}% "
        f"（下跌持续天数约 {cycle.post_cycle_drop_days} 天）"
    )

    # 片段信息
    if cycle.segments:
        lines.append("- 周期内部出货片段：")
        for i, seg in enumerate(cycle.segments, start=1):
            lines.append(
                f"  - 片段{i}：{seg.start_date.strftime('%Y-%m-%d')} ~ {seg.end_date.strftime('%Y-%m-%d')}"
            )
            lines.append(
                f"    · 高位价区：{seg.low_price:.2f} ~ {seg.high_price:.2f}，平均价约 {seg.avg_price:.2f}"
            )
            lines.append(
                f"    · 区间放量倍数：约 {seg.volume_ratio:.2f} 倍（对比前 60 日）"
            )
            lines.append(f"    · 区间天数：{seg.days} 天")
            lines.append(
                f"    · 片段结束后最大跌幅：约 {seg.post_drop_pct:.1f}%（向后 120 日内）"
            )
            if seg.watershed_events:
                lines.append("    · 片段内分水岭事件：")
                for we in seg.watershed_events:
                    lines.append(
                        f"      · {we.date.strftime('%Y-%m-%d')}："
                        f"收盘 {we.price:.2f}，突破前高 {we.breakthrough_price:.2f}，"
                        f"放量倍数约 {we.volume_ratio:.2f} 倍，"
                        f"后续最大涨幅约 {we.post_days_max_gain:.1f}%、"
                        f"最大跌幅约 {we.post_days_max_drop:.1f}%"
                    )
    return "\n".join(lines)


def build_llm_prompt(
    stock_code: str,
    df: pd.DataFrame,
    advanced_result: dict,
) -> str:
    """
    构建给大模型使用的提示词：
    - 上半部分是规则定义（大/中/小规模出货如何区分）
    - 下半部分是这只股票的结构化出货信息（周期 + 分水岭）
    """
    cycles = advanced_result.get("cycles") or []
    latest_cycle = advanced_result.get("latest_cycle")

    # 补充一段最近K线+量能信息，帮助大模型感知节奏（而不是只看结构化摘要）
    # 这里控制在最近 180 个交易日，避免提示词过长
    recent_bars = df.tail(180).copy()
    recent_lines: list[str] = []
    recent_lines.append("【最近约 180 个交易日的K线与量能概览（按时间顺序，自上而下越新）】")
    recent_lines.append("格式：日期 | 开盘 | 最高 | 最低 | 收盘 | 涨跌幅(%) | 成交量(万手)")
    for _, row in recent_bars.iterrows():
        date_str = (
            row["日期"].strftime("%Y-%m-%d")
            if hasattr(row["日期"], "strftime")
            else str(row["日期"])
        )
        change_pct = float(row.get("涨跌幅", 0.0))
        vol = float(row.get("成交量", 0.0)) / 10000.0  # 换算成万手/万股级别，便于阅读
        recent_lines.append(
            f"{date_str} | {row['开盘']:.2f} | {row['最高']:.2f} | {row['最低']:.2f} | "
            f"{row['收盘']:.2f} | {change_pct:.2f} | {vol:.2f}"
        )

    header = [
        f"你是一名擅长博弈交易结构分析的资深交易员，现在请你帮我判断一只股票历史上的出货规模。",
        f"标的代码：{stock_code}",
        "",
        "【出货规模定义（结合我的交易体系）】",
        "1. 小规模出货：",
        "   - 持续时间较短（通常几天到几周）；",
        "   - 通常围绕某次高调突破或分水岭附近，放量明显，但总体出货时间不长；",
        "   - 后续可能是中短期下跌或震荡，但不一定进入多年大熊。",
        "",
        "2. 中等规模出货：",
        "   - 出货时间通常在 1~3 个月左右；",
        "   - 在同一高位价区附近，可以看到 2 次及以上分水岭结构，或者多次高调突破+放量震荡；",
        "   - 出货结束后，往往会有数个月到一年左右的下跌或弱势震荡。",
        "",
        "3. 大规模出货：",
        "   - 出货周期很长（接近或超过一年），其间多次出现分水岭结构；",
        "   - 出货结束后，往往是 1~2 年级别的深跌 + 低位阴跌，等这轮熊市走完才有新行情；",
        "   - 典型例子就是 2019~2020 年 600536 那种：多次分水岭、高位长时间震荡，然后两年大跌。",
        "",
        "请你结合下面给出的『分水岭事件 / 出货片段 / 出货周期』，",
        "按照上面的定义，用你的语言判断：每一轮周期是小规模、中等规模还是大规模出货，并解释理由。",
        "",
        "【这只股票的结构化出货信息】",
    ]

    body_lines: list[str] = []
    if not cycles:
        body_lines.append("未检测到明显的出货周期，仅供参考。")
    else:
        for idx, cycle in enumerate(cycles, start=1):
            body_lines.append(format_cycle_for_prompt(cycle, idx))
            body_lines.append("")

    # 把最近K线+量能附在后面，供大模型“还原”走势感觉
    body_lines.append("\n".join(recent_lines))

    tail = [
        "【请输出】",
        "1. 针对每一个出货周期，给出：",
        "   - 你的出货规模判断（小规模/中等规模/大规模）；",
        "   - 主要理由（参考：分水岭次数、出货时长、放量特征、出货后下跌幅度和持续时间等）。",
        "2. 最后总结一句：最近一轮出货，对当前持仓的风险提示（比如：是否仍在大规模出货的阴影之下）。",
    ]

    return "\n".join(header + ["\n".join(body_lines)] + tail)


def main():
    # 加载 .env 中的大模型配置
    load_dotenv()

    stock_code = "600536"
    days = 30 if len(sys.argv) >= 3 else 1000

    print(f"=== 获取 {stock_code} 最近 {days} 天数据 ===")
    df = fetch_stock_data(stock_code, days=days)
    if df is None or df.empty:
        print("获取数据失败或为空")
        sys.exit(1)

    print(f"实际获取到 {len(df)} 行数据，日期范围：{df['日期'].min()} ~ {df['日期'].max()}")

    # 高级出货分析
    print("\n=== 运行高级出货分析器 ===")
    adv = analyze_distribution_advanced(df)
    print(adv.get("summary", "无总结"))

    # 构建给大模型的 prompt
    print("\n=== 以下是可直接复制给大模型的提示词（Prompt）===\n")
    prompt = build_llm_prompt(stock_code, df, adv)
    print(prompt)

    # ---------------------------------------------
    # 直接调用通义千问（通过 OpenAI 兼容接口）
    # 前提：你已经在环境里配置好：
    #   OPENAI_API_KEY     -> 通义的 API Key
    #   OPENAI_BASE_URL    -> 通义的 OpenAI 兼容网关地址（例如 https://dashscope.aliyuncs.com/compatible-mode/v1 ）
    #   QWEN_MODEL         -> 使用的模型名称（例如 qwen-plus / qwen-max 等）
    # ---------------------------------------------
    try:
        model_name = os.getenv("QWEN_MODEL", "qwen-plus")
        print(f"\n=== 调用大模型（{model_name}）进行出货规模判定 ===\n")

        client = OpenAI()  # 使用环境变量中的 KEY / BASE_URL

        resp = client.chat.completions.create(
            model="qwen-plus",
            messages=[
                {
                    "role": "system",
                    "content": "你是一名擅长博弈交易结构分析的资深交易员，严格按照用户给出的出货规模定义来判断。",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
        )

        content = resp.choices[0].message.content if resp.choices else ""
        print("=== 大模型返回的出货规模分析 ===\n")
        print(content)
    except Exception as e:
        print(f"\n[警告] 调用大模型失败：{e}")
        print("你仍然可以手动复制上面的 Prompt 到通义千问网页进行调试。")


if __name__ == "__main__":
    main()


