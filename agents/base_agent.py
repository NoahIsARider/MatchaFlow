"""
Agent基类：所有智能体的基础类
"""
from typing import List, Dict, Optional
from utils.llm_client import LLMClient
from database.shared_db import SharedDatabase


class BaseAgent:
    """
    智能体基类
    
    每个智能体具有：
    1. 角色定位和系统提示词
    2. 对话历史（短期记忆）
    3. 访问共享数据库的能力（长期记忆）
    4. 与LLM交互的能力
    """
    
    def __init__(self, role_name: str, system_prompt: str, 
                 llm_client: LLMClient, shared_db: SharedDatabase):
        """
        初始化智能体
        
        Args:
            role_name: 角色名称
            system_prompt: 系统提示词（定义角色行为）
            llm_client: LLM客户端
            shared_db: 共享数据库
        """
        self.role_name = role_name
        self.system_prompt = system_prompt
        self.llm_client = llm_client
        self.shared_db = shared_db
        
        # 短期记忆：对话历史
        self.conversation_history: List[Dict[str, str]] = []
        
        # 工作记忆：当前任务相关的临时信息
        self.working_memory: Dict = {}
        
    def think(self, user_message: str, context: Optional[str] = None,
              temperature: float = 0.7, max_tokens: int = 2000) -> str:
        """
        智能体思考并生成响应
        
        Args:
            user_message: 用户消息或任务描述
            context: 额外的上下文信息
            temperature: 生成温度
            max_tokens: 最大token数
            
        Returns:
            智能体的响应
        """
        # 构建消息列表
        messages = [{"role": "system", "content": self.system_prompt}]
        
        # 添加上下文信息
        if context:
            messages.append({"role": "system", "content": f"[上下文信息]\n{context}"})
        
        # 添加历史对话（最近的几轮）
        recent_history = self.conversation_history[-10:]  # 只保留最近10轮
        messages.extend(recent_history)
        
        # 添加当前消息
        messages.append({"role": "user", "content": user_message})
        
        # 调用LLM
        response = self.llm_client.chat(messages, temperature, max_tokens)
        
        # 更新对话历史
        self.conversation_history.append({"role": "user", "content": user_message})
        self.conversation_history.append({"role": "assistant", "content": response})
        
        return response
    
    def add_to_working_memory(self, key: str, value):
        """添加信息到工作记忆"""
        self.working_memory[key] = value
        
    def get_from_working_memory(self, key: str, default=None):
        """从工作记忆获取信息"""
        return self.working_memory.get(key, default)
    
    def clear_working_memory(self):
        """清空工作记忆"""
        self.working_memory.clear()
        
    def reset_conversation(self):
        """重置对话历史"""
        self.conversation_history.clear()
        
    def get_relevant_discussions(self) -> str:
        """从共享数据库获取相关讨论"""
        discussions = self.shared_db.get_discussions_for_agent(self.role_name)
        if not discussions:
            return "暂无相关讨论记录"
        
        result = "## 相关讨论记录\n\n"
        for d in discussions[-5:]:  # 只取最近5条
            result += f"**{d['from']} -> {d['to']}** ({d['topic']})\n{d['content']}\n\n"
        return result
    
    def communicate_with(self, other_agent_name: str, topic: str, 
                        message: str) -> str:
        """
        与另一个智能体通信
        
        Args:
            other_agent_name: 目标智能体名称
            topic: 讨论主题
            message: 消息内容
            
        Returns:
            对方的响应（需要由调用者从目标智能体获取）
        """
        # 记录到共享数据库
        self.shared_db.save_discussion(
            participants=[self.role_name, other_agent_name],
            topic=topic,
            content=message
        )
        
        print(f"[通信] {self.role_name} -> {other_agent_name}: {topic}")
        return message
    
    def __str__(self):
        return f"{self.role_name}"
