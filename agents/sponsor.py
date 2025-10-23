"""
项目发起人智能体
"""
from agents.base_agent import BaseAgent
from utils.llm_client import LLMClient
from database.shared_db import SharedDatabase


class SponsorAgent(BaseAgent):
    """
    项目发起人（Project Sponsor）
    
    职责：
    1. 提出项目需求
    2. 参与项目启动会议
    3. 评审项目成果
    4. 决定是否接受交付物
    """
    
    def __init__(self, llm_client: LLMClient, shared_db: SharedDatabase, 
                 system_prompt: str):
        super().__init__(
            role_name="项目发起人",
            system_prompt=system_prompt,
            llm_client=llm_client,
            shared_db=shared_db
        )
    
    def state_requirements(self, project_idea: str = None) -> str:
        """
        陈述项目需求
        
        Args:
            project_idea: 项目想法（如果为None，则由AI自动生成）
            
        Returns:
            需求描述
        """
        if project_idea:
            prompt = f"""作为项目发起人，我有一个项目想法：

{project_idea}

请详细阐述这个项目的：
1. 业务背景和目标
2. 预期成果和交付物
3. 初步的时间和预算期望
4. 项目的价值和重要性

请以专业的方式表述，字数控制在300-500字。
"""
        else:
            prompt = """作为项目发起人，请提出一个软件项目需求。

这个项目应该：
1. 有明确的业务价值
2. 技术上可行（适合小团队开发）
3. 有清晰的交付物
4. 开发周期适中（2-3个迭代）

请详细描述：
1. 项目背景和目标
2. 预期成果
3. 初步的时间和预算期望
4. 项目价值

请以专业的方式表述，字数控制在300-500字。
"""
        
        response = self.think(prompt, temperature=0.8)
        self.add_to_working_memory('initial_requirements', response)
        return response
    
    def participate_in_kickoff(self, meeting_context: str) -> str:
        """
        参与启动会议
        
        Args:
            meeting_context: 会议上下文信息
            
        Returns:
            发言内容
        """
        prompt = f"""现在进行项目启动会议。

{meeting_context}

作为项目发起人，请：
1. 确认对需求的理解
2. 对成本、范围、时间提出合理的约束条件
3. 表达对项目的期望

请简洁表达（200字以内）。
"""
        
        response = self.think(prompt, temperature=0.7)
        return response
    
    def review_product(self, cycle: int, product_description: str, 
                      code_files: str, review_only: bool = False) -> tuple[str, bool]:
        """
        评审产品
        
        Args:
            cycle: 当前循环次数
            product_description: 产品描述
            code_files: 代码文件列表
            review_only: 是否仅提供反馈，不进行验收
            
        Returns:
            如果review_only=True，返回(反馈内容, False)
            如果review_only=False，返回(反馈内容, 是否接受)
        """
        # 获取项目章程和约束条件
        charter = self.shared_db.data.get('project_charter', '')
        constraints = self.shared_db.data.get('constraints', {})
        
        context = f"""
项目章程（部分）：
{charter[:200] if charter else '无'}...

项目约束：
- 成本：{constraints.get('cost', '未定义')}
- 范围：{constraints.get('scope', '未定义')}
- 时间：{constraints.get('schedule', '未定义')}
"""
        
        if review_only:
            # 仅提供反馈模式
            prompt = f"""现在是第{cycle}次执行控制循环（评审阶段）。

产品描述：
{product_description}

已完成的代码文件：
{code_files}

请作为项目发起人评审这个产品，提供详细的改进意见：
1. 产品当前状态如何？
2. 存在哪些问题或不足？
3. 需要如何改进？
4. 对下一阶段的期望是什么？

请给出详细的评审意见（200-300字）。
"""
            response = self.think(prompt, context=context, temperature=0.7)
            # 在仅反馈模式下，总是返回False表示不进行验收
            return response, False
        else:
            # 验收模式
            prompt = f"""现在是第{cycle}次执行控制循环（验收阶段）。

产品描述：
{product_description}

已完成的代码文件：
{code_files}

请作为项目发起人评审这个产品，并决定是否接受：
1. 产品是否满足需求？
2. 质量是否达到预期？
3. 是否还有需要改进的地方？

然后做出最终决策：
- 如果产品满足要求，请明确说明"【接受】"
- 如果产品不满足要求，请明确说明"【拒绝】"

请先给出评审意见，然后在最后一行明确说明是否接受。
"""
            response = self.think(prompt, context=context, temperature=0.7)
            
            # 判断是否接受
            accepted = '【接受】' in response or '接受' in response or \
                     '可以验收' in response or '通过' in response
            
            return response, accepted
    
    def final_acceptance(self, deliverables_summary: str) -> str:
        """
        最终验收
        
        Args:
            deliverables_summary: 交付物摘要
            
        Returns:
            验收意见
        """
        prompt = f"""项目已完成，以下是交付物摘要：

{deliverables_summary}

作为项目发起人，请对项目进行最终验收：
1. 项目是否达到预期目标？
2. 交付物是否完整？
3. 对项目团队的评价
4. 项目的价值实现情况

请给出最终验收意见（200-300字）。
"""
        
        response = self.think(prompt, temperature=0.7)
        return response
