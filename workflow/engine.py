"""
工作流引擎：控制项目各阶段的执行
"""
import os
from datetime import datetime
from typing import Optional

from agents.sponsor import SponsorAgent
from agents.manager import ManagerAgent
from agents.team_member import TeamMemberAgent
from database.shared_db import SharedDatabase
from utils.llm_client import LLMClient
from utils.document_generator import DocumentGenerator
from config import PHASES, MAX_EXECUTION_CYCLES, SIMULATION_BASE_PATH, DELIVERABLES_FOLDER


class WorkflowEngine:
    """
    工作流引擎，控制项目的六个阶段：
    1. 预启动（Pre-initiation）
    2. 启动（Initiation）
    3. 计划（Planning）
    4. 执行（Execution）
    5. 控制（Control）
    6. 结束（Closure）
    """
    
    def __init__(self, project_code: str, llm_config: dict, 
                 agent_prompts: dict, project_idea: Optional[str] = None):
        """
        初始化工作流引擎
        
        Args:
            project_code: 项目代号
            llm_config: LLM配置
            agent_prompts: Agent提示词配置
            project_idea: 项目创意（可选）
        """
        self.project_code = project_code
        self.project_idea = project_idea
        
        # 初始化共享数据库
        self.shared_db = SharedDatabase(project_code)
        
        # 初始化LLM客户端
        self.llm_client = LLMClient(
            base_url=llm_config['base_url'],
            api_key=llm_config['api_key'],
            model=llm_config['model']
        )
        
        # 初始化三个智能体
        self.sponsor = SponsorAgent(
            llm_client=self.llm_client,
            shared_db=self.shared_db,
            system_prompt=agent_prompts['SPONSOR']
        )
        
        self.manager = ManagerAgent(
            llm_client=self.llm_client,
            shared_db=self.shared_db,
            system_prompt=agent_prompts['MANAGER']
        )
        
        self.team_member = TeamMemberAgent(
            llm_client=self.llm_client,
            shared_db=self.shared_db,
            system_prompt=agent_prompts['TEAM_MEMBER']
        )
        
        # 初始化文档生成器
        self.deliverables_path = os.path.join(
            SIMULATION_BASE_PATH, 
            project_code, 
            DELIVERABLES_FOLDER
        )
        self.doc_generator = DocumentGenerator(self.deliverables_path)
        
        print(f"\n{'='*60}")
        print(f"工作流引擎已初始化 - 项目代号：{project_code}")
        print(f"交付物路径：{self.deliverables_path}")
        print(f"{'='*60}\n")
    
    def run(self):
        """运行完整的项目生命周期"""
        try:
            print(f"\n{'='*60}")
            print(f"开始执行项目生命周期")
            print(f"{'='*60}\n")
            
            # 阶段1：预启动
            self.phase_pre_initiation()
            
            # 阶段2：启动
            self.phase_initiation()
            
            # 阶段3：计划
            self.phase_planning()
            
            # 阶段4&5：执行与控制（循环）
            accepted = False
            print(f"\n[系统] 执行-控制循环说明：")
            print(f"  - 前2次循环为强制review-only模式（只提意见，不验收）")
            print(f"  - 从第3次循环开始可以进行正式验收")
            print(f"  - 最多可以执行 {MAX_EXECUTION_CYCLES} 次循环\n")
            
            for cycle in range(1, MAX_EXECUTION_CYCLES + 1):
                self.shared_db.start_execution_cycle(cycle)
                
                # 执行阶段
                self.phase_execution(cycle)
                
                # 控制阶段
                self.phase_control(cycle)
                
                # 获取项目发起人反馈
                if cycle < 3:  # 前两次循环只收集反馈，不进行验收
                    print(f"\n[系统] 当前是第{cycle}次迭代（review-only模式），项目发起人将只提意见，不进行验收")
                    feedback = self.get_sponsor_review_only(cycle)
                    print(f"\n[项目] 项目发起人反馈意见已记录，继续下一次迭代")
                    if cycle == 2:  # 第二次迭代后提示下次可以验收
                        print("\n[系统] 已完成2次review-only循环，下次迭代将进行正式验收")
                else:
                    # 第三次及以后的迭代进行正式验收
                    print(f"\n[系统] 当前是第{cycle}次迭代（验收模式），项目发起人可以选择接受或拒绝")
                    accepted = self.get_sponsor_feedback(cycle)
                    
                    if accepted:
                        print(f"\n[项目] ✓ 项目发起人接受了第{cycle}次循环的成果，进入结束阶段")
                        break
                    else:
                        if cycle < MAX_EXECUTION_CYCLES:
                            remaining = MAX_EXECUTION_CYCLES - cycle
                            print(f"\n[项目] ✗ 项目发起人拒绝当前版本，要求继续改进")
                            print(f"[系统] 还剩 {remaining} 次循环机会，开始第{cycle + 1}次循环")
                        else:
                            print(f"\n[项目] ✗ 项目发起人拒绝当前版本")
                            print(f"[系统] 已达到最大循环次数（{MAX_EXECUTION_CYCLES}次），强制进入结束阶段")
            
            # 阶段6：结束
            self.phase_closure()
            
            print(f"\n{'='*60}")
            print(f"项目生命周期执行完毕")
            print(f"{'='*60}\n")
            
        except Exception as e:
            print(f"\n[错误] 工作流执行出错：{e}")
            import traceback
            traceback.print_exc()
    
    def phase_pre_initiation(self):
        """第一阶段：预启动"""
        print(f"\n{'='*60}")
        print(f"阶段 1/6: {PHASES['PRE_INITIATION']}")
        print(f"{'='*60}\n")
        
        print("[1.1] 项目发起人陈述需求...")
        requirements = self.sponsor.state_requirements(self.project_idea)
        print(f"\n需求描述：\n{requirements}\n")
        
        print("[1.2] 项目经理起草项目章程...")
        charter = self.manager.draft_project_charter(requirements)
        print(f"\n项目章程：\n{charter}\n")
        
        # 保存到数据库和文档
        self.shared_db.save_project_charter(charter)
        self.doc_generator.generate_project_charter(charter)
        
        print(f"[完成] {PHASES['PRE_INITIATION']}阶段完成\n")
    
    def phase_initiation(self):
        """第二阶段：启动"""
        print(f"\n{'='*60}")
        print(f"阶段 2/6: {PHASES['INITIATION']}")
        print(f"{'='*60}\n")
        
        print("[2.1] 召开项目启动会议...")
        
        # 项目发起人发言
        charter = self.shared_db.data['project_charter']
        meeting_context = f"项目章程已经制定：\n{charter[:300]}...\n\n现在需要确定项目的三大约束。"
        
        print("[2.2] 项目发起人发言...")
        sponsor_input = self.sponsor.participate_in_kickoff(meeting_context)
        print(f"\n项目发起人：\n{sponsor_input}\n")
        
        # 团队成员发言
        print("[2.3] 项目组成员发言...")
        team_input = self.team_member.participate_in_kickoff(meeting_context)
        print(f"\n项目组成员：\n{team_input}\n")
        
        # 项目经理主持，确定三大约束
        print("[2.4] 项目经理总结，确定三大约束...")
        constraints = self.manager.facilitate_kickoff_meeting(sponsor_input, team_input)
        
        print(f"\n三大约束：")
        print(f"成本：{constraints.get('cost', '未定义')}")
        print(f"范围：{constraints.get('scope', '未定义')}")
        print(f"进度：{constraints.get('schedule', '未定义')}\n")
        
        # 保存到数据库
        self.shared_db.save_constraints({
            'cost': constraints.get('cost', ''),
            'scope': constraints.get('scope', ''),
            'schedule': constraints.get('schedule', '')
        })
        
        # 生成会议记录
        meeting_content = f"""
## 参会人员发言

### 项目发起人
{sponsor_input}

### 项目组成员
{team_input}

### 项目经理总结

{constraints.get('cost', '未定义')}

{constraints.get('scope', '未定义')}

{constraints.get('schedule', '未定义')}
"""
        
        self.shared_db.save_meeting_record(
            meeting_type=PHASES['INITIATION'],
            content=meeting_content
        )
        
        self.doc_generator.generate_meeting_minutes(
            phase=PHASES['INITIATION'],
            participants=['项目发起人', '项目经理', '项目组成员'],
            content=meeting_content
        )
        
        print(f"[完成] {PHASES['INITIATION']}阶段完成\n")
    
    def phase_planning(self):
        """第三阶段：计划"""
        print(f"\n{'='*60}")
        print(f"阶段 3/6: {PHASES['PLANNING']}")
        print(f"{'='*60}\n")
        
        print("[3.1] 项目经理创建WBS...")
        wbs = self.manager.create_wbs()
        print(f"\nWBS（部分）：\n{wbs[:300]}...\n")
        
        # 保存WBS
        self.shared_db.save_wbs(wbs)
        self.doc_generator.generate_wbs(wbs)
        
        print("[3.2] 项目经理创建管理计划...")
        plans = self.manager.create_management_plans()
        
        # 保存管理计划
        self.shared_db.save_management_plans(plans)
        for plan_type, plan_content in plans.items():
            self.doc_generator.generate_management_plan(plan_type, plan_content)
            print(f"  - {plan_type}管理计划已创建")
        
        # 新增：关键路径分析
        print("\n[3.3] 项目经理进行关键路径分析...")
        cpm_data = self.manager.perform_critical_path_analysis()
        
        print(f"\n关键路径分析结果：")
        print(f"  关键路径：{cpm_data.get('critical_path', '未识别')}")
        print(f"  总工期：{cpm_data.get('total_duration', 0)}天")
        print(f"  关键活动数：{len(cpm_data.get('activities', []))}")
        
        # 保存关键路径分析
        self.shared_db.save_critical_path_analysis(cpm_data)
        self.doc_generator.generate_critical_path_report(cpm_data)
        
        print(f"\n[完成] {PHASES['PLANNING']}阶段完成\n")
    
    def phase_execution(self, cycle: int):
        """第四阶段：执行"""
        print(f"\n{'='*60}")
        print(f"阶段 4/6: {PHASES['EXECUTION']} (循环 {cycle}/{MAX_EXECUTION_CYCLES})")
        print(f"{'='*60}\n")
        
        print(f"[4.{cycle}.1] 项目组成员开发代码...")
        code_files = self.team_member.develop_code(cycle)
        
        # 保存代码文件
        for filename, code_content in code_files.items():
            self.shared_db.save_code_file(filename, code_content)
            self.doc_generator.save_code_file(filename, code_content)
            print(f"  - 已保存：{filename} ({len(code_content)}字符)")
        
        print(f"\n[4.{cycle}.2] 项目组成员向项目经理报告进展...")
        progress_report = self.team_member.report_progress(cycle, code_files)
        print(f"\n进展报告：\n{progress_report}\n")
        
        # 记录讨论
        self.shared_db.save_discussion(
            participants=['项目组成员', '项目经理'],
            topic=f'第{cycle}次循环进展报告',
            content=progress_report
        )
        
        # 更新执行输出
        execution_output = f"""
代码文件：
{chr(10).join([f'- {name}' for name in code_files.keys()])}

进展报告：
{progress_report}
"""
        self.shared_db.save_execution_cycle(cycle, 'execution', {'output': execution_output})
        
        print(f"[完成] {PHASES['EXECUTION']}阶段（循环{cycle}）完成\n")
    
    def phase_control(self, cycle: int):
        """第五阶段：控制"""
        print(f"\n{'='*60}")
        print(f"阶段 5/6: {PHASES['CONTROL']} (循环 {cycle}/{MAX_EXECUTION_CYCLES})")
        print(f"{'='*60}\n")
        
        print(f"[5.{cycle}.1] 项目经理进行挣值分析...")
        evm_data = self.manager.perform_evm_analysis(cycle)
        
        print(f"\nEVM分析结果：")
        print(f"  PV: {evm_data['pv']:.2f}")
        print(f"  EV: {evm_data['ev']:.2f}")
        print(f"  AC: {evm_data['ac']:.2f}")
        print(f"  CPI: {evm_data['cpi']:.2f}")
        print(f"  SPI: {evm_data['spi']:.2f}\n")
        
        # 保存EVM记录
        self.shared_db.save_evm_record(cycle, evm_data)
        self.doc_generator.generate_evm_report(cycle, evm_data)
        
        # 新增：关键链计划分析
        print(f"[5.{cycle}.2] 项目经理进行关键链计划分析...")
        ccpm_data = self.manager.perform_critical_chain_analysis(cycle)
        
        print(f"\n关键链分析结果：")
        print(f"  关键链：{ccpm_data.get('critical_chain', '未识别')}")
        print(f"  项目缓冲区：{ccpm_data.get('buffers', {}).get('project_buffer', 0)}天")
        print(f"  资源约束：{ccpm_data.get('resource_constraints', '未分析')[:50]}...")
        
        # 保存关键链分析
        self.shared_db.save_critical_chain_record(cycle, ccpm_data)
        self.doc_generator.generate_critical_chain_report(cycle, ccpm_data)
        
        # 新增：净现值分析
        print(f"[5.{cycle}.3] 项目经理进行净现值分析...")
        npv_data = self.manager.perform_npv_analysis(cycle)
        
        print(f"\nNPV分析结果：")
        print(f"  净现值：{npv_data.get('npv_value', 0):.2f}万元")
        print(f"  贴现率：{npv_data.get('discount_rate', 0.1)*100:.1f}%")
        print(f"  投资建议：{npv_data.get('investment_recommendation', '未评估')[:50]}...")
        
        # 保存NPV分析
        self.shared_db.save_npv_record(cycle, npv_data)
        self.doc_generator.generate_npv_report(cycle, npv_data)
        
        # 如果不是第一次循环，根据反馈更新计划
        if cycle > 1:
            print(f"[5.{cycle}.4] 项目经理更新管理计划...")
            last_feedback = self.shared_db.data['execution_cycles'][cycle - 2].get('sponsor_feedback', '')
            update_result = self.manager.update_plans(cycle, last_feedback)
            print(f"\n计划更新：\n{update_result['update_summary']}\n")
        
        # 更新控制输出
        control_output = f"""
EVM分析：
- PV: {evm_data['pv']:.2f}
- EV: {evm_data['ev']:.2f}
- AC: {evm_data['ac']:.2f}
- CPI: {evm_data['cpi']:.2f}
- SPI: {evm_data['spi']:.2f}

关键链分析：
- 关键链：{ccpm_data.get('critical_chain', '未识别')}
- 项目缓冲区：{ccpm_data.get('buffers', {}).get('project_buffer', 0)}天

NPV分析：
- 净现值：{npv_data.get('npv_value', 0):.2f}万元
- 投资建议：{npv_data.get('investment_recommendation', '未评估')[:100]}...

分析结论：
{evm_data['analysis'][:200]}...
"""
        self.shared_db.save_execution_cycle(cycle, 'control', {
            'evm': evm_data,
            'ccpm': ccpm_data,
            'npv': npv_data,
            'control_output': control_output
        })
        
        print(f"[完成] {PHASES['CONTROL']}阶段（循环{cycle}）完成\n")
    
    def get_sponsor_review_only(self, cycle: int) -> str:
        """
        获取项目发起人的评审意见（仅反馈，不进行验收）
        
        Args:
            cycle: 当前循环次数
            
        Returns:
            反馈意见
        """
        print(f"\n[反馈] 项目发起人评审第{cycle}次循环的成果（仅反馈）...")
        
        # 准备产品描述
        code_files = self.shared_db.data.get('code_files', {})
        code_list = '\n'.join([f'- {name}' for name in code_files.keys()])
        
        execution_output = self.shared_db.data['execution_cycles'][cycle - 1].get('execution_output', '')
        
        # 项目发起人评审（仅反馈模式）
        feedback = self.sponsor.review_product(
            cycle=cycle,
            product_description=execution_output,
            code_files=code_list,
            review_only=True
        )
        
        print(f"\n项目发起人反馈意见：\n{feedback}")
        
        # 保存反馈（标记为未接受）
        self.shared_db.update_cycle_feedback(cycle, feedback, False)
        
        # 记录讨论
        self.shared_db.save_discussion(
            participants=['项目发起人', '项目团队'],
            topic=f'第{cycle}次循环评审意见',
            content=f"项目发起人反馈（第{cycle}次评审）：\n{feedback}"
        )
        
        # 项目组成员回应反馈
        print(f"\n[讨论] 项目组成员回应反馈...")
        team_response = self.team_member.discuss_with_sponsor(cycle, feedback)
        print(f"\n项目组成员：\n{team_response}\n")
        
        self.shared_db.save_discussion(
            participants=['项目组成员', '项目发起人'],
            topic=f'第{cycle}次循环改进计划',
            content=team_response
        )
        
        return feedback
        
    def get_sponsor_feedback(self, cycle: int) -> bool:
        """
        获取项目发起人反馈（正式验收）
        
        Args:
            cycle: 当前循环次数
            
        Returns:
            是否接受
        """
        print(f"\n[验收] 项目发起人正式验收第{cycle}次循环的成果...")
        
        # 准备产品描述
        code_files = self.shared_db.data.get('code_files', {})
        code_list = '\n'.join([f'- {name}' for name in code_files.keys()])
        
        execution_output = self.shared_db.data['execution_cycles'][cycle - 1].get('execution_output', '')
        
        # 项目发起人评审（验收模式）
        feedback, accepted = self.sponsor.review_product(
            cycle=cycle,
            product_description=execution_output,
            code_files=code_list,
            review_only=False
        )
        
        print(f"\n项目发起人验收意见：\n{feedback}")
        print(f"\n决策：{'【接受】' if accepted else '【拒绝】'}\n")
        
        # 保存反馈
        self.shared_db.update_cycle_feedback(cycle, feedback, accepted)
        
        # 如果被拒绝，团队成员与发起人讨论
        if not accepted and cycle < MAX_EXECUTION_CYCLES:
            print("[讨论] 项目组成员与项目发起人讨论改进方案...")
            team_response = self.team_member.discuss_with_sponsor(cycle, feedback)
            print(f"\n项目组成员：\n{team_response}\n")
            
            self.shared_db.save_discussion(
                participants=['项目组成员', '项目发起人'],
                topic=f'第{cycle}次循环改进讨论',
                content=team_response
            )
        
        return accepted
    
    def phase_closure(self):
        """第六阶段：结束"""
        print(f"\n{'='*60}")
        print(f"阶段 6/6: {PHASES['CLOSURE']}")
        print(f"{'='*60}\n")
        
        print("[6.1] 准备最终交付物...")
        
        # 导出数据库
        db_export_path = os.path.join(self.deliverables_path, 'project_data.json')
        self.shared_db.export_to_file(db_export_path)
        
        print("[6.2] 生成项目总结报告...")
        summary = self.doc_generator.generate_final_summary(self.shared_db.data, self.project_code)
        self.shared_db.save_document('项目总结报告', summary)
        
        print("[6.3] 项目发起人最终验收...")
        deliverables_summary = f"""
交付物清单：
- 项目章程
- 会议记录 {len(self.shared_db.data['meeting_records'])} 份
- WBS
- 三大管理计划（成本、范围、进度）
- EVM报告 {len(self.shared_db.data['evm_records'])} 份
- 代码文件 {len(self.shared_db.data['code_files'])} 个
- 项目数据库（JSON格式）
- 项目总结报告
"""
        
        final_opinion = self.sponsor.final_acceptance(deliverables_summary)
        print(f"\n最终验收意见：\n{final_opinion}\n")
        
        # 保存验收意见
        self.shared_db.save_document('最终验收意见', final_opinion)
        acceptance_doc = f"""# 项目最终验收意见

{final_opinion}

---

**项目发起人签字：** ____________

**日期：** {datetime.now().strftime('%Y-%m-%d')}
"""
        self.doc_generator.save_document('最终验收意见.md', acceptance_doc)
        
        print(f"[完成] {PHASES['CLOSURE']}阶段完成\n")
        
        print(f"\n{'='*60}")
        print(f"项目总结")
        print(f"{'='*60}")
        
        # 格式化显示项目总结
        summary_data = self.shared_db.get_summary()
        print(f"项目章程长度: {summary_data.get('project_charter_length', 0)} 字符")
        print(f"约束条件数量: {summary_data.get('constraints_count', 0)} 个")
        print(f"WBS长度: {summary_data.get('wbs_length', 0)} 字符")
        print(f"管理计划数量: {summary_data.get('management_plans_count', 0)} 个")
        print(f"会议记录数量: {summary_data.get('meeting_records_count', 0)} 份")
        print(f"讨论记录数量: {summary_data.get('discussions_count', 0)} 条")
        print(f"代码文件数量: {summary_data.get('code_files_count', 0)} 个")
        print(f"文档数量: {summary_data.get('documents_count', 0)} 份")
        print(f"EVM记录数量: {summary_data.get('evm_records_count', 0)} 份")
        print(f"执行循环数量: {summary_data.get('execution_cycles_count', 0)} 次")
        print(f"关键路径分析: {'已完成' if summary_data.get('has_critical_path_analysis') else '未完成'}")
        print(f"关键链记录数量: {summary_data.get('critical_chain_records_count', 0)} 份")
        print(f"NPV记录数量: {summary_data.get('npv_records_count', 0)} 份")
        
        print(f"\n所有交付物已保存到：{self.deliverables_path}")
        print(f"{'='*60}\n")
