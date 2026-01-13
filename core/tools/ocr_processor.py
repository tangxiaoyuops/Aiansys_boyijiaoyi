"""
OCR处理工具
使用通义千问VL进行图片文字识别
"""
import os
import base64
from typing import Optional, Dict, Any
from PIL import Image
import io
from dotenv import load_dotenv
from openai import OpenAI

# 加载环境变量
load_dotenv()

# 全局客户端（单例）
_client: Optional[OpenAI] = None


def get_vision_client() -> OpenAI:
    """获取视觉模型客户端（单例模式）"""
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL"),
            timeout=120.0  # 120秒超时
        )
    return _client


def compress_image(image_path: str, max_size: int = 2048, quality: int = 85) -> bytes:
    """
    压缩图片以减少API调用成本
    
    Args:
        image_path: 图片路径
        max_size: 最大尺寸（宽或高的最大值）
        quality: JPEG质量（1-100）
    
    Returns:
        压缩后的图片字节数据
    """
    try:
        with Image.open(image_path) as img:
            # 转换为RGB模式（如果是RGBA等）
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # 计算缩放比例
            width, height = img.size
            if width > max_size or height > max_size:
                if width > height:
                    new_width = max_size
                    new_height = int(height * (max_size / width))
                else:
                    new_height = max_size
                    new_width = int(width * (max_size / height))
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # 保存为JPEG字节流
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=quality)
            return buffer.getvalue()
    except Exception as e:
        print(f"[OCR] 图片压缩失败: {e}")
        # 如果压缩失败，直接读取原文件
        with open(image_path, 'rb') as f:
            return f.read()


def image_to_base64(image_path: str) -> str:
    """
    将图片转换为Base64编码
    
    Args:
        image_path: 图片路径
    
    Returns:
        Base64编码的图片数据URL
    """
    try:
        # 压缩图片
        image_bytes = compress_image(image_path)
        # 转换为Base64
        base64_str = base64.b64encode(image_bytes).decode('utf-8')
        # 返回data URL格式
        return f"data:image/jpeg;base64,{base64_str}"
    except Exception as e:
        print(f"[OCR] 图片转Base64失败: {e}")
        raise


def extract_text_from_image(
    image_path: str,
    context: str = "",
    model: Optional[str] = None
) -> Dict[str, Any]:
    """
    从图片中提取文字
    
    Args:
        image_path: 图片路径
        context: 上下文提示（例如："这是一张股票K线图"）
        model: 模型名称（默认使用通义千问VL）
    
    Returns:
        包含识别结果的字典
        {
            "text": "识别的文字内容",
            "confidence": 0.95,  # 可选，如果模型返回
            "model": "qwen-vl-plus"
        }
    """
    import time
    start_time = time.time()
    
    try:
        print(f"[OCR] 开始识别图片: {image_path}")
        
        # 获取客户端
        client = get_vision_client()
        
        # 确定模型名称
        model_name = model or os.getenv("QWEN_VL_MODEL", "qwen-vl-plus")
        print(f"[OCR] 使用模型: {model_name}")
        
        # 转换图片为Base64
        base64_image = image_to_base64(image_path)
        print(f"[OCR] 图片已转换为Base64，大小: {len(base64_image)} 字符")
        
        # 构建提示词
        # 如果context包含用户的问题或说明，优先使用用户的说明
        if context:
            # 检查是否包含用户的问题（通常包含"?"、"帮我"、"分析"等关键词）
            if any(keyword in context for keyword in ['?', '？', '帮我', '分析', '识别', '提取', '多少', '哪个', '什么']):
                # 用户有具体问题，直接使用用户的说明作为主要提示
                prompt = f"{context}\n\n请仔细查看图片，回答用户的问题。同时识别图片中的所有文字内容，包括数字、日期、价格、成交量等关键信息。"
            else:
                # 用户只有一般说明，结合默认提示
                prompt = f"{context}\n\n请仔细识别这张图片中的所有文字内容，包括数字、日期、价格、成交量等关键信息。如果图片中包含表格，请保持表格结构。如果图片是K线图或股票相关图表，请特别关注价格、日期、成交量等数据。"
        else:
            prompt = "请仔细识别这张图片中的所有文字内容，包括数字、日期、价格、成交量等关键信息。如果图片中包含表格，请保持表格结构。如果图片是K线图或股票相关图表，请特别关注价格、日期、成交量等数据。"
        
        # 构建消息（使用OpenAI兼容的多模态格式）
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": base64_image
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ]
        
        print(f"[OCR] 正在调用视觉模型API...")
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=0.1  # 低温度以获得更准确的识别结果
        )
        
        elapsed_time = time.time() - start_time
        print(f"[OCR] API响应成功，耗时: {elapsed_time:.2f}秒")
        
        if response.choices and len(response.choices) > 0:
            text = response.choices[0].message.content or ""
            print(f"[OCR] 识别结果长度: {len(text)} 字符")
            
            return {
                "text": text,
                "model": model_name,
                "elapsed_time": elapsed_time
            }
        else:
            print(f"[OCR] 警告: 响应中没有choices")
            return {
                "text": "",
                "model": model_name,
                "elapsed_time": elapsed_time,
                "error": "模型未返回有效结果"
            }
            
    except Exception as e:
        elapsed_time = time.time() - start_time
        error_str = str(e)
        
        print(f"[OCR失败] 耗时: {elapsed_time:.2f}秒")
        print(f"[OCR失败] 错误类型: {type(e).__name__}")
        print(f"[OCR失败] 错误信息: {error_str}")
        
        return {
            "text": "",
            "model": model_name if 'model_name' in locals() else "unknown",
            "elapsed_time": elapsed_time,
            "error": error_str
        }


def analyze_stock_image(image_path: str) -> Dict[str, Any]:
    """
    专门用于股票分析场景的图片识别
    
    Args:
        image_path: 图片路径
    
    Returns:
        包含识别结果和分析的字典
    """
    context = """这是一张股票相关的图片，可能是：
1. K线图 - 请识别日期、开盘价、收盘价、最高价、最低价、成交量等关键数据
2. 财务报表 - 请提取营收、利润、增长率、每股收益等财务指标
3. 公告或新闻 - 请提取关键信息，包括日期、事件、影响等
4. 其他股票相关图表 - 请识别所有数字和关键信息

请按照以下格式输出：
- 如果是K线图，请列出关键的价格和成交量数据
- 如果是财报，请提取财务指标
- 如果是公告，请提取关键事件信息
"""
    
    result = extract_text_from_image(image_path, context)
    
    # 可以在这里添加额外的后处理逻辑
    # 例如：提取股票代码、价格区间等
    
    return result

