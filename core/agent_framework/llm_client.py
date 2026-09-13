"""
LLM客户端封装
统一调用接口
"""
from typing import Optional, Dict, Any
import os


class LLMClient:
    """LLM客户端封装"""
    
    def __init__(
        self,
        model: str = "gpt-4o",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000
    ):
        """
        初始化LLM客户端
        
        Args:
            model: 模型名称
            api_key: API密钥
            base_url: API基础URL
            temperature: 温度参数
            max_tokens: 最大token数
        """
        self.model = model
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL")
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # 初始化OpenAI客户端
        self._init_client()
    
    def _init_client(self):
        """初始化客户端"""
        try:
            from openai import OpenAI
            
            client_kwargs = {}
            if self.api_key:
                client_kwargs["api_key"] = self.api_key
            if self.base_url:
                client_kwargs["base_url"] = self.base_url
            
            self.client = OpenAI(**client_kwargs)
            
        except ImportError:
            raise ImportError("请安装openai: pip install openai")
    
    def generate(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        生成响应
        
        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词
            temperature: 温度参数(可选,覆盖默认值)
            max_tokens: 最大token数(可选,覆盖默认值)
        
        Returns:
            生成的文本
        """
        messages = []
        
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            raise RuntimeError(f"LLM调用失败: {str(e)}")
    
    def generate_with_history(
        self,
        prompt: str,
        conversation_history: list,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        带对话历史的生成
        
        Args:
            prompt: 用户提示词
            conversation_history: 对话历史
            system_prompt: 系统提示词
        
        Returns:
            生成的文本
        """
        messages = []
        
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        # 添加对话历史
        messages.extend(conversation_history)
        
        # 添加当前提示
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            raise RuntimeError(f"LLM调用失败: {str(e)}")
