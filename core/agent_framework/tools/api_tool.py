"""
API工具实现
"""
from typing import Dict, Any, Optional
import time
import requests
from .base import BaseTool, ToolMetadata


class APITool(BaseTool):
    """API工具 - 调用外部API"""
    
    def __init__(
        self, 
        api_endpoint: str, 
        metadata: ToolMetadata,
        method: str = "POST",
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 30
    ):
        """
        初始化API工具
        
        Args:
            api_endpoint: API端点URL
            metadata: 工具元数据
            method: HTTP方法(POST/GET)
            headers: 默认请求头
            timeout: 超时时间(秒)
        """
        super().__init__(metadata)
        self.api_endpoint = api_endpoint
        self.method = method.upper()
        self.default_headers = headers or {}
        self.timeout = timeout
    
    def execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行API工具
        
        Args:
            parameters: API请求参数
            context: 执行上下文
        
        Returns:
            执行结果
        """
        start_time = time.time()
        
        try:
            # 验证参数
            self.validate_parameters(parameters)
            
            # 合并请求头
            headers = {**self.default_headers}
            if "headers" in context:
                headers.update(context["headers"])
            
            # 发送请求
            if self.method == "GET":
                response = requests.get(
                    self.api_endpoint,
                    params=parameters,
                    headers=headers,
                    timeout=self.timeout
                )
            else:  # POST
                response = requests.post(
                    self.api_endpoint,
                    json=parameters,
                    headers=headers,
                    timeout=self.timeout
                )
            
            # 检查响应状态
            response.raise_for_status()
            
            # 解析响应
            result = response.json()
            
            # 记录执行时间
            execution_time = time.time() - start_time
            self._record_execution(execution_time)
            
            return {
                "status": "success",
                "result": result,
                "execution_time": execution_time,
                "tool_name": self.metadata.name,
                "tool_type": "api",
                "http_status": response.status_code,
                "api_endpoint": self.api_endpoint
            }
            
        except ValueError as e:
            execution_time = time.time() - start_time
            return {
                "status": "error",
                "error": f"参数验证失败: {str(e)}",
                "error_type": "ValidationError",
                "execution_time": execution_time,
                "tool_name": self.metadata.name
            }
            
        except requests.exceptions.Timeout:
            execution_time = time.time() - start_time
            return {
                "status": "error",
                "error": f"API请求超时(超过{self.timeout}秒)",
                "error_type": "TimeoutError",
                "execution_time": execution_time,
                "tool_name": self.metadata.name
            }
            
        except requests.exceptions.RequestException as e:
            execution_time = time.time() - start_time
            return {
                "status": "error",
                "error": f"API请求失败: {str(e)}",
                "error_type": "RequestError",
                "execution_time": execution_time,
                "tool_name": self.metadata.name
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            return {
                "status": "error",
                "error": str(e),
                "error_type": type(e).__name__,
                "execution_time": execution_time,
                "tool_name": self.metadata.name
            }
