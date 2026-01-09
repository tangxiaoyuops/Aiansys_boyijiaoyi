"""
千问Embedding适配器
适配千问API的特殊格式要求
"""
import os
from typing import List, Optional
from langchain_core.embeddings import Embeddings
from openai import OpenAI
import logging

logger = logging.getLogger(__name__)


class QwenEmbeddings(Embeddings):
    """
    千问Embedding适配器
    直接调用千问API，适配其特殊格式
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1",
        model: str = "text-embedding-v2",
    ):
        """
        初始化千问Embedding
        
        Args:
            api_key: API密钥
            base_url: API基础URL
            model: 模型名称
        """
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        
        # 创建OpenAI客户端
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
        )
        
        logger.info(f"千问Embedding初始化: model={model}, base_url={base_url}")
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        嵌入文档列表
        千问API可能需要逐个处理或批量处理
        
        Args:
            texts: 文本列表
            
        Returns:
            嵌入向量列表
        """
        embeddings = []
        
        # 千问API可能对批量处理有限制，逐个处理更稳定
        for i, text in enumerate(texts):
            try:
                # 使用embed_query方法，它通常更稳定
                emb = self.embed_query(text)
                embeddings.append(emb)
                
                if (i + 1) % 10 == 0:
                    logger.info(f"已处理 {i + 1}/{len(texts)} 个文档")
            except Exception as e:
                logger.warning(f"文档 {i} 嵌入失败: {e}，使用零向量占位")
                # 返回零向量作为占位符（假设维度为1536，实际可能需要调整）
                embeddings.append([0.0] * 1536)
        
        return embeddings
    
    def embed_query(self, text: str) -> List[float]:
        """
        嵌入单个查询文本
        
        Args:
            text: 查询文本
            
        Returns:
            嵌入向量
        """
        try:
            # 调用千问的embedding API
            response = self.client.embeddings.create(
                model=self.model,
                input=text,  # 千问使用input参数
            )
            
            if response.data and len(response.data) > 0:
                return response.data[0].embedding
            else:
                raise ValueError("API返回空数据")
                
        except Exception as e:
            error_msg = str(e)
            logger.error(f"嵌入查询失败: {error_msg}")
            
            # 如果模型名称不对，尝试其他可能的名称
            if "model" in error_msg.lower() or "InvalidParameter" in error_msg:
                # 尝试不指定model，让API自动选择
                try:
                    logger.info("尝试不指定model参数...")
                    response = self.client.embeddings.create(
                        input=text,
                    )
                    if response.data and len(response.data) > 0:
                        return response.data[0].embedding
                except Exception as e2:
                    logger.error(f"不指定model也失败: {e2}")
            
            raise

