"""
LLM 客户端工具
统一管理大模型调用
"""
import os
from openai import OpenAI
from dotenv import load_dotenv
from typing import Dict, Any, Optional


# 加载环境变量
load_dotenv()

# 全局客户端（单例）
_client: Optional[OpenAI] = None


def get_llm_client() -> OpenAI:
    """获取LLM客户端（单例模式）"""
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL")
        )
    return _client


def call_llm(
    system_prompt: str,
    user_prompt: str,
    model: Optional[str] = None,
    temperature: float = 0.3
) -> str:
    """
    调用大模型
    
    Args:
        system_prompt: 系统提示词
        user_prompt: 用户提示词
        model: 模型名称（默认从环境变量 QWEN_MODEL 读取）
        temperature: 温度参数
    
    Returns:
        模型返回的文本
    """
    try:
        client = get_llm_client()
        model_name = model or os.getenv("QWEN_MODEL", "qwen-plus")
        
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature
        )
        
        if response.choices and len(response.choices) > 0:
            return response.choices[0].message.content or ""
        return ""
    except Exception as e:
        print(f"[LLM调用失败] {e}")
        import traceback
        traceback.print_exc()
        return f"[LLM调用失败: {str(e)}]"


