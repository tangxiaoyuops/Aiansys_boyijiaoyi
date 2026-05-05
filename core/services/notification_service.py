"""
消息通知服务
支持多种通知方式：文件存储、Webhook、邮件等
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import json
import logging
import asyncio
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class EmailConfig:
    """邮件配置"""
    enabled: bool = False
    smtp_server: str = ""
    smtp_port: int = 465
    smtp_user: str = ""
    smtp_password: str = ""
    use_ssl: bool = True
    recipients: List[str] = field(default_factory=list)
    sender_name: str = "股票扫描助手"


@dataclass
class WebhookConfig:
    """Webhook配置"""
    enabled: bool = False
    url: str = ""
    webhook_type: str = "custom"  # "wechat", "dingtalk", "custom"


class NotificationService:
    """消息通知服务"""
    
    def __init__(
        self,
        output_dir: str = "output/scan_results",
        email_config: Optional[EmailConfig] = None,
        webhook_config: Optional[WebhookConfig] = None
    ):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.email_config = email_config or EmailConfig()
        self.webhook_config = webhook_config or WebhookConfig()
    
    async def save_result(self, result: Dict[str, Any]) -> str:
        """保存扫描结果到文件"""
        date_str = datetime.now().strftime("%Y%m%d")
        time_str = datetime.now().strftime("%H%M%S")
        filename = f"pool_scan_{date_str}_{time_str}.json"
        filepath = self.output_dir / filename
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        logger.info(f"[NotificationService] 结果已保存: {filepath}")
        return str(filepath)
    
    async def send_notification(
        self,
        result: Dict[str, Any],
        channels: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        发送通知
        
        Args:
            result: 扫描结果
            channels: 通知渠道列表 ["file", "webhook", "email"]
        
        Returns:
            各渠道发送状态
        """
        if channels is None:
            channels = ["file"]
        
        status = {}
        
        # 保存文件
        if "file" in channels:
            try:
                filepath = await self.save_result(result)
                status["file"] = {"success": True, "filepath": filepath}
            except Exception as e:
                status["file"] = {"success": False, "error": str(e)}
                logger.error(f"[NotificationService] 保存文件失败: {e}")
        
        # Webhook通知
        if "webhook" in channels and self.webhook_config.enabled:
            try:
                await self._send_webhook(result)
                status["webhook"] = {"success": True}
            except Exception as e:
                status["webhook"] = {"success": False, "error": str(e)}
                logger.error(f"[NotificationService] Webhook发送失败: {e}")
        
        # 邮件通知
        if "email" in channels and self.email_config.enabled:
            try:
                await self._send_email(result)
                status["email"] = {"success": True, "recipients": self.email_config.recipients}
            except Exception as e:
                status["email"] = {"success": False, "error": str(e)}
                logger.error(f"[NotificationService] 邮件发送失败: {e}")
        
        return status
    
    async def _send_webhook(self, result: Dict[str, Any]) -> None:
        """发送Webhook通知"""
        import aiohttp
        
        signals = result.get("signals", [])
        buy_signals = [s for s in signals if s["signal_type"] == "buy"]
        sell_signals = [s for s in signals if s["signal_type"] == "sell"]
        
        message = self._build_webhook_message(result, buy_signals, sell_signals)
        
        # 根据webhook类型构建请求体
        if self.webhook_config.webhook_type == "wechat":
            # 企业微信格式
            payload = {
                "msgtype": "markdown",
                "markdown": {"content": message}
            }
        elif self.webhook_config.webhook_type == "dingtalk":
            # 钉钉格式
            payload = {
                "msgtype": "text",
                "text": {"content": message}
            }
        else:
            # 自定义格式
            payload = {
                "message": message,
                "data": result
            }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.webhook_config.url,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                if resp.status != 200:
                    raise Exception(f"Webhook请求失败: {resp.status}")
                logger.info("[NotificationService] Webhook发送成功")
    
    async def _send_email(self, result: Dict[str, Any]) -> None:
        """发送邮件通知"""
        if not self.email_config.recipients:
            raise ValueError("邮件收件人列表为空")
        
        signals = result.get("signals", [])
        buy_signals = [s for s in signals if s["signal_type"] == "buy"]
        sell_signals = [s for s in signals if s["signal_type"] == "sell"]
        
        # 构建邮件内容
        subject = f"【股票扫描报告】{result['scan_time']}"
        html_content = self._build_email_html(result, buy_signals, sell_signals)
        text_content = self._build_email_text(result, buy_signals, sell_signals)
        
        # 创建邮件
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{self.email_config.sender_name} <{self.email_config.smtp_user}>"
        msg["To"] = ", ".join(self.email_config.recipients)
        
        msg.attach(MIMEText(text_content, "plain", "utf-8"))
        msg.attach(MIMEText(html_content, "html", "utf-8"))
        
        # 发送邮件
        def send_smtp():
            if self.email_config.use_ssl:
                with smtplib.SMTP_SSL(
                    self.email_config.smtp_server,
                    self.email_config.smtp_port
                ) as server:
                    server.login(
                        self.email_config.smtp_user,
                        self.email_config.smtp_password
                    )
                    server.sendmail(
                        self.email_config.smtp_user,
                        self.email_config.recipients,
                        msg.as_string()
                    )
            else:
                with smtplib.SMTP(
                    self.email_config.smtp_server,
                    self.email_config.smtp_port
                ) as server:
                    server.starttls()
                    server.login(
                        self.email_config.smtp_user,
                        self.email_config.smtp_password
                    )
                    server.sendmail(
                        self.email_config.smtp_user,
                        self.email_config.recipients,
                        msg.as_string()
                    )
        
        # 在线程池中执行
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, send_smtp)
        
        logger.info(f"[NotificationService] 邮件发送成功: {self.email_config.recipients}")
    
    def _build_webhook_message(
        self,
        result: Dict[str, Any],
        buy_signals: List[Dict],
        sell_signals: List[Dict]
    ) -> str:
        """构建Webhook消息"""
        message = f"【股票池扫描报告】\n"
        message += f"扫描时间: {result['scan_time']}\n"
        message += f"扫描股票: {result['scanned_stocks']}/{result['total_stocks']}\n"
        message += f"买入信号: {len(buy_signals)} 个\n"
        message += f"卖出信号: {len(sell_signals)} 个\n\n"
        
        if buy_signals:
            message += "【买入信号TOP5】\n"
            for s in buy_signals[:5]:
                message += f"- {s['code']} {s['name']}: {s['reasoning'][:50]}...\n"
        
        if sell_signals:
            message += "\n【卖出信号TOP5】\n"
            for s in sell_signals[:5]:
                message += f"- {s['code']} {s['name']}: {s['reasoning'][:50]}...\n"
        
        return message
    
    def _build_email_html(
        self,
        result: Dict[str, Any],
        buy_signals: List[Dict],
        sell_signals: List[Dict]
    ) -> str:
        """构建HTML邮件内容"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #1a73e8; color: white; padding: 20px; border-radius: 8px 8px 0 0; }}
                .summary {{ background: #f8f9fa; padding: 15px; margin: 20px 0; border-radius: 8px; }}
                .section {{ margin: 20px 0; }}
                .buy-signal {{ background: #e8f5e9; border-left: 4px solid #4caf50; padding: 12px; margin: 10px 0; }}
                .sell-signal {{ background: #ffebee; border-left: 4px solid #f44336; padding: 12px; margin: 10px 0; }}
                .signal-header {{ font-weight: bold; color: #1a73e8; }}
                .confidence {{ color: #666; font-size: 0.9em; }}
                .footer {{ text-align: center; color: #999; font-size: 0.8em; margin-top: 30px; }}
                table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
                th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background: #f5f5f5; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>股票池扫描报告</h1>
                    <p>扫描时间: {result['scan_time']}</p>
                </div>
                
                <div class="summary">
                    <h3>扫描概览</h3>
                    <table>
                        <tr><th>扫描股票数</th><td>{result['scanned_stocks']}/{result['total_stocks']}</td></tr>
                        <tr><th>买入信号</th><td style="color: green; font-weight: bold;">{len(buy_signals)} 个</td></tr>
                        <tr><th>卖出信号</th><td style="color: red; font-weight: bold;">{len(sell_signals)} 个</td></tr>
                    </table>
                </div>
        """
        
        # 买入信号
        if buy_signals:
            html += """
                <div class="section">
                    <h3 style="color: #4caf50;">买入信号</h3>
            """
            for s in buy_signals[:10]:
                html += f"""
                    <div class="buy-signal">
                        <div class="signal-header">{s['code']} {s['name']}</div>
                        <div>日期: {s['signal_date']} | 价格: {s['price']:.2f}</div>
                        <div>阶段: {s['stage_name']}</div>
                        <div>跌幅: {s.get('drop_pct', 0):.2f}% | 放量: {s.get('vol_ratio', 0):.2f}倍</div>
                        <div class="confidence">置信度: {s['confidence']:.2f}</div>
                        <div>建议: {s['suggested_action']}</div>
                    </div>
                """
            html += "</div>"
        
        # 卖出信号
        if sell_signals:
            html += """
                <div class="section">
                    <h3 style="color: #f44336;">卖出信号</h3>
            """
            for s in sell_signals[:10]:
                html += f"""
                    <div class="sell-signal">
                        <div class="signal-header">{s['code']} {s['name']}</div>
                        <div>日期: {s['signal_date']} | 价格: {s['price']:.2f}</div>
                        <div>阶段: {s['stage_name']}</div>
                        <div>涨幅: {s.get('gain_pct', 0):.2f}% | 放量: {s.get('vol_ratio', 0):.2f}倍</div>
                        <div class="confidence">置信度: {s['confidence']:.2f}</div>
                        <div>建议: {s['suggested_action']}</div>
                    </div>
                """
            html += "</div>"
        
        html += """
                <div class="footer">
                    <p>本报告由博弈交易分析系统自动生成，仅供参考，不构成投资建议。</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _build_email_text(
        self,
        result: Dict[str, Any],
        buy_signals: List[Dict],
        sell_signals: List[Dict]
    ) -> str:
        """构建纯文本邮件内容"""
        text = f"""
股票池扫描报告
================

扫描时间: {result['scan_time']}
扫描股票: {result['scanned_stocks']}/{result['total_stocks']}
买入信号: {len(buy_signals)} 个
卖出信号: {len(sell_signals)} 个

"""
        
        if buy_signals:
            text += "买入信号\n--------\n"
            for s in buy_signals[:10]:
                text += f"""
- {s['code']} {s['name']}
  日期: {s['signal_date']} | 价格: {s['price']:.2f}
  阶段: {s['stage_name']}
  跌幅: {s.get('drop_pct', 0):.2f}% | 放量: {s.get('vol_ratio', 0):.2f}倍
  置信度: {s['confidence']:.2f}
  建议: {s['suggested_action']}
"""
        
        if sell_signals:
            text += "\n卖出信号\n--------\n"
            for s in sell_signals[:10]:
                text += f"""
- {s['code']} {s['name']}
  日期: {s['signal_date']} | 价格: {s['price']:.2f}
  阶段: {s['stage_name']}
  涨幅: {s.get('gain_pct', 0):.2f}% | 放量: {s.get('vol_ratio', 0):.2f}倍
  置信度: {s['confidence']:.2f}
  建议: {s['suggested_action']}
"""
        
        text += "\n本报告由博弈交易分析系统自动生成，仅供参考，不构成投资建议。\n"
        
        return text
    
    def update_email_config(self, config: EmailConfig) -> None:
        """更新邮件配置"""
        self.email_config = config
    
    def update_webhook_config(self, config: WebhookConfig) -> None:
        """更新Webhook配置"""
        self.webhook_config = config
