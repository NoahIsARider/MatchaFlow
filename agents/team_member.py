"""
项目组成员智能体
"""
from agents.base_agent import BaseAgent
from utils.llm_client import LLMClient
from database.shared_db import SharedDatabase
from typing import Dict, List


class TeamMemberAgent(BaseAgent):
    """
    项目组成员（Team Member）
    
    职责：
    1. 参与启动会议，提供技术意见
    2. 执行开发任务
    3. 编写代码
    4. 与项目经理沟通进展
    """
    
    def __init__(self, llm_client: LLMClient, shared_db: SharedDatabase,
                 system_prompt: str):
        super().__init__(
            role_name="项目组成员",
            system_prompt=system_prompt,
            llm_client=llm_client,
            shared_db=shared_db
        )
    
    def participate_in_kickoff(self, meeting_context: str) -> str:
        """
        参与启动会议，提供技术意见
        
        Args:
            meeting_context: 会议上下文
            
        Returns:
            发言内容
        """
        prompt = f"""项目启动会议正在进行。

{meeting_context}

作为项目组成员（开发人员），请：
1. 对技术可行性给出评估
2. 对时间和资源估算提供建议
3. 指出可能的技术风险

请简洁表达（150-200字）。
"""
        
        response = self.think(prompt, temperature=0.7)
        return response
    
    def develop_code(self, cycle: int) -> Dict[str, str]:
        """
        开发代码
        
        Args:
            cycle: 当前执行循环次数
            
        Returns:
            代码文件字典 {filename: code_content}
        """
        # 获取项目信息
        charter = self.shared_db.data.get('project_charter', '')
        scope = self.shared_db.data.get('constraints', {}).get('scope', '')
        wbs = self.shared_db.data.get('wbs', '')
        
        context = f"""
项目章程（部分）：
{charter[:300] if charter else '无'}...

范围约束：
{scope[:200] if scope else '无'}...

WBS（部分）：
{wbs[:300] if wbs else '无'}...

当前循环：{cycle}/3
"""
        
        prompt = f"""请根据项目需求开发代码。

这是第{cycle}次执行循环，请：
1. 如果是第1次循环：创建项目基础框架和核心功能
2. 如果是第2次循环：完善功能，添加更多特性
3. 如果是第3次循环：优化代码，修复问题

请生成2-3个Python代码文件，每个文件应该：
- 有清晰的文件名（如main.py, utils.py等）
- 包含必要的导入语句
- 有适当的注释
- 代码简洁但完整（每个文件50-150行）

重要：你的目标是展示项目管理过程，代码不需要非常复杂，但要体现出工作量。

请按以下格式输出：

【文件名】filename1.py
【代码】
代码内容...
【文件结束】

【文件名】filename2.py
【代码】
代码内容...
【文件结束】
"""
        
        response = self.think(prompt, context=context, temperature=0.8, max_tokens=3000)
        
        # 解析代码文件
        code_files = self._parse_code_files(response, cycle)
        
        return code_files
    
    def report_progress(self, cycle: int, code_files: Dict[str, str]) -> str:
        """
        向项目经理报告进展
        
        Args:
            cycle: 当前循环
            code_files: 已完成的代码文件
            
        Returns:
            进展报告
        """
        file_list = '\n'.join([f"- {name} ({len(content)}字符)" 
                              for name, content in code_files.items()])
        
        prompt = f"""请向项目经理报告第{cycle}次循环的工作进展。

已完成的代码文件：
{file_list}

报告应包括：
1. 完成的功能
2. 遇到的问题（如果有）
3. 下一步计划

请简洁报告（150-200字）。
"""
        
        response = self.think(prompt, temperature=0.7)
        return response
    
    def discuss_with_sponsor(self, cycle: int, sponsor_feedback: str) -> str:
        """
        与项目发起人讨论产品
        
        Args:
            cycle: 当前循环
            sponsor_feedback: 项目发起人的反馈
            
        Returns:
            回应内容
        """
        prompt = f"""项目发起人对第{cycle}次循环的产品给出了反馈：

{sponsor_feedback}

作为开发人员，请回应：
1. 对反馈的理解
2. 可以改进的地方
3. 需要的支持

请简洁回应（100-150字）。
"""
        
        response = self.think(prompt, temperature=0.7)
        return response
    
    def _parse_code_files(self, response: str, cycle: int) -> Dict[str, str]:
        """
        解析LLM生成的代码文件
        
        Args:
            response: LLM响应
            cycle: 当前循环
            
        Returns:
            代码文件字典
        """
        code_files = {}
        
        # 尝试解析格式化的响应
        parts = response.split('【文件名】')
        
        for part in parts[1:]:  # 跳过第一个空部分
            try:
                # 提取文件名
                filename_end = part.find('\n')
                if filename_end == -1:
                    continue
                    
                filename = part[:filename_end].strip()
                
                # 提取代码
                code_start = part.find('【代码】')
                code_end = part.find('【文件结束】')
                
                if code_start != -1 and code_end != -1:
                    code = part[code_start + 5:code_end].strip()
                    code_files[filename] = code
            except Exception as e:
                print(f"[警告] 解析代码文件时出错：{e}")
                continue
        
        # 如果解析失败，生成默认代码
        if not code_files:
            code_files = self._generate_default_code(cycle)
        
        return code_files
    
    def _generate_default_code(self, cycle: int) -> Dict[str, str]:
        """
        生成默认代码（当解析失败时）
        
        Args:
            cycle: 当前循环
            
        Returns:
            代码文件字典
        """
        # 获取项目信息生成更相关的默认代码
        charter = self.shared_db.data.get('project_charter', '')
        project_name = 'project'
        
        # 尝试从章程中提取项目名称
        if '项目名称' in charter:
            lines = charter.split('\n')
            for line in lines:
                if '项目名称' in line:
                    project_name = line.split('：')[-1].split(':')[-1].strip()[:20]
                    break
        
        code_files = {}
        
        # main.py
        code_files['main.py'] = f'''"""
{project_name} - 主程序
循环 {cycle}
"""

def main():
    """主函数"""
    print("欢迎使用{project_name}")
    print("当前版本：循环{cycle}")
    
    # TODO: 实现核心功能
    
if __name__ == "__main__":
    main()
'''
        
        # utils.py
        if cycle >= 2:
            code_files['utils.py'] = f'''"""
{project_name} - 工具函数
循环 {cycle}
"""

def helper_function():
    """辅助函数"""
    pass

class Helper:
    """辅助类"""
    def __init__(self):
        pass
'''
        
        # config.py
        if cycle >= 3:
            code_files['config.py'] = f'''"""
{project_name} - 配置文件
循环 {cycle}
"""

CONFIG = {{
    'version': '{cycle}.0',
    'debug': True
}}
'''
        
        return code_files
