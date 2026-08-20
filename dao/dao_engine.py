"""
DAO 治理模拟 - 工作流引擎

六阶段：
1. 提案发起（Proposal）：Proposer 陈述提案 -> Governor 起草治理提案书
2. 社区讨论（Discussion）：三方讨论 -> 确定治理三大约束（预算/范围/时间线）
3. 治理设计（Design）：Governor 制定治理设计书
4&5. 执行-监控循环（Execution & Monitoring，最多 DAO_MAX_CYCLES 轮）：
     Member 模拟执行治理行动 -> Governor 监控分析 -> Proposer 评审/验收
6. 治理复盘（Review）：Governor 编制复盘报告 -> Proposer 最终验收
"""
import os
from datetime import datetime
from typing import Dict, Optional

from dao.dao_agents import ProposerAgent, GovernorAgent, MemberAgent
from dao.dao_calibration import load_calibration, calibration_prompt
from dao.dao_config import (DAO_PHASES, DAO_MAX_CYCLES, DAO_SIMULATION_BASE_PATH,
                            DAO_DELIVERABLES_FOLDER, DEFAULT_CALIBRATION)
from database.shared_db import SharedDatabase
from utils.llm_client import LLMClient
from utils.document_generator import DocumentGenerator


class DAOEngine:
    """DAO 治理模拟引擎"""

    def __init__(self, project_code: str, llm_config: dict,
                 agent_prompts: dict, calibration: Optional[Dict] = None,
                 proposal_idea: Optional[str] = None, max_cycles: int = DAO_MAX_CYCLES):
        self.project_code = project_code
        self.proposal_idea = proposal_idea
        self.max_cycles = max_cycles

        # 校准参数（未提供时用默认）
        self.calibration = calibration or dict(DEFAULT_CALIBRATION)
        cal_prompt = calibration_prompt(self.calibration)

        # 共享数据库 / LLM 客户端
        self.shared_db = SharedDatabase(project_code)
        self.llm_client = LLMClient(
            base_url=llm_config['base_url'],
            api_key=llm_config['api_key'],
            model=llm_config['model']
        )

        # 三个 DAO 智能体
        self.proposer = ProposerAgent(self.llm_client, self.shared_db,
                                      agent_prompts['PROPOSER'], cal_prompt)
        self.governor = GovernorAgent(self.llm_client, self.shared_db,
                                      agent_prompts['GOVERNOR'], cal_prompt)
        self.member = MemberAgent(self.llm_client, self.shared_db,
                                  agent_prompts['MEMBER'], cal_prompt)

        # 文档生成器
        self.deliverables_path = os.path.join(
            DAO_SIMULATION_BASE_PATH, project_code, DAO_DELIVERABLES_FOLDER)
        self.doc_generator = DocumentGenerator(self.deliverables_path)

        print(f"\n{'='*60}")
        print(f"DAO 治理模拟引擎已初始化 - 提案代号：{project_code}")
        print(f"校准数据：{self.calibration.get('source', 'default')}")
        print(f"交付物路径：{self.deliverables_path}")
        print(f"{'='*60}\n")

    # ----------------------------------------------------------
    def run(self):
        """运行完整的 DAO 治理生命周期"""
        try:
            print(f"\n{'='*60}\n开始执行 DAO 治理模拟\n{'='*60}\n")

            # 阶段1：提案发起
            self.phase_proposal()

            # 阶段2：社区讨论
            self.phase_discussion()

            # 阶段3：治理设计
            self.phase_design()

            # 阶段4&5：执行-监控循环
            print(f"\n[系统] 执行-监控循环说明：")
            print(f"  - 前2轮为强制 review-only 模式（只提意见，不验收）")
            print(f"  - 从第3轮开始可以进行正式验收")
            print(f"  - 最多执行 {self.max_cycles} 轮\n")

            accepted = False
            for cycle in range(1, self.max_cycles + 1):
                self.shared_db.start_execution_cycle(cycle)

                self.phase_execution(cycle)
                self.phase_monitoring(cycle)

                if cycle < 3:
                    print(f"\n[系统] 第{cycle}轮（review-only 模式），提案人只提意见")
                    feedback, _ = self.proposer.review_execution(
                        cycle, self._execution_summary(cycle), review_only=True)
                    print(f"\n[提案人] 评审意见已记录\n")
                    self.shared_db.update_cycle_feedback(cycle, feedback, False)
                    self._save_discussion('治理提案人', '社区团队',
                                          f'第{cycle}轮评审意见', feedback)
                    if cycle == 2:
                        print("[系统] 已完成2轮 review-only，下一轮将正式验收\n")
                else:
                    print(f"\n[系统] 第{cycle}轮（验收模式）")
                    feedback, accepted = self.proposer.review_execution(
                        cycle, self._execution_summary(cycle), review_only=False)
                    print(f"\n[提案人] 决策：{'【接受】' if accepted else '【拒绝】'}\n")
                    self.shared_db.update_cycle_feedback(cycle, feedback, accepted)
                    self._save_discussion('治理提案人', '社区团队',
                                          f'第{cycle}轮评审', feedback)

                    if accepted:
                        print(f"[提案人] ✓ 接受第{cycle}轮成果，进入治理复盘阶段\n")
                        break
                    if cycle < self.max_cycles:
                        print(f"[系统] ✗ 被拒绝，剩余 {self.max_cycles - cycle} 轮\n")
                        member_response = self.member.discuss_with_proposer(cycle, feedback)
                        print(f"[成员] {member_response}\n")
                        self._save_discussion('社区成员', '治理提案人',
                                              f'第{cycle}轮改进讨论', member_response)

            # 阶段6：治理复盘
            self.phase_review(accepted)

            print(f"\n{'='*60}\nDAO 治理模拟执行完毕\n{'='*60}\n")

        except Exception as e:
            print(f"\n[错误] DAO 工作流执行出错：{e}")
            import traceback
            traceback.print_exc()

    # ----------------------------------------------------------
    def phase_proposal(self):
        """阶段1：提案发起"""
        print(f"\n{'='*60}\n阶段 1/6: {DAO_PHASES['PROPOSAL']}\n{'='*60}\n")

        print("[1.1] 治理提案人陈述提案...")
        statement = self.proposer.state_proposal(self.proposal_idea)
        print(f"\n提案陈述：\n{statement}\n")

        print("[1.2] 治理协调员起草治理提案书...")
        book = self.governor.draft_proposal_book(statement)
        print(f"\n治理提案书：\n{book}\n")

        self.shared_db.save_document('治理提案书', book)
        self.doc_generator.save_document('治理提案书.md', f"# 治理提案书\n\n{book}\n")
        print(f"[完成] {DAO_PHASES['PROPOSAL']} 阶段完成\n")

    def phase_discussion(self):
        """阶段2：社区讨论"""
        print(f"\n{'='*60}\n阶段 2/6: {DAO_PHASES['DISCUSSION']}\n{'='*60}\n")

        book = self.shared_db.data['documents'].get('治理提案书', '')
        meeting_context = f"治理提案书已起草：\n{book[:300]}...\n\n现在进行社区讨论，确定治理预算、范围和时间线。"

        print("[2.1] 治理提案人发言...")
        proposer_input = self.proposer.participate_in_discussion(meeting_context)
        print(f"\n提案人：\n{proposer_input}\n")

        print("[2.2] 社区成员发言...")
        member_input = self.member.participate_in_discussion(meeting_context)
        print(f"\n成员：\n{member_input}\n")

        print("[2.3] 治理协调员总结，确定治理三大约束...")
        parameters = self.governor.facilitate_discussion(proposer_input, member_input)
        print(f"\n治理三大约束：")
        print(f"预算：{parameters.get('budget', '未定义')}")
        print(f"范围：{parameters.get('scope', '未定义')}")
        print(f"时间线：{parameters.get('timeline', '未定义')}\n")

        param_doc = (f"## 治理三大约束\n\n"
                     f"- 治理预算：{parameters.get('budget', '未定义')}\n"
                     f"- 治理范围：{parameters.get('scope', '未定义')}\n"
                     f"- 时间线：{parameters.get('timeline', '未定义')}")
        self.shared_db.save_document('治理参数', param_doc)
        self.doc_generator.save_document('治理参数.md', f"# 治理参数\n\n{param_doc}\n")

        minutes = f"## 参会人员发言\n\n### 治理提案人\n{proposer_input}\n\n### 社区成员\n{member_input}\n\n### 治理协调员总结\n{param_doc}"
        self.shared_db.save_meeting_record(DAO_PHASES['DISCUSSION'], minutes)
        self.doc_generator.save_document('会议记录_社区讨论.md', f"# 会议记录 - {DAO_PHASES['DISCUSSION']}\n\n{minutes}\n")
        print(f"[完成] {DAO_PHASES['DISCUSSION']} 阶段完成\n")

    def phase_design(self):
        """阶段3：治理设计"""
        print(f"\n{'='*60}\n阶段 3/6: {DAO_PHASES['DESIGN']}\n{'='*60}\n")

        print("[3.1] 治理协调员制定治理设计书...")
        design = self.governor.create_governance_design(
            self._parse_parameters_from_doc())
        print(f"\n治理设计书：\n{design}\n")

        self.shared_db.save_document('治理设计书', design)
        self.doc_generator.save_document('治理设计书.md', f"# 治理设计书\n\n{design}\n")
        print(f"[完成] {DAO_PHASES['DESIGN']} 阶段完成\n")

    def phase_execution(self, cycle: int):
        """阶段4：提案执行"""
        print(f"\n{'='*60}\n阶段 4/6: {DAO_PHASES['EXECUTION']} (轮次 {cycle}/{self.max_cycles})\n{'='*60}\n")

        print(f"[4.{cycle}.1] 社区成员模拟执行治理行动...")
        actions = self.member.execute_actions(cycle)

        action_doc = '\n'.join(f'- {name}: {content}' for name, content in actions.items())
        print(f"\n治理行动：\n{action_doc}\n")

        self.shared_db.save_document(f'执行行动_第{cycle}轮', action_doc)
        self.doc_generator.save_document(f'执行行动_第{cycle}轮.md', f"# 治理行动（第{cycle}轮）\n\n{action_doc}\n")

        print(f"[4.{cycle}.2] 社区成员汇报执行进展...")
        progress = self.member.report_progress(cycle, actions)
        print(f"\n进展汇报：\n{progress}\n")

        self._save_discussion('社区成员', '治理协调员', f'第{cycle}轮进展汇报', progress)
        self.shared_db.save_execution_cycle(cycle, 'execution', {
            'actions': actions, 'output': f"行动：\n{action_doc}\n\n汇报：\n{progress}"})
        print(f"[完成] {DAO_PHASES['EXECUTION']} 阶段（轮次{cycle}）完成\n")

    def phase_monitoring(self, cycle: int):
        """阶段5：治理监控"""
        print(f"\n{'='*60}\n阶段 5/6: {DAO_PHASES['MONITORING']} (轮次 {cycle}/{self.max_cycles})\n{'='*60}\n")

        print(f"[5.{cycle}.1] 治理协调员进行治理监控分析...")
        metrics = self.governor.perform_monitoring_analysis(cycle)

        print(f"\n监控指标：")
        print(f"  参与度：{metrics.get('participation', 'N/A')}")
        print(f"  集中度：{metrics.get('concentration', 'N/A')}")
        print(f"  执行质量：{metrics.get('execution_quality', 0):.1f}/100")
        print(f"  结论：{metrics.get('verdict', 'N/A')}")
        print(f"  建议：{metrics.get('recommendation', 'N/A')}\n")

        self.shared_db.save_document(f'监控报告_第{cycle}轮',
                                     f"参与度：{metrics.get('participation')}\n集中度：{metrics.get('concentration')}\n执行质量：{metrics.get('execution_quality')}\n结论：{metrics.get('verdict')}\n建议：{metrics.get('recommendation')}")
        self.doc_generator.save_document(f'监控报告_第{cycle}轮.md', f"# 治理监控报告（第{cycle}轮）\n\n{metrics.get('verdict', '')}\n\n## 指标\n- 参与度: {metrics.get('participation')}\n- 集中度: {metrics.get('concentration')}\n- 执行质量: {metrics.get('execution_quality')}/100\n\n## 建议\n{metrics.get('recommendation', '')}\n")

        self.shared_db.save_execution_cycle(cycle, 'monitoring', metrics)

        if cycle > 1 and self.shared_db.data['cycle_feedbacks']:
            print(f"[5.{cycle}.2] 治理协调员根据反馈更新治理设计...")
            last_feedback = self.shared_db.data['cycle_feedbacks'][-1].get('feedback', '')
            result = self.governor.update_design(cycle, last_feedback)
            print(f"\n设计更新：\n{result['update_summary']}\n")

        print(f"[完成] {DAO_PHASES['MONITORING']} 阶段（轮次{cycle}）完成\n")

    def phase_review(self, accepted: bool):
        """阶段6：治理复盘"""
        print(f"\n{'='*60}\n阶段 6/6: {DAO_PHASES['REVIEW']}\n{'='*60}\n")

        print("[6.1] 导出治理数据...")
        db_export_path = os.path.join(self.deliverables_path, 'dao_data.json')
        self.shared_db.export_to_file(db_export_path)

        print("[6.2] 治理协调员编制治理复盘报告...")
        report = self.governor.compile_review_report(self.shared_db.data, self.project_code)
        print(f"\n复盘报告：\n{report}\n")

        self.shared_db.save_document('治理复盘报告', report)
        self.doc_generator.save_document('治理复盘报告.md', f"# 治理复盘报告\n\n{report}\n")

        print("[6.3] 治理提案人最终验收...")
        deliverables_summary = f"""
交付物清单：
- 治理提案书
- 社区讨论会议记录
- 治理设计书
- 治理行动记录 {len([k for k in self.shared_db.data['documents'] if k.startswith('执行行动')])} 轮
- 治理监控报告 {len([k for k in self.shared_db.data['documents'] if k.startswith('监控报告')])} 份
- 治理复盘报告
- 治理数据库（JSON 格式）
"""
        final_opinion = self.proposer.final_acceptance(deliverables_summary)
        print(f"\n最终验收意见：\n{final_opinion}\n")

        self.shared_db.save_document('最终验收意见', final_opinion)
        acceptance_doc = f"""# 治理项目最终验收意见

{final_opinion}

---

**治理提案人签字：** ____________

**日期：** {datetime.now().strftime('%Y-%m-%d')}
"""
        self.doc_generator.save_document('最终验收意见.md', acceptance_doc)

        print(f"[完成] {DAO_PHASES['REVIEW']} 阶段完成\n")
        self._print_summary(accepted)

    # ----------------------------------------------------------
    def _execution_summary(self, cycle: int) -> str:
        """汇总第 cycle 轮的执行结果供评审"""
        docs = self.shared_db.data['documents']
        actions = docs.get(f'执行行动_第{cycle}轮', '（无行动记录）')
        monitor = docs.get(f'监控报告_第{cycle}轮', '（无监控报告）')
        return f"## 第{cycle}轮治理行动\n{actions}\n\n## 第{cycle}轮监控报告\n{monitor}"

    def _parse_parameters_from_doc(self) -> Dict[str, str]:
        """从已保存的治理参数文档解析三大约束"""
        doc = self.shared_db.data['documents'].get('治理参数', '')
        params = {}
        for key, label in (('budget', '治理预算'), ('scope', '治理范围'), ('timeline', '时间线')):
            for line in doc.splitlines():
                if f'{label}：' in line:
                    params[key] = line.split('：', 1)[1].strip()
                    break
            params.setdefault(key, '未定义')
        return params

    def _save_discussion(self, frm: str, to: str, topic: str, content: str):
        """保存讨论记录"""
        self.shared_db.save_discussion([frm, to], topic, content)

    def _print_summary(self, accepted: bool):
        """打印 DAO 模拟总结"""
        data = self.shared_db.data
        print(f"\n{'='*60}\nDAO 治理模拟总结\n{'='*60}")
        print(f"最终状态：{'✅ 提案被接受' if accepted else '⚠️ 达到最大轮次（未验收）'}")
        print(f"治理提案书长度: {len(data['documents'].get('治理提案书', ''))} 字符")
        print(f"讨论记录数量: {len(data['discussions'])} 条")
        print(f"会议记录数量: {len(data['meeting_records'])} 份")
        print(f"执行-监控轮次: {len([c for c in data['execution_cycles'] if c['phase'] == 'execution'])} 轮")
        print(f"评审反馈数量: {len(data['cycle_feedbacks'])} 条")
        print(f"治理文档数量: {len(data['documents'])} 份")
        print(f"校准数据源: {self.calibration.get('source', 'default')}")
        print(f"\n所有交付物已保存到：{self.deliverables_path}")
        print(f"{'='*60}\n")
