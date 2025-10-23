"""
LLM客户端：封装对外部大模型的调用
"""
from openai import OpenAI
from typing import List, Dict
import time


class LLMClient:
    """大模型客户端，使用OpenAI兼容接口"""
    
    def __init__(self, base_url: str, api_key: str, model: str):
        self.client = OpenAI(
            base_url=base_url,
            api_key=api_key
        )
        self.model = model
        
    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.7, 
             max_tokens: int = 2000) -> str:
        """
        发送聊天请求到大模型
        
        Args:
            messages: 消息列表，格式为 [{"role": "user/assistant/system", "content": "..."}]
            temperature: 温度参数，控制随机性
            max_tokens: 最大生成token数
            
        Returns:
            模型的响应文本
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"[LLM调用错误] {str(e)}")
            # 如果API调用失败，返回一个默认响应
            return f"[模拟响应] 由于API调用失败，这是一个模拟响应。错误信息：{str(e)}"
    
    def chat_with_retry(self, messages: List[Dict[str, str]], max_retries: int = 3,
                       temperature: float = 0.7, max_tokens: int = 2000) -> str:
        """
        带重试机制的聊天请求
        """
        for attempt in range(max_retries):
            try:
                return self.chat(messages, temperature, max_tokens)
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"[LLM调用失败] 尝试 {attempt + 1}/{max_retries}，等待重试...")
                    time.sleep(2 ** attempt)  # 指数退避
                else:
                    print(f"[LLM调用失败] 已达最大重试次数")
                    raise e
