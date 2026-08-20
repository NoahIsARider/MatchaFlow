"""
DAO 治理模拟 - 智能体定义

将原 PM 模式的 Sponsor/Manager/Team Member 映射为：
- ProposerAgent（治理提案人）
- GovernorAgent（治理协调员）
- MemberAgent（社区成员）
"""
from typing import Dict, Optional, Tuple

from agents.base_agent import BaseAgent
from utils.llm_client import LLMClient
from database.shared_db import SharedDatabase


class ProposerAgent(BaseAgent):
    """治理提案人：提出提案、参与讨论、评审执行结果、最终验收"""

    def __init__(self, llm_client: LLMClient, shared_db: SharedDatabase,
                 system_prompt: str, calibration_prompt: str = ''):
        super().__init__('治理提案人', system_prompt, llm_client, shared_db)
        self.calibration_prompt = calibration_prompt

    def state_proposal(self, proposal_idea: Optional[str] = None) -> str:
        """陈述治理提案需求"""
        if proposal_idea:
            prompt = f"""请基于以下治理提案构想，正式陈述你的提案（动机、目标、期望效果）：
提案构想：{proposal_idea}

请给出清晰的提案陈述（200-300字），说明这个提案要解决什么治理问题、如何解决。
"""
        else:
            prompt = """你观察到社区治理存在一些问题，请主动提出一个治理改进提案
（例如：投票门槛调整、委托机制引入、激励分配改革、透明度提升等）。

请给出清晰的提案陈述（200-300字），说明这个提案要解决什么治理问题、如何解决。"""
        return self.think(prompt, context=self.calibration_prompt, temperature=0.7)

    def participate_in_discussion(self, meeting_context: str) -> str:
        """参与社区讨论"""
        prompt = f"""以下是治理讨论的上下文：

{meeting_context}

作为治理提案人，请发言说明：
1. 提案对社区的价值
2. 你关心的关键治理参数
3. 对预算/范围/时间线的期望
请给出专业、有说服力的发言（150-250字）。"""
        return self.think(prompt, context=self.calibration_prompt, temperature=0.7)

    def review_execution(self, cycle: int, execution_summary: str,
                         review_only: bool = False) -> Tuple[str, bool]:
        """评审治理执行结果"""
        proposal_book = self.shared_db.data.get('documents', {}).get('治理提案书', '')
        parameters = self.shared_db.data.get('documents', {}).get('治理参数', '')

        context = f"""
治理提案书（部分）：
{proposal_book[:200] if proposal_book else '无'}...

治理三大约束：
{parameters[:200] if parameters else '未定义'}
"""

        if review_only:
            prompt = f"""现在是第{cycle}次执行-监控循环（评审阶段）。

治理执行情况：
{execution_summary}

请作为治理提案人评审治理执行结果，提供详细改进意见：
1. 执行情况是否符合提案目标？
2. 存在哪些问题或不足？
3. 需要如何改进？
4. 对下一阶段的期望？

请给出详细的评审意见（200-300字）。"""
            response = self.think(prompt, context=context, temperature=0.7)
            return response, False
        else:
            prompt = f"""现在是第{cycle}次执行-监控循环（验收阶段）。

治理执行情况：
{execution_summary}

请作为治理提案人评审治理执行结果，并决定是否接受：
1. 执行结果是否达到提案目标？
2. 治理质量是否达到预期（参与度、公平性、透明度）？
3. 是否还有需要改进的地方？

然后做出最终决策：
- 如果接受，请明确说明"【接受】"
- 如果拒绝，请明确说明"【拒绝】"

请先给出评审意见，最后一行明确说明是否接受。"""
            response = self.think(prompt, context=context, temperature=0.7)
            accepted = ('【接受】' in response or '接受' in response
                        or '可以验收' in response or '通过' in response)
            return response, accepted

    def final_acceptance(self, deliverables_summary: str) -> str:
        """最终验收"""
        prompt = f"""治理项目已全部完成，交付物如下：

{deliverables_summary}

请作为治理提案人给出最终验收意见：
1. 提案目标是否全部实现？
2. 治理执行过程是否规范？
3. 社区反馈如何？
4. 最终结论（通过/不通过）与后续建议。

请给出完整的验收意见（200-300字）。"""
        return self.think(prompt, context=self.calibration_prompt, temperature=0.7)


class GovernorAgent(BaseAgent):
    """治理协调员：起草提案书、主持讨论、制定治理设计、监控分析、复盘"""

    def __init__(self, llm_client: LLMClient, shared_db: SharedDatabase,
                 system_prompt: str, calibration_prompt: str = ''):
        super().__init__('治理协调员', system_prompt, llm_client, shared_db)
        self.calibration_prompt = calibration_prompt

    def draft_proposal_book(self, proposal_statement: str) -> str:
        """起草治理提案书"""
        prompt = f"""提案人的提案陈述如下：

{proposal_statement}

请作为治理协调员起草一份规范的治理提案书，包含：
1. 提案背景与动机
2. 提案目标
3. 拟议的治理机制（投票/激励/委托等）
4. 预期影响与风险
5. 需要的社区共识

请给出完整的治理提案书（400-600字）。"""
        return self.think(prompt, context=self.calibration_prompt, temperature=0.7)

    def facilitate_discussion(self, proposer_input: str, member_input: str) -> Dict[str, str]:
        """主持讨论，确定治理三大约束（预算/范围/时间线）"""
        prompt = f"""社区讨论发言记录：

【治理提案人】
{proposer_input}

【社区成员】
{member_input}

请作为治理协调员主持讨论，确定治理执行的三大约束：

约束1 - 治理预算（budget）：执行提案所需的资源/资金规模
约束2 - 治理范围（scope）：提案覆盖的治理模块/社区范围
约束3 - 时间线（timeline）：执行计划与关键里程碑

请严格按以下格式输出（每行一个约束，键: 值）：

budget: <治理预算描述>
scope: <治理范围描述>
timeline: <时间线描述>"""
        response = self.think(prompt, context=self.calibration_prompt, temperature=0.7)
        return self._parse_parameters(response)

    def create_governance_design(self, parameters: Dict[str, str]) -> str:
        """制定治理设计书"""
        param_text = '\n'.join(f'- {k}: {v}' for k, v in parameters.items())
        prompt = f"""治理三大约束：
{param_text}

请作为治理协调员制定完整的治理设计书，包含：
1. 投票机制设计（投票权、门槛、时长、法定人数）
2. 参数设定（激励分配、委托上限等）
3. 执行计划（按时间线的关键步骤）
4. 安全与反集中措施（结合社区集中度）

请给出完整的治理设计书（400-600字）。"""
        return self.think(prompt, context=self.calibration_prompt, temperature=0.7)

    def perform_monitoring_analysis(self, cycle: int) -> Dict:
        """治理监控：分析参与度/集中度指标，评估执行质量"""
        execution = self.shared_db.data['execution_cycles']
        actions = self.shared_db.data.get('documents', {}).get(f'执行行动_第{cycle}轮', '')
        prompt = f"""第{cycle}轮治理执行情况（成员行动记录）：

{actions[:500] if actions else '（无行动记录）'}

请作为治理协调员进行治理监控分析，输出以下指标：

指标1 - participation（参与度）：社区参与程度（高/中/低）与理由
指标2 - concentration（集中度）：决策集中程度（高/中/低）与理由
指标3 - execution_quality（执行质量）：治理行动的执行质量（0-100分）
指标4 - verdict（评估结论）：本轮治理执行的总体结论
指标5 - recommendation（调整建议）：是否需要调整治理参数及如何调整

请严格按以下格式输出（每行一个指标，键: 值）：

participation: <高/中/低>
concentration: <高/中/低>
execution_quality: <0-100的数字>
verdict: <总体结论>
recommendation: <调整建议>"""
        response = self.think(prompt, context=self.calibration_prompt, temperature=0.7)
        return self._parse_monitoring(response)

    def update_design(self, cycle: int, feedback: str) -> Dict[str, str]:
        """根据反馈更新治理设计"""
        prompt = f"""第{cycle}轮评审反馈如下：

{feedback}

请作为治理协调员根据反馈更新治理设计，输出调整摘要。

请严格按以下格式输出：

update_summary: <调整摘要，说明改了什么参数/机制及原因>"""
        response = self.think(prompt, context=self.calibration_prompt, temperature=0.7)
        summary = response.split('update_summary:', 1)[-1].strip() if 'update_summary:' in response else response
        return {'update_summary': summary}

    def compile_review_report(self, db_data: Dict, project_code: str) -> str:
        """编制治理复盘报告"""
        cycle_feedbacks = db_data.get('cycle_feedbacks', [])
        discussions = db_data.get('discussions', [])
        feedback_lines = '\n'.join(
            f"- 第{f['cycle']}轮: {'接受' if f['accepted'] else '反馈'}"
            for f in cycle_feedbacks
        ) or '- 无'
        prompt = f"""请作为治理协调员编制完整的治理复盘报告，包含：
1. 提案执行总览（项目代号：{project_code}）
2. 执行-监控循环回顾：
{feedback_lines}
3. 治理指标总结（参与度/集中度/执行质量）
4. 经验与教训
5. 对社区治理的长期建议

请给出完整的复盘报告（400-600字）。"""
        return self.think(prompt, context=self.calibration_prompt, temperature=0.7)

    def _parse_parameters(self, response: str) -> Dict[str, str]:
        """解析治理三大约束"""
        params = {}
        for key in ('budget', 'scope', 'timeline'):
            for line in response.splitlines():
                line = line.strip()
                if line.lower().startswith(f'{key}:'):
                    params[key] = line.split(':', 1)[1].strip()
                    break
            params.setdefault(key, '未定义')
        return params

    def _parse_monitoring(self, response: str) -> Dict:
        """解析监控指标"""
        parsed = {}
        for key in ('participation', 'concentration', 'execution_quality',
                    'verdict', 'recommendation'):
            for line in response.splitlines():
                line = line.strip()
                if line.lower().startswith(f'{key}:'):
                    parsed[key] = line.split(':', 1)[1].strip()
                    break
            parsed.setdefault(key, 'N/A')
        try:
            parsed['execution_quality'] = float(str(parsed['execution_quality']).replace('分', '').strip())
        except (ValueError, TypeError):
            parsed['execution_quality'] = 0.0
        return parsed


class MemberAgent(BaseAgent):
    """社区成员：参与讨论、模拟执行治理行动、回应反馈"""

    def __init__(self, llm_client: LLMClient, shared_db: SharedDatabase,
                 system_prompt: str, calibration_prompt: str = ''):
        super().__init__('社区成员', system_prompt, llm_client, shared_db)
        self.calibration_prompt = calibration_prompt

    def participate_in_discussion(self, meeting_context: str) -> str:
        """参与社区讨论"""
        prompt = f"""以下是治理讨论的上下文：

{meeting_context}

作为社区成员，请发言说明：
1. 你对这个提案的态度（支持/观望/反对）及理由
2. 你关心的利益点
3. 你希望治理设计包含什么

请给出真实、具体的发言（150-250字）。"""
        return self.think(prompt, context=self.calibration_prompt, temperature=0.7)

    def execute_actions(self, cycle: int) -> Dict[str, str]:
        """模拟执行治理行动（投票/委托/链上操作等）"""
        design = self.shared_db.data.get('documents', {}).get('治理设计书', '')
        prompt = f"""治理设计书（部分）：

{design[:300] if design else '（暂无）'}...

这是第{cycle}轮治理执行。请作为社区成员模拟执行 3-5 项具体治理行动
（如：对某项动议投票、委托投票权、参与社区讨论、执行链上操作等），
每项行动需包含：行动名称、具体内容、影响。

请严格按以下格式输出（每行一个行动）：

行动1: <行动名称> | <具体内容> | <影响>
行动2: <行动名称> | <具体内容> | <影响>
..."""
        response = self.think(prompt, context=self.calibration_prompt, temperature=0.7)
        return self._parse_actions(response)

    def report_progress(self, cycle: int, actions: Dict[str, str]) -> str:
        """汇报执行进展"""
        action_lines = '\n'.join(f'- {name}: {content}' for name, content in actions.items())
        prompt = f"""第{cycle}轮治理行动记录：

{action_lines}

请作为社区成员向治理协调员汇报本轮执行进展：
1. 完成了哪些行动
2. 遇到什么困难
3. 对治理机制的感受

请给出汇报（150-250字）。"""
        return self.think(prompt, context=self.calibration_prompt, temperature=0.7)

    def discuss_with_proposer(self, cycle: int, proposer_feedback: str) -> str:
        """回应提案人反馈"""
        prompt = f"""治理提案人对第{cycle}轮执行的反馈：

{proposer_feedback}

请作为社区成员回应提案人的反馈：
1. 是否认同反馈意见
2. 说明执行中的实际情况
3. 提出改进承诺

请给出回应（150-250字）。"""
        return self.think(prompt, context=self.calibration_prompt, temperature=0.7)

    def _parse_actions(self, response: str) -> Dict[str, str]:
        """解析行动记录"""
        actions = {}
        for line in response.splitlines():
            line = line.strip()
            if '行动' in line and '|' in line:
                parts = line.split('|')
                if len(parts) >= 2:
                    name = parts[0].split(':', 1)[-1].strip()
                    actions[name] = ' | '.join(p.strip() for p in parts[1:])
        if not actions:
            actions['行动1'] = f'参与社区讨论与投票 | 对提案相关动议投出赞成票 | 推动提案落地'
        return actions
