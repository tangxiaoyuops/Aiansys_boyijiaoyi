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
            base_url=os.getenv("OPENAI_BASE_URL"),
            timeout=600.0  # 600秒超时（10分钟）
        )
    return _client


def call_llm(
    system_prompt: str,
    user_prompt: str,
    model: Optional[str] = None,
    temperature: float = 0.3,
    timeout: int = 120
) -> str:
    """
    调用大模型
    
    Args:
        system_prompt: 系统提示词
        user_prompt: 用户提示词
        model: 模型名称（默认从环境变量 QWEN_MODEL 读取）
        temperature: 温度参数
        timeout: 超时时间（秒），默认120秒
    
    Returns:
        模型返回的文本
    """
    import time
    start_time = time.time()
    
    try:
        print(f"[LLM调用] 开始调用大模型...")
        print(f"[LLM调用] 模型: {model or os.getenv('QWEN_MODEL', 'qwen-plus')}")
        print(f"[LLM调用] 系统提示词长度: {len(system_prompt)} 字符")
        print(f"[LLM调用] 用户提示词长度: {len(user_prompt)} 字符")
        
        client = get_llm_client()
        model_name = model or os.getenv("QWEN_MODEL", "qwen-plus")
        
        print(f"[LLM调用] 正在发送请求到API...")
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature
        )
        
        elapsed_time = time.time() - start_time
        print(f"[LLM调用] API响应成功，耗时: {elapsed_time:.2f}秒")
        
        if response.choices and len(response.choices) > 0:
            content = response.choices[0].message.content or ""
            print(f"[LLM调用] 返回内容长度: {len(content)} 字符")
            return content
        print(f"[LLM调用] 警告: 响应中没有choices")
        return ""
    except Exception as e:
        elapsed_time = time.time() - start_time
        error_str = str(e)
        
        # 提取关键错误信息
        error_msg = error_str
        if 'inappropriate content' in error_str or 'data_inspection_failed' in error_str:
            error_msg = "内容审核未通过：模型认为输出内容可能包含不当内容"
        elif 'BadRequestError' in error_str or '400' in error_str:
            # 尝试提取更简洁的错误信息
            if 'message' in error_str:
                try:
                    import json
                    # 尝试解析错误信息
                    if "'message':" in error_str:
                        start = error_str.find("'message':") + 11
                        end = error_str.find("'", start)
                        if end > start:
                            error_msg = error_str[start:end]
                except:
                    pass
        
        print(f"[LLM调用失败] 耗时: {elapsed_time:.2f}秒")
        print(f"[LLM调用失败] 错误类型: {type(e).__name__}")
        print(f"[LLM调用失败] 错误信息: {error_msg}")
        
        # 抛出异常，让调用方处理
        raise Exception(error_msg)


